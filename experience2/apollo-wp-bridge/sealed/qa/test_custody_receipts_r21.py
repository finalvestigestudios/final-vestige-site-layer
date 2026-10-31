"""R21: independently verify editor-only content-addressed export shelf."""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from custody_receipts import build_receipts, EXPORT_NAMES, ReceiptError, CASEFILE_SHA
from source_concordance import build_context_index
from atlas_admission import build_atlas_admission
from media_rights_ledger import build_media_rights
GENERATED=HERE.parent.parent/'generated'


def prepared():
    return {name: ((GENERATED/name).read_bytes() if name in EXPORT_NAMES[:4]
                   else build_context_index().encode() if name=='source-context.json'
                   else build_atlas_admission()[2].encode() if name=='atlas-admission.json'
                   else build_media_rights()[2].encode()) for name in EXPORT_NAMES}

class ReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items=prepared()
        cls.html,cls.css,cls.receipt=build_receipts(cls.items)

    def test_01_exact_seven_verified_source_exports(self):
        self.assertEqual(list(self.receipt['exports_sha256']),list(EXPORT_NAMES))
        self.assertEqual(self.receipt['export_count'],7)
        self.assertEqual(self.receipt['canonical_source_revision'],CASEFILE_SHA)
        self.assertTrue(self.receipt['not_a_signature'])
        for name,data in self.items.items():
            self.assertIn(hashlib.sha256(data).hexdigest(),self.html)
            self.assertIn('{{FV_EX2_CUSTODY_EXPORT:'+name+'}}',self.html)
            self.assertEqual(self.html.count('data-custody-receipt="'+name+'"'),1)

    def test_02_no_editorial_fabrication_or_photo_or_scripts(self):
        self.assertEqual(self.receipt['media_reuse_clearances'],0)
        self.assertEqual(self.receipt['atlas_admitted_coordinates'],0)
        self.assertIn('It is not a digital signature',self.html)
        self.assertIn('source catalog discrepancy',self.html)
        self.assertIn('six image-reuse reviews',self.html)
        self.assertNotRegex(self.html.lower(),r'<(?:script|img|iframe|picture|form)\b')
        self.assertEqual(self.html.count('<a '),7)
        self.assertIn('prefers-reduced-motion',self.css)
        self.assertIn('container-type:inline-size',self.css)
        self.assertIn('min-height:44px',self.css)

    def test_03_bytes_are_hashed_not_parsed_and_normalized(self):
        m=dict(self.items);m['evidence-export.json']+=b'\n'
        newer=build_receipts(m)[2]
        self.assertNotEqual(newer['exports_sha256']['evidence-export.json'],
                            self.receipt['exports_sha256']['evidence-export.json'])
        self.assertEqual(newer['exports_sha256']['response-export.csv'],
                         self.receipt['exports_sha256']['response-export.csv'])

    def test_04_missing_reordered_or_synthetic_exports_fail_closed(self):
        for mutation in (dict(list(self.items.items())[:-1]),
                         dict(reversed(list(self.items.items()))),
                         {**self.items,'fake.json':b'not a real export'}):
            with self.subTest(mutation=tuple(mutation)),self.assertRaises(ReceiptError):
                build_receipts(mutation)

    def test_05_non_bytes_and_oversized_payload_denied(self):
        for payload in (None,'text',b'',b'A'*500001):
            m=dict(self.items);m['media-rights.json']=payload
            with self.subTest(type=type(payload).__name__),self.assertRaises(ReceiptError):
                build_receipts(m)

    def test_06_digest_and_html_deterministic(self):
        self.assertEqual(build_receipts(self.items),(self.html,self.css,self.receipt))
        self.assertEqual(hashlib.sha256(self.html.encode()).hexdigest(),self.receipt['html_sha256'])
        self.assertEqual(hashlib.sha256(self.css.encode()).hexdigest(),self.receipt['css_sha256'])
        self.assertEqual(self.html.count('data-custody-receipt='),7)

if __name__=='__main__':unittest.main()
