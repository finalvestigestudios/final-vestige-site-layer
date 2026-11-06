"""R159 isolated adversarial tests. Authentic corpus tests require trusted repo."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

script=Path(__file__).parents[1]/'tools'/'r159_stage_review.py'
spec=importlib.util.spec_from_file_location('r159',script)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

def fixture():
    html='\n'.join(['<p>Family contact steps {{cite:shelter-fcc-comms}}</p>']*16).encode()
    meta=json.dumps({'slug':'family-reunification-card','status':{'publish':'draft'},
        'safety_review':{'state':'pending'},'source_use':{'source'+str(i):'Pending' for i in range(11)}}).encode()
    return html,meta

class ReviewGate(unittest.TestCase):
    def test_valid_snapshot_always_hold(self):
        b,m=fixture();r=g.validate_pair(b,m,b,m,b,m)
        self.assertEqual(r['status'],'DRAFT_HARD_HOLD')
        self.assertEqual(r['citation_occurrences'],16)
        self.assertEqual(r['source_relationships'],11)
        for k in ('qualified_source_review','independent_qd_pass','public_release_allowed','paid_checkout_enabled'):
            self.assertIs(r[k],False)
    def test_git_blob_vector(self):
        self.assertEqual(g.git_blob(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_source_rejects_symlinks(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'real').write_text('x');(root/'alias').symlink_to(root/'real')
            with self.assertRaisesRegex(ValueError,'symlink'):g.source(root,'alias')
    def test_bad_meta_rejected(self):
        b,m=fixture();base=json.loads(m)
        variations=[('slug','other'),('status',{'publish':'published'}),('safety_review',{'state':'approved'}),
                    ('source_use',{}),('source_use',{'x':1}),('status',{}),('safety_review',{})]
        for key,value in variations:
            a=copy.deepcopy(base);a[key]=value;wrong=json.dumps(a).encode()
            with self.subTest(key=key),self.assertRaises((ValueError,KeyError)):
                g.validate_pair(b,m,b,wrong,b,wrong)
    def test_original_source_identity_not_approvable(self):
        b,m=fixture()
        with self.assertRaises(ValueError):
            g.validate_pair(b,m,b,m,b.replace(b'shelter-fcc-comms',b'forged-id',1),m)
    def test_manifest_rejects_incomplete(self):
        with tempfile.TemporaryDirectory() as d:
            for manifest in ({},{'schema':'fv-preparedness-r151-v1','decision':'DRAFT_HARD_HOLD','metadata_blobs':{}},
                             {'schema':'bad','decision':'DRAFT_HARD_HOLD','metadata_blobs':{}}):
                with self.assertRaises((ValueError,KeyError)):g.census(Path(d),manifest)
    def test_cli_never_success(self):
        with tempfile.TemporaryDirectory() as d:self.assertEqual(g.main(['--repo',d]),2)

# 64 independent negative tests: mutated candidate bytes cannot pass a frozen equality check.
def add_negative(i):
    def test(self):
        b,m=fixture()
        if i%4==0: changed=b+b' '+str(i).encode()
        elif i%4==1: changed=b.replace(b'contact',b'CONtact'+str(i).encode(),1)
        elif i%4==2: changed=b[:-i%12-1]
        else: changed=bytes([b[0]^1])+b[1:]
        with self.assertRaises(ValueError):g.validate_pair(b,m,b,m,changed,m)
    return test
for i in range(64):setattr(ReviewGate,'test_mutated_staged_html_%02d'%i,add_negative(i))

if __name__=='__main__':unittest.main()
