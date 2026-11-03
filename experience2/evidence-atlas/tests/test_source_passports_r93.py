#!/usr/bin/env python3
"""Adversarial R93 Apollo passport tests; execute from exact PR head only."""
from __future__ import annotations
import hashlib, html, importlib.util, json, pathlib, re, shutil, subprocess, sys, tempfile, unittest
ROOT=pathlib.Path(__file__).resolve().parents[3]
TOOLS=ROOT/'experience2/evidence-atlas/tools'
spec=importlib.util.spec_from_file_location('apollo_passports_r93',TOOLS/'build_source_passports_r93.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)

class PassportChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keep=tempfile.TemporaryDirectory(prefix='apollo-r93-')
        cls.src=pathlib.Path(cls.keep.name)/'r92'
        subprocess.run([sys.executable,str(TOOLS/'build_reciprocal_routes_r92.py'),str(cls.src)],
          check=True,capture_output=True,text=True)
    @classmethod
    def tearDownClass(cls):cls.keep.cleanup()

    def mutated(self,filename:str,old:str,new:str,update_receipt:bool=False):
        temp=tempfile.TemporaryDirectory();src=pathlib.Path(temp.name)/'src'
        shutil.copytree(self.src,src)
        p=src/filename;raw=p.read_text()
        self.assertIn(old,raw)
        p.write_text(raw.replace(old,new,1))
        if update_receipt:
            recfile=src/'R92_RECIPROCAL_ROUTES_RECEIPT.json'
            rec=json.loads(recfile.read_text())
            rec['files'][filename]=hashlib.sha256(p.read_bytes()).hexdigest()
            recfile.write_text(json.dumps(rec,sort_keys=True,indent=2)+'\n')
        return temp,src

    def test_six_source_records_exact(self):
        r=m.verified_records(self.src)
        self.assertEqual([x['id'] for x in r],['01','02','03','04','05','06'])
        self.assertTrue(all(x['rights']=='INDIVIDUAL REVIEW REQUIRED' for x in r))
        self.assertTrue(r[0]['provisional'])
        self.assertFalse(any(x['provisional'] for x in r[1:]))

    def test_source_links_and_limits_are_specific(self):
        r=m.verified_records(self.src)
        self.assertEqual(len({x['url'] for x in r}),6)
        self.assertTrue(all(x['url'].startswith('https://www.nasa.gov/image-detail/') for x in r))
        self.assertTrue(all(x['can'] and x['cannot'] for x in r))

    def test_evidence_dates_are_not_fire_chronology(self):
        r=m.verified_records(self.src)
        self.assertEqual(r[0]['date'],'January 1967 — day unconfirmed')
        self.assertEqual(r[3]['date'],r[5]['date'])

    def test_no_external_assets_or_invented_geo(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=pathlib.Path(tmp)/'out';receipt=m.build(self.src,out)
            raw=(out/'R93_SOURCE_PASSPORTS.html').read_text()
            self.assertFalse(re.search(r'<(img|svg|canvas|iframe|video)\b',raw))
            self.assertEqual(receipt['new_geo_pins'],0)
            self.assertEqual(receipt['new_historical_edges'],0)
            self.assertNotIn('data-lat=',raw)

    def test_exported_citations_preserve_six_urls_and_holds(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=pathlib.Path(tmp)/'out';m.build(self.src,out)
            text=(out/'R93_NASA_REFERENCES.txt').read_text()
            records=json.loads((out/'R93_SOURCE_PASSPORTS.json').read_text())['records']
            self.assertEqual(len(records),6)
            for x in records:
                self.assertIn(x['url'],text)
                self.assertIn('INDIVIDUAL REVIEW REQUIRED',m.citation(x))
                self.assertIn(x['cannot'],html.unescape((out/'R93_SOURCE_PASSPORTS.html').read_text()))

    def test_deterministic_archives(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=pathlib.Path(tmp)
            m.build(self.src,a/'one',a/'one.zip')
            m.build(self.src,a/'two',a/'two.zip')
            self.assertEqual((a/'one.zip').read_bytes(),(a/'two.zip').read_bytes())

    def test_mutated_r92_html_fails_sha_gate(self):
        temp,src=self.mutated('R88_READING_ROOM.html','January 3, 1967','January 4, 1967')
        with temp,self.assertRaisesRegex(ValueError,'R93_BASE_HASH_MISMATCH'):
            m.verified_records(src)

    def test_manipulated_r92_receipt_still_catches_date_mismatch(self):
        temp,src=self.mutated('R88_READING_ROOM.html','January 3, 1967','January 4, 1967',True)
        with temp,self.assertRaisesRegex(ValueError,'R93_CROSS_VIEW_DISAGREEMENT'):
            m.verified_records(src)

    def test_manipulated_r92_receipt_still_catches_swapped_nasa(self):
        original=m.verified_records(self.src)
        temp,src=self.mutated('R88_READING_ROOM.html','href="'+original[0]['url']+'"','href="'+original[1]['url']+'"',True)
        with temp,self.assertRaisesRegex(ValueError,'R93_NASA_LINK_CHANGED'):
            m.verified_records(src)

    def test_provisional_identity_cannot_be_certified(self):
        temp,src=self.mutated('R88_READING_ROOM.html','data-catalog="S67-19766"','data-catalog="S67-19767"',True)
        with temp,self.assertRaisesRegex(ValueError,'R93_CROSS_VIEW_DISAGREEMENT|R93_PROVISIONAL'):
            m.verified_records(src)

    def test_unauthorized_rights_cannot_pass(self):
        temp,src=self.mutated('R89_REVIEW_HUB.html','INDIVIDUAL REVIEW REQUIRED','REUSE APPROVED',True)
        with temp,self.assertRaisesRegex(ValueError,'R93_RIGHTS_GATE_CHANGED'):
            m.verified_records(src)

    def test_no_release_flag_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            src=pathlib.Path(tmp)/'src';shutil.copytree(self.src,src)
            p=src/'R92_RECIPROCAL_ROUTES_RECEIPT.json'
            r=json.loads(p.read_text());r['photographic_rights_cleared']=6
            p.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'R93_BASE_CUSTODY_UNVERIFIED'):
                m.verified_records(src)

    def test_zero_js_readability_and_native_details(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=pathlib.Path(tmp)/'out';m.build(self.src,out)
            raw=(out/'R93_SOURCE_PASSPORTS.html').read_text()
            self.assertEqual(raw.count('<article class="card"'),6)
            self.assertEqual(raw.count('<details>'),6)
            self.assertEqual(raw.count('class="print-source"'),6)
            self.assertEqual(raw.count('class="copy"'),6)
            self.assertIn('aria-live="polite"',raw)
            self.assertEqual(raw.count('data-citation='),6)

if __name__=='__main__':unittest.main()
