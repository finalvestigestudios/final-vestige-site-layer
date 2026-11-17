"""Non-sending offline R412 gates: structural evidence, not legal approval."""
import json
import re
import unittest
from pathlib import Path
from html.parser import HTMLParser

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parent / 'campaign-2026-mind'
ISSUE = (HERE/'ISSUE04_APOLLO_OPTIONAL.md').read_text()
HTML = (HERE/'ISSUE04_APOLLO_OFFLINE.html').read_text()
TXT = (HERE/'ISSUE04_APOLLO_OFFLINE.txt').read_text()
LEDGER = json.loads((HERE/'CLAIM_TIMELINE_AND_RELEASE.json').read_text())

class AnchorCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag == 'a': self.links.append(dict(attrs).get('href', ''))

class ReleaseTests(unittest.TestCase):
    def test_canonical_4_2_unchanged(self):
        j=json.loads((CAMPAIGN/'manifest.json').read_text())
        self.assertEqual(j['mix']['editorial'],4)
        self.assertEqual(j['mix']['commercial_review_pending'],2)
        self.assertEqual(len(j['issues']),6)
        self.assertTrue(all(i['publish_state']=='hold' for i in j['issues']))
    def test_canonical_04_not_overwritten(self):
        original=(CAMPAIGN/'issues/04-the-hatch-and-the-spark.md').read_text()
        self.assertIn('Fourteen seconds. A much longer explanation.',original)
        self.assertIn('the spark', ISSUE.lower())
    def test_source_precision(self):
        self.assertEqual(LEDGER['later_report_to_rupture_seconds'],14.7)
        self.assertEqual(LEDGER['preliminary_interval_seconds'],14)
        self.assertTrue(all(not e['ignition_proven'] for e in LEDGER['events_gmt_1967_01_27']))
        self.assertIn('23:31:04.7',ISSUE)
        self.assertIn('23:31:19.4',ISSUE)
        self.assertIn('not proof',ISSUE.lower())
        self.assertIn('not conclusively',ISSUE.lower())
    def test_single_editorial_destination_and_research_sources(self):
        p=AnchorCollector();p.feed(HTML)
        self.assertEqual(len(p.links),5)
        self.assertEqual(len([x for x in p.links if x.startswith('https://finalvestige.com/')]),1)
        self.assertEqual(len([x for x in p.links if 'nasa.gov/' in x]),4)
        self.assertTrue(all(x.startswith('https://') for x in p.links))
    def test_format_and_visual_accessibility_basics(self):
        self.assertIn('lang="en"',HTML)
        self.assertIn('role="presentation"',HTML)
        self.assertIn('name="viewport"',HTML)
        self.assertIn('<h1',HTML)
        self.assertNotRegex(HTML,r'<(script|iframe|form|img)\b')
        self.assertNotIn('utm_',HTML)
        self.assertNotIn('tracking',HTML.lower())
        self.assertIn('Proposed preheader',HTML)
    def test_parity_of_critical_timeline_and_source_urls(self):
        for token in ['23:30:54.8','23:31:04.7','23:31:19.4',
            'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/',
            'https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html']:
            for material in (ISSUE, HTML, TXT):
                self.assertIn(token,material)
    def test_no_merchant_activation(self):
        for material in (ISSUE,HTML,TXT):
            self.assertNotRegex(material,r'https?://(?:www\.)?(?:zen12|hypnosislive|inspire3)\.com')
            self.assertNotIn('affiliate link',material.lower())
    def test_all_permissions_fail_closed(self):
        self.assertEqual(LEDGER['status'],'NOT_ADOPTED_HOLD_UNSENT')
        self.assertTrue(LEDGER['campaign']['all_six_hold'])
        self.assertFalse(any(LEDGER['permissions'].values()))
        for material in (ISSUE,HTML,TXT):
            self.assertIn('[[VALID_FV_POSTAL_ADDRESS_REQUIRED]]',material)
            self.assertIn('[[LIVE_JETPACK_UNSUBSCRIBE_REQUIRED]]',material)
    def test_subject_truth_not_false_precision(self):
        subj=re.search(r'^\*\*Subject:\*\* (.+)$',ISSUE,re.M).group(1)
        self.assertLessEqual(len(subj),60)
        self.assertNotIn('Fourteen seconds',subj)
        self.assertIn('spark',subj.lower())
        self.assertIn('preheader',ISSUE.lower())
        self.assertIn('not a verified Jetpack',ISSUE)
    def test_scoped_only_and_one_cta(self):
        self.assertIn('ONE EDITORIAL CTA',TXT)
        self.assertIn('ONE',TXT)
        self.assertIn('Read our investigation',ISSUE)
        self.assertIn('NOT_ADOPTED',ISSUE)
        self.assertIn('HOLD_UNSENT',ISSUE)

if __name__ == '__main__': unittest.main()
