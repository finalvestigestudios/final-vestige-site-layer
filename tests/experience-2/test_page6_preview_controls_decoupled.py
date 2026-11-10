#!/usr/bin/env python3
"""EX2 scoped WordPress renderer: keep internal study controls out of reader UI.

Tests against the repository's pinned eleven-file design source, not live
WordPress/Assembler. No CMS writes, subscription requests or HTTP dependencies.
"""
from __future__ import annotations
import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'experience2/home-flagship'
COMPOSER = ROOT / 'tools/experience-2/compose_page6_flagship.py'
spec = importlib.util.spec_from_file_location('ex2_scoped_composer', COMPOSER)
m = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = m
spec.loader.exec_module(m)


class WordPressPreviewControlIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = m.stage_payload(SRC)

    def test_no_design_study_toolbar_in_scoped_html(self):
        # The JS/CSS may retain selector names; only DOM controls must vanish.
        self.assertNotIn('<div class="fv-hf__studio"', self.payload)
        self.assertNotIn('<details class="fv-hf__studio-controls"', self.payload)
        self.assertNotIn('DESIGN STUDY · NOT LIVE', self.payload)

    def test_all_seven_chapters_remain(self):
        for chapter in m.CHAPTERS:
            with self.subTest(chapter=chapter):
                self.assertEqual(self.payload.count('id="' + chapter + '"'), 1)

    def test_focus_rail_survives_without_javascript(self):
        self.assertIn('class="fv-hf__focus-rail"', self.payload)
        self.assertIn('href="https://finalvestige.com/focus/"', self.payload)

    def test_direction_contract_retained(self):
        # Preview URL param and all three visual treatments remain in pinned JS.
        self.assertIn("['dossier', 'museum', 'observatory']", self.payload)
        self.assertIn("new URLSearchParams(window.location.search).get('direction')", self.payload)
        self.assertIn('data-fv-direction="dossier"', self.payload)

    def test_enhancement_does_not_require_picker(self):
        self.assertIn('if (!group || !status ||', self.payload)
        self.assertNotIn('if (!group || !status || !directionGroup ||', self.payload)
        self.assertIn('if (directionGroup) directionGroup.hidden = false;', self.payload)
        self.assertIn('if (directionGroup) directionGroup.hidden = true;', self.payload)

    def test_original_preview_source_untouched(self):
        html = (SRC / 'index.html').read_text()
        js = (SRC / 'flagship.js').read_text()
        self.assertIn('DESIGN STUDY · NOT LIVE', html)
        for d in ('dossier', 'museum', 'observatory'):
            self.assertIn('data-fv-direction-choice="' + d + '"', html)
        self.assertIn('!directionGroup ||', js)

    def test_pinned_sources_not_mutated(self):
        for file, blob in m.PINNED_GIT_BLOBS.items():
            with self.subTest(file=file):
                self.assertEqual(m.git_blob((SRC / file).read_bytes()), blob)

    def test_missing_original_picker_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            for fname in m.PINNED_GIT_BLOBS:
                shutil.copy2(SRC / fname, p / fname)
            f = p / 'index.html'
            f.write_text(f.read_text().replace('fv-hf__studio-controls', 'altered-controls'))
            with self.assertRaises(m.AdmissionError):
                m.stage_payload(p, pin=False)

    def test_missing_js_optional_group_contract_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            for fname in m.PINNED_GIT_BLOBS:
                shutil.copy2(SRC / fname, p / fname)
            f = p / 'flagship.js'
            f.write_text(f.read_text().replace('directionGroup.hidden = false;', 'unknown.hidden = false;'))
            with self.assertRaises(m.AdmissionError):
                m.stage_payload(p, pin=False)


if __name__ == '__main__':
    unittest.main()
