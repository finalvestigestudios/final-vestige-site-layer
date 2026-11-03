"""R100 in-memory adversarial tests; never write to source tree or CMS."""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import r100_printed_planner_context_custody as gate

FIELDS = ("wp-people", "wp-days", "wp-stored", "wp-filled",
          "wp-hot", "wp-pets", "wp-petgal", "wp-extra")
SOURCES = ("cdc-water-store", "ready-water", "ready-pets")
BODY = """<p>Print the result. Printing is the only way to retain the output.</p>
<form id="wp-form" class="pa-tool" onsubmit="return false">
<label for="wp-people">People</label><input id="wp-people" type="number">
<label for="wp-days">Days</label><input id="wp-days" type="number">
<label for="wp-stored">Stored</label><input id="wp-stored" type="number">
<label for="wp-filled">Date</label><input id="wp-filled" type="date">
<label for="wp-hot">Heat</label><input id="wp-hot" type="checkbox">
<label for="wp-pets">Pets</label><input id="wp-pets" type="number">
<label for="wp-petgal">Pet water</label><input id="wp-petgal" type="number">
<label for="wp-extra">Extra</label><input id="wp-extra" type="number">
<button type="button" id="wp-print">Print</button></form>
<div id="wp-out" class="pa-tool-out" role="status" aria-live="polite"></div>
<p>{{cite:cdc-water-store}} {{cite:ready-water}} {{cite:ready-pets}}</p>
<script>computeWaterPlan({}); out.innerHTML = ''; window.print();</script>"""
META = {"slug": "water-planner", "kind": "tool", "status": {"publish": "draft"},
        "safety_review": {"state": "pending"},
        "source_use": {s: "Original reading scope" for s in SOURCES}}

class StubCss:
    report = {"release_state": "HOLD", "may_publish": False,
              "calculator_hidden_on_print_REVIEW_REQUIRED": True}
    @classmethod
    def audit_stylesheet(cls, css):
        return cls.report


class R100(unittest.TestCase):
    def test_original_synthetic_inventory_holds(self):
        result = gate.audit(BODY, "synthetic-CSS", META, StubCss)
        self.assertEqual(result["hidden_print_assumption_fields"], sorted(FIELDS))
        self.assertEqual(result["cited_source_ids_NOT_HUMAN_VERIFIED"], sorted(SOURCES))
        self.assertEqual(result["source_citation_occurrences"], 3)
        self.assertEqual(result["release_state"], "HOLD")
        self.assertFalse(result["may_publish"])
        self.assertEqual(result["independent_QD"], "NOT_REVIEWED")
        self.assertEqual(result["sha256_seal"], gate.seal({k: v for k, v in result.items() if k != "sha256_seal"}))

    def test_deterministic_report_and_no_false_human_review(self):
        self.assertEqual(gate.audit(BODY, "a", META, StubCss),
                         gate.audit(BODY, "a", META, StubCss))
        out = gate.audit(BODY, "a", META, StubCss)
        self.assertEqual(out["qualified_water_and_medical_safety_review"], "NOT_REVIEWED")
        self.assertEqual(out["browser_print_verification"], "NOT_REVIEWED")

    def test_source_identity_whitespace_still_holds(self):
        out = gate.audit(BODY.replace("<p>{{cite", "<p> {{cite"), "a", META, StubCss)
        self.assertEqual(out["source_citation_occurrences"], 3)

    def test_custody_digest_changes_with_body(self):
        a = gate.audit(BODY, "a", META, StubCss)
        b = gate.audit(BODY.replace("People</label>", "Household people</label>"), "a", META, StubCss)
        self.assertNotEqual(a["sha256_seal"], b["sha256_seal"])

    def test_print_css_state_must_hold(self):
        original = StubCss.report
        try:
            for report in ({"release_state": "PASS", "may_publish": True,
                            "calculator_hidden_on_print_REVIEW_REQUIRED": True},
                           {"release_state": "HOLD", "may_publish": False,
                            "calculator_hidden_on_print_REVIEW_REQUIRED": False}):
                StubCss.report = report
                with self.assertRaises(gate.Hold):
                    gate.audit(BODY, "a", META, StubCss)
        finally:
            StubCss.report = original


def add_mutation(name, mutate):
    def test(self):
        body, meta = mutate(BODY, copy.deepcopy(META))
        with self.assertRaises(gate.Hold, msg=name):
            gate.audit(body, "synthetic-CSS", meta, StubCss)
    setattr(R100, "test_mutation_" + name, test)

for field in FIELDS:
    add_mutation("missing_field_" + field.replace("-", "_"),
                 lambda body, meta, f=field: (body.replace('id="' + f + '"', 'id="missing-' + f + '"'), meta))
    add_mutation("missing_label_" + field.replace("-", "_"),
                 lambda body, meta, f=field: (body.replace('for="' + f + '"', 'for="unknown-' + f + '"'), meta))
    add_mutation("duplicate_field_" + field.replace("-", "_"),
                 lambda body, meta, f=field: (body.replace('<button type="button"', '<input id="' + f + '"><button type="button"'), meta))

for source in SOURCES:
    add_mutation("missing_citation_" + source.replace("-", "_"),
                 lambda body, meta, s=source: (body.replace('{{cite:' + s + '}}', ''), meta))
    add_mutation("missing_source_scope_" + source.replace("-", "_"),
                 lambda body, meta, s=source: (body, {**meta, "source_use": {k:v for k,v in meta["source_use"].items() if k != s}}))

for name, old, new in (
    ("missing_form", '<form id="wp-form"', '<form id="not-wp-form"'),
    ("missing_form_class", 'class="pa-tool"', 'class="not-pa-tool"'),
    ("missing_result", 'id="wp-out"', 'id="gone"'),
    ("result_in_hidden_form", '</form>\n<div id="wp-out"', '<div id="wp-out"'),
    ("missing_result_role", 'role="status"', 'role="button"'),
    ("missing_result_live", 'aria-live="polite"', 'aria-live="off"'),
    ("missing_button", 'id="wp-print"', 'id="noprint"'),
    ("missing_print_call", 'window.print();', 'alert(1);'),
    ("missing_compute_call", 'computeWaterPlan({});', 'otherFn({});'),
    ("missing_output_render", 'out.innerHTML', 'out.otherProp'),
    ("lost_claim", 'Print the result', 'Do something else'),
    ("lost_print_promise", 'Printing is the only way', 'We store inputs'),
    ("duplicate_id", '<div id="wp-out"', '<div id="wp-form"'),
    ("nested_form", '<button type="button"', '<form><button type="button"'),
):
    add_mutation(name, lambda body, meta, o=old, n=new: (body.replace(o, n), meta))

for name, change in (
    ("published_state", {"status": {"publish": "published"}}),
    ("approved_state", {"safety_review": {"state": "approved"}}),
    ("wrong_slug", {"slug": "made-up-planner"}),
    ("wrong_kind", {"kind": "article"}),
    ("missing_reading_scope", {"source_use": {s: "" for s in SOURCES}}),
    ("unknown_source", {"source_use": {**META["source_use"], "other": "a"}}),
):
    add_mutation(name, lambda body, meta, c=change: (body, {**meta, **c}))

if __name__ == "__main__":
    unittest.main()
