#!/usr/bin/env python3
"""R26 offline custody contract, complementary to real Chromium PDF tests."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import unittest
from print_source_transcript_r25 import build_print_transcript, CASEFILE, GENERATED, CASEFILE_PIN

class PrintPdfR26(unittest.TestCase):
    def test_offline_fingerprints_are_exact_staged_bytes(self):
        html, css, receipt = build_print_transcript()
        record_digest=sha256((CASEFILE/'records.json').read_bytes()).hexdigest()
        export_digest=sha256((GENERATED/'evidence-export.json').read_bytes()).hexdigest()
        self.assertEqual(receipt['casefile_head'],CASEFILE_PIN)
        self.assertEqual(receipt['casefile_records_sha256'],record_digest)
        self.assertEqual(receipt['evidence_export_sha256'],export_digest)
        for value in (CASEFILE_PIN,record_digest,export_digest):
            self.assertEqual(html.count(value),1)
        self.assertIn('they do not independently authenticate NASA records',html)
        self.assertIn('Offline source-custody fingerprints',html)
        self.assertIn('@media print',css)

    def test_no_sensitive_or_geographic_media_in_offline_ledger(self):
        html, css, receipt=build_print_transcript()
        self.assertEqual(receipt['records'],6)
        self.assertEqual(receipt['images_embedded'],0)
        self.assertEqual(receipt['atlas_pins'],0)
        self.assertEqual(receipt['atlas_edges'],0)
        self.assertIn('IMAGE REUSE NOT CLEARED',html)
        for forbidden in ('<img','<script','<iframe','_wpnonce','admin-ajax','data-lat=','data-lon='):
            self.assertNotIn(forbidden,html.lower())

if __name__=='__main__':unittest.main()
