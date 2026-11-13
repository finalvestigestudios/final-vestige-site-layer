"""Synthetic, canonical-file-free R352 tool lifecycle and source custody tests."""
from __future__ import annotations
import copy
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import r352_tool_lifecycle_custody_gate as gate
from test_r351_canonical_route_gate import SOURCE

PLANNED=sorted(gate.EXPECTED_NOT_STARTED)
DRAFTED=sorted(gate.EXPECTED_DRAFTED)
SECTIONS=['start-here','water','food','shelter-power','health-sanitation',
          'family-communication','lost-ways','field-tools']

def fixture():
    art=[{'slug':f'a-{i:02}','section':SECTIONS[i%7]} for i in range(1,36)]
    tools=[{'slug':x,'status':'drafted-pending-safety-review','gate':True} for x in DRAFTED]
    tools += [{'slug':x,'status':'not-started'} for x in PLANNED]
    tax={'base_path':'/preparedness/','sections':[{'slug':x} for x in SECTIONS],
         'slate':art,'tools':tools}
    documents=[]
    for row in art:
        documents.append({'kind':'articles','body':'A source-backed draft for review.',
                          'meta':{'slug':row['slug'],'section':row['section'],
                                  'track':'modern','status':{'publish':'draft'},
                                  'safety_review':{'state':'pending'}}})
    for i,slug in enumerate(DRAFTED):
        documents.append({'kind':'tools','body':f'Draft {slug} for review.',
                          'meta':{'slug':slug,'section':'field-tools','track':'modern',
                                  'n':101+i,'status':{'publish':'draft'},
                                  'safety_review':{'state':'pending'}}})
    return tax,documents

class Lifecycle(unittest.TestCase):
    def test_nine_planned_six_authored_three_unstarted_is_not_a_conflict(self):
        tax,docs=fixture();v=gate.audit(tax,docs,SOURCE)
        self.assertEqual(v['errors'],[])
        self.assertEqual((v['planned_tool_count'],v['drafted_tool_count'],v['not_started_tool_count'],v['authored_tool_count']), (9,6,3,6))
        self.assertEqual(v['status'],'DRAFT_CUSTODY_ONLY_HARD_HOLD')
    def test_no_release_or_paid_sales_claims_in_clean_case(self):
        tax,docs=fixture();v=gate.audit(tax,docs,SOURCE)
        for key in gate.HOLD:self.assertIs(v[key],False)
    def test_pantry_and_kit_lifecycle_are_not_interchangeable(self):
        tax,docs=fixture()
        self.assertEqual(next(x for x in tax['tools'] if x['slug']=='pantry-worksheet')['status'],'not-started')
        self.assertIn('kit-builder',v:=gate.audit(tax,docs,SOURCE)['authored_tool_slugs'])
        self.assertNotIn('pantry-worksheet',v)
    def test_actual_metadata_number_collision_is_hard_held(self):
        tax,docs=fixture(); m={d['meta']['slug']:d['meta'] for d in docs if d['kind']=='tools'}
        m['reunification-plan']['n']=102;m['home-fire-escape-worksheet']['n']=102
        m['kit-builder']['n']=103;m['power-outage-planner']['n']=103
        out=gate.audit(tax,docs,SOURCE)
        self.assertIn('DUPLICATE_TOOL_DISPLAY_NUMBERS_REQUIRE_REVIEW',out['errors'])
        self.assertEqual(out['duplicate_tool_display_numbers']['102'],['home-fire-escape-worksheet','reunification-plan'])
        self.assertEqual(out['duplicate_tool_display_numbers']['103'],['kit-builder','power-outage-planner'])
        self.assertFalse(out['may_publish'])
    def test_duplicate_tool_number_bool_rejected(self):
        tax,docs=fixture();docs[-1]['meta']['n']=True
        self.assertIn('INVALID_TOOL_NUMBER:'+docs[-1]['meta']['slug'],gate.audit(tax,docs,SOURCE)['errors'])
    def test_no_checkout_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(gate.git_audit(Path(d))['status'],'INVALID_HARD_HOLD')
    def test_exact_builder_blob_cannot_be_faked_by_synthetic_fixture(self):
        tax,docs=fixture();out=gate.audit(tax,docs,SOURCE,exact_builder=True)
        self.assertIn('BUILDER_BLOB_DRIFT',out['errors'])
    def test_taxonomy_pin_rejects_rewritten_text(self):
        tax,docs=fixture();out=gate.audit(tax,docs,SOURCE,taxonomy_raw=b'{}')
        self.assertIn('TAXONOMY_BLOB_DRIFT',out['errors'])
    def test_new_status_and_gate_drift(self):
        tax,docs=fixture();tax['tools'][0]['status']='approved'
        self.assertIn('UNRECOGNIZED_TOOL_LIFECYCLE:'+DRAFTED[0],gate.audit(tax,docs,SOURCE)['errors'])
        tax,docs=fixture();tax['tools'][0]['gate']=False
        self.assertIn('DRAFTED_TOOL_WITHOUT_GATE:'+DRAFTED[0],gate.audit(tax,docs,SOURCE)['errors'])
    def test_synthetic_unlisted_article(self):
        tax,docs=fixture();docs[-1]['kind']='articles'
        self.assertIn('UNLISTED_ARTICLE:'+DRAFTED[-1],gate.audit(tax,docs,SOURCE)['errors'])
    def test_metadata_approvals_refused(self):
        tax,docs=fixture();docs[-1]['meta']['safety_review']['state']='approved'
        self.assertIn('TOOL_SAFETY_OR_SECTION_DRIFT:'+DRAFTED[-1],gate.audit(tax,docs,SOURCE)['errors'])
    def test_unsafe_route_and_external_url(self):
        tax,docs=fixture();docs[-1]['meta']['url']='https://evil.example/preparedness/x/'
        self.assertIn('CONTRADICTORY_URL:tools/'+DRAFTED[-1],gate.audit(tax,docs,SOURCE)['errors'])
    def test_builder_contract_must_match(self):
        tax,docs=fixture();out=gate.audit(tax,docs,SOURCE.replace('/{slug}/','/{slug}'))
        self.assertIn('ROUTE_BUILDER_CONTRACT_DRIFT',out['errors'])

# 41 distinct positive fixture identities + 41 distinct missing manuscript cases.
def _identity(i):
    def test(self):
        tax,docs=fixture();m=docs[i]['meta'];out=gate.audit(tax,docs,SOURCE)
        self.assertEqual(out['errors'],[])
        if docs[i]['kind']=='tools': self.assertIn(m['slug'],out['tools_fingerprints'])
        else:self.assertEqual(out['authored_article_count'],35)
    return test

def _removed(i):
    def test(self):
        tax,docs=fixture();removed=docs.pop(i);out=gate.audit(tax,docs,SOURCE)
        self.assertIn('AUTHORED_COUNT_NOT_35_PLUS_6',out['errors'])
        if removed['kind']=='tools': self.assertIn('AUTHORED_TOOLS_DO_NOT_MATCH_DRAFTED_PLAN',out['errors'])
        else:self.assertIn('ARTICLE_BODY_SLATE_MISMATCH',out['errors'])
    return test

for i in range(41):
    setattr(Lifecycle,f'test_identity_{i+1:02}',_identity(i))
    setattr(Lifecycle,f'test_missing_{i+1:02}',_removed(i))

if __name__=='__main__':unittest.main()
