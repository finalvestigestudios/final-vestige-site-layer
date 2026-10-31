"""Exact-source static regression for WordPress archival responsive media.

These checks do NOT claim live HTTP transfer, actual browser selection,
performance, usage-rights approval or WordPress staging success.
"""
import html
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import unittest

HOME = Path(__file__).resolve().parents[1]
EXPECTED_VARIANTS = {
    "apollo": {300: (300, 233), 768: (768, 598), 1024: (1024, 797)},
    "franklin": {189: (189, 300), 644: (644, 1024), 768: (768, 1221), 960: (960, 1526)},
    "malbone": {768: (768, 519), 1024: (1024, 692), 1536: (1536, 1038)},
}

class ImageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "img":
            d = dict(attrs)
            if "data-fv-archive-img" in d:
                self.images.append(d)

class ResponsiveArchiveMedia(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (HOME / "index.html").read_text(encoding="utf-8")
        cls.ledger = json.loads((HOME / "source-manifest.json").read_text(encoding="utf-8"))
        parser = ImageParser()
        parser.feed(cls.source)
        cls.images = parser.images

    def test_three_original_source_images_only(self):
        self.assertEqual(len(self.images), 3)
        self.assertEqual(
            {record["image_url"] for record in self.ledger["records"]},
            {image["src"] for image in self.images},
        )

    def test_all_three_have_valid_accessible_dimensions(self):
        for image in self.images:
            self.assertTrue(image.get("alt"), image["src"])
            self.assertGreater(int(image.get("width", 0)), 0)
            self.assertGreater(int(image.get("height", 0)), 0)

    def test_below_fold_assets_not_promoted_to_lcp(self):
        for image in self.images:
            self.assertEqual(image.get("loading"), "lazy", image["src"])
            self.assertNotEqual(image.get("fetchpriority"), "high", image["src"])

    def test_exact_wordpress_proxy_derivatives(self):
        for record in self.ledger["records"]:
            image = next(x for x in self.images if x["src"] == record["image_url"])
            src = image["src"]
            kind = record["id"]
            self.assertIn(kind, EXPECTED_VARIANTS)
            self.assertTrue(src.startswith(("https://finalvestige.com/wp-content/uploads/",
                                             "https://i0.wp.com/finalvestige.com/wp-content/uploads/")))
            candidates = image.get("srcset", "").split(", ")
            expected = EXPECTED_VARIANTS[kind]
            self.assertEqual(len(candidates), len(expected), kind)
            for candidate in candidates:
                url, width_desc = candidate.rsplit(" ", 1)
                width = int(width_desc.removesuffix("w"))
                self.assertIn(width, expected, kind)
                parsed = urlsplit(html.unescape(url))
                self.assertEqual(parsed.scheme, "https")
                self.assertEqual(parsed.netloc, "i0.wp.com")
                expected_path = ("/finalvestige.com" + urlsplit(src).path
                                 if urlsplit(src).netloc == "finalvestige.com"
                                 else urlsplit(src).path)
                self.assertEqual(parsed.path, expected_path)
                query = parse_qs(parsed.query)
                self.assertEqual(query.get("ssl"), ["1"])
                self.assertEqual(query.get("fit"), ["%d,%d" % expected[width]])

    def test_sizes_present_and_not_width_agnostic(self):
        for image in self.images:
            sizes = image.get("sizes", "")
            self.assertIn("max-width:600px", sizes)
            self.assertIn("max-width:920px", sizes)
            self.assertIn("vw", sizes)

    def test_unpublished_design_and_existing_seven_chapters(self):
        self.assertIn("DO NOT DEPLOY AS THE WORDPRESS HOME PAGE", self.source)
        for dest in ("fv-hf-title", "fv-hf-chronicle", "fv-hf-evidence",
                     "fv-hf-inquiry", "fv-hf-method-title", "fv-hf-observer",
                     "fv-hf-mind-title"):
            self.assertIn('href="#'+dest+'"', self.source)
        self.assertIn('href="https://finalvestige.com/focus/"', self.source)

    def test_no_new_remote_executable_assets(self):
        self.assertEqual(self.source.count(' src="./'), 4)
        self.assertEqual(self.source.count('<link rel="stylesheet" href="./'), 6)
        self.assertNotIn("inspire3.com/checkout", self.source.lower())

if __name__ == "__main__":
    unittest.main()
