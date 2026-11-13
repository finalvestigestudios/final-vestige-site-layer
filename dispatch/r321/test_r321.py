"""Read-only regression tests for the optional R321 historical Dispatch review."""
from pathlib import Path
from html.parser import HTMLParser
import unittest, json

ROOT=Path(__file__).resolve().parent
MASTER=ROOT.parent/'campaign-2026-mind'

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]; self.links=[]; self.headings=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs); self.tags.append(tag)
        if tag=='a': self.links.append(a)
        if tag in ('h1','h2','h3'): self.headings.append(tag)

class R321Guards(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/'issue02-proposed.html').read_text(encoding='utf-8')
        cls.markdown=(ROOT/'issue02-proposed.md').read_text(encoding='utf-8')
        cls.plain=(ROOT/'issue02-proposed.txt').read_text(encoding='utf-8')
        cls.dom=LinkParser(); cls.dom.feed(cls.html)
        cls.manifest=json.loads((MASTER/'manifest.json').read_text(encoding='utf-8'))

    def test_original_six_issue_mix_unchanged(self):
        issues=self.manifest['issues']
        self.assertEqual(len(issues),6)
        self.assertEqual(sum(i['kind']=='editorial' for i in issues),4)
        self.assertEqual(sum(i['kind']=='commercial-review-pending' for i in issues),2)
        self.assertEqual(self.manifest['status'],'DRAFT_UNSENT_NO_SCHEDULING')

    def test_master_campaign_still_blocked(self):
        for issue in self.manifest['issues']:
            self.assertEqual(issue['publish_state'],'hold')
            self.assertIsNone(issue['merchant_affiliate_url'])

    def test_subject_preheader_parity(self):
        for s in [self.html,self.markdown,self.plain]:
            self.assertIn('A witness signed. Did that prove anything?',s)
            self.assertIn('Puységur’s 1785 volume preserved written claims, signatures—and failure.',s)

    def test_bibliography_and_failed_prediction(self):
        for item in ['1784–1785','1785','1813','unsuccessful prediction','Louis de Rieux']:
            self.assertIn(item,self.markdown)
        self.assertIn('Wood Library-Museum',self.markdown)
        self.assertIn('Bibliothèque nationale de France',self.markdown)

    def test_one_primary_cta(self):
        links=[a for a in self.dom.links if a.get('data-primary-cta')=='true']
        self.assertEqual(len(links),1)
        self.assertEqual(links[0].get('href'),'https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/')
        self.assertEqual(self.plain.count('EXAMINE THE RECORDS —'),1)

    def test_only_three_disclosed_links(self):
        self.assertEqual(len(self.dom.links),3)
        self.assertTrue(all(a.get('href','').startswith('https://') for a in self.dom.links))
        self.assertTrue(all('utm_' not in a['href'] for a in self.dom.links))

    def test_email_markup_has_no_tracking(self):
        for tag in ('img','script','iframe','form','video','audio'):
            self.assertNotIn(tag,self.dom.tags)
        self.assertNotIn('tracking-pixel',self.html)

    def test_review_accessibility_structure(self):
        self.assertIn('<html lang="en">',self.html)
        self.assertIn('name="viewport"',self.html)
        self.assertIn('role="presentation"',self.html)
        self.assertEqual(self.dom.headings.count('h1'),1)

    def test_non_sending_placeholders_intentionally_present(self):
        for s in [self.html,self.markdown,self.plain]:
            self.assertIn('[[VALID_POSTAL_ADDRESS_REQUIRED]]',s)
            self.assertIn('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]',s)
            self.assertIn('HOLD',s)

    def test_no_unverified_merchant_or_clinical_claim(self):
        for s in [self.html,self.markdown,self.plain]:
            for phrase in ['affiliates.inspire3.com','buy now','guaranteed cure','clinically proven']:
                self.assertNotIn(phrase,s.lower())

    def test_original_issue_02_unchanged(self):
        self.assertIn('Before hypnosis had a name',(MASTER/'issues'/'02-before-hypnosis-had-a-name.md').read_text(encoding='utf-8'))
        self.assertEqual(self.manifest['issues'][1]['subject'],'Before hypnosis had a name')

if __name__=='__main__':
    unittest.main()
