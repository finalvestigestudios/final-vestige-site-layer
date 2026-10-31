#!/usr/bin/env python3
"""Private, deterministic per-occurrence citation review queue for Preparedness.

A source-use note covers an article/source PAIR; a single source can be invoked for
multiple different claims. This ledger preserves every visible {{cite:id}} token,
its paragraph-level editorial context, contributor-owned physical source row,
and an evidence/content fingerprint. It is NOT a source or safety verification.
No network, WordPress, publication, source-metadata, or human-approval writes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from html import unescape
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import sys

CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
BLOCKS = frozenset({"p", "li", "td", "th", "blockquote", "dd", "dt", "figcaption",
                    "caption", "h1", "h2", "h3", "h4", "h5", "h6", "div", "section"})
NONVISIBLE = frozenset({"script", "style", "template", "noscript", "svg"})
ACCEPTED_STATES = frozenset({"pending", "approved", "not-required"})
BASELINE = {"draft_items": 36, "article_source_pairs": 367, "physical_source_rows": 224,
            "shared_url_groups": 30}
MAX_FIELD = 6000


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def compact(value: str) -> str:
    return " ".join(unescape(value).split())


class VisibleClaims(HTMLParser):
    """Map literal citation tokens to their closest semantic text container.

    Reject citations appearing only in attributes, comments, script or hidden
    templates. An HTML parser is essential here: a regex stripping tags would
    quietly manufacture false claim contexts from markup or nearby paragraphs.
    """
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.frames: list[dict] = []
        self.refs: list[dict] = []
        self.hidden: list[str] = []
        self.heading = ""
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in NONVISIBLE:
            self.hidden.append(tag)
        if tag in BLOCKS and not self.hidden:
            self.frames.append({"tag": tag, "parts": [], "refs": [], "heading": self.heading})

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # Self-closing tags cannot contain substantive citation claims.
        return

    def handle_data(self, text: str) -> None:
        if self.hidden:
            return
        for frame in self.frames:
            frame["parts"].append(text)
        for match in CITE.finditer(text):
            if not self.frames:
                self.errors.append("visible citation outside semantic text block")
                continue
            frame = self.frames[-1]
            ref = {"source_id": match.group(1), "block": frame, "line": self.getpos()[0],
                   "ordinal": len(self.refs) + 1, "offset": match.start()}
            frame["refs"].append(ref)
            self.refs.append(ref)

    def handle_endtag(self, tag: str) -> None:
        if self.hidden:
            if tag == self.hidden[-1]:
                self.hidden.pop()
            return
        if tag in BLOCKS:
            if not self.frames or self.frames[-1]["tag"] != tag:
                # The site's existing HTML validator remains the authority for
                # complete well-formedness; this queue cannot silently cross blocks.
                self.errors.append(f"unmatched semantic closing tag {tag}")
                return
            frame = self.frames.pop()
            if tag in {"h1", "h2", "h3"}:
                self.heading = compact("".join(frame["parts"]))[:300]

    def finish(self, body: str) -> list[dict]:
        raw_tokens = CITE.findall(body)
        if self.frames or self.hidden:
            self.errors.append("unclosed semantic block or hidden element")
        if len(raw_tokens) != len(self.refs):
            self.errors.append("citation token in nonvisible HTML, comment or attribute")
        if raw_tokens != [ref["source_id"] for ref in self.refs]:
            self.errors.append("literal citations and visible text citations disagree")
        if self.errors:
            raise ValueError("; ".join(sorted(set(self.errors))))
        result = []
        for ref in self.refs:
            frame = ref["block"]
            raw_context = "".join(frame["parts"])
            full = compact(CITE.sub("", raw_context))
            if not full:
                raise ValueError(f"citation {ref['ordinal']} has no surrounding claim text")
            # A long list/div must not erase an individual's adjacent claim.
            # Preserve the full contextual hash even when the display excerpt is shortened.
            excerpt = full if len(full) <= 1000 else full[:500] + " … [EXCERPT; SEE ORIGINAL BODY] … " + full[-350:]
            result.append({"ordinal": ref["ordinal"], "source_id": ref["source_id"],
                           "block_tag": frame["tag"], "heading": frame["heading"],
                           "body_line": ref["line"], "context_excerpt": excerpt,
                           "context_chars": len(full), "context_sha256": hashlib.sha256(full.encode()).hexdigest(),
                           "context_is_excerpt": len(full) > 1000})
        return result


def parse_visible_claims(body: str) -> list[dict]:
    if not isinstance(body, str) or not body.strip():
        raise ValueError("article body missing")
    if "\x00" in body:
        raise ValueError("article body contains NUL")
    parser = VisibleClaims()
    parser.feed(body)
    parser.close()
    return parser.finish(body)


def physical_row_index(rows: list[dict]) -> dict[tuple[str, str, str], dict]:
    result: dict[tuple[str, str, str], dict] = {}
    keys: set[str] = set()
    for row in rows:
        key = (row["origin"], row["source_id"], row["url"])
        if key in result or row["row_key"] in keys:
            raise ValueError("duplicate source row identity or physical source key")
        if not str(row["url"]).startswith("https://"):
            raise ValueError("non-HTTPS source registry URL")
        result[key] = row
        keys.add(row["row_key"])
    return result


def scan_article(slug: str, meta: dict, resolver, index: dict, evidence_fingerprint: str) -> tuple[list[dict], set[str]]:
    if meta.get("slug") != slug or not isinstance(meta.get("_body"), str):
        raise ValueError(f"{slug}: inconsistent article body/slug")
    if meta.get("status", {}).get("publish") != "draft":
        raise ValueError(f"{slug}: refuse non-draft state")
    review = meta.get("safety_review", {})
    if review.get("state") not in ACCEPTED_STATES:
        raise ValueError(f"{slug}: unknown safety review state")
    notes = meta.get("source_use")
    if not isinstance(notes, dict) or not notes:
        raise ValueError(f"{slug}: missing per-source editorial use notes")
    claims = parse_visible_claims(meta["_body"])
    used = {x["source_id"] for x in claims}
    if used != set(notes):
        raise ValueError(f"{slug}: citation/source_use parity mismatch: {sorted(used ^ set(notes))}")
    if not re.fullmatch(r"[a-f0-9]{64}", evidence_fingerprint):
        raise ValueError(f"{slug}: invalid evidence SHA256")
    body_sha = hashlib.sha256(meta["_body"].encode("utf-8")).hexdigest()
    seen: set[str] = set()
    for claim in claims:
        sid = claim["source_id"]
        note = notes[sid]
        if not isinstance(note, str) or not note.strip() or len(note) > MAX_FIELD:
            raise ValueError(f"{slug}: missing/oversized specific evidence use note for {sid}")
        source = resolver(meta, sid)
        key = (source["_origin"], sid, source["url"])
        row = index.get(key)
        if row is None:
            raise ValueError(f"{slug}: resolved citation lacks exact physical contributor row: {sid}")
        if not isinstance(row.get("supports"), str) or not row["supports"].strip():
            raise ValueError(f"{slug}: source {sid} has no support assertion")
        identity = {"slug": slug, "source_id": sid, "ordinal": claim["ordinal"],
                    "source_row_key": row["row_key"], "article_evidence_sha256": evidence_fingerprint,
                    "body_sha256": body_sha, "context_sha256": claim["context_sha256"],
                    "source_use_sha256": hashlib.sha256(note.encode("utf-8")).hexdigest(),
                    "source_support_sha256": hashlib.sha256(row["supports"].encode("utf-8")).hexdigest(),
                    "source_limits_sha256": hashlib.sha256(str(row.get("reading_limits") or "").encode("utf-8")).hexdigest()}
        item_sha = digest(identity)
        if item_sha in seen:
            raise ValueError(f"{slug}: duplicate occurrence identity")
        seen.add(item_sha)
        claim.update({"article": slug, "article_evidence_sha256": evidence_fingerprint,
                      "body_sha256": body_sha, "source_origin": source["_origin"],
                      "source_row_key": row["row_key"], "source_url": source["url"],
                      "article_source_use": note, "contributor_claimed_support": row["supports"],
                      "contributor_reading_limits": row.get("reading_limits"),
                      "inherited_safety_state": review["state"],
                      "claim_review": "PENDING_INDEPENDENT_HUMAN_CHECK",
                      "claim_request_sha256": item_sha, "release_state": "HOLD", "may_publish": False})
    return claims, used


def make_report(lib, *, rows: list[dict], fingerprint, expect: dict | None = None) -> dict:
    index = physical_row_index(rows)
    all_claims = []
    pairs: set[tuple[str, str]] = set()
    routes: set[str] = set()
    states: dict[str, int] = {}
    for slug, meta in sorted(lib.articles.items(), key=lambda x: (x[1].get("n", 999), x[0])):
        route = lib.url_path(slug)
        if route in routes:
            raise ValueError("duplicate article route")
        routes.add(route)
        claims, used = scan_article(slug, meta, lib.source_for, index, fingerprint(lib, meta))
        pairs.update((slug, sid) for sid in used)
        all_claims.extend(claims)
        state = meta["safety_review"]["state"]
        states[state] = states.get(state, 0) + 1
    shared_groups = sum(len(group) > 1 for group in _group_rows(rows).values())
    counts = {"draft_items": len(lib.articles), "article_source_pairs": len(pairs),
              "physical_source_rows": len(rows), "shared_url_groups": shared_groups,
              "citation_occurrences": len(all_claims)}
    for name, value in (expect or {}).items():
        if counts.get(name) != value:
            raise ValueError(f"baseline drift {name}: got {counts.get(name)} expected {value}; require explicit review")
    ids = [c["claim_request_sha256"] for c in all_claims]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate claim occurrence across article corpus")
    return {"schema_version": 1, "authority": "MACHINE_ONLY_NO_EXTERNAL_SOURCE_OR_SAFETY_APPROVAL",
            "release_state": "HOLD", "may_publish": False, "human_link_checks_documented_by_tool": 0,
            "reviewed_claim_occurrences": 0, "verified_citation_claims": 0,
            "counts": counts, "inherited_safety_states": dict(sorted(states.items())),
            "evidence_digest_sha256": digest(ids), "claims": all_claims}


def _group_rows(rows: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(row["url"], []).append(row)
    return groups


def csv_safe(v: object) -> str:
    text = str(v if v is not None else "").replace("\x00", "")
    if text.lstrip().startswith(("=", "+", "-", "@")) or text.startswith(("\t", "\r", "\n")):
        return "'" + text
    return text


def csv_export(report: dict) -> str:
    out = io.StringIO(newline="")
    cols = ("article", "ordinal", "source_id", "source_origin", "source_row_key", "source_url",
            "heading", "block_tag", "context_excerpt", "article_source_use", "contributor_claimed_support",
            "contributor_reading_limits", "inherited_safety_state", "claim_review", "claim_request_sha256")
    writer = csv.DictWriter(out, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for claim in report["claims"]:
        writer.writerow({name: csv_safe(claim.get(name)) for name in cols})
    return out.getvalue()


def safe_export(path: Path, payload: str, root: Path) -> None:
    root = root.resolve(strict=True)
    if path.is_symlink():
        raise ValueError("export cannot overwrite symlink")
    target = path.resolve(strict=False)
    if not target.is_relative_to(root) or target.parent != root:
        raise ValueError("review export must be a direct path within private preparedness/build")
    if not target.parent.is_dir():
        raise ValueError("private build folder is missing")
    # Review-only report; never write public output tree or WordPress paths.
    target.write_text(payload, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json-out", type=Path)
    ap.add_argument("--csv-out", type=Path)
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "tools"))
    import build
    import evidence_freeze
    import source_review_queue
    lib = build.Library(root)
    report = make_report(lib, rows=source_review_queue.source_rows(root),
                         fingerprint=evidence_freeze.fingerprint, expect=BASELINE)
    dest = root / "build"
    if args.json_out:
        safe_export(args.json_out, json.dumps(report, ensure_ascii=False, indent=2) + "\n", dest)
    if args.csv_out:
        safe_export(args.csv_out, csv_export(report), dest)
    print(json.dumps({"release_state": "HOLD", "counts": report["counts"],
                      "evidence_digest_sha256": report["evidence_digest_sha256"],
                      "claim_reviews_completed": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
