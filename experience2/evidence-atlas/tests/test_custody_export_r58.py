#!/usr/bin/env python3
"""R58 exact-custody text export: preserve on-page disclosures and reject drift."""
import pathlib,unittest,sys
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import build_atlas,build_wordpress_stage

class CustodyParser(HTMLParser):
    def __init__(self):super().__init__();self.drawers=0;self.dt=[]
    def handle_starttag(self,t,a):
        d=dict(a)
        if t=='details' and 'data-fva-drawer' in d:self.drawers+=1

class CustodyExportR58(unittest.TestCase):
    def test_six_rights_not_cleared_and_static_custody(self):
        page=build_atlas.make_html(build_atlas.validate_custody(),'','')
        p=CustodyParser();p.feed(page)
        self.assertEqual(p.drawers,6)
        self.assertEqual(page.count('Individual review required. No photograph is reproduced here.'),6)
        self.assertIn('not a human link check',page)
        self.assertNotIn('<img',page)
    def test_export_uses_strict_native_drawers_and_no_remote_access(self):
        script=(ROOT/'atlas.js').read_text()
        for token in ('const custodyFields=[','const sourceCustody=(card,id,catalog)=>{',
                      "fields[2]!== (id==='01'",'Custody claims changed',
                      "children.length!==custodyFields.length*2",'lines.push(...sourceCustody(cards[i],id,catalog))',
                      'NOT rights clearance','human link or image-rights check'):
            self.assertIn(token,script)
        for token in ('fetch(', 'XMLHttpRequest(', 'sendBeacon(', 'navigator.geolocation', 'localStorage', 'sessionStorage'):
            self.assertNotIn(token,script)
    def test_source_lock_and_version(self):
        php=(ROOT/'final-vestige-ex2-evidence-atlas.php').read_text()
        suite=(ROOT/'integration/fv-ex2-apollo-suite.php').read_text()
        self.assertIn('0.0.58-staging',php)
        self.assertIn('0.0.65-staging',suite)
        self.assertIn('25b23884c72cb9369ce2b5ee5d70b83ded368e29',suite)
        self.assertEqual(build_atlas.validate_rights_audit(build_atlas.validate_custody())['status'],'STAGING_HOLD')
if __name__=='__main__':unittest.main()
