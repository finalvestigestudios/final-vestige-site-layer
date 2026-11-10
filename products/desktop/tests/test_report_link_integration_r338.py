"""Synthetic integration checks of the publisher's new post-link witness."""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import report_evidence as report

class ReportLinkIntegrationR338(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="r338-integrated-")
        self.addCleanup(tmp.cleanup)
        self.parent = Path(tmp.name)
        self.destination = self.parent / 'verification.json'
        self.payload = {'release_authorized': False, 'status': 'integrity_only'}

    def temp_paths(self):
        return list(self.parent.glob('.fvs-candidate-report-*'))

    def test_real_hardlink_is_verified_then_staging_cleaned(self):
        report.publish_report(self.destination, self.payload)
        self.assertEqual(json.loads(self.destination.read_text()), self.payload)
        self.assertEqual(self.temp_paths(), [])

    def test_fake_link_creating_same_size_copy_rejected_with_evidence_preserved(self):
        def wrong_link(source, target):
            Path(target).write_bytes(b'X' + Path(source).read_bytes()[1:])
        with patch.object(report.os, 'link', side_effect=wrong_link):
            with self.assertRaises(report.ReportEvidenceError):
                report.publish_report(self.destination, self.payload)
        self.assertEqual(len(self.temp_paths()), 1)
        self.assertTrue(self.destination.exists())

    def test_fake_link_creating_identical_copy_rejected_as_wrong_inode(self):
        def wrong_link(source, target):
            Path(target).write_bytes(Path(source).read_bytes())
        with patch.object(report.os, 'link', side_effect=wrong_link):
            with self.assertRaises(report.ReportEvidenceError):
                report.publish_report(self.destination, self.payload)
        self.assertEqual(len(self.temp_paths()), 1)
        self.assertTrue(self.destination.exists())

    def test_link_is_noop_rejected_and_staging_preserved(self):
        with patch.object(report.os, 'link', return_value=None):
            with self.assertRaises(report.ReportEvidenceError):
                report.publish_report(self.destination, self.payload)
        self.assertEqual(len(self.temp_paths()), 1)
        self.assertFalse(self.destination.exists())

    def test_link_returns_real_hardlink_but_mutates_bytes_rejected(self):
        real_link = os.link
        def corrupt_link(source, target):
            real_link(source, target)
            Path(target).write_bytes(b'X' + Path(target).read_bytes()[1:])
        with patch.object(report.os, 'link', side_effect=corrupt_link):
            with self.assertRaises(report.ReportEvidenceError):
                report.publish_report(self.destination, self.payload)
        self.assertTrue(self.destination.exists())
        self.assertEqual(len(self.temp_paths()), 1)

    def test_existing_target_is_not_overwritten(self):
        self.destination.write_bytes(b'customer-kept')
        with self.assertRaises(report.ReportEvidenceError):
            report.publish_report(self.destination, self.payload)
        self.assertEqual(self.destination.read_bytes(), b'customer-kept')
        self.assertEqual(self.temp_paths(), [])

    def test_invalid_json_does_not_create_stage(self):
        with self.assertRaises(report.ReportEvidenceError):
            report.publish_report(self.destination, {'value': float('nan')})
        self.assertEqual(self.temp_paths(), [])

    def test_private_error_on_postlink_fault(self):
        with patch.object(report, 'verify_published_link', side_effect=report.LinkWitnessError('PRIVATE_CLIENT')):
            with self.assertRaises(report.ReportEvidenceError) as caught:
                report.publish_report(self.destination, self.payload)
        self.assertNotIn('PRIVATE_CLIENT', str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.assertEqual(len(self.temp_paths()), 1)

if __name__ == '__main__':
    unittest.main()
