import unittest
from email.message import EmailMessage
from inbox_preview_gate import audit

SUBJECT='The person who changed mid-conversation'
POSTAL='Founder-validated postal address here'  # synthetic fixture, never asserted as a real address

def make(*, subject=SUBJECT, unsubscribe=True, disclose=True, merchant=False, placeholder=False, plain=True, html=True, postal=True):
    m=EmailMessage();m['Subject']=subject;m['From']='Final Vestige Studios <donotreply@wordpress.com>'
    m['To']='test-recipient@example.invalid'
    body='Read our source: https://doi.org/10.3758/BF03208840. '
    if disclose:body+='If you purchase through a link on our guide, we may earn a commission. '
    if postal:body+=POSTAL+' '
    if unsubscribe:body+='Unsubscribe here. '
    if placeholder:body+='[[ADDRESS_REQUIRED]] '
    if plain:m.set_content(body)
    else:m.set_content('')
    target='https://hypnosislive.com/catalog' if merchant else 'https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/'
    link='<a href="https://example.invalid/opt-out">Unsubscribe</a>' if unsubscribe else ''
    markup=f'<html><body><p>{body}</p><a href="{target}">Read the guide</a>{link}</body></html>'
    if html:m.add_alternative(markup,subtype='html')
    return m.as_bytes()

def review(data=None,edition='03',**kw):
    return audit(data or make(),edition=edition,expected_subject=SUBJECT,sender_label='Final Vestige Studios',legal_postal_text=POSTAL,**kw)

class AuditTests(unittest.TestCase):
    def test_no_evidence_is_never_sendable(self):
        r=review();self.assertEqual(r['status'],'HOLD_UNSENT');self.assertFalse(r['send_authorized'])
    def test_synthetic_fixture_not_real_preview(self):
        r=review();self.assertFalse(r['evidence_attested']['jetpack_native_preview_verified'])
    def test_missing_unsub(self):
        r=review(make(unsubscribe=False));self.assertFalse(r['structural_checks']['visible_unsubscribe_url_syntax'])
    def test_subject_mismatch(self):
        r=review(make(subject='Misleading subject'));self.assertFalse(r['structural_checks']['subject_exact'])
    def test_missing_address(self):
        r=review(make(postal=False));self.assertFalse(r['structural_checks']['postal_address_present'])
    def test_placeholders_block(self):
        r=review(make(placeholder=True));self.assertFalse(r['structural_checks']['no_template_placeholders'])
    def test_merchant_direct_block(self):
        r=review(make(merchant=True));self.assertFalse(r['structural_checks']['no_direct_merchant_destination'])
    def test_missing_disclosure(self):
        r=review(make(disclose=False));self.assertFalse(r['structural_checks']['near_offer_disclosure'])
    def test_editorial_no_commercial_obligation(self):
        r=review(make(disclose=False),edition='01');self.assertTrue(r['structural_checks']['near_offer_disclosure'])
    def test_both_mime_parts_required(self):
        r=review(make(html=False));self.assertFalse(r['structural_checks']['html_and_plaintext'])
    def test_no_recipient_data_leak(self):
        r=review();self.assertNotIn('test-recipient',str(r));self.assertIsNone(r['recipient_count'])
    def test_booleans_not_strings(self):
        r=review(evidence={'founder_campaign_approval':'true'});self.assertFalse(r['evidence_attested']['founder_campaign_approval'])
    def test_no_false_positive_from_only_headers(self):
        data=make(unsubscribe=False).replace(b'Unsubscribe here.',b'')
        r=review(data);self.assertFalse(r['structural_checks']['visible_unsubscribe_url_syntax'])
    def test_even_all_attested_cannot_send(self):
        base=review();ev={k:True for k in base['evidence_attested']};r=review(evidence=ev)
        self.assertEqual(r['status'],'REVIEW_CANDIDATE_ONLY');self.assertFalse(r['send_authorized'])
    def test_false_commercial_permission_retains_hold(self):
        base=review();ev={k:True for k in base['evidence_attested']};ev['named_merchant_email_permission_verified']=False
        self.assertEqual(review(evidence=ev)['status'],'HOLD_UNSENT')

if __name__=='__main__':unittest.main()
