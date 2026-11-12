"""R309 adversarial tests using synthetic, private temporary fixtures only."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

P = Path(__file__).resolve().parents[1]/'tools'/'r309_tool_identity_hold.py'
spec=importlib.util.spec_from_file_location('fv_r309_identity',P)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)


def fixture():
    base='preparedness/'
    entries={
      base+'taxonomy.json':json.dumps({'tools':[
        {'slug':'family-reunification-card','gate':True,'status':'drafted-pending-safety-review'},
        {'slug':'reunification-plan','gate':True,'status':'drafted-pending-safety-review'}]}),
      base+'content/tools/family-reunification-card.meta.json':json.dumps({'kind':'tool','n':104,
        'slug':'family-reunification-card','status':{'publish':'draft'},
        'safety_review':{'state':'pending'}}),
      base+'content/tools/family-reunification-card.body.html':'<p>Wallet card, privacy-first</p>',
      base+'content/tools/reunification-plan.meta.json':json.dumps({'kind':'tool','n':102,
        'slug':'reunification-plan','status':{'publish':'draft'},
        'safety_review':{'state':'pending'}}),
      base+'content/tools/reunification-plan.body.html':'<p>Full household plan</p>',
      base+'content/articles/family-communication-plan.body.html':
        '<p>Reference {{link:family-reunification-card|wallet card}}</p>',
      base+'content/articles/shelter-or-evacuate.body.html':
        '<p>Reference {{link:family-reunification-card|family card}}</p>',
    }
    return {k:v.encode() for k,v in entries.items()}


class IdentityControls(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.data=fixture()
        for name,data in self.data.items():
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        self.oids={k:mod.git_blob(v) for k,v in self.data.items()}
        self.prior={'state':'DRAFT_HARD_HOLD','errors':[],
                    'publication_authorized':False,'independent_qd_pass':False,
                    'medical_safety_verified':False}

    def inspect(self,**kwargs):
        return mod.audit(self.root,upstream=self.prior,baseline=self.oids,
                         pinned=self.oids,**kwargs)

    def test_clean_fixture_preserves_hard_hold(self):
        r=self.inspect();self.assertEqual(r['errors'],[]);self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
        self.assertEqual(r['source_blobs_verified'],7)
        self.assertFalse(r['publication_authorized'])
        self.assertFalse(r['paid_offer_approved'])
        self.assertFalse(r['independent_qd_pass'])
        self.assertFalse(r['all_41_drafts_verified'])

    def test_missing_checkout_is_invalid(self):
        self.assertEqual(mod.main(['--repo-root',str(self.root)]),1)

    def test_false_upstream_approval_rejected(self):
        self.prior['publication_authorized']=True
        self.assertIn('R308_PREDECESSOR_UNVERIFIED',self.inspect()['errors'])

    def test_false_upstream_qd_rejected(self):
        self.prior['independent_qd_pass']=True
        self.assertIn('R308_PREDECESSOR_UNVERIFIED',self.inspect()['errors'])

    def test_false_upstream_safety_rejected(self):
        self.prior['medical_safety_verified']=True
        self.assertIn('R308_PREDECESSOR_UNVERIFIED',self.inspect()['errors'])

    def test_nonunique_tool_numbers_rejected(self):
        path=self.root/'preparedness/content/tools/reunification-plan.meta.json'
        path.write_text(path.read_text().replace('"n": 102','"n": 104'))
        self.assertIn('SOURCE_BLOB_CHANGED:preparedness/content/tools/reunification-plan.meta.json',self.inspect()['errors'])

    def test_invalid_pinned_inventory_rejected(self):
        changed={**self.oids,'extra':'abcd'}
        r=mod.audit(self.root,pinned=changed,baseline=self.oids,upstream=self.prior)
        self.assertIn('PINNED_TOOL_SOURCE_INVENTORY_CHANGED',r['errors'])

    def test_unauthorized_pin_reassignment_rejected(self):
        changed=dict(self.oids);key=next(iter(changed));changed[key]='0'*40
        r=mod.audit(self.root,pinned=changed,baseline=self.oids,upstream=self.prior)
        self.assertIn('SOURCE_IDENTITY_ATTESTATION_CHANGED:'+key,r['errors'])


for index,name in enumerate(mod.PINNED):
    def missing(self,name=name):
        (self.root/name).unlink()
        self.assertIn('SOURCE_MISSING_OR_SYMLINK:'+name,self.inspect()['errors'])
    def substituted(self,name=name):
        path=self.root/name;path.write_bytes(path.read_bytes()+b' ')
        self.assertIn('SOURCE_BLOB_CHANGED:'+name,self.inspect()['errors'])
    def symlink(self,name=name):
        path=self.root/name;path.unlink();path.symlink_to(self.root/next(iter(self.oids)))
        self.assertIn('SOURCE_MISSING_OR_SYMLINK:'+name,self.inspect()['errors'])
    def unavailable_parent(self,name=name):
        path=self.root/name;path.unlink();path.parent.rename(path.parent.with_name(path.parent.name+'-gone'))
        self.assertIn('SOURCE_MISSING_OR_SYMLINK:'+name,self.inspect()['errors'])
    setattr(IdentityControls,f'test_absent_{index:02d}',missing)
    setattr(IdentityControls,f'test_mutated_{index:02d}',substituted)
    setattr(IdentityControls,f'test_symlink_{index:02d}',symlink)
    setattr(IdentityControls,f'test_parent_move_{index:02d}',unavailable_parent)


if __name__=='__main__':unittest.main()
