import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import unittest
from email.message import EmailMessage
from received_email_audit import inspect_bytes

class AuditTests(unittest.TestCase):
    def make(self, text='Read the investigation. Our office: 123 Test Street, Anywhere, CA 90000',
             html='<a href="https://finalvestige.com/archive/">Read investigation</a> <a href="https://wordpress.com/unsubscribe?id=SECRET">Unsubscribe</a> 123 Test Street, Anywhere, CA 90000',
             subject='Evidence Dispatch', fixture=False, extra=None):
        m=EmailMessage()
        m['From']='Final Vestige <donotreply@wordpress.com>'
        m['To']='private-user@example.com'
        m['Subject']=subject
        m['Received']='by mx.example.net with ESMTPS'
        m['Authentication-Results']='mx.example.net; dkim=pass'
        m['List-Unsubscribe']='<https://wordpress.com/unsubscribe?token=SECRET>'
        m['List-Unsubscribe-Post']='List-Unsubscribe=One-Click'
        if fixture:m['X-FV-Review-Only']='TRUE'
        if extra: m['X-Source-Test']=extra
        m.set_content(text)
        m.add_alternative('<html><body>'+html+'</body></html>',subtype='html')
        return m.as_bytes()
    def audit(self, data):
        return inspect_bytes(data, expected_subject='Evidence Dispatch',approved_postal_text='123 Test Street, Anywhere, CA 90000')
    def test_clear_structure_does_not_auto_approve(self):
        d=self.audit(self.make())
        self.assertFalse(d['fail_or_unknown'])
        self.assertEqual(d['release_status'],'HOLD_UNSENT')
        self.assertNotEqual(d['actual_delivered'],True)
    def test_fixture_rejected(self):
        self.assertFalse(self.audit(self.make(fixture=True))['checks']['not_fixture'])
    def test_fixture_body_rejected(self):
        self.assertFalse(self.audit(self.make(text='OFFLINE QA ONLY NEVER SEND'))['checks']['not_fixture'])
    def test_wrong_subject(self):
        self.assertFalse(self.audit(self.make(subject='Buy now'))['checks']['expected_subject_matches'])
    def test_no_subject_expectation_is_unknown(self):
        self.assertFalse(inspect_bytes(self.make())['checks']['expected_subject_matches'])
    def test_no_postal_attestation(self):
        self.assertFalse(inspect_bytes(self.make(),expected_subject='Evidence Dispatch')['checks']['approved_publisher_postal_text_present'])
    def test_missing_postal(self):
        x=self.make(text='Hello',html='<a href="https://finalvestige.com/archive/">read</a>')
        self.assertFalse(self.audit(x)['checks']['approved_publisher_postal_text_present'])
    def test_placeholder_block(self):
        x=self.make(text='[[VALID_POSTAL_ADDRESS_REQUIRED]]')
        self.assertFalse(self.audit(x)['checks']['no_release_placeholders'])
    def test_no_cta_if_only_unsub(self):
        x=self.make(html='<a href="https://wordpress.com/unsubscribe">Unsubscribe</a>')
        self.assertFalse(self.audit(x)['checks']['https_editorial_cta_candidate'])
    def test_non_https_does_not_count(self):
        x=self.make(html='<a href="javascript:alert(1)">Read</a>')
        self.assertFalse(self.audit(x)['checks']['https_editorial_cta_candidate'])
    def test_mailto_not_editorial_cta(self):
        x=self.make(html='<a href="mailto:example@example.com">Read</a>')
        self.assertFalse(self.audit(x)['checks']['https_editorial_cta_candidate'])
    def test_no_piis_in_output(self):
        d=str(self.audit(self.make()))
        for s in ('private-user@example.com','token=SECRET','donotreply@wordpress.com','123 Test Street'):
            self.assertNotIn(s,d)
    def test_missing_alternative(self):
        m=EmailMessage();m['Subject']='Evidence Dispatch';m.set_content('Only plain text')
        self.assertFalse(self.audit(m.as_bytes())['checks']['both_mime_alternatives'])
    def test_empty_and_oversized_rejected(self):
        for b in (b'',b'x'*1_500_001):
            with self.assertRaises(ValueError):self.audit(b)
    def test_email_word_in_plaintext_not_unsub(self):
        m=EmailMessage();m['Subject']='Evidence Dispatch';m.set_content('You may unsubscribe')
        m.add_alternative('<html><body>No unsub href</body></html>',subtype='html')
        self.assertFalse(self.audit(m.as_bytes())['checks']['unsubscribe_candidate_present'])
    def test_disclosure_does_not_equal_merchant_acceptance(self):
        x=self.make(text='We may earn a commission. '+ 'Our office: 123 Test Street, Anywhere, CA 90000')
        d=self.audit(x)
        self.assertIn('merchant_email_rights_and_disclosure_if_commercial',d['requires_external_attestation'])
    def test_no_from(self):
        m=EmailMessage();m['Subject']='Evidence Dispatch';m.set_content('Hello')
        self.assertFalse(self.audit(m.as_bytes())['checks']['from_header_present'])

if __name__=='__main__':unittest.main()
