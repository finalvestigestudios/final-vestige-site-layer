"""R86 offline failure-injection tests for true component-to-NASA parity."""
import importlib.util, json, sys, tempfile, unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/build_concordance_r86.py'
s=importlib.util.spec_from_file_location('r86_concordance',P)
m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m)
class ConcordanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.good=m.verify()
        cls.desk=m.DESK.read_text('utf-8')
        atlas=m.load(m.ATLAS,'r86_atlas_test')
        cls.atlas=atlas.make_html(atlas.validate_custody(),
            (m.ATLAS.parent/'atlas.css').read_text(),
            (m.ATLAS.parent/'atlas.js').read_text())
    def assert_holds(self,doc,kind):
        with self.assertRaisesRegex(ValueError,'R86_CUSTODY_HOLD'):
            m.validate_component(doc,self.good['records'],kind)
    def test_six_exact_parities(self):
        self.assertEqual(len(self.good['desk']),6)
        self.assertEqual(len(self.good['atlas']),6)
        self.assertEqual(self.good['records'][0]['precision'],'MONTH_ONLY')
    def test_wrong_desk_nasa_url_fails(self):
        self.assert_holds(self.desk.replace('/amf-s67-15717/','/amf-s67-21294/'),'desk')
    def test_wrong_atlas_nasa_url_fails(self):
        self.assert_holds(self.atlas.replace('href="https://www.nasa.gov/image-detail/amf-s67-15717/"',
          'href="https://www.nasa.gov/image-detail/fake-source/"'),'atlas')
    def test_desk_drawer_removed_fails(self):
        self.assert_holds(self.desk.replace('data-fvx-photo-record="01"','data-fvx-photo-record="00"'),'desk')
    def test_fake_catalog_fails(self):
        self.assert_holds(self.desk.replace('NASA S67-15717','NASA UNREVIEWED-99'),'desk')
    def test_fabricated_photo_binary_fails(self):
        self.assert_holds(self.desk.replace('data-fvx-photo-record="01"','<img src="data:,x"> data-fvx-photo-record="01"'),'desk')
    def test_removed_source_fails(self):
        self.assert_holds(self.atlas.replace('data-fva-id="06"','data-fva-id="99"'),'atlas')
    def test_multiple_source_links_fails(self):
        self.assert_holds(self.desk.replace('NASA archive record ↗</a>',
          'NASA archive record ↗</a><a href="https://www.nasa.gov/image-detail/other/">unapproved</a>',1),'desk')
    def test_render_no_js_no_pictures_no_geo_and_six_cards(self):
        page=m.render(self.good)
        self.assertEqual(page.count('<article class="evidence"'),6)
        self.assertEqual(page.count('<summary>'),6)
        self.assertEqual(page.count('class="primary"'),6)
        self.assertNotIn('<script',page)
        self.assertNotIn('<img',page)
        self.assertNotIn('data-lat',page)
        self.assertIn('0 of 6 photographs cleared',page)
    def test_build_twice_byte_identical_receipts(self):
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            one,two=Path(a),Path(b)
            ra,rb=m.build(one),m.build(two)
            self.assertEqual(ra,rb)
            self.assertEqual(ra['photo_rights_cleared'],0)
            self.assertFalse(ra['approved_for_publication'])
            for name in ('R86_EVIDENCE_CONCORDANCE.html','concordance_r86.css',
                         'R86_CONCORDANCE_RECEIPT.json'):
                self.assertEqual((one/name).read_bytes(),(two/name).read_bytes())
if __name__=='__main__':unittest.main()
