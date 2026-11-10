"""R260 offline synthetic regression tests. Never imply browser or QD approval."""
import importlib.util
import json
from pathlib import Path
import unittest

SRC = Path(__file__).resolve().parents[1] / 'tools/r260_family_card_print_disclosure_witness_hold.py'
spec = importlib.util.spec_from_file_location('r260', SRC)
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def fixture():
    labels = ''.join('<p><b>' + x + '</b> _______________</p>' for x in r.LABELS)
    return '''<style>@media screen { .pa-card-mainhide { color: green; } }
@media print { .pa-card-mainhide { display: none !important; }
  .pa-printonly { display: block !important; } }</style>
<div class="pa-alert pa-alert--stop pa-card-mainhide"><p>A printed card can be lost</p>
<p>Anyone who finds it can read it. Do not put a child's full name, a medical diagnosis or a password on it.</p></div>
<noscript><p>The form below still works and prints.</p></noscript>
<noscript><div class="pa-printsheet"><div class="pa-foldcard">''' + labels + '''</div></div></noscript>
<script>pr.appendChild(el('p', 'pa-printpage-note', 'Cut out each card and fold it on the dotted line to wallet size. Keep the card with you. Review it each year.'));</script>'''


def check(text):
    raw = text.encode('utf-8')
    return r.inspect(raw, expected_blob=r.git_blob(raw))


class Positive(unittest.TestCase):
    def test_positive_fixture_is_hold(self):
        self.assertEqual(check(fixture())['state'], r.HOLD)

    def test_release_flags_all_false(self):
        row = check(fixture())
        for key in ('browser_print_verified', 'privacy_certified', 'medical_safety_verified',
                    'source_review_approved', 'independent_qd_pass', 'merchant_approved', 'release_authorized'):
            self.assertIs(row[key], False)

    def test_observed_warning_is_hidden(self):
        self.assertTrue(check(fixture())['print_css_hides_original_privacy_alert'])

    def test_fallback_has_thirteen_fields(self):
        self.assertEqual(check(fixture())['nojs_print_fallback_field_count'], 13)

    def test_result_serializable_and_no_personal_values(self):
        self.assertNotIn('_______________', json.dumps(check(fixture())))

    def test_print_only_css_extraction(self):
        self.assertIn('pa-card-mainhide', r.print_css(fixture()))
        self.assertNotIn('color: green', r.print_css(fixture()))

    def test_independent_source_pin_enforced(self):
        with self.assertRaisesRegex(ValueError, 'original body identity'):
            r.inspect(fixture().encode('utf-8'))

    def test_safe_human_review_flag(self):
        self.assertTrue(check(fixture())['human_editorial_and_privacy_review_required'])

    def test_original_document_id_is_fixed(self):
        self.assertEqual(check(fixture())['source_path'], r.BODY_PATH)

    def test_syntax_imports(self):
        self.assertTrue(callable(r.audit))


MUTATIONS = []

def add(label, before, after):
    MUTATIONS.append((label, before, after))


for i, value in enumerate((
    'A printed card can be lost', 'Anyone who finds it can read it.',
    "a child's full name", 'a medical diagnosis', 'a password',
    'Cut out each card', 'Review it each year.',
    'The form below still works and prints.',
    'pa-alert--stop', 'pa-printsheet', 'pa-printpage-note',
)):
    add('tamper_copy_%02d' % i, value, 'REMOVED_REVIEW_WITNESS_%02d' % i)
for i, label in enumerate(r.LABELS):
    add('tamper_field_%02d' % i, '<b>'+label+'</b>', '<b>Changed %02d:</b>' % i)
for i, value in enumerate(('a password', 'a medical diagnosis', "a child's full name",
                           'Anyone who finds it can read it.', 'A printed card can be lost')):
    add('tamper_warning_%02d' % i, value, value.upper())
for i, value in enumerate(('lost', 'private', 'privacy', 'password', 'medical', 'child', 'school', 'confidential')):
    add('leak_print_note_%02d' % i, 'Review it each year.', 'Review it each year. ' + value)
for i, value in enumerate(('lost', 'private', 'privacy', 'password', 'diagnosis', 'confidential')):
    add('leak_fallback_%02d' % i, '<p><b>Reviewed:</b> _______________</p>',
        '<p><b>Reviewed:</b> _______________</p><p>' + value + '</p>')
for i, new in enumerate(('display: block !important', 'display: none', 'display: none;',
                         'visibility: hidden', 'opacity: 0', 'display : none')):
    add('tamper_print_rule_%02d' % i, 'display: none !important', new)
add('tamper_print_media', '@media print', '@media screen')
add('tamper_screen_alert_class', 'pa-alert pa-alert--stop pa-card-mainhide', 'pa-alert pa-alert--stop')
add('tamper_header', '<style>', '<style missing')
add('tamper_style_close', '</style>', '</wrong>')
add('tamper_print_sheet_close', '</noscript>\n<script>', '</something>\n<script>')


class Adversarial(unittest.TestCase):
    def test_reject_bad_bytes(self):
        for raw in (b'', b'\0', b'\xff', b'a'*3_000_001):
            with self.subTest(raw=raw[:8]), self.assertRaises(ValueError):
                r.inspect(raw, expected_blob=r.git_blob(raw))

    def test_reject_bad_pins(self):
        for pin in ('', 'a'*39, 'z'*40, 23, None):
            with self.subTest(pin=pin), self.assertRaises(ValueError):
                r.inspect(fixture().encode(), expected_blob=pin)

    def test_unbalanced_media_block(self):
        changed = fixture().replace('display: block !important; } }', 'display: block !important; }')
        with self.assertRaises(ValueError):
            check(changed)


def build_mutation(before, after):
    def body(self):
        original = fixture()
        self.assertIn(before, original)
        changed = original.replace(before, after, 1)
        self.assertNotEqual(changed, original)
        with self.assertRaises(ValueError):
            check(changed)
    return body


for label, before, after in MUTATIONS:
    setattr(Adversarial, 'test_' + label, build_mutation(before, after))


if __name__ == '__main__':
    unittest.main()
