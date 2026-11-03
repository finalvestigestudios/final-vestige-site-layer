#!/usr/bin/env python3
"""R98 adversarial source custody, native navigation, deterministic archive acceptance."""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TOOLS=ROOT/'experience2/evidence-atlas/tools'
if not (TOOLS/'build_source_roundtrip_r98.py').exists():
    TOOLS=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r98',TOOLS/'build_source_roundtrip_r98.py')
r98=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r98)

class RoundTripTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        temp=Path(cls.temp.name)
        if os.environ.get('APOLLO_R97_SRC'):
            cls.source=Path(os.environ['APOLLO_R97_SRC'])
        else:
            subprocess.run([sys.executable,str(TOOLS/'build_reciprocal_routes_r92.py'),str(temp/'r92')],check=True)
            subprocess.run([sys.executable,str(TOOLS/'build_source_passports_r93.py'),'--src',str(temp/'r92'),'--out',str(temp/'r93')],check=True)
            subprocess.run([sys.executable,str(TOOLS/'build_curated_atlas_r94.py'),'--src',str(temp/'r93'),'--out',str(temp/'r94')],check=True)
            subprocess.run([sys.executable,str(TOOLS/'build_source_gallery_r97.py'),'--src',str(temp/'r94'),'--out',str(temp/'r97')],check=True)
            cls.source=temp/'r97'
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def isolated_source(self):
        t=tempfile.TemporaryDirectory()
        p=Path(t.name)/'source'
        shutil.copytree(self.source,p)
        return t,p

    def test_full_custody_and_links(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)
            result=r98.build(self.source,p/'out')
            self.assertEqual(result['views'],7)
            self.assertEqual(result['reciprocal_gallery_links'],54)
            self.assertEqual(len(result['files']),30)
            self.assertEqual(result['photo_rights_cleared'],0)
            self.assertEqual(result['geo_pins'],0)
            self.assertEqual(result['images_embedded'],0)
            source=json.loads((self.source/'R93_SOURCE_PASSPORTS.json').read_text())
            for file,prefix in r98.VIEWS.items():
                s=(p/'out'/file).read_text()
                self.assertEqual(s.count('class="r98-route"'),6)
                self.assertEqual(s.count('href="r98_crosslinks.css"'),1)
                self.assertNotIn('<img',s)
                self.assertNotIn('<iframe',s)
                for row in source['records']:
                    ident=prefix+row['id']
                    match=re.search(r'<article\b[^>]*\bid="'+re.escape(ident)+r'"[^>]*>(.*?)</article>',s,re.S)
                    self.assertIsNotNone(match)
                    card=match.group(1)
                    self.assertIn(row['url'],card)
                    self.assertIn(row['catalog'],card)
                    self.assertIn('Alternate views of NASA source '+row['id'],card)
                    if file!='R97_SOURCE_GALLERY.html':
                        self.assertIn('R97_SOURCE_GALLERY.html#gallery-'+row['id'],card)
                    else:
                        for target in ('R85_NASA_SOURCE_REVIEW.html#r85-source-', 'R88_READING_ROOM.html#r88-', 'R89_REVIEW_HUB.html#r89-source-'):
                            self.assertIn(target+row['id'],card)
            for name,digest in result['files'].items():
                self.assertEqual(r98.sha((p/'out'/name).read_bytes()),digest)

    def test_reproducible_zip(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)
            r98.build(self.source,p/'one',p/'one.zip')
            r98.build(self.source,p/'two',p/'two.zip')
            self.assertEqual((p/'one.zip').read_bytes(),(p/'two.zip').read_bytes())
            self.assertEqual(len((p/'one.zip').read_bytes())>10000,True)

    def test_unreviewed_js_fails(self):
        t,p=self.isolated_source()
        try:
            (p/'evil.js').write_text('alert(1)')
            with self.assertRaisesRegex(ValueError,'UNREVIEWED_FILES'):r98.custody(p)
        finally:t.cleanup()

    def test_mutated_html_fails_even_if_card_kept(self):
        t,p=self.isolated_source()
        try:
            f=p/'R97_SOURCE_GALLERY.html';f.write_text(f.read_text()+'<script>bad()</script>')
            with self.assertRaisesRegex(ValueError,'HASH_MISMATCH'):r98.custody(p)
        finally:t.cleanup()

    def test_swapped_source_even_with_rehashed_receipt_fails(self):
        t,p=self.isolated_source()
        try:
            f=p/'R88_READING_ROOM.html';s=f.read_text();a='https://www.nasa.gov/image-detail/apollo-1-crew-honored/';b='https://www.nasa.gov/image-detail/amf-s67-15717/'
            self.assertIn(a,s);self.assertIn(b,s)
            s=re.sub(r'(<article\b[^>]*\bid="r88-01"[^>]*>)(.*?)(</article>)',lambda m:m.group(1)+m.group(2).replace(a,'SWAPPED_SOURCE_01')+m.group(3),s,count=1,flags=re.S)
            f.write_text(s)
            rp=p/'R97_GALLERY_RECEIPT.json';v=json.loads(rp.read_text());v['files'][f.name]=r98.sha(f.read_bytes());rp.write_text(json.dumps(v))
            with self.assertRaisesRegex(ValueError,'SOURCE_CARD_MISMATCH'):
                r98.build(p,Path(t.name)/'out')
        finally:t.cleanup()

    def test_falsely_cleared_rights_flag_fails(self):
        t,p=self.isolated_source()
        try:
            f=p/'R97_GALLERY_RECEIPT.json';v=json.loads(f.read_text());v['photo_rights_cleared']=1;f.write_text(json.dumps(v))
            with self.assertRaisesRegex(ValueError,'UNAPPROVED_RELEASE'):r98.custody(p)
        finally:t.cleanup()

    def test_provisional_day_cannot_change_even_with_updated_receipt(self):
        t,p=self.isolated_source()
        try:
            f=p/'R93_SOURCE_PASSPORTS.json';data=json.loads(f.read_text());data['records'][0]['date']='January 27, 1967';f.write_text(json.dumps(data))
            rp=p/'R97_GALLERY_RECEIPT.json';v=json.loads(rp.read_text());v['files'][f.name]=r98.sha(f.read_bytes());rp.write_text(json.dumps(v))
            with self.assertRaisesRegex(ValueError,'CREW_PROVISIONAL'):r98.custody(p)
        finally:t.cleanup()

    def test_output_exists_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'dirty').write_text('existing')
            with self.assertRaisesRegex(ValueError,'NONEMPTY_OUTPUT'):r98.build(self.source,p)

    def test_archive_exists_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'existing.zip').write_bytes(b'old')
            with self.assertRaisesRegex(ValueError,'ARCHIVE_EXISTS'):r98.build(self.source,p/'new',p/'existing.zip')

    def test_input_symlink_fails(self):
        t,p=self.isolated_source()
        try:
            (p/'r98_fake.css').symlink_to(p/'source_gallery_r97.css')
            with self.assertRaisesRegex(ValueError,'UNREVIEWED_FILES'):r98.custody(p)
        finally:t.cleanup()

if __name__=='__main__':unittest.main()
