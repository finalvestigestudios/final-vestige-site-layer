#!/usr/bin/env python3
"""R81: sanitization and fail-closed tests for authentic WP synced-pattern holds."""
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from wp_reusable_r77 import (
    R81_FAILURE_CODES, R81_PHASES, write_r81_safe_failure
)

class SyncedPatternHoldTests(unittest.TestCase):
    def _capture(self, error, phase='CUSTODY', width=390, js=True,
                 expected=True, completed=2):
        with tempfile.TemporaryDirectory() as root:
            dest = Path(root)
            record = write_r81_safe_failure(dest, error,
                width=width, js=js, expected_apollo=expected,
                phase=phase, completed_cases=completed)
            raw = (dest / 'R81_SYNCED_PATTERN_HOLD.json').read_text()
            self.assertEqual(json.loads(raw), record)
            return record, raw

    def test_known_source_assertion_code_preserved(self):
        e, raw = self._capture(AssertionError('R77_NESTED_SHORTCODE_MISSING'))
        self.assertEqual(e['assertion_code'], 'R77_NESTED_SHORTCODE_MISSING')
        self.assertEqual(e['checkpoint'], 'CUSTODY')
        self.assertFalse(e['authentic_wordpress_gate_passed'])

    def test_arbitrary_failure_message_never_written(self):
        secret = 'COOKIE=top-secret; URL=http://127.0.0.1:9438/wp-admin/'
        e, raw = self._capture(AssertionError(secret), phase=secret)
        self.assertNotIn(secret, raw)
        self.assertNotIn('top-secret', raw)
        self.assertNotIn('wp-admin', raw)
        self.assertEqual(e['assertion_code'], 'UNCLASSIFIED_ASSERTION')
        self.assertEqual(e['checkpoint'], 'UNCLASSIFIED_PHASE')

    def test_timeout_discloses_only_type(self):
        e, raw = self._capture(TimeoutError('password hunter2'), phase='PERFORMANCE')
        self.assertNotIn('hunter2', raw)
        self.assertEqual(e['exception_kind'], 'TimeoutError')
        self.assertEqual(e['assertion_code'], 'UNCLASSIFIED_ASSERTION')

    def test_unexpected_width_and_out_of_range_case_count_are_bounded(self):
        e, raw = self._capture(ValueError('http://private'), width=99999,
                               completed=999)
        self.assertIsNone(e['width'])
        self.assertEqual(e['completed_r77_cases'], 5)
        self.assertNotIn('http://private', raw)

    def test_static_codes_only(self):
        self.assertIn('R77_AXE_VIOLATIONS', R81_FAILURE_CODES)
        self.assertEqual(R81_PHASES, {
            'NAVIGATION','NETWORK','ASSET_DISCOVERY','CUSTODY',
            'INTERACTION','ACCESSIBILITY','PERFORMANCE','PRINT',
        })
        self.assertTrue(all(s.startswith('R77_') for s in R81_FAILURE_CODES))

if __name__ == '__main__':
    unittest.main()
