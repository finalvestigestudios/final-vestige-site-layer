"""NASA link, era, source-date and rights regression tests for Apollo R13."""
import copy
import json
from pathlib import Path
import unittest
from nasa_editorial_gate import audit, audit_files, EditorialHold, CASEFILE, GENERATED

class NasaEditorialGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records=json.loads((CASEFILE/'records.json').read_text(encoding='utf-8'))
        cls.export=json.loads((GENERATED/'evidence-export.json').read_text(encoding='utf-8'))
        cls.html=(GENERATED/'fragment.html').read_text(encoding='utf-8')

    def mutate(self, f):
        a=copy.deepcopy(self.records);b=copy.deepcopy(self.export)
        f(a,b)
        with self.assertRaises(EditorialHold):audit(a,b,self.html)

    def test_01_verified_source_fixture(self):
        receipt=audit_files()
        self.assertEqual(receipt['nasa_image_pages_checked'],6)
        self.assertEqual(receipt['source_rights'],'HOLD_PER_ITEM_REVIEW')
        self.assertEqual(receipt['images_reproduced'],0)
        self.assertEqual(len(receipt['witness_sha256']),64)

    def test_02_reject_catalog_url_relabel_or_host_spoof(self):
        for field,new in [('image_url','https://www.nasa.gov.evil.invalid/record'),
                          ('source_id','NASA OFFICIAL APPROVED'),
                          ('source_date','27 Jan 1967'),
                          ('image_credit','NASA OFFICIALLY APPROVED')]:
            with self.subTest(field=field):
                self.mutate(lambda a,b:a['records'][1].__setitem__(field,new))

    def test_03_no_image_rights_promotion(self):
        self.mutate(lambda a,b:a['records'][0].__setitem__('rights','cleared_commercial_promotions'))
        self.mutate(lambda a,b:b.update(not_a_rights_clearance=False))
        self.mutate(lambda a,b:b.update(no_reproduced_images=False))
        self.mutate(lambda a,b:a.update(rights_policy='https://other.invalid/policy'))

    def test_04_catch_2017_tribute_being_turned_into_1967_footage(self):
        for index in (3,5):
            with self.subTest(index=index):
                self.mutate(lambda a,b:a['records'][index].update(
                    finding='This shows the 1967 hatch during the fatal fire.',
                    image_description='The spacecraft during the fire.',
                    limit='The image proves the fire sequence.'))

    def test_05_retains_training_and_damage_distinctions(self):
        self.mutate(lambda a,b:a['records'][2].__setitem__(
            'limit','This image depicts the fatal fire in the command module.'))
        self.mutate(lambda a,b:a['records'][4].__setitem__(
            'image_description','An electrical arc at the precise point of ignition.'))

    def test_06_export_must_match_editorial_source(self):
        for field,value in [('image_date','28 Jan 1967'),
                            ('image_record_url','https://www.nasa.gov/fake'),
                            ('geometry','Cape Canaveral, Florida 28.6,-80.6'),
                            ('media_status','embedded')]:
            with self.subTest(field=field):
                self.mutate(lambda a,b:b['records'][1].__setitem__(field,value))

    def test_07_no_silent_media_embed_or_lost_drawer(self):
        for html in (self.html + '<img src="https://www.nasa.gov/image.png">',
                     self.html.replace('id="source-03"','id="missing-03"'),
                     self.html.replace('https://www.nasa.gov/image-detail/amf-s67-21294/','',1)):
            with self.subTest(length=len(html)),self.assertRaises(EditorialHold):
                audit(self.records,self.export,html)

    def test_08_snapshot_date_is_not_a_live_license_approval(self):
        self.mutate(lambda a,b:a.update(verified_at='2026-11-01'))
        report=audit(self.records,self.export,self.html)
        self.assertIn('No live fetch',report['limitations'])
        self.assertNotEqual(report['source_rights'],'APPROVED')

if __name__=='__main__':unittest.main()
