"""Source-level governance and accessibility invariants for the unpublished flagship prototype."""
import json
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    "finalvestige.com", "www.nasa.gov", "commons.wikimedia.org",
    "digitalcollections.nypl.org", "www.rmg.co.uk", "www.historymuseum.ca",
    "doi.org",
}

class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []
        self.ids = set()
        self.images = []
        self.buttons = []
        self.attrs = []
        self.hidden_cases = []
    _ns = 0
    def handle_endtag(self, tag):
        if tag.lower() == 'noscript': self._ns -= 1
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'noscript': self._ns += 1
        a = dict(attrs)
        self.tags.append(tag)
        self.attrs.append((tag, a))
        if "id" in a:
            if a["id"] in self.ids:
                raise ValueError("Duplicate id: " + a["id"])
            self.ids.add(a["id"])
        if tag == "a": self.links.append(a.get("href", ""))
        if tag == "img" and not self._ns: self.images.append(a)
        if tag == "button": self.buttons.append(a)
        if "data-fv-case" in a and "hidden" in a: self.hidden_cases.append(a["data-fv-case"])

class HomepageContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.css = (ROOT / "flagship.css").read_text(encoding="utf-8")
        cls.js = (ROOT / "flagship.js").read_text(encoding="utf-8")
        cls.manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
        cls.dom = Audit()
        cls.dom.feed(cls.html)

    def test_single_heading_and_sections(self):
        self.assertEqual(self.dom.tags.count("h1"), 1)
        for key in ("fv-hf-title", "fv-hf-evidence", "fv-hf-mind-title", "fv-hf-method-title"):
            self.assertIn(key, self.dom.ids)

    def test_no_js_every_evidence_remains(self):
        self.assertEqual(len([a for tag, a in self.dom.attrs if "data-fv-case" in a]), 3)
        self.assertEqual(self.dom.hidden_cases, [])
        self.assertEqual(self.dom.tags.count("details"), 8)
        self.assertEqual(self.dom.tags.count("summary"), 8)
        self.assertIn('class="fv-hf__case-choice-group" data-fv-case-buttons hidden', self.html)

    def test_exact_three_original_source_plates(self):
        ids = {r["id"] for r in self.manifest["records"]}
        self.assertEqual(ids, {"apollo", "franklin", "malbone"})
        self.assertEqual({a["data-fv-case"] for tag,a in self.dom.attrs if "data-fv-case" in a}, ids)
        self.assertEqual(len(self.dom.images), 3)
        for r in self.manifest["records"]:
            self.assertTrue(any(a.get("src") == r["image_url"] for a in self.dom.images))
            self.assertIn(r["source_url"], self.dom.links)
            self.assertIn(r["article_url"], self.dom.links)
            self.assertTrue(r.get("limitation") and r.get("media_rights_status"))

    def test_image_alt_dimensions_and_loading(self):
        for img in self.dom.images:
            self.assertGreater(len(img.get("alt", "")), 35)
            self.assertGreater(int(img["width"]), 0)
            self.assertGreater(int(img["height"]), 0)
            self.assertEqual(img["decoding"], "async")
        self.assertIn("srcset", self.dom.images[2])
        self.assertIn("sizes", self.dom.images[2])
        self.assertTrue(self.dom.images[2]["src"].startswith("https://i0.wp.com/"))
        self.assertIn("1536w", self.dom.images[2]["srcset"])
        self.assertEqual(self.dom.images[2]["src"], self.manifest["records"][2]["image_url"])
        self.assertNotEqual(self.dom.images[2]["src"], self.manifest["records"][2]["original_wordpress_image_url"])
        # All three evidence images sit below the fold (chapter 3, reached only by scrolling
        # past the hero and chronicle); none should be promoted with eager/fetchpriority=high,
        # which belongs only to a genuine above-the-fold LCP candidate (see
        # test_responsive_archive_media.test_below_fold_assets_not_promoted_to_lcp).
        self.assertEqual([img["loading"] for img in self.dom.images], ["lazy", "lazy", "lazy"])
        self.assertTrue(all("fetchpriority" not in img for img in self.dom.images))

    def test_links_are_safe_no_unapproved_affiliate(self):
        self.assertTrue(all(href.startswith("#") or href.startswith("https://") for href in self.dom.links))
        self.assertTrue(all(urlparse(href).hostname in ALLOWED for href in self.dom.links if href.startswith("https://")))
        self.assertNotIn("inspire3.com", self.html)
        self.assertNotIn('href="/mind/"', self.html)
        self.assertIn("https://finalvestige.com/focus/", self.dom.links)
        self.assertIn("https://finalvestige.com/affiliate-disclosure/", self.dom.links)

    def test_accessibility_and_fail_open_enhancement(self):
        self.assertIn("aria-pressed", self.html)
        self.assertIn('aria-live="polite"', self.html)
        for key in ("ArrowLeft", "ArrowRight", "Home", "End"):
            self.assertIn(key, self.js)
        for marker in ("resetStatic", "panel.hidden = false", "group.hidden = true"):
            self.assertIn(marker, self.js)
        self.assertNotIn("touch-action:none", self.css)
        self.assertEqual(self.js.count("event.preventDefault()"), 1)
        self.assertIn("prefers-reduced-motion:reduce", self.css)
        self.assertIn(":focus-visible", self.css)
        self.assertIn("@media(max-width:600px)", self.css)

    def test_single_locked_art_direction(self):
        # Founder approved Black Dossier (blended with Museum After Hours warmth) as the one
        # shipped identity on 2026-11-01; the multi-direction studio picker is retired.
        self.assertNotIn("data-fv-direction-choice", self.html)
        self.assertNotIn("data-fv-direction", self.html)
        self.assertNotIn('fv-direction="museum"', self.css)
        self.assertNotIn('fv-direction="observatory"', self.css)
        self.assertNotIn("DIRECTIONS", self.js)
        self.assertIn("DESIGN CANDIDATE", self.html)
        self.assertIn("NOT LIVE", self.html)

    def test_source_claim_boundaries_and_commerce(self):
        self.assertIn("crew photograph documents the astronauts—not the hatch", self.html)
        self.assertIn("not claiming that the 1903 map depicts", self.html)
        self.assertIn("The note records what its writers reported", self.html)
        self.assertIn("pending", self.manifest["records"][2]["media_rights_status"].lower())
        self.assertEqual(self.manifest["commercial_boundaries"]["affiliate_links_in_prototype"], 0)

if __name__ == "__main__":
    unittest.main()
