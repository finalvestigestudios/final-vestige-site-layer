"""R88 actual-source reading-room adversarial contracts."""
import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1]/'tools/build_reading_room_r88.py'
spec=importlib.util.spec_from_file_location('r88_contracts',HERE)
r88=importlib.util.module_from_spec(spec);spec.loader.exec_module(r88)

class ReaderContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rail,cls.report,cls.groups,cls.uncertain=r88.verified_records()
        cls.page=r88.page(cls.report['records'])
    def test_real_component_concordance(self):
        self.assertEqual(len(self.report['desk']),6)
        self.assertEqual(len(self.report['atlas']),6)
        self.assertEqual(len(self.report['records']),6)
    def test_six_official_urls_bound_to_cards(self):
        for item in self.report['records']:
            block=self.page.split(f'id="r88-{item["id"]}"',1)[1].split('</article>',1)[0]
            self.assertIn('href="'+item['url']+'"',block)
            self.assertIn('data-catalog="'+r88.e(item['catalog'])+'"',block)
    def test_six_drawers_keyboard_native(self):
        self.assertEqual(self.page.count('<details>'),6)
        self.assertEqual(self.page.count('<summary>'),6)
        self.assertEqual(self.page.count('class="compare-choice" hidden'),6)
    def test_crew_uncertainty(self):
        self.assertIn('S67-19766 crew-portrait identity remains provisional',self.page)
        self.assertIn('Month only — cannot place',self.page)
        self.assertEqual([r['id'] for r in self.uncertain],['01'])
    def test_no_unsafe_geography_or_embedded_media(self):
        self.assertIsNone(re.search(r'<(?:img|iframe|picture|video)\b|data-(?:lat|lon|geo-edge)',self.page,re.I))
    def test_rights_pending(self):
        self.assertEqual(self.page.count('INDIVIDUAL REVIEW REQUIRED'),6)
        self.assertIn('0/6 individual photo-use assessments',self.page)
    def test_nojs_content_complete(self):
        self.assertEqual(self.page.count('<article class="record"'),6)
        self.assertIn('reading_room_r88.js" defer',self.page)
        self.assertIn('id="r88-compare" hidden',self.page)
    def test_source_script_is_local_only(self):
        script=r88.JS.read_text('utf8')
        for token in ('fetch(', 'XMLHttpRequest','eval(','.innerHTML','localStorage','sessionStorage'):
            self.assertNotIn(token,script)
    def test_build_has_all_outputs(self):
        with tempfile.TemporaryDirectory() as work:
            dest=Path(work);receipt=r88.build(dest)
            self.assertEqual(receipt['photo_rights_cleared'],0)
            self.assertEqual(receipt['unplaced_ids'],['01'])
            self.assertEqual(len(receipt['chronology_milestones']),4)
            for fname in ('R88_READING_ROOM.html','reading_room_r88.css','reading_room_r88.js',
                          'R87_PHOTOGRAPH_DATE_RAIL.html','chronology_r87.css','R88_READING_ROOM_RECEIPT.json'):
                self.assertTrue((dest/fname).is_file(),fname)
    def test_fail_closed_tampered_url(self):
        with tempfile.TemporaryDirectory() as work:
            broken=dict(self.report);broken['records']=[dict(r) for r in self.report['records']]
            broken['records'][0]['url']='https://nasa.gov.evil.test/image-detail/not-real/'
            with patch.object(r88,'verified_records',return_value=(self.rail,broken,self.groups,self.uncertain)):
                with self.assertRaises(AssertionError):r88.build(Path(work)/'stage')
            self.assertFalse((Path(work)/'stage').exists())
    def test_fail_closed_missing_record(self):
        with tempfile.TemporaryDirectory() as work:
            broken=dict(self.report);broken['records']=broken['records'][:5]
            with patch.object(r88,'verified_records',return_value=(self.rail,broken,self.groups,self.uncertain)):
                with self.assertRaises(AssertionError):r88.build(Path(work)/'stage')
    def test_deterministic_review_archive(self):
        with tempfile.TemporaryDirectory() as work:
            dest=Path(work)/'render';r88.build(dest)
            a=Path(work)/'a.zip';b=Path(work)/'b.zip'
            self.assertEqual(r88.package(dest,a),r88.package(dest,b))
            receipt=json.loads((dest/'R88_READING_ROOM_RECEIPT.json').read_text())
            self.assertFalse(receipt['publication_approved'])
            self.assertFalse(receipt['hosted_wordpress_verified'])

if __name__=='__main__':unittest.main()
