#!/usr/bin/env python3
"""Synthetic controls, not authenticated WordPress or real subscriber tests."""
import unittest
from verify_native_signup_continuity import inspect

NATIVE = '<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->'
MARGINS = '\n'.join(
    '<span class="fv-margin-strip__item" style="--i:%d">Record %02d from public source</span>' % (n,n)
    for n in range(72))
ORIGINAL = (
    '<!-- wp:html -->\n<div class="fv-margin-strip fv-margin-strip--rotator">'
    + MARGINS + '</div><!-- /wp:html -->\n'
    + '<!-- wp:group -->A new investigation. ' + NATIVE
    + '<p>Unsubscribe anytime · <a href="/dispatch/">About Dispatch</a></p><!-- /wp:group -->\n'
    + '<a href="/focus/">Seven Day Focus Fieldbook</a>'
)
REVIEW = '<!-- wp:shortcode -->[fv_ex2_playground]<!-- /wp:shortcode -->'


class ContinuityTests(unittest.TestCase):
    def assert_blocked(self, candidate, expected):
        result = inspect(ORIGINAL, candidate)
        self.assertEqual(result['decision'], 'RELEASE_HOLD')
        self.assertTrue(any(expected in x for x in result['blockers']), result['blockers'])

    def test_01_positive_preserved_native_and_records(self):
        receipt = inspect(ORIGINAL, ORIGINAL + '\n<!-- wp:html -->New archival section<!-- /wp:html -->')
        self.assertEqual(receipt['decision'], 'SOURCE_CONTINUITY_PASS_NOT_RELEASE_APPROVAL')
        self.assertEqual(receipt['candidate_record']['margins_items'], 72)

    def test_02_review_shortcode_is_not_release_page(self):
        self.assert_blocked(REVIEW, 'CANDIDATE_NATIVE_JETPACK_BLOCK')

    def test_03_removing_native_jetpack_fails(self):
        self.assert_blocked(ORIGINAL.replace(NATIVE,''), 'CANDIDATE_NATIVE_JETPACK_BLOCK')

    def test_04_mutating_jetpack_options_fails(self):
        self.assert_blocked(ORIGINAL.replace('is-style-split','is-style-other'),
                            'CANDIDATE_NATIVE_JETPACK_BLOCK_CHANGED')

    def test_05_duplicating_jetpack_fails(self):
        self.assert_blocked(ORIGINAL + NATIVE, 'CANDIDATE_NATIVE_JETPACK_BLOCK_NOT_EXACTLY_ONE')

    def test_06_missing_margin_fails(self):
        old = '<span class="fv-margin-strip__item" style="--i:71">Record 71 from public source</span>'
        self.assert_blocked(ORIGINAL.replace(old,''), 'CANDIDATE_MARGINS_CONTENT')

    def test_07_fabricated_margin_fails(self):
        self.assert_blocked(ORIGINAL.replace('Record 01 from public source','An invented record'),
                            'CANDIDATE_MARGINS_CONTENT')

    def test_08_isolated_review_link_leak_fails(self):
        self.assert_blocked(ORIGINAL+'<a href="/fv-ex2-focus-review/">Review</a>',
                            'REVIEW_ONLY_MARKER_LEAK')

    def test_09_review_shortcode_leak_fails(self):
        self.assert_blocked(ORIGINAL+REVIEW, 'REVIEW_ONLY_MARKER_LEAK')

    def test_10_missing_dispatch_fails(self):
        self.assert_blocked(ORIGINAL.replace('/dispatch/','/other/'), 'DISPATCH_DESTINATION_MISSING')

    def test_11_missing_focus_fails(self):
        self.assert_blocked(ORIGINAL.replace('/focus/','/other/'), 'FOCUS_DESTINATION_MISSING')

    def test_12_corrupted_baseline_fails(self):
        receipt = inspect(ORIGINAL.replace(NATIVE,''), ORIGINAL)
        self.assertIn('BASELINE_NATIVE_JETPACK_BLOCK_NOT_EXACTLY_ONE', receipt['blockers'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
