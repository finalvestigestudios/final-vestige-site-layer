#!/usr/bin/env python3
"""R449: original candidate-level source citation incidence, DRAFT/HARD HOLD.

Read-only, stacked on R448. Never selects manuscripts, resolves disputed source
reading depth, approves safety/QD, publishes WordPress, or verifies paid orders.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re

R448_PATH = Path(__file__).with_name("r448_article_readiness_matrix.py")
_spec = importlib.util.spec_from_file_location("r448_parent", R448_PATH)
r448 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r448)

STATE = "DRAFT_HARD_HOLD"
CITE = re.compile(r"\{\{cite:([a-z0-9][a-z0-9-]*)\}\}")
FRAG = re.compile(r"\{\{\s*cite\s*:", re.I)
HIDDEN = {"script", "style", "template", "noscript", "svg"}
ARTICLE_DIR = Path("preparedness/content/articles")

class CitationReader(HTMLParser):
    """Visible raw citation markers with claim-context custody, no safety inference."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.stack = []
        self.citations = []
        self.errors = []
    def handle_starttag(self, tag, attrs):
        if FRAG.search(self.get_starttag_text() or ""):
            self.errors.append("CITATION_IN_HTML_ATTRIBUTE")
        hidden = tag.lower() in HIDDEN or any(
            name.lower() == "aria-hidden" and str(value).lower() == "true"
            for name, value in attrs)
        self.stack.append((tag.lower(), hidden))
    def handle_startendtag(self, tag, attrs):
        if FRAG.search(self.get_starttag_text() or ""):
            self.errors.append("CITATION_IN_HTML_ATTRIBUTE")
    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1, -1, -1):
            if self.stack[index][0] == tag.lower():
                del self.stack[index:]
                break
    def handle_comment(self, data):
        if FRAG.search(data):
            self.errors.append("CITATION_IN_COMMENT")
    def handle_data(self, data):
        if FRAG.search(data):
            if any(hidden for _, hidden in self.stack):
                self.errors.append("CITATION_IN_HIDDEN_ELEMENT")
                return
            remaining = CITE.sub("", data)
            if FRAG.search(remaining):
                self.errors.append("MALFORMED_CITATION_MARKER")
            fingerprint = hashlib.sha256(" ".join(data.split()).encode()).hexdigest()
            self.citations.extend({"source_id": m.group(1),
                "original_line": self.getpos()[0],
                "visible_context_sha256": fingerprint} for m in CITE.finditer(data))
        elif "{{cite" in data.lower():
            self.errors.append("MALFORMED_CITATION_MARKER")

def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def read_json(raw):
    return json.loads(raw.decode("utf-8"), object_pairs_hook=r448.object_unique)

def safe_read(root, relative):
    """None means absent on that contributor branch. Never follow symlinks."""
    root = Path(root)
    p = root / relative
    if not p.exists():
        return None
    if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(root.resolve()):
        raise ValueError("UNSAFE_OR_OUTSIDE_ORIGINAL_BRANCH_ROOT")
    return p.read_bytes()

def audit_original_incidence(docket, packet, heads, roots, *,
                             docket_raw=None, packet_raw=None, test_only=False):
    """Check exact body candidate multiplicities and cite-to-source_use placement.

    test_only is a unit-test API; it bypasses the R448 authenticated baseline,
    but outputs are explicitly SYNTHETIC and never qualify any release.
    """
    errors, candidates = [], []
    if not test_only:
        if not isinstance(docket_raw, bytes) or not isinstance(packet_raw, bytes):
            errors.append("AUTHENTIC_R397_AND_R446_BYTES_REQUIRED")
        else:
            baseline = r448.audit(docket, docket_raw, packet, packet_raw, heads)
            if not baseline["structural_evidence_pass"]:
                errors.append("R448_CUSTODY_BASELINE_FAILED")
                errors.extend(baseline["errors"])
    pins = {r["branch"]: r["sha"] for r in docket.get("branch_pins", [])}
    if not isinstance(roots, dict) or set(roots) != set(pins):
        errors.append("ALL_NINE_ORIGINAL_BRANCH_ROOTS_REQUIRED")
    if not test_only and heads != pins:
        errors.append("CURRENT_ORIGINAL_CONTRIBUTOR_HEADS_DRIFTED")
    sources = {r["source_id"] for r in docket.get("all_original_source_id_crosswalk", [])}
    observed = {}
    for row in sorted(docket.get("original_articles", []), key=lambda item: item["slug"]):
        slug = row["slug"]
        expected = row["body_candidate_git_blobs"]
        found = []
        for branch in sorted(pins):
            if branch not in roots:
                continue
            body_path = ARTICLE_DIR / (slug + ".body.html")
            meta_path = ARTICLE_DIR / (slug + ".meta.json")
            body = safe_read(roots[branch], body_path)
            meta_raw = safe_read(roots[branch], meta_path)
            if body is None and meta_raw is None:
                continue
            if body is None or meta_raw is None:
                errors.append("BODY_META_PAIR_INCOMPLETE:" + slug)
                continue
            sha = git_blob(body)
            found.append(sha)
            try:
                meta = read_json(meta_raw)
                markup = body.decode("utf-8")
            except (ValueError, UnicodeDecodeError):
                errors.append("NON_UTF8_OR_DUPLICATE_META:" + slug)
                continue
            if meta.get("slug") != slug:
                errors.append("META_ARTICLE_SLUG_DRIFT:" + slug)
            source_use = meta.get("source_use", {})
            if not isinstance(source_use, dict) or any(
                not isinstance(v, str) or not v.strip() for v in source_use.values()):
                errors.append("INVALID_DECLARED_READING_SCOPE:" + slug)
                source_use = {}
            if meta.get("status", {}).get("publish") not in ("draft", None):
                errors.append("UNAPPROVED_PUBLISH_STATE:" + slug)
            if meta.get("safety_review", {}).get("state") not in ("pending", "not-reviewed", None):
                errors.append("UNAPPROVED_SAFETY_REVIEW:" + slug)
            parser = CitationReader()
            parser.feed(markup)
            parser.close()
            if "&#123;" in markup or "&#x7b;" in markup.lower():
                errors.append("ENTITY_ENCODED_CITATION_REQUIRES_REVIEW:" + slug)
            errors.extend(e + ":" + slug for e in parser.errors)
            cited = {x["source_id"] for x in parser.citations}
            if cited - sources:
                errors.append("CITATION_MISSING_FROM_R397_SOURCE_REGISTER:" + slug)
            if cited - set(source_use):
                errors.append("CITATION_LACKS_META_SOURCE_READING_SCOPE:" + slug)
            if set(source_use) - sources:
                errors.append("META_SOURCE_USE_NOT_IN_ORIGINAL_REGISTER:" + slug)
            candidates.append({"slug": slug, "original_branch": branch,
                "body_git_blob": sha, "meta_git_blob": git_blob(meta_raw),
                "literal_visible_citation_count": len(parser.citations),
                "distinct_cited_source_ids": len(cited),
                "placement_fingerprints": parser.citations,
                "meta_source_use_ids": sorted(source_use),
                "declared_but_not_cited": sorted(set(source_use) - cited),
                "original_human_source_reading_approved": False,
                "qualified_safety_approved": False})
        observed[slug] = found
        if Counter(found) != Counter(expected):
            errors.append("ORIGINAL_BODY_APPEARANCE_MULTIPLICITY_DRIFT:" + slug)
    # Explicit original fork custody includes source fragment variants, never select.
    for fork in docket.get("original_fork_disputes", []):
        path = Path(fork["path"])
        if path.is_absolute() or ".." in path.parts or path.parts[0] != "preparedness":
            errors.append("INVALID_ORIGINAL_FORK_PATH")
            continue
        for variant in fork["variants"]:
            branch = variant["branch"]
            if branch not in roots:
                errors.append("MISSING_FORK_CONTRIBUTOR_ROOT")
                continue
            raw = safe_read(roots[branch], path)
            if raw is None or git_blob(raw) != variant["git_blob_sha"]:
                errors.append("ORIGINAL_BODY_META_OR_FRAGMENT_FORK_BLOB_DRIFT:" + str(path))
    return {"schema": "R449_ORIGINAL_CITATION_INCIDENCE_HARD_HOLD_v1",
        "release_state": STATE, "synthetic_test_only": bool(test_only),
        "structural_evidence_pass": not errors,
        "errors": sorted(set(errors)), "candidates": candidates,
        "original_article_identities": len(docket.get("original_articles", [])),
        "candidate_appearances_loaded": len(candidates),
        "unresolved_source_disputes": len(docket.get("source_evidence_disputes", [])),
        "unselected_original_forks": len(docket.get("original_fork_disputes", [])),
        "qualified_safety_approved": False, "qd_pass": False,
        "publication_allowed": False, "cms_write_allowed": False,
        "merchant_offer_verified": False, "verified_paid_orders": None,
        "net_revenue_per_1000_qualified_sessions": None}

def main(argv=None):
    p = argparse.ArgumentParser(description="Original citation replay; ALWAYS HARD HOLD")
    for k in ("docket", "packet", "observed-heads", "roots", "output"):
        p.add_argument("--" + k, type=Path, required=True)
    a = p.parse_args(argv)
    try:
        inputs = [a.docket, a.packet, a.observed_heads, a.roots]
        if a.output.resolve() in {p.resolve() for p in inputs}:
            raise ValueError("REFUSE_EVIDENCE_INPUT_OVERWRITE")
        raw = a.docket.read_bytes()
        packet_raw = a.packet.read_bytes()
        report = audit_original_incidence(read_json(raw), read_json(packet_raw),
            read_json(a.observed_heads.read_bytes()), read_json(a.roots.read_bytes()),
            docket_raw=raw, packet_raw=packet_raw)
    except (OSError, ValueError, TypeError, KeyError) as exc:
        report = {"release_state": STATE, "structural_evidence_pass": False,
                  "errors": ["INVALID_OR_MISSING_INPUT:" + type(exc).__name__],
                  "qualified_safety_approved": False, "qd_pass": False,
                  "publication_allowed": False, "cms_write_allowed": False}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"release_state": STATE, "structural_evidence_pass":
        report.get("structural_evidence_pass"), "errors": report.get("errors")}))
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
