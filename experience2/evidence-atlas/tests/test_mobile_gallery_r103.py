#!/usr/bin/env python3
"""R103 adversarial source boundary tests (no network or WordPress writes)."""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from build_mobile_gallery_r103 import build, validate, R99_RECEIPT


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


class MobileGalleryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.environ.get('APOLLO_R103_R99'):
            raise unittest.SkipTest('R103 sealed fixture required; dedicated R103 CI supplies APOLLO_R103_R99')
        cls.src=Path(os.environ['APOLLO_R103_R99']).resolve()
        validate(cls.src)

    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='apollo-r103-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.src=self.root/'src'
        shutil.copytree(self.__class__.src,self.src)

    def assert_rejected(self):
        with self.assertRaises(ValueError): build(self.src,self.root/'output')

    def test_deterministic_zip_and_pins(self):
        one=build(self.src,self.root/'one',self.root/'one.zip')
        two=build(self.src,self.root/'two',self.root/'two.zip')
        self.assertEqual(sha(self.root/'one.zip'),sha(self.root/'two.zip'))
        self.assertEqual(one,two)
        self.assertEqual(one['nasa_photo_rights_cleared'],0)
        self.assertEqual(one['geo_pins'],0)
        self.assertEqual(one['images_embedded'],0)
        php=(self.root/'one/fv-apollo-r99-private-preview.php').read_text()
        self.assertIn("current_user_can('edit_others_posts')",php)
        for name in ('review/R97_SOURCE_GALLERY.html','review/source_gallery_r97.css','review/source_gallery_r97.js'):
            self.assertIn("'"+one['files'][name]+"'",php)
        html=(self.root/'one/review/R97_SOURCE_GALLERY.html').read_text()
        self.assertEqual(html.count('data-jump-compare'),6)
        self.assertEqual(html.count('https://www.nasa.gov/image-detail/'),12)
        self.assertEqual(html.count('INDIVIDUAL RIGHTS REVIEW PENDING'),6)

    def test_reject_modified_photo_claims(self):
        p=self.src/'review/R97_SOURCE_GALLERY.html'
        p.write_text(p.read_text().replace('RIGHTS REVIEW PENDING','RIGHTS CLEARED'))
        self.assert_rejected()

    def test_reject_modified_css(self):
        p=self.src/'review/source_gallery_r97.css'
        p.write_bytes(p.read_bytes()+b'/* unauthorized */')
        self.assert_rejected()

    def test_reject_unreviewed_asset(self):
        (self.src/'review/other.js').write_text('alert(1)')
        self.assert_rejected()

    def test_reject_missing_asset(self):
        (self.src/'review/source_gallery_r97.js').unlink()
        self.assert_rejected()

    def test_reject_symlink(self):
        p=self.src/'review/source_gallery_r97.js';p.unlink();p.symlink_to(self.src/'review/source_gallery_r97.css')
        self.assert_rejected()

    def test_reject_release_flag(self):
        p=self.src/R99_RECEIPT
        r=json.loads(p.read_text());r['publication_approved']=True;p.write_text(json.dumps(r))
        self.assert_rejected()

    def test_reject_weakened_role_access(self):
        p=self.src/'fv-apollo-r99-private-preview.php'
        p.write_text(p.read_text().replace("current_user_can('edit_others_posts')","current_user_can('edit_posts')"))
        self.assert_rejected()


if __name__=='__main__':unittest.main()
