"""R15: year context lens and derived authenticated NASA custody index.

Tests enforce exactly the source meaning and rights boundaries of the original
six catalog witnesses. CSS-only browser interaction lives in browser_exact.py.
"""
import copy
from hashlib import sha256
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from source_concordance import (build_concordance, build_context_index, ConcordanceHold,
                                CASEFILE, GENERATED)


class TemporalLens(unittest.TestCase):
    def test_pinned_era_counts_and_native_no_js_controls(self):
        html, css, receipt = build_concordance()
        self.assertEqual(html.count('type="radio"'), 4)
        self.assertIn('name="fv-ex2-source-era"', html)
        self.assertIn('id="fv-ex2-lens-all"', html)
        self.assertIn('id="fv-ex2-lens-1966"', html)
        self.assertIn('id="fv-ex2-lens-1967"', html)
        self.assertIn('id="fv-ex2-lens-2017"', html)
        self.assertIn('all" checked', html)
        self.assertEqual({y:html.count(' data-concordance-era="'+y+'"')
                          for y in ('1966','1967','2017')},
                         {'1966':1,'1967':3,'2017':2})
        self.assertIn('@supports selector(:has(*))', css)
        self.assertIn('.fv-ex2-concordance__filters{display:none;', css)
        self.assertIn('.fv-ex2-concordance__filters{display:flex}', css)
        self.assertEqual(receipt['filter_counts'],{'all':6,'1966':1,'1967':3,'2017':2})
        self.assertTrue(receipt['css_only_era_filter'])
        self.assertEqual(html.count('{{FV_EX2_CONTEXT_EXPORT}}'),1)

    def test_canonical_context_export_parity(self):
        raw = build_context_index()
        idx = json.loads(raw)
        original = json.loads((CASEFILE/'records.json').read_text())['records']
        self.assertEqual(idx['record_count'],6)
        self.assertEqual(idx['media_rights'],'HOLD_PER_ITEM_REVIEW')
        self.assertTrue(idx['not_a_rights_clearance'])
        self.assertTrue(idx['not_an_incident_reconstruction'])
        self.assertEqual(idx['geographic_coordinates_assigned'],0)
        for row, item in zip(original,idx['records']):
            self.assertEqual(item['claim_id'],row['id'])
            self.assertEqual(item['catalog_id'],row['source_id'])
            self.assertEqual(item['catalog_date'],row['source_date'])
            self.assertEqual(item['source_url'],row['image_url'])
            self.assertEqual(item['cannot_establish'],row['limit'])
            self.assertEqual(item['media_status'],row['rights'])
            self.assertEqual(item['geometry'],'not_assigned')
            self.assertEqual(item['chronology_anchor'],'#stage-'+row['id'])
            self.assertEqual(item['source_drawer_anchor'],'#source-'+row['id'])
        self.assertEqual(sha256(raw.encode()).hexdigest(),build_concordance()[2]['context_index_sha256'])

    def test_two_independent_runs_same_output_bytes(self):
        self.assertEqual(build_context_index().encode(),build_context_index().encode())
        self.assertEqual(build_concordance(),build_concordance())

    def mutate(self, change):
        with tempfile.TemporaryDirectory() as d:
            cp=Path(d)/'source'; gp=Path(d)/'render'
            cp.mkdir(); gp.mkdir()
            data=json.loads((CASEFILE/'records.json').read_text())
            change(data)
            (cp/'records.json').write_text(json.dumps(data))
            shutil.copyfile(GENERATED/'fragment.html',gp/'fragment.html')
            with self.assertRaises(ConcordanceHold):build_context_index(cp,gp)

    def test_1966_era_forgery_denied(self):
        self.mutate(lambda data:data['records'][2].update(source_date='Jan 1967'))

    def test_2017_tribute_reclassified_denied(self):
        self.mutate(lambda data:data['records'][5].update(source_date='Jan 1967'))

    def test_rogue_media_rights_denied(self):
        self.mutate(lambda data:data['records'][0].update(rights='permission_granted'))

    def test_spoofed_nasa_domain_denied(self):
        self.mutate(lambda data:data['records'][0].update(image_url='https://www.nasa.gov.evil.test/image-detail/a/'))

    def test_duplicate_source_record_denied(self):
        self.mutate(lambda data:data['records'][1].update(id='01'))

    def test_empty_limit_denied(self):
        self.mutate(lambda data:data['records'][4].update(limit=''))

    def test_missing_source_drawer_denied(self):
        with tempfile.TemporaryDirectory() as d:
            cp=Path(d)/'source'; gp=Path(d)/'render'
            cp.mkdir(); gp.mkdir()
            shutil.copyfile(CASEFILE/'records.json',cp/'records.json')
            frag=(GENERATED/'fragment.html').read_text().replace('id="source-06"','id="missing-source-06"')
            (gp/'fragment.html').write_text(frag)
            with self.assertRaises(ConcordanceHold): build_context_index(cp,gp)


if __name__=='__main__': unittest.main()
