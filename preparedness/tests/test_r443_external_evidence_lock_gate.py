"""R443 synthetic lock/claim/source adversarial tests; NOT QD or real article safety."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TOOLS=Path(__file__).resolve().parents[1]/'tools'
sys.path.insert(0,str(TOOLS))
import r443_external_evidence_lock_gate as g
import r442_claim_source_binding_gate as prior
import r440_original_slate_evidence_replay as replay


def fixture():
    heads={f'claude/prep-{i}':f'{i+1:040x}' for i in range(9)}
    sources=[{'source_id':f'source-{i}', 'variants':[{'branch':'claude/prep-0',
        'source_blob':f'{i+20:040x}','url':f'https://agency.example/record/{i}'}]}
        for i in range(203)]
    articles=[];bodies={};annotations={}
    for i in range(35):
        slug=f'article-{i}';sid=f'source-{i}'
        body=f'<article><h2>Authenticity only</h2><p>Claim {i} {{{{cite:{sid}}}}}</p></article>'.encode()
        bodies[slug]=body
        articles.append({'slug':slug,'body_candidate_git_blobs':[g.blob(body)]})
        cited,ex=prior.extract_citations(body)
        assert not ex
        annotations[slug]={'body_git_blob':g.blob(body),'citations':[{**c,'source_variant':copy.deepcopy(sources[i]['variants'][0]),
            'reading_scope_exact':'Claim-specific source reading scope','review_state':'HUMAN_REVIEW_REQUIRED'} for c in cited]}
    disputes=[]
    for i in range(5):
        disputes.append({'source_id':f'source-{i}','decision':'HUMAN_REVIEW_REQUIRED','selected_record':None,
            'variants':[{'branch':f'claude/prep-{j}','source_blob':f'{30+i+j:040x}',
            'url':f'https://agency.example/dispute/{i}/{j}',
            'supports_exact':'bounded source','reading_scope_notes_exact':'Limited scope'} for j in range(2)]})
    forks=[{'path':f'preparedness/content/articles/article-{i}.body.html',
            'decision':'HUMAN_REVIEW_REQUIRED','selected_sha':None,
            'variants':[{'branch':f'claude/prep-{j}', 'git_blob_sha':f'{i+j+81:040x}', 'byte_length':100} for j in range(2)]}
            for i in range(9)]
    counts={'original_article_count':35,'original_object_paths':77,'original_source_fragments':7,
            'source_record_occurrences':280,'original_distinct_source_ids':203,
            'base_source_records':34,'source_evidence_disputes':5,'unselected_original_forks':9}
    docket={'schema':1,'repo':g.REPO,'issue':136,'parent_conversion_issue':820,
            'provenance':'ORIGINAL_UNSELECTED_GIT_SOURCE_INVENTORY',
            'release_state':g.DRAFT,'publication_approved':False,'qualified_safety_approved':False,
            'merchant_offer_verified':False,'automatic_variant_selection':False,
            'expected':counts,'observed':counts,
            'branch_pins':[{'branch':k,'sha':v} for k,v in heads.items()],
            'original_articles':articles, 'all_original_source_id_crosswalk':sources,
            'source_evidence_disputes':disputes,'original_fork_disputes':forks,
            'shared_exact_url_review_groups':[{'url':f'https://agency.example/shared/{i}',
               'ids':[f'source-{i*2}',f'source-{i*2+1}'],'review_required':True} for i in range(17)]}
    base={'schema':1,'release_state':g.DRAFT,'articles':annotations}
    lock={'schema':1,'repo':g.REPO,'issue':136,'conversion_issue':820,
            'release_state':g.DRAFT,'review_state':'INDEPENDENT_REVIEW_REQUIRED',
            'qd_pass':False,'publishing_allowed':False,'paid_offer_verified':False,
            'docket_sha256':g.sha256(g.canonical_json(docket)),
            'citation_baseline_sha256':g.sha256(g.canonical_json(base)),
            'contributor_heads':heads,
            'articles':{s:{'body_git_blob':g.blob(data),'body_sha256':g.sha256(data),'byte_length':len(data),
                'citation_annotation_sha256':g.sha256(g.canonical_json(annotations[s]))} for s,data in bodies.items()}}
    return docket,base,lock,heads,bodies


class LockTests(unittest.TestCase):
    def setUp(self):
        self.d,self.a,self.lock,self.heads,self.b=fixture()
        self.pin=None;self.raw=None
    def report(self):
        raw=self.raw if self.raw is not None else g.canonical_json(self.lock)
        pin=self.pin if self.pin is not None else g.sha256(raw)
        return g.inspect_lock(self.d,self.a,self.lock,pin,raw,self.heads,self.b)
    def has(self,expected):
        self.assertTrue(any(expected in x for x in self.report()['errors']),self.report()['errors'])
    def test_synthetic_baseline_has_zero_errors(self):self.assertEqual(self.report()['errors'],[])
    def test_fixture_original_articles_35(self):self.assertEqual(len(self.d['original_articles']),35)
    def test_fixture_original_sources_203(self):self.assertEqual(len(self.d['all_original_source_id_crosswalk']),203)
    def test_fixture_disputes_5(self):self.assertEqual(len(self.d['source_evidence_disputes']),5)
    def test_fixture_forks_9(self):self.assertEqual(len(self.d['original_fork_disputes']),9)
    def test_fixture_shared_urls_17(self):self.assertEqual(len(self.d['shared_exact_url_review_groups']),17)
    def test_fixture_branch_heads_9(self):self.assertEqual(len(self.heads),9)
    def test_fixture_r440_passes(self):self.assertEqual(replay.inspect_docket(self.d,self.heads),[])
    def test_fixture_r442_passes(self):self.assertEqual(prior.review_bundle(self.d,self.b,self.a)['errors'],[])
    def test_release_status_held(self):self.assertEqual(self.report()['release_state'],g.DRAFT)
    def test_never_eligible(self):self.assertIs(self.report()['eligible'],False)
    def test_never_qualified_pass(self):self.assertIs(self.report()['qd_pass'],False)
    def test_never_published(self):self.assertIs(self.report()['publishing_allowed'],False)
    def test_never_paid_offer_verified(self):self.assertIs(self.report()['paid_offer_verified'],False)
    def test_exact_article_count(self):self.assertEqual(self.report()['articles_examined'],35)
    def test_independence_warning(self):self.assertIn('INDEPENDENT_REVIEW_OF_LOCK_ORIGIN_REQUIRED',self.report()['blockers'])
    def test_qualified_safety_block(self):self.assertIn('QUALIFIED_FOOD_MEDICAL_EMERGENCY_PRIVACY_QD_REVIEW_REQUIRED',self.report()['blockers'])
    def test_native_build_block(self):self.assertIn('FULL_NATIVE_BUILD_AND_AUTHENTIC_WORDPRESS_EXPORTS_REQUIRED',self.report()['blockers'])
    def test_docket_bytes_mismatch(self):self.d['new']='tampered';self.has('LOCK_DIGEST_DRIFT:docket_sha256')
    def test_baseline_bytes_mismatch(self):self.a['new']='tampered';self.has('LOCK_DIGEST_DRIFT:citation_baseline_sha256')
    def test_expected_pin_invalid(self):self.pin='abc';self.has('INDEPENDENT_LOCK_DIGEST_PIN_MISSING')
    def test_expected_pin_missing(self):self.pin='';self.has('INDEPENDENT_LOCK_DIGEST_PIN_MISSING')
    def test_expected_pin_mismatch(self):self.pin='f'*64;self.has('EXTERNAL_LOCK_DIGEST_MISMATCH')
    def test_external_lock_no_bytes(self):self.raw=b'';self.has('RAW_EXTERNAL_LOCK_BYTES_REQUIRED')
    def test_external_lock_inconsistent_raw(self):self.raw=b'{}';self.pin=g.sha256(g.canonical_json(self.lock));self.has('EXTERNAL_LOCK_DIGEST_MISMATCH')
    def test_lock_bytes_object_mismatch(self):self.raw=b'{}';self.pin=g.sha256(self.raw);self.has('RAW_LOCK_NOT_CANONICAL_OR_OBJECT_MISMATCH')
    def test_lock_whitespace_not_canonical(self):self.raw=b'  '+g.canonical_json(self.lock);self.pin=g.sha256(self.raw);self.has('RAW_LOCK_NOT_CANONICAL_OR_OBJECT_MISMATCH')
    def test_duplicate_json_key_rejected(self):e=[];g.safe_parse(b'{"x":1,"x":2}','X',e);self.assertIn('X_MALFORMED_JSON',e)
    def test_lock_wrong_repo(self):self.lock['repo']='some/other';self.has('LOCK_OWNER_SCHEMA_OR_ISSUE_DRIFT')
    def test_lock_wrong_issue(self):self.lock['issue']=999;self.has('LOCK_OWNER_SCHEMA_OR_ISSUE_DRIFT')
    def test_lock_wrong_conversion_issue(self):self.lock['conversion_issue']=999;self.has('LOCK_OWNER_SCHEMA_OR_ISSUE_DRIFT')
    def test_lock_schema_changed(self):self.lock['schema']=2;self.has('LOCK_OWNER_SCHEMA_OR_ISSUE_DRIFT')
    def test_lock_claims_pass(self):self.lock['qd_pass']=True;self.has('LOCK_CLAIMS_UNAPPROVED_PERMISSION')
    def test_lock_claims_published(self):self.lock['publishing_allowed']=True;self.has('LOCK_CLAIMS_UNAPPROVED_PERMISSION')
    def test_lock_claims_paid(self):self.lock['paid_offer_verified']=True;self.has('LOCK_CLAIMS_UNAPPROVED_PERMISSION')
    def test_lock_claims_approved(self):self.lock['review_state']='APPROVED';self.has('LOCK_PREMATURE_REVIEW_OR_RELEASE_STATE')
    def test_lock_claims_live(self):self.lock['release_state']='LIVE';self.has('LOCK_PREMATURE_REVIEW_OR_RELEASE_STATE')
    def test_lock_docket_digest_invalid(self):self.lock['docket_sha256']='xyz';self.has('LOCK_DIGEST_MISSING:docket_sha256')
    def test_lock_baseline_digest_invalid(self):self.lock['citation_baseline_sha256']='xyz';self.has('LOCK_DIGEST_MISSING:citation_baseline_sha256')
    def test_lock_source_sha_wrong(self):self.lock['docket_sha256']='f'*64;self.has('LOCK_DIGEST_DRIFT:docket_sha256')
    def test_lock_annotation_sha_wrong(self):self.lock['citation_baseline_sha256']='f'*64;self.has('LOCK_DIGEST_DRIFT:citation_baseline_sha256')
    def test_missing_heads(self):self.heads=None;self.has('INDEPENDENT_NINE_CONTRIBUTOR_HEAD_OBSERVATIONS_MISSING')
    def test_head_changed(self):self.heads['claude/prep-0']='f'*40;self.has('CURRENT_CONTRIBUTOR_HEADS_NOT_AT_ORIGINAL_PINS')
    def test_head_extra(self):self.heads['unexpected']='a'*40;self.has('CURRENT_CONTRIBUTOR_HEADS_NOT_AT_ORIGINAL_PINS')
    def test_missing_head(self):self.heads.pop('claude/prep-0');self.has('CURRENT_CONTRIBUTOR_HEADS_NOT_AT_ORIGINAL_PINS')
    def test_lock_head_changed(self):self.lock['contributor_heads']['claude/prep-0']='f'*40;self.has('EXTERNAL_LOCK_BRANCH_MAP_DRIFT')
    def test_lock_missing_head(self):self.lock['contributor_heads'].pop('claude/prep-0');self.has('EXTERNAL_LOCK_BRANCH_MAP_DRIFT')
    def test_missing_bodies(self):self.b=None;self.has('AUTHENTIC_ORIGINAL_ARTICLE_BYTES_MISSING')
    def test_missing_body(self):self.b.pop('article-0');self.has('AUTHENTIC_ARTICLE_SET_NOT_EXACTLY_ORIGINAL_35')
    def test_extra_body(self):self.b['extra']=b'x';self.has('AUTHENTIC_ARTICLE_SET_NOT_EXACTLY_ORIGINAL_35')
    def test_changed_body(self):self.b['article-0']+=b'changed';self.has('ORIGINAL_BODY_EXTERNAL_LOCK_MISMATCH:article-0')
    def test_changed_body_but_updated_lock(self):
        self.b['article-0']+=b'changed'; raw=self.b['article-0'];row=self.lock['articles']['article-0']
        row['body_sha256']=g.sha256(raw);row['body_git_blob']=g.blob(raw);row['byte_length']=len(raw)
        self.has('BODY_NOT_ORIGINAL_GIT_CANDIDATE:article-0')
    def test_body_wrong_type(self):self.b['article-0']='x';self.has('ORIGINAL_BODY_BYTES_MISSING_OR_OVERSIZED:article-0')
    def test_body_empty(self):self.b['article-0']=b'';self.has('ORIGINAL_BODY_BYTES_MISSING_OR_OVERSIZED:article-0')
    def test_body_oversized(self):self.b['article-0']=b'X'*2000001;self.has('ORIGINAL_BODY_BYTES_MISSING_OR_OVERSIZED:article-0')
    def test_body_lock_wrong_length(self):self.lock['articles']['article-0']['byte_length']=99;self.has('ORIGINAL_BODY_EXTERNAL_LOCK_MISMATCH:article-0')
    def test_body_lock_wrong_sha(self):self.lock['articles']['article-0']['body_sha256']='f'*64;self.has('ORIGINAL_BODY_EXTERNAL_LOCK_MISMATCH:article-0')
    def test_body_lock_wrong_git_blob(self):self.lock['articles']['article-0']['body_git_blob']='f'*40;self.has('ORIGINAL_BODY_EXTERNAL_LOCK_MISMATCH:article-0')
    def test_missing_article_lock(self):self.lock['articles'].pop('article-0');self.has('ARTICLE_LOCK_SET_NOT_EXACTLY_ORIGINAL_35')
    def test_extra_article_lock(self):self.lock['articles']['stranger']={};self.has('ARTICLE_LOCK_SET_NOT_EXACTLY_ORIGINAL_35')
    def test_lock_row_not_object(self):self.lock['articles']['article-0']=None;self.has('ARTICLE_LOCK_ROW_MISSING:article-0')
    def test_lock_row_missing_source_digest(self):self.lock['articles']['article-0'].pop('citation_annotation_sha256');self.has('ANNOTATION_EXTERNAL_LOCK_MISMATCH:article-0')
    def test_lock_annotation_hash_changed(self):self.lock['articles']['article-0']['citation_annotation_sha256']='0'*64;self.has('ANNOTATION_EXTERNAL_LOCK_MISMATCH:article-0')
    def test_annotation_body_ref_changed(self):self.a['articles']['article-0']['body_git_blob']='0'*40;self.has('ANNOTATION_BODY_GIT_IDENTITY_MISMATCH:article-0')
    def test_annotation_claim_changed(self):self.a['articles']['article-0']['citations'][0]['reading_scope_exact']='wrong';self.has('ANNOTATION_EXTERNAL_LOCK_MISMATCH:article-0')
    def test_missing_citation_annotation_article(self):self.a['articles'].pop('article-0');self.has('ANNOTATION_ARTICLE_SET_NOT_EXACTLY_ORIGINAL_35')
    def test_extra_citation_annotation_article(self):self.a['articles']['stranger']={};self.has('ANNOTATION_ARTICLE_SET_NOT_EXACTLY_ORIGINAL_35')
    def test_original_article_removed(self):self.d['original_articles'].pop();self.has('THIRTY_FIVE_ARTICLE_IDENTITIES_REQUIRED')
    def test_original_article_collision(self):self.d['original_articles'][1]['slug']='article-0';self.has('ARTICLE_ORIGINAL_IDENTITY_COLLISION')
    def test_original_article_candidate_mutation(self):self.d['original_articles'][0]['body_candidate_git_blobs']=['f'*40];self.has('BODY_NOT_ORIGINAL_GIT_CANDIDATE:article-0')
    def test_r442_source_variant_changed(self):
        self.a['articles']['article-0']['citations'][0]['source_variant']['url']='https://malicious.example'
        self.has('R442:CITATION_NOT_BOUND_TO_ONE_ORIGINAL_SOURCE_VARIANT')
    def test_r442_missing_scope(self):
        self.a['articles']['article-0']['citations'][0]['reading_scope_exact']=''
        self.has('R442:MISSING_CITATION_READING_SCOPE')
    def test_r440_premature_fork(self):
        self.d['original_fork_disputes'][0]['selected_sha']='f'*40
        self.has('R440:PREMATURE_FORK_SELECTION')
    def test_r440_premature_source(self):
        self.d['source_evidence_disputes'][0]['selected_record']={'chosen':True}
        self.has('R440:PREMATURE_SOURCE_ADJUDICATION')
    def test_r440_duplicate_urls_group(self):
        self.d['shared_exact_url_review_groups'][1]['url']=self.d['shared_exact_url_review_groups'][0]['url']
        self.has('R440:SHARED_URL_GROUP_COLLISION')
    def test_r440_changed_reading_depth(self):
        self.d['source_evidence_disputes'][0]['variants'][0]['reading_scope_notes_exact']=''
        self.has('R440:INCOMPLETE_SOURCE_SUPPORT_AND_READING_SCOPE')
    def test_deterministic(self):self.assertEqual(self.report(),self.report())
    def test_safe_parse_valid(self):self.assertEqual(g.safe_parse(b'{"x":1}','X',[]),{'x':1})
    def test_safe_parse_non_object(self):e=[];self.assertEqual(g.safe_parse(b'[]','X',e),{});self.assertIn('X_NOT_OBJECT',e)
    def test_safe_parse_invalid_utf8(self):e=[];g.safe_parse(b'\xff','X',e);self.assertIn('X_MALFORMED_JSON',e)
    def test_safe_parse_empty(self):e=[];g.safe_parse(b'','X',e);self.assertIn('X_BYTES_MISSING_OR_OVERSIZED',e)
    def test_safe_parse_nan(self):e=[];g.safe_parse(b'{"x":NaN}','X',e);self.assertIn('X_MALFORMED_JSON',e)
    def test_safe_parse_big(self):e=[];g.safe_parse(b'x'*(g.MAX_JSON+1),'X',e);self.assertIn('X_BYTES_MISSING_OR_OVERSIZED',e)
    def test_canonical_key_order(self):self.assertEqual(g.canonical_json({'b':2,'a':1}),g.canonical_json({'a':1,'b':2}))
    def test_git_blob_distinct(self):self.assertNotEqual(g.blob(b'A'),g.blob(b'B'))
    def test_cli_missing_evidence_exit_2(self):
        with tempfile.TemporaryDirectory() as td:
            td=Path(td)
            for name in ['d','a','l','h']:(td/name).write_text('{}')
            p=subprocess.run([sys.executable,str(TOOLS/'r443_external_evidence_lock_gate.py'),
                '--docket',str(td/'d'),'--frozen-citation-baseline',str(td/'a'),
                '--external-lock',str(td/'l'),'--observed-contributor-heads',str(td/'h'),
                '--expected-lock-sha256','0'*64,'--repo-root',str(td)],text=True,capture_output=True,timeout=5)
            self.assertEqual(p.returncode,2)
            report=json.loads(p.stdout)
            self.assertFalse(report['eligible']);self.assertFalse(report['qd_pass'])
            self.assertIn('THIRTY_FIVE_ARTICLE_IDENTITIES_REQUIRED',report['errors'])

if __name__=='__main__':unittest.main()
