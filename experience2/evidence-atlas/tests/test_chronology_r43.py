"""R43 strict custody chronology contract: no inferred event sequence or map points."""
from pathlib import Path
import hashlib
from html.parser import HTMLParser
import tempfile
import sys
import unittest

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import build_wordpress_stage as stage

class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

class R43Chronology(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.manifest=stage.build(Path(cls.tmp.name))
        cls.html=(Path(cls.tmp.name)/'fv-ex2-evidence-atlas/templates/atlas-fragment.html').read_text()
        obj=Structure(); obj.feed(cls.html)
        cls.tags=obj.tags

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_chronology_has_three_explicit_source_eras(self):
        eras=[a['data-fva-era'] for t,a in self.tags if 'data-fva-era' in a]
        self.assertEqual(eras,['1966','1967','2017'])
        self.assertIn('not a reconstruction of the Apollo 1 fire',self.html)
        self.assertIn('One photographic day is unresolved.',self.html)

    def test_link_identity_one_per_custody_source(self):
        timejumps=[a for t,a in self.tags if 'data-fva-timejump' in a]
        self.assertEqual(len(timejumps),6)
        self.assertEqual({a['data-fva-time-id'] for a in timejumps},set(stage.build_atlas.IDS))
        self.assertEqual({a['href'] for a in timejumps},
                         {'#fva-record-'+i for i in stage.build_atlas.IDS})
        indexjumps=[a for t,a in self.tags if 'data-fva-jump' in a]
        self.assertEqual(len(indexjumps),6)

    def test_every_time_date_is_unchanged_crosswalk_data(self):
        custody=stage.build_atlas.validate_custody()
        values=[a['datetime'] for t,a in self.tags if t=='time']
        self.assertEqual(len(values),6)
        self.assertEqual(sorted(values),sorted(r['date'] for r in custody['records']))
        self.assertIn('<time datetime="1967-01">January 1967; exact day not asserted</time>',self.html)

    def test_1967_source_records_are_not_sorted_into_fake_day_sequence(self):
        # Three 1967 sources: S67-19766 has month precision, not a fictitious day.
        self.assertIn('January records are not arranged as an accident sequence.',self.html)
        self.assertNotIn('datetime="1967-01-01"',self.html)
        self.assertNotIn('datetime="1967-01-27"',self.html)

    def test_no_unreviewed_media_or_geographic_claims(self):
        for token in ('<img','<picture','<canvas','data-lat','data-lng','geo-pin','coordinate="'):
            self.assertNotIn(token,self.html)
        self.assertEqual(self.html.count('Individual review required. No photograph is reproduced here.'),6)
        self.assertEqual(self.manifest['media_rights_unreviewed'],6)

    def test_no_broken_heading_reference(self):
        ids={attrs['id'] for _,attrs in self.tags if 'id' in attrs}
        self.assertIn('fva-chronology-title',ids)
        self.assertTrue(any(a.get('aria-labelledby')=='fva-chronology-title' for _,a in self.tags))
        for t,a in self.tags:
            for ref_name in ('aria-controls','aria-labelledby','for'):
                if ref_name in a:
                    self.assertTrue(all(ref in ids for ref in a[ref_name].split()))

    def test_built_fragment_hash_matches_php_pin(self):
        php=(HERE/'final-vestige-ex2-evidence-atlas.php').read_text()
        h=hashlib.sha256(self.html.encode('utf-8')).hexdigest()
        self.assertIn("define('FV_EX2_ATLAS_TEMPLATE_SHA256', '"+h+"')",php)
        self.assertIn('0.0.57-staging',php)

    def test_deterministic_fragment_on_rebuild(self):
        with tempfile.TemporaryDirectory() as another:
            again=stage.build(Path(another))
            self.assertEqual(again,self.manifest)
            self.assertEqual((Path(another)/'fv-ex2-evidence-atlas/templates/atlas-fragment.html').read_text(),self.html)

if __name__=='__main__':unittest.main()
