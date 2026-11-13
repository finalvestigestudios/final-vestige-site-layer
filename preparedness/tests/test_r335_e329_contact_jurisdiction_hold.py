"""R335 synthetic safety-gate probes. No assertions of emergency advice accuracy or QD."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import tempfile
import unittest
from preparedness.tests.test_r333_e327_nine_slot_supersession_hold import fixture
from preparedness.tools import r331_editorial_handoff_custody_gate as original
from preparedness.tools import r335_e329_contact_jurisdiction_hold as gate

CONTACT=('''<h2 id="contact">Step 1: The out-of-area contact</h2>
'''
         '''<p>The FCC's guide recommends that you designate someone out of the area.{{cite:shelter-fcc-comms}}</p>'''
         '''<p>Kids can bring a card.{{cite:shelter-cdc-reunification}}</p>
'''
         '''<h2 id="card">Step 2: What the plan should hold</h2>
''')
CANDIDATE=("The out-of-area contact helps a family report status and check-in, not emergency dispatch. "
 "A person at the emergency scene should contact local emergency services serving that location. "
 "911 calls do not usually transfer across jurisdictions, with few exceptions. "
 "For remote emergency aid in another jurisdiction, look up its official agency website "
 "to find the appropriate 10-digit number. Local rules vary; ask the agency directly. "
 "Do not place an unannounced 911 practice call.")

def synthetic():
    docs,pins=fixture()
    html=docs['a_body'].decode()
    html=html.replace('<h2 id="phones">',CONTACT+'<h2 id="phones">',1)
    docs['a_body']=html.encode()
    meta=json.loads(docs['a_meta'])
    meta['source_use']={'shelter-fcc-comms':{},'shelter-cdc-reunification':{}}
    docs['a_meta']=json.dumps(meta,sort_keys=True).encode()
    pins.update({key:original.git_blob(docs[key]) for key in ('a_body','a_meta')})
    return docs,pins

class ContactR335(unittest.TestCase):
    def setUp(self):
        self.docs,self.pins=synthetic()
        self.order=gate.review_order()
        self.candidate=None
    def audit(self):return gate.audit_documents(self.docs,pins=self.pins,work_order=self.order,candidate=self.candidate)
    def rejects(self,fragment=None):
        r=self.audit()
        self.assertEqual(r['state'],'INVALID_HARD_HOLD',r['errors'])
        self.assertFalse(r['may_publish']);self.assertFalse(r['independent_qd_pass'])
        if fragment:self.assertTrue(any(fragment in x for x in r['errors']),r['errors'])
        return r
    def test_baseline_synthetic_stays_hard_hold(self):
        r=self.audit();self.assertEqual(r['state'],'DRAFT_HARD_HOLD',r['errors'])
        self.assertEqual(r['source_provenance'],'SIMULATED_PIN_TEST')
        self.assertEqual((r['article15_original_claims_unresolved'],r['tool104_original_claims_unresolved']),(9,8))
        self.assertEqual(r['legacy_contributor_conflicts_unresolved'],15)
    def test_valid_candidate_is_in_memory_only(self):
        self.candidate=CANDIDATE
        old=copy.deepcopy(self.docs)
        r=self.audit()
        self.assertEqual(r['state'],'DRAFT_HARD_HOLD',r['errors'])
        self.assertEqual(old,self.docs)
        self.assertTrue(r['in_memory_preview']['no_original_written'])
        self.assertFalse(r['qualified_source_support_approved'])
    def test_sources_not_claim_support(self):
        self.assertTrue(self.audit()['draft_source_urls_unadjudicated'])
        self.assertTrue(all(x['status']=='UNADJUDICATED' for x in self.order['claim_targets']))
    def test_semantic_keys_are_distinct_and_stable(self):
        self.assertEqual(len(set(gate.SEMANTIC.values())),4)
        self.assertEqual(self.audit()['review_semantic_map']['e329_new'],'article15.contact.out_of_area_jurisdiction_limits')
    def test_external_vs_engineering_ordinals_both_flagged(self):
        o=self.order
        self.assertIn('E327-05_PHONE',o['external_editorial_ordinal_conflict'])
        self.assertIn('R333_PHONE_E327-09',o['engineering_ordinal_conflict'])
    def test_protected_phone_and_child_claims_unchanged(self):
        self.candidate=CANDIDATE; old=copy.deepcopy(self.docs)
        self.audit();self.assertEqual(self.docs['a_body'],old['a_body'])
        self.assertEqual(self.docs['t_body'],old['t_body'])
    def test_real_orig_pin_not_forged(self):
        self.assertEqual(self.order['original_body_git_blob'],original.SOURCES['a_body'][1])
    def test_missing_native_rejects_without_side_effects(self):
        with tempfile.TemporaryDirectory() as temp:
            before=list(Path(temp).iterdir())
            with self.assertRaises(OSError):gate.native_audit(Path(temp))
            self.assertEqual(before,list(Path(temp).iterdir()))
    def test_unpinned_synthetic_rejects(self):
        self.assertEqual(gate.audit_documents(self.docs)['state'],'INVALID_HARD_HOLD')
    def test_missing_doc_rejects(self):
        del self.docs['a_body'];self.rejects()
    def test_nonbytes_rejects(self):
        self.docs['a_body']=self.docs['a_body'].decode();self.rejects()
    def test_no_change_to_100_export_verification(self):
        r=self.audit();self.assertFalse(r['authentic_50_wordpress_50_preview_exports_verified'])
        self.assertFalse(r['verified_purchasable_fv_preparedness_product'])
    def test_candidate_nonstring(self):
        self.candidate={'html':'approved'};self.rejects('CANDIDATE_MUST_BE_PLAIN_TEXT')
    def test_candidate_too_short(self):
        self.candidate='no';self.rejects('CANDIDATE_LENGTH_OUTSIDE_REVIEW_BOUNDS')
    def test_candidate_too_long(self):
        self.candidate=CANDIDATE+'x'*2600;self.rejects('CANDIDATE_LENGTH_OUTSIDE_REVIEW_BOUNDS')
    def test_tool104_identity_not_replaced_by_102(self):
        self.docs['t_meta']=self.docs['t_meta'].replace(b'104',b'102');self.rejects()

# Each semantic field, URL, reviewer/disposition flag must fail on substitution.
for ix,field in enumerate(gate.REQUIRED_FIELDS,1):
    def _substitute(self,field=field):
        v=self.order[field]
        self.order[field]=not v if type(v) is bool else ('AUTHENTICATED_QD_PASS' if type(v) is str else [])
        self.rejects('UNAUTHORIZED_SEMANTIC_MAPPING_SOURCE_OR_APPROVAL_'+field.upper())
    setattr(ContactR335,f'test_{ix:02d}_forged_review_identity_{field}',_substitute)

for ix,(claim,url) in enumerate(gate.CLAIMS,1):
    def _url(self,i=ix-1):
        self.order['claim_targets'][i]['url']='https://example.invalid/false-citation'
        self.rejects('UNAUTHORIZED_SEMANTIC_MAPPING_SOURCE_OR_APPROVAL_CLAIM_TARGETS')
    def _state(self,i=ix-1):
        self.order['claim_targets'][i]['status']='VERIFIED'
        self.rejects('UNAUTHORIZED_SEMANTIC_MAPPING_SOURCE_OR_APPROVAL_CLAIM_TARGETS')
    def _claim(self,i=ix-1):
        self.order['claim_targets'][i]['claim']='guaranteed'
        self.rejects('UNAUTHORIZED_SEMANTIC_MAPPING_SOURCE_OR_APPROVAL_CLAIM_TARGETS')
    setattr(ContactR335,f'test_{ix:02d}_source_url_forgery',_url)
    setattr(ContactR335,f'test_{ix:02d}_source_status_forgery',_state)
    setattr(ContactR335,f'test_{ix:02d}_source_claim_forgery',_claim)

for ix,frag in enumerate(['<script>alert(1)</script>','<h2 id="card">fake</h2>',
                          '<a href="https://example.com">pay</a>','{{cite:unreviewed}}',
                          '{{link:family-reunification-card|BUY}}','\x00','\x1a'],1):
    def _bad(self,frag=frag):
        self.candidate=CANDIDATE+' '+frag;self.rejects('CANDIDATE_FORBIDDEN_MARKUP_CITATION_OR_CONTROL')
    setattr(ContactR335,f'test_{ix:02d}_forbidden_markup',_bad)
for ix,frag in enumerate(['guarantees','guaranteed','always','never','universal','medically safe','QD PASS','100%'],1):
    def _bad(self,frag=frag):
        self.candidate=CANDIDATE+' '+frag;self.rejects('CANDIDATE_UNREVIEWED_ABSOLUTE')
    setattr(ContactR335,f'test_{ix:02d}_false_guarantee',_bad)
for ix,frag in enumerate(['pay now','checkout','purchase','exclusive offer','buy today','affiliate'],1):
    def _bad(self,frag=frag):
        self.candidate=CANDIDATE+' '+frag;self.rejects('CANDIDATE_COMMERCIAL_OR_PII_SCOPE_BREACH')
    setattr(ContactR335,f'test_{ix:02d}_commerce_injection',_bad)
for ix,frag in enumerate(['dial 911 to test','call 911 for a practice','text 911 for a test','transfer 911 to any'],1):
    def _bad(self,frag=frag):
        self.candidate=CANDIDATE+' '+frag;self.rejects('CANDIDATE_UNSCHEDULED_TEST_OR_UNIVERSAL_TRANSFER')
    setattr(ContactR335,f'test_{ix:02d}_911_test_false_claim',_bad)

for ix,needle in enumerate(['out-of-area contact','person at the emergency scene','911 calls do not usually transfer',
                             '10-digit number','not emergency dispatch','Local rules vary'],1):
    def _missing(self,needle=needle):
        self.candidate=CANDIDATE.replace(needle,'[UNADJUDICATED]')
        self.rejects('CANDIDATE_SOURCE_SCOPE_REQUIRES_HUMAN_REVIEW')
    setattr(ContactR335,f'test_{ix:02d}_missing_jurisdiction_scope',_missing)

for ix,mutation,code in [
 (1,b'<h2 id="contact">Duplicate</h2>','REQUIRED_H2_NOT_UNIQUE_CONTACT'),
 (2,b'<h2 id="card">Duplicate</h2>','REQUIRED_H2_NOT_UNIQUE_CARD'),
 (3,b'<h2 id="phones">Duplicate</h2>','REQUIRED_H2_NOT_UNIQUE_PHONES'),
 (4,b'<h2 id="school">Duplicate</h2>','REQUIRED_H2_NOT_UNIQUE_SCHOOL'),
 (5,b'<h2 id="limits">Duplicate</h2>','REQUIRED_H2_NOT_UNIQUE_LIMITS'),
 (6,b'<!-- <h2 id="contact">fake</h2> -->','POSSIBLE_COMMENTED_H2_SPOOF'),
 ]:
    def _mutate(self,mutation=mutation,code=code):
        self.docs['a_body']+=mutation
        self.pins['a_body']=original.git_blob(self.docs['a_body'])
        self.rejects(code)
    setattr(ContactR335,f'test_{ix:02d}_spoof_section',_mutate)

for ix,needle in enumerate([b"The FCC's guide recommends",b'out of the area',
                             b'{{cite:shelter-fcc-comms}}',b'{{cite:shelter-cdc-reunification}}'],1):
    def _lost(self,needle=needle):
        self.docs['a_body']=self.docs['a_body'].replace(needle,b'[REPLACED]',1)
        self.pins['a_body']=original.git_blob(self.docs['a_body'])
        self.rejects('ORIGINAL_CONTACT_WITNESS_LOST')
    setattr(ContactR335,f'test_{ix:02d}_lost_contact_witness',_lost)

if __name__=='__main__':unittest.main()
