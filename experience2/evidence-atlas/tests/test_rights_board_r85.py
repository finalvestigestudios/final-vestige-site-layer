#!/usr/bin/env python3
"""Adversarial, offline custody gates for the R85 review board."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

BUILDER = Path(__file__).resolve().parents[1] / "tools/build_rights_board_r85.py"
spec = importlib.util.spec_from_file_location("build_rights_board_r85", BUILDER)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class ReviewBoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = module.load_sources()

    def mutated(self):
        return copy.deepcopy(self.original)

    def must_fail(self, docs):
        with self.assertRaisesRegex(ValueError, "R85_SOURCE_HOLD"):
            module.verify(docs)

    def test_canonical_six_sources_and_pending_rights(self):
        r = module.verify(self.mutated())
        self.assertEqual(tuple(x["id"] for x in r), module.IDS)
        self.assertTrue(all(x["url"].startswith("https://www.nasa.gov/image-detail/") for x in r))
        self.assertEqual(r[0]["precision"], "MONTH_ONLY")
        self.assertEqual(r[0]["identity"], "PROVISIONAL_NO_PAGE_PIA")
        self.assertEqual(r[3]["date"], r[5]["date"])

    def test_canonical_source_git_blob_pins(self):
        for key, (path, expected) in module.SOURCES.items():
            self.assertEqual(module.git_blob((module.ROOT / path).read_bytes()), expected)

    def test_reproduction_marked_cleared_rejected(self):
        d=self.mutated()
        d["nasa"]["records"][3]["reuse_status"]="CLEARED"
        self.must_fail(d)

    def test_review_counter_fake_approval_rejected(self):
        d=self.mutated()
        d["nasa"]["reusable_media_assessments_completed"]=1
        self.must_fail(d)

    def test_unreviewed_photo_binary_rejected(self):
        d=self.mutated()
        d["rights"]["records"][0]["downloaded_or_embedded"]=True
        self.must_fail(d)

    def test_crosswalk_media_status_change_rejected(self):
        d=self.mutated()
        d["crosswalk"]["records"][5]["media_rights"]="APPROVED"
        self.must_fail(d)

    def test_malicious_nasa_lookalike_domain_rejected(self):
        d=self.mutated()
        new="https://www.nasa.gov.evil.test/image-detail/anything/"
        for key,field in (("crosswalk","photo_url"),("nasa","nasa_url"),("rights","nasa_page")):
            d[key]["records"][2][field]=new
        self.must_fail(d)

    def test_nasa_query_or_fragment_mutation_rejected(self):
        for suffix in ("?utm_source=unknown","#tampered"):
            d=self.mutated()
            for key,field in (("crosswalk","photo_url"),("nasa","nasa_url"),("rights","nasa_page")):
                d[key]["records"][2][field]+=suffix
            self.must_fail(d)

    def test_crew_month_only_must_not_be_fabricated_day(self):
        d=self.mutated()
        d["nasa"]["records"][0]["date_precision"]="DAY"
        d["nasa"]["records"][0]["taken_date"]="1967-01-12"
        d["crosswalk"]["records"][0]["date"]="1967-01-12"
        self.must_fail(d)

    def test_crew_provisional_pia_must_not_be_confirmed(self):
        d=self.mutated()
        d["nasa"]["records"][0]["identity_status"]="PIA_ON_OFFICIAL_PAGE"
        d["nasa"]["records"][0]["nasa_page_pia"]="S67-19766"
        self.must_fail(d)

    def test_photo_identity_swap_rejected(self):
        d=self.mutated()
        d["nasa"]["records"][1],d["nasa"]["records"][2] = (
            d["nasa"]["records"][2],d["nasa"]["records"][1])
        self.must_fail(d)

    def test_same_day_2017_cannot_be_sequenced(self):
        d=self.mutated()
        d["nasa"]["records"][5]["date_display"]="January 25, 2017"
        self.must_fail(d)

    def test_map_or_embedded_image_policy_cannot_shift(self):
        for field in ("images_embedded","geographic_pins","speculative_edges"):
            d=self.mutated()
            d["nasa"][field]=1
            self.must_fail(d)

    def test_url_validator_blocks_credentials_and_port(self):
        for value in ("https://www.nasa.gov@attacker.com/image-detail/hi",
                      "https://www.nasa.gov:444/image-detail/hi",
                      "http://www.nasa.gov/image-detail/hi",
                      "https://www.nasa.gov/search/",
                      "https://www.nasa.gov/image-detail/a?token=x"):
            self.assertFalse(module.nasa_url(value), value)

    def test_markup_accessible_without_js_or_external_images(self):
        m=module.markup(module.verify(self.mutated()))
        self.assertEqual(m.count('<article class="card"'),6)
        self.assertEqual(m.count('<details>'),6)
        self.assertEqual(m.count('<summary>'),6)
        self.assertEqual(m.count('class="buttonlink"'),6)
        self.assertNotIn("<script",m)
        self.assertNotIn("<img",m)
        self.assertNotIn("data-lat",m)
        self.assertIn("noindex,nofollow",m)
        self.assertIn("provisional",m)

    def test_deterministic_twice_and_receipt_custody(self):
        with tempfile.TemporaryDirectory() as one, tempfile.TemporaryDirectory() as two:
            a,b=Path(one),Path(two)
            first=module.build(a,self.mutated())
            second=module.build(b,self.mutated())
            self.assertEqual(first,second)
            for name in ("R85_NASA_SOURCE_REVIEW.html","R85_RIGHTS_RECEIPT.json",
                         "rights_board_r85.css"):
                self.assertEqual((a/name).read_bytes(),(b/name).read_bytes())
            self.assertEqual(first["rights_cleared"],0)
            self.assertEqual(first["images_embedded"],0)
            self.assertFalse(first["release_approved"])
            self.assertEqual(first["html_sha256"],
                hashlib.sha256((a/"R85_NASA_SOURCE_REVIEW.html").read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
