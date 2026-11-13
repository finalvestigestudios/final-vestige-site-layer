"""R332 adversarial fixtures: no canonical source or WordPress output mutations."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import tempfile
import unittest
from preparedness.tools import r331_editorial_handoff_custody_gate as prior
from preparedness.tools import r332_provenance_citation_custody_hold as gate


def fixture():
    docs={}
    for role in prior.SOURCES:
        anchors=list(dict.fromkeys(a for _,k,a,_ in prior.CLAIMS if k==role))
        if role=='a_body':
            anchors+= [a for _,a,_,_,_ in gate.ROWS if a not in anchors]
        if role.endswith('body'):
            docs[role]=(''.join('<p>'+x+'</p>\n' for x in anchors)).encode()
        else:
            m={'n':15 if role=='a_meta' else 104,
               'slug':'family-communication-plan' if role=='a_meta' else 'family-reunification-card',
               'status':{'editorial':'drafted','publish':'draft'},
               'safety_review':{'state':'pending','reviewer':None,'date':None},
               'source_use':{},'note':'. '.join(anchors)}
            docs[role]=json.dumps(m,sort_keys=True).encode()
    return docs,{k:prior.git_blob(v) for k,v in docs.items()}

class R332(unittest.TestCase):
    def setUp(self):
        self.docs,self.pins=fixture()
        self.proposals=gate.proposed_rows()
    def run_gate(self):
        return gate.audit_documents(self.docs,pins=self.pins,proposals=self.proposals)
    def require_invalid(self,fragment):
        r=self.run_gate()
        self.assertEqual(r['state'],'INVALID_HARD_HOLD',r['errors'])
        self.assertTrue(any(fragment in e for e in r['errors']),r['errors'])
        self.assertFalse(r['may_publish'])
        self.assertFalse(r['qualified_safety_approved'])
    def test_complete_fixture_is_held(self):
        x=self.run_gate()
        self.assertEqual(x['state'],'DRAFT_HARD_HOLD',x['errors'])
        self.assertEqual(len(x['review']),8)
        self.assertEqual(x['original_claims_unresolved'],17)
        self.assertEqual(x['tool104_claims_unresolved'],8)
        self.assertFalse(x['claim_support_verified'])
        self.assertFalse(x['candidate_source_ids_are_registered'])
        self.assertFalse(x['merchant_conversion_verified'])
    def test_real_git_pins_reject_synthetic(self):
        self.assertEqual(gate.audit_documents(self.docs)['state'],'INVALID_HARD_HOLD')
    def test_missing_checkout_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            before=list(Path(td).iterdir());x=gate.native_audit(Path(td))
            self.assertEqual(x['state'],'INVALID_HARD_HOLD');self.assertEqual(before,list(Path(td).iterdir()))
    def test_tool104_not_edited(self):
        before=self.docs['t_body'];before2=self.docs['t_meta']
        self.run_gate()
        self.assertEqual(self.docs['t_body'],before);self.assertEqual(self.docs['t_meta'],before2)
    def test_privacy_slot_requires_manual_review(self):
        p=self.proposals['E326-04']
        self.assertIsNone(p['source_id']);self.assertIsNone(p['source_url'])
        self.assertEqual(p['notes'],'NONCITATION_PRIVACY_OR_EDITORIAL_REVIEW')
    def test_provenance_slot_is_eighth(self):
        self.assertEqual(gate.REQUIRED[-1],'E326-08')
        self.assertIn('Red Cross',gate.ROWS[-1][1])
    def test_no_authority_fields_true(self):
        x=self.run_gate()
        for field in ('claim_support_verified','qualified_safety_approved','independent_qd_pass','may_publish','merchant_conversion_verified'):
            self.assertFalse(x[field])
    def test_proposed_source_urls_are_not_verification(self):
        x=self.run_gate();self.assertTrue(all(not row['source_verified'] for row in x['review']))
    def test_original_article_citations_unchanged(self):
        raw=self.docs['a_body'];self.run_gate();self.assertEqual(raw,self.docs['a_body'])
    def test_draft_safety_state_unchanged(self):
        before=self.docs['a_meta'];self.run_gate();self.assertEqual(before,self.docs['a_meta'])
    def test_wrong_old_metadata_approval(self):
        m=json.loads(self.docs['a_meta']);m['status']['publish']='published'
        self.docs['a_meta']=json.dumps(m).encode();self.pins['a_meta']=prior.git_blob(self.docs['a_meta'])
        self.require_invalid('DRAFT_SAFETY_OR_IDENTITY_DRIFT')
    def test_tool_swap(self):
        self.docs['t_body'],self.docs['a_body']=self.docs['a_body'],self.docs['t_body']
        self.require_invalid('PINNED_GIT_SOURCE_CHANGED')
    def test_missing_a_role(self):
        del self.docs['t_meta'];self.require_invalid('FOUR_REQUIRED_ORIGINAL_DOCUMENT_ROLES')
    def test_missing_review_row(self):
        del self.proposals['E326-08'];self.require_invalid('EIGHT_REVIEW_ROWS_REQUIRED')
    def test_extra_review_row(self):
        self.proposals['E326-09']=copy.deepcopy(self.proposals['E326-01']);self.require_invalid('EIGHT_REVIEW_ROWS_REQUIRED')

for idx,(rid,needle,newid,url,oldid) in enumerate(gate.ROWS,1):
    def _remove(self,needle=needle,rid=rid):
        self.docs['a_body']=self.docs['a_body'].replace(needle.encode(),b'ALTERED ORIGINAL',1)
        self.pins['a_body']=prior.git_blob(self.docs['a_body'])
        self.require_invalid('MISSING_OR_REPEATED_ORIGINAL_ANCHOR_'+rid)
    def _double(self,needle=needle,rid=rid):
        self.docs['a_body']+=b'<p>'+needle.encode()+b'</p>'
        self.pins['a_body']=prior.git_blob(self.docs['a_body'])
        self.require_invalid('MISSING_OR_REPEATED_ORIGINAL_ANCHOR_'+rid)
    def _falsepass(self,rid=rid):
        self.proposals[rid]['qualified_safety_approved']=True
        self.require_invalid('FALSE_HUMAN_APPROVAL_'+rid)
    def _sourcereplacement(self,rid=rid,oldid=oldid):
        self.proposals[rid]['source_id']=oldid or 'shelter-fcc-comms'
        self.require_invalid('PROPOSAL_CUSTODY_DRIFT_'+rid)
    def _falseverified(self,rid=rid):
        self.proposals[rid]['reviewed']=True
        self.require_invalid('FALSE_HUMAN_APPROVAL_'+rid)
    def _falsepublished(self,rid=rid):
        self.proposals[rid]['state']='published'
        self.require_invalid('FALSE_HUMAN_APPROVAL_'+rid)
    for label,fn in [('anchor_removed',_remove),('anchor_repeated',_double),('false_safety',_falsepass),
                     ('old_source_substitute',_sourcereplacement),('false_reviewed',_falseverified),('false_published',_falsepublished)]:
        setattr(R332,'test_%02d_%s'%(idx,label),fn)

if __name__=='__main__':unittest.main()
