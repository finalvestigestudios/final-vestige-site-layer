"""Synthetic Assembler first-screen custody checks (offline; never WordPress acceptance).
Run: python -m unittest discover -s tests/experience-2 -p 'test_page6_assembler_first_screen.py' -v
"""
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools/experience-2"))
from compose_page6_flagship import AdmissionError, CHAPTERS, PINNED_GIT_BLOBS, stage_payload, compose


def synthetic_page():
    margins = "".join(f'<span class="fv-margin-strip__item">Public record {n:02d}</span>' for n in range(72))
    chapters = "".join(f'<section id="{c}">Old chapter</section>' for c in CHAPTERS)
    return (f'<!-- wp:html --><div class="fv-margin-strip">{margins}</div><!-- /wp:html -->'
            f'<!-- wp:html --><div data-fv-home-flagship>{chapters}</div><!-- /wp:html -->'
            '<!-- wp:html --><section class="fv-focus-cta"><a class="fv-focus-cta__button" href="/focus/">Focus</a></section><!-- /wp:html -->'
            '<!-- wp:jetpack/subscriptions /-->'
            '<!-- wp:html --><div>Public footer</div><!-- /wp:html -->')


class FirstScreenIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = REPO / "experience2/home-flagship"
        cls.payload = stage_payload(cls.source)

    def test_duplicate_theme_header_removed_from_integrated_payload(self):
        self.assertNotIn('<div class="fv-hf__masthead"', self.payload)
        self.assertNotIn('<header class="fv-hf__masthead"', self.payload)
        self.assertNotIn('<a class="fv-hf__brand"', self.payload)
        self.assertNotIn('<details class="fv-hf__mobile-menu"', self.payload)
        self.assertNotIn('<nav class="fv-hf__nav"', self.payload)
        self.assertIn('fv-hf--wp-integrated', self.payload)

    def test_first_screen_focus_link_is_direct_and_semantically_labelled(self):
        self.assertEqual(self.payload.count('class="fv-hf__focus-rail"'), 1)
        rail = re.search(r'<div class="fv-hf__focus-rail".*?</div>', self.payload, re.S)
        self.assertIsNotNone(rail)
        self.assertIn('aria-label="Free reader resource"', rail.group())
        self.assertIn('class="fv-hf__mast-cta" href="https://finalvestige.com/focus/"', rail.group())
        self.assertIn('min-height:44px', self.payload)
        self.assertIn('.fv-hf--wp-integrated .fv-hf__focus-rail', self.payload)

    def test_original_evidence_and_art_directions_remain(self):
        for chapter in CHAPTERS:
            self.assertEqual(self.payload.count(f'id="{chapter}"'), 1)
        # Internal founder preview options remain in the immutable standalone
        # source, but must not appear as public WordPress page controls.
        original = (self.source / 'index.html').read_text()
        for direction in ("dossier", "museum", "observatory"):
            self.assertEqual(original.count(f'data-fv-direction-choice="{direction}"'), 1)
            self.assertEqual(self.payload.count(f'data-fv-direction-choice="{direction}"'), 0)
        self.assertNotIn('<div class="fv-hf__studio"', self.payload)
        self.assertIn('Inspect the museum record', self.payload)
        self.assertIn('EDITORIAL TYPESETTING', self.payload)
        self.assertIn('Skip to the main archive', self.payload)

    def test_existing_native_focus_and_jetpack_remain_outside_swap(self):
        raw = synthetic_page()
        composed, receipt = compose(raw, self.payload)
        self.assertEqual(receipt['margins_retained'], 72)
        self.assertEqual(receipt['native_focus_destination'], '/focus/')
        self.assertTrue(receipt['native_jetpack_retained'])
        self.assertEqual(composed.count("<!-- wp:jetpack/subscriptions"), 1)
        self.assertEqual(composed.count('fv-focus-cta__button'), 1)

    def test_missing_or_modified_source_masthead_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td)
            for name in PINNED_GIT_BLOBS:
                (dest/name).write_bytes((self.source/name).read_bytes())
            index = dest/"index.html"
            raw = index.read_text()
            index.write_text(raw.replace('<header class="fv-hf__masthead">',
                                         '<header class="fv-hf__unknown">', 1))
            with self.assertRaises(AdmissionError):
                stage_payload(dest, pin=False)

    def test_missing_source_focus_action_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            dest = Path(td)
            for name in PINNED_GIT_BLOBS:
                (dest/name).write_bytes((self.source/name).read_bytes())
            index = dest/"index.html"
            index.write_text(index.read_text().replace(
                'class="fv-hf__mast-cta" href="https://finalvestige.com/focus/"',
                'class="fv-hf__mast-cta" href="https://example.invalid/"',1))
            with self.assertRaises(AdmissionError):
                stage_payload(dest, pin=False)

if __name__=="__main__":
    unittest.main(verbosity=2)
