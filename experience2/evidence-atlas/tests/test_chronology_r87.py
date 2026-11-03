"""R87 adversarial source-date custody tests; no network or WordPress writes."""
import importlib.util
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

SOURCE=Path(__file__).resolve().parents[1]/'tools/build_chronology_r87.py'
spec=importlib.util.spec_from_file_location('apollo_chronology_r87',SOURCE)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)

def real():
    r86=m.HERE/'build_concordance_r86.py'
    spec=importlib.util.spec_from_file_location('r86_chronology_test',r86)
    s=importlib.util.module_from_spec(spec);sys.modules[spec.name]=s;spec.loader.exec_module(s)
    return s.verify(),json.loads(m.CROSSWALK.read_text('utf8'))

class ChronologySourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.report,cls.custody=real()
    def modified(self,func):
        report,crosswalk=deepcopy(self.report),deepcopy(self.custody)
        func(report,crosswalk)
        with self.assertRaisesRegex(ValueError,'R87_CUSTODY_HOLD'):
            m.verified_groups(report,crosswalk)
    def test_real_source_grouping(self):
        groups,unplaced=m.verified_groups(self.report,self.custody)
        self.assertEqual([a for a,_ in groups],['1966-10-18','1967-01-03','1967-01-28','2017-01-24'])
        self.assertEqual([r['id'] for r in groups[-1][1]],['04','06'])
        self.assertEqual([r['id'] for r in unplaced],['01'])
    def test_source_identity_swap_rejected(self):
        self.modified(lambda a,b:a['records'][1].update(url=a['records'][2]['url']))
    def test_catalog_tamper_rejected(self):
        self.modified(lambda a,b:a['records'][1].update(catalog='S67-XXX'))
    def test_date_label_tamper_rejected(self):
        self.modified(lambda a,b:a['records'][1].update(component_date_label='January 27, 1967'))
    def test_bad_month_to_day_promotion_rejected(self):
        self.modified(lambda a,b:(b['records'][0].update(date='1967-01-27'),a['records'][0].update(precision='DAY')))
    def test_fake_crew_day_rejected(self):
        self.modified(lambda a,b:(b['records'][0].update(date='1967-01-27'),a['records'][0].update(precision='DAY')))
    def test_missing_uncertainty_rejected(self):
        self.modified(lambda a,b:a['records'][0].update(date='January 1967'))
    def test_forged_pia_rejected(self):
        self.modified(lambda a,b:a['records'][0].update(identity='PIA_ON_OFFICIAL_PAGE'))
    def test_crosswalk_duplicate_rejected(self):
        self.modified(lambda a,b:b['records'][4].update(id='02'))
    def test_cleared_rights_rejected(self):
        self.modified(lambda a,b:b['records'][2].update(media_rights='APPROVED'))
    def test_widened_source_host_rejected(self):
        self.modified(lambda a,b:(a['records'][2].update(url='https://www.nasa.gov.evil.test/image-detail/anything/'),b['records'][2].update(photo_url='https://www.nasa.gov.evil.test/image-detail/anything/')))
    def test_missing_record_rejected(self):
        self.modified(lambda a,b:a['records'].pop())
    def test_duplicate_group_date_rejected(self):
        def mutate(a,b):
            a['records'][4].update(date='January 3, 1967',component_date_label='January 3, 1967')
            b['records'][4].update(date='1967-01-03',date_label='January 3, 1967')
        self.modified(mutate)
    def test_generated_html_has_six_native_drawers(self):
        groups,u=m.verified_groups(self.report,self.custody)
        text=m.render(groups,u)
        self.assertEqual(text.count('<details>'),6)
        self.assertEqual(text.count('<time datetime='),4)
        self.assertIn('S67-19766',text)
        self.assertIn('exact day unconfirmed',text)
        self.assertNotIn('<img',text)
        self.assertNotIn('data-lat',text)
        self.assertNotIn('data-geo-edge',text)
    def test_determinism(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/'built'
            a=m.build(folder)
            b=m.build(folder)
            self.assertEqual(a,b)
            self.assertEqual(a['media_reuse_cleared'],0)
            self.assertFalse(a['approved_for_publication'])
            self.assertEqual(a['html_sha256'],m.sha256((folder/'R87_PHOTOGRAPH_DATE_RAIL.html').read_bytes()))
            p1,p2=Path(tmp)/'a.zip',Path(tmp)/'b.zip'
            self.assertEqual(m.package(folder,p1),m.package(folder,p2))
            self.assertEqual(p1.read_bytes(),p2.read_bytes())

if __name__=='__main__':unittest.main()
