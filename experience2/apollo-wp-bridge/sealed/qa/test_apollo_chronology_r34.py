#!/usr/bin/env python3
"""R34 source integrity tests; no WordPress or external media access."""
import copy
import json
from pathlib import Path
import unittest
from bs4 import BeautifulSoup
from apollo_chronology_r34 import build, verify, PERIOD_COUNTS

HERE=Path(__file__).resolve().parent
REG=json.loads((HERE/'nasa_catalog_primary_r33.json').read_text())
CSS=(HERE/'apollo_chronology_r34.css').read_text()
JS=(HERE/'apollo_chronology_r34.js').read_text()

class ChronologyTests(unittest.TestCase):
    def setUp(self): self.html=build(REG,CSS,JS)
    def invalid(self, edit):
        bad=copy.deepcopy(REG); edit(bad)
        with self.assertRaises(ValueError):build(bad,CSS,JS)
    def invalid_html(self, edit):
        soup=BeautifulSoup(self.html,'html.parser');edit(soup)
        with self.assertRaises(ValueError): verify(str(soup),REG)
    def test_valid_source_contract(self):
        verify(self.html,REG)
        s=BeautifulSoup(self.html,'html.parser')
        self.assertEqual(len(s.select('section.records article')),6)
        self.assertEqual(len(s.select('details')),12)
        self.assertEqual({year:len(s.select(f'[data-source-period="{year}"]')) for year in PERIOD_COUNTS},PERIOD_COUNTS)
    def test_no_javascript_controls_hidden(self):
        s=BeautifulSoup(self.html,'html.parser')
        self.assertIn('hidden',s.select_one('[data-r34-controls]').attrs)
        self.assertEqual(len(s.select('section.records > article[hidden]')),0)
    def test_month_only_source_not_converted_into_day(self):
        s=BeautifulSoup(self.html,'html.parser')
        first=s.select_one('#catalog-01')
        self.assertEqual((first['data-photo-date'],first['data-date-precision']),('1967-01','month'))
        self.assertIn('day and its proposed',s.select_one('.r34-chronology').get_text(' ',strip=True))
    def test_invalid_photo_date(self):self.invalid(lambda x:x['records'][0].update(date='1967-01-27'))
    def test_remove_alias_hold(self):self.invalid(lambda x:x['records'][0].update(identity_status='REVIEWED'))
    def test_changed_2017_record(self):self.invalid(lambda x:x['records'][3].update(date='1967-01-24'))
    def test_unauthorized_map_pin(self):self.invalid_html(lambda s:s.select_one('#catalog-05').__setitem__('data-lat','29.5'))
    def test_external_image_rejected(self):self.invalid_html(lambda s:s.select_one('article').append(s.new_tag('img',src='https://nasa.gov/a.jpg')))
    def test_source_mismatch_rejected(self):self.invalid_html(lambda s:s.select_one('#catalog-02 a').__setitem__('href','https://www.nasa.gov/image-detail/amf-s67-21294/'))
    def test_rights_hold_must_survive(self):self.invalid_html(lambda s:s.select_one('#catalog-05 p.small:last-of-type').clear())
    def test_controls_must_fail_open_without_js(self):self.invalid_html(lambda s:s.select_one('[data-r34-controls]').attrs.pop('hidden'))
    def test_duplicate_id_rejected(self):self.invalid_html(lambda s:s.select_one('#catalog-05').__setitem__('id','catalog-04'))
    def test_extra_script_rejected(self):self.invalid_html(lambda s:s.body.append(s.new_tag('script',src='https://example.org/a.js')))
    def test_css_breakout_rejected(self):
        with self.assertRaises(ValueError):build(REG,CSS+'\n</style><img src=x>',JS)
    def test_js_breakout_rejected(self):
        with self.assertRaises(ValueError):build(REG,CSS,JS+'\n</script><img src=x>')
    def test_untrusted_editorial_strings_escape(self):
        altered=copy.deepcopy(REG);altered['records'][2]['limitation']='<img src=x onerror=alert(1)>'
        page=build(altered,CSS,JS)
        self.assertNotIn('onerror=',str(BeautifulSoup(page,'html.parser').select('img')))
        self.assertEqual(len(BeautifulSoup(page,'html.parser').select('img')),0)

if __name__=='__main__':unittest.main()
