"""Fully synthetic MIME regression. No subscriber information or real mail used."""
from email.message import EmailMessage
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('receive_only', HERE / 'check_received_mime.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

ADDRESS = '123 Synthetic Verification Avenue, Example City, ZZ 99999'
PLAIN = ('The historical record is a problem of evidence. The researcher saw a change but not everybody did. '
         'The useful question is what was actually recorded, and which conclusions can be supported. '
         'An independent source gives the date, observations, and limits; review them before believing a claim. '
         'More: https://finalvestige.com/focus/ Unsubscribe: https://example.invalid/stop?token=DO_NOT_EXPOSE')
HTML = ('<html><body><p>' + PLAIN.replace('https://example.invalid/stop?token=DO_NOT_EXPOSE', '') +
        '</p><a href="https://example.invalid/stop?token=TOP_SECRET_TEST">Unsubscribe</a></body></html>')


def make_mail(issue=1, subject=None, text=PLAIN, html=HTML, header=True, from_header=True,
              date_header=True, one_click=True):
    msg = EmailMessage()
    if from_header:
        msg['From'] = 'Final Vestige <noreply@example.invalid>'
    msg['To'] = 'Private Recipient <test-subscriber@example.invalid>'
    if date_header:
        msg['Date'] = 'Sat, 31 Oct 2026 14:00:00 +0000'
    with open(HERE.parent / 'manifest.json', encoding='utf-8') as f:
        entries = json.load(f)['issues']
    msg['Subject'] = subject if subject is not None else entries[issue - 1]['subject']
    if header:
        msg['List-Unsubscribe'] = '<https://example.invalid/u?auth=SUPER_SECRET>, <mailto:remove@example.invalid>'
    if one_click:
        msg['List-Unsubscribe-Post'] = 'List-Unsubscribe=One-Click'
    if text is not None:
        msg.set_content(text)
    if html is not None:
        if text is None:
            msg.set_content(html, subtype='html')
        else:
            msg.add_alternative(html, subtype='html')
    return msg.as_bytes()


class ReceivedMIMETests(unittest.TestCase):
    def test_01_no_default_release(self):
        self.assertEqual(MODULE.parse_received(make_mail(), 1)['status'], 'HOLD_UNSENT_UNVERIFIED')

    def test_02_subject_exact(self):
        self.assertTrue(MODULE.parse_received(make_mail(), 1)['checks']['matches_planned_subject'])

    def test_03_subject_mismatch_blocker(self):
        r = MODULE.parse_received(make_mail(subject='Winning focus GUARANTEED'), 1)
        self.assertIn('SUBJECT_NOT_EXACT', r['blocker_codes'])

    def test_04_text_and_html_present(self):
        r = MODULE.parse_received(make_mail(), 1)
        self.assertTrue(r['checks']['has_plaintext_part'] and r['checks']['has_html_part'])

    def test_05_list_unsubscribe_syntax_observed(self):
        self.assertTrue(MODULE.parse_received(make_mail(), 1)['checks']['has_list_unsubscribe_header_syntax'])

    def test_06_list_unsubscribe_absent_not_invented(self):
        self.assertFalse(MODULE.parse_received(make_mail(header=False), 1)['checks']['has_list_unsubscribe_header_syntax'])

    def test_07_oneclick_claim_never_equated_with_functionality(self):
        r = MODULE.parse_received(make_mail(), 1)
        self.assertTrue(r['checks']['has_one_click_header_claim'])
        self.assertIn('Manual confirmation of working unsubscribe for this exact rendered message', r['external_verifications_still_required'])

    def test_08_oneclick_missing(self):
        self.assertFalse(MODULE.parse_received(make_mail(one_click=False), 1)['checks']['has_one_click_header_claim'])

    def test_09_visible_html_optout(self):
        self.assertTrue(MODULE.parse_received(make_mail(text=None), 1)['checks']['contains_visible_optout_in_received_content'])

    def test_10_visible_plaintext_optout(self):
        self.assertTrue(MODULE.parse_received(make_mail(html=None), 1)['checks']['contains_visible_optout_in_received_content'])

    def test_11_no_visible_optout_does_not_pass_header_alone(self):
        r = MODULE.parse_received(make_mail(text='A'*350, html='<p>'+'B'*350+'</p>'), 1)
        self.assertIn('VISIBLE_OPTOUT_NOT_ESTABLISHED', r['blocker_codes'])

    def test_12_optout_link_must_have_permitted_scheme(self):
        self.assertFalse(MODULE.is_optout_href('javascript:alert(1)'))
        self.assertFalse(MODULE.is_optout_href('http://notsecure.example.invalid/u'))
        self.assertFalse(MODULE.is_optout_href('//example.invalid/unsub'))
        self.assertTrue(MODULE.is_optout_href('https://example.invalid/unsub'))
        self.assertTrue(MODULE.is_optout_href('mailto:stop@example.invalid'))

    def test_13_no_html_only_unsubscribe_without_link(self):
        r = MODULE.parse_received(make_mail(text='A'*350, html='<p>unsubscribe</p>'), 1)
        self.assertFalse(r['checks']['contains_visible_optout_in_received_content'])

    def test_14_script_content_not_counted_as_visible(self):
        v = MODULE.VisibleText();v.feed('<script>Unsubscribe</script><p>Nothing</p>')
        self.assertNotIn('Unsubscribe', v.normalized())

    def test_15_style_content_not_counted_as_visible(self):
        v = MODULE.VisibleText();v.feed('<style>.thing{content:"Unsubscribe"}</style><p>Nothing</p>')
        self.assertNotIn('Unsubscribe', v.normalized())

    def test_16_none_address_hard_block(self):
        r = MODULE.parse_received(make_mail(), 1)
        self.assertIsNone(r['checks']['postal_text_matches_private_input'])
        self.assertIn('POSTAL_PRIVATE_ATTESTATION_ABSENT', r['blocker_codes'])

    def test_17_private_address_match_bool_only(self):
        r = MODULE.parse_received(make_mail(text=PLAIN+' '+ADDRESS), 1, ADDRESS)
        self.assertTrue(r['checks']['postal_text_matches_private_input'])
        self.assertNotIn(ADDRESS, json.dumps(r))

    def test_18_address_not_present_fail(self):
        r = MODULE.parse_received(make_mail(), 1, ADDRESS)
        self.assertIn('POSTAL_NOT_VISIBLE_IN_RECEIVED_BODY', r['blocker_codes'])

    def test_19_too_short_address_not_valid(self):
        r = MODULE.parse_received(make_mail(text=PLAIN+' P.O. 1'), 1, 'P.O. 1')
        self.assertFalse(r['checks']['postal_text_matches_private_input'])

    def test_20_merchant_classification(self):
        self.assertEqual(MODULE.parse_received(make_mail(issue=3), 3)['classification'], 'commercial-review-pending')

    def test_21_editorial_disclosure_none(self):
        self.assertIsNone(MODULE.parse_received(make_mail(), 1)['checks']['contains_commercial_disclosure'])

    def test_22_commercial_disclosure_required(self):
        self.assertIn('COMMERCIAL_DISCLOSURE_MISSING', MODULE.parse_received(make_mail(issue=3), 3)['blocker_codes'])

    def test_23_commercial_disclosure_found_but_still_hold(self):
        r = MODULE.parse_received(make_mail(issue=3, text=PLAIN+' Final Vestige may earn a commission.'), 3)
        self.assertTrue(r['checks']['contains_commercial_disclosure'])
        self.assertEqual(r['status'], 'HOLD_UNSENT_UNVERIFIED')

    def test_24_synthetic_token_detected(self):
        r = MODULE.parse_received(make_mail(text=PLAIN+' [[VALID_POSTAL_ADDRESS_REQUIRED]]'), 1)
        self.assertIn('UNSENT_TOKEN_LEAK', r['blocker_codes'])

    def test_25_guide_placeholder_detected(self):
        r = MODULE.parse_received(make_mail(issue=3, text=PLAIN+' [[APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]]'), 3)
        self.assertIn('UNSENT_TOKEN_LEAK', r['blocker_codes'])

    def test_26_visible_preview_unverified_token_detected(self):
        r = MODULE.parse_received(make_mail(text=PLAIN+' [UNVERIFIED: APPROVED_ZEN12_WARMUP_GUIDE_URL_REQUIRED]'), 1)
        self.assertIn('UNSENT_TOKEN_LEAK', r['blocker_codes'])

    def test_27_short_excerpt_risk_detected(self):
        r = MODULE.parse_received(make_mail(text='Unsubscribe: https://example.invalid/stop', html=None), 1)
        self.assertIn('SHORT_OR_EXCERPT_RISK', r['blocker_codes'])

    def test_28_header_missing_sender(self):
        self.assertEqual(MODULE.parse_received(make_mail(from_header=False), 1)['error_code'], 'MISSING_ESSENTIAL_HEADERS')

    def test_29_header_missing_date(self):
        self.assertEqual(MODULE.parse_received(make_mail(date_header=False), 1)['error_code'], 'MISSING_ESSENTIAL_HEADERS')

    def test_30_empty_mime_invalid(self):
        self.assertEqual(MODULE.parse_received(b'', 1)['error_code'], 'INVALID_OR_OVERSIZED_SAMPLE')

    def test_31_oversized_mime_rejected(self):
        self.assertEqual(MODULE.parse_received(b'X' * (MODULE.LIMIT_BYTES+1), 1)['error_code'], 'INVALID_OR_OVERSIZED_SAMPLE')

    def test_32_mime_without_headers(self):
        self.assertEqual(MODULE.parse_received(b'hello', 1)['error_code'], 'MISSING_ESSENTIAL_HEADERS')

    def test_33_no_real_email_addresses_or_tokens_in_output(self):
        s = json.dumps(MODULE.parse_received(make_mail(), 1))
        for term in ('test-subscriber', 'noreply@example.invalid', 'SUPER_SECRET', 'DO_NOT_EXPOSE', 'TOP_SECRET_TEST'):
            self.assertNotIn(term, s)

    def test_34_no_unsubscribe_url_exposed(self):
        self.assertNotIn('example.invalid', json.dumps(MODULE.parse_received(make_mail(), 1)))

    def test_35_no_external_links_clicked(self):
        self.assertNotIn('urllib.request', (HERE / 'check_received_mime.py').read_text())

    def test_36_no_email_sending_imports(self):
        src = (HERE / 'check_received_mime.py').read_text()
        for term in ('smtplib', 'requests.', 'http.client', 'imaplib', 'subprocess.'):
            self.assertNotIn(term, src)

    def test_37_full_explanation_of_limits(self):
        s = MODULE.parse_received(make_mail(), 1)['external_verifications_still_required']
        self.assertTrue(any('sender identity' in item.lower() for item in s))
        self.assertTrue(any('Founder permission' in item for item in s))

    def test_38_html_only_does_not_pretend_plaintext(self):
        self.assertFalse(MODULE.parse_received(make_mail(text=None), 1)['checks']['has_plaintext_part'])

    def test_39_plaintext_only_does_not_pretend_html(self):
        self.assertFalse(MODULE.parse_received(make_mail(html=None), 1)['checks']['has_html_part'])

    def test_40_no_final_ready_outcome_anywhere(self):
        for n in range(1,7):
            self.assertEqual(MODULE.parse_received(make_mail(issue=n), n)['status'], 'HOLD_UNSENT_UNVERIFIED')

    def test_41_cli_generates_redacted_report(self):
        with tempfile.TemporaryDirectory() as t:
            eml = Path(t) / 'private_sample.eml';eml.write_bytes(make_mail())
            out = Path(t) / 'result.json'
            proc = subprocess.run([sys.executable, str(HERE/'check_received_mime.py'), '--eml', str(eml),
                                   '--issue', '1', '--json-report', str(out)], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(json.loads(out.read_text())['status'], 'HOLD_UNSENT_UNVERIFIED')
            self.assertNotIn('example.invalid', proc.stdout)
            self.assertNotIn('test-subscriber', out.read_text())


if __name__ == '__main__':
    unittest.main()
