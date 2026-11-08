"""Proof of previously unsafe outcomes and regressions in the existing received-email auditor.

All messages, recipients, unsubscribe URLs, addresses and affiliate links are synthetic.
No network calls, inbox queries or actual mail sending.
"""
import importlib.util
from email.message import EmailMessage
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "received_email_audit.py"
spec = importlib.util.spec_from_file_location("received_email_audit", MODULE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
SUBJECT = "The twelve-minute meditation question"
EXCERPT = "A twelve-minute routine deserves a careful test before any product recommendation."
POSTAL = "Synthetic PO Box 123, Fictionville, CA 00000"  # not an actual address
CTA = "https://finalvestige.com/mind/zen12-guide/"  # synthetic future URL, NOT live
DISC = "If you buy through our review, Final Vestige may earn a commission."
FOOT = '<a href="https://wordpress.com/unsubscribe?token=synthetic">Unsubscribe</a>'


def mime(html):
    msg=EmailMessage()
    msg['From']='Final Vestige <donotreply@wordpress.com>'
    msg['To']='synthetic@example.invalid'
    msg['Subject']=SUBJECT
    msg.set_content('Check the HTML preview for the information.')
    msg.add_alternative(html,subtype='html')
    return msg.as_bytes()


def report(html,cta=CTA,issue=3):
    return audit.audit_received(mime(html),issue=issue,expected_subject=SUBJECT,
                                expected_excerpt=EXCERPT,expected_postal=POSTAL,
                                expected_cta=cta)

class HardeningTests(unittest.TestCase):
    def test_hidden_disclosure_does_not_pass(self):
        r=report(f'<div>{EXCERPT}</div><p hidden>{DISC}</p><p>{POSTAL}</p><a href="{CTA}">Read guide</a>{FOOT}')
        self.assertEqual(r['checks']['commercial_disclosure_visible'],'FAIL')
        self.assertEqual(r['checks']['commercial_disclosure_before_cta'],'FAIL')

    def test_display_none_disclosure_does_not_pass(self):
        r=report(f'<p>{EXCERPT}</p><span style="display: none">{DISC}</span><p>{POSTAL}</p><a href="{CTA}">Read</a>{FOOT}')
        self.assertEqual(r['checks']['commercial_disclosure_visible'],'FAIL')

    def test_aria_hidden_disclosure_does_not_pass(self):
        r=report(f'<p>{EXCERPT}</p><div aria-hidden="true">{DISC}</div><p>{POSTAL}</p><a href="{CTA}">Read</a>{FOOT}')
        self.assertEqual(r['checks']['commercial_disclosure_visible'],'FAIL')

    def test_hidden_postal_does_not_pass(self):
        r=report(f'<p>{EXCERPT}</p><p style="visibility:hidden">{POSTAL}</p><p>{DISC}</p><a href="{CTA}">Read</a>{FOOT}')
        self.assertEqual(r['checks']['founder_verified_postal_address'],'FAIL')

    def test_hidden_unsubscribe_not_accepted(self):
        r=report(f'<p>{EXCERPT}</p><p>{DISC}</p><p>{POSTAL}</p><a href="{CTA}">Read</a><div style="opacity:0">{FOOT}</div>')
        self.assertEqual(r['checks']['visible_optout_mechanism'],'FAIL')

    def test_hidden_merchant_link_still_flagged(self):
        r=report(f'<p>{EXCERPT}</p><p>{DISC}</p><p>{POSTAL}</p><a href="{CTA}">Read</a><a hidden href="https://zen12.com/order">hidden merchant</a>{FOOT}')
        self.assertEqual(r['checks']['no_direct_merchant_link'],'FAIL')

    def test_logo_and_footer_links_cannot_substitute_exact_cta(self):
        r=report(f'<p>{EXCERPT}</p><p>{DISC}</p><p>{POSTAL}</p><a href="https://finalvestige.com/">Site</a><a href="https://finalvestige.com/privacy-policy/">Privacy</a>{FOOT}')
        self.assertEqual(r['checks']['onsite_cta_route_present'],'PASS')
        self.assertEqual(r['checks']['exact_edition_cta_visible'],'FAIL')

    def test_cta_exact_path_and_query_required(self):
        wrong='https://finalvestige.com/mind/zen12-guide/?campaign=changed'
        r=report(f'<p>{EXCERPT}</p><p>{DISC}</p><p>{POSTAL}</p><a href="{wrong}">Read</a>{FOOT}')
        self.assertEqual(r['checks']['exact_edition_cta_visible'],'FAIL')

    def test_disclosure_after_cta_is_detected(self):
        r=report(f'<p>{EXCERPT}</p><a href="{CTA}">Read the review</a><p>{DISC}</p><p>{POSTAL}</p>{FOOT}')
        self.assertEqual(r['checks']['commercial_disclosure_visible'],'PASS')
        self.assertEqual(r['checks']['exact_edition_cta_visible'],'PASS')
        self.assertEqual(r['checks']['commercial_disclosure_before_cta'],'FAIL')

    def test_disclosure_before_cta_passes_structural_proximity_check(self):
        r=report(f'<p>{EXCERPT}</p><p>{DISC}</p><a href="{CTA}">Read the review</a><p>{POSTAL}</p>{FOOT}')
        self.assertEqual(r['checks']['exact_edition_cta_visible'],'PASS')
        self.assertEqual(r['checks']['commercial_disclosure_before_cta'],'PASS')
        self.assertEqual(r['status'],'HOLD_FOR_HUMAN_AND_EXTERNAL_PROOFS')

    def test_unknown_commercial_guide_cannot_be_verified(self):
        r=report(f'<p>{EXCERPT}</p><p>{DISC}</p><a href="{CTA}">Read</a><p>{POSTAL}</p>{FOOT}',cta='[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]')
        self.assertEqual(r['checks']['exact_edition_cta_visible'],'UNKNOWN_UNAPPROVED_CTA')
        self.assertEqual(r['checks']['commercial_disclosure_before_cta'],'UNKNOWN_UNAPPROVED_CTA')

    def test_no_approved_cta_cannot_be_invented(self):
        r=report(f'<p>{EXCERPT}</p><p>{DISC}</p><a href="{CTA}">Read</a><p>{POSTAL}</p>{FOOT}',cta=None)
        self.assertEqual(r['checks']['exact_edition_cta_visible'],'UNKNOWN_UNAPPROVED_CTA')

    def test_markup_nested_hidden_script_not_visible(self):
        r=report(f'<p>{EXCERPT}</p><template><div>{DISC}</div></template><div hidden><p>{POSTAL}</p></div><a href="{CTA}">Read</a>{FOOT}')
        self.assertEqual(r['checks']['commercial_disclosure_visible'],'FAIL')
        self.assertEqual(r['checks']['founder_verified_postal_address'],'FAIL')

    def test_plaintext_exact_cta(self):
        message=EmailMessage()
        message['From']='Final Vestige <donotreply@wordpress.com>'
        message['To']='synthetic@example.invalid'
        message['Subject']=SUBJECT
        message.set_content(f'{EXCERPT}\n{DISC}\n{CTA}\n{POSTAL}\nUnsubscribe: https://wordpress.com/unsubscribe')
        r=audit.audit_received(message.as_bytes(),issue=3,expected_subject=SUBJECT,
                                expected_excerpt=EXCERPT,expected_postal=POSTAL,expected_cta=CTA)
        self.assertEqual(r['checks']['exact_edition_cta_visible'],'PASS')
        self.assertEqual(r['checks']['commercial_disclosure_before_cta'],'PASS')

    def test_report_does_not_expose_secret_urls_or_postal(self):
        import json
        r=report(f'<p>{EXCERPT}</p><p>{DISC}</p><a href="{CTA}">Read the review</a><p>{POSTAL}</p>{FOOT}')
        o=json.dumps(r)
        self.assertNotIn('token=synthetic',o)
        self.assertNotIn('Fictionville',o)
        self.assertNotIn('synthetic@example.invalid',o)

if __name__=='__main__': unittest.main()
