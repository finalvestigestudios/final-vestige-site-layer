#!/usr/bin/env python3
"""Offline, standard-library R108 Apollo creator-bridge source/custody checks."""
import hashlib
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "landing-preview.html"
CUSTODY = HERE.parent / "research-desk" / "sources" / "R37_PHOTO_CUSTODY_CROSSWALK.json"
R37_BLOB_SHA1 = "ca00a51d8d47d02f9ccc2fbb55df31a0ed36e7ea"

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.ids, self.links, self.primary, self.scripts = [], [], [], [], []
        self.controls, self.forms, self.media = [], [], []
        self.has_noindex = False
    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        self.tags.append(tag)
        if "id" in props: self.ids.append(props["id"])
        if tag == "a":
            self.links.append(props.get("href", ""))
            if "data-fv-primary-cta" in props: self.primary.append(props.get("href"))
        if tag == "meta" and props.get("name") == "robots":
            self.has_noindex = "noindex" in props.get("content", "")
        if tag in ("img","picture","video","audio","iframe","canvas","svg","source"):
            self.media.append(tag)
        if tag == "script" and props.get("src"): self.scripts.append(props["src"])
        if tag == "form": self.forms.append(props)
        if tag == "button" and "data-fv-mode" in props:
            self.controls.append(props["data-fv-mode"])

def git_blob(blob):
    return hashlib.sha1(b"blob " + str(len(blob)).encode() + b"\0" + blob).hexdigest()

class BridgeSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf8")
        cls.page = Page()
        cls.page.feed(cls.source)
        raw = CUSTODY.read_bytes()
        cls.custody_sha1 = git_blob(raw)
        cls.custody = json.loads(raw)
    def test_pin_actual_r37_custody(self):
        self.assertEqual(self.custody_sha1, R37_BLOB_SHA1)
        self.assertEqual(self.custody["schema"], "fv.ex2.apollo.photo_custody.r37.v1")
    def test_six_exact_nasa_photographic_links(self):
        rows = self.custody["records"]
        self.assertEqual([r["id"] for r in rows], ["01","02","03","04","05","06"])
        for row in rows:
            self.assertEqual(self.page.links.count(row["photo_url"]), 1)
            self.assertEqual(row["media_rights"], "INDIVIDUAL_REVIEW_REQUIRED")
    def test_provisional_identity_remains_visible(self):
        self.assertIn("S67-19766 (provisional)", self.source)
        self.assertIn("NASA page does not itself print this catalog ID", self.source)
        self.assertNotIn("individually cleared", self.source)
    def test_no_third_party_media_or_scripts(self):
        self.assertEqual(self.page.media, [])
        self.assertEqual(self.page.scripts, [])
        self.assertNotIn("fetch(", self.source)
        self.assertNotIn("sendBeacon", self.source)
    def test_no_inferred_geography(self):
        for pattern in (r"\bdata-lat=",r"\bdata-lon=",r"\bdata-geo=",r"<canvas",r"leaflet",r"mapbox"):
            self.assertNotRegex(self.source.lower(),pattern)
    def test_no_checkout_form_or_unverified_price(self):
        self.assertEqual(self.page.forms, [])
        self.assertNotIn("payhip.com", self.source)
        self.assertNotRegex(self.source, r"\$[0-9]+")
    def test_single_contextual_primary_action(self):
        self.assertEqual(self.page.primary, ["#classroom-preview"])
        self.assertIn('id="classroom-preview"',self.source)
        self.assertIn("product hypothesis, not a listing", self.source)
    def test_noindex_staging(self):
        self.assertTrue(self.page.has_noindex)
        self.assertIn("STAGING CANDIDATE", self.source)
    def test_unique_section_ids(self):
        self.assertEqual(len(self.page.ids), len(set(self.page.ids)))
        self.assertIn("event-sequence", self.page.ids)
        self.assertIn("source-custody", self.page.ids)
    def test_photo_dates_separate_from_fire_event(self):
        self.assertIn("Photographic dates and the fire chronology", self.source)
        self.assertIn("Retrospective hatch exhibit", self.source)
        self.assertIn("The precise ignition moment remains unknown", self.source)
    def test_nojs_native_details_and_content(self):
        self.assertGreaterEqual(self.page.tags.count("details"), 3)
        self.assertEqual(self.page.tags.count("summary"), self.page.tags.count("details"))
        self.assertEqual(self.source.count('class="plate" data-fv-claim='), 4)
        self.assertIn('data-fv-lens hidden', self.source)
    def test_progressive_control_semantics(self):
        self.assertEqual(self.page.controls, ["all","known","limit"])
        self.assertIn('aria-pressed="true"', self.source)
        self.assertIn("aria-live", self.source)
    def test_responsive_and_accessible(self):
        self.assertIn("max-width:800px",self.source)
        self.assertIn("max-width:370px",self.source)
        self.assertIn("prefers-reduced-motion:reduce", self.source)
        self.assertIn("forced-colors:active", self.source)
        self.assertIn("a:focus-visible", self.source)
    def test_source_and_rights_guidance(self):
        self.assertIn(self.custody["historical_primary"],self.page.links)
        self.assertIn(self.custody["rights_guidance"],self.page.links)
        self.assertIn("0/6", self.source)
    def test_original_live_article_route_not_modified(self):
        self.assertIn("https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/",self.page.links)

if __name__=="__main__":
    unittest.main()
