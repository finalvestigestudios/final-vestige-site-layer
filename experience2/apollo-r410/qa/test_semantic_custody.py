#!/usr/bin/env python3
"""R410 QA: synthetic fixture positive controls AND adversarial semantic drift."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
SRC=HERE/'semantic_custody.py'
spec=importlib.util.spec_from_file_location('apollo_r410_semantic',SRC)
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m)
R408=HERE.parents[1]/'apollo-r408'
HTML=subprocess.check_output(['php',str(R408/'qa/fixture.php')],text=True)
FIRST=HTML[HTML.find('<div class="fv-r408__experience">'):]
end=FIRST.find('<div class="fv-r408__experience">',4)
FIRST=FIRST[:end] if end!=-1 else FIRST
BEGIN=FIRST.find('<section data-fvx-ledger>')
END=FIRST.find('</section>',BEGIN)+len('</section>')
ORIGINAL=FIRST[BEGIN:END]
HASH=m.r409.git_blob(ORIGINAL.encode('utf-8'))

def inspected(html=FIRST,original=ORIGINAL):
    return m.compare(original,html,allow_synthetic_fixture=True,original_blob=HASH)

class Tests(unittest.TestCase):
    def test_synthetic_positive_only(self):
        x=inspected();self.assertTrue(x['pass'],x);self.assertEqual(x['status'],'SYNTHETIC_TEST_ONLY')
    def test_production_cannot_override_original_blob(self):
        x=m.compare(ORIGINAL,FIRST,original_blob=HASH)
        self.assertIn('test_bypass_disallowed',x['errors'])
        self.assertIn('original_git_blob_mismatch',x['errors'])
    def test_fake_nasa_source_text_drift(self):
        x=inspected(FIRST.replace('Not a primary historical text.','It is incontrovertible that an alien started this fire.',1))
        self.assertIn('record_01_historical_text_drift',x['errors'])
    def test_change_one_record_heading(self):
        x=inspected(FIRST.replace('Test-only record 2','Altered record 2',1))
        self.assertIn('record_02_heading_drift',x['errors'])
    def test_change_nasa_publication_for_one_card(self):
        x=inspected(FIRST.replace(m.r409.BOARD,m.r409.LATER,1))
        self.assertIn('atlas_NASA_publication_01',x['errors'])
    def test_atlas_source_binding_swap(self):
        old='#fv-ex2-ledger-apollo1-r407-i1-record-03'
        x=inspected(FIRST.replace(old,'#fv-ex2-ledger-apollo1-r407-i1-record-04',1))
        self.assertIn('atlas_record_binding_03',x['errors'])
    def test_swapped_category(self):
        x=inspected(FIRST.replace('data-fv-r408-kind="sequence"','data-fv-r408-kind="conditions"',1))
        self.assertIn('category_drift_03',x['errors'])
    def test_hollowed_out_limit_in_one_card(self):
        x=inspected(FIRST.replace('Do not present one proposed ignition site or circuit as conclusively proven.','Everything is known!',1))
        self.assertIn('atlas_evidence_limitation_05',x['errors'])
    def test_source_record_hidden(self):
        x=inspected(FIRST.replace('data-fvx-record id="','data-fvx-record hidden id="',1))
        self.assertIn('record_01_concealed',x['errors'])
    def test_atlas_card_hidden(self):
        x=inspected(FIRST.replace('data-fv-r408-card data-fv-r408-kind=','data-fv-r408-card aria-hidden="true" data-fv-r408-kind=',1))
        self.assertIn('atlas_concealed_01',x['errors'])
    def test_record_removed(self):
        x=inspected(FIRST.replace('data-fvx-record','data-stripped-record',1))
        self.assertIn('rendered_record_count',x['errors'])
    def test_original_source_tampered(self):
        x=inspected(original=ORIGINAL.replace('Not a primary historical text.','Fabrication',1))
        self.assertIn('original_git_blob_mismatch',x['errors'])
    def test_missing_input_cli_holds(self):
        with tempfile.TemporaryDirectory() as d:
            result=subprocess.run(['python',str(SRC),'--original',d+'/missing.html','--rendered',d+'/missing2.html'],capture_output=True,text=True)
            self.assertEqual(result.returncode,2)
            self.assertIn('required_input_missing',result.stdout)
    def test_repeat_instance_invalid(self):
        x=inspected(FIRST+FIRST)
        self.assertIn('rendered_record_count',x['errors'])
    def test_non_approved_nasa_url_in_record_detected(self):
        test=ORIGINAL.replace('</article>','<a href="https://www.nasa.gov/research">NASA</a></article>',1)
        x=inspected(FIRST.replace('</article>','<a href="https://www.nasa.gov/other">NASA</a></article>',1),test)
        self.assertIn('record_01_source_link_drift',x['errors'])

if __name__=='__main__':unittest.main(verbosity=2)
