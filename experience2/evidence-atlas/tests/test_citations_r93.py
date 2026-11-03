#!/usr/bin/env python3
"""R93 source-citation adversarial gates; no WP or production access."""
import csv
from copy import deepcopy
import importlib.util
import io
from pathlib import Path
import shutil
import tempfile
import unittest

BUILDER=Path(__file__).resolve().parents[1]/'tools'/'build_citations_r93.py'
SPEC=importlib.util.spec_from_file_location('citation_r93',BUILDER)
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

class CitationReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Under a source checkout, this generates the R92 source-exact stage.
        cls.tmp=tempfile.TemporaryDirectory(prefix='r93-tests-')
        cls.root=Path(cls.tmp.name)
        cls.stage=cls.root/'r92'
        import importlib.util,sys
        path=BUILDER.with_name('build_reciprocal_routes_r92.py')
        spec=importlib.util.spec_from_file_location('r92_r93_test_parent',path)
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        module.build(cls.stage)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def copy_stage(self):
        dest=self.root/('tamper-'+str(len(list(self.root.iterdir()))))
        shutil.copytree(self.stage,dest)
        return dest
    def test_valid_provenance_export(self):
        records=M.extract(self.stage)
        self.assertEqual(len(records),6)
        self.assertEqual([r['group'] for r in records].count('uncertain'),1)
        self.assertEqual([r['group'] for r in records].count('retrospective'),2)
        self.assertEqual(len(set(r['nasa_source_url'] for r in records)),6)
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/'preview';r=M.assemble(self.stage,out)
            self.assertFalse(r['deployment_allowed'])
            csv_rows=list(csv.DictReader(io.StringIO((out/'R93_APOLLO_SOURCE_REGISTER.csv').read_text())))
            self.assertEqual(len(csv_rows),6)
            self.assertEqual(csv_rows[0]['catalog_identity_status'].startswith('Provisional'),True)
            self.assertEqual((out/'R93_SOURCE_REGISTER.html').read_text().count('class="item"'),6)
            self.assertEqual((out/'R93_SOURCE_REGISTER.html').read_text().count('image-detail/'),12)
    def test_reject_parent_hash_tamper(self):
        stage=self.copy_stage();p=stage/'R88_READING_ROOM.html';p.write_text(p.read_text()+'<!-- altered -->')
        with self.assertRaisesRegex(ValueError,'HASH_MISMATCH'):M.extract(stage)
    def test_reject_falsified_source_status(self):
        stage=self.copy_stage();p=stage/'R92_RECIPROCAL_ROUTES_RECEIPT.json'
        p.write_text(p.read_text().replace('"photographic_rights_cleared": 0','"photographic_rights_cleared": 6'))
        with self.assertRaisesRegex(ValueError,'PARENT_CUSTODY'):M.extract(stage)
    def test_reject_swapped_valid_nasa_urls_even_with_changed_hash_receipt(self):
        stage=self.copy_stage();p=stage/'R88_READING_ROOM.html'
        data=p.read_text();r=M.extract(stage);a,b=r[0]['nasa_source_url'],r[1]['nasa_source_url']
        data=data.replace(a,'__HOLDER__').replace(b,a).replace('__HOLDER__',b);p.write_text(data)
        import json
        receipt=stage/'R92_RECIPROCAL_ROUTES_RECEIPT.json';r92=json.loads(receipt.read_text())
        r92['files']['R88_READING_ROOM.html']=M.sha(p.read_bytes());receipt.write_text(json.dumps(r92))
        with self.assertRaisesRegex(ValueError,'SOURCE_OR_EVIDENCE_BOUNDARY'):M.extract(stage)
    def test_reject_incorrect_limit_even_with_changed_hash_receipt(self):
        stage=self.copy_stage();p=stage/'R88_READING_ROOM.html'
        data=p.read_text().replace('A damage photograph cannot establish a unique ignition mechanism.</p>',
                                    'A photograph proves a unique ignition mechanism.</p>',1)
        p.write_text(data)
        import json
        receipt=stage/'R92_RECIPROCAL_ROUTES_RECEIPT.json';r92=json.loads(receipt.read_text())
        r92['files']['R88_READING_ROOM.html']=M.sha(p.read_bytes());receipt.write_text(json.dumps(r92))
        with self.assertRaisesRegex(ValueError,'EVIDENCE_LIMIT_MISMATCH'):M.extract(stage)
    def test_reject_provisional_date_substitution(self):
        stage=self.copy_stage();p=stage/'R88_READING_ROOM.html'
        data=p.read_text().replace('data-date="January 1967 — day unconfirmed"','data-date="January 27, 1967"')
        p.write_text(data)
        import json
        receipt=stage/'R92_RECIPROCAL_ROUTES_RECEIPT.json';r92=json.loads(receipt.read_text())
        r92['files']['R88_READING_ROOM.html']=M.sha(p.read_bytes());receipt.write_text(json.dumps(r92))
        with self.assertRaisesRegex(ValueError,'PORTRAIT_DAY'):M.extract(stage)
    def test_csv_formula_guard(self):
        bad=deepcopy(M.extract(self.stage));bad[0]['title']='=HYPERLINK("https://bad.test")'
        with self.assertRaisesRegex(ValueError,'FORMULA_HAZARD'):M.make_csv(bad)
    def test_no_js_always_shows_six(self):
        html=M.render(M.extract(self.stage))
        self.assertEqual(html.count('data-period='),6)
        self.assertIn('class="filter-panel" hidden',html)
        self.assertEqual(html.count('aria-label="Reviewed evidence views for source'),6)
        self.assertNotIn('<img',html)
        self.assertNotIn('data-lat=',html)
        self.assertNotIn('data-geo-edge',html)
    def test_refuse_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder);(out/'something').write_text('x')
            with self.assertRaisesRegex(ValueError,'OUTPUT_NOT_EMPTY'):M.assemble(self.stage,out)
    def test_export_is_deterministic(self):
        with tempfile.TemporaryDirectory() as folder:
            a,b=Path(folder)/'a',Path(folder)/'b'
            M.assemble(self.stage,a);M.assemble(self.stage,b)
            files_a={f.name:M.sha(f.read_bytes()) for f in a.iterdir()}
            files_b={f.name:M.sha(f.read_bytes()) for f in b.iterdir()}
            self.assertEqual(files_a,files_b)

if __name__=='__main__':unittest.main()
