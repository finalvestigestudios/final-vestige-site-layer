#!/usr/bin/env python3
"""Deterministic negative/positive tests; no network, WP write or merchant access."""
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('acceptance', HERE/'staging_acceptance.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def fixture():
    return {'width':390,'js':True,'http':200,'redirects':0,
        'approved_origin':'https://staging.example.test', 'final_origin':'https://staging.example.test',
        'document':{'records':5,'educator':1,'source_links':5,'unsafe_source_links':0,
          'free_ctas':['https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'],
          'paid_ctas':0,'overflow':False,'source_drawers':4,'text_length':1500},
        'axe_violations':[], 'lab_vitals':{'lcp':1100.0,'cls':0.01}}

class Contract(unittest.TestCase):
    def test_origin_safe(self):
        self.assertEqual(mod.canonical_origin('https://staging.example.test/safe/'),'https://staging.example.test')
    def test_http_rejected(self):self.assertIsNone(mod.canonical_origin('http://staging.example.test'))
    def test_production_rejected(self):self.assertIsNone(mod.canonical_origin('https://finalvestige.com'))
    def test_www_production_rejected(self):self.assertIsNone(mod.canonical_origin('https://www.finalvestige.com'))
    def test_credentials_rejected(self):self.assertIsNone(mod.canonical_origin('https://a:b@staging.example.test'))
    def test_query_rejected(self):self.assertIsNone(mod.canonical_origin('https://staging.example.test/x?token=1'))
    def test_fragment_rejected(self):self.assertIsNone(mod.canonical_origin('https://staging.example.test/x#x'))
    def test_custom_port_rejected(self):self.assertIsNone(mod.canonical_origin('https://staging.example.test:444/x'))
    def test_localhost_rejected(self):self.assertIsNone(mod.canonical_origin('https://localhost/x'))
    def test_origin_mismatch(self):
        self.assertTrue(mod.validate_args('https://staging.example.test/x','https://other.example.test','', ''))
    def test_no_unpinned_axe(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'axe.js';p.write_bytes(b'a'*25001)
            self.assertTrue(mod.validate_args('https://staging.example.test/x','https://staging.example.test',str(p),'b'*64))
    def test_symlink_axe_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'axe.js';p.write_bytes(b'a'*25001)
            link=Path(d)/'link.js';link.symlink_to(p)
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertTrue(mod.validate_args('https://staging.example.test/x','https://staging.example.test',str(link),digest))
    def test_hash_matching_axe_probe(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'axe.js';p.write_bytes(b'a'*25001)
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertEqual(mod.validate_args('https://staging.example.test/x','https://staging.example.test',str(p),digest),[])
    def test_approved_origin_must_be_origin_only(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'axe.js';p.write_bytes(b'a'*25001)
            digest=hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertTrue(mod.validate_args('https://staging.example.test/x','https://staging.example.test/other',str(p),digest))
    def test_complete_record_pass(self):self.assertEqual(mod.inspect_row(fixture()),[])
    def test_redirect_fail(self):
        x=fixture();x['redirects']=1;self.assertTrue(mod.inspect_row(x))
    def test_cross_origin_fail(self):
        x=fixture();x['final_origin']='https://elsewhere.example.test';self.assertTrue(mod.inspect_row(x))
    def test_missing_records_fail(self):
        x=fixture();x['document']['records']=4;self.assertTrue(mod.inspect_row(x))
    def test_unsafe_provenance_fail(self):
        x=fixture();x['document']['unsafe_source_links']=1;self.assertTrue(mod.inspect_row(x))
    def test_paid_cta_fail(self):
        x=fixture();x['document']['paid_ctas']=1;self.assertTrue(mod.inspect_row(x))
    def test_second_cta_fail(self):
        x=fixture();x['document']['free_ctas'].append('https://example.com/');self.assertTrue(mod.inspect_row(x))
    def test_wrong_destination_fail(self):
        x=fixture();x['document']['free_ctas']=['https://example.com/'];self.assertTrue(mod.inspect_row(x))
    def test_no_educator_preview_fail(self):
        x=fixture();x['document']['educator']=0;self.assertTrue(mod.inspect_row(x))
    def test_horizontal_overflow_fail(self):
        x=fixture();x['document']['overflow']=True;self.assertTrue(mod.inspect_row(x))
    def test_zero_lcp_fail(self):
        x=fixture();x['lab_vitals']['lcp']=None;self.assertTrue(mod.inspect_row(x))
    def test_slow_lcp_fail(self):
        x=fixture();x['lab_vitals']['lcp']=3000;self.assertTrue(mod.inspect_row(x))
    def test_shift_fail(self):
        x=fixture();x['lab_vitals']['cls']=.11;self.assertTrue(mod.inspect_row(x))
    def test_axe_fail(self):
        x=fixture();x['axe_violations']=[{'id':'color-contrast'}];self.assertTrue(mod.inspect_row(x))
    def test_nojs_acceptable_without_vitals(self):
        x=fixture();x['js']=False;x['lab_vitals']={};self.assertEqual(mod.inspect_row(x),[])

if __name__=='__main__':unittest.main(verbosity=2)
