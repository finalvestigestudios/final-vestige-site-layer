"""R440 synthetic custody tests: never grant release/medical safety/merchant approval."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SRC=Path(__file__).resolve().parents[1]/'tools'/'r440_original_slate_evidence_replay.py'
sp=importlib.util.spec_from_file_location('r440',SRC)
g=importlib.util.module_from_spec(sp);sp.loader.exec_module(g)

def fake_docket():
    p=[{'branch':f'claude/prep-{i}','sha':f'{i+1:040x}'} for i in range(9)]
    src=[{'source_id':f'source-{i}','variants':[{'branch':p[0]['branch'],'source_blob':'1'*40,'url':f'https://agency.example/{i}'}]} for i in range(203)]
    a=[{'slug':f'article-{i}','body_candidate_git_blobs':['2'*40]} for i in range(35)]
    disputes=[{'source_id':f'source-{i}','decision':'HUMAN_REVIEW_REQUIRED','selected_record':None,
               'variants':[{'branch':p[j]['branch'],'source_blob':'3'*40,'url':f'https://agency.example/{i}',
                            'supports_exact':'Scoped, original readable evidence','reading_scope_notes_exact':'Original page read only'} for j in (0,1)]}
              for i in range(5)]
    forks=[{'path':f'preparedness/content/articles/article-{i}.body.html','decision':'HUMAN_REVIEW_REQUIRED',
            'selected_sha':None,'variants':[{'branch':p[j]['branch'],'git_blob_sha':f'{j+4:040x}',
                                            'byte_length':123+j} for j in (0,1)]} for i in range(9)]
    groups=[{'url':f'https://agency.example/shared-{i}','ids':[f'source-{2*i}',f'source-{2*i+1}'],'review_required':True} for i in range(17)]
    return {'schema':1,'provenance':'ORIGINAL_UNSELECTED_GIT_SOURCE_INVENTORY',
            'repo':'finalvestigestudios/final-vestige-site-layer','issue':136,'parent_conversion_issue':820,
            'expected':copy.deepcopy(g.COUNTS),'observed':copy.deepcopy(g.COUNTS),
            'release_state':'DRAFT_HARD_HOLD','publication_approved':False,
            'qualified_safety_approved':False,'merchant_offer_verified':False,'automatic_variant_selection':False,
            'branch_pins':p,'original_articles':a,'source_evidence_disputes':disputes,
            'original_fork_disputes':forks,'all_original_source_id_crosswalk':src,
            'shared_exact_url_review_groups':groups}

def heads(d):return {x['branch']:x['sha'] for x in d['branch_pins']}

class Contract(unittest.TestCase):
    def setUp(self):self.d=fake_docket()
    def check(self, code):self.assertIn(code,g.inspect_docket(self.d))
    def test_clean_synthetic_contract(self):self.assertEqual([],g.inspect_docket(self.d,heads(self.d)))
    def test_missing_checkout_is_hold(self):self.assertIn('AUTHENTIC_CHECKOUT_NOT_PROVIDED',g.audit(self.d)['errors'])
    def test_missing_live_shas_is_hold(self):self.assertIn('LIVE_CONTRIBUTOR_SHAS_NOT_ATTESTED_IN_THIS_EXECUTION',g.audit(self.d)['errors'])
    def test_always_draft(self):self.assertEqual(g.audit(self.d)['release_state'],'DRAFT_HARD_HOLD')
    def test_never_eligible(self):self.assertIs(g.audit(self.d)['eligible'],False)
    def test_never_publish_approved(self):self.assertIs(g.audit(self.d)['publication_approved'],False)
    def test_never_safety_approved(self):self.assertIs(g.audit(self.d)['qualified_safety_approved'],False)
    def test_never_offer_verified(self):self.assertIs(g.audit(self.d)['merchant_offer_verified'],False)
    def test_never_select_forks(self):self.assertIs(g.audit(self.d)['automatic_fork_selection'],False)
    def test_no_native_build_claim(self):self.assertIs(g.audit(self.d)['native_build_executed'],False)
    def test_invalid_docket(self):self.assertIn('INVALID_R397_DOCKET_SCHEMA',g.inspect_docket({}))
    def test_not_list(self):self.assertIn('INVALID_R397_DOCKET_SCHEMA',g.inspect_docket(None))
    def test_wrong_owner(self):self.d['repo']='other/repo';self.check('DOCKET_OWNER_OR_ISSUE_DRIFT')
    def test_wrong_issue(self):self.d['issue']=137;self.check('DOCKET_OWNER_OR_ISSUE_DRIFT')
    def test_wrong_business_issue(self):self.d['parent_conversion_issue']=999;self.check('DOCKET_OWNER_OR_ISSUE_DRIFT')
    def test_true_publish(self):self.d['publication_approved']=True;self.check('UNSAFE_RELEASE_OR_SELECTION_STATE:publication_approved')
    def test_true_safety(self):self.d['qualified_safety_approved']=True;self.check('UNSAFE_RELEASE_OR_SELECTION_STATE:qualified_safety_approved')
    def test_true_merchant(self):self.d['merchant_offer_verified']=True;self.check('UNSAFE_RELEASE_OR_SELECTION_STATE:merchant_offer_verified')
    def test_auto_variant(self):self.d['automatic_variant_selection']=True;self.check('UNSAFE_RELEASE_OR_SELECTION_STATE:automatic_variant_selection')
    def test_release_state(self):self.d['release_state']='QD_PASS';self.check('UNSAFE_RELEASE_STATE')
    def test_branch_count(self):self.d['branch_pins'].pop();self.check('INVALID_NINE_BRANCH_PINS')
    def test_branch_duplicate(self):self.d['branch_pins'][1]['branch']=self.d['branch_pins'][0]['branch'];self.check('DUPLICATE_BRANCH')
    def test_branch_wrong_namespace(self):self.d['branch_pins'][0]['branch']='production';self.check('UNEXPECTED_BRANCH_NAMESPACE')
    def test_branch_bad_sha(self):self.d['branch_pins'][0]['sha']='garbage';self.check('INVALID_BRANCH_PIN')
    def test_branch_missing_head(self):self.assertTrue(any(x.startswith('UNVERIFIED_OR_DRIFTED_CONTRIBUTOR_HEAD') for x in g.inspect_docket(self.d,{})))
    def test_branch_extra_head(self):h=heads(self.d);h['extra']='x';self.assertIn('BRANCH_HEAD_SET_MISMATCH',g.inspect_docket(self.d,h))
    def test_article_missing(self):self.d['original_articles'].pop();self.check('INVALID_ORIGINAL_ARTICLE_LIST')
    def test_article_duplicate(self):self.d['original_articles'][1]['slug']='article-0';self.check('DUPLICATE_ORIGINAL_ARTICLE_SLUG')
    def test_article_slug_traversal(self):self.d['original_articles'][0]['slug']='../x';self.check('INVALID_ORIGINAL_ARTICLE_SLUG')
    def test_article_sha_missing(self):self.d['original_articles'][0]['body_candidate_git_blobs']=[];self.check('INVALID_ORIGINAL_BODY_OBJECTS:article-0')
    def test_article_sha_duplicate(self):self.d['original_articles'][0]['body_candidate_git_blobs']=['2'*40]*2;self.check('INVALID_ORIGINAL_BODY_OBJECTS:article-0')
    def test_source_dispute_count(self):self.d['source_evidence_disputes'].pop();self.check('FIVE_SOURCE_DISPUTES_CHANGED')
    def test_source_decision_unreviewed(self):self.d['source_evidence_disputes'][0]['decision']='PASS';self.check('PREMATURE_SOURCE_ADJUDICATION')
    def test_source_auto_selection(self):self.d['source_evidence_disputes'][0]['selected_record']='x';self.check('PREMATURE_SOURCE_ADJUDICATION')
    def test_source_variant_missing(self):self.d['source_evidence_disputes'][0]['variants'].pop();self.check('MISSING_SOURCE_VARIANTS')
    def test_source_reading_scope_missing(self):self.d['source_evidence_disputes'][0]['variants'][0]['reading_scope_notes_exact']='';self.check('INCOMPLETE_SOURCE_SUPPORT_AND_READING_SCOPE')
    def test_source_support_missing(self):self.d['source_evidence_disputes'][0]['variants'][0]['supports_exact']='';self.check('INCOMPLETE_SOURCE_SUPPORT_AND_READING_SCOPE')
    def test_source_duplicate(self):self.d['source_evidence_disputes'][0]['source_id']='source-1';self.check('DUPLICATE_SOURCE_DISPUTE')
    def test_forks_count(self):self.d['original_fork_disputes'].pop();self.check('NINE_FORKS_CHANGED')
    def test_fork_selected(self):self.d['original_fork_disputes'][0]['selected_sha']='c'*40;self.check('PREMATURE_FORK_SELECTION')
    def test_fork_missing_variant(self):self.d['original_fork_disputes'][0]['variants'].pop();self.check('MISSING_FORK_CANDIDATES')
    def test_fork_zero_length(self):self.d['original_fork_disputes'][0]['variants'][0]['byte_length']=0;self.check('INVALID_FORK_CANDIDATE')
    def test_fork_bool_length(self):self.d['original_fork_disputes'][0]['variants'][0]['byte_length']=True;self.check('INVALID_FORK_CANDIDATE')
    def test_fork_duplicate_path(self):self.d['original_fork_disputes'][1]['path']=self.d['original_fork_disputes'][0]['path'];self.check('DUPLICATE_FORK_PATH')
    def test_fork_outside_path(self):self.d['original_fork_disputes'][0]['path']='other/foo';self.check('UNSAFE_FORK_PATH')
    def test_fork_traversal(self):self.d['original_fork_disputes'][0]['path']='preparedness/content/articles/../../secret';self.check('UNSAFE_FORK_PATH')
    def test_source_ids_count(self):self.d['all_original_source_id_crosswalk'].pop();self.check('SOURCE_ID_CROSSWALK_COUNT_CHANGED')
    def test_source_ids_collision(self):self.d['all_original_source_id_crosswalk'][0]['source_id']='source-1';self.check('SOURCE_ID_LOSS_OR_COLLISION')
    def test_source_id_invalid(self):self.d['all_original_source_id_crosswalk'][0]['source_id']='SOURCE:1';self.check('SOURCE_ID_LOSS_OR_COLLISION')
    def test_shared_groups_count(self):self.d['shared_exact_url_review_groups'].pop();self.check('SHARED_URL_GROUPS_CHANGED')
    def test_shared_group_duplicate(self):self.d['shared_exact_url_review_groups'][0]['ids']=['source-1','source-1'];self.check('SHARED_URL_SCOPE_OR_REVIEW_LOST')
    def test_shared_group_outside_source(self):self.d['shared_exact_url_review_groups'][0]['ids']=['source-1','not-registered'];self.check('SHARED_URL_SCOPE_OR_REVIEW_LOST')
    def test_shared_group_approval_leak(self):self.d['shared_exact_url_review_groups'][0]['review_required']=False;self.check('SHARED_URL_SCOPE_OR_REVIEW_LOST')
    def test_shared_url_collision(self):self.d['shared_exact_url_review_groups'][0]['url']=self.d['shared_exact_url_review_groups'][1]['url'];self.check('SHARED_URL_GROUP_COLLISION')
    def test_count_bool_is_not_int(self):self.d['expected']['original_article_count']=True;self.check('FROZEN_COUNT_DRIFT:original_article_count')
    def test_count_loss(self):self.d['observed']['source_record_occurrences']=279;self.check('FROZEN_COUNT_DRIFT:source_record_occurrences')
    def test_result_determinism(self):self.assertEqual(g.audit(self.d),g.audit(copy.deepcopy(self.d)))

class FileCustody(unittest.TestCase):
    def setUp(self):self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name)
    def write(self,name,data):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);return p
    def test_git_sha_matches(self):self.assertEqual(g.git_blob_sha(b'hello'),'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_ordinary_read(self):self.write('preparedness/a.txt',b'data');self.assertEqual(g.bounded_read(self.root,'preparedness/a.txt'),b'data')
    def test_traversal(self):self.assertRaises(ValueError,g.bounded_read,self.root,'preparedness/../escape')
    def test_absolute(self):self.assertRaises(ValueError,g.bounded_read,self.root,'/etc/passwd')
    def test_other_root(self):self.assertRaises(ValueError,g.bounded_read,self.root,'other/foo')
    def test_backslash(self):self.assertRaises(ValueError,g.bounded_read,self.root,r'preparedness\foo')
    def test_empty_file(self):self.write('preparedness/empty',b'');self.assertRaises(ValueError,g.bounded_read,self.root,'preparedness/empty')
    def test_symlink(self):
        p=self.write('preparedness/file',b'secret'); (p.parent/'alias').symlink_to(p)
        self.assertRaises((ValueError,OSError),g.bounded_read,self.root,'preparedness/alias')
    def test_hardlink(self):
        p=self.write('preparedness/file',b'x');os.link(p,p.parent/'alias')
        self.assertRaises((ValueError,OSError),g.bounded_read,self.root,'preparedness/alias')
    def test_oversize(self):self.write('preparedness/file',b'x'*(g.MAX_FILE+1));self.assertRaises(ValueError,g.bounded_read,self.root,'preparedness/file')
    def test_missing_file(self):self.assertRaises(OSError,g.bounded_read,self.root,'preparedness/nope')
    def test_single_original_object_reads(self):
        d=fake_docket();body=b'<p>Read {{cite:source-0}} before action.</p>';slug='article-0'
        self.write(f'preparedness/content/articles/{slug}.body.html',body)
        self.write(f'preparedness/content/articles/{slug}.meta.json',json.dumps({'slug':slug,'n':1,'status':{'publish':'draft'},'safety_review':{'state':'pending'},'source_use':{'source-0':'page read'}}).encode())
        d['original_articles'][0]['body_candidate_git_blobs']=[g.git_blob_sha(body)]
        report=g.inspect_checkout(d,self.root)
        self.assertEqual(report['articles_read'],1)
        self.assertEqual(report['citation_occurrences_in_checkout'],1)
        self.assertTrue(any('MISSING_OR_UNSAFE_ARTICLE_OBJECTS' in x for x in report['errors']))
    def test_missing_authentic_evidence_cli(self):
        p=subprocess.run([sys.executable,'-I',str(SRC),str(self.root/'missing.json')],capture_output=True,text=True)
        self.assertEqual(p.returncode,2)
        self.assertEqual(json.loads(p.stdout)['release_state'],'DRAFT_HARD_HOLD')

if __name__=='__main__':unittest.main()
