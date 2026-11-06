"""Run: python -m unittest discover -s r150 -p 'test_*.py' -v"""
import unittest
from email.message import EmailMessage
from received_mail_audit import inspect

CTA = "https://finalvestige.com/2026/11/02/change-blindness/"
ADDRESS = "VERIFIED DEMO BUSINESS POSTAL - SYNTHETIC NOT REAL"
SUBJECT = "The mind is not a camera"


def synthetic(*, subject=SUBJECT, sender="Final Vestige Studios <donotreply@wordpress.com>",
              address=ADDRESS, disclosure=True, unsub=True, cta=CTA,
              html=True, bad_img=False, js=False, with_plain=True, full=True, late_gap=False):
    m = EmailMessage()
    m["Subject"] = subject
    m["From"] = sender
    m["To"] = "fictitious-recipient@example.invalid"
    m["Date"] = "Thu, 05 Nov 2026 12:00:00 -0800"
    body = ("A useful, specific research observation and its limitations. " * 13) if full else "Short. "
    if address: body += address + ". "
    if disclosure: body += " If you buy, Final Vestige may earn a commission. "
    if late_gap: body += " Irrelevant intervening paragraph. " * 100
    if with_plain: m.set_content(body + "\n" + cta + "\nUnsubscribe")
    else: m.set_content(" ")
    html_body = "<html><body><main><p>"+body+"</p>"
    if cta: html_body += '<a href="'+cta+'">Read the investigation</a>'
    if unsub: html_body += '<a href="https://example.invalid/unsubscribe/tokenized">Unsubscribe</a>'
    if bad_img: html_body += '<img src="x.jpg">'
    if js: html_body += '<script>alert(1)</script>'
    html_body += '</main></body></html>'
    if html: m.add_alternative(html_body, subtype="html")
    return m.as_bytes()


def audit(raw=None, issue=1, **kwargs):
    args = dict(issue=issue, subject=SUBJECT, cta_url=CTA, publisher_address=ADDRESS,
                authorized_inbox=True, native_consent=True, optout_checked=True,
                source_proof=True, merchant_email_permission=True)
    args.update(kwargs)
    return inspect(raw if raw is not None else synthetic(), **args)


class ReceivedMailAudit(unittest.TestCase):
    def test_good_editorial_only_candidate(self):
        r=audit();self.assertEqual(r['verdict'],'RECEIVED_COPY_QA_CANDIDATE_ONLY_NOT_SEND_APPROVAL')
    def test_no_auto_send(self):self.assertFalse(audit()['send_authorized'])
    def test_no_commercial_link_activation(self):self.assertFalse(audit(issue=3)['commercial_link_authorized'])
    def test_wrong_subject_rejected(self):self.assertEqual(audit(synthetic(subject='Confirm your subscription'))['verdict'],'NOT_A_CAMPAIGN_MESSAGE')
    def test_confirmation_without_campaign_not_receipt(self):
        r=audit(synthetic(subject='Confirm your subscription',address='',unsub=False,full=False))
        self.assertFalse(r['checks']['subject_matches_campaign'])
    def test_from_display_check(self):self.assertFalse(audit(synthetic(sender='Some Other Newsletter <donotreply@wordpress.com>'))['checks']['sender_display_matches'])
    def test_sender_domain_check(self):self.assertFalse(audit(synthetic(sender='Final Vestige Studios <fake@example.invalid>'))['checks']['sender_domain_matches_documented_jetpack'])
    def test_not_valid_optout_absent(self):self.assertFalse(audit(synthetic(unsub=False))['checks']['visible_optout_indicator'])
    def test_optout_untested_blocks(self):self.assertFalse(audit(optout_checked=False)['checks']['actual_optout_test_attested'])
    def test_address_absent_blocks(self):self.assertFalse(audit(synthetic(address=''))['checks']['publisher_address_in_body'])
    def test_address_unconfirmed_blocks(self):self.assertFalse(audit(publisher_address=None)['checks']['publisher_address_confirmed_by_owner'])
    def test_missing_html_cta_blocks(self):self.assertFalse(audit(synthetic(cta=''))['checks']['first_party_cta_in_html_with_label'])
    def test_missing_plain_cta_blocks(self):self.assertFalse(audit(synthetic(with_plain=False))['checks']['first_party_cta_in_plaintext'])
    def test_short_body_blocks(self):self.assertFalse(audit(synthetic(full=False))['checks']['substantive_full_text'])
    def test_commercial_requires_disclosure(self):self.assertFalse(audit(synthetic(disclosure=False),issue=3)['checks']['affiliate_disclosure_adjacent_html'])
    def test_commercial_disclosure_far_from_cta_is_rejected(self):
        r=audit(synthetic(late_gap=True),issue=3)
        self.assertFalse(r['checks']['affiliate_disclosure_adjacent_html'])
        self.assertFalse(r['checks']['affiliate_disclosure_adjacent_plaintext'])
    def test_editorial_does_not_require_merchant(self):self.assertTrue(audit(merchant_email_permission=False)['checks']['merchant_email_permission_attested'])
    def test_commercial_requires_merchant(self):self.assertFalse(audit(issue=5,merchant_email_permission=False)['checks']['merchant_email_permission_attested'])
    def test_image_alt_is_required(self):self.assertFalse(audit(synthetic(bad_img=True))['checks']['html_images_have_alt'])
    def test_script_is_prohibited(self):self.assertFalse(audit(synthetic(js=True))['checks']['html_no_scripts_or_forms'])
    def test_native_consent_not_inferred(self):self.assertFalse(audit(native_consent=False)['checks']['native_opt_in_eligibility_evidence'])
    def test_authorized_inbox_not_inferred(self):self.assertFalse(audit(authorized_inbox=False)['checks']['accessed_in_authorized_received_inbox'])
    def test_source_proof_not_inferred(self):self.assertFalse(audit(source_proof=False)['checks']['independently_checked_source'])
    def test_privacy_no_recipient(self):self.assertNotIn('fictitious-recipient',str(audit()))
    def test_privacy_no_unsubscribe_token(self):self.assertNotIn('tokenized',str(audit()))
    def test_invalid_issue_refused(self):
        with self.assertRaises(ValueError):audit(issue=7)
    def test_invalid_external_cta_refused(self):
        with self.assertRaises(ValueError):audit(cta_url='https://inspire3.com/')
    def test_invalid_js_cta_refused(self):
        with self.assertRaises(ValueError):audit(cta_url='javascript:alert(1)')
    def test_all_checks_true_still_not_send_approved(self):
        self.assertTrue(all(audit()['checks'].values()));self.assertFalse(audit()['send_authorized'])

if __name__=='__main__': unittest.main()
