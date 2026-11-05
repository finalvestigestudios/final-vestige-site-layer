"""R133: exercise the integrated 35-article reader-visible citation gate.

All reads are local, deterministic, and draft-only. The human-review state
must not be interpreted as scientific, medical, publishing, or QD approval.
"""
from __future__ import annotations

import pathlib
import re
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build
import validate
import r122_reader_visible_citation_gate as visibility

CITE = re.compile(r"\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}")


class ReleaseCandidateCitationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = build.Library()
        cls.by_number = {
            meta["n"]: meta for slug, meta in cls.lib.articles.items()
            if meta.get("kind") != "tool"
        }
        if set(cls.by_number) != set(range(1, 36)):
            raise AssertionError("Expected exactly 35 separately numbered article drafts")

    def check_article(self, n: int):
        meta = self.by_number[n]
        slug = meta["slug"]
        body = meta["_body"]
        result = visibility.check_body(body, slug)
        self.assertFalse(result["concealed"], f"{slug}: {result}")
        self.assertEqual(result["raw"], result["visible"], slug)
        self.assertGreater(len(result["visible"]), 0, slug)
        self.assertEqual(meta["status"]["publish"], "draft", slug)
        cited = set(result["raw"])
        self.assertFalse(cited - set(meta["source_use"]), f"{slug}: unexplained {cited - set(meta['source_use'])}")
        for sid in cited:
            self.assertIsInstance(meta["source_use"][sid], str, f"{slug}: {sid}")
            self.assertTrue(meta["source_use"][sid].strip(), f"{slug}: {sid}")
            self.assertEqual(self.lib.source_for(meta, sid)["id"], sid)

    def test_35_numbered_articles_only(self):
        self.assertEqual(len(self.by_number), 35)
        self.assertEqual(len({m["slug"] for m in self.by_number.values()}), 35)

    def test_existing_jerky_author_identity_is_held(self):
        meta = self.lib.articles["pemmican-and-dried-meats"]
        self.assertIn("hist-food-nchfp-jerky", visibility.check_body(meta["_body"], meta["slug"])["raw"])
        self.assertEqual(self.lib.source_for(meta, "hist-food-nchfp-jerky")["_origin"], "hist-food")

    def test_primary_validator_detects_concealed_in_memory_mutation(self):
        # Mutate the local Library object only; do not write any article file.
        lib = build.Library()
        article = lib.articles["pemmican-and-dried-meats"]
        original = article["_body"]
        try:
            article["_body"] += '<span hidden>{{cite:hist-food-nchfp-jerky}}</span>'
            errors, _ = validate.validate(lib)
            self.assertTrue(any("citation token not reader-visible" in e for e in errors), errors)
        finally:
            article["_body"] = original

    def test_primary_validator_rejects_malformed_citation(self):
        lib = build.Library()
        article = lib.articles["pemmican-and-dried-meats"]
        original = article["_body"]
        try:
            article["_body"] += "<p>{{cite:BAD ID}}</p>"
            errors, _ = validate.validate(lib)
            self.assertTrue(any("reader-visible citation integrity: MALFORMED_CITATION" in e
                                for e in errors), errors)
        finally:
            article["_body"] = original


def _test_article(n):
    def test(self):
        self.check_article(n)
    return test


# 35 independent numbered real-article checks (plus the 62 original R122
# synthetic cases). The overall tests remain UNVERIFIED until executed
# in a trusted complete checkout; defining tests does not constitute a pass.
for n in range(1, 36):
    setattr(ReleaseCandidateCitationTests, f"test_actual_article_{n:02d}", _test_article(n))


class ConservativeParserRegressions(unittest.TestCase):
    def test_visible_citation_in_figure_caption(self):
        r = visibility.check_body("<figure><figcaption>{{cite:source-one}}</figcaption></figure>", "fixture")
        self.assertEqual(r["visible"], ["source-one"])

    def test_hidden_inside_parent(self):
        r = visibility.check_body('<aside aria-hidden="true"><p>{{cite:source-one}}</p></aside>', "fixture")
        self.assertTrue(r["concealed"])

    def test_sibling_after_hidden_visible(self):
        r = visibility.check_body('<aside hidden>Hidden</aside><p>{{cite:source-one}}</p>', "fixture")
        self.assertFalse(r["concealed"])

    def test_same_id_visible_and_hidden_is_rejected(self):
        r = visibility.check_body('<p>{{cite:source-one}}</p><span hidden>{{cite:source-one}}</span>', "fixture")
        self.assertTrue(r["concealed"])

    def test_hidden_link_attribute(self):
        r = visibility.check_body('<a href="{{cite:source-one}}">Source</a>', "fixture")
        self.assertTrue(r["concealed"])

    def test_visible_table_cell(self):
        r = visibility.check_body('<table><tr><td>{{cite:source-one}}</td></tr></table>', "fixture")
        self.assertFalse(r["concealed"])

    def test_nested_hidden_then_visible(self):
        r = visibility.check_body('<div hidden><b>{{cite:source-one}}</b></div><p>{{cite:source-two}}</p>', "fixture")
        self.assertEqual(r["visible"], ["source-two"])

    def test_script_source_does_not_count(self):
        r = visibility.check_body('<script>const source="{{cite:source-one}}";</script>', "fixture")
        self.assertTrue(r["concealed"])


if __name__ == "__main__":
    unittest.main()
