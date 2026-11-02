"""Governance and semantic checks for staged archive chronology, no WordPress mutations."""
import json
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class ChronicleContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.markup=(ROOT/'index.html').read_text(encoding='utf-8')
        cls.style=(ROOT/'chronicle.css').read_text(encoding='utf-8')
        cls.ledger=json.loads((ROOT/'chronicle-source-ledger.json').read_text(encoding='utf-8'))

    def test_unique_anchors(self):
        for a in ('fv-hf-chronicle','fv-hf-title','fv-hf-evidence','fv-hf-method-title','fv-hf-mind-title'):
            self.assertEqual(len(re.findall(r'id="'+a+'"',self.markup)),1,a)

    def test_native_skip_and_six_chapters(self):
        self.assertIn('class="fv-hf__skip"',self.markup)
        self.assertEqual(self.markup.count('class="fv-hf__chapter-nav"'),1)
        for target in ('#fv-hf-title','#fv-hf-chronicle','#fv-hf-evidence','#fv-hf-inquiry','#fv-hf-method-title','#fv-hf-mind-title'):
            self.assertIn('href="'+target+'"',self.markup)

    def test_two_messages_not_animated_fabrications(self):
        self.assertIn('“All well.”',self.markup)
        self.assertIn('“Terror and Erebus were deserted”',self.markup)
        self.assertIn('not a document facsimile',self.markup)
        self.assertIn('aria-labelledby="fv-hf-chronicle-title"',self.markup)
        self.assertIn('datetime="1847-05-28"',self.markup)

    def test_evidence_limits_visible_and_native_disclosure(self):
        self.assertIn('<details>',self.markup)
        self.assertIn('What this evidence establishes—and what it cannot',self.markup)
        self.assertIn('25th April 1848',self.markup)
        self.assertIn('26 April 1848',self.markup)
        self.assertIn('does not erase',self.markup)

    def test_primary_sources_present(self):
        for host in ('https://www.rmg.co.uk/collections/objects/rmgc-object-504898',
                     'https://www.historymuseum.ca/blog/a-very-special-piece-of-paper',
                     'https://finalvestige.com/2026/08/20/all-well-was-written-first-franklin-expedition/'):
            self.assertIn(host,self.markup)
        self.assertEqual(self.ledger['asset_rights']['new_external_images'],0)
        self.assertEqual(self.ledger['asset_rights']['new_javascript_bytes'],0)

    def test_no_affiliate_or_new_signup_route(self):
        self.assertNotIn('inspire3.com',self.markup)
        self.assertNotIn('affiliate_id=',self.markup)
        self.assertIn('https://finalvestige.com/focus/',self.markup)

    def test_scope_and_mobile_override(self):
        self.assertIn('.fv-hf__chronicle',self.style)
        self.assertRegex(self.style,r'@media\(max-width:920px\).*?\.fv-hf__nav\{display:flex')
        self.assertIn('prefers-reduced-motion:reduce',self.style)
        self.assertIn('.fv-hf__skip:focus',self.style)
        self.assertIn('color:var(--hf-ink)',self.style)

    def test_unchanged_historical_boundary(self):
        self.assertIn('Does not establish individual later fates',self.ledger['chronology'][1]['limitation'])

if __name__=='__main__':unittest.main()
