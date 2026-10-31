"""R22 editorial bridge: adversarial source status, anchors, accessibility, build integrity."""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
import zipfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
from build_sealed import build, ROOT
from qa.wayfinder_r22 import SECTIONS, build_wayfinder, WayfinderError
from qa.source_concordance import build_concordance
from qa.media_rights_ledger import build_media_rights
from qa.atlas_admission import build_atlas_admission


def receipts():
    return build_concordance()[2],build_media_rights()[3],build_atlas_admission()[3]


class R22Wayfinder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conc,cls.rights,cls.atlas=receipts()
        cls.html,cls.css,cls.receipt=build_wayfinder(cls.conc,cls.rights,cls.atlas)

    def test_01_route_integrity_and_no_js(self):
        self.assertEqual(len(SECTIONS),7)
        self.assertEqual(self.receipt['wayfinder_targets'],[x[0] for x in SECTIONS])
        for target, label, detail, status in SECTIONS:
            self.assertEqual(self.html.count(f'href="#{target}"'),1)
            self.assertIn(label,self.html)
        self.assertIn('<nav ',self.html)
        self.assertIn('aria-labelledby=',self.html)
        self.assertNotRegex(self.html,r'(?i)<(?:img|script|iframe|form)')
        self.assertNotIn('onclick=',self.html)

    def test_02_derived_risk_holds_are_visible(self):
        self.assertIn('six image-reuse reviews remain open',self.html)
        self.assertIn('zero admitted point coordinates',self.html)
        self.assertIn('one source catalog label is unresolved',self.html)
        self.assertEqual(self.receipt['admitted_coordinates'],0)
        self.assertEqual(self.receipt['admitted_edges'],0)
        self.assertEqual(self.receipt['media_rights_reuse_holds'],6)
        self.assertEqual(self.receipt['research_desk_identifier_review_holds'],1)

    def test_03_tampered_geo_or_rights_refused(self):
        for target,mutation in [('atlas',{'map_coordinates':1}),('atlas',{'map_edges':1}),
                                ('atlas',{'pending_primary_source_location_review':5}),
                                ('rights',{'status':'CLEARED'}),('rights',{'images_embedded':1}),
                                ('rights',{'catalog_label_holds':0}),
                                ('concordance',{'record_count':5}),('concordance',{'photos_embedded':1})]:
            with self.subTest(target=target,mutation=mutation):
                a,b,c=dict(self.conc),dict(self.rights),dict(self.atlas)
                {'concordance':a,'rights':b,'atlas':c}[target].update(mutation)
                with self.assertRaises(WayfinderError):build_wayfinder(a,b,c)

    def test_04_catalog_crosswalk_must_not_be_silently_resolved(self):
        a=dict(self.conc);a['research_desk_crosswalk']=dict(a['research_desk_crosswalk'])
        a['research_desk_crosswalk']['catalog_label_review_holds']=0
        with self.assertRaises(WayfinderError):build_wayfinder(a,self.rights,self.atlas)

    def test_05_export_count_hold_and_hash_receipt(self):
        with self.assertRaises(WayfinderError):
            build_wayfinder(self.conc,self.rights,self.atlas,receipt_export_count=8)
        self.assertEqual(self.receipt['html_sha256'],hashlib.sha256(self.html.encode()).hexdigest())
        self.assertEqual(self.receipt['css_sha256'],hashlib.sha256(self.css.encode()).hexdigest())

    def test_06_scoped_responsive_css_and_focus(self):
        self.assertIn('container-type:inline-size',self.css)
        self.assertIn('@container(max-width:480px)',self.css)
        self.assertIn(':focus-visible',self.css)
        self.assertIn('prefers-reduced-motion:reduce',self.css)
        self.assertNotRegex(self.css,r'(?m)^\s*(body|html|h1|a|nav|div)\s*\{')

    def test_07_plugin_embeds_same_hash_checked_seven_wayfinder_links(self):
        with tempfile.TemporaryDirectory() as t:
            out=Path(t)/'stage.zip';manifest=build(out)
            self.assertEqual(manifest['editorial_wayfinder'],self.receipt)
            self.assertEqual(manifest['outputs_sha256']['wayfinder.html'],self.receipt['html_sha256'])
            self.assertEqual(manifest['outputs_sha256']['wayfinder.css'],self.receipt['css_sha256'])
            with zipfile.ZipFile(out) as z:
                php=z.read(ROOT+'/fv-ex2-apollo-sealed.php')
            self.assertIn(b'X-FV-EX2-Apollo-Wayfinder-SHA256',php)
            self.assertNotIn(b"add_action('wp_ajax_nopriv_",php)

if __name__=='__main__':unittest.main()
