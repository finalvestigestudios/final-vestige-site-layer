"""R153 adversarial review-interlock tests; synthetic only, NEVER safety approval."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('r153', Path(__file__).resolve().parents[1] / 'tools' / 'r153_review_packet_gate.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)

RESOLVED = {
 'home-fire-escape-worksheet': [('usfa-fire-escape',2)],
 'kit-builder': [('cdc-water-store',2), ('ready-are-you-ready',11), ('ready-pets',7)],
 'power-outage-planner': [('fsis-power-failure',1)],
 'reunification-plan': [('ready-are-you-ready',1)],
 'water-planner': [('cdc-water-store',2), ('ready-pets',1), ('ready-water',4)]}

def fixtures():
    d={'schema':'FV-PREP-R149-TOOL-CLAIM-CUSTODY-1','publication_allowed':False,'independent_qd':'NOT_APPROVED',
       'source_scope_human_review':'PENDING','human_link_checked_rows':0,'currently_unresolved_source_ids':58,
       'source_use_row_count':67,'source_use_rows':[],'tool_summaries':[],
       'candidate_tool_origins':{k: ('base' if k=='water-planner' else 'start' if k in ('kit-builder','reunification-plan') else 'shelter') for k in m.TOOLS}}
    for tool,(sources,occurrences) in m.TOOLS.items():
        resolved=RESOLVED.get(tool,[])
        unresolved=sources-len(resolved)
        extras=occurrences-sum(n for _,n in resolved)-unresolved
        items=[(f'{tool}-synthetic-{i}',1+(extras if i==0 else 0),False) for i in range(unresolved)] + [(s,n,True) for s,n in resolved]
        for sid,n,is_resolved in items:
            d['source_use_rows'].append({'tool':tool,'source_id':sid,'citation_occurrences':n,
                'current_origin':'base','candidate_origin':d['candidate_tool_origins'][tool],
                'currently_resolvable':is_resolved,'title':'Synthetic '+sid,'publisher':'Fixture Publisher',
                'literal_url':'https://example.org/'+sid,'source_supports':'Fixture source explanation only',
                'author_specific_use':'Fixture author use only', 'review_decision':'PENDING',
                'human_link_check_recorded':False,'human_source_scope_adjudicated':False,
                'medical_safety_approved':False,'reviewer':None})
        d['tool_summaries'].append({'tool':tool,'publication_allowed':False})
    c={'schema':'fv-preparedness-r151-v1','decision':'DRAFT_HARD_HOLD','qd_pass':False,
       'qualified_safety_review':False,'metadata_blobs':{str(i):'x'*40 for i in range(35)},
       'branches':{str(i):'branch'+str(i) for i in range(7)},
       'source_head_commits':{str(i):'a'*40 for i in range(7)},
       'articles':[{'slug':slug,'resolution':'PINNED_SUBSTITUTION_PENDING'} for slug in m.SLUGS]
       + [{'slug':'other-'+str(i),'resolution':'UPSTREAM_EOL_ONLY'} for i in range(5)]}
    a={'schema':'fv-preparedness-r152-v1','decision':'DRAFT_HARD_HOLD','qd_pass':False,
       'qualified_food_safety_approval':False,'release_authorized':False,
       'source_variants':{'same_url_is_not_same_evidence':True,
          'review':'PENDING_INDEPENDENT_HUMAN_SOURCE_AND_FOOD_SAFETY_REVIEW',
          'origins':{name:{'human_link_check':False} for name in ('base','food','hist-food')}},
       'articles':{slug:{'substitutions':n,'citations':total,'decision':'PENDING_HUMAN_SOURCE_REVIEW',
                           'contexts':[{'line':i+1,'excerpt':'Synthetic citation context'} for i in range(n)]}
                   for slug,(n,total) in m.SLUGS.items()}}
    return d,c,a

class InterlockTest(unittest.TestCase):
    def setUp(self): self.d,self.c,self.a=fixtures()
    def packet(self): return m.make_packet(self.d,self.c,self.a)
    def broken(self, obj, key, val):
        obj[key]=val
        with self.assertRaises((ValueError,KeyError,TypeError)): self.packet()
    def test_01_positive_full_75_item_packet(self):
        p=self.packet(); self.assertEqual((p['review_tasks_total'],len(p['tool_review_tasks']),len(p['historic_food_review_tasks'])),(75,67,8))
    def test_02_citation_multiplicity(self): self.assertEqual(self.packet()['tool_citation_occurrences'],173)
    def test_03_unresolved_source_count(self): self.assertEqual(self.packet()['tool_unresolved'],58)
    def test_04_interpretation_shadow_count(self): self.assertEqual(self.packet()['source_interpretation_changes'],4)
    def test_05_status_hard_hold(self): self.assertEqual(self.packet()['decision'],'DRAFT_HARD_HOLD')
    def test_06_never_qd(self): self.assertFalse(self.packet()['independent_qd_pass'])
    def test_07_never_source_review(self): self.assertFalse(self.packet()['qualified_source_review'])
    def test_08_never_medical_safety(self): self.assertFalse(self.packet()['medical_safety_approved'])
    def test_09_never_paid_sku(self): self.assertFalse(self.packet()['genuine_paid_preparedness_sku_verified'])
    def test_10_never_crosswalk_writes(self): self.assertFalse(self.packet()['source_crosswalk_modified_by_r153'])
    def test_11_stable_fingerprint(self): self.assertEqual(self.packet()['packet_fingerprint'],self.packet()['packet_fingerprint'])
    def test_12_deterministic_round_trip(self): self.assertEqual(self.packet(),m.make_packet(copy.deepcopy(self.d),copy.deepcopy(self.c),copy.deepcopy(self.a)))
    def test_13_original_docket_not_mutated(self):
        before=copy.deepcopy(self.d); self.packet(); self.assertEqual(before,self.d)
    def test_14_row_count_forgery(self): self.broken(self.d,'source_use_row_count',66)
    def test_15_missing_row(self): self.d['source_use_rows'].pop(); self.assertRaises(ValueError,self.packet)
    def test_16_duplicate_row(self): self.d['source_use_rows'][1]=self.d['source_use_rows'][0]; self.assertRaises(ValueError,self.packet)
    def test_17_missing_tool(self): self.d['source_use_rows'][0]['tool']='bad'; self.assertRaises(ValueError,self.packet)
    def test_18_blank_source_id(self): self.d['source_use_rows'][0]['source_id']=''; self.assertRaises(ValueError,self.packet)
    def test_19_citation_count_inflated(self): self.d['source_use_rows'][0]['citation_occurrences']+=1; self.assertRaises(ValueError,self.packet)
    def test_20_citation_count_deleted(self): self.d['source_use_rows'][0]['citation_occurrences']=0; self.assertRaises(ValueError,self.packet)
    def test_21_negative_occurrence(self): self.d['source_use_rows'][0]['citation_occurrences']=-1; self.assertRaises(ValueError,self.packet)
    def test_22_boolean_occurrence(self): self.d['source_use_rows'][0]['citation_occurrences']=True; self.assertRaises(ValueError,self.packet)
    def test_23_http_source(self): self.d['source_use_rows'][0]['literal_url']='http://example.com'; self.assertRaises(ValueError,self.packet)
    def test_24_missing_support(self): self.d['source_use_rows'][0]['source_supports']=''; self.assertRaises(ValueError,self.packet)
    def test_25_missing_author_use(self): self.d['source_use_rows'][0]['author_specific_use']=''; self.assertRaises(ValueError,self.packet)
    def test_26_missing_publisher(self): self.d['source_use_rows'][0]['publisher']=''; self.assertRaises(ValueError,self.packet)
    def test_27_suggested_origin_swap(self): self.d['source_use_rows'][0]['candidate_origin']='base'; self.assertRaises(ValueError,self.packet)
    def test_28_forged_link_check(self): self.d['source_use_rows'][0]['human_link_check_recorded']=True; self.assertRaises(ValueError,self.packet)
    def test_29_forged_review(self): self.d['source_use_rows'][0]['review_decision']='APPROVED'; self.assertRaises(ValueError,self.packet)
    def test_30_forged_medical_approval(self): self.d['source_use_rows'][0]['medical_safety_approved']=True; self.assertRaises(ValueError,self.packet)
    def test_31_forged_source_scope(self): self.d['source_use_rows'][0]['human_source_scope_adjudicated']=True; self.assertRaises(ValueError,self.packet)
    def test_32_forged_reviewer(self): self.d['source_use_rows'][0]['reviewer']='X'; self.assertRaises(ValueError,self.packet)
    def test_33_forged_qd_docket(self): self.broken(self.d,'independent_qd',True)
    def test_34_forged_publication_docket(self): self.broken(self.d,'publication_allowed',True)
    def test_35_forged_source_decision_docket(self): self.broken(self.d,'source_scope_human_review',True)
    def test_36_forged_link_checks_docket(self): self.broken(self.d,'human_link_checked_rows',67)
    def test_37_forged_unresolved_total(self): self.broken(self.d,'currently_unresolved_source_ids',0)
    def test_38_forged_tool_publication(self): self.d['tool_summaries'][0]['publication_allowed']=True; self.assertRaises(ValueError,self.packet)
    def test_39_candidate_tools_missing(self): del self.d['candidate_tool_origins']['kit-builder']; self.assertRaises(ValueError,self.packet)
    def test_40_candidate_tool_origin_changed(self): self.d['candidate_tool_origins']['kit-builder']='foo'; self.assertRaises(ValueError,self.packet)
    def test_41_forged_contributor_qd(self): self.broken(self.c,'qd_pass',True)
    def test_42_forged_contributor_medical(self): self.broken(self.c,'qualified_safety_review',True)
    def test_43_forged_contributor_decision(self): self.broken(self.c,'decision','PASS')
    def test_44_missing_metadata(self): self.c['metadata_blobs'].pop('0'); self.assertRaises(ValueError,self.packet)
    def test_45_missing_contributor(self): self.c['branches'].pop('0'); self.assertRaises(ValueError,self.packet)
    def test_46_fake_contributor_sha(self): self.c['source_head_commits']['0']='NOT_SHA'; self.assertRaises(ValueError,self.packet)
    def test_47_missing_three_way_article(self): self.c['articles'].pop(); self.assertRaises(ValueError,self.packet)
    def test_48_auto_applied_jerky_substitution(self): self.c['articles'][0]['resolution']='APPLIED'; self.assertRaises(ValueError,self.packet)
    def test_49_forged_historical_qd(self): self.broken(self.a,'qd_pass',True)
    def test_50_forged_historical_food_safety(self): self.broken(self.a,'qualified_food_safety_approval',True)
    def test_51_forged_historical_release(self): self.broken(self.a,'release_authorized',True)
    def test_52_missing_three_sources(self): self.a['source_variants']['origins'].pop('base'); self.assertRaises(ValueError,self.packet)
    def test_53_url_equivalence_misclaim(self): self.a['source_variants']['same_url_is_not_same_evidence']=False; self.assertRaises(ValueError,self.packet)
    def test_54_forged_variant_link_check(self): self.a['source_variants']['origins']['base']['human_link_check']=True; self.assertRaises(ValueError,self.packet)
    def test_55_removed_jerky_context(self): self.a['articles']['pemmican-and-dried-meats']['contexts'].pop(); self.assertRaises(ValueError,self.packet)
    def test_56_added_jerky_citation(self): self.a['articles']['pemmican-and-dried-meats']['substitutions']=8; self.assertRaises(ValueError,self.packet)
    def test_57_changed_citation_total(self): self.a['articles']['pioneer-travel-rations']['citations']=40; self.assertRaises(ValueError,self.packet)
    def test_58_forged_historical_approval(self): self.a['articles']['pioneer-travel-rations']['decision']='APPROVED'; self.assertRaises(ValueError,self.packet)
    def test_59_missing_historical_excerpt(self): self.a['articles']['pemmican-and-dried-meats']['contexts'][0]['excerpt']=''; self.assertRaises(ValueError,self.packet)
    def test_60_invalid_historical_line(self): self.a['articles']['pemmican-and-dried-meats']['contexts'][0]['line']=0; self.assertRaises(ValueError,self.packet)
    def test_61_overlong_context(self): self.a['articles']['pemmican-and-dried-meats']['contexts'][0]['excerpt']='x'*321; self.assertRaises(ValueError,self.packet)
    def test_62_sha256_different_inputs(self): self.assertNotEqual(m.fingerprint({'a':1}),m.fingerprint({'a':2}))
    def test_63_git_blob_sha(self): self.assertEqual(m.git_blob(b'test'),'30d74d258442c7c65512eafab474568dd706c430')
    def test_64_load_pinned_rejects_missing(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError): m.load_pinned(Path(t),m.R149_PATH,m.R149_BLOB)
    def test_65_load_pinned_rejects_modified_blob(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/m.R149_PATH; path.parent.mkdir(parents=True); path.write_text('{}')
            with self.assertRaises(ValueError): m.load_pinned(Path(t),m.R149_PATH,m.R149_BLOB)
    def test_66_load_pinned_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/m.R149_PATH; path.parent.mkdir(parents=True); (Path(t)/'src').write_text('{}'); path.symlink_to(Path(t)/'src')
            with self.assertRaises(ValueError): m.load_pinned(Path(t),m.R149_PATH,m.R149_BLOB)
    def test_67_cli_always_holds(self):
        with tempfile.TemporaryDirectory() as t: self.assertEqual(m.main(['--repo',t]),2)
    def test_68_all_67_mutation_checks(self):
        for i in range(67):
            with self.subTest(i=i):
                d=copy.deepcopy(self.d); d['source_use_rows'][i]['review_decision']='PASSED'
                with self.assertRaises(ValueError): m.make_packet(d,self.c,self.a)
    def test_69_all_67_scope_removal_checks(self):
        for i in range(67):
            with self.subTest(i=i):
                d=copy.deepcopy(self.d); d['source_use_rows'][i]['author_specific_use']=''
                with self.assertRaises(ValueError): m.make_packet(d,self.c,self.a)
    def test_70_all_eight_context_removals(self):
        for slug in m.SLUGS:
            for i in range(m.SLUGS[slug][0]):
                with self.subTest(slug=slug,i=i):
                    a=copy.deepcopy(self.a); a['articles'][slug]['contexts'][i]['excerpt']=''
                    with self.assertRaises(ValueError): m.make_packet(self.d,self.c,a)

if __name__=='__main__': unittest.main()
