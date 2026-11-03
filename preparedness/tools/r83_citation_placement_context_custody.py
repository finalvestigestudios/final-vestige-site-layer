#!/usr/bin/env python3
"""R83 PRIVATE HOLD — exact citation placement and surrounding-claim context custody.

A citation retained after prose revision is NOT automatically evidence for the
revised claim. Classifies lexical changes and unrendered citation locations for
human review. Uses R82's four complete Git snapshots and does not alter them.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
from html.parser import HTMLParser
import importlib.util
import io
import json
from pathlib import Path
import re

SCHEMA = "r83-four-snapshot-citation-placement-context-hold-v1"
STAGES = ("frozen", "integrated", "current", "rc")
REVIEW = "NOT_REVIEWED"
BLOCKS = frozenset(("p", "li", "td", "th", "dt", "dd", "figcaption",
                    "blockquote", "pre", "summary", "h1", "h2", "h3",
                    "h4", "h5", "h6"))
NON_VISIBLE = frozenset(("script", "style", "template", "noscript"))
VOID = frozenset(("area", "base", "br", "col", "embed", "hr", "img",
                  "input", "link", "meta", "param", "source", "track", "wbr"))
CITATION = re.compile(r"\{\{cite:([^{}]+)\}\}")


class Hold(ValueError):
    """Review-only custody failed closed."""


def need(value, message):
    if not value:
        raise Hold(message)


def parent_module():
    path = Path(__file__).with_name("r82_four_snapshot_citation_custody.py")
    need(path.is_file() and not path.is_symlink(), "R82 exact parent missing")
    spec = importlib.util.spec_from_file_location("r83_r82_parent", path)
    need(spec is not None and spec.loader is not None, "R82 import unavailable")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def normalize_text(value):
    return " ".join(value.split())


class CitationScope(HTMLParser):
    """Text-node-only locator. Tokens in markup/comments are NOT claim anchors."""

    def __init__(self, html):
        super().__init__(convert_charrefs=False)
        need(type(html) is str, "complete HTML must be UTF-8 string")
        self.source = html
        self.lines = [0]
        for line in html.splitlines(keepends=True):
            self.lines.append(self.lines[-1] + len(line))
        self.stack = []
        self.frames = []
        self.hits = {}
        self.heading_frames = []

    def _charpos(self):
        line, col = self.getpos()
        need(1 <= line <= len(self.lines), "HTML parser line out of range")
        return self.lines[line - 1] + col

    def _bytepos(self, charpos):
        return len(self.source[:charpos].encode("utf-8"))

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        frame = None
        if tag in BLOCKS:
            frame = {"tag": tag, "start": self._bytepos(self._charpos()),
                     "pieces": []}
            self.frames.append(frame)
            if tag.startswith("h") and tag[1:].isdigit():
                self.heading_frames.append(frame)
        if tag not in VOID:
            self.stack.append((tag, frame))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        for idx in range(len(self.stack) - 1, -1, -1):
            if self.stack[idx][0] == tag:
                del self.stack[idx:]
                return

    def handle_data(self, data):
        active = [frame for _, frame in self.stack if frame is not None]
        for frame in active:
            frame["pieces"].append(data)
        if any(tag in NON_VISIBLE for tag, _ in self.stack):
            return
        start = self._charpos()
        for match in CITATION.finditer(data):
            location = self._bytepos(start + match.start())
            need(location not in self.hits, "duplicate citation byte location")
            self.hits[location] = (match.group(0), active[-1] if active else None)

    def mapping(self, events):
        need(type(events) is list, "citation token list missing")
        headings = sorted(
            (frame["start"], normalize_text("".join(frame["pieces"])))
            for frame in self.heading_frames)
        rows = []
        seen = set()
        raw = self.source.encode("utf-8")
        for event in events:
            offset = event["byte_offset"]
            token = event["literal_token"]
            need(type(offset) is int and offset >= 0
                 and type(token) is str and token.encode("utf-8") ==
                 raw[offset:offset + len(token.encode("utf-8"))],
                 "R82 literal citation bytes or location changed")
            need(offset not in seen, "citation location duplicated")
            seen.add(offset)
            hit = self.hits.get(offset)
            visible = hit is not None and hit[0] == token and hit[1] is not None
            frame = hit[1] if visible else None
            context = "".join(frame["pieces"]) if frame else None
            preceding = [value for start, value in headings if start <= offset]
            heading = preceding[-1] if preceding else None
            rows.append({
                "ordinal": event["ordinal"], "literal_token": token,
                "raw_source_id": event["raw_source_id"],
                "literal_byte_offset": offset,
                "line_number": event["line_number"],
                "scope_state": ("VISIBLE_CONTAINER_NOT_SUPPORT_PROOF" if visible
                                else "UNMAPPED_OR_NONVISIBLE_REVIEW"),
                "container_kind": frame["tag"] if frame else None,
                "complete_container_text_UNABRIDGED": context,
                "container_text_digest": digest(normalize_text(context).encode("utf-8"))
                if context is not None else None,
                "nearest_preceding_heading_UNABRIDGED": heading,
                "source_candidates_NOT_ALIASED":
                    event["distinct_scoped_source_variants_NOT_ALIASED"],
                "source_scope_state": event["scope_state"],
                "human_claim_support_review": REVIEW,
                "qualified_safety_review": REVIEW, "may_publish": False,
            })
        return rows


def anchors(snapshot):
    need(type(snapshot) is dict and snapshot.get("stage") in STAGES,
         "invalid R82 article stage")
    raw = snapshot["complete_HTML_UTF8"]
    need(digest(raw.encode("utf-8")) == snapshot["body_sha256"],
         "article HTML no longer matches R82 original bytes")
    parser = CitationScope(raw)
    parser.feed(raw)
    parser.close()
    rows = parser.mapping(snapshot["citations_in_original_order"])
    need(len(rows) == snapshot["citation_count"]
         and [e["ordinal"] for e in rows] == list(range(len(rows))),
         "citation count or original ordering dropped")
    return rows


def occurrence_keys(events):
    counts = Counter()
    result = {}
    for event in events:
        sid = event["raw_source_id"]
        need(type(sid) is str and sid, "empty citation source identity")
        counts[sid] += 1
        key = (sid, counts[sid])
        need(key not in result, "duplicate citation occurrence key")
        result[key] = event
    return result


def compare(before, after):
    """Occurrence-rank alignment never asserts that retained IDs support text."""
    old = occurrence_keys(before)
    new = occurrence_keys(after)
    orders = []
    for sid, rank in sorted(set(old) | set(new)):
        a = old.get((sid, rank))
        b = new.get((sid, rank))
        cues = []
        if a is None:
            cues.append("CITATION_ADDED_REVIEW")
        elif b is None:
            cues.append("CITATION_REMOVED_REVIEW")
        else:
            if a["scope_state"] != "VISIBLE_CONTAINER_NOT_SUPPORT_PROOF" or \
                    b["scope_state"] != "VISIBLE_CONTAINER_NOT_SUPPORT_PROOF":
                cues.append("NONVISIBLE_OR_UNMAPPED_REVIEW")
            if a["container_text_digest"] != b["container_text_digest"] or \
                    a["container_kind"] != b["container_kind"]:
                cues.append("CONTAINER_CONTEXT_CHANGED_REVIEW")
            if a["nearest_preceding_heading_UNABRIDGED"] != \
                    b["nearest_preceding_heading_UNABRIDGED"]:
                cues.append("SECTION_CONTEXT_CHANGED_REVIEW")
            if a["source_candidates_NOT_ALIASED"] != b["source_candidates_NOT_ALIASED"] or \
                    a["source_scope_state"] != b["source_scope_state"]:
                cues.append("SOURCE_CANDIDATE_VARIANTS_CHANGED_REVIEW")
            if a["literal_byte_offset"] != b["literal_byte_offset"]:
                cues.append("CITATION_BYTE_POSITION_CHANGED_REVIEW")
            if a["ordinal"] != b["ordinal"]:
                cues.append("CITATION_SEQUENCE_ORDER_CHANGED_REVIEW")
        orders.append({"raw_source_id": sid, "within_ID_occurrence": rank,
                       "before_FULL_ANCHOR": a, "after_FULL_ANCHOR": b,
                       "review_cues_NOT_VERDICTS": cues,
                       "human_claim_support_review": REVIEW,
                       "qualified_safety_review": REVIEW, "may_publish": False})
    return orders


def construct(r82_report):
    """Every R82 source/HTML/metadata record remains pinned by the parent seal."""
    r82 = parent_module()
    r82.verify(r82_report)
    need(r82_report.get("release_state") == "HOLD"
         and r82_report.get("may_publish") is False,
         "R82 source is not a protected draft")
    records = []
    total = 0
    unmapped = 0
    cues_count = Counter()
    for item in r82_report["all_29_article_citation_metadata_histories_UNABRIDGED"]:
        four = item["four_unabridged_HTML_and_metadata_snapshots"]
        need(set(four) == set(STAGES), "lost historical article snapshot")
        four_anchors = {stage: anchors(four[stage]) for stage in STAGES}
        changes = compare(four_anchors["current"], four_anchors["rc"])
        for stage in STAGES:
            total += len(four_anchors[stage])
            unmapped += sum(e["scope_state"] != "VISIBLE_CONTAINER_NOT_SUPPORT_PROOF"
                            for e in four_anchors[stage])
        for order in changes:
            cues_count.update(order["review_cues_NOT_VERDICTS"])
        records.append({
            "origin": item["origin"], "path": item["path"],
            "four_snapshot_citation_anchors_NOT_APPROVED": four_anchors,
            "current_TO_rc_occurrence_rank_review": changes,
            "human_claim_support_review": REVIEW,
            "qualified_safety_review": REVIEW, "may_publish": False,
        })
    need(len(records) == 29, "contributor article groups missing")
    report = {
        "schema": SCHEMA, "issue": 136, "release_state": "HOLD",
        "may_publish": False, "medical_safety_approved": False,
        "human_source_approvals": 0, "human_claim_approvals": 0,
        "qualified_safety_approvals": 0, "independent_QD_approvals": 0,
        "exact_r82_evidence_sha256_seal": r82_report["sha256_seal"],
        "separate_RC_sha": r82_report["separate_RC_sha"],
        "counts": {"article_groups": len(records),
                   "four_stage_snapshots": len(records) * 4,
                   "four_stage_citation_anchors": total,
                   "unmapped_or_nonvisible_review_anchors": unmapped,
                   "current_rc_review_occurrence_rows": sum(len(x[
                       "current_TO_rc_occurrence_rank_review"]) for x in records),
                   "review_cues_NOT_CONFIRMED_ERRORS": dict(sorted(cues_count.items()))},
        "all_29_four_stage_citation_context_packets_UNABRIDGED": records
    }
    report["sha256_seal"] = digest(canonical(report))
    return report


def verify(report, exact_r82_report):
    need(type(report) is dict and report.get("schema") == SCHEMA
         and report.get("issue") == 136 and report.get("release_state") == "HOLD"
         and report.get("may_publish") is False
         and report.get("medical_safety_approved") is False
         and all(report.get(k) == 0 for k in (
             "human_source_approvals", "human_claim_approvals",
             "qualified_safety_approvals", "independent_QD_approvals")),
         "forged approval or release state")
    need(report.get("sha256_seal") == digest(canonical({
        key: value for key, value in report.items() if key != "sha256_seal"})),
        "R83 private ledger digest mismatch")
    need(report == construct(exact_r82_report),
         "R83 anchor/claim-context reconstruction mismatch")


def reviewer_csv(report, exact_r82_report):
    verify(report, exact_r82_report)
    r82 = parent_module()
    out = io.StringIO(newline="")
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["origin", "article", "citation_ID", "within_ID_occurrence",
                     "review_cues_NOT_VERDICTS", "human_review", "release"])
    for row in report["all_29_four_stage_citation_context_packets_UNABRIDGED"]:
        for item in row["current_TO_rc_occurrence_rank_review"]:
            cues = item["review_cues_NOT_VERDICTS"]
            if cues:
                writer.writerow([r82.safe_csv(row["origin"]),
                                 r82.safe_csv(row["path"]),
                                 r82.safe_csv(item["raw_source_id"]),
                                 item["within_ID_occurrence"], ";".join(cues),
                                 REVIEW, "HOLD"])
    return out.getvalue()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv-stdout", action="store_true",
                        help="private review queue only; never post as public content")
    args = parser.parse_args(argv)
    r82 = parent_module().live_report()
    report = construct(r82)
    verify(report, r82)
    if args.csv_stdout:
        print(reviewer_csv(report, r82), end="")
    else:
        print(json.dumps({"schema": SCHEMA, "release": "HOLD",
                          "counts": report["counts"],
                          "exact_r82_evidence_seal": report[
                              "exact_r82_evidence_sha256_seal"],
                          "r83_sha256_seal": report["sha256_seal"],
                          "human_claim_or_safety_approvals": 0,
                          "public_or_WordPress_writes": 0}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (Hold, KeyError, TypeError, ValueError, OSError) as exc:
        raise SystemExit("R83 FAILED CLOSED — " + str(exc))
