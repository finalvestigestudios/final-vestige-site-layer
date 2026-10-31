"""R9 synthetic email-client ambiguity and merchant-reference regressions.

Zero live recipients, mail sends, credentials, network calls, or vendor tracking links.
The marker email/domain/address values are deliberately synthetic.
"""
import importlib.util
import json
import re
from email.message import EmailMessage
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'received_email_audit.py'
spec = importlib.util.spec_from_file_location('fv_audit_r9', SOURCE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

EXCERPT = 'A twelve-minute routine deserves a careful test before any product recommendation.'
DISCLOSURE = 'If you buy through our review, Final Vestige may earn a commission.'
POSTAL = 'Synthetic PO Box 123, Fictionville, CA 00000'
CTA = 'https://finalvestige.com/mind/zen12-guide/'  # synthetic UNPUBLISHED source-contract example
SUBJECT = 'The twelve-minute meditation question'
OPTOUT = '<a href="https://wordpress.com/unsubscribe?token=synthetic">Unsubscribe</a>'

def email_with(*htmls, plain='Synthetic test only; this is not a subscriber message.'):
    e = EmailMessage()
    e['From'] = 'Final Vestige <donotreply@wordpress.com>'
    e['To'] = 'fictional-recipient@example.invalid'
    e['Subject'] = SUBJECT
    e.set_content(plain)
    for html in htmls:
        e.add_alternative(html, subtype='html')
    return e.as_bytes()

def check(raw):
    return audit.audit_received(raw, issue=3, expected_subject=SUBJECT,
                                expected_excerpt=EXCERPT,
                                expected_postal=POSTAL, expected_cta=CTA)

def body(*parts):
    return '<p>' + EXCERPT + '</p>' + ''.join(parts) + '<p>' + POSTAL + '</p>' + OPTOUT

class R9Tests(unittest.TestCase):
    def test_baseline_ordinary_synthetic_html_is_inspectable_but_unsent(self):
        result = check(email_with(body(f'<p>{DISCLOSURE}</p><a href="{CTA}">Read</a>')))
        self.assertEqual(result['checks']['exact_edition_cta_visible'], 'PASS')
        self.assertEqual(result['checks']['no_direct_merchant_link'], 'PASS')
        self.assertEqual(result['status'], 'HOLD_FOR_HUMAN_AND_EXTERNAL_PROOFS')
        self.assertTrue(result['checks']['computed_email_client_visibility'].startswith('UNKNOWN'))

    def test_visible_unanchored_merchant_url_fails(self):
        r=check(email_with(body(f'<p>{DISCLOSURE}</p><p>https://zen12.com/order</p><a href="{CTA}">Read</a>')))
        self.assertEqual(r['checks']['no_direct_merchant_link'], 'FAIL')

    def test_remote_merchant_image_fails_even_without_anchor(self):
        r=check(email_with(body(f'<p>{DISCLOSURE}</p><img alt="" src="https://zen12.com/track?private=token"><a href="{CTA}">Read</a>')))
        self.assertEqual(r['checks']['no_direct_merchant_link'], 'FAIL')

    def test_merchant_srcset_fails(self):
        r=check(email_with(body(f'<p>{DISCLOSURE}</p><source srcset="https://zen12.com/a.jpg 1x, https://inspire3.com/b.jpg 2x"><a href="{CTA}">Read</a>')))
        self.assertEqual(r['checks']['no_direct_merchant_link'], 'FAIL')

    def test_merchant_form_action_fails(self):
        r=check(email_with(body(f'<p>{DISCLOSURE}</p><form action="https://hypnosislive.com/buy"><button>Buy</button></form><a href="{CTA}">Read</a>')))
        self.assertEqual(r['checks']['no_direct_merchant_link'], 'FAIL')

    def test_merchant_css_background_url_fails(self):
        r=check(email_with(body(f'<p>{DISCLOSURE}</p><style>p{{background-image:url(https://zen12.com/pixel)}}</style><a href="{CTA}">Read</a>')))
        self.assertEqual(r['checks']['no_direct_merchant_link'], 'FAIL')

    def test_merchant_in_html_comment_fails_closed(self):
        r=check(email_with(body(f'<p>{DISCLOSURE}</p><!-- https://inspire3.com/offer --><a href="{CTA}">Read</a>')))
        self.assertEqual(r['checks']['no_direct_merchant_link'], 'FAIL')

    def test_lookalike_subdomain_does_not_trigger_false_vendor_match(self):
        r=check(email_with(body(f'<p>{DISCLOSURE}</p><p>https://zen12.com.evil.invalid/test</p><a href="{CTA}">Read</a>')))
        self.assertEqual(r['checks']['no_direct_merchant_link'], 'PASS')

    def test_css_class_hidden_disclosure_fails(self):
        r=check(email_with('<style>.ghost{display:none}</style>'+body(f'<p class="ghost">{DISCLOSURE}</p><a href="{CTA}">Read</a>')))
        self.assertEqual(r['checks']['commercial_disclosure_visible'], 'FAIL')
        self.assertEqual(r['checks']['commercial_disclosure_before_cta'], 'FAIL')

    def test_css_id_hidden_postal_fails(self):
        html=f'<style>#mailer{{visibility:hidden}}</style><p>{EXCERPT}</p><p>{DISCLOSURE}</p><a href="{CTA}">Read</a><p id="mailer">{POSTAL}</p>{OPTOUT}'
        r=check(email_with(html))
        self.assertEqual(r['checks']['founder_verified_postal_address'], 'FAIL')

    def test_css_class_hidden_optout_fails(self):
        html=f'<style>.quiet{{opacity:0!important}}</style><p>{EXCERPT}</p><p>{DISCLOSURE}</p><a href="{CTA}">Read</a><p>{POSTAL}</p><div class="quiet">{OPTOUT}</div>'
        r=check(email_with(html))
        self.assertEqual(r['checks']['visible_optout_mechanism'], 'FAIL')

    def test_css_class_hidden_exact_cta_fails(self):
        html=f'<style>.quiet{{display:none!important}}</style><p>{EXCERPT}</p><p>{DISCLOSURE}</p><p class="quiet"><a href="{CTA}">Read</a></p><p>{POSTAL}</p>{OPTOUT}'
        r=check(email_with(html))
        self.assertEqual(r['checks']['exact_edition_cta_visible'], 'FAIL')

    def test_css_rule_after_html_still_hides_disclosure(self):
        html=body(f'<p class="ghost">{DISCLOSURE}</p><a href="{CTA}">Read</a>')+'<style>.ghost{display:none}</style>'
        r=check(email_with(html))
        self.assertEqual(r['checks']['commercial_disclosure_visible'], 'FAIL')

    def test_unsupported_complex_css_visibility_fails_closed_unknown(self):
        html=f'<style>.parent .ghost{{display:none}}</style><p>{EXCERPT}</p><p class="ghost">{DISCLOSURE}</p><a href="{CTA}">Read</a><p>{POSTAL}</p>{OPTOUT}'
        r=check(email_with(html))
        self.assertEqual(r['status'], 'HOLD_RENDERING_UNVERIFIED')
        self.assertEqual(r['checks']['css_visibility'], 'UNKNOWN_REQUIRES_REAL_EMAIL_CLIENT')

    def test_media_query_with_hiding_is_not_assumed_visible(self):
        html=f'<style>@media(max-width:600px){{.hide{{display:none}}}}</style><p>{EXCERPT}</p><p class="hide">{DISCLOSURE}</p><a href="{CTA}">Read</a><p>{POSTAL}</p>{OPTOUT}'
        r=check(email_with(html))
        self.assertEqual(r['status'], 'HOLD_RENDERING_UNVERIFIED')

    def test_two_conflicting_html_alternatives_are_not_combined(self):
        good=body(f'<p>{DISCLOSURE}</p><a href="{CTA}">Read</a>')
        bad='<p>Other story without commission notice or postal.</p>'+OPTOUT
        r=check(email_with(good,bad))
        self.assertEqual(r['status'],'HOLD_INVALID_MIME')
        self.assertEqual(r['checks']['mime_decode'],'FAIL')

    def test_two_plaintext_alternatives_are_not_combined(self):
        e=EmailMessage();e['From']='Final Vestige <donotreply@wordpress.com>';e['To']='fictional@example.invalid';e['Subject']=SUBJECT
        e.set_content('one');e.add_alternative('two',subtype='plain')
        r=check(e.as_bytes())
        self.assertEqual(r['status'],'HOLD_INVALID_MIME')

    def test_duplicate_from_headers_are_invalid(self):
        raw=email_with(body(f'<p>{DISCLOSURE}</p><a href="{CTA}">Read</a>'))
        raw=b'From: Spoof <spoof@example.invalid>\r\n'+raw
        r=check(raw)
        self.assertEqual(r['status'],'HOLD_INVALID_MIME')

    def test_duplicate_subject_headers_are_invalid(self):
        raw=email_with(body(f'<p>{DISCLOSURE}</p><a href="{CTA}">Read</a>'))
        raw=b'Subject: Another misleading subject\r\n'+raw
        r=check(raw)
        self.assertEqual(r['status'],'HOLD_INVALID_MIME')

    def test_missing_to_header_is_invalid_received_mail_evidence(self):
        raw=email_with(body(f'<p>{DISCLOSURE}</p><a href="{CTA}">Read</a>'))
        raw=re.sub(rb'(?mi)^To:[^\r\n]*\r?\n', b'', raw, count=1)
        r=check(raw)
        self.assertEqual(r['status'],'HOLD_INVALID_MIME')

    def test_forwarded_nested_message_does_not_count_as_primary_email(self):
        inner=EmailMessage();inner['From']='Final Vestige <donotreply@wordpress.com>';inner['To']='fictional@example.invalid';inner['Subject']=SUBJECT
        inner.set_content('Inner mail')
        parent=EmailMessage();parent['From']='Final Vestige <donotreply@wordpress.com>';parent['To']='fictional@example.invalid';parent['Subject']=SUBJECT
        parent.set_content('Outer unrelated mail');parent.add_attachment(inner)
        r=check(parent.as_bytes())
        self.assertEqual(r['status'],'HOLD_INVALID_MIME')

    def test_source_exposes_no_send_or_network_api(self):
        source=SOURCE.read_text()
        for forbidden in ('smtplib', 'requests.', 'wp_insert_post(', 'publish(', 'send_email('):
            self.assertNotIn(forbidden,source)

    def test_reports_never_expose_private_tokens_or_test_identifiers(self):
        raw=email_with(body(f'<p>{DISCLOSURE}</p><img src="https://zen12.com/a?private=token"><a href="{CTA}">Read</a>'))
        report=json.dumps(check(raw))
        for secret in ('fictional-recipient', 'example.invalid', 'private=token', 'Fictionville', 'synthetic', 'donotreply@'):
            self.assertNotIn(secret,report)

if __name__=='__main__': unittest.main()
