"""Static accessible preview and evidence link integrity checks."""
import importlib.util
import json
from pathlib import Path
import unittest

BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('per_issue_preflight',BASE/'per_issue_preflight.py')
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
import sys
sys.path.insert(0,str(BASE))
from build_review_board import render

class BoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m=json.loads((BASE/'fixtures'/'manifest_snapshot.json').read_text(encoding='utf-8'))
        cls.a=json.loads((BASE/'edition_attestations.json').read_text(encoding='utf-8'))
        cls.l=json.loads((BASE/'canonical_cta_ledger.json').read_text(encoding='utf-8'))
        cls.html=render(cls.m,cls.a,cls.l)

    def test_actual_manifest_content_present(self):
        for entry in self.m['issues']:
            self.assertIn(entry['subject'].replace("'",'&#x27;'),self.html)

    def test_six_semantic_cards(self):
        self.assertEqual(self.html.count('<article class="card '),6)
        self.assertEqual(self.html.count('HELD — NOT SENT'),6)

    def test_no_active_commercial_links_or_external_dependencies(self):
        self.assertNotIn('<script',self.html)
        self.assertNotIn('https://zen12.com',self.html)
        self.assertNotIn('https://hypnosislive.com',self.html)
        self.assertNotIn('src="https://',self.html)
        self.assertNotIn('pixel.gif',self.html)

    def test_no_private_data_in_artifact(self):
        self.assertNotIn('@gmail.com',self.html)
        self.assertNotIn('WordPress.com on',self.html)
        self.assertNotIn('tracking_id',self.html)

    def test_accessible_review_navigation(self):
        for fragment in ['lang="en"','viewport','href="#main"','id="main"','aria-labelledby="issue-1"','details','summary',':focus-visible','prefers-reduced-motion']:
            self.assertIn(fragment,self.html)

    def test_offline_render_is_deterministic(self):
        self.assertEqual(self.html,render(self.m,self.a,self.l))

    def test_ledger_is_unique_and_source_grounded(self):
        self.assertEqual([e['number'] for e in self.l['entries']],list(range(1,7)))
        self.assertEqual(len({e['number'] for e in self.l['entries']}),6)
        for e in self.l['entries']:
            self.assertTrue(all(url.startswith('https://') for url in e['source_urls']))
            self.assertTrue(e['source_titles'])

    def test_commercial_destinations_never_exposed(self):
        for n in (3,5):
            self.assertTrue(self.l['entries'][n-1]['cta_expected'].startswith('[['))
            self.assertIn('Blocked:',self.l['entries'][n-1]['destination_status'])

    def test_live_editorial_links_match_manifest(self):
        for n in (1,2,4,6):
            self.assertEqual(self.l['entries'][n-1]['cta_expected'],self.m['issues'][n-1]['editorial_cta'])
            self.assertTrue(self.m['issues'][n-1]['editorial_cta'].startswith('https://finalvestige.com/'))

    def test_research_does_not_substitute_vendor_efficacy(self):
        for n in (3,5):
            self.assertTrue(any('NCCIH' in s for s in self.l['entries'][n-1]['source_titles']))

if __name__=='__main__':unittest.main()
