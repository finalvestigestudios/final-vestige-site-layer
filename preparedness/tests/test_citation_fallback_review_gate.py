"""R25 independent synthetic/adversarial citation-source packet tests.

No private repository, CMS or network dependencies; never treats synthetic
fixtures as a human audit of actual emergency/medical claims.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import citation_fallback_review_gate as gate

SHARED = 'https://example.org/shared-document'

class Library:
    def __init__(self):
        self.article_origins = {'plan':'start', 'water-planner':'base'}
        self.articles = {
            'plan': {'slug':'plan','status':{'publish':'draft'},
                     'source_use':{'a':'Long direct source-use note for guidance, checked by humans later.',
                                   'shared':'Specific passage and reading limit for the Start contributor.'},
                     '_body':'<h2>Plan</h2><p>Use the list{{cite:a}} but check local rules{{cite:shared}}. Confirm again{{cite:a}}.</p>'},
            'water-planner': {'slug':'water-planner','kind':'tool','status':{'publish':'draft'},
                              'source_use':{'a':'Tool calculation draws on this reference.'},
                              '_body':'<p>Calculated water needs{{cite:a}}</p>'}}
        self.source_variants = {
            'a':[{'id':'a','_origin':'base','url':'https://example.org/a',
                   'verified_on':'2026-10-29','supports':'Baseline evidence with original precise scope.','notes':'Not clinical clearance.'}],
            'shared':[{'id':'shared','_origin':'base','url':SHARED,'verified_on':'2026-10-29',
                       'supports':'Base inspected sections A and B, not C.','notes':'Restricted reading depth.'},
                      {'id':'shared','_origin':'start','url':SHARED,'verified_on':'2026-10-30',
                       'supports':'Start author inspected section C only.','notes':'Do not infer A/B.'}]}
        self.crosswalk_groups = {SHARED:{'review_status':'pending-human-source-and-reading-scope-review',
                                         'reviewer':None,'reviewed_on':None}}
    def source_for(self,meta,sid):
        own = self.article_origins[meta['slug']]
        variants = self.source_variants[sid]
        return next((s for s in variants if s['_origin']==own),
                    next((s for s in variants if s['_origin']=='base'), None))

SMALL=(1,1,4,3,1,1)

def check(lib=None, expected=SMALL):
    return gate.audit(lib or Library(), expected=expected)

class R25Valid(unittest.TestCase):
    def test_valid_packet_is_hold(self):
        got=check()
        self.assertEqual(got['release_state'],'HOLD')
        self.assertIs(got['may_publish'], False)
        self.assertIs(got['independent_QD_approval'],False)
    def test_counts_match(self):
        self.assertEqual(check()['counts'],dict(articles=1,tools=1,citations=4,relationships=3,
                base_fallback_relationships=1,shared_url_groups_unreviewed=1))
    def test_all_excerpts_present(self):
        self.assertEqual(sum(len(r['all_citation_contexts_for_human_claim_review']) for r in check()['review_queue']),4)
    def test_full_original_reading_depth_preserved(self):
        r=next(r for r in check()['review_queue'] if r['source_id']=='shared')
        self.assertEqual(r['source_supports_as_recorded'],'Start author inspected section C only.')
        self.assertEqual(r['article_source_use_as_recorded'],'Specific passage and reading limit for the Start contributor.')
    def test_base_fallback_explicit(self):
        r=next(r for r in check()['review_queue'] if r['slug']=='plan' and r['source_id']=='a')
        self.assertTrue(r['base_fallback_requires_human_scope_review'])
        self.assertEqual(r['source_origin'],'base')
    def test_own_source_preferred_over_base(self):
        r=next(r for r in check()['review_queue'] if r['source_id']=='shared')
        self.assertEqual(r['source_origin'],'start')
        self.assertFalse(r['base_fallback_requires_human_scope_review'])
    def test_shared_url_pending_human(self):
        r=next(r for r in check()['review_queue'] if r['source_id']=='shared')
        self.assertTrue(r['shared_url_group_requires_human_review'])
    def test_human_safety_not_claimed(self):
        for row in check()['review_queue']:
            self.assertIs(row['human_link_checked_by_this_gate'],False)
            self.assertIs(row['human_claim_reviewed_by_this_gate'],False)
    def test_stable_packet_digest(self):
        one,two=check(),check()
        self.assertEqual(one,two)
        digest=one.pop('fingerprint_sha256')
        self.assertEqual(digest,hashlib.sha256(gate.canonical(one)).hexdigest())
    def test_excerpt_transforms_html(self):
        self.assertIn('[CITATION]',check()['review_queue'][0]['all_citation_contexts_for_human_claim_review'][0])
    def test_default_requirements_cover_entire_archive(self):
        self.assertEqual(gate.EXPECTED,(35,1,1959,367,43,30))
    def test_default_contract_fails_on_two_piece_fixture(self):
        with self.assertRaises(gate.ReviewHold):gate.audit(Library())
    def test_no_artifact_writes_performed(self):
        self.assertEqual(check()['machine_authority'],'STRUCTURAL_CITATION_TO_SOURCE_REVIEW_QUEUE_ONLY')

class R25Mutations(unittest.TestCase):
    pass

def mutate_field(case):
    lib=Library()
    a=lib.articles['plan']
    tool=lib.articles['water-planner']
    base=lib.source_variants['a'][0]
    shared=lib.source_variants['shared'][1]
    group=lib.crosswalk_groups[SHARED]
    targets={
        'missing_article':lambda:lib.articles.pop('plan'),
        'extra_article':lambda:lib.articles.update(extra=copy.deepcopy(a)),
        'missing_origin':lambda:lib.article_origins.pop('plan'),
        'extra_origin':lambda:lib.article_origins.update(extra='start'),
        'wrong_origin':lambda:lib.article_origins.update(plan='unlisted'),
        'none_origin':lambda:lib.article_origins.update(plan=None),
        'duplicate_slug':lambda:a.update(slug='water-planner'),
        'slash_slug':lambda:a.update(slug='plan/duplicate'),
        'metadata_slug_mismatch':lambda:a.update(slug='wrong'),
        'no_tool_kind':lambda:tool.pop('kind'),
        'tool_kind_wrong':lambda:tool.update(kind='article'),
        'tool_published':lambda:tool['status'].update(publish='published'),
        'plan_published':lambda:a['status'].update(publish='published'),
        'plan_status_missing':lambda:a.pop('status'),
        'plan_status_none':lambda:a.update(status=None),
        'tool_status_missing':lambda:tool.pop('status'),
        'article_body_missing':lambda:a.pop('_body'),
        'article_body_none':lambda:a.update(_body=None),
        'tool_body_none':lambda:tool.update(_body=None),
        'article_source_use_none':lambda:a.update(source_use=None),
        'source_use_missing':lambda:a['source_use'].pop('shared'),
        'source_use_extra':lambda:a['source_use'].update(ghost='not cited'),
        'source_use_blank':lambda:a['source_use'].update(a='  '),
        'source_use_nonstr':lambda:a['source_use'].update(a=7),
        'missing_citation':lambda:a.update(_body=a['_body'].replace('{{cite:shared}}','')),
        'extra_citation':lambda:a.update(_body=a['_body']+'{{cite:a}}'),
        'new_unknown_citation':lambda:a.update(_body=a['_body'].replace('{{cite:shared}}','{{cite:ghost}}')),
        'unknown_source_id':lambda:lib.source_variants.pop('shared'),
        'no_fallback_base':lambda:lib.source_variants['a'][0].update(_origin='shelter'),
        'duplicated_base_variant':lambda:lib.source_variants['a'].append(copy.deepcopy(base)),
        'duplicated_own_variant':lambda:lib.source_variants['shared'].append(copy.deepcopy(shared)),
        'url_insecure':lambda:base.update(url='http://example.org/a'),
        'url_invalid_type':lambda:base.update(url=17),
        'source_id_missing':lambda:base.pop('id'),
        'source_id_nonstr':lambda:base.update(id=10),
        'source_origin_none':lambda:base.update(_origin=None),
        'source_verify_missing':lambda:base.pop('verified_on'),
        'source_verify_none':lambda:base.update(verified_on=None),
        'source_verify_bad':lambda:base.update(verified_on='2026/10/29'),
        'supports_missing':lambda:base.pop('supports'),
        'supports_blank':lambda:base.update(supports=' '),
        'supports_nonstr':lambda:base.update(supports=[]),
        'crosswalk_empty':lambda:lib.crosswalk_groups.clear(),
        'crosswalk_add_unknown':lambda:lib.crosswalk_groups.update(unknown={}),
        'crosswalk_mark_resolved':lambda:group.update(review_status='resolved'),
        'crosswalk_add_reviewer':lambda:group.update(reviewer='No review proven'),
        'crosswalk_add_review_date':lambda:group.update(reviewed_on='2026-10-31'),
        'duplicate_url_merge':lambda:shared.update(url='https://example.org/unrelated'),
        'selected_source_not_verified':lambda:shared.update(verified_on=None),
        'render_source_select_wrong':lambda:setattr(lib,'source_for',lambda meta,sid:base),
    }
    targets[case]()
    return lib

def mutation_test(case):
    def run(self):
        with self.assertRaises(gate.ReviewHold):
            check(mutate_field(case))
    return run

CASES=(
 'missing_article','extra_article','missing_origin','extra_origin','wrong_origin',
 'none_origin','duplicate_slug','slash_slug','metadata_slug_mismatch','no_tool_kind',
 'tool_kind_wrong','tool_published','plan_published','plan_status_missing',
 'plan_status_none','tool_status_missing','article_body_missing','article_body_none',
 'tool_body_none','article_source_use_none','source_use_missing','source_use_extra',
 'source_use_blank','source_use_nonstr','missing_citation','extra_citation',
 'new_unknown_citation','unknown_source_id','no_fallback_base','duplicated_base_variant',
 'duplicated_own_variant','url_insecure','url_invalid_type','source_id_missing',
 'source_id_nonstr','source_origin_none','source_verify_missing','source_verify_none',
 'source_verify_bad','supports_missing','supports_blank','supports_nonstr',
 'crosswalk_empty','crosswalk_add_unknown','crosswalk_mark_resolved',
 'crosswalk_add_reviewer','crosswalk_add_review_date','duplicate_url_merge',
 'selected_source_not_verified','render_source_select_wrong'
)
for case in CASES:
    setattr(R25Mutations, 'test_reject_'+case, mutation_test(case))

if __name__=='__main__':unittest.main()
