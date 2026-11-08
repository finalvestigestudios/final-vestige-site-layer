"""Synthetic fixtures only: no subscribers, real addresses, deliverability or sends."""
import unittest
from email.message import EmailMessage
from receipt_review import audit_mime

def msg(text='', html=None, unsub=None):
    m = EmailMessage()
    m['From'] = 'Example Sender <noreply@example.invalid>'
    m['To'] = 'Private Test <receiver@example.invalid>'
    m['Subject'] = 'A synthetic newsletter specimen'
    if unsub:
        m['List-Unsubscribe'] = unsub
    m.set_content(text)
    if html is not None:
        m.add_alternative(html, subtype='html')
    return m.as_bytes()

class ReceiptReviewTests(unittest.TestCase):
    def test_plain_content_is_not_receipt_proof(self):
        r = audit_mime(msg('Unsubscribe from this list.'))
        self.assertTrue(r['unsub_body_text_present_not_functional_proof'])
        self.assertFalse(r['ready_to_send'])
        self.assertFalse(r['has_html_part'])

    def test_header_not_functional_proof(self):
        r = audit_mime(msg('Hello', unsub='<https://example.invalid/unsubscribe>'))
        self.assertTrue(r['unsub_header_present_not_functional_proof'])
        self.assertTrue(r['requires_optout_operation_verification'])
        self.assertFalse(r['ready_to_send'])

    def test_html_readable_disclosure(self):
        r = audit_mime(msg('Hello', '<html><body><p>If you buy, we may earn a commission.</p><p>Unsubscribe</p></body></html>'))
        self.assertTrue(r['has_html_part'])
        self.assertTrue(r['prospective_commission_disclosure_present'])
        self.assertTrue(r['has_plaintext_part'])

    def test_hidden_script_not_evidence(self):
        r = audit_mime(msg('Hello', '<script>we may earn a commission</script><p>Hi</p>'))
        self.assertFalse(r['prospective_commission_disclosure_present'])

    def test_hard_stop_detected(self):
        r = audit_mime(msg('[[VALID_POSTAL_ADDRESS_REQUIRED]]'))
        self.assertTrue(r['hard_stop_placeholder_present'])

    def test_no_pii_in_result(self):
        r = audit_mime(msg('Private user: realname@example.invalid'))
        self.assertNotIn('example.invalid', str(r))
        self.assertNotIn('realname', str(r))

    def test_large_payload_rejected(self):
        with self.assertRaises(ValueError):
            audit_mime(b'X' * 3_000_001)

    def test_empty_message_not_proven(self):
        r = audit_mime(b'\r\n')
        self.assertFalse(r['mime_parse_ok'])
        self.assertFalse(r['ready_to_send'])

if __name__ == '__main__':
    unittest.main()
