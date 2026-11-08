"""Native offline tests: source-sensitive, intentionally fail-closed reviewer checks."""
import json
import re
import unittest
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse

P = Path(__file__).parent
HOLD = 'HOLD_UNSENT'
CTA = 'https://finalvestige.com/2026/11/02/change-blindness/'

class Elements(HTMLParser):
    def __init__(self):
        super().__init__(); self.tags=[]; self.links=[]; self.attrs=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs);self.tags.append(tag);self.attrs.append((tag,d))
        if tag=='a':self.links.append(d.get('href',''))

def evaluate(ledger, html, md, plain):
    """Return diagnostic flags only. Never return a production-send approval."""
    bad=[]
    if ledger['release']['status'] != HOLD:bad.append('release-status-not-held')
    if ledger['canonical_campaign']['allocation']!={'editorial':[1,2,4,6],'commercial_reserved':[3,5]}:bad.append('allocation-changed')
    if ledger['canonical_campaign']['rewrite_approved'] or ledger['alternate']['approved_substitution']:bad.append('unauthorized-alternative')
    if ledger['alternate']['primary_cta']!=CTA or CTA not in plain or CTA not in html or CTA not in md:bad.append('cta-drift')
    if ledger['attribution_contract']['revenue_per_1000_qualified_sessions'] is not None:bad.append('fake-revenue')
    if any(value is True for key, value in ledger['merchant'].items() if key != 'selected_offer'):bad.append('unsupported-merchant-proof')
    if ledger['provider']['welcome_received_verified'] or ledger['provider']['email_eligible_population_verified'] or ledger['provider']['native_jetpack_email_preview_verified']:bad.append('fake-provider-proof')
    for val in ['[[VALID_POSTAL_ADDRESS_REQUIRED]]','[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]']:
        if any(val not in x for x in (html,md,plain)):bad.append('removed-hard-hold:'+val)
    p=Elements();p.feed(html)
    if any(tag in p.tags for tag in ['script','iframe','form','video','audio']):bad.append('unsafe-email-markup')
    if len([href for href in p.links if href==CTA])<1:bad.append('missing-primary-cta')
    if any(('zen12.com' in href or 'affiliates.inspire3.com' in href or 'awin1.com' in href) for href in p.links):bad.append('merchant-link-in-email')
    if not all(urlparse(u).scheme=='https' for u in p.links):bad.append('insecure-link')
    return {'status':HOLD,'failures':bad}

class R177(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md=(P/'ISSUE_06_CANDIDATE.md').read_text()
        cls.plain=(P/'ISSUE_06_PLAINTEXT.txt').read_text()
        cls.html=(P/'ISSUE_06_PREVIEW.html').read_text()
        cls.ledger=json.loads((P/'RELEASE_AND_FUNNEL_LEDGER.json').read_text())
    def verdict(self,ledger=None,html=None,md=None,plain=None):
        return evaluate(ledger or self.ledger,html or self.html,md or self.md,plain or self.plain)
    def test_holds_even_when_clean(self):self.assertEqual(self.verdict(),{'status':HOLD,'failures':[]})
    def test_canonical_pr(self):self.assertEqual(self.ledger['canonical_campaign']['pr'],175)
    def test_canonical_sha(self):self.assertEqual(len(self.ledger['canonical_campaign']['sha']),40)
    def test_four_two_allocation(self):self.assertEqual(self.ledger['canonical_campaign']['allocation']['editorial'],[1,2,4,6])
    def test_unapproved_substitution(self):self.assertFalse(self.ledger['alternate']['approved_substitution'])
    def test_subject_true(self):self.assertIn('**Subject:** The witness who missed the switch',self.md)
    def test_subject_short(self):self.assertLessEqual(len('The witness who missed the switch'),54)
    def test_preheader_short(self):self.assertLessEqual(len('A 1998 campus experiment offers a better ending than another focus promise.'),110)
    def test_html_viewport(self):self.assertIn('name="viewport"',self.html)
    def test_html_language(self):self.assertIn('lang="en"',self.html)
    def test_html_role(self):self.assertIn('role="presentation"',self.html)
    def test_readonly_cta(self):self.assertIn(CTA,self.plain)
    def test_source_1998(self):self.assertIn('https://doi.org/10.3758/BF03208840',self.md)
    def test_source_limits(self):self.assertIn('first experiment',self.plain)
    def test_no_clinical_claim(self):self.assertIn('not a controlled experiment',self.plain)
    def test_no_repeat_signup(self):self.assertNotIn('Subscribe today',self.plain)
    def test_no_fake_numbers(self):self.assertIsNone(self.ledger['attribution_contract']['revenue_per_1000_qualified_sessions'])
    def test_nonadditive(self):self.assertFalse(self.ledger['provider']['counts_are_additive'])
    def test_three_confirmed_not_eligible(self):self.assertFalse(self.ledger['provider']['email_eligible_population_verified'])
    def test_hard_hold_addr(self):self.assertIn('[[VALID_POSTAL_ADDRESS_REQUIRED]]',self.md)
    def test_hard_hold_unsub(self):self.assertIn('[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]',self.md)
    def test_no_merchant_link(self):self.assertNotIn('zen12.com/',self.html)
    def test_reject_fake_merchant_approval(self):
        v=json.loads(json.dumps(self.ledger));v['merchant']['email_channel_allowed_for_fv']=True
        self.assertIn('unsupported-merchant-proof',self.verdict(ledger=v)['failures'])
    def test_reject_fake_revenue(self):
        v=json.loads(json.dumps(self.ledger));v['attribution_contract']['revenue_per_1000_qualified_sessions']=500
        self.assertIn('fake-revenue',self.verdict(ledger=v)['failures'])
    def test_reject_fake_received_welcome(self):
        v=json.loads(json.dumps(self.ledger));v['provider']['welcome_received_verified']=True
        self.assertIn('fake-provider-proof',self.verdict(ledger=v)['failures'])
    def test_reject_switched_cta(self):self.assertIn('cta-drift',self.verdict(plain=self.plain.replace(CTA,'https://example.com'))['failures'])
    def test_reject_removed_postal(self):self.assertTrue(any('removed-hard-hold' in x for x in self.verdict(html=self.html.replace('[[VALID_POSTAL_ADDRESS_REQUIRED]]','SECRET'))['failures']))
    def test_reject_hidden_executable(self):self.assertIn('unsafe-email-markup',self.verdict(html=self.html+'<script>alert(1)</script>')['failures'])
    def test_reject_unauthorized_merchant_link(self):self.assertIn('merchant-link-in-email',self.verdict(html=self.html+'<a href="https://zen12.com/">BUY</a>')['failures'])
    def test_reject_unauthorized_substitution(self):
        v=json.loads(json.dumps(self.ledger));v['alternate']['approved_substitution']=True
        self.assertIn('unauthorized-alternative',self.verdict(ledger=v)['failures'])

if __name__=='__main__':unittest.main(verbosity=2)
