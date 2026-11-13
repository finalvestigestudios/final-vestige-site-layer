"""R334 adversarial tests: semantic supersession, source/citation and draft-only safety."""
from __future__ import annotations
import copy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from preparedness.tests.test_r333_e327_nine_slot_supersession_hold import fixture
from preparedness.tools import r331_editorial_handoff_custody_gate as prior
from preparedness.tools import r334_e328_semantic_supersession_hold as gate

CANDIDATE = ("A backup phone is only useful if the device and network work. The California power outage "
 "example is not a nationwide rule. If using VoIP internet-based voice, register the physical address "
 "for 911 with the provider, and update the address when you move the device. A wireless phone "
 "without an active plan may reach 911 but may not supply a location, and the call center cannot "
 "call it back. Text-to-911 depends on local service; calling is preferred when possible. Arrange "
 "a scheduled test through the published non-emergency number, never by an unannounced 911 call.")

class SemanticR334(unittest.TestCase):
    def setUp(self):
        self.documents,self.pins=fixture()
        self.proposal=gate.work_order()
        self.candidate=None
    def result(self):
        return gate.audit_documents(self.documents,pins=self.pins,proposed=self.proposal,candidate=self.candidate)
    def must_hold(self,code=None):
        report=self.result()
        self.assertEqual(report['state'],'INVALID_HARD_HOLD',report['errors'])
        self.assertFalse(report['may_publish'])
        self.assertFalse(report['independent_qd_pass'])
        if code:self.assertIn(code,report['errors'])
        return report
    def test_legitimate_synthetic_baseline_is_not_approval(self):
        v=self.result();self.assertEqual(v['state'],'DRAFT_HARD_HOLD',v['errors'])
        self.assertEqual(v['provenance'],'SIMULATED_PIN_TEST')
        self.assertTrue(v['ordinal_collision_found'])
        self.assertEqual(v['editorial_declared_parent'],'E327-05')
        self.assertEqual(v['semantic_missing_child_parent'],'E327-05')
        self.assertEqual(v['semantic_phone_parent'],'E327-09')
        self.assertEqual((v['article15_original_claims_unresolved'],v['tool104_original_claims_unresolved']),(9,8))
        self.assertEqual(v['cross_cluster_conflicts_unresolved'],15)
        self.assertFalse(v['may_merge'])
    def test_clean_synthetic_proposed_text_only_in_memory(self):
        self.candidate=CANDIDATE
        before=copy.deepcopy(self.documents)
        v=self.result()
        self.assertEqual(v['state'],'DRAFT_HARD_HOLD',v['errors'])
        self.assertEqual(before,self.documents)
        self.assertIsNotNone(v['in_memory_preview'])
        self.assertTrue(v['in_memory_preview']['no_original_source_written'])
        self.assertFalse(v['citation_claim_support_approved'])
    def test_true_original_pins_not_substituted(self):
        self.assertEqual(gate.original.SOURCES['a_body'][1],'8ac8bd7dba3be15d477c15737e54d83364d72527')
        self.assertEqual(len(gate.original.SOURCES),4)
    def test_phone_and_missing_child_semantics_separate(self):
        self.assertNotEqual(gate.SEMANTIC['PHONE_SERVICE_AND_911_LOCATION'],gate.SEMANTIC['MISSING_CHILD_LAW_ENFORCEMENT_FIRST'])
        self.assertEqual(gate.SEMANTIC['PHONE_SERVICE_AND_911_LOCATION'],'E327-09')
        self.assertEqual(gate.SEMANTIC['MISSING_CHILD_LAW_ENFORCEMENT_FIRST'],'E327-05')
    def test_source_readback_is_not_source_support(self):
        self.assertTrue(self.result()['source_register_urls_are_unadjudicated'])
        self.assertTrue(all(x['review_status']=='UNADJUDICATED' for x in self.proposal['source_targets']))
    def test_missing_synthetic_pin_fails(self):
        self.assertEqual(gate.audit_documents(self.documents)['state'],'INVALID_HARD_HOLD')
    def test_native_empty_checkout_fails_no_creation(self):
        with tempfile.TemporaryDirectory() as d:
            old=list(Path(d).rglob('*'))
            with self.assertRaises(OSError):gate.native_audit(Path(d))
            self.assertEqual(old,list(Path(d).rglob('*')))
    def test_pure_read_only_on_missing_data(self):
        self.assertEqual(gate.audit_documents({},pins=self.pins)['state'],'INVALID_HARD_HOLD')
    def test_no_original_changes_even_candidate(self):
        self.candidate=CANDIDATE
        old=copy.deepcopy(self.documents)
        self.result()
        self.assertEqual(old,self.documents)
    def test_proposed_text_not_published(self):
        self.candidate=CANDIDATE
        v=self.result()
        for key in ('citation_claim_support_approved','editorial_change_applied','native_50_pair_exports_verified',
                    'independent_qd_pass','qualified_safety_and_child_privacy_approved',
                    'merchant_preparedness_offer_verified','may_merge','may_publish'):
            self.assertIs(v[key],False,key)
    def test_unchanged_limits_provenance_paragraph(self):
        self.candidate=CANDIDATE
        old=self.documents['a_body']
        self.result()
        self.assertEqual(old,self.documents['a_body'])
    def test_non_unique_fcc_occurrence_rejected(self):
        self.documents['a_body']=self.documents['a_body'].replace(b'The FCC page is undated in source disclosure',b'Undated disclosure')
        self.pins['a_body']=prior.git_blob(self.documents['a_body'])
        self.must_hold('TWO_DISTINCT_FCC_CUSTODY_ANCHORS_REQUIRED')
    def test_comment_spoof_h2_rejected(self):
        self.documents['a_body']+=b'<!-- <h2 id="phones">inert</h2> -->'
        self.pins['a_body']=prior.git_blob(self.documents['a_body'])
        self.must_hold('POSSIBLE_COMMENTED_SECTION_SPOOF')
    def test_rewrite_tool104_rejected(self):
        self.documents['t_body']=self.documents['t_body'].replace(b'call 911 for anything life-threatening',b'NEW PHONE CLAIM')
        self.must_hold('PINNED_GIT_SOURCE_CHANGED_T_BODY')
    def test_fake_approved_meta_rejected(self):
        self.documents['a_meta']=self.documents['a_meta'].replace(b'"draft"',b'"published"')
        self.must_hold('PINNED_GIT_SOURCE_CHANGED_A_META')
    def test_extraneous_proposal_column_rejected(self):
        self.proposal['qd']='PASS';self.must_hold('E328_EXACT_REVIEW_SCHEMA_REQUIRED')
    def test_missing_proposal_column_rejected(self):
        del self.proposal['work_order'];self.must_hold('E328_EXACT_REVIEW_SCHEMA_REQUIRED')
    def test_non_mapping_rejected(self):
        self.proposal=[];self.must_hold('E328_EXACT_REVIEW_SCHEMA_REQUIRED')
    def test_candidate_excessively_short_rejected(self):
        self.candidate='VoIP';self.must_hold('CANDIDATE_LENGTH_OR_EMPTY')
    def test_candidate_excessively_long_rejected(self):
        self.candidate=CANDIDATE+'X'*3500;self.must_hold('CANDIDATE_LENGTH_OR_EMPTY')
    def test_candidate_integers_rejected(self):
        self.candidate=911;self.must_hold('CANDIDATE_NOT_PLAIN_TEXT')
    def test_candidate_repeated_citations_rejected(self):
        self.candidate=CANDIDATE+' {{cite:shelter-fcc-comms}}';self.must_hold('CANDIDATE_MARKUP_TOKEN_OR_CONTROL_CODE')
    def test_no_2026_ready_date_assumption_in_gate(self):
        self.assertNotIn('Ready.gov March 2026 verified',str(gate.work_order()))

# 18 exact schema mutations. Any change to a review identity, source target,
# state or false approval MUST be rejected, without editing original sources.
for idx,key in enumerate(gate.SAFE,1):
    def _bad_field(self,key=key):
        value=self.proposal[key]
        self.proposal[key]=not value if type(value) is bool else ('FAKE_APPROVED' if type(value) is str else [])
        self.must_hold('E328_UNAUTHORIZED_CROSSWALK_OR_APPROVAL_'+key.upper())
    setattr(SemanticR334,'test_%02d_forged_field_%s'%(idx,key),_bad_field)

# New claim evidence may not be promoted from URL readback to independently
# registered sources. Probe every one of the six identified claims separately.
for idx,(claim,url) in enumerate(gate.EVIDENCE,1):
    def _bad_url(self,i=idx-1):
        self.proposal['source_targets'][i]['url']='https://example.invalid/danger'
        self.must_hold('E328_UNAUTHORIZED_CROSSWALK_OR_APPROVAL_SOURCE_TARGETS')
    def _approved(self,i=idx-1):
        self.proposal['source_targets'][i]['review_status']='APPROVED'
        self.must_hold('E328_UNAUTHORIZED_CROSSWALK_OR_APPROVAL_SOURCE_TARGETS')
    def _rename(self,i=idx-1):
        self.proposal['source_targets'][i]['claim']='some-other-topic'
        self.must_hold('E328_UNAUTHORIZED_CROSSWALK_OR_APPROVAL_SOURCE_TARGETS')
    setattr(SemanticR334,'test_%02d_source_url_forgery'%idx,_bad_url)
    setattr(SemanticR334,'test_%02d_source_review_forgery'%idx,_approved)
    setattr(SemanticR334,'test_%02d_source_claim_forgery'%idx,_rename)

# A missing substantive safety scope is a reviewer defect, NOT a safety finding;
# lexical matching does not establish that any sentence is safe or correct.
missing={
    'voip':'VoIP',
    'registered_physical_address':'physical address',
    'change_location':'update the address when you move',
    'service_power_dependency':'power outage',
    'no_plan_location_limit':'without an active plan',
    'cannot_callback':'cannot call it back',
    'text_911_locality':'Text-to-911 depends on local',
    'scheduled_non_emergency_test':'scheduled test through the published non-emergency',
    'california_only':'California power outage example is not a nationwide rule',
}
for idx,(flag,needle) in enumerate(missing.items(),1):
    def _missing(self,flag=flag,needle=needle):
        self.candidate=CANDIDATE.replace(needle,'[editorial TODO]')
        self.must_hold('CANDIDATE_SOURCE_SCOPE_NEEDS_REVIEW_'+flag.upper())
    setattr(SemanticR334,'test_%02d_missing_scope_%s'%(idx,flag),_missing)

for idx,payload in enumerate(['<script>alert(1)</script>','<p>editorial text</p>','{{cite:fake}}','{{link:held-tool}}',
                               '\x00','\x1f','<img src=x>','</h2>','<iframe src="bad">','<a href="/checkout">Pay now</a>'],1):
    def _markup(self,payload=payload):
        self.candidate=CANDIDATE+' '+payload
        self.must_hold('CANDIDATE_MARKUP_TOKEN_OR_CONTROL_CODE')
    setattr(SemanticR334,'test_%02d_unreviewed_markup_or_token'%idx,_markup)
for idx,payload in enumerate(['guarantees','guaranteed','100%','always works','never fails','medically safe','QD PASS'],1):
    def _absolute(self,payload=payload):
        self.candidate=CANDIDATE+' This '+payload+'.'
        self.must_hold('CANDIDATE_UNREVIEWED_ABSOLUTE_ASSURANCE')
    setattr(SemanticR334,'test_%02d_false_assurance'%idx,_absolute)

# Tampering with original source/metadata or the independent wallet card must
# not pass even if an attacker generates new synthetic pins for the altered files.
for idx,(role,mutation) in enumerate([
    ('a_body',b'\n<!-- injected -->'),('t_body',b'\n<!-- updated tool -->'),
    ('a_meta',b'\n '),('t_meta',b'\n '),
    ('a_body',b'<h2 id="phones">evil</h2>'),('a_body',b'<h2 id="school">evil</h2>'),
    ('a_body',b'<h2 id="limits">evil</h2>'),
],1):
    def _tamper(self,role=role,mutation=mutation):
        self.documents[role]+=mutation
        if b'<h2' in mutation:self.pins[role]=prior.git_blob(self.documents[role])
        self.must_hold()
    setattr(SemanticR334,'test_%02d_source_or_section_mutation'%idx,_tamper)

if __name__=='__main__':unittest.main()
