"""R79 NASA source-page audit: approved source custody and adverse edits must fail closed."""
import copy
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_nasa_gallery_r79 import validate, render_html, build, AUDIT
ROOT = HERE.parents[2]

class GalleryIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads((ROOT / AUDIT).read_text())

    def reject(self, mutate, name):
        changed = copy.deepcopy(self.original)
        mutate(changed)
        with self.subTest(name=name), self.assertRaises(ValueError):
            validate(ROOT, audit=changed)

    def test_original_source_records(self):
        rows = validate(ROOT)
        self.assertEqual(len(rows), 6)
        self.assertEqual(sum(bool(r["nasa_page_pia"]) for r in rows), 5)
        self.assertEqual(sum(r["identity_status"].startswith("PROVISIONAL") for r in rows), 1)

    def test_closed_rights_and_identity_mutations(self):
        self.reject(lambda x: x["records"][0].__setitem__("nasa_page_pia", "S67-19766"), "invented PIA")
        self.reject(lambda x: x["records"][0].__setitem__("identity_status", "PIA_ON_OFFICIAL_PAGE"), "invented identity")
        self.reject(lambda x: x["records"][2].__setitem__("reuse_status", "CLEARED"), "invented permission")
        self.reject(lambda x: x.__setitem__("reusable_media_assessments_completed", 6), "fabricated rights review")
        self.reject(lambda x: x.__setitem__("images_embedded", 1), "image binary added")
        self.reject(lambda x: x.__setitem__("geographic_pins", 1), "unsupported geo pin")
        self.reject(lambda x: x.__setitem__("speculative_edges", 2), "unsupported geo edge")
        self.reject(lambda x: x["records"][4].__setitem__("catalog_claim", "S67-21295"), "catalog change")
        self.reject(lambda x: x["records"][5].__setitem__("credit_on_page", "NASA Approved"), "invented NASA credit")
        self.reject(lambda x: x["records"][3].__setitem__("nasa_page_last_updated", "2026-12-03"), "future page revision")

    def test_urls_dates_and_record_count(self):
        self.reject(lambda x: x["records"][1].__setitem__("nasa_url", "https://www.nasa.gov.evil.example/image-detail/amf-s67-15717/"), "NASA domain confusion")
        self.reject(lambda x: x["records"][1].__setitem__("nasa_url", "https://www.nasa.gov@evil.example/image-detail/amf-s67-15717/"), "credentialed URL")
        self.reject(lambda x: x["records"][1].__setitem__("nasa_url", "http://www.nasa.gov/image-detail/amf-s67-15717/"), "plaintext URL")
        self.reject(lambda x: x["records"][1].__setitem__("nasa_url", "https://www.nasa.gov/image-detail/amf-s67-15717/?ref=unknown"), "unreviewed query")
        self.reject(lambda x: x["records"][1].__setitem__("taken_date", "1967-01-27"), "date replaced with fire")
        self.reject(lambda x: x["records"][0].__setitem__("date_precision", "DAY"), "invented day precision")
        self.reject(lambda x: x["records"].reverse(), "records reordered")
        self.reject(lambda x: x["records"].append(copy.deepcopy(x["records"][0])), "duplicate record")

    def test_standalone_nojs_gallery(self):
        self.reject(lambda x: x["records"][0].__setitem__("evidence_scope", "NASA approved this photo for commercial use"), "false endorsement")
        self.reject(lambda x: x["records"][0].__setitem__("unsupported", "invented claim"), "unknown field")
        markup = render_html(ROOT)
        self.assertEqual(markup.count('<article class="card'), 6)
        self.assertEqual(markup.count('class="source-drawer"'), 6)
        self.assertEqual(markup.count('class="print-custody"'), 6)
        self.assertEqual(markup.count("Read original NASA image-detail record"), 6)
        for forbidden in ("<img", "<script", "data-lat=", "data-geo-edge="):
            self.assertNotIn(forbidden, markup)
        self.assertIn("All six photographs require individual reuse review", markup)

    def test_byte_identical_reproducible_source_artifact(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp)/"a.zip", Path(tmp)/"b.zip"
            out1, out2 = build(ROOT, a), build(ROOT, b)
            self.assertEqual(out1["zip_sha256"], out2["zip_sha256"])
            self.assertEqual(a.read_bytes(), b.read_bytes())
            with zipfile.ZipFile(a) as z:
                self.assertIsNone(z.testzip())
                manifest = json.loads(z.read("R79_MANIFEST.json"))
                self.assertEqual(manifest["nasa_official_page_reviews"], 6)
                self.assertEqual(manifest["nasa_catalog_matches"], 5)
                self.assertEqual(manifest["image_reuse_cleared"], 0)
                self.assertFalse(manifest["production_deployed"])

if __name__ == "__main__":
    unittest.main()
