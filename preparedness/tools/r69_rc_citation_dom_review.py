#!/usr/bin/env python3
"""R69 PRIVATE HOLD: citation-to-HTML-DOM visibility and block-context work orders.

Mechanical HTML parsing is NOT browser rendering, factual source verification,
qualified health/safety review, or permission to publish. Runs read-only against
R68's pinned original-and-release-candidate evidence. Only private reviewer CSV
may be exported; no WordPress, navigation or source-fingerprint updates.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from html.parser import HTMLParser
import importlib.util
import io
import json
from pathlib import Path
import re
import sys

SCHEMA = "r69-private-rc-dom-citation-context-review-v1"
# R68's actual schema is asserted below, not inferred from PR prose.
PARENT_SCHEMA = "r68-private-rc-document-citation-source-scope-v1"
HOLD = ("may_publish", "independent_QD_approval",
        "qualified_safety_clearance", "human_source_links_verified")
EXPECTED = (35, 6, 1959, 244, 2173)
CITE = re.compile(r"\{\{cite:([a-z0-9-]+)\}\}")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
BLOCK = frozenset(("p", "li", "td", "th", "tr", "h1", "h2", "h3", "h4", "h5", "h6",
                   "blockquote", "figcaption", "dt", "dd", "summary", "pre", "div"))
SUPPRESS = frozenset(("script", "style", "template", "head", "svg", "math", "iframe", "canvas"))
VOID = frozenset(("area", "base", "br", "col", "embed", "hr", "img", "input",
                  "link", "meta", "param", "source", "track", "wbr"))
TOPICS = {
    "WATER_SANITATION": r"\b(?:water|boil(?:ing)?|purif(?:y|ication)|chlorin(?:e|ation)|filter(?:ing)?|sewage)\b",
    "FOOD_STORAGE": r"\b(?:food|cann(?:ing|ed)|botulis(?:m|tic)|refrigerat(?:ed|ion)|freez(?:e|ing)|jerky)\b",
    "MEDICINE_HEALTH": r"\b(?:medicin(?:e|es)|medicat(?:ion|ions)|prescri(?:be|ption)|insulin|pharmac(?:ist|y)|infection|wound|dose|treatment)\b",
    "FIRE_CO_GENERATOR": r"\b(?:fire|smoke|generator|carbon monoxide|ventilat(?:ion|e)|gas leak|flame|fuel|stove|charcoal)\b",
    "EVACUATION_POWER": r"\b(?:evacuat(?:e|ion)|power outage|electric(?:ity|al)|battery|flood|earthquake|shelter)\b",
}
TOPIC_RX = {key: re.compile(pattern, re.I) for key, pattern in TOPICS.items()}


class ReviewHold(ValueError):
    """Invalid custody, changed citations or unauthorized release state."""


def need(ok, reason):
    if not ok:
        raise ReviewHold(reason)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
        separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest()


def raw_sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def is_sha(value):
    return type(value) is str and HEX64.fullmatch(value) is not None


class CitationDomAudit(HTMLParser):
    """Lexically map R68 citation offsets to HTML *data* and nearest blocks.

    DOM text classification is intentionally conservative. External styles,
    script behavior, responsive layouts and screen readers are NOT evaluated.
    """
    def __init__(self, html):
        super().__init__(convert_charrefs=False)
        self.html = html
        self.line_offsets = [0] + [i + 1 for i, c in enumerate(html) if c == "\n"]
        self.stack = []
        self.blocks = [{"block_id": "root", "tag": "root", "element_id": None,
                        "start_offset": 0, "text_parts": [], "citation_offsets": []}]
        self.by_offset = {}

    def _offset(self):
        line, column = self.getpos()
        need(0 < line <= len(self.line_offsets), "HTML parser line out of range")
        return self.line_offsets[line - 1] + column

    def _suppressed(self):
        return any(x["hidden"] for x in self.stack)

    def _block(self):
        return next((x["block"] for x in reversed(self.stack)
                     if x["block"] is not None), 0)

    def _start(self, tag, attrs, *, empty=False):
        attr = {k.lower(): v for k, v in attrs if k is not None}
        style = (attr.get("style") or "").lower()
        local_hidden = (tag in SUPPRESS or tag == "noscript" or
                        "hidden" in attr or "inert" in attr or
                        (attr.get("aria-hidden") or "").lower() == "true" or
                        bool(re.search(r"(?:^|;)\s*display\s*:\s*none(?:\s*!important)?\s*(?:;|$)", style)) or
                        bool(re.search(r"(?:^|;)\s*visibility\s*:\s*hidden(?:\s*!important)?\s*(?:;|$)", style)))
        hidden = self._suppressed() or local_hidden
        block_idx = None
        if tag in BLOCK:
            block_idx = len(self.blocks)
            self.blocks.append({"block_id": "block-" + str(block_idx), "tag": tag,
                "element_id": attr.get("id"), "start_offset": self._offset(),
                "text_parts": [], "citation_offsets": []})
        if not empty and tag not in VOID:
            self.stack.append({"tag": tag, "hidden": hidden, "block": block_idx})

    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs, empty=True)

    def handle_endtag(self, tag):
        for idx in range(len(self.stack) - 1, -1, -1):
            if self.stack[idx]["tag"] == tag:
                del self.stack[idx:]
                return

    def handle_data(self, data):
        at = self._offset()
        need(self.html[at:at + len(data)] == data,
             "HTML data offset not identical to unabridged source")
        hidden = self._suppressed()
        block_idx = self._block()
        if not hidden:
            self.blocks[block_idx]["text_parts"].append(data)
        for match in CITE.finditer(data):
            offset = at + match.start()
            need(offset not in self.by_offset, "duplicate parsed citation offset")
            self.by_offset[offset] = {
                "classification": "SUPPRESSED_OR_A11Y_HIDDEN_DOM_TEXT" if hidden
                                  else "DOM_TEXT_POTENTIALLY_VISIBLE_NOT_BROWSER_VERIFIED",
                "block_idx": block_idx if not hidden else None,
            }
            if not hidden:
                self.blocks[block_idx]["citation_offsets"].append(offset)


def construct(parent, *, expected=EXPECTED):
    """Pure machine triage. Only live_report() re-fetches pinned Git evidence."""
    need(type(expected) is tuple and len(expected) == 5 and
         all(type(x) is int and x >= 0 for x in expected) and expected[0] > 0
         and expected[1] > 0 and expected[2] > 0 and expected[3] > 0,
         "invalid source/citation count contract")
    need(type(parent) is dict and parent.get("schema") == PARENT_SCHEMA and
         parent.get("release_state") == "HOLD" and
         parent.get("machine_only") is True and
         all(parent.get(k) is False for k in HOLD) and
         is_sha(parent.get("fingerprint_sha256")) and
         digest({k:v for k,v in parent.items() if k != "fingerprint_sha256"}) ==
         parent["fingerprint_sha256"], "R68 sealed evidence or safety HOLD failed")
    counts = parent.get("counts")
    need(type(counts) is dict and tuple(counts.get(k) for k in
         ("original_articles_conserved", "candidate_tools",
          "original_citations_preserved_under_R66",
          "candidate_sources_conserved_under_R67",
          "RC_citation_occurrences_UNREVIEWED")) == expected and
         counts.get("human_source_or_claim_checks_performed_BY_R68") == 0,
         "R68 original/RC citation census or human-check claim changed")
    docs = parent.get("all_RC_document_and_source_review_tasks_UNABRIDGED_NOT_APPROVED")
    need(type(docs) is list and len(docs) == expected[0] + expected[1],
         "missing R68 original/candidate document review tasks")
    seen, urls, packet = set(), set(), []
    total = 0
    suppressed = 0
    non_text = 0
    candidates_with_unresolved = 0
    blocks_with_topics_and_no_local_citation = 0
    for task in sorted(docs, key=lambda x: (x.get("kind", ""), x.get("slug", ""))):
        need(type(task) is dict and is_sha(task.get("task_sha256")) and
             task["task_sha256"] == digest({k:v for k,v in task.items()
                                           if k != "task_sha256"}) and
             task.get("human_claim_review") == "NOT_REVIEWED" and
             task.get("human_source_review") == "NOT_REVIEWED" and
             task.get("qualified_safety_review") == "NOT_REVIEWED" and
             task.get("independent_QD_review") == "NOT_REVIEWED",
             "R68 document task fingerprint or human/safety review state changed")
        kind, slug = task.get("kind"), task.get("slug")
        url = task.get("proposed_WordPress_url_DRAFT_ONLY")
        body = task.get("RC_body_HTML_UNABRIDGED_NOT_SAFETY_CLEARED")
        citations = task.get("all_RC_citation_occurrences_NOT_CLAIM_SUPPORT")
        need(kind in ("article", "tool") and type(slug) is str and bool(slug)
             and slug not in seen and type(url) is str and url.startswith("/preparedness/")
             and url not in urls and type(body) is str and body and
             raw_sha(body) == task.get("RC_body_utf8_sha256") and
             type(citations) is list and
             task.get("RC_metadata_UNABRIDGED_NOT_SAFETY_CLEARED", {}).get("status", {}).get("publish") == "draft",
             "R68 document identity, URL, HTML or draft-only state changed")
        seen.add(slug)
        urls.add(url)
        observed = list(CITE.finditer(body))
        need(body.count("{{cite:") == len(observed) and len(citations) == len(observed),
             "R68 citation token count drift or malformed token")
        for index, (claim, match) in enumerate(zip(citations, observed), 1):
            need(type(claim) is dict and claim.get("ordinal") == index and
                 claim.get("source_id") == match.group(1) and
                 claim.get("unicode_codepoint_offset_in_candidate_html") == match.start() and
                 claim.get("exact_citation_token") == match.group(0) and
                 claim.get("human_claim_support") == "NOT_REVIEWED" and
                 type(claim.get("all_possible_origin_and_id_pairs_NOT_MERGED")) is list,
                 "R68 citation order/source/offset or human review changed")
        audit = CitationDomAudit(body)
        try:
            audit.feed(body)
            audit.close()
        except (ValueError, AssertionError) as exc:
            raise ReviewHold("invalid HTML citation audit: " + str(exc)) from exc
        issue_count = 0
        citation_rows = []
        for claim, match in zip(citations, observed):
            offset = match.start()
            found = audit.by_offset.get(offset)
            if found is None:
                category, block_index = "NON_DOM_TEXT_ATTRIBUTE_COMMENT_OR_TOKEN_SPLIT", None
                non_text += 1
                issue_count += 1
            else:
                category, block_index = found["classification"], found["block_idx"]
                if category != "DOM_TEXT_POTENTIALLY_VISIBLE_NOT_BROWSER_VERIFIED":
                    suppressed += 1
                    issue_count += 1
            citation_rows.append({
                "ordinal": claim["ordinal"], "source_id": match.group(1),
                "unicode_codepoint_offset": offset, "literal_token": match.group(0),
                "DOM_CLASSIFICATION_NOT_BROWSER_PROOF": category,
                "nearest_HTML_text_block_id_OR_NULL": (
                    audit.blocks[block_index]["block_id"] if block_index is not None else None),
                "candidate_source_identity_OR_NULL":
                    claim.get("scoped_candidate_source_identity_OR_NULL"),
                "all_source_identity_variants_NOT_ALIASED":
                    claim["all_possible_origin_and_id_pairs_NOT_MERGED"],
                "human_claim_support_review": "NOT_REVIEWED",
            })
        block_rows = []
        for block in audit.blocks:
            txt = "".join(block["text_parts"])
            if not txt.strip():
                continue
            topic_flags = sorted(k for k,rx in TOPIC_RX.items() if rx.search(txt))
            local = sorted(block["citation_offsets"])
            flags = []
            if topic_flags and not local:
                flags.append("TOPIC_SIGNAL_WITH_NO_CITATION_IN_THIS_DOM_BLOCK_REVIEW_CONTEXT")
                blocks_with_topics_and_no_local_citation += 1
            if topic_flags and local:
                flags.append("TOPIC_SIGNAL_WITH_CITATION_NOT_CLAIM_SUPPORT_PROOF")
            block_rows.append({
                "block_id": block["block_id"], "html_tag": block["tag"],
                "html_element_id_OR_NULL": block["element_id"],
                "start_offset_codepoints": block["start_offset"],
                "DOM_TEXT_UNABRIDGED_NOT_BROWSER_VERIFIED": txt,
                "DOM_text_sha256": raw_sha(txt),
                "citation_offsets_in_DOM_text": local,
                "review_topic_signals_NOT_SAFETY_CLASSIFICATION": topic_flags,
                "review_flags_NOT_SAFETY_VERDICTS": flags,
                "human_claim_support_review": "NOT_REVIEWED",
            })
        if issue_count:
            candidates_with_unresolved += 1
        total += len(citations)
        row = {
            "kind": kind, "slug":slug, "proposed_url_PRIVATE_DRAFT_ONLY":url,
            "R68_task_sha256":task["task_sha256"],
            "R68_HTML_sha256":task["RC_body_utf8_sha256"],
            "citation_visibility_audit_NOT_BROWSER_PROOF":citation_rows,
            "full_DOM_text_blocks_UNABRIDGED_NOT_SOURCE_APPROVED":block_rows,
            "R68_original_citation_and_reading_evidence_POINTER":parent["fingerprint_sha256"],
            "R68_prior_review_flags_NOT_CLEARED":task.get("review_flags_NOT_SAFETY_VERDICTS"),
            "unresolved_DOM_citation_count":issue_count,
            "human_source_review":"NOT_REVIEWED",
            "qualified_safety_review":"NOT_REVIEWED",
            "independent_QD_review":"NOT_REVIEWED",
        }
        row["task_sha256"] = digest(row)
        packet.append(row)
    need(len(seen) == expected[0] + expected[1] and total == expected[4],
         "R69 lost release-candidate documents or citation occurrences")
    result = {
        "schema":SCHEMA, "issue":136, "release_state":"HOLD", "machine_only":True,
        "R68_exact_original_RC_custody_fingerprint_sha256":parent["fingerprint_sha256"],
        "R68_parent_git_SHA":parent.get("RC_git_commit_sha256_NOT_RELEASE_APPROVAL"),
        "all_document_DOM_text_and_citation_review_orders_NOT_APPROVED":packet,
        "counts":{
            "candidate_articles":expected[0], "candidate_tools":expected[1],
            "original_citation_occurrences_kept_in_R68":expected[2],
            "candidate_source_records_kept_in_R68":expected[3],
            "candidate_citation_occurrences_accounted_for":total,
            "citations_in_potentially_visible_DOM_text":total - suppressed - non_text,
            "citations_in_suppressed_or_a11y_hidden_DOM_text":suppressed,
            "citations_outside_HTML_data_nodes":non_text,
            "documents_with_non_visible_or_non_text_citations":candidates_with_unresolved,
            "review_topic_blocks_without_same_block_citation":blocks_with_topics_and_no_local_citation,
            "human_claim_or_safety_checks_performed_BY_R69":0,
        },
        "limitations":(
            "HTMLParser establishes only text-node placement, not CSS visibility, "
            "screen-reader behavior or page render. Source identity scope is NOT "
            "equivalence or claim support. Keyword topic signals are fallible review "
            "triage, never safety findings. Full original/candidate HTML, all "
            "source-reading notes and research relationships stay frozen under R68 "
            "fingerprint. Qualified review, human link checks, independently "
            "approved custody re-baseline and QD remain missing; fail CLOSED."
        ),
        **{k: False for k in HOLD},
    }
    result["fingerprint_sha256"] = digest(result)
    return result


def csv_tasks(report):
    need(type(report) is dict and report.get("schema") == SCHEMA and
         report.get("release_state") == "HOLD" and
         report.get("machine_only") is True and
         all(report.get(k) is False for k in HOLD) and
         is_sha(report.get("fingerprint_sha256")) and
         report["fingerprint_sha256"] == digest({k:v for k,v in report.items()
             if k != "fingerprint_sha256"}), "unsigned or publish-cleared R69 task packet")
    sink = io.StringIO(newline="")
    writer = csv.writer(sink, lineterminator="\n")
    writer.writerow(["kind", "slug", "private_draft_url", "citation_offset",
        "citation_source_id", "DOM_classification_NOT_browser_proof",
        "nearest_block_id", "source_variants_NOT_aliased",
        "human_review_state", "review_notes_UNTRUSTED"])
    def neutral(value):
        value = "" if value is None else str(value)
        return "'" + value if value[:1] in ("\t", "\r", "\n") or value.lstrip().startswith(("=", "+", "-", "@")) else value
    for doc in report["all_document_DOM_text_and_citation_review_orders_NOT_APPROVED"]:
        for cite in doc["citation_visibility_audit_NOT_BROWSER_PROOF"]:
            writer.writerow([neutral(x) for x in (
                doc["kind"], doc["slug"], doc["proposed_url_PRIVATE_DRAFT_ONLY"],
                cite["unicode_codepoint_offset"], cite["source_id"],
                cite["DOM_CLASSIFICATION_NOT_BROWSER_PROOF"],
                cite["nearest_HTML_text_block_id_OR_NULL"],
                json.dumps(cite["all_source_identity_variants_NOT_ALIASED"], ensure_ascii=False),
                "NOT_REVIEWED", "")])
    return sink.getvalue()


def live_report(repo_root=None):
    parent = Path(__file__).with_name("r68_rc_document_citation_scope.py")
    need(parent.is_file() and not parent.is_symlink(), "R68 exact custody module absent")
    spec=importlib.util.spec_from_file_location("r69_pinned_parent_r68", parent)
    need(spec is not None and spec.loader is not None, "cannot load R68 custody")
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    root = Path(repo_root).resolve() if repo_root else Path(__file__).resolve().parents[2]
    parent_report=mod.live_report(root)
    report=construct(parent_report)
    need(report == construct(parent_report), "R69 report non-deterministic")
    return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--task-csv-stdout", action="store_true")
    args=parser.parse_args(argv)
    try:
        result=live_report(args.repo_root)
        if args.task_csv_stdout:
            sys.stdout.write(csv_tasks(result))
        else:
            print(json.dumps({"schema":SCHEMA,"release_state":"HOLD",
                 "fingerprint_sha256":result["fingerprint_sha256"],
                 "counts":result["counts"], "all_publication_clearance":False},sort_keys=True))
    except (ReviewHold, ValueError, KeyError, TypeError) as exc:
        print("R69 PRIVATE HOLD: "+str(exc),file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
