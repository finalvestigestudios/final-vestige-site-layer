"""Browser-backed regression for the actual locked-folio staging gate.

Fixture is deliberately representative, NOT actual WordPress staging. The
separate acceptance runner imports this same function on real WordPress DOM.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import unittest

BASE = Path(__file__).resolve().parent.parent
SOURCE = BASE / 'qa/release-candidate/editorial_identity_gate.py'
spec = importlib.util.spec_from_file_location('fv_editorial_gate', SOURCE)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

HTML = '''<!doctype html><html lang="en"><head><style>
.fv-hf__folio-note {background:#d4bc8d; width:300px; min-height:320px; display:block;}
</style></head><body>
<main data-fv-home-flagship>
<aside class="fv-hf__opening-art" aria-label="Franklin editorial study">
<div class="fv-hf__folio-note">
<div><time datetime="1847-05-28">28 May 1847</time></div>
<div class="fv-hf__folio-margin">April 1848 / added in the margin</div>
<div class="fv-hf__folio-note-foot">EDITORIAL TYPESETTING · NOT A FACSIMILE</div>
</div>
<a href="https://www.rmg.co.uk/collections/objects/rmgc-object-504898">Inspect the museum record</a>
</aside>
</main></body></html>'''


class LockedIdentityBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(
            headless=True, executable_path=shutil.which('chromium') or None,
            args=['--no-sandbox'],
        )

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def check(self, html):
        page = self.browser.new_page(viewport={'width': 390, 'height': 840})
        try:
            page.set_content(html)
            return gate.check_locked_editorial_identity(page)
        finally:
            page.close()

    def test_accepted_locked_evidence_folio(self):
        checks = self.check(HTML)
        self.assertTrue(all(checks.values()), checks)
        self.assertEqual(len(checks), 7)

    def test_legacy_direction_picker_is_rejected(self):
        checks = self.check(HTML.replace('</main>', '<button data-fv-direction-choice="museum">Museum</button></main>'))
        self.assertFalse(checks['locked_direction_no_legacy_picker'])

    def test_legacy_direction_attribute_is_rejected(self):
        checks = self.check(HTML.replace('<main data-fv-home-flagship>', '<main data-fv-home-flagship data-fv-direction="dossier">'))
        self.assertFalse(checks['locked_direction_no_legacy_picker'])

    def test_missing_original_date_is_rejected(self):
        checks = self.check(HTML.replace('datetime="1847-05-28"', 'datetime="1847-05-29"'))
        self.assertFalse(checks['folio_1847_original_dated'])

    def test_missing_addendum_is_rejected(self):
        checks = self.check(HTML.replace('April 1848', 'April 1849'))
        self.assertFalse(checks['folio_1848_addition_explicit'])

    def test_false_facsimile_is_rejected(self):
        checks = self.check(HTML.replace('NOT A FACSIMILE', 'ORIGINAL FACSIMILE'))
        self.assertFalse(checks['folio_disclaims_facsimile'])

    def test_lost_museum_link_is_rejected(self):
        checks = self.check(HTML.replace('rmgc-object-504898', 'rmgc-object-000000'))
        self.assertFalse(checks['folio_original_source_link'])

    def test_hidden_artifact_is_rejected(self):
        checks = self.check(HTML.replace('display:block;', 'display:none;'))
        self.assertFalse(checks['archival_folio_one_visible'])

    def test_unpainted_artifact_is_rejected(self):
        checks = self.check(HTML.replace('background:#d4bc8d;', 'background:transparent;'))
        self.assertFalse(checks['folio_real_geometry_and_paint'])


if __name__ == '__main__':
    unittest.main()
