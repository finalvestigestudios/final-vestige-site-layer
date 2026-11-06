import unittest
from email.message import EmailMessage
from received_eml_preflight import inspect, LinkText


def fixture(with_unsub=True, with_disclosure=True):
    m=EmailMessage()
    m['From']='Final Vestige Studios <donotreply@wordpress.com>'
    m['To']='synthetic@example.test'
    m['Subject']='The mind is not a camera'
    m['List-Unsubscribe']='<https://example.test/unsubscribe>'
    m.set_content('Editorial letter. Unsubscribe at your subscription settings.' + (' If you buy, we may earn a commission.' if with_disclosure else ''))
    u='<a href="https://example.test/unsubscribe">Unsubscribe</a>' if with_unsub else 'Preferences'
    m.add_alternative('<html><body><p>Research and evidence.</p><a href="https://finalvestige.com/2026/11/02/change-blindness/">Read the investigation</a><p>'+u+'</p>'+('<p>If you purchase we may earn a commission.</p>' if with_disclosure else '')+'</body></html>',subtype='html')
    return m.as_bytes()

class InboundTests(unittest.TestCase):
    def test_fail_closed_default(self):
        a=inspect(fixture())
        self.assertEqual(a['release_decision'],'HOLD_UNSENT')
        self.assertIn('evidence_is_genuine_received_mail_attested', a['failed_gates'])
    def test_always_hold_with_all_attestations(self):
        fields=['genuine_received_mail','fv_postal_line_observed','fv_postal_address_verified','unsubscribe_worked','provider_email_eligible','welcome_received','founder_final_approval','merchant_email_permission','merchant_earning_link']
        a={k:True for k in fields};a['synthetic_fixture']=False
        r=inspect(fixture(),attest=a)
        self.assertEqual(r['release_decision'],'HOLD_UNSENT')
    def test_synthetic_never_counts(self):
        self.assertFalse(inspect(fixture(),attest={'genuine_received_mail':True,'synthetic_fixture':True})['checks']['evidence_is_genuine_received_mail_attested'])
    def test_no_pii_in_output(self):
        import json
        s=json.dumps(inspect(fixture()))
        self.assertNotIn('synthetic@example',s)
        self.assertNotIn('donotreply@wordpress',s)
        self.assertNotIn('The mind is not',s)
    def test_has_firstparty(self):
        self.assertTrue(inspect(fixture())['checks']['first_party_cta_present'])
    def test_plain_and_html_required(self):
        m=EmailMessage();m['From']='Final Vestige Studios <donotreply@wordpress.com>';m['Subject']='Test';m.set_content('Text only. Unsubscribe.')
        self.assertFalse(inspect(m.as_bytes())['checks']['has_html_part'])
    def test_commercial_requires_partner(self):
        r=inspect(fixture(),kind='commercial')
        self.assertIn('named_merchant_email_permission_attested',r['failed_gates'])
        self.assertIn('named_merchant_earning_link_attested',r['failed_gates'])
    def test_commercial_disclosure_missing(self):
        self.assertIn('commercial_disclosure_visible',inspect(fixture(with_disclosure=False),kind='commercial')['failed_gates'])
    def test_unsubscribe_text_without_link_fails(self):
        self.assertIn('unsubscribe_clickable_in_html',inspect(fixture(with_unsub=False))['failed_gates'])
    def test_headers_do_not_prove_optout(self):
        r=inspect(fixture())
        self.assertTrue(r['checks']['list_unsubscribe_header_present'])
        self.assertFalse(r['checks']['unsubscribe_completed_in_authorized_browser_attested'])
    def test_html_parser_omits_script(self):
        h=LinkText();h.feed('<script>Unsubscribe</script><a href="https://example.test/ok">Learn</a>')
        self.assertNotIn('Unsubscribe',''.join(h.visible))
    def test_placeholder_fails(self):
        b=fixture().replace(b'Research and evidence.',b'Research and evidence. [INSERT_POSTAL]')
        self.assertIn('has_no_placeholders',inspect(b)['failed_gates'])
    def test_too_large_rejected(self):
        with self.assertRaises(ValueError):inspect(b'x'*2_000_001)
    def test_bad_kind_rejected(self):
        with self.assertRaises(ValueError):inspect(fixture(),kind='transaction')
    def test_no_vendor_link_when_inactive(self):
        self.assertTrue(inspect(fixture(),kind='commercial')['checks']['no_activated_affiliate_href'])
    def test_no_automatic_release_even_in_commercial(self):
        self.assertEqual(inspect(fixture(),kind='commercial')['release_decision'],'HOLD_UNSENT')

if __name__ == '__main__':unittest.main()
