"""Synthetic receipt rejection and source pinning for R191 combined preflight."""
from __future__ import annotations
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

PATH=Path(__file__).resolve().parents[1]/'tools/r191_full_integrated_preflight.py'
spec=importlib.util.spec_from_file_location('r191integrated',PATH)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)

def receipts():
    n={'schema':'fv-preparedness-r190-atomic-native-six-tool-privacy-v1',
       'state':g.HOLD,'native_structural_checks_complete':True,
       'privacy_exports_structurally_checked':True,'generated_tools_checked':6,
       'native_steps_checked':12,'publication_authorized':False,
       'independent_qd_pass':False,'merchant_offer_verified':False,
       'verified_paid_orders':None,'realized_net_revenue':None}
    c={'schema':'fv-preparedness-r191-resource-offer-boundary-v1',
       'state':g.HOLD,'authored_checked':6,'wp_exports_checked':6,
       'errors':[],'publication_authorized':False,
       'independent_qd_pass':False,'merchant_offer_verified':False,
       'privacy_browser_qa_complete':False,'verified_paid_orders':None,
       'realized_net_revenue':None}
    return n,c

class Contract(unittest.TestCase):
    def test_success_is_structural_only(self):
        n,c=receipts()
        self.assertIsNone(g.admit(n,c,build_returncode=0,same_sources=True))
        self.assertEqual(n['state'],g.HOLD)
        self.assertEqual(c['state'],g.HOLD)

    def test_invalid_exit(self):
        self.assertEqual(g.main(['--repo','/nonexistent-path']),2)

    def test_does_not_claim_safety(self):
        r=g.preflight(Path('/nonexistent-path'))
        self.assertEqual(r['state'],g.INVALID)
        self.assertFalse(r['independent_qd_pass'])
        self.assertIsNone(r['verified_paid_orders'])

    def test_boolean_build_returncode_invalid(self):
        n,c=receipts()
        with self.assertRaises(ValueError):g.admit(n,c,build_returncode=False,same_sources=True)

    def test_nonzero_build_returncode_invalid(self):
        n,c=receipts()
        with self.assertRaises(ValueError):g.admit(n,c,build_returncode=1,same_sources=True)

    def test_changed_source_invalid(self):
        n,c=receipts()
        with self.assertRaises(ValueError):g.admit(n,c,build_returncode=0,same_sources=False)

    def test_reject_changed_producer(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);(d/'r190_atomic_native_privacy_preflight.py').write_text('print(1)')
            with self.assertRaises(ValueError):g.load(d,'r190_atomic_native_privacy_preflight.py')

    def test_missing_producer_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):g.load(Path(tmp),'r191_static_resource_offer_gate.py')

    def test_unregistered_producer_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):g.load(Path(tmp),'evil.py')

    def test_symlink_producer_invalid(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            (d/'x').write_text('x')
            (d/'r191_static_resource_offer_gate.py').symlink_to(d/'x')
            with self.assertRaises(ValueError):g.load(d,'r191_static_resource_offer_gate.py')

    def test_original_tool_sha(self):
        data=b'x'
        self.assertEqual(g.git_blob(data),'c1b0730e0133447badcfd47fd144e254807b06e1')

def _make_error_mutations():
    muts=[]
    for key,bad in [
        ('schema','bad'),('state','PASS'),('native_structural_checks_complete',False),
        ('privacy_exports_structurally_checked',False),('generated_tools_checked',5),
        ('native_steps_checked',11),('publication_authorized',True),
        ('independent_qd_pass',True),('merchant_offer_verified',True),
        ('verified_paid_orders',1),('realized_net_revenue',19)]:
        muts.append(('native_'+key,'native',key,bad))
    for key,bad in [
        ('schema','bad'),('state','PASS'),('authored_checked',5),
        ('authored_checked_bool',True),('wp_exports_checked',5),
        ('wp_exports_checked_bool',True),('errors',['bad']),
        ('publication_authorized',True),('independent_qd_pass',True),
        ('merchant_offer_verified',True),('privacy_browser_qa_complete',True),
        ('verified_paid_orders',1),('realized_net_revenue',19)]:
        k=key.replace('_bool','')
        muts.append(('css_'+key,'css',k,bad))
    return muts

class Mutations(unittest.TestCase):
    pass

for name,target,key,value in _make_error_mutations():
    def f(self, target=target,key=key,value=value):
        n,c=receipts()
        (n if target=='native' else c)[key]=value
        with self.assertRaises(ValueError):g.admit(n,c,build_returncode=0,same_sources=True)
    setattr(Mutations,'test_reject_'+name,f)

if __name__=='__main__':unittest.main()
