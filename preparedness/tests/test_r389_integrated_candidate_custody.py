"""R389 synthetic cross-gate regression tests. No real emergency advice is approved."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('r389', HERE/'tools/r389_integrated_candidate_custody.py')
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)
A, B, C = 'a'*40, 'b'*40, 'c'*40


def candidate(branch='claude/prep-shelter-5e1e0e', blob=A):
    return {'branch': branch, 'body_sha': blob}


def fixture():
    articles = [{'slug':f'guide-{i:02d}', 'variants':[candidate()]} for i in range(35)]
    packet = {'status':'REVIEW_PACKET_HARD_HOLD', 'release':'DRAFT_HARD_HOLD',
              'publication_approved':False,'qualified_safety_approved':False,
              'errors':[],'articles':articles,'unselected_conflicts':[{'path':f'path-{i}'} for i in range(9)]}
    impact = {'status':'SOURCE_IMPACT_REVIEW_HARD_HOLD','release_state':'DRAFT_HARD_HOLD',
              'publication_approved':False,'qualified_safety_approved':False,'errors':[],
              'counts':{'original_articles':35,'source_collision_groups':5,'source_gaps':3}}
    alias = {'status':'SOURCE_URL_ALIAS_REVIEW_HARD_HOLD','release_state':'DRAFT_HARD_HOLD',
             'publication_approved':False,'qualified_safety_approved':False,'errors':[],
             'counts':{'original_articles':35,'unselected_source_collisions':5,'alias_review_groups':17}}
    render = {'status':'RENDER_PARITY_REVIEW_HARD_HOLD','release_state':'DRAFT_HARD_HOLD',
              'publication_approved':False,'qualified_safety_approved':False,'errors':[],
              'counts':{'original_articles':35,'matched_exports':35,'nonarticle_exports_needing_independent_review':15},
              'articles':[{'slug':a['slug'],'matching_variant_candidates':[candidate()],'errors':[]} for a in articles]}
    anchor = {'status':'CLAIM_POSITION_REVIEW_HARD_HOLD','release_state':'DRAFT_HARD_HOLD',
              'publication_approved':False,'qualified_safety_approved':False,'errors':[],
              'counts':{'original_articles':35,'checked_exports':35},
              'articles':[{'slug':a['slug'],'matching_original_candidates':[candidate()]} for a in articles]}
    return packet, impact, alias, render, anchor


class SyntheticIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.wp, self.preview = (Path(self.tmp.name)/x for x in ('wp','preview'))
        self.wp.mkdir(); self.preview.mkdir()
        for i in range(35):
            (self.wp/f'guide-{i:02d}.html').write_text('x')
            (self.preview/f'guide-{i:02d}.html').write_text('x')
        for i in range(15):
            (self.wp/f'tool-{i:02d}.html').write_text('x')
            (self.preview/f'tool-{i:02d}.html').write_text('x')
        self.data = fixture()

    def audit(self, input=None):
        return G.reconcile(*(input or self.data), self.wp, self.preview)

    def bad(self, input=None, expected=None):
        result=self.audit(input)
        self.assertEqual(result['status'],'INVALID_HARD_HOLD')
        self.assertFalse(result['publication_approved'])
        self.assertFalse(result['qualified_safety_approved'])
        self.assertFalse(result['live_release_allowed'])
        if expected:self.assertIn(expected,result['errors'])

    def test_complete_consistent_synthetic_docket_only(self):
        x=self.audit()
        self.assertEqual(x['status'],'INTEGRATED_REVIEW_HARD_HOLD')
        self.assertFalse(x['publication_approved'])
        self.assertFalse(x['human_approved'])
        self.assertEqual(x['counts']['wp_exports'],50)
        self.assertEqual(x['counts']['candidate_intersection_articles'],35)
        self.assertEqual(x['counts']['unselected_manuscript_forks'],9)
        self.assertEqual(x['counts']['source_gaps_pending_human_review'],3)

    def test_repeatable_deterministic_digest(self):
        self.assertEqual(self.audit()['review_digest_sha256'],self.audit()['review_digest_sha256'])

    def test_multiple_original_candidates_not_auto_selected(self):
        rows=list(self.data)
        rows=copy.deepcopy(rows)
        for key in (0,3,4):
            if key==0:rows[0]['articles'][0]['variants'].append(candidate('claude/prep-shelter-continuation',B))
            if key==3:rows[3]['articles'][0]['matching_variant_candidates'].append(candidate('claude/prep-shelter-continuation',B))
            if key==4:rows[4]['articles'][0]['matching_original_candidates'].append(candidate('claude/prep-shelter-continuation',B))
        x=self.audit(rows)
        self.assertEqual(x['status'],'INTEGRATED_REVIEW_HARD_HOLD')
        self.assertEqual(len(x['candidate_intersections'][0]['matching_review_candidates']),2)
        self.assertFalse(x['candidate_intersections'][0]['auto_selected'])

    def test_render_and_anchor_individually_pass_but_no_common_original(self):
        x=copy.deepcopy(self.data)
        for key in (0,3,4):
            if key==0:x[0]['articles'][0]['variants'].append(candidate('claude/prep-shelter-continuation',B))
            if key==4:x[4]['articles'][0]['matching_original_candidates']=[candidate('claude/prep-shelter-continuation',B)]
        self.bad(x,'CROSS_GATE_CANDIDATE_DISJOINT:guide-00')

    def test_branch_same_hash_but_different_provenance_not_overlap(self):
        x=copy.deepcopy(self.data)
        x[0]['articles'][0]['variants'].append(candidate('claude/prep-shelter-continuation',A))
        x[4]['articles'][0]['matching_original_candidates']=[candidate('claude/prep-shelter-continuation',A)]
        self.bad(x,'CROSS_GATE_CANDIDATE_DISJOINT:guide-00')

    def test_claim_anchor_must_be_a_subordinate_gate_not_release_clearance(self):
        x=self.audit()
        self.assertIn('QUALIFIED_WATER_FOOD_EMERGENCY_PRIVACY_QD_REVIEW_UNGRANTED',x['release_blockers'])
        self.assertIn('PURCHASABLE_RIGHTS_CLEARED_PREPAREDNESS_SKU_UNVERIFIED',x['release_blockers'])

    def test_valid_empty_safety_approval_cannot_pass(self):
        x=copy.deepcopy(self.data)
        x[0]['qualified_safety_approved']=None
        self.bad(x,'FAILED_OR_APPROVED_REPORT:packet')

    def test_byte_deterministic_original_git_blob(self):
        self.assertEqual(G.blob_sha(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')

    def test_blobs_with_different_bytes_have_distinct_hash(self):
        self.assertNotEqual(G.blob_sha(b'a'),G.blob_sha(b'b'))

    def test_no_native_repo_fails_closed(self):
        with self.assertRaises(Exception):G.native(Path(self.tmp.name)/'nonexistent',self.wp,self.preview)

    def test_missing_directory_fails_closed(self):
        self.preview.rmdir() if not any(self.preview.iterdir()) else None
        for f in self.preview.iterdir():f.unlink()
        self.preview.rmdir()
        self.bad(expected='PREVIEW:MISSING_OR_SYMLINK_EXPORT_DIRECTORY')

    def test_wrong_report_type_fails_closed(self):
        x=list(self.data);x[1]=None
        self.bad(x,'MISSING_OR_MALFORMED_REPORT:impact')

    def test_symlink_export_file_rejected(self):
        (self.wp/'evil.html').symlink_to(self.wp/'guide-00.html')
        self.bad(expected='WP:UNSAFE_EXPORT_ENTRY:evil.html')

    def test_empty_export_rejected(self):
        (self.wp/'guide-00.html').write_text('')
        self.bad(expected='WP:EXPORT_SIZE_INVALID:guide-00.html')

    def test_export_non_html_rejected(self):
        (self.wp/'unexpected.txt').write_text('x')
        self.bad(expected='WP:UNEXPECTED_EXPORT_FILENAME:unexpected.txt')

    def test_extra_preview_only_export(self):
        (self.preview/'unexpected.html').write_text('x')
        self.bad(expected='WP_PREVIEW_EXACT_FILE_SET_MISMATCH')

    def test_unexpected_fifty_first_pair_needs_nonarticle_accounting(self):
        (self.wp/'extra.html').write_text('x');(self.preview/'extra.html').write_text('x')
        self.bad(expected='NONARTICLE_EXPORT_ACCOUNTING_DRIFT')

    def test_truncated_to_forty_nine_pairs(self):
        (self.wp/'tool-14.html').unlink();(self.preview/'tool-14.html').unlink()
        self.bad(expected='FIFTY_PRIVATE_EXPORT_PAIRS_NOT_VERIFIED')

    def test_different_report_sets_rejected(self):
        x=copy.deepcopy(self.data)
        x[3]['articles'][0]['slug']='impostor'
        self.bad(x,'ARTICLE_REPORT_SLUG_SET_MISMATCH')


def add_mutation_test(name, index, keypath, newval, expected):
    def f(self):
        x=copy.deepcopy(self.data)
        ob=x[index]
        for key in keypath[:-1]:ob=ob[key]
        ob[keypath[-1]]=newval
        self.bad(x,expected)
    f.__name__='test_'+name
    setattr(SyntheticIntegration,f.__name__,f)


# Mutations deliberately exercise independent release/safety/citation contract edges.
for name,idx,path,val,err in [
    ('packet_status',0,['status'],'PASS','FAILED_OR_APPROVED_REPORT:packet'),
    ('impact_status',1,['status'],'PASS','FAILED_OR_APPROVED_REPORT:impact'),
    ('alias_status',2,['status'],'PASS','FAILED_OR_APPROVED_REPORT:alias'),
    ('render_status',3,['status'],'PASS','FAILED_OR_APPROVED_REPORT:render'),
    ('anchor_status',4,['status'],'PASS','FAILED_OR_APPROVED_REPORT:anchor'),
    ('packet_errors',0,['errors'],['tampered'],'FAILED_OR_APPROVED_REPORT:packet'),
    ('impact_errors',1,['errors'],['tampered'],'FAILED_OR_APPROVED_REPORT:impact'),
    ('alias_errors',2,['errors'],['tampered'],'FAILED_OR_APPROVED_REPORT:alias'),
    ('render_errors',3,['errors'],['tampered'],'FAILED_OR_APPROVED_REPORT:render'),
    ('anchor_errors',4,['errors'],['tampered'],'FAILED_OR_APPROVED_REPORT:anchor'),
    ('packet_published',0,['publication_approved'],True,'FAILED_OR_APPROVED_REPORT:packet'),
    ('impact_published',1,['publication_approved'],True,'FAILED_OR_APPROVED_REPORT:impact'),
    ('alias_published',2,['publication_approved'],True,'FAILED_OR_APPROVED_REPORT:alias'),
    ('render_published',3,['publication_approved'],True,'FAILED_OR_APPROVED_REPORT:render'),
    ('anchor_published',4,['publication_approved'],True,'FAILED_OR_APPROVED_REPORT:anchor'),
    ('packet_safety',0,['qualified_safety_approved'],True,'FAILED_OR_APPROVED_REPORT:packet'),
    ('impact_safety',1,['qualified_safety_approved'],True,'FAILED_OR_APPROVED_REPORT:impact'),
    ('alias_safety',2,['qualified_safety_approved'],True,'FAILED_OR_APPROVED_REPORT:alias'),
    ('render_safety',3,['qualified_safety_approved'],True,'FAILED_OR_APPROVED_REPORT:render'),
    ('anchor_safety',4,['qualified_safety_approved'],True,'FAILED_OR_APPROVED_REPORT:anchor'),
    ('impact_wrong_release',1,['release_state'],'LIVE','INVALID_RELEASE_STATE:impact'),
    ('alias_wrong_release',2,['release_state'],'LIVE','INVALID_RELEASE_STATE:alias'),
    ('render_wrong_release',3,['release_state'],'LIVE','INVALID_RELEASE_STATE:render'),
    ('anchor_wrong_release',4,['release_state'],'LIVE','INVALID_RELEASE_STATE:anchor'),
    ('packet_wrong_release',0,['release'],'LIVE','INVALID_RELEASE_STATE:packet'),
    ('impact_commerce',1,['merchant_offer_verified'],True,'INAPPROPRIATE_APPROVAL:impact'),
    ('render_commerce',3,['merchant_offer_verified'],True,'INAPPROPRIATE_APPROVAL:render'),
    ('anchor_live',4,['live_release_allowed'],True,'INAPPROPRIATE_APPROVAL:anchor'),
    ('packet_missing_article',0,['articles'],fixture()[0]['articles'][:-1],'ORIGINAL_35_ARTICLE_9_FORK_INVENTORY_MISMATCH'),
    ('packet_missing_fork',0,['unselected_conflicts'],fixture()[0]['unselected_conflicts'][:-1],'ORIGINAL_35_ARTICLE_9_FORK_INVENTORY_MISMATCH'),
    ('impact_only_34',1,['counts','original_articles'],34,'FIVE_COLLISIONS_OR_ARTICLE_IMPACT_DRIFT'),
    ('impact_only_4_collisions',1,['counts','source_collision_groups'],4,'FIVE_COLLISIONS_OR_ARTICLE_IMPACT_DRIFT'),
    ('alias_only_34',2,['counts','original_articles'],34,'SOURCE_ALIAS_IMPACT_DRIFT'),
    ('alias_only_4_collisions',2,['counts','unselected_source_collisions'],4,'SOURCE_ALIAS_IMPACT_DRIFT'),
    ('render_only_34',3,['counts','original_articles'],34,'RENDER_35_ARTICLE_COVERAGE_MISSING'),
    ('render_only_34_exports',3,['counts','matched_exports'],34,'RENDER_35_ARTICLE_COVERAGE_MISSING'),
    ('anchor_only_34',4,['counts','original_articles'],34,'ANCHOR_35_ARTICLE_COVERAGE_MISSING'),
    ('anchor_only_34_exports',4,['counts','checked_exports'],34,'ANCHOR_35_ARTICLE_COVERAGE_MISSING'),
    ('render_empty_candidate',3,['articles',0,'matching_variant_candidates'],[],'RENDER_CANDIDATE_INVALID:guide-00'),
    ('anchor_empty_candidate',4,['articles',0,'matching_original_candidates'],[],'ANCHOR_CANDIDATE_INVALID:guide-00'),
    ('render_nonoriginal_candidate',3,['articles',0,'matching_variant_candidates'],[candidate(blob=C)],'RENDER_CANDIDATE_INVALID:guide-00'),
    ('anchor_nonoriginal_candidate',4,['articles',0,'matching_original_candidates'],[candidate(blob=B)],'ANCHOR_CANDIDATE_INVALID:guide-00'),
    ('original_bad_branch',0,['articles',0,'variants'],[candidate('bad-origin',A)],'INVALID_ORIGINAL_VARIANTS:guide-00'),
    ('original_bad_sha',0,['articles',0,'variants'],[candidate(blob='abc')],'INVALID_ORIGINAL_VARIANTS:guide-00'),
    ('original_empty_variants',0,['articles',0,'variants'],[],'INVALID_ORIGINAL_VARIANTS:guide-00'),
    ('original_duplicate_variant',0,['articles',0,'variants'],[candidate(),candidate()],'INVALID_ORIGINAL_VARIANTS:guide-00'),
    ('render_duplicate_row',3,['articles'],fixture()[3]['articles']+[fixture()[3]['articles'][0]],'DUPLICATE_ARTICLE_REPORT_ROW'),
    ('anchor_duplicate_row',4,['articles'],fixture()[4]['articles']+[fixture()[4]['articles'][0]],'DUPLICATE_ARTICLE_REPORT_ROW'),
    ('original_duplicate_slug',0,['articles',1,'slug'],'guide-00','DUPLICATE_OR_INVALID_ORIGINAL_SLUG'),
    ('original_invalid_slug',0,['articles',1,'slug'],'../evil','DUPLICATE_OR_INVALID_ORIGINAL_SLUG'),
    ('render_missing_row',3,['articles'],fixture()[3]['articles'][:-1],'ARTICLE_REPORT_SLUG_SET_MISMATCH'),
    ('anchor_missing_row',4,['articles'],fixture()[4]['articles'][:-1],'ARTICLE_REPORT_SLUG_SET_MISMATCH'),
    ('render_candidate_errors',3,['articles',0,'errors'],['hidden-citation'],'RENDER_CANDIDATE_INVALID:guide-00'),
]:
    add_mutation_test(name,idx,path,val,err)

if __name__=='__main__':unittest.main()
