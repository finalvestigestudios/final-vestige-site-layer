#!/usr/bin/env python3
"""Adversarial, offline-only tests for tagged Apollo PDF source annotations.

No network, CMS access, screenshots or browser required. The separate real
Chromium PDF test establishes that the generated files satisfy this contract.
"""
from __future__ import annotations
import json
from pathlib import Path
import unittest
from browser_pdf_r26 import verify_pdf_semantics
from print_source_transcript_r25 import CASEFILE, NASA_POLICY, REPORT as NASA_REPORT

SOURCES = [r['image_url'] for r in json.loads(
    (CASEFILE / 'records.json').read_text(encoding='utf-8'))['records']]
META = ('Title: Private Apollo 1 Evidence Review — Final Vestige\n'
        'Tagged:          yes\nJavaScript:      no\n')


def inventory(sources=None, extra=None):
    destinations = (SOURCES if sources is None else sources) + [NASA_REPORT, NASA_POLICY]
    if extra is not None:
        destinations.append(extra)
    return 'Page  Type          URL\n' + ''.join(
        '   1  Annotation    ' + uri + '\n' for uri in destinations)


class OfflinePdfSemanticsR27(unittest.TestCase):
    def test_valid_source_only_tagged_document(self):
        result = verify_pdf_semantics(META, inventory(), SOURCES)
        self.assertEqual(result['clickable_nasa_records'], 6)
        self.assertEqual(result['unapproved_destinations'], 0)
        self.assertTrue(result['tagged'])

    def test_reject_untagged_document(self):
        with self.assertRaisesRegex(AssertionError, 'not structurally tagged'):
            verify_pdf_semantics(META.replace('yes', 'no'), inventory(), SOURCES)

    def test_reject_missing_document_title(self):
        with self.assertRaisesRegex(AssertionError, 'recognizable document title'):
            verify_pdf_semantics(META.replace('Private Apollo 1 Evidence Review — Final Vestige', 'Untitled'), inventory(), SOURCES)

    def test_reject_pdf_javascript(self):
        with self.assertRaisesRegex(AssertionError, 'embedded JavaScript'):
            verify_pdf_semantics(META.replace('JavaScript:      no', 'JavaScript:      yes'), inventory(), SOURCES)

    def test_reject_missing_source_annotation(self):
        with self.assertRaisesRegex(AssertionError, 'Missing canonical NASA link'):
            verify_pdf_semantics(META, inventory(SOURCES[1:]), SOURCES)

    def test_reject_duplicate_source_annotation(self):
        with self.assertRaisesRegex(AssertionError, 'one clickable PDF source link'):
            verify_pdf_semantics(META, inventory(SOURCES + [SOURCES[0]]), SOURCES)

    def test_reject_unapproved_external_destination(self):
        with self.assertRaisesRegex(AssertionError, 'unauthorized PDF link'):
            verify_pdf_semantics(META, inventory(extra='https://example.com/'), SOURCES)

    def test_reject_non_https_annotation(self):
        with self.assertRaisesRegex(AssertionError, 'non-HTTPS PDF annotation'):
            verify_pdf_semantics(META, inventory(extra='javascript:alert(1)'), SOURCES)

    def test_reject_rights_policy_omission(self):
        with self.assertRaisesRegex(AssertionError, 'Missing canonical NASA link'):
            verify_pdf_semantics(META, inventory().replace('   1  Annotation    ' + NASA_POLICY + '\n', ''), SOURCES)

    def test_reject_five_record_contract(self):
        with self.assertRaisesRegex(AssertionError, 'Exactly six distinct'):
            verify_pdf_semantics(META, inventory(), SOURCES[:5])


if __name__ == '__main__':
    unittest.main(verbosity=2)
