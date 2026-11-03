#!/usr/bin/env python3
"""R99 read-only preview: adversarial inputs, route parity, reproducibility and PHP pinning."""
import importlib.util
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
TOOL=ROOT/'experience2/evidence-atlas/tools/build_wp_private_preview_r99.py'
TEMPLATE=ROOT/'experience2/evidence-atlas/integration/r99-private-preview-template.php'
if not TOOL.exists():
    TOOL=Path(__file__).with_name('build_wp_private_preview_r99.py')
    TEMPLATE=Path(__file__).with_name('r99-private-preview-template.php')
spec=importlib.util.spec_from_file_location('r99',TOOL)
r99=importlib.util.module_from_spec(spec);spec.loader.exec_module(r99)

class PrivatePreviewR99(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.work=Path(cls.temp.name)
        cls.source=cls.work/'r98'
        import os,sys
        override=os.environ.get('APOLLO_R98_SRC')
        if override:
            shutil.copytree(override,cls.source)
        else:
            tool=TOOL.parent
            for stage,args in (
                ('r92',[str(tool/'build_reciprocal_routes_r92.py'),str(cls.work/'r92')]),
                ('r93',[str(tool/'build_source_passports_r93.py'),'--src',str(cls.work/'r92'),'--out',str(cls.work/'r93')]),
                ('r94',[str(tool/'build_curated_atlas_r94.py'),'--src',str(cls.work/'r93'),'--out',str(cls.work/'r94')]),
                ('r97',[str(tool/'build_source_gallery_r97.py'),'--src',str(cls.work/'r94'),'--out',str(cls.work/'r97')]),
                ('r98',[str(tool/'build_source_roundtrip_r98.py'),'--src',str(cls.work/'r97'),'--out',str(cls.source)]),
            ):
                subprocess.run([sys.executable,*args],check=True,stdout=subprocess.DEVNULL)
        r99.verify(cls.source)
    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def output(self):
        temp=tempfile.TemporaryDirectory();p=Path(temp.name)
        receipt=r99.build(self.source,p/'one',TEMPLATE,p/'one.zip')
        return temp,p,receipt

    def test_custody_and_no_cms_writes(self):
        temp,p,receipt=self.output()
        try:
            self.assertEqual(receipt['view_count'],7)
            self.assertEqual(receipt['content_or_settings_writes'],0)
            self.assertFalse(receipt['publication_approved'])
            self.assertEqual(receipt['rights_cleared'],0)
            self.assertEqual(receipt['images_embedded'],0)
            self.assertEqual(len(receipt['files']),len(list((p/'one/review').iterdir()))+1)
            php=(p/'one/fv-apollo-r99-private-preview.php').read_text()
            self.assertIn('current_user_can(\'edit_others_posts\')',php)
            self.assertNotIn('current_user_can(\'edit_posts\')',php)
            fixture=(TEMPLATE.parent.parent/'tests/php_preview_contract_r99.php').read_text()
            self.assertIn("current_user_can('edit_others_posts')",fixture)
            self.assertNotIn("current_user_can('edit_posts')",fixture)
            self.assertNotIn('update_option(',php)
            self.assertNotIn('wp_insert_post(',php)
            for name,sha in receipt['files'].items():
                self.assertEqual(r99.digest((p/'one'/name).read_bytes()),sha)
        finally:temp.cleanup()

    def test_nasa_links_and_42_source_cards_stay_present(self):
        temp,p,_=self.output()
        try:
            records=json.loads((self.source/'R93_SOURCE_PASSPORTS.json').read_text())['records']
            for name in r99.VIEWS:
                html=(p/'one/review'/name).read_text()
                self.assertIn('?fv_apollo_r99=',html)
                self.assertNotIn('<img',html.lower())
                for record in records:
                    self.assertIn(record['url'],html)
                    self.assertIn(record['catalog'],html)
                for ref in re.findall(r'\b(?:href|src)="([^"]+)"',html):
                    self.assertTrue(ref.startswith(('#','https://www.nasa.gov/','?fv_apollo_r99=')),ref)
        finally:temp.cleanup()

    def test_private_adapter_php_lints(self):
        if shutil.which('php') is None:self.skipTest('php CLI absent')
        temp,p,_=self.output()
        try:
            proc=subprocess.run(['php','-l',str(p/'one/fv-apollo-r99-private-preview.php')],capture_output=True,text=True)
            self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
        finally:temp.cleanup()

    def test_deterministic(self):
        temp,p,_=self.output()
        try:
            r99.build(self.source,p/'two',TEMPLATE,p/'two.zip')
            self.assertEqual((p/'one.zip').read_bytes(),(p/'two.zip').read_bytes())
        finally:temp.cleanup()

    def test_r98_manifest_tamper(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'copy';shutil.copytree(self.source,p)
            f=p/'R98_ROUNDTRIP_RECEIPT.json';f.write_text(f.read_text()+'\n')
            with self.assertRaisesRegex(ValueError,'EXACT_R98_RECEIPT'):r99.verify(p)

    def test_source_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'copy';shutil.copytree(self.source,p)
            f=p/'R97_SOURCE_GALLERY.html';f.write_text(f.read_text().replace('NASA source 01','NASA source 88',1))
            with self.assertRaisesRegex(ValueError,'SOURCE_HASH'):r99.verify(p)

    def test_unexpected_asset_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'copy';shutil.copytree(self.source,p);(p/'injected.js').write_text('alert(1)')
            with self.assertRaisesRegex(ValueError,'EXTRA_OR_MISSING'):r99.verify(p)

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'copy';shutil.copytree(self.source,p)
            f=p/'source_gallery_r97.js';f.unlink();f.symlink_to(self.source/f.name)
            with self.assertRaisesRegex(ValueError,'SOURCE_HASH'):r99.verify(p)

    def test_unreviewed_markup_rejected(self):
        allowed={'R97_SOURCE_GALLERY.html','source_gallery_r97.css'}
        for html in ('<html><a href="https://evil.example/x"></a></html>',
                     '<html><img src="pic.jpg"></html>',
                     '<html><a onclick="alert(1)" href="#source">X</a></html>'):
            with self.assertRaises(ValueError):r99.review_html(html,allowed)

    def test_fragment_retained(self):
        original='<html><a href="R97_SOURCE_GALLERY.html#gallery-01">Gallery</a></html>'
        got=r99.review_html(original,{'R97_SOURCE_GALLERY.html'})
        self.assertIn('?fv_apollo_r99=R97_SOURCE_GALLERY.html#gallery-01',got)

    def test_nonempty_output_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'out';p.mkdir();(p/'existing').write_text('x')
            with self.assertRaisesRegex(ValueError,'OUTPUT_NOT_EMPTY'):r99.build(self.source,p,TEMPLATE)

    def test_bad_template_marker_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t);template=p/'bad.php';template.write_text('<?php echo "no pins";')
            with self.assertRaisesRegex(ValueError,'TEMPLATE_MARKER'):r99.build(self.source,p/'out',template)

if __name__=='__main__':unittest.main()
