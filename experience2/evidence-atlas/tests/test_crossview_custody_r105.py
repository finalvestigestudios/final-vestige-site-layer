#!/usr/bin/env python3
"""R105 adversarial source/route tests; supplied fixture must be sealed R103."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_source_crossview_r105 import audit, RECEIPT


class CrossviewCustodyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.environ.get('APOLLO_R105_STAGE'):
            raise unittest.SkipTest('R105 sealed fixture required; workflow supplies APOLLO_R105_STAGE')
        cls.fixture = Path(os.environ['APOLLO_R105_STAGE']).resolve()
        cls.verified = audit(cls.fixture)

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='apollo-r105-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / 'stage'
        shutil.copytree(self.fixture, self.root)

    def tamper(self, filename, before, after, update_receipt=True):
        p = self.root / 'review' / filename
        raw = p.read_text(encoding='utf-8')
        self.assertIn(before, raw)
        p.write_text(raw.replace(before, after, 1), encoding='utf-8')
        if update_receipt:
            rp = self.root / RECEIPT
            receipt = json.loads(rp.read_text())
            receipt['files']['review/' + filename] = hashlib.sha256(p.read_bytes()).hexdigest()
            rp.write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')

    def test_repeatable_receipt(self):
        self.assertEqual(audit(self.root), audit(self.root))
        self.assertEqual(self.verified['source_count'], 6)
        self.assertEqual(self.verified['view_count'], 7)
        self.assertGreaterEqual(self.verified['fragment_links_checked'], 50)

    def test_detect_wrong_hash(self):
        self.tamper('R97_SOURCE_GALLERY.html', 'STAGING HOLD', 'STAGING MOVE', False)
        with self.assertRaisesRegex(ValueError, 'R105_HASH_MISMATCH'):
            audit(self.root)

    def test_detect_broken_fragment_even_with_new_hash(self):
        self.tamper('R97_SOURCE_GALLERY.html', '#passport-01', '#nonexistent-r105')
        with self.assertRaisesRegex(ValueError, 'R105_BROKEN_FRAGMENT'):
            audit(self.root)

    def test_detect_invented_nasa_source_even_with_new_hash(self):
        self.tamper('R97_SOURCE_GALLERY.html',
                    'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
                    'https://www.nasa.gov/image-detail/unreviewed-source-r105/')
        with self.assertRaisesRegex(ValueError, 'R105_SOURCE_SET_DRIFT'):
            audit(self.root)

    def test_detect_unreviewed_geography_even_with_new_hash(self):
        self.tamper('R97_SOURCE_GALLERY.html', 'data-card="01"',
                    'data-card="01" data-lat="28.5"')
        with self.assertRaisesRegex(ValueError, 'R105_VIEW_INTEGRITY'):
            audit(self.root)

    def test_detect_photo_embed_even_with_new_hash(self):
        self.tamper('R97_SOURCE_GALLERY.html', '<main id="gallery">',
                    '<main id="gallery"><img src="unreviewed.jpg" alt="">')
        with self.assertRaisesRegex(ValueError, 'R105_VIEW_INTEGRITY'):
            audit(self.root)

    def test_detect_duplicate_id_even_with_new_hash(self):
        self.tamper('R97_SOURCE_GALLERY.html', '<main id="gallery">',
                    '<main id="gallery"><span id="gallery"></span>')
        with self.assertRaisesRegex(ValueError, 'R105_DUPLICATE_HTML_ID'):
            audit(self.root)

    def test_detect_rights_claim_removed_even_with_new_hash(self):
        self.tamper('R97_SOURCE_GALLERY.html',
                    'INDIVIDUAL RIGHTS REVIEW PENDING', 'RIGHTS CLEARED')
        with self.assertRaisesRegex(ValueError, 'R105_GALLERY_RIGHTS_OR_PROVISIONAL_CLAIM_CHANGED'):
            audit(self.root)

    def test_detect_added_unapproved_asset(self):
        (self.root / 'review' / 'unreviewed.js').write_text('alert(1)')
        with self.assertRaisesRegex(ValueError, 'R105_FILE_INVENTORY'):
            audit(self.root)

    def test_detect_removed_historic_receipt(self):
        (self.root / 'R99_PRIVATE_PREVIEW_RECEIPT.json').unlink()
        with self.assertRaisesRegex(ValueError, 'R105_FILE_INVENTORY'):
            audit(self.root)


if __name__ == '__main__':
    unittest.main()
