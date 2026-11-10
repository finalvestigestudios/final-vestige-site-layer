"""Synthetic Gutenberg negative controls for the read-only Page 6 scoped composer.

These are not WordPress/Jetpack integration tests. No production data or DB fixtures.
Run: python -m unittest discover -s tests/experience-2 -p 'test_page6_scoped_composer.py' -v
"""
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'tools/experience-2'))
from compose_page6_flagship import CHAPTERS, HTML_BLOCK, JETPACK, PINNED_GIT_BLOBS, AdmissionError, compose, stage_payload

def synthetic_page():
    margins = ''.join(f'<span class="fv-margin-strip__item">Public record {i:02d}</span>' for i in range(72))
    chapters = ''.join(f'<section id="{i}">Earlier chapter {i}</section>' for i in CHAPTERS)
    return (f'<!-- wp:html -->\n<div class="fv-margin-strip">{margins}</div>\n<!-- /wp:html -->'
            f'<!-- wp:html -->\n<div data-fv-home-flagship>{chapters}</div>\n<!-- /wp:html -->'
            f'<!-- wp:html -->\n<section class="fv-focus-cta"><a class="fv-focus-cta__button" href="/focus/">Focus Fieldbook</a></section>\n<!-- /wp:html -->'
            f'<!-- wp:group --><div class="wp-block-group">Dispatch signup<!-- wp:jetpack/subscriptions {{"className":"is-style-split"}} /--></div><!-- /wp:group -->'
            f'<!-- wp:html -->\n<footer>Other public homepage content</footer>\n<!-- /wp:html -->')

class ScopedIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use the exact source in a clean checkout; never silently accept an approximate version.
        cls.source = REPO / 'experience2' / 'home-flagship'
        if not cls.source.is_dir():
            raise RuntimeError('Expected exact source directory experience2/home-flagship is missing')
        cls.payload = stage_payload(cls.source)
        cls.base = synthetic_page()

    def test_exact_outside_custody(self):
        out, receipt = compose(self.base, self.payload)
        blocks = list(HTML_BLOCK.finditer(self.base))
        target = next(m for m in blocks if 'data-fv-home-flagship' in m.group(1))
        self.assertEqual(out[:target.start()], self.base[:target.start()])
        self.assertEqual(out[-len(self.base[target.end():]):], self.base[target.end():])
        self.assertEqual(receipt['margins_retained'], 72)
        self.assertEqual(len(JETPACK.findall(out)), 1)
        self.assertTrue(receipt['native_focus_retained'])
        self.assertEqual(receipt['chapter_count'], 7)
        self.assertEqual(len(re.findall(r'<div\b[^>]*\bdata-fv-home-flagship\b', out)),1)
        for i in CHAPTERS:
            self.assertEqual(out.count(f'id="{i}"'), 1)

    def test_payload_assets_and_landmarks(self):
        self.assertEqual(self.payload.count('<style data-fv-source='),1)
        self.assertEqual(self.payload.count('<script data-fv-source='),4)
        self.assertNotRegex(self.payload,r'<(?:html|head|body|main|header|footer)(?:\s|>)')
        self.assertIn('role="region" aria-label="The living archive"',self.payload)
        self.assertIn('Skip to the main archive',self.payload)

    def test_idempotent(self):
        once,_ = compose(self.base,self.payload)
        twice,_ = compose(once,self.payload)
        self.assertEqual(once,twice)

    def test_missing_target(self):
        with self.assertRaises(AdmissionError):
            compose(self.base.replace('data-fv-home-flagship','data-other'),self.payload)

    def test_duplicate_target(self):
        target=list(HTML_BLOCK.finditer(self.base))[1].group(0)
        with self.assertRaises(AdmissionError):compose(self.base+target,self.payload)

    def test_jetpack_removed(self):
        with self.assertRaises(AdmissionError):
            compose(self.base.replace('wp:jetpack/subscriptions','wp:paragraph'),self.payload)

    def test_jetpack_inside_target(self):
        target=list(HTML_BLOCK.finditer(self.base))[1].group(0)
        altered=self.base.replace(target,target.replace('</div>','<!-- wp:jetpack/subscriptions /--></div>'),1)
        altered=altered.replace('<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->','')
        with self.assertRaises(AdmissionError):compose(altered,self.payload)

    def test_71_margins(self):
        with self.assertRaises(AdmissionError):
            compose(self.base.replace('class="fv-margin-strip__item"','class="missing"',1),self.payload)

    def test_focus_disappears(self):
        with self.assertRaises(AdmissionError):
            compose(self.base.replace('href="/focus/"','href="https://example.invalid/focus/"'),self.payload)

    def test_real_page6_root_relative_focus_action(self):
        _, receipt = compose(self.base, self.payload)
        self.assertEqual(receipt['native_focus_destination'], '/focus/')

    def test_approved_absolute_focus_action(self):
        raw = self.base.replace('href="/focus/"', 'href="https://finalvestige.com/focus/"')
        _, receipt = compose(raw, self.payload)
        self.assertEqual(receipt['native_focus_destination'], 'https://finalvestige.com/focus/')

    def test_reject_native_focus_query_open_redirect_and_merchants(self):
        for url in ('/focus/?subscribe=1', '//evil.example/focus/',
                    'https://evil.example/focus/', 'javascript:alert(1)',
                    'http://finalvestige.com/focus/', '/products/'):
            with self.subTest(url=url), self.assertRaises(AdmissionError):
                compose(self.base.replace('href="/focus/"', f'href="{url}"'), self.payload)

    def test_unrelated_absolute_focus_link_not_valid_evidence(self):
        bad = self.base.replace('href="/focus/"', 'href="/products/"')
        bad += '<a href="https://finalvestige.com/focus/">Unrelated</a>'
        with self.assertRaises(AdmissionError): compose(bad, self.payload)

    def test_duplicate_native_focus_action_fails(self):
        duplicate = '<a class="fv-focus-cta__button" href="/focus/">Duplicate</a>'
        bad = self.base.replace('Focus Fieldbook</a>', 'Focus Fieldbook</a>'+duplicate, 1)
        with self.assertRaises(AdmissionError): compose(bad, self.payload)

    def test_duplicate_chapter_outside(self):
        with self.assertRaises(AdmissionError):
            compose(self.base+'<div id="fv-hf-evidence"></div>',self.payload)

    def test_gutenberg_directive_in_payload(self):
        with self.assertRaises(AdmissionError):
            compose(self.base,self.payload+'<!-- /wp:html -->')

    def test_tampered_source_blob(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in PINNED_GIT_BLOBS:
                (Path(tmp)/name).write_bytes((self.source/name).read_bytes())
            source=Path(tmp)/'flagship.js'
            source.write_text('// tampered\n'+source.read_text())
            with self.assertRaises(AdmissionError):stage_payload(Path(tmp))

    def test_duplicate_candidate_chapter(self):
        with self.assertRaises(AdmissionError):
            compose(self.base,self.payload+'<section id="fv-hf-title"></section>')

    def test_missing_other_blocks(self):
        with self.assertRaises(AdmissionError):
            compose(list(HTML_BLOCK.finditer(self.base))[1].group(0),self.payload)
