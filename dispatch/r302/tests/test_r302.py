"""Offline source, email-safe specimen, and fatal release redline checks. No sends."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

R = Path(__file__).resolve().parents[1]
HTML = (R / 'issue04-alternative.html').read_text(encoding='utf-8')
PLAIN = (R / 'issue04-alternative.txt').read_text(encoding='utf-8')
README = (R / 'README.md').read_text(encoding='utf-8')
ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
SOURCES = [
    'https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/chro.html',
    'https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/invest.html',
    'https://nssdc.gsfc.nasa.gov/planetary/lunar/apollo1info.html',
    'https://www.nasa.gov/history/55-years-ago-the-apollo-1-fire-and-its-aftermath/',
]

class LinkAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links=[]; self.banned=[]; self.lang=False; self.tables=[]; self.h1s=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if tag == 'html' and a.get('lang') == 'en':self.lang=True
        if tag == 'h1':self.h1s+=1
        if tag == 'a':self.links.append(a.get('href',''))
        if tag == 'table':self.tables.append(a.get('role'))
        if tag in ('script','form','iframe','img','video','audio','input','button'):
            self.banned.append(tag)

class ReleaseGuards(unittest.TestCase):
    def setUp(self):
        self.parser=LinkAudit(); self.parser.feed(HTML)
    def test_one_primary_article_link(self):
        self.assertEqual(self.parser.links.count(ARTICLE),1)
    def test_plain_cta_matches(self):
        self.assertEqual(PLAIN.count(ARTICLE),1)
    def test_readable_subject(self):
        subject=re.search(r'^Subject: (.+)$',PLAIN,re.M).group(1)
        self.assertEqual(subject,'The hatch and the missing spark')
        self.assertLessEqual(len(subject),65)
        self.assertIn(subject,HTML)
    def test_preheader_is_proposed_not_verified(self):
        self.assertIn('Preheader: What NASA', PLAIN)
        self.assertIn('preheader field verified',README)
    def test_no_fourteen_second_claim(self):
        self.assertNotRegex(HTML+r'\n'+PLAIN,r'(?i)fourteen seconds|14 seconds')
    def test_approximate_seventeen_second_claim(self):
        self.assertIn('about 17 seconds',PLAIN)
        self.assertIn('about 17 seconds',HTML)
    def test_ninety_seconds_is_ideal(self):
        self.assertIn('90 seconds in ideal conditions',PLAIN)
        self.assertIn('90 seconds in ideal conditions',HTML)
    def test_not_exact_ignition(self):
        self.assertIn('could not be positively identified',PLAIN)
        self.assertIn('could not be positively identified',HTML)
    def test_no_undocumented_transcript(self):
        self.assertNotIn('we have a bad fire',PLAIN.lower())
        self.assertNotIn('we have a bad fire',HTML.lower())
    def test_all_historical_sources_present(self):
        for source in SOURCES:
            with self.subTest(source=source):
                self.assertIn(source,PLAIN)
                self.assertIn(source,HTML)
                self.assertIn(source,README)
    def test_single_primary_action_not_merchant(self):
        self.assertEqual(len(self.parser.links),len(SOURCES)+1)
        for link in self.parser.links:
            self.assertTrue(link==ARTICLE or link in SOURCES)
    def test_html_no_unsafe_tags(self):
        self.assertEqual(self.parser.banned,[])
    def test_html_accessibility_basics(self):
        self.assertTrue(self.parser.lang)
        self.assertEqual(self.parser.h1s,1)
        self.assertEqual(self.parser.tables,['presentation','presentation'])
        self.assertIn('name="viewport"',HTML)
    def test_legal_hold_both_formats(self):
        for content in (PLAIN,HTML):
            self.assertIn('[[VALID_POSTAL_ADDRESS_REQUIRED]]',content)
            self.assertIn('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]',content)
    def test_no_merchant_link_or_tracking(self):
        for content in (PLAIN,HTML):
            self.assertNotRegex(content,r'(?i)utm_(source|campaign|content)=|clickbank|hoplink|inspire3\.com/affiliate')
    def test_all_formats_explicit_unsent(self):
        self.assertIn('NOT APPROVED OR SENT',PLAIN)
        self.assertIn('UNSENT REVIEW',HTML)
        self.assertIn('NOT_ADOPTED',README)
    def test_revenue_missing_not_invented(self):
        self.assertIn('NOT COMPUTABLE',README)
        self.assertIn('actual eligible subscriber count UNKNOWN',README)
    def test_original_master_not_rewritten(self):
        self.assertIn('master Issue 04',README)
        self.assertIn('NOT_ADOPTED',README)
    def test_no_double_optin_assumption(self):
        self.assertNotIn('three confirmed subscribers',README.lower())
    def test_consent_and_commerce_gates_still_closed(self):
        for phrase in ('merchant email rights','functional unsubscribe','Actual','HOLD_UNSENT'):
            self.assertIn(phrase.lower(),README.lower())

if __name__=='__main__':
    unittest.main()
