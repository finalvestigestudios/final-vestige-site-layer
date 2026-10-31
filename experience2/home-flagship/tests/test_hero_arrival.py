"""Large visual entrance, historical source honesty and responsive/no-JS invariants."""
from pathlib import Path
import re
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ArrivalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/"index.html").read_text(encoding="utf-8")
        cls.css=(ROOT/"flagship.css").read_text(encoding="utf-8")
    def test_exactly_one_document_headline(self):
        self.assertEqual(len(re.findall(r"<h1\b",self.html)),1)
        self.assertIn('id="fv-hf-title"',self.html)
    def test_source_grounded_not_facsimile(self):
        for s in ("THE VICTORY POINT NOTE","28 MAY 1847","APRIL 1848","EDITORIAL TYPESETTING","NOT A FACSIMILE","rmg.co.uk/collections/objects/rmgc-object-504898"):
            self.assertIn(s,self.html)
    def test_paper_caption_color_meets_wcag_aa(self):
        # Small 9px archival labels must meet 4.5:1, not merely large-text AA.
        def luminance(hexcode):
            values = [int(hexcode[i:i+2],16)/255 for i in (1,3,5)]
            linear = [v/12.92 if v<=.04045 else ((v+0.055)/1.055)**2.4 for v in values]
            return sum(v*w for v,w in zip(linear, (0.2126,0.7152,0.0722)))
        light=luminance("#e3d7bc")
        muted=luminance("#635032")
        self.assertGreaterEqual((light+0.05)/(muted+0.05),4.5)
        self.assertIn("color:#635032",self.css)

    def test_hero_has_no_new_third_party_media(self):
        self.assertEqual(len(re.findall(r"<img\b",self.html)),3)
        self.assertEqual(len(re.findall(r"<script\b[^>]*\bsrc=",self.html)),4)
    def test_archive_pillars_preserved(self):
        for s in ('href="https://finalvestige.com/focus/"','/free-resources/puysegurs-animal-magnetism-files/','fv-hf__chapter-nav','data-fv-case-buttons'):
            self.assertIn(s,self.html)
    def test_responsive_and_focus(self):
        self.assertIn('@media(max-width:600px)',self.css)
        self.assertIn('prefers-reduced-motion:reduce',self.css)
        self.assertIn(':focus-visible',self.css)
    def test_folio_not_hidden_from_accessibility_tree(self):
        self.assertIn('<aside class="fv-hf__opening-art fv-hf__folio-arrival" aria-label=',self.html)
        self.assertNotIn('aria-hidden="true"><div class="fv-hf__folio-stage"',self.html)
    def test_seven_chapters_and_three_original_pictures(self):
        self.assertEqual(len(re.findall(r'data-fv-archive-img',self.html)),3)
        for x in ('fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'):
            self.assertIn('href="#'+x+'"',self.html)
