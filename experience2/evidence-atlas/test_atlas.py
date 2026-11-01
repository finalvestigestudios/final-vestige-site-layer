"""R39 real-crosswalk source custody and deterministic Atlas build tests."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from html.parser import HTMLParser
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('build_atlas', HERE / 'build_atlas.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags=[]
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag,dict(attrs)))

class AtlasIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=tempfile.TemporaryDirectory()
        cls.out=Path(cls.d.name)
        cls.receipt=builder.build(cls.out)
        cls.page=(cls.out/'apollo-evidence-atlas.html').read_text(encoding='utf8')
        cls.tree=Tags();cls.tree.feed(cls.page)
        cls.custody=builder.validate_custody()
    @classmethod
    def tearDownClass(cls):cls.d.cleanup()
    def test_exact_custody_blob(self):
        self.assertEqual(builder.git_blob(builder.CROSSWALK.read_bytes()),builder.EXPECTED_BLOB)
    def test_original_six_nasa_destinations(self):
        urls={tag['href'] for name,tag in self.tree.tags if name=='a' and 'href' in tag}
        self.assertTrue(all(url in urls for url in builder.EXPECTED_URLS.values()))
        self.assertEqual(sum('nasa.gov/image-detail' in x for x in urls),6)
    def test_six_cards_have_review_pending(self):
        cards=[a for t,a in self.tree.tags if t=='article' and 'data-fva-record' in a]
        self.assertEqual([a['data-fva-id'] for a in cards],list(builder.IDS))
        self.assertEqual([a['data-fva-year'] for a in cards],['1967','1967','1966','2017','1967','2017'])
        self.assertEqual(self.page.count('Individual review required. No photograph is reproduced here.'),6)
        self.assertEqual(self.receipt['image_rights'],'6 INDIVIDUAL_REVIEW_REQUIRED')
    def test_no_media_geo_or_speculative_relationships(self):
        self.assertFalse(any(t in {'img','picture','video','iframe','canvas','svg','audio'} for t,_ in self.tree.tags))
        self.assertFalse(any('data-lat' in a or 'data-lng' in a or 'data-fva-geo' in a for _,a in self.tree.tags))
        self.assertEqual(self.receipt['geographic_pins'],0)
        self.assertEqual(self.receipt['relationship_edges'],0)
        self.assertIn('Why no map?',self.page)
    def test_accessible_labels_and_targets(self):
        ids=[a['id'] for _,a in self.tree.tags if 'id' in a]
        self.assertEqual(len(ids),len(set(ids)))
        for _,a in self.tree.tags:
            for attr in ('aria-labelledby','aria-controls'):
                if attr in a:
                    self.assertTrue(all(x in ids for x in a[attr].split()),a[attr])
        self.assertIn('aria-live="polite"',self.page)
        self.assertIn('role="group"',self.page)
    def test_nojs_fails_open(self):
        self.assertIn('data-fva-controls hidden',self.page)
        self.assertNotIn('data-fva-record hidden',self.page)
        self.assertIn('<details data-fva-drawer>',self.page)
    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as t:
            b=builder.build(Path(t))
            self.assertEqual(self.receipt,b)
            for name in ('apollo-evidence-atlas.html','atlas-build-manifest.json'):
                self.assertEqual((self.out/name).read_bytes(),(Path(t)/name).read_bytes())
    def test_changed_crosswalk_bytes_fail_closed(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'crosswalk.json';shutil.copyfile(builder.CROSSWALK,p)
            p.write_bytes(p.read_bytes().replace(b'INDIVIDUAL_REVIEW_REQUIRED',b'CLEARED',1))
            with self.assertRaisesRegex(ValueError,'changed without independent review'):
                builder.validate_custody(p)
    def test_unreviewed_filename_is_not_structured_catalog_claim(self):
        self.assertIn('structured catalog metadata not separately confirmed',self.page)
    def test_retro_not_misrepresented(self):
        self.assertEqual(self.page.count('Retrospective exhibit, not contemporaneous evidence'),2)
    def test_default_no_external_scripts(self):
        self.assertNotIn('src="http',self.page)
        self.assertNotIn('href="http',self.page.split('<style>')[0])
        self.assertNotIn('fetch(', (HERE/'atlas.js').read_text())

if __name__=='__main__': unittest.main()
