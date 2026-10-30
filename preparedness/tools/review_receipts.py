#!/usr/bin/env python3
"""Fail-closed, offline reviewer handoff for Preparedness source/claim scopes.

Creates hash-bound review *requests*, never review approvals. Output is NOT evidence
that external pages were read, that medical/safety guidance is correct, or that
WordPress publication is authorized.
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
import hashlib
import io
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
_HEX = re.compile(r"[0-9a-f]{64}\Z")


def digest(value: object) -> str:
    """Stable digest of a JSON value, not a signature or independent attestation."""
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def build_manifest(queue: dict, fingerprints: dict[str, str]) -> dict:
    """Bind every reported citation to its exact article/source-scope fingerprint."""
    if queue.get("schema_version") != 1 or queue.get("release_state") != "HOLD" or queue.get("may_publish") is not False:
        raise ValueError("queue version or mandatory release hold changed")
    if queue.get("errors") or queue.get("summary", {}).get("structural_errors"):
        raise ValueError("source queue contains unresolved structural errors")
    prior = queue.get("sha256_review_queue_payload")
    actual = digest({k: v for k, v in queue.items() if k != "sha256_review_queue_payload"})
    if prior != actual:
        raise ValueError("source queue payload fingerprint does not match input")
    citations = queue.get("citations")
    groups = queue.get("collisions")
    if not isinstance(citations, list) or not isinstance(groups, list):
        raise ValueError("source queue citations/collisions must be arrays")
    if len(citations) != queue["summary"].get("article_source_citation_pairs"):
        raise ValueError("citation count changed from source queue summary")
    if len(groups) != queue["summary"].get("shared_url_groups"):
        raise ValueError("shared URL count changed from source queue summary")
    names = {x.get("article") for x in citations}
    if set(fingerprints) != names or any(not isinstance(v, str) or not _HEX.fullmatch(v) for v in fingerprints.values()):
        raise ValueError("missing, extra or invalid exact article-source fingerprints")
    records, seen_cites = [], set()
    group_index = {}
    for g in groups:
        url = g.get("url")
        keys = g.get("source_row_keys")
        if not isinstance(url, str) or not url.startswith("https://") or url in group_index:
            raise ValueError("invalid or duplicated shared source URL")
        if not isinstance(keys, list) or len(keys) < 2 or len(set(keys)) != len(keys):
            raise ValueError("shared URL must preserve distinct physical contributor source rows")
        if g.get("review_status") not in ("pending-human-source-and-reading-scope-review", "resolved"):
            raise ValueError("unknown shared source review state")
        group_index[url] = g
    for c in citations:
        article, sid, row = c.get("article"), c.get("source_id"), c.get("source_row_key")
        identity = (article, sid)
        if not all(isinstance(v, str) and v for v in identity + (row,)) or identity in seen_cites:
            raise ValueError("missing or repeated article-to-source citation identity")
        seen_cites.add(identity)
        url = c.get("url")
        if c.get("shared_url_group") != (url in group_index):
            raise ValueError("citation shared-URL flag mismatches declared groups")
        if url in group_index and row not in group_index[url]["source_row_keys"]:
            raise ValueError("shared citation lost its distinct physical source row")
        if c.get("source_origin") not in ("base", c.get("article_origin")):
            raise ValueError("citation borrowed another contributor's reading scope")
        if not isinstance(c.get("author_claim_scope"), str) or not c["author_claim_scope"].strip():
            raise ValueError("citation has no article-specific reading scope")
        if not isinstance(c.get("contributor_claim_scope"), str) or not c["contributor_claim_scope"].strip():
            raise ValueError("citation has no contributor-specific claim support")
        source_digest = fingerprints[article]
        data = {
            "article": article, "article_path": c["article_path"],
            "article_status": c["status"], "article_safety_state": c["safety_review"],
            "source_id": sid, "source_row_key": row, "url": url,
            "source_origin": c["source_origin"], "article_origin": c["article_origin"],
            "article_source_fingerprint": source_digest,
            "article_claim_scope": c["author_claim_scope"],
            "contributor_claim_scope": c["contributor_claim_scope"],
            "contributor_reading_limits": c.get("reading_limits"),
            "machine_checked_on": c.get("machine_checked_on"),
            "human_link_checked_prior": c.get("human_link_checked") is True,
            "shared_url": url in group_index,
        }
        if c["status"] != "draft":
            raise ValueError("publication status changed: only unpublished drafts can be reviewed")
        records.append({**data, "review_request_sha256": digest(data),
                        "review_state": "PENDING_HUMAN", "approved": False})
    records.sort(key=lambda x: (x["article"], x["source_id"], x["source_row_key"]))
    packets = []
    for url, group in sorted(group_index.items()):
        group_cites = [c for c in records if c["url"] == url]
        expected = set(group.get("cited_source_rows", []))
        actual_rows = {c["source_row_key"] for c in group_cites}
        if expected != actual_rows:
            raise ValueError("shared URL cited contributor row inventory changed")
        data = {
            "url": url, "review_status_previous": group["review_status"],
            "all_source_row_keys": sorted(group["source_row_keys"]),
            "cited_source_row_keys": sorted(actual_rows),
            "uncited_source_row_keys": sorted(set(group["source_row_keys"]) - actual_rows),
            "citations": [{"article": c["article"], "source_id": c["source_id"],
                           "source_row_key": c["source_row_key"],
                           "review_request_sha256": c["review_request_sha256"],
                           "article_claim_scope": c["article_claim_scope"],
                           "contributor_claim_scope": c["contributor_claim_scope"],
                           "contributor_reading_limits": c["contributor_reading_limits"]}
                          for c in group_cites],
        }
        packets.append({**data, "packet_sha256": digest(data),
                        "review_state": "PENDING_HUMAN", "approved": False,
                        "human_tasks": ["Open exact current primary source URL and record date, redirects and version",
                                        "Compare each contributor's inspected text and limits, without merging their evidence",
                                        "Check article-specific factual claims against the actual supporting section",
                                        "Escalate any water, food, medicine, infant, fire or CO advice to qualified safety review"]})
    result = {
        "schema_version": 1, "purpose": "REVIEW_REQUESTS_NOT_INDEPENDENT_QA_OR_SAFETY_APPROVAL",
        "release_state": "HOLD", "may_publish": False, "human_review_performed": False,
        "source_queue_sha256": prior, "counts": {"citation_requests": len(records),
                                                "shared_url_packets": len(packets),
                                                "pending_human_url_checks": queue["summary"]["human_link_checks_pending"]},
        "citations": records, "shared_url_packets": packets,
    }
    result["manifest_sha256"] = digest(result)
    return result


def safe_csv_cell(value: object) -> str:
    """Avoid spreadsheet formula injection when humans open exported scopes in Excel."""
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)
    if re.match(r"\s*[=+@\-]", value) or value.startswith(("\t", "\r", "\n", "\ufeff")):
        return "'" + value
    return value


def citation_csv(manifest: dict) -> str:
    cols = ("review_request_sha256", "article", "article_path", "article_status",
            "article_safety_state", "source_id", "source_row_key", "url",
            "source_origin", "article_source_fingerprint", "article_claim_scope",
            "contributor_claim_scope", "contributor_reading_limits", "review_state")
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\r\n")
    writer.writerow(cols)
    for item in manifest["citations"]:
        writer.writerow([safe_csv_cell(item.get(col)) for col in cols])
    return out.getvalue()


def guarded_output_dir(target: Path, root: Path = ROOT) -> Path:
    """Prevent a review export from writing to WordPress input or outside build/."""
    build = root / "build"
    if build.is_symlink():
        raise ValueError("build root must not be a symlink")
    allowed = build.resolve()
    destination = target.resolve()
    if not destination.is_relative_to(allowed):
        raise ValueError("review output must be within the Preparedness build directory")
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, help="optional offline output under preparedness/build/ only")
    parser.add_argument("--require-release-ready", action="store_true")
    args = parser.parse_args(argv)
    sys.path.insert(0, str(ROOT / "tools"))
    import build
    import evidence_freeze
    import source_review_queue
    lib = build.Library()
    queue = source_review_queue.build_review_queue(lib)
    fingerprints = {slug: evidence_freeze.fingerprint(lib, meta)
                    for slug, meta in lib.articles.items()}
    try:
        result = build_manifest(queue, fingerprints)
        encoded = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
        if args.out_dir:
            destination = guarded_output_dir(args.out_dir)
            destination.mkdir(parents=True, exist_ok=True)
            (destination / "review-requests.json").write_text(encoded, encoding="utf-8")
            (destination / "citation-review.csv").write_text(citation_csv(result), encoding="utf-8", newline="")
        else:
            sys.stdout.write(encoded)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f"Review packet FAILED CLOSED: {exc}", file=sys.stderr)
        return 2
    return 1 if args.require_release_ready else 0


if __name__ == "__main__":
    raise SystemExit(main())
