"""R471 synthetic negative tests. Never writes the real checkout or CMS."""
from __future__ import annotations
from copy import deepcopy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "r471_exact_export_guard", ROOT / "tools/r471_wordpress_export_custody.py")
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)

class ExportCases(unittest.TestCase):
    def setUp(self):
        self.slugs = ["guide-%02d" % i for i in range(35)]
        self.body = (b"<!-- wp:html -->\n<div class='pa'>Draft: not public. "
                     b"Independent safety/source and QD verification pending. "
                     b"<span class='pa-src-use'>Scope: passage 2</span>"
                     b"<section class='pa-review'>Safety review pending</section>"
                     b"</div>\n<!-- /wp:html -->")
        self.expected = {}
        for slug in self.slugs:
            self.expected["wp/" + slug + ".html"] = self.body
            self.expected["preview/" + slug + ".html"] = self.body
        for kind in ("wp", "preview"):
            self.expected[kind + "/landing.html"] = b"private draft landing"
        self.actual = dict(self.expected)
        self.report = {
            "articles": [{"slug": s, "canonical":
                          "https://finalvestige.com/preparedness/shelter/" + s + "/"}
                         for s in self.slugs],
            "release_evidence": {"state": "HOLD",
                                 "independent_qa_verified": False,
                                 "wordpress_publication_performed": False},
        }

    def run_gate(self, expected=None, actual=None, report=None, slugs=None):
        return guard.audit_exports(
            self.expected if expected is None else expected,
            self.actual if actual is None else actual,
            self.report if report is None else report,
            self.slugs if slugs is None else slugs)

    def test_35_draft_outputs_are_only_structurally_checked(self):
        rec = self.run_gate()
        self.assertEqual(rec["articles_checked"], 35)
        self.assertEqual(rec["export_files_checked"], 72)
        self.assertFalse(rec["qualified_qd_pass"])
        self.assertFalse(rec["may_publish"])
        self.assertFalse(rec["wordpress_writes"])

    def test_duplicate_json_property_is_hard_hold(self):
        with self.assertRaises(guard.ExportHold):
            guard.strict_json('{"state":"HOLD","state":"QD_PASS"}')

    def test_nested_duplicate_json_property_is_hard_hold(self):
        with self.assertRaises(guard.ExportHold):
            guard.strict_json('{"report":{"state":1,"state":2}}')

    def test_missing_original_article(self):
        with self.assertRaises(guard.ExportHold):
            self.run_gate(slugs=self.slugs[:-1])

    def test_repeated_article_identity(self):
        with self.assertRaises(guard.ExportHold):
            self.run_gate(slugs=self.slugs[:-1] + [self.slugs[0]])

    def test_non_draft_claims_rejected(self):
        for claim in (b"QD PASS", b"Reviewed / safe", b"Published"):
            changed = {key: value.replace(b"Draft: not public", claim)
                       for key, value in self.expected.items()}
            with self.subTest(claim=claim), self.assertRaises(guard.ExportHold):
                self.run_gate(expected=changed, actual=changed)

    def test_release_claims_are_rejected(self):
        for field, value in (
            ("state", "READY"), ("state", "PUBLISHED"), ("state", "QD_PASS"),
            ("state", "REQUIRES_INDEPENDENT_QA"), ("state", None),
            ("independent_qa_verified", True), ("independent_qa_verified", "false"),
            ("wordpress_publication_performed", True),
            ("wordpress_publication_performed", "false"),
        ):
            altered = deepcopy(self.report)
            altered["release_evidence"][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(guard.ExportHold):
                self.run_gate(report=altered)

def isolate_missing_artifact(i):
    def test(self):
        changed = dict(self.actual)
        changed.pop("wp/" + self.slugs[i] + ".html")
        with self.assertRaises(guard.ExportHold):
            self.run_gate(actual=changed)
    return test

def isolate_byte_tamper(i):
    def test(self):
        changed = dict(self.actual)
        key = "preview/" + self.slugs[i] + ".html"
        changed[key] += b"<!-- silent extra content -->"
        with self.assertRaises(guard.ExportHold):
            self.run_gate(actual=changed)
    return test

def isolate_canonical_fork(i):
    def test(self):
        altered = deepcopy(self.report)
        altered["articles"][i]["canonical"] = altered["articles"][34]["canonical"]
        with self.assertRaises(guard.ExportHold):
            self.run_gate(report=altered)
    return test

for index in range(20):
    setattr(ExportCases, "test_missing_artifact_%02d" % index,
            isolate_missing_artifact(index))
    setattr(ExportCases, "test_tampered_preview_%02d" % index,
            isolate_byte_tamper(index))
for index in range(12):
    setattr(ExportCases, "test_duplicate_canonical_%02d" % index,
            isolate_canonical_fork(index))

if __name__ == "__main__":
    unittest.main()
