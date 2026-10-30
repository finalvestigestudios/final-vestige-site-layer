"""Adversarial, privacy-preserving synthetic MIME tests. No actual user email."""
import importlib.util
import json
from pathlib import Path
from email.message import EmailMessage
import unittest

MODULE = Path(__file__).resolve().parents[1] / "received_email_audit.py"
spec = importlib.util.spec_from_file_location("received_email_audit", MODULE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

EXCERPT = ("A twelve-minute audio session sounds easier to fit into a busy day than an hour of meditation. "
           "But convenience isn't evidence that both produce the same result. "
           "This edition includes an affiliate evaluation: if you later purchase through a qualifying link "
           "in our guide, Final Vestige may earn a commission.")
SUBJECT = "The twelve-minute meditation question"
ADDR = "Final Vestige Business Address, PO Box 123, Fictionville CA 00000"  # synthetic, NOT valid


def sample(*, plain=None, html=None, from_header='Final Vestige <donotreply@wordpress.com>',
           subject=SUBJECT, include_unsub=True, with_footer=True):
    base = (EXCERPT + ('\n' + ADDR if with_footer else '')) if plain is None else plain
    if include_unsub:
        base += '\nUnsubscribe: https://wordpress.com/unsubscribe?token=synthetic'
    msg = EmailMessage()
    msg['From'] = from_header
    msg['To'] = 'synthetic-reader@example.invalid'
    msg['Subject'] = subject
    msg['List-Unsubscribe'] = '<https://wordpress.com/unsubscribe?token=synthetic>'
    msg.set_content(base)
    if html is not None:
        msg.add_alternative(html, subtype='html')
    return msg.as_bytes()


def run(raw, issue=3, mode='excerpt', expected_postal=ADDR, full_body_marker=''):
    return audit.audit_received(raw, issue=issue, expected_subject=SUBJECT,
                                expected_excerpt=EXCERPT, expected_postal=expected_postal,
                                email_mode=mode, full_body_marker=full_body_marker)


class MimeProofTests(unittest.TestCase):
    def test_missing_email_is_hold(self):
        self.assertEqual(run(None)['status'], 'HOLD_NO_RECEIVED_EMAIL')

    def test_complete_synthetic_plain_email_still_hold(self):
        r = run(sample())
        self.assertEqual(r['checks']['subject_matches_approved_draft'], 'PASS')
        self.assertEqual(r['checks']['sender_display_name'], 'PASS')
        self.assertEqual(r['checks']['visible_optout_mechanism'], 'PASS')
        self.assertEqual(r['status'], 'HOLD_FOR_HUMAN_AND_EXTERNAL_PROOFS')

    def test_wrong_subject_fails(self):
        self.assertEqual(run(sample(subject='Instant riches'))['checks']['subject_matches_approved_draft'], 'FAIL')

    def test_lookalike_sender_fails(self):
        self.assertEqual(run(sample(from_header='Final Vestige <attacker@evil.test>'))['checks']['wordpress_from_domain'], 'FAIL')

    def test_wrong_display_name_fails(self):
        self.assertEqual(run(sample(from_header='Other <donotreply@wordpress.com>'))['checks']['sender_display_name'], 'FAIL')

    def test_missing_custom_excerpt_head_fails(self):
        self.assertEqual(run(sample(plain='Just five words.\n'+ADDR))['checks']['custom_excerpt_head'], 'FAIL')

    def test_missing_custom_excerpt_tail_fails(self):
        self.assertEqual(run(sample(plain=EXCERPT[:95]+'\n'+ADDR))['checks']['custom_excerpt_tail'], 'FAIL')

    def test_list_unsubscribe_header_alone_is_not_enough(self):
        self.assertEqual(run(sample(include_unsub=False))['checks']['visible_optout_mechanism'], 'FAIL')

    def test_no_postal_evidence_is_unknown(self):
        self.assertEqual(run(sample(), expected_postal=None)['checks']['founder_verified_postal_address'], 'UNKNOWN')

    def test_automattic_address_cannot_substitute_business_address(self):
        mail = sample(with_footer=False, plain=EXCERPT+'\nAutomattic, 60 29th St, San Francisco, CA 94110')
        self.assertEqual(run(mail)['checks']['founder_verified_postal_address'], 'FAIL')

    def test_private_postal_matches_but_value_not_returned(self):
        report = run(sample())
        self.assertEqual(report['checks']['founder_verified_postal_address'], 'PASS')
        self.assertNotIn(ADDR, json.dumps(report))

    def test_no_real_postal_value_in_output(self):
        report = run(sample(), expected_postal=None)
        self.assertNotIn('Fictionville', json.dumps(report))

    def test_commercial_disclosure_missing_fails(self):
        altered = EXCERPT.replace('Final Vestige may earn a commission', 'We offer information')
        report = run(sample(plain=altered+'\n'+ADDR))
        self.assertEqual(report['checks']['commercial_disclosure_visible'], 'FAIL')

    def test_commercial_disclosure_present(self):
        self.assertEqual(run(sample())['checks']['commercial_disclosure_visible'], 'PASS')

    def test_commercial_permissions_remain_unknown(self):
        report = run(sample())
        self.assertTrue(report['checks']['affiliate_email_permission'].startswith('UNKNOWN'))

    def test_html_optout_anchor(self):
        html = ('<html><body><p>'+EXCERPT+'</p><p>'+ADDR+'</p>'
                '<a href="https://wordpress.com/unsubscribe?token=synthetic">Unsubscribe</a>'
                '<a href="https://finalvestige.com/dispatch/">Read more</a></body></html>')
        report = run(sample(plain=EXCERPT+'\n'+ADDR, html=html, include_unsub=False))
        self.assertEqual(report['checks']['visible_optout_mechanism'], 'PASS')
        self.assertEqual(report['checks']['onsite_cta_route_present'], 'PASS')

    def test_html_merchant_link_not_permitted(self):
        html = ('<p>'+EXCERPT+'</p><p>'+ADDR+'</p><a href="https://zen12.com/offer">Buy</a>'
                '<a href="https://wordpress.com/unsubscribe">Unsubscribe</a>')
        self.assertEqual(run(sample(html=html))['checks']['no_direct_merchant_link'], 'FAIL')

    def test_html_missing_disclosure_cannot_use_plain_fallback(self):
        html = ('<p>Just audio, no important details shown.</p><p>'+ADDR+'</p>'
                '<a href="https://wordpress.com/unsubscribe">Unsubscribe</a>')
        self.assertEqual(run(sample(html=html))['checks']['commercial_disclosure_visible'], 'FAIL')

    def test_html_missing_optout_cannot_use_plain_fallback(self):
        html = ('<p>'+EXCERPT+'</p><p>'+ADDR+'</p>'
                '<a href="https://finalvestige.com/dispatch/">Read</a>')
        self.assertEqual(run(sample(html=html))['checks']['visible_optout_mechanism'], 'FAIL')

    def test_html_missing_excerpt_tail_cannot_use_plain_fallback(self):
        html = ('<p>A twelve-minute audio session sounds easier to fit into a busy day</p><p>'+ADDR+'</p>'
                '<a href="https://wordpress.com/unsubscribe">Unsubscribe</a>')
        self.assertEqual(run(sample(html=html))['checks']['custom_excerpt_tail'], 'FAIL')

    def test_plain_direct_merchant_link_detected(self):
        mail = sample(plain=EXCERPT+'\n'+ADDR+'\nhttps://zen12.com/freeaudio')
        self.assertEqual(run(mail)['checks']['no_direct_merchant_link'], 'FAIL')

    def test_html_hidden_script_is_not_counted_as_disclosure(self):
        html = ('<script>Final Vestige may earn a commission</script><div>No disclosure here.</div>'
                '<p>'+ADDR+'</p><a href="https://wordpress.com/unsubscribe">Unsubscribe</a>')
        plain = 'No disclosure here.' + '\n'+ADDR
        self.assertEqual(run(sample(plain=plain, html=html))['checks']['commercial_disclosure_visible'], 'FAIL')

    def test_javascript_uri_not_usable_for_unsubscribe(self):
        html = ('<p>'+EXCERPT+'</p><a href="javascript:alert(1)">Unsubscribe</a>')
        self.assertEqual(run(sample(plain=EXCERPT, html=html, include_unsub=False))['checks']['visible_optout_mechanism'], 'FAIL')

    def test_placeholder_blocks_safety(self):
        raw = sample(plain=EXCERPT+'\n[[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]\n'+ADDR)
        self.assertEqual(run(raw)['checks']['no_unresolved_tokens'], 'FAIL')

    def test_full_mode_marker_detects_excerpt_truncation(self):
        self.assertEqual(run(sample(), mode='full', full_body_marker='at the very end of the story')
                         ['checks']['full_article_in_email'], 'FAIL')

    def test_full_mode_missing_marker_argument_unknown(self):
        self.assertEqual(run(sample(), mode='full')['checks']['full_article_in_email'], 'UNKNOWN')

    def test_preheader_not_claimed_verified(self):
        self.assertTrue(run(sample())['checks']['preheader_appearance'].startswith('UNKNOWN'))

    def test_invalid_issue_rejected(self):
        with self.assertRaises(ValueError):
            run(sample(), issue=7)

    def test_oversize_fails_closed(self):
        self.assertEqual(run(b'a'*(audit.MAX_MIME_BYTES+1))['status'], 'HOLD_INVALID_MIME')

    def test_mailto_optout_accepted_as_mechanism_not_functionality(self):
        mail = sample(plain=EXCERPT+'\n'+ADDR+'\nUnsubscribe: mailto:unsubscribe@example.invalid',include_unsub=False)
        r = run(mail)
        self.assertEqual(r['checks']['visible_optout_mechanism'], 'PASS')
        self.assertTrue(r['checks']['optout_link_functional'].startswith('UNKNOWN'))

    def test_report_contains_no_addressee_or_message_text(self):
        r = json.dumps(run(sample()))
        self.assertNotIn('synthetic-reader', r)
        self.assertNotIn('A twelve-minute audio', r)

    def test_no_read_receipt_or_send_op_present(self):
        self.assertFalse(hasattr(audit, 'send_email'))
        self.assertFalse(hasattr(audit, 'publish'))

    def test_unsafe_unsubscribe_url_rejected(self):
        for href in ('javascript:alert(1)', '', 'data:text/plain,hi', 'https://', 'mailto:no-at-sign'):
            self.assertFalse(audit.is_usable_optout(href))

    def test_fake_merchant_subdomain_detection(self):
        self.assertFalse(audit.is_merchant_url('https://zen12.com.evil.test/buy'))
        self.assertTrue(audit.is_merchant_url('https://shop.zen12.com/buy'))


if __name__ == '__main__':
    unittest.main()
