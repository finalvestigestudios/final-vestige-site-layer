#!/usr/bin/env python3
"""R33 source/editorial mutation tests. No network or WordPress writes."""
import copy
import json
import os
from pathlib import Path
import unittest
from bs4 import BeautifulSoup
from nasa_catalog_custody_r33 import validate_registry,verify_casefile,render

HERE=Path(__file__).resolve().parent
REG=json.loads((HERE/'nasa_catalog_primary_r33.json').read_text())
CASE_PATH=Path(os.environ.get('FV_APOLLO_CASEFILE_HTML',str(HERE/'actual_php_response.html')))
CASE=CASE_PATH.read_text() if CASE_PATH.exists() else None

class SourceCustodyTests(unittest.TestCase):
    def invalid(self, edit):
        bad=copy.deepcopy(REG);edit(bad)
        with self.assertRaises(ValueError):validate_registry(bad)

    def invalid_case(self, edit):
        if CASE is None:self.skipTest('set FV_APOLLO_CASEFILE_HTML to exact generated PHP response')
        soup=BeautifulSoup(CASE,'html.parser');edit(soup)
        with self.assertRaises(ValueError):verify_casefile(str(soup),REG)

    def test_complete_real_sealed_php(self):
        validate_registry(REG)
        if CASE is None:self.skipTest('set FV_APOLLO_CASEFILE_HTML to exact generated PHP response')
        verify_casefile(CASE,REG)

    def test_six_nasa_domains(self):
        self.assertEqual(len(REG['records']),6)
        self.assertTrue(all(r['source'].startswith('https://www.nasa.gov/image-detail/') for r in REG['records']))

    def test_wrong_catalog_url(self):
        self.invalid(lambda d:d['records'][4].update(source='https://www.nasa.gov/image-detail/amf-s67-15717/'))

    def test_source_domain_trick(self):
        self.invalid(lambda d:d['records'][3].update(source='https://www.nasa.gov.evil.invalid/image-detail/a/'))

    def test_date_conflation(self):
        self.invalid(lambda d:d['records'][3].update(date='1967-01-24'))

    def test_2017_context_removed(self):
        self.invalid(lambda d:d['records'][3].update(limitation='This is a source image.'))

    def test_catalog_alias_hold_removed(self):
        self.invalid(lambda d:d['records'][0].update(identity_status='SOURCE VERIFIED'))

    def test_rights_hold_removed(self):
        self.invalid(lambda d:d['records'][2].update(identity_status='REUSE APPROVED'))

    def test_geo_claim_rejected(self):
        self.invalid(lambda d:d['records'][1].update(finding='Put a map_edge between NASA events.'))

    def test_extra_record_field(self):
        self.invalid(lambda d:d['records'][0].update(endorsement='NASA-approved'))

    def test_casefile_source_mismatch(self):
        self.invalid_case(lambda s:s.select_one('#source-concordance [data-concordance-record="02"] a[href^="https://www.nasa.gov/image-detail/"]').__setitem__('href','https://www.nasa.gov/image-detail/amf-s67-21294/'))

    def test_casefile_rights_removed(self):
        self.invalid_case(lambda s:s.select_one('#fv-ex2-media-rights [data-media-review="05"]').__delitem__('data-media-hold'))

    def test_casefile_unreviewed_geo_pin(self):
        self.invalid_case(lambda s:s.select_one('#atlas').__setitem__('data-lat','29.5'))

    def test_casefile_identity_hold_removed(self):
        def change(s):
            item=s.select_one('[data-crosswalk-review="hold"]');del item['data-crosswalk-review']
        self.invalid_case(change)

    def test_annex_has_no_executable_or_embedded_images(self):
        s=BeautifulSoup(render(REG),'html.parser')
        self.assertEqual(len(s.select('article')),6)
        self.assertEqual(len(s.select('details')),12)
        self.assertFalse(s.select('script,img,iframe,form'))
        self.assertEqual(len(s.select('a[href^="https://www.nasa.gov/image-detail/"]')),6)
        self.assertEqual(len(s.select('a[target="_blank"]:not([rel~="noopener"])')),0)

    def test_escape_in_untrusted_editorial_copy(self):
        safe=copy.deepcopy(REG);safe['records'][0]['finding']='<img src=x onerror=alert(1)>'
        html=render(safe)
        self.assertIn('&lt;img',html)
        self.assertNotIn('<img',html)

if __name__=='__main__':unittest.main()
