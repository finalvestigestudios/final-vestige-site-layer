"""R341 synthetic conflict-docket adversarial tests. These do NOT clear QD."""
from __future__ import annotations
import copy
from pathlib import Path
import tempfile
import unittest
from preparedness.tools import r341_nine_branch_conflict_review_hold as gate


def fixture():
    s={
        'schema':gate.CROSSWALK_SCHEMA,
        'scope':'READ_ONLY_GIT_TREE_OBJECTS_NOT_MERGE_SAFETY_OR_SOURCE_CLAIM_APPROVAL',
        'source_heads':dict(gate.HEADS),'integrated_base_commit':gate.INTEGRATION_BASE,
        'distinct_source_divergence_count':14,
        'unresolved_legacy_adjudication_conflict_count_from_issue136':15,
        'divergence_count_is_not_legacy_docket_count':True,
        'source_tree_truncation_detected':False,'integrated_article_bodies':35,
        'integrated_tool_bodies':6,'integrated_missing_body_metadata_pairs':[],
        'source_candidate_paths_missing_from_integrated':[],
        'seven_original_clusters':list(gate.HEADS)[:7],
        'two_shelter_descendants':list(gate.HEADS)[7:],
        'differing_shared_source_paths':[],
    }
    for key in gate.ALLOWED_RELEASE_FALSE+('word_depth_verified','canonical_url_uniqueness_verified'):
        s[key]=False
    rows=[]
    article_slugs=['family-communication-plan','home-fire-escape-plan',
                   'outage-heat-cold-generators','shelter-or-evacuate'] + [f'slate-article-{i:02d}' for i in range(31)]
    tool_slugs=['power-outage-planner','reunification-plan','family-reunification-card',
                'water-planner','kit-builder','home-fire-escape-worksheet']
    for kind,slugs in (('articles',article_slugs),('tools',tool_slugs)):
        for slug in slugs:
            entry={'kind':kind,'slug':slug,'body_blob':'0'*40,'meta_blob':'0'*40}
            for f in ('body.html','meta.json'):
                p=f'preparedness/content/{kind}/{slug}.{f}'
                if p in gate.INTEGRATED:
                    entry['body_blob' if f=='body.html' else 'meta_blob']=gate.INTEGRATED[p]
            rows.append(entry)
    witness={'schema':gate.WITNESS_SCHEMA,'entries':rows,'source_heads':dict(gate.HEADS),
             'release_state':'DRAFT_HARD_HOLD','unresolved_holds':[
                '15_contributor_conflicts','17_article15_tool104_claims',
                'independent_qualified_safety_review','50_wp_50_preview_native_exports',
                'real_paid_sku_checkout_and_net_revenue']}
    for f in ('qualified_qd_pass','historical_and_emergency_safety_approved','source_claim_support_verified',
              'published_or_live','commercial_sku_verified'):witness[f]=False
    for path,blob in gate.INTEGRATED.items():
        clusters=['shelter-continuation','shelter-followup'] if '/tools/' in path else (
            list(gate.HEADS) if path.endswith('taxonomy.json') else ['shelter','shelter-continuation','shelter-followup'])
        contributors=[{'cluster':c,'blob': ('e'*40 if c!='shelter-followup' or path not in gate.SAME_AS_ONE_CONTRIBUTOR else blob)} for c in clusters]
        s['differing_shared_source_paths'].append({
          'path':path,'integrated_blob':blob,'contributors':contributors,
          'integrated_matches_contributor':['shelter-followup'] if path in gate.SAME_AS_ONE_CONTRIBUTOR else [],
          'resolution':'NOT_ADJUDICATED_BY_OBJECT_IDENTITY'})
    return s,witness

class Integrity(unittest.TestCase):
    def setUp(self):self.c,self.w=fixture()
    def audit(self):return gate.check(self.c,self.w)
    def rejected(self,code):
        r=self.audit()
        self.assertEqual(r['state'],'INVALID_HARD_HOLD')
        self.assertTrue(any(code in e for e in r['errors']),r['errors'])
        self.assertIs(r['independent_qd_pass'],False)
        self.assertIs(r['may_publish'],False)
    def test_synthetic_clean_still_draft(self):
        r=self.audit();self.assertEqual(r['state'],'DRAFT_HARD_HOLD');self.assertEqual(r['errors'],[])
        self.assertEqual(r['counts']['raw_source_paths'],14)
        self.assertEqual(r['counts']['human_review_groups'],8)
        self.assertEqual(r['counts']['matching_contributor_paths_still_unresolved'],2)
        self.assertEqual(len(r['human_review_packets']),8)
        self.assertEqual((r['article15_original_claims_unresolved'],r['tool104_original_claims_unresolved']),(9,8))
        self.assertEqual(r['legacy_editorial_conflicts_unresolved'],15)
        self.assertTrue(all(x['human_review_required'] and not x['may_publish'] for x in r['human_review_packets']))
    def test_group_docket_types(self):
        r=self.audit()
        got={x['semantic_group']:x for x in r['human_review_packets']}
        self.assertEqual(set(got),set(gate.GROUPS))
        self.assertEqual(len(got['taxonomy']['raw_source_paths']),1)
        self.assertEqual(len(got['family-communication-plan']['raw_source_paths']),2)
        self.assertIn('Tool #104',got['reunification-plan']['subject'])
    def test_frozen_ledger_blobs_distinct(self):
        self.assertNotEqual(gate.CROSSWALK_GIT_BLOB,gate.WITNESS_GIT_BLOB)
        self.assertEqual(len(gate.INTEGRATED),14)
        self.assertTrue(all(gate.HEX40.fullmatch(x) for x in gate.INTEGRATED.values()))
    def test_missing_native_checkout_no_write(self):
        with tempfile.TemporaryDirectory() as td:
            r=gate.audit_native(Path(td));self.assertEqual(r['state'],'INVALID_HARD_HOLD')
            self.assertEqual(list(Path(td).iterdir()),[])
    def test_invalid_mapping(self):
        self.assertEqual(gate.check(None,self.w)['state'],'INVALID_HARD_HOLD')
    def test_service_animal_anchor_correct_section(self):
        s='<h2 id="special">Access</h2><p>'+gate.SERVICE_ANIMAL_ANCHOR+' and that needs review.</p><h2 id="next">Next</h2>'
        r=gate.check(self.c,self.w,s)
        self.assertEqual(r['state'],'DRAFT_HARD_HOLD')
        self.assertTrue(r['requires_independent_disability_access_and_legal_review'])
    def test_service_animal_anchor_elsewhere_rejected(self):
        s='<h2 id="next">Next</h2><p>'+gate.SERVICE_ANIMAL_ANCHOR+'</p><h2 id="special">Access</h2>'
        self.assertIn('SERVICE_ANIMAL_CLAIM_SECTION_SCOPE_DRIFT',gate.check(self.c,self.w,s)['errors'])
    def test_service_animal_anchor_duplicate_rejected(self):
        s='<h2 id="special">Access</h2>'+gate.SERVICE_ANIMAL_ANCHOR*2
        self.assertIn('NEW_SERVICE_ANIMAL_ORIGINAL_ANCHOR_MISSING_OR_REPEATED',gate.check(self.c,self.w,s)['errors'])
    def test_service_animal_anchor_next_section_rejected(self):
        s='<h2 id="special">Access</h2><h2 id="other">Elsewhere</h2>'+gate.SERVICE_ANIMAL_ANCHOR
        self.assertIn('SERVICE_ANIMAL_CLAIM_OUTSIDE_SPECIAL_SECTION',gate.check(self.c,self.w,s)['errors'])
    def test_article15_is_not_tool104(self):
        self.assertNotIn('family-reunification-card',[gate.group_for_path(x) for x in gate.INTEGRATED])
    def test_path_aliases_rejected(self):
        for path in ('preparedness/../taxonomy.json','preparedness/content/tools/family-reunification-card.body.html',
                     'preparedness/content/articles/FAMILY.body.html','preparedness/content/tools/reunification-plan.fake.json'):
            with self.subTest(path=path):
                with self.assertRaises(ValueError):gate.group_for_path(path)
    def test_forged_counts(self):
        self.c['unresolved_legacy_adjudication_conflict_count_from_issue136']=14
        self.rejected('RAW_OBJECT_VS_LEGACY_CONFLICT_COUNT_COLLISION')
    def test_false_original_coverage(self):
        self.c['integrated_article_bodies']=34
        self.rejected('INTEGRATED_35_ARTICLE_6_TOOL_COVERAGE_DRIFT')
    def test_forged_contributor_label(self):
        self.c['differing_shared_source_paths'][0]['contributors'][0]['cluster']='false-team'
        self.rejected('INVALID_CONTRIBUTOR_GIT_OBJECT')
    def test_contributor_duplicate(self):
        row=self.c['differing_shared_source_paths'][0]
        row['contributors'].append(copy.deepcopy(row['contributors'][0]))
        self.rejected('DUPLICATE_CONTRIBUTOR')
    def test_match_laundering(self):
        row=self.c['differing_shared_source_paths'][0]
        row['integrated_matches_contributor']=['shelter']
        self.rejected('FABRICATED_CONTRIBUTOR_MATCH')
    def test_release_notes_forgery(self):
        self.w['release_state']='PUBLISHED'
        self.rejected('WITNESS_RELEASE_OR_HOLD_LEDGER_DRIFT')
    def test_shuffled_rows_are_safe(self):
        self.c['differing_shared_source_paths'].reverse()
        self.assertEqual(self.audit()['state'],'DRAFT_HARD_HOLD')
    def test_duplicate_docket(self):
        row=copy.deepcopy(self.c['differing_shared_source_paths'][0])
        self.c['differing_shared_source_paths'][1]=row
        self.rejected('DUPLICATE_RAW_SOURCE_DIFF')
    def test_path_traversal(self):
        self.c['differing_shared_source_paths'][0]['path']='../../outside'
        self.rejected('UNKNOWN_OR_PATH_TRAVERSAL_SOURCE_DIFF')
    def test_missing_audit_item(self):
        self.c['differing_shared_source_paths'].pop()
        self.rejected('EXACT_14_RAW_SHARED_OBJECT_DIFFS_REQUIRED')
    def test_unexpected_audit_item(self):
        self.c['differing_shared_source_paths'].append(copy.deepcopy(self.c['differing_shared_source_paths'][0]))
        self.rejected('EXACT_14_RAW_SHARED_OBJECT_DIFFS_REQUIRED')
    def test_witness_missing_metadata(self):
        self.w['entries'][0].pop('meta_blob')
        self.rejected('41_ENTRY_GIT_SOURCE_WITNESS_DISAGREEMENT')
    def test_witness_extra_entry(self):
        self.w['entries'].append(copy.deepcopy(self.w['entries'][0]))
        self.rejected('EXACT_41_ENTRY_WITNESS_REQUIRED')


def change_path(idx,case):
    def test(self):
        path=list(gate.INTEGRATED)[idx]
        row=next(r for r in self.c['differing_shared_source_paths'] if r['path']==path)
        if case=='integrated':row['integrated_blob']='a'*40
        elif case=='approve':row['resolution']='APPROVED'
        elif case=='contributors':row['contributors']=[]
        elif case=='witness':
            for w in self.w['entries']:
                if w['slug'] in path and '/content/' in path:
                    w['body_blob']='a'*40;w['meta_blob']='a'*40
            if '/content/' not in path:row['integrated_blob']='b'*40
        r=self.audit()
        self.assertEqual(r['state'],'INVALID_HARD_HOLD',(case,path,r['errors']))
        self.assertIs(r['may_publish'],False)
    return test

for idx,path in enumerate(gate.INTEGRATED):
    for case in ('integrated','approve','contributors','witness'):
        setattr(Integrity, f'test_drift_{idx:02d}_{case}',change_path(idx,case))

def change_head(name):
    def test(self):
        self.c['source_heads'][name]='0'*40
        self.rejected('NINE_HEAD_SOURCE_CUSTODY_DRIFT')
    return test
for name in gate.HEADS:
    setattr(Integrity,'test_branch_head_'+name.replace('-','_'),change_head(name))

def forge_flag(key,document):
    def test(self):
        getattr(self,document)[key]=True
        self.rejected('FALSE' if document=='w' else 'FORGED')
    return test
for key in gate.ALLOWED_RELEASE_FALSE+('word_depth_verified','canonical_url_uniqueness_verified'):
    setattr(Integrity,'test_forged_crosswalk_'+key,forge_flag(key,'c'))
for key in ('qualified_qd_pass','historical_and_emergency_safety_approved','source_claim_support_verified','published_or_live','commercial_sku_verified'):
    setattr(Integrity,'test_forged_witness_'+key,forge_flag(key,'w'))

if __name__=='__main__':unittest.main()
