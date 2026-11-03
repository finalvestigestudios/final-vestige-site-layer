"""R101 synthetic, corpus, private rendering and JS-state regression tests.

All mutations are in memory; no repository/CMS/network writes occur.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build
import r98_print_source_visibility_custody as css_gate
import r100_printed_planner_context_custody as baseline
import r101_water_print_context_private_candidate as gate


class R101(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()
        cls.original = cls.lib.articles["water-planner"]["_body"]
        cls.meta = cls.lib.articles["water-planner"]
        cls.css = cls.lib.css

    def candidate(self):
        return gate.build_candidate(self.lib, build, baseline, css_gate)

    def test_actual_source_corpus_before_candidate(self):
        body, report = gate.assess(self.lib, baseline, css_gate)
        self.assertEqual(body, self.original)
        self.assertEqual(len(report["hidden_print_assumption_fields"]), 8)
        self.assertEqual(report["cited_source_ids_NOT_HUMAN_VERIFIED"],
                         ["cdc-water-store", "ready-pets", "ready-water"])
        self.assertEqual(report["release_state"], "HOLD")
        self.assertFalse(report["may_publish"])

    def test_candidate_renders_both_private_types(self):
        wp, preview, receipt = self.candidate()
        self.assertIn("<!-- wp:html -->", wp)
        self.assertIn('id="wp-print-context"', wp)
        self.assertIn('id="wp-print-context"', preview)
        self.assertIn("Safety review pending", wp)
        self.assertIn("Draft: not public", wp)
        self.assertIn("PRIVATE PRINT REVIEW", preview)
        self.assertIn("NOT_REVIEWED", wp)
        self.assertEqual(receipt["release_state"], "HOLD")
        self.assertFalse(receipt["may_publish"])
        self.assertFalse(receipt["wordpress_import_authorized"])
        self.assertEqual(receipt["human_source_claim_review"], "NOT_REVIEWED")
        self.assertEqual(receipt["qualified_water_and_medical_safety_review"], "NOT_REVIEWED")
        self.assertEqual(receipt["actual_browser_print_qa"], "NOT_REVIEWED")
        self.assertEqual(receipt["independent_QD"], "NOT_REVIEWED")

    def test_original_is_untouched_after_private_build(self):
        before = self.original
        before_meta = copy.deepcopy(self.meta)
        self.candidate()
        self.assertEqual(self.lib.articles["water-planner"]["_body"], before)
        self.assertEqual(self.lib.articles["water-planner"], before_meta)

    def test_deterministic_candidate_and_receipt(self):
        a = self.candidate()
        b = self.candidate()
        self.assertEqual(a, b)
        self.assertEqual(a[2]["sha256_seal"],
                         gate.digest(gate.canonical({k: v for k, v in a[2].items()
                                                     if k != "sha256_seal"})))

    def test_all_original_citations_and_navigation_survive(self):
        wp, preview, receipt = self.candidate()
        self.assertEqual(receipt["original_citation_occurrences"], 6)
        self.assertEqual(receipt["candidate_citation_occurrences"], 6)
        self.assertEqual(receipt["eight_assumptions"], [x[0] for x in gate.FIELDS])
        self.assertIn("cdc-water-store", self.original)
        self.assertIn("ready-pets", self.original)
        self.assertIn("Source 1:", wp)
        self.assertIn("Source 2:", wp)
        self.assertIn("Source 3:", wp)
        self.assertIn("No calculation is available without JavaScript", preview)
        self.assertEqual(gate.patch_body(self.original).count("{{cite:"),
                         self.original.count("{{cite:"))

    def test_original_content_is_still_subsequence_with_one_insertion(self):
        modified = gate.patch_body(self.original)
        restored = modified.replace(gate.ANCHOR + gate.markup(), gate.ANCHOR)
        restored = restored.split("\n<!-- " + gate.SENTINEL + " -->", 1)[0]
        self.assertEqual(restored, self.original)

    def test_static_print_visibility_reviewer_boundary(self):
        wp, preview, receipt = self.candidate()
        for token in ('@media screen', '@media print', 'display: block !important',
                      "beforeprint", "addEventListener('input'",
                      "addEventListener('change'", "textContent = format",
                      'data-r101-status="NOT_REVIEWED"',
                      "No calculation is available without JavaScript"):
            self.assertIn(token, preview)
        self.assertNotIn("localStorage", gate.SCRIPT)
        self.assertNotIn("sessionStorage", gate.SCRIPT)
        self.assertNotIn("XMLHttpRequest", gate.SCRIPT)
        self.assertNotIn("sendBeacon", gate.SCRIPT)
        self.assertNotIn("fetch(", gate.SCRIPT)
        self.assertNotIn("innerHTML", gate.SCRIPT)
        self.assertNotIn("Date.now()", gate.SCRIPT)

    def test_eight_labels_and_fields_one_to_one(self):
        candidate = gate.patch_body(self.original)
        inv = gate.Inventory()
        inv.feed(candidate)
        inv.close()
        self.assertEqual(inv.values, [f[0] for f in gate.FIELDS])
        self.assertEqual(inv.review_marks, 2)
        self.assertEqual(inv.scripts, 2)
        for field, label, _kind, _max in gate.FIELDS:
            self.assertIn(label, candidate)
            self.assertEqual(candidate.count('data-r101-value="' + field + '"'), 1)

    def test_print_isolation_and_no_wordpress_or_main_page_write(self):
        with tempfile.TemporaryDirectory() as temp:
            # Writing ONLY under caller-provided /tmp, not the source repository.
            result = subprocess.run(
                [sys.executable, "-I", str(ROOT / "tools" /
                 "r101_water_print_context_private_candidate.py"), "--out-dir", temp],
                cwd=ROOT, capture_output=True, text=True, check=True)
            receipt = json.loads(result.stdout)
            self.assertEqual(len(list(Path(temp).iterdir())), 3)
            for path in Path(temp).iterdir():
                self.assertIn("R101-", path.name)
                self.assertTrue(path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["release_state"], "HOLD")
            self.assertFalse(receipt["wordpress_import_authorized"])

    def test_scratch_output_refuses_preexisting_file_without_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            existing = Path(temp) / "water-planner-R101-PRIVATE-DRAFT.html"
            existing.write_text("prior independent review", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-I", str(ROOT / "tools" /
                 "r101_water_print_context_private_candidate.py"), "--out-dir", temp],
                cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(existing.read_text(encoding="utf-8"),
                             "prior independent review")
            self.assertIn("refusing to overwrite", result.stderr)

    def test_scratch_directory_symlink_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / "real"
            destination.mkdir()
            shortcut = Path(temp) / "link"
            try:
                shortcut.symlink_to(destination, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlinks prohibited by this platform")
            with self.assertRaises(gate.Hold):
                gate.safe_output_dir(str(shortcut))

    def test_inspect_only_produces_no_artifact(self):
        result = subprocess.run(
            [sys.executable, "-I", str(ROOT / "tools" /
             "r101_water_print_context_private_candidate.py"), "--inspect-only"],
            cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)["release_state"], "HOLD")

    def test_repository_output_path_rejected(self):
        with self.assertRaises(gate.Hold):
            gate.safe_output_dir(str(ROOT / "build" / "r101"))
        with self.assertRaises(gate.Hold):
            gate.safe_output_dir(str(ROOT))
        with self.assertRaises(gate.Hold):
            gate.safe_output_dir(str(ROOT.parent))

    def test_node_runtime_tracks_changes_before_print_without_storage(self):
        if not shutil.which("node"):
            self.skipTest("Node absent; hosted CI must execute this test")
        js = gate.SCRIPT.split("<script", 1)[1].split(">", 1)[1].split("</script>", 1)[0]
        harness = r"""
const vm = require('vm'), assert = require('assert/strict');
const script = SCRIPT_LITERAL;
let beforePrint = null;
const names = ['wp-people', 'wp-days', 'wp-stored', 'wp-filled',
               'wp-hot', 'wp-pets', 'wp-petgal', 'wp-extra'];
const entries = new Map();
const defaults = ['4', '3', '', '', '', '', '', ''];
names.forEach((id, i) => {
  entries.set(id, {
    id, value: defaults[i], checked: false,
    handlers: {}, addEventListener(name, fn) { this.handlers[name] = fn; }
  });
});
let touched = {};
const box = { querySelector(sel) {
  const match = /^\[data-r101-value="(wp-[a-z]+)"\]$/.exec(sel);
  if (!match) throw Error('untrusted selector: ' + sel);
  if (!touched[match[1]]) touched[match[1]] = { textContent: '' };
  return touched[match[1]];
}};
const form = { contains(input) { return entries.get(input.id) === input; } };
const warning = {textContent: ''};
const document = { getElementById(id) {
  if (id === 'wp-print-context') return box;
  if (id === 'wp-form') return form;
  if (id === 'wp-print-context-pending') return warning;
  return entries.get(id);
}};
const window = { addEventListener(name, fn) {
  if (name === 'beforeprint') beforePrint = fn;
}};
const context = { document, window, Number, Math };
vm.runInNewContext(script, context, { timeout: 500 });
assert.equal(touched['wp-people'].textContent, '4');
assert.equal(touched['wp-days'].textContent, '3');
assert.equal(touched['wp-stored'].textContent, 'Not supplied (calculator uses zero)');
assert.equal(touched['wp-hot'].textContent, 'No');
assert.equal(touched['wp-filled'].textContent, 'Not supplied');
assert.ok(warning.textContent.includes('Not a verification'));
entries.get('wp-hot').checked = true;
entries.get('wp-hot').handlers.change();
assert.equal(touched['wp-hot'].textContent, 'Yes');
entries.get('wp-people').value = '127';
entries.get('wp-people').handlers.input();
assert.equal(touched['wp-people'].textContent, '100 (calculator limit/rounding applied)');
entries.get('wp-pets').value = '2.6';
entries.get('wp-pets').handlers.change();
assert.equal(touched['wp-pets'].textContent, '3 (calculator limit/rounding applied)');
entries.get('wp-petgal').value = '<img src=x onerror=alert(1)>';
entries.get('wp-petgal').handlers.input();
assert.equal(touched['wp-petgal'].textContent, 'Invalid entry: calculator uses zero');
entries.get('wp-filled').value = '2026-11-03';
entries.get('wp-stored').value = '25.5';
beforePrint();
assert.equal(touched['wp-filled'].textContent, '2026-11-03');
assert.equal(touched['wp-stored'].textContent, '25.5');
assert.equal(Object.keys(touched).length, 8);
console.log('R101 eight-field private DOM snapshot, clamping, and print event PASS');
"""
        harness = harness.replace("SCRIPT_LITERAL", json.dumps(js))
        result = subprocess.run(["node", "-e", harness], capture_output=True,
                                text=True, check=True)
        self.assertIn("PASS", result.stdout)


def add_bad_source_mutation(name, mutate):
    def test(self):
        original = self.lib.articles["water-planner"]["_body"]
        meta = self.lib.articles["water-planner"]
        oldmeta = copy.deepcopy(meta)
        try:
            b, m = mutate(original, copy.deepcopy(meta))
            self.lib.articles["water-planner"] = m
            self.lib.articles["water-planner"]["_body"] = b
            with self.assertRaises((gate.Hold, baseline.Hold, ValueError),
                                   msg=name):
                self.candidate()
        finally:
            self.lib.articles["water-planner"] = meta
            meta.clear()
            meta.update(oldmeta)
    setattr(R101, "test_failclosed_" + name, test)


for field in (x[0] for x in gate.FIELDS):
    safe = field.replace("-", "_")
    add_bad_source_mutation(
        "missing_input_" + safe,
        lambda b, m, f=field: (b.replace('id="' + f + '"', 'id="wrong-' + f + '"'), m))
    add_bad_source_mutation(
        "lost_label_" + safe,
        lambda b, m, f=field: (b.replace('for="' + f + '"', 'for="unknown-' + f + '"'), m))
    add_bad_source_mutation(
        "duplicate_input_" + safe,
        lambda b, m, f=field: (b.replace('<button type="button" class="pa-btn" id="wp-print">',
                                     '<input id="' + f + '">' +
                                     '<button type="button" class="pa-btn" id="wp-print">'), m))

for source in ("cdc-water-store", "ready-water", "ready-pets"):
    add_bad_source_mutation(
        "missing_citation_" + source.replace("-", "_"),
        lambda b, m, s=source: (b.replace("{{cite:" + s + "}}", ""), m))
    add_bad_source_mutation(
        "wrong_reading_scope_" + source.replace("-", "_"),
        lambda b, m, s=source: (b, {**m, "source_use": {
            **m["source_use"], s: "This source verifies the entire personalized medical plan."}}))

for name, old, new in (
    ("missing_original_print_boundary", gate.ANCHOR, ""),
    ("duplicate_original_print_boundary", gate.ANCHOR, gate.ANCHOR * 2),
    ("script_boundary_injection", "</script>", "</script><script>alert(1)</script>"),
    ("preinjected_candidate", gate.ANCHOR, gate.ANCHOR + '<div id="wp-print-context"></div>'),
    ("lost_printing_language", "Printing is the only way", "Background cloud sync"),
    ("altered_compute", "computeWaterPlan(", "fakeCompute("),
    ("altered_render", "out.innerHTML", "out.otherProp"),
    ("tampered_source_metadata", "Print the result", "Other action"),
):
    add_bad_source_mutation(name, lambda b, m, o=old, n=new: (b.replace(o, n), m))

for name, key, value in (
    ("published_without_review", "status", {"publish": "published"}),
    ("safety_premature_approval", "safety_review", {"state": "approved"}),
    ("wrong_kind", "kind", "article"),
    ("wrong_slug", "slug", "other-tool"),
):
    add_bad_source_mutation(name, lambda b, m, k=key, v=value: (b, {**m, k: v}))


if __name__ == "__main__":
    unittest.main()
