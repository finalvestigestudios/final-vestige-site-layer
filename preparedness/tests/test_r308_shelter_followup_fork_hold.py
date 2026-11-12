"""R308 self-contained synthetic tests. Fixtures NEVER touch source directories."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / 'tools/r308_shelter_followup_fork_hold.py'
spec=importlib.util.spec_from_file_location('r308_fork',MODULE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def prior():
    return {'state':'DRAFT_HARD_HOLD','errors':[],
       'bound_format_proofs':4,'substantive_body_differences_unadjudicated':10,
       'metadata_differences_unadjudicated':12,'publication_authorized':False,
       'independent_qd_pass':False,'medical_safety_verified':False,
       'privacy_verified':False,'paid_offer_approved':False,'all_41_drafts_verified':False}

class ForkCustodyFixture(TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory(prefix='r308-isolated-fork-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.rows=[];self.originals={}
        for i,(path,_,_) in enumerate(m.OBSERVED):
            content=(f'<article id="synthetic-{i}">synthetic, not safety advice</article>\n').encode()
            integrated=m.git_blob(content)
            later=integrated if i in (8,9,10,11) else m.git_blob(content+b'UNREVIEWED')
            self.rows.append([path,integrated,later])
            target=self.root/'preparedness'/path
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(content);self.originals[path]=content
        self.observed=tuple(tuple(r) for r in self.rows)
        self.prior=prior()

    def result(self):
        with patch.object(m,'OBSERVED',self.observed):
            return m.audit(self.root,self.rows,self.prior)

    def invalid(self,code=None):
        r=self.result()
        self.assertEqual(r['state'],'INVALID_HARD_HOLD',r)
        self.assertFalse(r['publication_authorized'])
        self.assertFalse(r['independent_qd_pass'])
        self.assertFalse(r['medical_safety_verified'])
        self.assertIsNone(r['confirmed_paid_orders'])
        if code:self.assertTrue(any(code in e for e in r['errors']),r['errors'])

    def test_healthy_fork_is_still_hard_hold(self):
        r=self.result()
        self.assertEqual(r['errors'],[])
        self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
        self.assertEqual(r['integrated_git_blobs_verified'],16)
        self.assertEqual(r['matching_followup_oids_observed'],4)
        self.assertEqual(r['divergent_followup_oids_unadjudicated'],12)
        self.assertEqual(r['scope_counts'],{'article':8,'tool':6,'registry':2})
        self.assertFalse(r['native_build_executed'])
        self.assertFalse(r['all_41_drafts_verified'])

    def test_read_only_within_fixture(self):
        self.result()
        for path,body in self.originals.items():
            self.assertEqual((self.root/'preparedness'/path).read_bytes(),body)

    def test_absent_checkout_is_invalid(self):
        with TemporaryDirectory() as td:
            self.assertEqual(m.main(['--repo-root',td]),1)

    def test_missing_prior(self):
        self.prior=None;self.invalid('R307_UNVERIFIED')

    def test_bad_prior_state(self):
        self.prior['state']='QD_PASS';self.invalid('R307_UNVERIFIED')

    def test_bad_prior_errors(self):
        self.prior['errors']=['incomplete'];self.invalid('R307_UNVERIFIED')

    def test_prior_count_drift(self):
        self.prior['bound_format_proofs']=5;self.invalid('R307_LINEAGE_COUNT_MISMATCH')

    def test_bool_is_not_integer_proof(self):
        self.prior['bound_format_proofs']=True;self.invalid('R307_LINEAGE_COUNT_MISMATCH')

    def test_lost_row(self):
        self.rows.pop();self.invalid('INCOMPLETE_SHELTER_FORK_MATRIX')

    def test_duplicate_row(self):
        self.rows[-1]=self.rows[0][:];self.invalid('DUPLICATE_OR_INVALID_PATH')

    def test_reassigned_crosswalk_pair(self):
        self.rows[0][1]=self.rows[1][1];self.invalid('UNAPPROVED_FORK_EVIDENCE_DRIFT')

    def test_traversal_disallowed(self):
        self.rows[0][0]='../outside.body.html';self.invalid('UNAPPROVED_FORK_EVIDENCE_DRIFT')

    def test_no_live_sale_status(self):
        r=self.result();self.assertIsNone(r['net_revenue_per_1000_qualified_human_sessions'])

    def test_no_risk_approval_even_when_matching(self):
        r=self.result();self.assertFalse(r['privacy_verified']);self.assertFalse(r['paid_offer_approved'])

    def test_fake_branch_identity(self):
        with patch.object(m,'OBSERVED',self.observed):
            r=m.audit(self.root,self.rows,self.prior,heads={'frozen':m.FROZEN_SHELTER_HEAD,
                'continuation':m.CONTINUATION_HEAD,'followup':'0'*40,'integrated':m.R307_HEAD})
        self.assertIn('BRANCH_IDENTITY_DRIFT',r['errors'])

    def test_unknown_extra_row(self):
        self.rows[0][0]='content/tools/unauthorized.html';self.invalid('UNAPPROVED_FORK_EVIDENCE_DRIFT')

    def test_unsigned_blob_id(self):
        self.rows[0][2]='not-a-sha';self.invalid('INVALID_GIT_BLOB')

    def test_frozen_names_remain_read_only(self):
        self.assertEqual(len(m.OBSERVED),16)
        self.assertEqual(m.FROZEN_SHELTER_HEAD,'5daeaf2dd5ab71806a6b73c91edfb1d8df5da976')

def mutation(i,action):
    def test(self):
        rel,old,new=self.rows[i]
        p=self.root/'preparedness'/rel
        if action=='append':
            p.write_bytes(p.read_bytes()+b'CHANGED')
            self.invalid('INTEGRATED_CONTENT_DRIFT')
        elif action=='remove':
            p.unlink();self.invalid('MISSING_OR_SYMLINK_SOURCE')
        elif action=='symlink':
            p.unlink();p.symlink_to(self.root/'preparedness'/self.rows[(i+1)%16][0])
            self.invalid('MISSING_OR_SYMLINK_SOURCE')
        elif action=='swap_integrated':
            self.rows[i][1]=self.rows[(i+1)%16][1]
            self.invalid('UNAPPROVED_FORK_EVIDENCE_DRIFT')
        elif action=='swap_followup':
            self.rows[i][2]=self.rows[(i+1)%16][2]
            self.invalid('UNAPPROVED_FORK_EVIDENCE_DRIFT')
        elif action=='change_type':
            self.rows[i][1]=123
            self.invalid('INVALID_GIT_BLOB')
    return test

for index in range(16):
    for action in ('append','remove','symlink','swap_integrated','swap_followup','change_type'):
        setattr(ForkCustodyFixture,f'test_record_{index:02d}_{action}',mutation(index,action))

for key in ('publication_authorized','independent_qd_pass','medical_safety_verified',
            'privacy_verified','paid_offer_approved','all_41_drafts_verified'):
    def test(self,key=key):
        self.prior[key]=True
        self.invalid('R307_FALSE_RELEASE')
    setattr(ForkCustodyFixture,'test_forged_upstream_'+key,test)

if __name__=='__main__':main()
