"""Offline adversarial tests; never write canonical sources or assert QD PASS."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import tempfile
import unittest
from preparedness.tools import r331_editorial_handoff_custody_gate as prior
from preparedness.tools import r332_provenance_citation_custody_hold as earlier
from preparedness.tools import r333_e327_nine_slot_supersession_hold as gate


def fixture():
    docs={}
    for role in prior.SOURCES:
        anchors=list(dict.fromkeys(a for _,r,a,_ in prior.CLAIMS if r==role))
        if role=='a_body':
            anchors+= [a for _,a,_,_,_ in earlier.ROWS if a not in anchors]
            paragraphs=''.join('<p>'+a+'</p>\n' for a in anchors)
            # Place the *first* FCC mention inside #phones and the second
            # within #limits, matching the authentic source's real ambiguity.
            docs[role]=('<h2 id="intro">Intro</h2>\n'+paragraphs+
                       '<h2 id="phones">Phones</h2><p><span class="pa-tag pa-tag--unc">Uncertain</span> The FCC page is undated, and the earlier advice needs verification.</p>'+
                       '<h2 id="school">School</h2>\n<h2 id="limits">Limits</h2><p>The FCC page is undated in source disclosure.</p>').encode()
        elif role.endswith('body'):
            docs[role]=(''.join('<p>'+a+'</p>\n' for a in anchors)).encode()
        else:
            metadata={'n':15 if role=='a_meta' else 104,
             'slug':'family-communication-plan' if role=='a_meta' else 'family-reunification-card',
             'status':{'editorial':'drafted','publish':'draft'},
             'safety_review':{'state':'pending','reviewer':None,'date':None},
             'source_use':{},'notes':'. '.join(anchors)}
            docs[role]=json.dumps(metadata,sort_keys=True).encode()
    return docs,{k:prior.git_blob(raw) for k,raw in docs.items()}

class E327(unittest.TestCase):
    def setUp(self):
        self.docs,self.pins=fixture()
        self.p=gate.proposals()
    def run_gate(self):
        return gate.audit_documents(self.docs,pins=self.pins,proposed=self.p)
    def held(self):
        v=self.run_gate()
        self.assertEqual(v['state'],'INVALID_HARD_HOLD',v['errors'])
        self.assertFalse(v['may_publish'])
        self.assertFalse(v['independent_qd_pass'])
        return v
    def test_valid_synthetic_still_held(self):
        v=self.run_gate()
        self.assertEqual(v['state'],'DRAFT_HARD_HOLD',v['errors'])
        self.assertEqual((v['article15_original_claims_unresolved'],v['tool104_original_claims_unresolved']),(9,8))
        self.assertEqual(v['active_e327_review_slots'],9)
        self.assertEqual(v['phone_phrase_global_occurrences'],2)
        self.assertIsNotNone(v['phone_section_paragraph_sha256'])
        self.assertEqual(v['provenance'],'SIMULATED_PIN_TEST')
    def test_unpinned_synthetic_is_invalid(self):
        self.assertEqual(gate.audit_documents(self.docs)['state'],'INVALID_HARD_HOLD')
    def test_native_missing_is_invalid(self):
        with tempfile.TemporaryDirectory() as t:
            before=list(Path(t).iterdir())
            with self.assertRaises(OSError):gate.native_audit(Path(t))
            self.assertEqual(before,list(Path(t).iterdir()))
    def test_only_article_is_targeted(self):
        self.assertTrue(all(x['scope']=='ARTICLE_15_ONLY' for x in self.p.values()))
        old=self.docs['t_body']; self.run_gate();self.assertEqual(old,self.docs['t_body'])
    def test_all_false_authorities(self):
        v=self.run_gate()
        for k in ('editorial_revision_applied','source_register_edited','citation_support_approved',
                  'qualified_emergency_and_privacy_review','independent_qd_pass',
                  'word_press_draft_export_verified','paid_offer_authenticated','may_publish'):
            self.assertIs(v[k],False,k)
    def test_nine_replaces_eight_not_stacks(self):
        self.assertEqual([x[1] for x in gate.WORK[:8]],list(earlier.REQUIRED))
        self.assertIsNone(gate.WORK[-1][1])
    def test_double_apply_e326_blocked(self):
        self.p['E326-01']=copy.deepcopy(self.p['E327-01'])
        v=self.held();self.assertIn('DOUBLE_APPLY_E326_E327_FORBIDDEN',v['errors'])
    def test_global_phrase_nonunique_is_not_error(self):
        self.assertEqual(self.run_gate()['phone_phrase_global_occurrences'],2)
        self.assertEqual(self.run_gate()['state'],'DRAFT_HARD_HOLD')
    def test_duplicate_phone_section_rejected(self):
        self.docs['a_body']+=b'<h2 id="phones">Extra</h2>'
        self.pins['a_body']=prior.git_blob(self.docs['a_body'])
        self.assertIn('PHONE_SECTION_BOUNDARY_MISSING_OR_REPEATED',self.held()['errors'])
    def test_duplicate_school_section_rejected(self):
        self.docs['a_body']+=b'<h2 id="school">Extra</h2>'
        self.pins['a_body']=prior.git_blob(self.docs['a_body'])
        self.assertIn('PHONE_SECTION_BOUNDARY_MISSING_OR_REPEATED',self.held()['errors'])
    def test_phone_paragraph_missing_rejected(self):
        self.docs['a_body']=self.docs['a_body'].replace(b'pa-tag--unc',b'pa-tag--other')
        self.pins['a_body']=prior.git_blob(self.docs['a_body'])
        self.assertIn('PHONE_UNCERTAINTY_PARAGRAPH_NOT_UNIQUE_IN_SECTION',self.held()['errors'])
    def test_phone_uncertain_paragraph_duplicate_rejected(self):
        needle=b'<p><span class="pa-tag pa-tag--unc">Uncertain</span> The FCC page is undated, and the earlier advice needs verification.</p>'
        self.docs['a_body']=self.docs['a_body'].replace(needle,needle+needle)
        self.pins['a_body']=prior.git_blob(self.docs['a_body'])
        self.assertIn('PHONE_UNCERTAINTY_PARAGRAPH_NOT_UNIQUE_IN_SECTION',self.held()['errors'])
    def test_limits_paragraph_is_not_rewritten(self):
        v=self.run_gate()
        self.assertEqual(v['review'][-1]['scoped_to'],'SECTION_H2_PHONES_PARAGRAPH')
        self.assertEqual(v['review'][-1]['source_anchor_occurrences_within_scope'],1)
    def test_original_source_git_pin_rejects_changes(self):
        self.docs['a_body']+=b'\n<!-- unauthorized source change -->'
        self.assertIn('PINNED_GIT_SOURCE_CHANGED_A_BODY',self.held()['errors'])
    def test_tool_swap_rejected(self):
        self.docs['a_body'],self.docs['t_body']=self.docs['t_body'],self.docs['a_body']
        self.assertIn('PINNED_GIT_SOURCE_CHANGED_A_BODY',self.held()['errors'])
    def test_unchanged_metadata_gate(self):
        m=json.loads(self.docs['a_meta']);m['status']['publish']='published'
        self.docs['a_meta']=json.dumps(m).encode();self.pins['a_meta']=prior.git_blob(self.docs['a_meta'])
        self.assertIn('DRAFT_SAFETY_OR_IDENTITY_DRIFT_A_META',self.held()['errors'])
    def test_missing_review_row(self):
        del self.p['E327-09'];self.assertIn('EXACT_NINE_E327_REPLACEMENTS_REQUIRED',self.held()['errors'])
    def test_extra_review_row(self):
        self.p['extra']=copy.deepcopy(self.p['E327-09'])
        self.assertIn('EXACT_NINE_E327_REPLACEMENTS_REQUIRED',self.held()['errors'])
    def test_none_source_for_privacy_and_provenance(self):
        self.assertIsNone(self.p['E327-04']['source_id'])
        self.assertIsNone(self.p['E327-08']['source_id'])
    def test_no_canonical_mutations(self):
        original=copy.deepcopy(self.docs);self.run_gate();self.assertEqual(original,self.docs)

for i,(rid,old,anchor,source,url) in enumerate(gate.WORK,1):
    def _bad_source(self,rid=rid):
        self.p[rid]['source_id']='shelter-fcc-comms'
        self.assertIn('E327_CUSTODY_OR_FALSE_CLEARANCE_'+rid+'_SOURCE_ID',self.held()['errors'])
    def _approve(self,rid=rid):
        self.p[rid]['qualified_safety_approved']=True
        self.assertIn('E327_CUSTODY_OR_FALSE_CLEARANCE_'+rid+'_QUALIFIED_SAFETY_APPROVED',self.held()['errors'])
    def _published(self,rid=rid):
        self.p[rid]['publish_allowed']=True
        self.assertIn('E327_CUSTODY_OR_FALSE_CLEARANCE_'+rid+'_PUBLISH_ALLOWED',self.held()['errors'])
    def _source_verified(self,rid=rid):
        self.p[rid]['source_supported']=True
        self.assertIn('E327_CUSTODY_OR_FALSE_CLEARANCE_'+rid+'_SOURCE_SUPPORTED',self.held()['errors'])
    def _append(self,rid=rid):
        self.p[rid]['replacement_mode']='APPEND'
        self.assertIn('E327_CUSTODY_OR_FALSE_CLEARANCE_'+rid+'_REPLACEMENT_MODE',self.held()['errors'])
    def _tool(self,rid=rid):
        self.p[rid]['scope']='TOOL_104'
        self.assertIn('E327_CUSTODY_OR_FALSE_CLEARANCE_'+rid+'_SCOPE',self.held()['errors'])
    def _register(self,rid=rid):
        self.p[rid]['source_registered']=True
        self.assertIn('E327_CUSTODY_OR_FALSE_CLEARANCE_'+rid+'_SOURCE_REGISTERED',self.held()['errors'])
    def _false_review(self,rid=rid):
        self.p[rid]['reviewer_approved']=True
        self.assertIn('E327_CUSTODY_OR_FALSE_CLEARANCE_'+rid+'_REVIEWER_APPROVED',self.held()['errors'])
    def _missing(self,rid=rid,anchor=anchor):
        if rid=='E327-09':
            self.docs['a_body']=self.docs['a_body'].replace(b'The FCC page is undated, and the earlier advice',b'OLDER PHONE CLAIM, and the earlier advice')
        else:self.docs['a_body']=self.docs['a_body'].replace(anchor.encode(),b'UNREVIEWED CHANGE')
        self.pins['a_body']=prior.git_blob(self.docs['a_body'])
        self.assertIn('ORIGINAL_REPLACEMENT_ANCHOR_MISSING_OR_REPEATED_'+rid,self.held()['errors'])
    for label,fn in [('old_source',_bad_source),('false_safety',_approve),('false_publish',_published),
       ('false_source_support',_source_verified),('append_not_replace',_append),('wrong_tool',_tool),
       ('false_source_register',_register),('false_human_review',_false_review),('lost_anchor',_missing)]:
        setattr(E327,'test_%02d_%s'%(i,label),fn)

if __name__=='__main__':unittest.main()
