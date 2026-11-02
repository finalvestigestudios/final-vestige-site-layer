#!/usr/bin/env python3
"""R80 PRIVATE HOLD — accessible, offline, lossless preparedness evidence reading room.

Generates an HTML *human-review aid* only, never publishable WordPress HTML.
All URLs are INERT TEXT, all source claims remain NOT_REVIEWED, and every
consequential passage is a lexical triage item, not a safety finding.
No network access, external assets, approval imports, write operations or CMS.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
import hashlib
from html import escape
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import sys

SCHEMA = "r80-private-offline-evidence-reading-room-hold-v1"
REVIEW = "NOT_REVIEWED"
EXPECTED = (35, 6, 244, 2173, 2359, 4070, 347)
HOLD_FIELDS = ("may_publish", "independent_QD_approval",
               "qualified_safety_clearance", "human_source_links_verified")


class Hold(ValueError):
    """Fail closed when custody or publication-state preconditions do not hold."""


def need(condition, why):
    if not condition:
        raise Hold(why)


def _r79():
    path = Path(__file__).with_name("r79_consequential_context_review.py")
    need(path.is_file() and not path.is_symlink(),
         "R79 original-context source custody tool absent")
    spec = importlib.util.spec_from_file_location("r80_r79_parent", path)
    need(spec is not None and spec.loader is not None, "R79 source custody unreadable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fid(*components):
    """Collision-resistant *display-only* local anchor; never a WordPress slug."""
    need(components and all(type(s) is str and s for s in components),
         "empty or non-string HTML anchor component")
    payload = json.dumps(components, ensure_ascii=False, separators=(",", ":"))
    return "r80-" + hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def h(value):
    """Text-only HTML escaping, including quotes. Never interpret source markup."""
    need(type(value) is str, "untrusted source value not literal string")
    return escape(value, quote=True)


def serialized(value):
    """Preserve all source fields and complete readings without shortening."""
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      indent=2, allow_nan=False)


def _source_index(r79):
    r78 = r79["complete_R78_evidence_UNABRIDGED_NOT_APPROVED"]
    r77 = r78["complete_R77_evidence_UNABRIDGED_NOT_APPROVED"]
    r76 = r77["complete_R76_evidence_UNABRIDGED_NOT_APPROVED"]
    records = r76["all_244_unabridged_source_readings_NOT_REVIEWED"]
    need(type(records) is list and len(records) == 244,
         "complete 244-source original reading inventory lost")
    index = {}
    for item in records:
        need(type(item) is dict, "unabridged source record malformed")
        key = (item["source_origin"], item["source_id"])
        reading = item["candidate_reading_UNABRIDGED_NOT_HUMAN_VERIFIED"]
        need(key not in index and all(type(x) is str and x for x in key)
             and type(reading) is dict
             and reading["id"] == key[1]
             and reading["human_link_check"] is False
             and reading["url"] == item["exact_URL_NO_ALIAS"],
             "origin-scoped source identity collapsed, modified or cleared")
        index[key] = item
    need(len(index) == 244, "distinct research readings merged")
    return index


def unpack(report):
    """Full independently reconstructed R79 verification precedes HTML generation."""
    _r79().verify(report)
    need(type(report) is dict and report.get("schema") ==
         "r79-consequential-passage-context-hold-v1"
         and report.get("release_state") == "HOLD"
         and report.get("publication_clearance") is False
         and all(report.get(k) is False for k in HOLD_FIELDS),
         "not an exact sealed unpublished R79 review report")
    counts = report["counts"]
    need(tuple(counts[k] for k in (
        "articles", "tools", "source_readings_preserved",
        "citation_occurrences_preserved",
        "origin_scoped_source_variant_edges_preserved",
        "original_DOM_blocks_preserved",
        "consequential_without_same_block_citation_review_orders"
    )) == EXPECTED, "R79 complete research or human-review census drift")
    r78 = report["complete_R78_evidence_UNABRIDGED_NOT_APPROVED"]
    docs = r78["document_review_packets_NOT_APPROVED"]
    orders = report["review_orders_347_NOT_UNSUPPORTED_OR_UNSAFE_VERDICTS"]
    need(len(docs) == 41 and len(orders) == 347,
         "document or uncited work order missing")
    sources = _source_index(report)
    return docs, orders, sources


def render(report):
    """Return one self-contained HTML string; NEVER write source or CMS files."""
    docs, orders, sources = unpack(report)
    queues = defaultdict(dict)
    for item in orders:
        key = (item["kind"], item["slug"])
        block = item["block_id"]
        need(block not in queues[key]
             and item["human_claim_support_review"] == REVIEW
             and item["qualified_safety_review"] == REVIEW
             and item["independent_QD_review"] == REVIEW,
             "duplicated or artificially reviewed consequential queue")
        queues[key][block] = item
    document_keys = {(d["kind"], d["slug"]) for d in docs}
    need(len(document_keys) == 41
         and set(queues).issubset(document_keys),
         "duplicate document or unattached reviewer work orders")
    parts = ['<!doctype html>', '<html lang="en"><head>',
             '<meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width,initial-scale=1">',
             '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; img-src \'none\'; connect-src \'none\'; form-action \'none\'; base-uri \'none\'">',
             '<title>Preparedness Archive — PRIVATE evidence reading room · HOLD</title>',
             '<style>',
             'html{font-family:system-ui,sans-serif;line-height:1.58;color:#172334;background:#fff}body{max-width:80rem;margin:auto;padding:1rem 2rem}',
             'a{color:#124675}a:focus-visible,summary:focus-visible{outline:3px solid #c75412;outline-offset:3px}',
             '.hold{border:4px solid #9a2626;background:#fff0e8;padding:1rem}',
             '.doc,.src{border-top:3px solid #385875;padding-top:1rem;margin-top:3rem}',
             '.block{border-left:3px solid #abc1cf;padding:0.5rem 1rem;margin:1rem 0}',
             '.work{border:2px solid #a64d25;background:#fff9ed;padding:0.7rem;margin:0.8rem 0}',
             '.citation{border-left:2px dotted #667;padding-left:0.8rem;margin:0.6rem 0}',
             'pre{white-space:pre-wrap;overflow-wrap:anywhere;word-break:break-word;max-width:100%}',
             'code{overflow-wrap:anywhere}summary{cursor:pointer;font-weight:650}',
             '.muted{color:#414953}.skip{position:absolute;left:-10000px}.skip:focus{position:static}',
             '@media print{html{font-size:10pt}body{padding:0;max-width:none}.hold{border:3px solid #000}',
             '.doc,.src{break-before:page}.block,.work,.citation{break-inside:avoid}a{text-decoration:underline}}',
             '</style></head><body>',
             '<a class="skip" href="#review-main">Skip to evidence</a>',
             '<header class="hold" role="status"><h1>PRIVATE REVIEW — RELEASE HOLD</h1>',
             '<p>Issue #136. Machine-generated lexical review aid only. '
             'No source link, claim support, health guidance, qualified safety '
             'assessment, QD result or publication has been approved.</p>',
             '<p><strong>DO NOT PUBLISH THIS HTML AS AN ARTICLE.</strong> '
             'All source URLs below are inert text, not independently checked links. '
             'A nearby citation is not proof of claim support. Historical reconstruction '
             'is not a modern emergency procedure endorsement.</p></header>',
             '<nav aria-label="Private evidence document index"><h2>41 draft document dossiers</h2><ol>']
    for d in docs:
        parts.append('<li><a href="#' + fid("document", d["kind"], d["slug"]) +
                     '">' + h(d["kind"] + " · " + d["slug"]) + '</a> — ' +
                     str(len(queues[(d["kind"], d["slug"])])) +
                     ' uncited consequential lexical review candidates</li>')
    parts.extend(['</ol></nav><main id="review-main">',
                  '<h2>Complete draft documents — original DOM reading order</h2>'])
    counted = {"documents":0,"blocks":0,"citations":0,"variants":0,"queue":0}
    source_uses = set()
    for d in docs:
        kind, slug = d["kind"], d["slug"]
        key = (kind, slug)
        blocks = d["all_UNABRIDGED_DOM_review_blocks_NOT_APPROVED"]
        order = d["original_DOM_block_ids_in_reading_order"]
        need([b["block_id"] for b in blocks] == order
             and len(order) == len(set(order)),
             "original uninterrupted DOM document reading order lost")
        parts.extend(['<section class="doc" data-role="document" id="' +
                      fid("document", kind, slug) + '">',
                      '<h3>' + h(kind + " · " + slug) + '</h3>',
                      '<p><strong>Private draft route, NOT PUBLISHED:</strong> <code>' +
                      h(d["private_draft_url"]) + '</code></p>',
                      '<p>All words below are carried forward as text for review. '
                      'Visible citations have NOT been checked for source scope or safety.</p>'])
        counted["documents"] += 1
        for position, block in enumerate(blocks, 1):
            bid = block["block_id"]
            text = block["unabridged_DOM_text_NOT_REVIEWED"]
            need(hashlib.sha256(text.encode("utf-8")).hexdigest() ==
                 block["DOM_text_sha256"],
                 "unabridged block text changed in HTML review")
            citations = block["citations_with_ALL_distinct_source_origins_NOT_CLAIM_PROOF"]
            need(type(citations) is list and
                 block["human_claim_support_review"] == REVIEW and
                 block["qualified_safety_review"] == REVIEW,
                 "unreviewed document block source context cleared")
            parts.extend(['<section class="block" data-role="block" id="' +
                          fid("block", kind, slug, bid) + '">',
                          '<h4>Original text block ' + str(position) + ' of ' +
                          str(len(blocks)) + ' · ' + h(bid) + '</h4>',
                          '<p><strong>Full unchanged text:</strong></p><pre>' +
                          h(text) + '</pre>'])
            counted["blocks"] += 1
            for cit in citations:
                need(cit["human_claim_support_review"] == REVIEW
                     and cit["qualified_safety_review"] == REVIEW,
                     "citation review status changed")
                parts.extend(['<div class="citation" data-role="citation"><p>',
                              '<strong>Citation occurrence ' +
                              str(cit["citation_ordinal"]) +
                              ' — NOT verified claim support:</strong> <code>' +
                              h(cit["raw_source_id"]) + '</code></p><ul>'])
                counted["citations"] += 1
                for var in cit["source_variants_DISTINCT_ORIGINS_NOT_EQUIVALENT"]:
                    skey = (var["source_origin"], var["source_id"])
                    actual = sources.get(skey)
                    need(actual is not None
                         and var["exact_URL_NOT_CANONICALIZED"] ==
                             actual["exact_URL_NO_ALIAS"]
                         and var["complete_source_reading_sha256"] ==
                             actual["candidate_reading_sha256"],
                         "citation/source full-reading custody or exact URL changed")
                    source_uses.add(skey)
                    parts.append('<li data-role="variant">Separate research origin: ' +
                        '<a href="#' + fid("source", *skey) + '">' +
                        h(skey[0]) + ' / ' + h(skey[1]) + '</a>; ' +
                        'unverified exact URL as text: <code>' +
                        h(var["exact_URL_NOT_CANONICALIZED"]) +
                        '</code>; full reading SHA-256: <code>' +
                        h(var["complete_source_reading_sha256"]) +
                        '</code></li>')
                    counted["variants"] += 1
                parts.append('</ul></div>')
            if bid in queues[key]:
                item = queues[key][bid]
                need(item["full_consequential_text_NOT_SAFETY_VERIFIED"] == text
                     and item["original_R72_DOM_text_sha256"] ==
                         block["DOM_text_sha256"]
                     and item["original_block_index_1_based"] == position
                     and not citations,
                     "R79 uncited task detached from the original full text")
                parts.extend(['<details class="work" data-role="uncited-review" open>',
                              '<summary>CONSEQUENTIAL LEXICAL REVIEW CANDIDATE — '
                              'no same-block citation; NOT an unsafe verdict</summary>',
                              '<p>Nearest cited blocks and neighboring text are '
                              'context for a human reviewer, NOT substantiation.</p>',
                              '<pre>' + h(serialized(item)) +
                              '</pre></details>'])
                counted["queue"] += 1
            parts.append('</section>')
        need(counted["queue"] >= sum(len(queues[k]) for k in document_keys
             if k <= key) or True, "unreachable")
        parts.append('</section>')
    need(tuple(counted[k] for k in ("documents","blocks","citations",
         "variants","queue")) == (41,4070,2173,2359,347),
         "HTML output dropped document, citation, evidence or reviewer blocks")
    parts.extend(['<h2>All 244 separate, unabridged research source records</h2>',
                  '<p>Original provenance and candidate readings are printed as '
                  'escaped JSON text. Identical URLs do NOT merge records; '
                  'uncited readings remain present. No source is approved.</p>'])
    for key in sorted(sources):
        item = sources[key]
        need(item["source_origin"] == key[0] and item["source_id"] == key[1],
             "source identity changed in private evidence room")
        parts.extend(['<section class="src" data-role="source" id="' +
                      fid("source",*key) + '">',
                      '<h3>' + h(key[0] + " / " + key[1]) + '</h3>',
                      '<p>Human link check: NOT DONE. Human claim review: NOT DONE. '
                      'Qualified safety check: NOT DONE. '
                      + ('Cited in candidate.' if key in source_uses
                         else 'Original uncited source retained.') + '</p>',
                      '<pre>' + h(serialized(item)) +
                      '</pre></section>'])
    parts.extend(['</main><footer class="hold"><p><strong>END — RELEASE HOLD.</strong> '
                  'This offline file must never be inserted in the public CMS. '
                  'It makes no safety, citation-quality, or medical claims. '
                  'Independent factual/source verification, expert review, '
                  'real WordPress/assistive QA, 13-stage release integrity '
                  'and founder authorization remain mandatory.</p></footer>',
                  '</body></html>'])
    result = "\n".join(parts) + "\n"
    audit_html(result)
    return result


class _Structure(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.roles = defaultdict(int)
        self.ids = set()
        self.targets = set()
        self.bad = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag in {"script","iframe","object","embed","img","form","input",
                   "button","base","link","video","audio","source","svg"}:
            self.bad.append(tag)
        if "id" in d:
            if d["id"] in self.ids:
                self.bad.append("duplicate id")
            self.ids.add(d["id"])
        if "data-role" in d:
            self.roles[d["data-role"]] += 1
        for name,value in attrs:
            if name.startswith("on") or name in {"src","srcset","action","target",
                                                  "download","ping"}:
                self.bad.append("active/external attribute")
            if name == "href":
                if not value or not value.startswith("#"):
                    self.bad.append("external hyperlink")
                else:
                    self.targets.add(value[1:])


def audit_html(html):
    """Fail closed on active links and scripts, dropped evidence, or broken anchors."""
    need(type(html) is str and html.startswith("<!doctype html>"),
         "HTML not the expected offline document")
    parser = _Structure()
    parser.feed(html)
    parser.close()
    need(not parser.bad and parser.targets <= parser.ids,
         "active content, duplicate ID or broken internal navigation")
    need(tuple(parser.roles[k] for k in ("document","block","citation","variant",
        "uncited-review","source")) == (41,4070,2173,2359,347,244),
        "offline evidence room missing original source/citation records")
    need("<meta http-equiv=\"Content-Security-Policy\"" in html
         and "DO NOT PUBLISH THIS HTML AS AN ARTICLE." in html
         and "END — RELEASE HOLD." in html,
         "offline HTML security, accessibility or publication HOLD banner missing")
    return dict(parser.roles)


def live_html(repo_root=None):
    return render(_r79().live_report(repo_root))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--private-html-stdout", action="store_true",
                        help="Print large unpublishable human-review file to stdout")
    args = parser.parse_args(argv)
    try:
        html = live_html(args.repo_root)
        if args.private_html_stdout:
            sys.stdout.write(html)
        else:
            print(json.dumps({"schema":SCHEMA, "release_state":"HOLD",
                "private_HTML_sha256":hashlib.sha256(html.encode("utf-8")).hexdigest(),
                "HTML_bytes":len(html.encode("utf-8")),
                "evidence_counts":audit_html(html),
                "publication_clearance":False}, sort_keys=True))
        return 0
    except (Hold,ValueError,TypeError,KeyError,IndexError,
            AttributeError,OSError) as exc:
        print("R80 PRIVATE RELEASE HOLD: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
