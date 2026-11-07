"""Isolated synthetic regression for R190 native+privacy joint admission.

This deliberately does NOT run the authentic repository's 35+6 native build or
claim independent safety, privacy, source, QD, sale or merchant verification.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SRC=Path(__file__).resolve().parents[1]/'tools/r190_atomic_native_privacy_preflight.py'
spec=importlib.util.spec_from_file_location('r190gate',SRC)
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)


def receipts():
    checks=[{'step':x,'status':'CHECKED' if i<3 else 'STRUCTURAL_HOLD'}
            for i,x in enumerate(r.NATIVE_STEPS)]
    native={'schema':'fv-preparedness-r188-producer-bound-preflight-v1',
            'state':r.HOLD,'native_structural_checks_complete':True,
            'publication_authorized':False,'independent_qd_pass':False,
            'merchant_offer_verified':False,
            'producer_code':{'schema':'fv-preparedness-r188-producer-code-custody-v1',
                             'state':r.HOLD,'producer_count':16,
                             'producer_manifest_sha256':'a'*64,
                             'publication_authorized':False},
            'native':{'schema':'fv-preparedness-r186-whole-archive-native-preflight-v1',
                      'state':r.HOLD,'census':{'articles':35,'tools':6,
                        'distinct_draft_canonicals':41,'published':0},
                      'publication_authorized':False},
            'checks':checks}
    privacy={'schema':'fv-preparedness-r189-six-tool-privacy-commerce-v1',
             'state':r.HOLD,'errors':[],
             'tools_checked':6,'js_producers_verified':9,'wp_exports_checked':6,
             'publication_authorized':False,'independent_qd_pass':False,
             'qualified_safety_review_complete':False,
             'privacy_browser_qa_complete':False,'merchant_offer_verified':False,
             'verified_paid_orders':None,'realized_net_revenue':None}
    return native,privacy


class Contract(unittest.TestCase):
    def test_baseline_valid_structural_hold(self):
        n,p=receipts();self.assertIsNone(r.adjudicate(n,p,build_returncode=0,unchanged=True))

    def test_build_invalid_boolean_returncode(self):
        n,p=receipts()
        with self.assertRaises(ValueError): r.adjudicate(n,p,build_returncode=False,unchanged=True)

    def test_build_nonzero(self):
        n,p=receipts()
        with self.assertRaises(ValueError): r.adjudicate(n,p,build_returncode=1,unchanged=True)

    def test_source_changed(self):
        n,p=receipts()
        with self.assertRaises(ValueError): r.adjudicate(n,p,build_returncode=0,unchanged=False)

    def test_no_success_state_even_with_valid_receipts(self):
        n,p=receipts()
        self.assertEqual(n['state'],r.HOLD)
        self.assertEqual(p['state'],r.HOLD)
        self.assertNotEqual(n['state'],'PASS')

    def test_recursion_false_clearance(self):
        for obj in ({'z':[{'publication_authorized':True}]},{'qualified_safety_review_complete':None},
                    {'a':{'independent_qd_pass':'false'}}):
            with self.subTest(obj=obj):
                with self.assertRaises(ValueError):r._no_false_clearance(obj)


class Files(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'preparedness'
        (self.root/'tools').mkdir(parents=True)
        (self.root/'content/articles').mkdir(parents=True)
        (self.root/'tools/a.py').write_text('print("hold")\n')
        (self.root/'content/articles/a.body.html').write_text('<p>Guide</p>')

    def test_manifest_deterministic(self):
        a=r._files_and_digest(self.root)
        self.assertEqual(a,r._files_and_digest(self.root))
        self.assertEqual(r._manifest_digest(a),r._manifest_digest(dict(reversed(list(a.items())))))
        self.assertEqual(len(r._manifest_digest(a)),64)

    def test_manifest_detects_authored_change(self):
        a=r._files_and_digest(self.root)
        (self.root/'content/articles/a.body.html').write_text('<p>Changed</p>')
        self.assertNotEqual(a,r._files_and_digest(self.root))

    def test_manifest_skips_generated_build(self):
        a=r._files_and_digest(self.root)
        (self.root/'build/wp').mkdir(parents=True)
        (self.root/'build/wp/test.html').write_text('generated')
        self.assertEqual(a,r._files_and_digest(self.root))

    def test_manifest_skips_pycache(self):
        a=r._files_and_digest(self.root)
        (self.root/'__pycache__').mkdir()
        (self.root/'__pycache__/x.pyc').write_bytes(b'a')
        self.assertEqual(a,r._files_and_digest(self.root))

    def test_manifest_skips_pycs(self):
        a=r._files_and_digest(self.root)
        (self.root/'tools/x.pyc').write_bytes(b'a')
        self.assertEqual(a,r._files_and_digest(self.root))

    def test_manifest_new_source_detected(self):
        a=r._files_and_digest(self.root)
        (self.root/'tools/new.py').write_text('print(2)')
        self.assertNotEqual(a,r._files_and_digest(self.root))

    def test_manifest_deleted_source_detected(self):
        a=r._files_and_digest(self.root)
        (self.root/'tools/a.py').unlink()
        self.assertNotEqual(a,r._files_and_digest(self.root))

    def test_manifest_reject_symlink_file(self):
        (self.root/'tools/alias.py').symlink_to(self.root/'tools/a.py')
        with self.assertRaises(ValueError):r._files_and_digest(self.root)

    def test_manifest_reject_symlink_directory(self):
        (self.root/'tools/link').symlink_to(self.root/'content/articles',target_is_directory=True)
        with self.assertRaises(ValueError):r._files_and_digest(self.root)

    def test_manifest_reject_symlinked_root(self):
        (self.root.parent/'alias').symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(ValueError):r._files_and_digest(self.root.parent/'alias')

    def test_manifest_reject_missing_root(self):
        with self.assertRaises(ValueError):r._files_and_digest(self.root/'missing')

    def test_manifest_reject_large_file(self):
        p=self.root/'tools/big.py';p.write_bytes(b'0'*16)
        original=r.MAX_BYTES
        try:
            r.MAX_BYTES=10
            with self.assertRaises(ValueError):r._files_and_digest(self.root)
        finally:r.MAX_BYTES=original

    def test_manifest_reject_too_many_files(self):
        original=r.MAX_FILES
        try:
            r.MAX_FILES=1
            with self.assertRaises(ValueError):r._files_and_digest(self.root)
        finally:r.MAX_FILES=original

    def test_git_blob_known_identity(self):
        self.assertEqual(r.git_blob(b'test'),hashlib.sha1(b'blob 4\x00test').hexdigest())

    def test_source_only_preflight_does_not_clear_release(self):
        pkt=r.preflight(self.root.parent)
        self.assertEqual(pkt['state'],r.INVALID)
        self.assertFalse(pkt['publication_authorized'])
        self.assertIsNone(pkt['verified_paid_orders'])
        self.assertFalse(pkt['privacy_browser_qa_complete'])

    def test_no_zero_exit(self):
        self.assertEqual(r.main(['--repo',str(self.root.parent)]),2)


NATIVE_CASES={
    'wrong-native-schema': lambda n,p:n.__setitem__('schema','forged'),
    'missing-native-structural':lambda n,p:n.pop('native_structural_checks_complete'),
    'native-invalid':lambda n,p:n.__setitem__('state',r.INVALID),
    'native-pass':lambda n,p:n.__setitem__('state','PASS'),
    'native-approved':lambda n,p:n.__setitem__('publication_authorized',True),
    'native-qdp':lambda n,p:n.__setitem__('independent_qd_pass',True),
    'native-commerce':lambda n,p:n.__setitem__('merchant_offer_verified',True),
    'missing-code-proof':lambda n,p:n.pop('producer_code'),
    'wrong-code-proof-schema':lambda n,p:n['producer_code'].__setitem__('schema','fake'),
    'code-not-hold':lambda n,p:n['producer_code'].__setitem__('state','PASS'),
    'code-15':lambda n,p:n['producer_code'].__setitem__('producer_count',15),
    'code-17':lambda n,p:n['producer_code'].__setitem__('producer_count',17),
    'code-boolean-count':lambda n,p:n['producer_code'].__setitem__('producer_count',True),
    'code-proof-weak-fingerprint':lambda n,p:n['producer_code'].__setitem__('producer_manifest_sha256','b'*63),
    'code-proof-upper':lambda n,p:n['producer_code'].__setitem__('producer_manifest_sha256','A'*64),
    'missing-inner-native':lambda n,p:n.pop('native'),
    'wrong-inner-schema':lambda n,p:n['native'].__setitem__('schema','fake'),
    'inner-invalid':lambda n,p:n['native'].__setitem__('state',r.INVALID),
    '35-article-loss':lambda n,p:n['native']['census'].__setitem__('articles',34),
    '41-route-loss':lambda n,p:n['native']['census'].__setitem__('distinct_draft_canonicals',40),
    'tool-loss':lambda n,p:n['native']['census'].__setitem__('tools',5),
    'published-route':lambda n,p:n['native']['census'].__setitem__('published',1),
    'extra-native-check':lambda n,p:n['checks'].append({'step':'r189','status':'STRUCTURAL_HOLD'}),
    'missing-native-check':lambda n,p:n['checks'].pop(),
    'reordered-check':lambda n,p:n['checks'].reverse(),
    'false-check-pass':lambda n,p:n['checks'][3].__setitem__('status','CHECKED'),
    'false-unit-hold':lambda n,p:n['checks'][2].__setitem__('status','STRUCTURAL_HOLD'),
    'false-validate-pass':lambda n,p:n['checks'][0].__setitem__('status','PASS'),
    'missing-step-name':lambda n,p:n['checks'][1].pop('step'),
    'hidden-positive':lambda n,p:n['checks'][3].__setitem__('publication_allowed',True),
}
PRIVACY_CASES={
    'wrong-privacy-schema':lambda n,p:p.__setitem__('schema','fake'),
    'privacy-invalid':lambda n,p:p.__setitem__('state',r.INVALID),
    'privacy-pass':lambda n,p:p.__setitem__('state','PASS'),
    'error-visible':lambda n,p:p.__setitem__('errors',['unsafe html']),
    'no-errors-field':lambda n,p:p.pop('errors'),
    'five-tools':lambda n,p:p.__setitem__('tools_checked',5),
    'bool-tools':lambda n,p:p.__setitem__('tools_checked',True),
    'eight-js':lambda n,p:p.__setitem__('js_producers_verified',8),
    'four-export':lambda n,p:p.__setitem__('wp_exports_checked',4),
    'falsely-approved':lambda n,p:p.__setitem__('publication_authorized',True),
    'false-qdp':lambda n,p:p.__setitem__('independent_qd_pass',True),
    'false-safety':lambda n,p:p.__setitem__('qualified_safety_review_complete',True),
    'false-browser':lambda n,p:p.__setitem__('privacy_browser_qa_complete',True),
    'false-merchant':lambda n,p:p.__setitem__('merchant_offer_verified',True),
    'fake-order-count':lambda n,p:p.__setitem__('verified_paid_orders',0),
    'fake-net-revenue':lambda n,p:p.__setitem__('realized_net_revenue',0.0),
    'hidden-approval':lambda n,p:p.__setitem__('nested',{'customer_conversion_verified':True}),
    'missing-privacy-qa':lambda n,p:p.pop('privacy_browser_qa_complete'),
}


def scenario(name,mutation):
    def test(self):
        n,p=receipts()
        mutation(n,p)
        with self.assertRaises(ValueError):
            r.adjudicate(n,p,build_returncode=0,unchanged=True)
    test.__name__='test_reject_'+name.replace('-','_')
    return test

for name,mutation in {**NATIVE_CASES,**PRIVACY_CASES}.items():
    setattr(Contract,'test_reject_'+name.replace('-','_'),scenario(name,mutation))

for idx,step in enumerate(r.NATIVE_STEPS):
    def break_step(i):
        def test(self):
            n,p=receipts()
            n['checks'][i]['status']='SKIPPED'
            with self.assertRaises(ValueError):r.adjudicate(n,p,build_returncode=0,unchanged=True)
        return test
    setattr(Contract,f'test_skip_stage_{idx:02}',break_step(idx))

if __name__=='__main__':unittest.main()
