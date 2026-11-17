"""R442 synthetic adversarial custody tests, never advice-quality or release review."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SRC=Path(__file__).resolve().parents[1]/'tools'/'r442_claim_source_binding_gate.py'
spec=importlib.util.spec_from_file_location('r442', SRC)
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)


def fixture():
    branches=[{'branch':f'claude/prep-{i}','sha':f'{i+1:040x}'} for i in range(9)]
    sources=[{'source_id':f'source-{i}','variants':[{'branch':branches[0]['branch'],'source_blob':f'{i+1:040x}',
              'url':f'https://official.example/record/{i}'}]} for i in range(203)]
    articles=[]; bodies={}; rows={}
    for i in range(35):
        slug=f'article-{i}'; sid=f'source-{i}'
        body=f'<article><h2>Preparedness source</h2><p>First actionable claim {{{{cite:{sid}}}}}</p></article>'.encode()
        bodies[slug]=body;articles.append({'slug':slug,'body_candidate_git_blobs':[g.git_blob(body)]})
        cited,_=g.extract_citations(body)
        rows[slug]={'body_git_blob':g.git_blob(body),'citations':[{**c,'reading_scope_exact':'Original page, limited to this stated claim',
             'review_state':'HUMAN_REVIEW_REQUIRED','source_variant':copy.deepcopy(sources[i]['variants'][0])} for c in cited]}
    docket={'schema':1,'original_articles':articles,'all_original_source_id_crosswalk':sources,
            'source_evidence_disputes':[{'source_id':f'source-{i}'} for i in range(5)],
            'shared_exact_url_review_groups':[{'ids':[f'source-{2*i}',f'source-{2*i+1}']} for i in range(17)]}
    annotations={'schema':1,'release_state':g.DRAFT,'articles':rows}
    return docket,bodies,annotations


class SafeFixture(unittest.TestCase):
    def setUp(self):self.d,self.b,self.a=fixture()
    def report(self):return g.review_bundle(self.d,self.b,self.a)
    def expect(self,part):
        all_errors='\n'.join(self.report()['errors'])
        self.assertIn(part,all_errors)
    def test_fixture_has_35(self):self.assertEqual(len(self.b),35)
    def test_fixture_has_203(self):self.assertEqual(len(self.d['all_original_source_id_crosswalk']),203)
    def test_clean_synthetic_structure(self):self.assertEqual(self.report()['errors'],[])
    def test_release_never_eligible(self):self.assertIs(self.report()['eligible'],False)
    def test_no_fake_qd_pass(self):self.assertIs(self.report()['qd_pass'],False)
    def test_no_publication_approval(self):self.assertIs(self.report()['publication_approved'],False)
    def test_no_merchant_approval(self):self.assertIs(self.report()['merchant_offer_verified'],False)
    def test_draft_status(self):self.assertEqual(self.report()['release_state'],g.DRAFT)
    def test_citation_count(self):self.assertEqual(self.report()['citation_occurrences'],35)
    def test_reviewed_count(self):self.assertEqual(self.report()['reviewed_articles'],35)
    def test_disputed_citations_blocked(self):self.assertIn('ORIGINAL_CONTESTED_SOURCE_USED_REQUIRES_ADJUDICATION',self.report()['blockers'])
    def test_shared_ids_blocked(self):self.assertIn('SHARED_EXACT_URL_IDS_REQUIRE_IDENTITY_REVIEW',self.report()['blockers'])
    def test_independent_review_always_needed(self):self.assertIn('INDEPENDENT_QUALIFIED_SAFETY_AND_SOURCE_REVIEW_REQUIRED',self.report()['blockers'])
    def test_missing_docket(self):self.assertIn('INVALID_ORIGINAL_DOCKET',g.review_bundle({},self.b,self.a)['errors'])
    def test_missing_bodies(self):self.assertIn('AUTHENTIC_ORIGINAL_BODY_BYTES_MISSING',g.review_bundle(self.d,None,self.a)['errors'])
    def test_missing_annotations(self):self.assertIn('INDEPENDENT_FROZEN_CITATION_BASELINE_MISSING',g.review_bundle(self.d,self.b,None)['errors'])
    def test_missing_article(self):self.b.pop('article-0');self.expect('ORIGINAL_BODY_SET_NOT_EXACTLY_35')
    def test_extra_article(self):self.b['extra']=b'<p>x</p>';self.expect('ORIGINAL_BODY_SET_NOT_EXACTLY_35')
    def test_missing_attestation_article(self):self.a['articles'].pop('article-0');self.expect('BASELINE_ARTICLE_SET_NOT_EXACTLY_35')
    def test_extra_attestation_article(self):self.a['articles']['extra']={};self.expect('BASELINE_ARTICLE_SET_NOT_EXACTLY_35')
    def test_invalid_baseline_schema(self):self.a['schema']=4;self.expect('INVALID_FROZEN_CITATION_BASELINE')
    def test_unsafe_baseline_release(self):self.a['release_state']='QD_PASS';self.expect('INVALID_FROZEN_CITATION_BASELINE')
    def test_duplicate_article_slug(self):self.d['original_articles'][1]['slug']='article-0';self.expect('ARTICLE_SLUG_COLLISION')
    def test_duplicate_source_id(self):self.d['all_original_source_id_crosswalk'][1]['source_id']='source-0';self.expect('SOURCE_ID_COLLISION')
    def test_missing_original_source(self):self.d['all_original_source_id_crosswalk'].pop();self.expect('TWO_HUNDRED_THREE_ORIGINAL_SOURCE_IDENTITIES_REQUIRED')
    def test_missing_original_article(self):self.d['original_articles'].pop();self.expect('THIRTY_FIVE_ORIGINAL_ARTICLE_IDENTITIES_REQUIRED')
    def test_missing_shared_groups(self):self.d['shared_exact_url_review_groups'].pop();self.expect('SEVENTEEN_SHARED_URL_GROUPS_MUST_REMAIN_VISIBLE')
    def test_missing_disputes(self):self.d['source_evidence_disputes'].pop();self.expect('FIVE_DISPUTES_MUST_REMAIN_UNSELECTED')
    def test_body_change(self):self.b['article-0']+=b'<!-- mutated -->';self.expect('BODY_NOT_IN_FROZEN_CANDIDATE_SET')
    def test_body_hash_attestation_changed(self):self.a['articles']['article-0']['body_git_blob']='f'*40;self.expect('ATTESTATION_BODY_HASH_MISMATCH')
    def test_citation_source_swapped(self):self.a['articles']['article-0']['citations'][0]['source_id']='source-1';self.expect('CITATION_CLAIM_BINDING_CHANGED')
    def test_citation_context_swapped(self):self.a['articles']['article-0']['citations'][0]['context_sha256']='0'*64;self.expect('CITATION_CLAIM_BINDING_CHANGED')
    def test_citation_context_invalid_digest(self):self.a['articles']['article-0']['citations'][0]['context_sha256']='xx';self.expect('INVALID_CONTEXT_DIGEST')
    def test_citation_occurrence_changed(self):self.a['articles']['article-0']['citations'][0]['occurrence']=2;self.expect('CITATION_CLAIM_BINDING_CHANGED')
    def test_citation_block_changed(self):self.a['articles']['article-0']['citations'][0]['block_index']=9;self.expect('CITATION_CLAIM_BINDING_CHANGED')
    def test_missing_citation(self):self.a['articles']['article-0']['citations']=[];self.expect('CITATION_OCCURRENCE_COUNT_DRIFT')
    def test_missing_citation_list(self):self.a['articles']['article-0'].pop('citations');self.expect('ATTESTATION_CITATIONS_NOT_LIST')
    def test_missing_attestation(self):self.a['articles']['article-0']=None;self.expect('ARTICLE_CITATION_ATTESTATION_MISSING')
    def test_missing_source_reading_scope(self):self.a['articles']['article-0']['citations'][0]['reading_scope_exact']='';self.expect('MISSING_CITATION_READING_SCOPE')
    def test_spaces_only_source_scope(self):self.a['articles']['article-0']['citations'][0]['reading_scope_exact']='  \n ';self.expect('MISSING_CITATION_READING_SCOPE')
    def test_wrong_source_blob(self):self.a['articles']['article-0']['citations'][0]['source_variant']['source_blob']='f'*40;self.expect('CITATION_NOT_BOUND_TO_ONE_ORIGINAL_SOURCE_VARIANT')
    def test_wrong_source_branch(self):self.a['articles']['article-0']['citations'][0]['source_variant']['branch']='claude/unknown';self.expect('CITATION_NOT_BOUND_TO_ONE_ORIGINAL_SOURCE_VARIANT')
    def test_wrong_source_url(self):self.a['articles']['article-0']['citations'][0]['source_variant']['url']='https://evil.example';self.expect('CITATION_NOT_BOUND_TO_ONE_ORIGINAL_SOURCE_VARIANT')
    def test_missing_source_variant(self):self.a['articles']['article-0']['citations'][0].pop('source_variant');self.expect('CITATION_NOT_BOUND_TO_ONE_ORIGINAL_SOURCE_VARIANT')
    def test_source_variant_collision(self):v=self.d['all_original_source_id_crosswalk'][0]['variants'][0];self.d['all_original_source_id_crosswalk'][0]['variants']=[v,v];self.expect('CITATION_NOT_BOUND_TO_ONE_ORIGINAL_SOURCE_VARIANT')
    def test_missing_original_variants(self):self.d['all_original_source_id_crosswalk'][0]['variants']=[];self.expect('ORIGINAL_SOURCE_VARIANTS_MISSING')
    def test_fake_approval(self):self.a['articles']['article-0']['citations'][0]['review_state']='QD_PASS';self.expect('PREMATURE_CITATION_REVIEW_CLAIM')
    def test_claim_approval_instead_pending(self):self.a['articles']['article-0']['citations'][0]['review_state']='APPROVED';self.expect('PREMATURE_CITATION_REVIEW_CLAIM')
    def test_unknown_cited_source(self):
        self.b['article-0']=b'<p>Claim {{cite:unknown-id}}</p>'
        self.d['original_articles'][0]['body_candidate_git_blobs']=[g.git_blob(self.b['article-0'])]
        self.expect('CITED_SOURCE_NOT_IN_ORIGINAL_DOCKET:unknown-id')
    def test_non_bytes_body(self):self.b['article-0']='x';self.expect('MISSING_AUTHENTIC_BODY')
    def test_empty_body(self):self.b['article-0']=b'';self.expect('BODY_MISSING_OR_OVERSIZED')
    def test_invalid_utf8(self):self.b['article-0']=b'\xff';self.expect('BODY_NOT_UTF8')
    def test_duplicate_cite_added(self):
        body=self.b['article-0'].replace(b'</p>',b' {{cite:source-0}}</p>')
        self.b['article-0']=body;self.d['original_articles'][0]['body_candidate_git_blobs']=[g.git_blob(body)]
        self.expect('CITATION_OCCURRENCE_COUNT_DRIFT')
    def test_script_cite_hidden(self):
        body=self.b['article-0'].replace(b'</article>',b'<script>{{cite:source-2}}</script></article>')
        self.b['article-0']=body;self.d['original_articles'][0]['body_candidate_git_blobs']=[g.git_blob(body)]
        self.expect('HIDDEN_OR_UNSCOPED_CITATION_MARKER')
    def test_attribute_cite_hidden(self):
        body=self.b['article-0'].replace(b'<article>',b'<article data-note="{{cite:source-2}}">')
        self.b['article-0']=body;self.d['original_articles'][0]['body_candidate_git_blobs']=[g.git_blob(body)]
        self.expect('HIDDEN_OR_UNSCOPED_CITATION_MARKER')
    def test_paragraph_changed_same_source(self):
        body=self.b['article-0'].replace(b'First actionable claim',b'Contradictory claim')
        self.b['article-0']=body;self.d['original_articles'][0]['body_candidate_git_blobs']=[g.git_blob(body)]
        self.a['articles']['article-0']['body_git_blob']=g.git_blob(body)
        self.expect('CITATION_CLAIM_BINDING_CHANGED')
    def test_not_all_sources_same_url(self):
        self.assertNotEqual(self.d['all_original_source_id_crosswalk'][0]['variants'][0]['url'],self.d['all_original_source_id_crosswalk'][1]['variants'][0]['url'])
    def test_stability(self):self.assertEqual(self.report(),g.review_bundle(copy.deepcopy(self.d),copy.deepcopy(self.b),copy.deepcopy(self.a)))
    def test_main_missing_fixture_exit_2(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'x.json';p.write_text('{}')
            v=subprocess.run([sys.executable,str(SRC),'--docket',str(p)],capture_output=True,text=True,timeout=5)
            self.assertEqual(v.returncode,2);self.assertFalse(json.loads(v.stdout)['eligible'])


class Extract(unittest.TestCase):
    def test_plain_paragraph(self):self.assertEqual(len(g.extract_citations(b'<p>Hello {{cite:source-1}}</p>')[0]),1)
    def test_span_inside_paragraph(self):self.assertEqual(len(g.extract_citations(b'<p>Hello <span>{{cite:source-1}}</span></p>')[0]),1)
    def test_script_citation_hidden(self):self.assertIn('HIDDEN_OR_UNSCOPED_CITATION_MARKER',g.extract_citations(b'<script>{{cite:source-1}}</script>')[1])
    def test_style_citation_hidden(self):self.assertIn('HIDDEN_OR_UNSCOPED_CITATION_MARKER',g.extract_citations(b'<style>{{cite:source-1}}</style>')[1])
    def test_attribute_citation_hidden(self):self.assertIn('HIDDEN_OR_UNSCOPED_CITATION_MARKER',g.extract_citations(b'<p data-x="{{cite:source-1}}">Hello</p>')[1])
    def test_not_utf8(self):self.assertIn('BODY_NOT_UTF8',g.extract_citations(b'\xff')[1])
    def test_oversize(self):self.assertIn('BODY_MISSING_OR_OVERSIZED',g.extract_citations(b'x'*(g.MAX_BODY+1))[1])
    def test_empty(self):self.assertIn('BODY_MISSING_OR_OVERSIZED',g.extract_citations(b'')[1])
    def test_two_occurrences_same_id(self):
        r,e=g.extract_citations(b'<p>A {{cite:one}}</p><p>B {{cite:one}}</p>')
        self.assertEqual([x['occurrence'] for x in r],[1,2])
    def test_context_digest_diff(self):
        a=g.extract_citations(b'<p>A {{cite:one}}</p>')[0][0]['context_sha256']
        b=g.extract_citations(b'<p>B {{cite:one}}</p>')[0][0]['context_sha256']
        self.assertNotEqual(a,b)
    def test_normalize_whitespace(self):self.assertEqual(g.normalize(' A\n   B '),'A B')
    def test_determinism(self):self.assertEqual(g.extract_citations(b'<p>A {{cite:one}}</p>'),g.extract_citations(b'<p>A {{cite:one}}</p>'))
    def test_source_variant_none(self):self.assertIsNone(g.variant_key(None))
    def test_source_variant_key(self):self.assertEqual(g.variant_key({'branch':'b','source_blob':'s','url':'u'}),('b','s','u'))

if __name__=='__main__':unittest.main()
