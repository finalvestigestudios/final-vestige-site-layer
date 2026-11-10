import unittest
from email.message import EmailMessage
from inbox_evidence import inspect_eml

EXAMPLE_ADDRESS = 'TEST ONLY — 1 Example Road, Example City, CA 00000'

def fixture(*, sender='Final Vestige Studios', subject='A documented finding',
            html=None, plain=None, address=EXAMPLE_ADDRESS, unsub=True,
            additional_link='', header=True):
    m = EmailMessage()
    m['From'] = f'{sender} <synthetic@example.invalid>'
    m['To'] = 'PRIVATE-DO-NOT-LOG@example.invalid'
    m['Subject'] = subject
    if header: m['List-Unsubscribe'] = '<https://finalvestige.com/unsubscribe/fake-token>'
    content = plain if plain is not None else f'Archive evidence. {address}\nUnsubscribe via the site footer.'
    m.set_content(content)
    markup = html if html is not None else (f'<p>Archive evidence</p><p>{address}</p>' +
       ('<p><a href="https://finalvestige.com/unsubscribe/fake-token">Unsubscribe</a></p>' if unsub else '') +
       (f'<p><a href="{additional_link}">More information</a></p>' if additional_link else ''))
    m.add_alternative(markup, subtype='html')
    return m.as_bytes()

class OfflineInspectorTests(unittest.TestCase):
    def check(self, **kwargs):
        return inspect_eml(fixture(**kwargs), publisher_postal_address=EXAMPLE_ADDRESS)
    def test_all_synthetic_gates_still_hold(self):
        d=self.check();self.assertEqual(d['release'], 'HOLD_UNSENT');self.assertIn('FOUNDER_FINAL_SEND_APPROVAL_REQUIRED', d['blockers'])
    def test_privacy_sensitive_headers_not_emitted(self):
        d=self.check();self.assertNotIn('PRIVATE-DO-NOT-LOG',repr(d));self.assertNotIn('example.invalid',repr(d));self.assertNotIn('synthetic@',repr(d))
    def test_sha256_evidence_trace(self):
        d=self.check();self.assertEqual(len(d['raw_sha256']), 64)
    def test_subject_missing(self):
        data=fixture().replace(b'Subject: A documented finding\n', b'')
        d=inspect_eml(data,publisher_postal_address=EXAMPLE_ADDRESS);self.assertIn('SENDER_OR_SUBJECT_NOT_AUTHENTICATED',d['blockers'])
    def test_sender_mismatch(self):
        self.assertIn('SENDER_OR_SUBJECT_NOT_AUTHENTICATED',self.check(sender='Someone Else')['blockers'])
    def test_missing_postal_address(self):
        self.assertIn('STUDIO_POSTAL_ADDRESS_UNVERIFIED',self.check(address='not the signed-off address')['blockers'])
    def test_no_provided_address_never_valid(self):
        d=inspect_eml(fixture());self.assertFalse(d['visible_studio_postal_exact_match'])
    def test_visible_unsubscribe_required(self):
        d=self.check(unsub=False,plain='This copy has no opt out.');self.assertIn('VISIBLE_UNSUBSCRIBE_NOT_ESTABLISHED',d['blockers'])
    def test_header_only_not_proof(self):
        d=self.check(unsub=False,plain='Ordinary content.');self.assertTrue(d['list_unsubscribe_header_present']);self.assertIn('VISIBLE_UNSUBSCRIBE_NOT_ESTABLISHED',d['blockers'])
    def test_external_link_detected(self):
        d=self.check(additional_link='https://zen12.com/hnp');self.assertIn('NON_OWNED_OR_UNAPPROVED_DESTINATION',d['blockers'])
    def test_host_lookalike_detected(self):
        d=self.check(additional_link='https://finalvestige.com.evil.invalid/x');self.assertEqual(d['external_or_unsafe_destination_count'],1)
    def test_javascript_detected(self):
        d=self.check(additional_link='javascript:alert(1)');self.assertIn('NON_OWNED_OR_UNAPPROVED_DESTINATION',d['blockers'])
    def test_subdomain_allowed_without_earning_authorization(self):
        d=self.check(additional_link='https://sub.finalvestige.com/p');self.assertEqual(d['external_or_unsafe_destination_count'],0);self.assertEqual(d['release'],'HOLD_UNSENT')
    def test_empty_rejected(self):
        with self.assertRaises(ValueError):inspect_eml(b'')
    def test_large_rejected(self):
        with self.assertRaises(ValueError):inspect_eml(b'a'*2_000_001)
    def test_never_calls_send_or_provider(self):
        import inspect
        from inbox_evidence import inspect_eml as fn
        s=inspect.getsource(fn);self.assertNotIn('requests.',s);self.assertNotIn('smtplib',s)
    def test_unsubscribe_is_not_functionality_proof(self):
        d=self.check();self.assertIn('UNSUBSCRIBE_FUNCTION_NOT_TESTED',d['blockers'])
    def test_hidden_unsub_is_not_counted(self):
        d=self.check(unsub=False,plain='Ordinary note.',html='<div style="display: none">Unsubscribe</div>');self.assertIn('VISIBLE_UNSUBSCRIBE_NOT_ESTABLISHED',d['blockers'])

if __name__=='__main__':unittest.main()
