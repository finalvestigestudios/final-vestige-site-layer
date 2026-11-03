#!/usr/bin/env python3
"""R100 private HOLD: audit water-planner print assumptions and source custody.

Static evidence only. It never claims a browser printed anything, that
calculator inputs/outputs were clinically validated, or that a page can ship.
No files are written, no network requests are made, and no CMS is contacted.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

SCHEMA = "r100-private-print-planner-context-custody-v1"
EXPECTED_FIELDS = frozenset({
    "wp-people", "wp-days", "wp-stored", "wp-filled", "wp-hot",
    "wp-pets", "wp-petgal", "wp-extra",
})
EXPECTED_SOURCES = frozenset({"cdc-water-store", "ready-water", "ready-pets"})
# Exact author-reviewed reading-scope text is frozen for this draft. Any edit
# requires a new human source/citation review, not a silent hash refresh.
EXPECTED_READING_SCOPE = {
    "cdc-water-store": (
        "The baseline of 1 gallon per person per day; 3 days minimum and 2 weeks as a goal; "
        "replace self-stored water every six months."
    ),
    "ready-water": (
        "The baseline; the statement that needs can double in very hot temperatures; "
        "the six-month replacement of non-commercial water."
    ),
    "ready-pets": (
        "That pets need several days' supply of water, with no quantity given, "
        "which is why pet and medical allowances are left for you to enter."
    ),
}


class Hold(ValueError):
    """The unreviewed print/source context has changed; stop the audit."""


def need(condition, why):
    if not condition:
        raise Hold(why)


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def seal(report):
    return sha(json.dumps(report, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":"), allow_nan=False))


class Nodes(HTMLParser):
    """Bounded, non-rendering HTML inventory: ids, tags, form and source labels."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids = {}
        self.forms = []
        self.form_depth = 0
        self.inputs = {}
        self.labels_for = set()
        self.nested_labels = set()
        self.label_depth = 0
        self.print_buttons = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if len(a) != len(attrs):
            self.errors.append("duplicate HTML attribute")
        node_id = a.get("id")
        if node_id is not None:
            if node_id in self.ids:
                self.errors.append("duplicate HTML id: " + node_id)
            self.ids[node_id] = (tag, a, self.form_depth)
        if tag == "label":
            self.label_depth += 1
        if tag == "form":
            if self.form_depth:
                self.errors.append("nested form")
            self.forms.append(a)
            self.form_depth += 1
        if tag == "input":
            if self.label_depth and node_id:
                self.nested_labels.add(node_id)
            if not node_id or node_id in self.inputs:
                self.errors.append("duplicate or missing input id")
            else:
                self.inputs[node_id] = (a, self.form_depth)
        if tag == "label" and a.get("for"):
            self.labels_for.add(a["for"])
        if tag == "button" and node_id == "wp-print":
            self.print_buttons.append((a, self.form_depth))

    def handle_endtag(self, tag):
        if tag == "label":
            self.label_depth -= 1
            if self.label_depth < 0:
                self.errors.append("unexpected closing label")
                self.label_depth = 0
        if tag == "form":
            self.form_depth -= 1
            if self.form_depth < 0:
                self.errors.append("unexpected closing form")
                self.form_depth = 0


def audit(body, css, meta, css_gate):
    need(type(body) is str and type(css) is str and type(meta) is dict,
         "source inputs must be full text and metadata")
    need(len(body.encode("utf-8")) < 100_000, "tool HTML exceeded audited size")
    need(meta.get("slug") == "water-planner" and meta.get("kind") == "tool",
         "wrong tool or incomplete tool metadata")
    need(meta.get("status", {}).get("publish") == "draft", "private draft state changed")
    need(meta.get("safety_review", {}).get("state") == "pending",
         "human safety review state changed; independently inspect")
    css_report = css_gate.audit_stylesheet(css)
    need(css_report.get("release_state") == "HOLD" and
         css_report.get("may_publish") is False,
         "R99 print source-safety gate must remain fail-closed")
    need(css_report.get("calculator_hidden_on_print_REVIEW_REQUIRED") is True,
         "print calculator visibility changed; static workorder no longer applies")
    p = Nodes()
    p.feed(body)
    p.close()
    need(not p.errors and p.form_depth == 0 and p.label_depth == 0,
         "invalid form/ids: " + ", ".join(p.errors))
    need(len(p.forms) == 1 and p.forms[0].get("id") == "wp-form" and
         "pa-tool" in p.forms[0].get("class", "").split(),
         "planner input form or print-hide selector changed")
    need(set(p.inputs) == EXPECTED_FIELDS,
         "water planner field identifiers changed: " + str(sorted(set(p.inputs) ^ EXPECTED_FIELDS)))
    need(all(depth == 1 for _, depth in p.inputs.values()),
         "one or more calculator inputs escaped print-hidden form")
    need(EXPECTED_FIELDS <= p.labels_for | p.nested_labels,
         "one or more inputs lost its label")
    need(len(p.print_buttons) == 1 and p.print_buttons[0][1] == 1,
         "print action not in hidden calculator form")
    need(p.ids.get("wp-out", (None, {}, 0))[0] == "div" and
         p.ids["wp-out"][2] == 0 and
         "pa-tool-out" in p.ids["wp-out"][1].get("class", "").split(),
         "dynamic plan output no longer appears outside hidden form")
    need(p.ids["wp-out"][1].get("role") == "status" and
         p.ids["wp-out"][1].get("aria-live") == "polite",
         "dynamic results accessibility state changed")
    need("window.print()" in body and "computeWaterPlan(" in body and
         "out.innerHTML" in body, "calculator/print wiring changed; re-review required")
    cited = re.findall(r"\{\{cite:([a-z0-9-]+)\}\}", body)
    need(set(cited) == EXPECTED_SOURCES and len(cited) >= len(EXPECTED_SOURCES),
         "original planner citation bindings changed")
    uses = meta.get("source_use", {})
    need(type(uses) is dict and set(uses) == EXPECTED_SOURCES and
         all(isinstance(v, str) and v.strip() for v in uses.values()),
         "original planner per-source reading scope changed")
    need(uses == EXPECTED_READING_SCOPE,
         "source reading depth/claim scope changed; independent review required")
    need("Print the result" in body and "Printing is the only way" in body,
         "original print affordance/copy changed; re-review required")
    report = {
        "schema": SCHEMA, "issue": 136,
        "release_state": "HOLD", "may_publish": False,
        "human_source_claim_review": "NOT_REVIEWED",
        "qualified_water_and_medical_safety_review": "NOT_REVIEWED",
        "independent_QD": "NOT_REVIEWED",
        "browser_print_verification": "NOT_REVIEWED",
        "original_tool_html_sha256": sha(body),
        "original_print_css_sha256": sha(css),
        "source_reading_scope_sha256": seal(uses),
        "cited_source_ids_NOT_HUMAN_VERIFIED": sorted(set(cited)),
        "source_citation_occurrences": len(cited),
        "hidden_print_assumption_fields": sorted(EXPECTED_FIELDS),
        "assumption_field_count": len(EXPECTED_FIELDS),
        "computed_output_is_JS_generated_NOT_PRINT_TESTED": True,
        "form_inputs_hidden_in_print": True,
        "computed_result_container_outside_hidden_form": True,
        "print_context_workorder_NOT_APPROVED": (
            "The existing @media print stylesheet hides all eight user inputs "
            "inside .pa-tool, while the computed #wp-out results remain outside "
            "that form. Printed totals may not identify the household, heat, pet, "
            "medical, stored-water and date assumptions used. Verify actual "
            "browser print and whether a printable assumption summary is required "
            "before any publication or safety signoff. Do not infer medical safety."
        ),
    }
    report["sha256_seal"] = seal(report)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--private-json-stdout", action="store_true")
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "tools"))
    import build
    import r98_print_source_visibility_custody as css_gate
    import r93_rendered_citation_fidelity as r93
    import r94_body_custody as r94
    import r95_dom_attribute_custody as r95
    import r96_visible_source_safety_shell as r96
    import r97_structured_data_route_custody as r97
    lib = build.Library()
    previous = css_gate.audit_library(lib, build.build_article,
                                      r97.audit_library, r96.audit_library,
                                      r95.audit_library, r93.audit_document, r94.audit_body)
    need(previous["protected_article_drafts"] == 35 and
         previous["protected_real_tool_drafts"] == 1,
         "35+1 private draft inventory changed")
    result = audit(lib.articles["water-planner"]["_body"], lib.css,
                   lib.articles["water-planner"], css_gate)
    result["prior_36_draft_custody_seal"] = previous["sha256_seal"]
    result["sha256_seal"] = seal({k: v for k, v in result.items() if k != "sha256_seal"})
    print(json.dumps(result, sort_keys=True) if args.private_json_stdout else
          json.dumps({"schema": SCHEMA, "release_state": "HOLD", "may_publish": False,
                      "source_citation_occurrences": result["source_citation_occurrences"],
                      "hidden_print_assumption_fields": result["hidden_print_assumption_fields"],
                      "sha256_seal": result["sha256_seal"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Hold, ValueError, KeyError, OSError) as exc:
        print(json.dumps({"schema": SCHEMA, "release_state": "HOLD",
                          "may_publish": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
