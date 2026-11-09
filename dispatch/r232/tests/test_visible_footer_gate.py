"""Privacy-safe synthetic red-team MIME fixtures; no outbound requests or sends."""
import pathlib
import sys
import unittest
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from visible_footer_gate import inspect_footer_channels, HOLD, safe_https

ADDRESS = 'Final Vestige Studios, Example Suite 200, Exampletown, CA 00000'
SUBJECT = 'The mind is not a camera'
URL = 'https://example.invalid/manage?opaque=123'


def fixture(html=None, plain=None, header=False):
    if html is None:
        html=f'<html><body><p>{ADDRESS}</p><a href="{URL}">Unsubscribe</a></body></html>'
    if plain is None:
        plain=f'Body. {ADDRESS}\nUnsubscribe: {URL}'
    m = EmailMessage()
    m['From'] = 'Publisher <p@example.invalid>'
    m['To'] = 'Recipient <test@example.invalid>'
    m['Subject'] = SUBJECT
    m['Date'] = formatdate(usegmt=True)
    m['Message-ID'] = make_msgid(domain='example.invalid')
    if header:
        m['List-Unsubscribe'] = f'<{URL}>'
    m.set_content(plain)
    m.add_alternative(html, subtype='html')
    return m.as_bytes()


class RedTeam(unittest.TestCase):
    def check(self, html=None, plain=None, header=False):
        return inspect_footer_channels(fixture(html, plain, header), expected_subject=SUBJECT,
                                       verified_publisher_address=ADDRESS)

    def test_baseline_offline_all_true_still_hold(self):
        r=self.check()
        self.assertEqual(r['blockers'], [])
        self.assertEqual(r['state'], HOLD)
        self.assertEqual(r['proof_level'], 'OFFLINE_BYTES_ONLY')

    def test_hidden_attribute_is_not_visible_proof(self):
        r=self.check(f'<div hidden>{ADDRESS}<a href="{URL}">Unsubscribe</a></div>', 'No footer')
        self.assertFalse(r['checks']['html_visible_address_present'])
        self.assertFalse(r['checks']['html_visible_optout'])

    def test_inline_display_none_not_visible(self):
        r=self.check(f'<div style="display:none">{ADDRESS}<a href="{URL}">Unsubscribe</a></div>')
        self.assertFalse(r['checks']['html_visible_address_present'])
        self.assertFalse(r['checks']['html_visible_optout'])

    def test_template_not_visible(self):
        r=self.check(f'<template>{ADDRESS}<a href="{URL}">Unsubscribe</a></template>')
        self.assertFalse(r['checks']['html_visible_address_present'])

    def test_aria_hidden_not_visible(self):
        r=self.check(f'<div aria-hidden="true">{ADDRESS}<a href="{URL}">Unsubscribe</a></div>')
        self.assertFalse(r['checks']['html_visible_optout'])

    def test_opacity_zero_not_visible(self):
        r=self.check(f'<div style="opacity:0">{ADDRESS}<a href="{URL}">Unsubscribe</a></div>')
        self.assertFalse(r['checks']['html_visible_address_present'])

    def test_visibility_hidden_not_visible(self):
        r=self.check(f'<section style="visibility: hidden">{ADDRESS}</section>')
        self.assertFalse(r['checks']['html_visible_address_present'])

    def test_sender_has_address_only_in_plain_is_blocker(self):
        r=self.check('<p>Here is the story, without postal details.</p>')
        self.assertTrue(r['checks']['plaintext_address_present'])
        self.assertFalse(r['checks']['html_visible_address_present'])

    def test_html_only_unsubscribe_is_blocker(self):
        r=self.check(plain=f'Body {ADDRESS}')
        self.assertFalse(r['checks']['plaintext_visible_optout'])

    def test_plain_only_unsubscribe_is_blocker(self):
        r=self.check(html=f'<p>{ADDRESS}</p><p>No optout present.</p>')
        self.assertFalse(r['checks']['html_visible_optout'])

    def test_header_only_unsubscribe_does_not_pass(self):
        r=self.check(html=f'<p>{ADDRESS}</p>', plain=f'{ADDRESS}', header=True)
        self.assertFalse(r['checks']['plaintext_visible_optout'])
        self.assertFalse(r['checks']['html_visible_optout'])

    def test_unsafe_scheme_is_rejected(self):
        r=self.check(html=f'<p>{ADDRESS}</p><a href="javascript:alert(1)">Unsubscribe</a>')
        self.assertFalse(r['checks']['html_visible_optout'])

    def test_opaque_token_https_url_is_accepted(self):
        r=self.check()
        self.assertTrue(r['checks']['html_visible_optout'])
        self.assertTrue(r['checks']['plaintext_visible_optout'])

    def test_missing_plaintext_postal_is_rejected(self):
        r=self.check(plain=f'Body\nUnsubscribe: {URL}')
        self.assertFalse(r['checks']['plaintext_address_present'])

    def test_mailto_only_not_assumed_jetpack_optout(self):
        r=self.check(html=f'<p>{ADDRESS}</p><a href="mailto:u@example.invalid">Unsubscribe</a>')
        self.assertFalse(r['checks']['html_visible_optout'])

    def test_safe_https_rejects_credentials_and_space(self):
        self.assertFalse(safe_https('https://user:pass@example.invalid/manage'))
        self.assertFalse(safe_https('https://example.invalid/foo bar'))

    def test_private_inputs_never_leak(self):
        s=str(self.check())
        self.assertNotIn(ADDRESS, s)
        self.assertNotIn(URL, s)
        self.assertNotIn('test@example.invalid',s)

    def test_attested_address_alone_does_not_prove_real_address(self):
        r=self.check()
        self.assertIn('Publisher postal ownership/validity', ' '.join(r['manual_checks_required']))
        self.assertEqual(r['state'], HOLD)


if __name__ == '__main__':
    unittest.main()
