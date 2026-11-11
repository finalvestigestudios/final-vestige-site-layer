"""Synthetic-only adversarial tests for independently reviewed R281 inspector."""
import unittest
from email.message import EmailMessage
from independent_mime_review import inspect_bytes, allowed_url, HOLD

P = 'Record. Final Vestige Studios, 123 Test Street, Town, CA 90000. Unsubscribe: https://wordpress.com/unsubscribe/abc'
H = '<p>Record. Final Vestige Studios, 123 Test Street, Town, CA 90000.</p><a href="https://wordpress.com/unsubscribe/abc">Unsubscribe</a>'

def sample(plain=P, html=H, *, sender='Final Vestige <donotreply@wordpress.com>', header=True):
    m = EmailMessage()
    m['From'] = sender
    m['To'] = 'Subscriber <reader@example.org>'
    m['Date'] = 'Wed, 11 Nov 2026 13:00:00 +0000'
    m['Subject'] = 'An evidence-led Dispatch'
    m['Message-ID'] = '<sample@wordpress.com>'
    if header:
        m['List-Unsubscribe'] = '<https://wordpress.com/unsubscribe/abc>'
    m.set_content(plain)
    m.add_alternative(html, subtype='html')
    return m.as_bytes()

class SafeURLs(unittest.TestCase):
    def test_exact_hosts(self):
        for host in ('finalvestige.com', 'www.finalvestige.com', 'wordpress.com', 'subscriptions.wordpress.com'):
            with self.subTest(host=host): self.assertTrue(allowed_url('https://'+host+'/unsubscribe'))
    def test_phishing(self):
        for u in ('http://finalvestige.com/unsub','https://finalvestige.com.evil.test/unsub',
                  'https://finalvestige.com@evil.test/unsub', 'https://evil.test@finalvestige.com/unsub',
                  'https://finalvestige.com:8080/unsub', 'https://finalvestige.com/[[REQUIRED]]',
                  'javascript:alert(1)', 'https://www.finalvestige.com.evil.test/unsub'):
            with self.subTest(url=u): self.assertFalse(allowed_url(u))

class SyntheticEvidence(unittest.TestCase):
    def test_complete_fixture_is_never_authorization(self):
        x=inspect_bytes(sample());self.assertTrue(x['structural_checks_pass']);self.assertEqual(x['release_state'],HOLD)
        self.assertTrue(all(x[k] is False for k in ('sender_authenticated','real_received_jetpack_message_verified','business_postal_ownership_verified','unsubscribe_functional_verified','subscriber_eligible_and_consented','affiliate_email_permission_verified','founder_approved_send')))
    def test_no_private_content_returned(self):
        s=repr(inspect_bytes(sample()));self.assertNotIn('reader@example',s);self.assertNotIn('123 Test',s);self.assertNotIn('donotreply@',s)
    def test_untrusted_phishing_url(self):
        x=inspect_bytes(sample(html=H.replace('wordpress.com/unsubscribe','wordpress.com.evil.test/unsubscribe')))
        self.assertFalse(x['checks']['accessible_https_optout_candidate'])
    def test_unsubscribe_path_without_label(self):
        x=inspect_bytes(sample(html=H.replace('>Unsubscribe<','>Read the investigation<')))
        self.assertFalse(x['checks']['accessible_https_optout_candidate'])
    def test_visible_label_not_linked(self):
        x=inspect_bytes(sample(html=H.replace('>Unsubscribe<','>Read</a><p>Unsubscribe<')))
        self.assertFalse(x['checks']['accessible_https_optout_candidate'])
    def test_hidden_postal(self):
        x=inspect_bytes(sample(html=H.replace('123 Test Street','<span hidden>123 Test Street</span>')))
        self.assertFalse(x['checks']['publisher_postal_candidate_in_both_parts']);self.assertFalse(x['checks']['no_obscured_html'])
    def test_hidden_unsub_link(self):
        x=inspect_bytes(sample(html=H.replace('<a href','<a aria-hidden="true" href')))
        self.assertFalse(x['checks']['accessible_https_optout_candidate'])
    def test_css_hidden_unsub_link(self):
        x=inspect_bytes(sample(html=H.replace('<a href','<a style="display:/**/none" href')))
        self.assertFalse(x['checks']['accessible_https_optout_candidate'])
    def test_css_styles_are_manual_review(self):
        x=inspect_bytes(sample(html='<style>.footer{display:none}</style>'+H))
        self.assertFalse(x['checks']['no_obscured_html'])
    def test_template_hidden(self):
        x=inspect_bytes(sample(html=H.replace('<a href','<template><a href')+'</template>'))
        self.assertFalse(x['checks']['accessible_https_optout_candidate'])
    def test_no_html_postal_but_plaintext_has_it(self):
        x=inspect_bytes(sample(html=H.replace('123 Test Street','not supplied')))
        self.assertFalse(x['checks']['publisher_postal_candidate_in_both_parts'])
    def test_missing_header_does_not_auto_fail_body(self):
        x=inspect_bytes(sample(header=False));self.assertFalse(x['checks']['list_unsubscribe_header_candidate']);self.assertTrue(x['structural_checks_pass'])
    def test_unsafe_form(self):
        x=inspect_bytes(sample(html=H+'<form></form>'));self.assertFalse(x['checks']['no_unsafe_markup'])
    def test_attachment(self):
        m=EmailMessage();m['From']='A <a@wordpress.com>';m['To']='b@example.org';m['Subject']='Hi';m['Date']='Wed, 11 Nov 2026 13:00:00 +0000';m['Message-ID']='<test@wordpress.com>';m.set_content(P);m.add_alternative(H,subtype='html');m.add_attachment(b'secret',maintype='application',subtype='octet-stream',filename='subscribers.csv');self.assertFalse(inspect_bytes(m.as_bytes())['checks']['no_attachments'])
    def test_size_limit(self):
        with self.assertRaises(ValueError):inspect_bytes(b'a'*2_000_001)
    def test_nonbytes(self):
        with self.assertRaises(ValueError):inspect_bytes('not bytes')

if __name__ == '__main__':unittest.main()
