"""R89 release-review integration contracts. No publication pathway."""
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

BUILDER = Path(__file__).resolve().parents[1] / "tools/build_review_hub_r89.py"
spec = importlib.util.spec_from_file_location("r89_tests", BUILDER)
r89 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r89)

class IntegratedReviewContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = tempfile.TemporaryDirectory()
        cls.output = Path(cls.work.name) / "built"
        cls.receipt = r89.build(cls.output)
        cls.board = r89.module("build_rights_board_r85.py", "r85_r89_test")
        cls.urls = {r["url"] for r in cls.board.verify(cls.board.load_sources())}
        r88 = r89.module("build_reading_room_r88.py", "r88_r90_tests")
        _, report, _, _ = r88.verified_records()
        cls.records = report["records"]
    @classmethod
    def tearDownClass(cls):
        cls.work.cleanup()


    def _mutate_card(self, page, modify, expected):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "review"
            shutil.copytree(self.output, target)
            file = target / page
            original = file.read_text("utf8")
            changed = modify(original)
            self.assertNotEqual(original, changed, "Mutation must be effective")
            file.write_text(changed, encoding="utf8")
            with self.assertRaisesRegex(ValueError, expected):
                r89.audit_source_bindings(target, self.records)

    def test_r90_card_scoped_link_custody_all_24_bindings(self):
        result = r89.audit_source_bindings(self.output, self.records)
        self.assertEqual(len(result), 24)
        for page, prefix in (("R89_REVIEW_HUB.html", "r89-source-"),
                             ("R88_READING_ROOM.html", "r88-"),
                             ("R87_PHOTOGRAPH_DATE_RAIL.html", "r87-record-"),
                             ("R85_NASA_SOURCE_REVIEW.html", "r85-source-")):
            for source in self.records:
                self.assertEqual(result[page + "#" + prefix + source["id"]]["record"],
                                 source["id"])
        self.assertEqual(self.receipt["record_source_bindings"], result)
        self.assertEqual(self.receipt["source_urls_by_id"],
                         {r["id"]: r["url"] for r in self.records})

    def test_r90_swapped_official_nasa_links_rejected_in_all_four_surfaces(self):
        # Both destinations remain genuine NASA URLs, so the old aggregate
        # six-URL set check passed. Each record now fails its own custody check.
        first, second = [r["url"] for r in self.records[:2]]
        for page in r89.PAGES:
            def swap(contents):
                marker = 'href="' + first + '"'
                other = 'href="' + second + '"'
                return contents.replace(marker, 'href="R90-TEMP"', 1).replace(
                    other, marker, 1).replace('href="R90-TEMP"', other, 1)
            with self.subTest(page=page):
                self._mutate_card(page, swap, "R90_CARD_SOURCE_URL_SWAPPED")

    def test_r90_source_card_title_mislabelling_rejected(self):
        self._mutate_card("R89_REVIEW_HUB.html",
            lambda text: text.replace('id="r89-title-01">Apollo 1 Crew Honored',
                                      'id="r89-title-01">Different NASA subject', 1),
            "R90_CARD_TITLE_DRIFT")

    def test_r90_day_precision_change_rejected(self):
        self._mutate_card("R88_READING_ROOM.html",
            lambda text: text.replace('data-date="January 1967 — day unconfirmed"',
                                      'data-date="January 27, 1967"', 1).replace(
                                          '<strong>Photograph date:</strong> January 1967 — day unconfirmed',
                                          '<strong>Photograph date:</strong> January 27, 1967', 1),
            "R90_CARD_EVIDENCE_DRIFT")

    def test_r90_removed_photo_rights_hold_rejected(self):
        self._mutate_card("R85_NASA_SOURCE_REVIEW.html",
            lambda text: text.replace("REUSE REVIEW PENDING", "REUSE APPROVED", 1),
            "R90_CARD_RIGHTS_HOLD_REMOVED")

    def test_r90_claim_boundary_drift_rejected(self):
        self._mutate_card("R89_REVIEW_HUB.html",
            lambda text: text.replace(self.records[4]["limitation"],
                                      "A photograph proves the ignition mechanism.", 1),
            "R90_CARD_EVIDENCE_DRIFT")

    def test_r90_duplicate_source_card_id_rejected(self):
        self._mutate_card("R89_REVIEW_HUB.html",
            lambda text: text.replace('id="r89-source-02"', 'id="r89-source-01"', 1),
            "R90_MISSING_DUPLICATE_OR_MALFORMED_CARD")

    def test_four_complete_readable_views(self):
        for name in r89.PAGES:
            with self.subTest(page=name):
                data = (self.output / name).read_text()
                self.assertIn('name="viewport"', data)
                self.assertIn('noindex,nofollow', data)
                self.assertIn('STAGING', data.upper())
        self.assertEqual(len(self.receipt["verified_page_links"]), 4)

    def test_six_source_identity_in_every_view(self):
        self.assertEqual(self.receipt["nasa_sources"], 6)
        for row in self.receipt["verified_page_links"].values():
            self.assertEqual(row["nasa_source_links"], 6)

    def test_deep_links_all_resolve(self):
        self.assertEqual(len(r89.audit_pages(self.output, self.urls)), 4)
        for number in range(1, 7):
            rid = f"{number:02}"
            page = (self.output / r89.PAGES[0]).read_text()
            for link in ("R88_READING_ROOM.html#r88-",
                         "R87_PHOTOGRAPH_DATE_RAIL.html#r87-record-",
                         "R85_NASA_SOURCE_REVIEW.html#r85-source-"):
                self.assertIn(link + rid, page)

    def test_release_remains_hold_even_with_valid_sources(self):
        for key in ("publication_approved", "hosted_wordpress_verified",
                    "production_cwv_verified"):
            self.assertIs(self.receipt[key], False)
        for key in ("photo_rights_cleared", "images_embedded", "geo_pins",
                    "inferred_edges"):
            self.assertEqual(self.receipt[key], 0)

    def test_no_js_hub_with_natively_accessible_disclosures(self):
        page = (self.output / "R89_REVIEW_HUB.html").read_text()
        self.assertNotIn("<script", page)
        self.assertEqual(page.count("<details>"), 6)
        self.assertEqual(page.count("<summary>"), 6)
        self.assertEqual(page.count('class="source"'), 6)

    def test_crew_portrait_ambiguity_remains_visible(self):
        page = (self.output / "R89_REVIEW_HUB.html").read_text()
        self.assertIn("S67-19766", page)
        self.assertIn("day unknown", page)
        self.assertIn("January 27, 1967", page)

    def test_html_has_no_embedded_media_or_geo(self):
        for name in r89.PAGES:
            text = (self.output / name).read_text()
            self.assertIsNone(re.search(r"<(?:img|video|iframe|picture|audio)\b|data-(?:lat|lon|geo-edge)\b",text,re.I))

    def test_tampered_primary_link_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder)
            shutil.copytree(self.output, dest / "copy")
            copy = dest / "copy"
            target = copy / "R89_REVIEW_HUB.html"
            target.write_text(target.read_text().replace(
                'href="https://www.nasa.gov/image-detail/', 'href="https://nasa.gov.evil.example/image-detail/', 1))
            with self.assertRaisesRegex(ValueError, "UNREVIEWED_EXTERNAL"):
                r89.audit_pages(copy, self.urls)

    def test_broken_cross_page_anchor_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            copy = Path(folder) / "copy"
            shutil.copytree(self.output, copy)
            target = copy / "R89_REVIEW_HUB.html"
            target.write_text(target.read_text().replace(
                "R88_READING_ROOM.html#r88-01", "R88_READING_ROOM.html#r88-nonexistent", 1))
            with self.assertRaisesRegex(ValueError, "BROKEN_CROSS_DOCUMENT"):
                r89.audit_pages(copy, self.urls)

    def test_unreviewed_media_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            copy = Path(folder) / "copy"
            shutil.copytree(self.output, copy)
            target = copy / "R89_REVIEW_HUB.html"
            target.write_text(target.read_text().replace("</body>", "<img src='alien.png'></body>"))
            with self.assertRaisesRegex(ValueError, "UNAPPROVED_DUPLICATE_MEDIA"):
                r89.audit_pages(copy, self.urls)

    def test_print_custody_outside_closed_disclosures(self):
        page = (self.output / "R89_REVIEW_HUB.html").read_text()
        blocks = page.split('<article class="source"')[1:]
        self.assertEqual(len(blocks), 6)
        for item in blocks:
            visible = item.split("</details>", 1)[1].split("</article>", 1)[0]
            self.assertIn('class="print-custody"', visible)
            self.assertIn("INDIVIDUAL REVIEW REQUIRED", visible)
            self.assertIn("https://www.nasa.gov/image-detail/", visible)

    def test_source_receipt_hashes_are_exact(self):
        for name, digest in self.receipt["file_sha256"].items():
            self.assertEqual(r89.digest((self.output / name).read_bytes()), digest)
        for name, data in self.receipt["verified_page_links"].items():
            self.assertEqual(data["sha256"], r89.digest((self.output / name).read_bytes()))

    def test_output_must_not_overwrite_reviewed_data(self):
        with self.assertRaisesRegex(ValueError, "OUTPUT_MUST_BE_EMPTY"):
            r89.build(self.output)

    def test_deterministic_archive_bytes_and_manifest(self):
        with tempfile.TemporaryDirectory() as folder:
            a = Path(folder) / "a.zip"
            b = Path(folder) / "b.zip"
            self.assertEqual(r89.package(self.output, a), r89.package(self.output, b))
            self.assertEqual(a.read_bytes(), b.read_bytes())
            from zipfile import ZipFile
            with ZipFile(a) as z:
                manifest = json.loads(z.read("SHA256_MANIFEST.json"))
                self.assertIs(manifest["deployment_allowed"], False)
                self.assertEqual(
                    manifest["files"]["built/R89_REVIEW_HUB.html"],
                    r89.digest(z.read("built/R89_REVIEW_HUB.html")))

if __name__ == "__main__":
    unittest.main()
