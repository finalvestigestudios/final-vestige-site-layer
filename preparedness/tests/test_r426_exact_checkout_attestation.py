"""R426 exact-commit attestation synthetic tests: NO safety/checkout/CI approval."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import r426_exact_checkout_attestation as gate


def cmd(repo,*args):
    p=subprocess.run(['git','-C',str(repo),*args],check=True,capture_output=True)
    return p.stdout.strip().decode()


def base():
    root=Path(tempfile.mkdtemp(prefix='fv-r426-base-'))
    cmd(root,'init','-q');cmd(root,'config','user.name','FV fixture');cmd(root,'config','user.email','fixture@example.invalid')
    for path in gate.FILES:
        p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('TEST ONLY '+path+'\n')
    cmd(root,'add','.');cmd(root,'commit','-qm','synthetic only')
    sha=cmd(root,'rev-parse','HEAD')
    pins=[]
    for i in range(9):
        branch=f'review/preparedness-cluster-{i:02d}'
        cmd(root,'branch',branch,sha)
        pins.append({'branch':branch,'sha':sha})
    docket={'schema':1,'issue':136,'release_state':'DRAFT_HARD_HOLD',
            'publication_approved':False,'qualified_safety_approved':False,
            'original_articles':[{'slug':f'article-{n:02d}'} for n in range(1,36)],
            'branch_pins':pins}
    raw=json.dumps(docket,sort_keys=True,separators=(',',':')).encode()
    rows=[]
    for path in gate.FILES:
        b=(root/path).read_bytes()
        rows.append({'path':path,'git_blob':gate.gitblob(b),'tested_sha256':hashlib.sha256(b).hexdigest()})
    receipt={'schema':1,'issue':136,'release_state':'DRAFT_HARD_HOLD','approved':False,
             'head_sha':sha,'files':rows}
    return root,raw,receipt,sha


class ExactGitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source,cls.docket,cls.receipt,cls.head=base()
        cls.pin=gate.gitblob(cls.docket)
    @classmethod
    def tearDownClass(cls):shutil.rmtree(cls.source)
    def setUp(self):
        self.root=Path(tempfile.mkdtemp(prefix='fv-r426-case-'))
        self.repo=self.root/'repo';shutil.copytree(self.source,self.repo)
        self.docket_raw=self.docket
        self.r=copy.deepcopy(self.receipt)
    def tearDown(self):shutil.rmtree(self.root)
    def run_gate(self):return gate.check(self.repo,self.docket_raw,self.r,expected_head=self.head,expected_pin=self.pin)
    def has(self,key):
        r=self.run_gate()
        self.assertFalse(r['exact_code_and_test_checkout_attested']);self.assertFalse(r['eligible'])
        self.assertTrue(any(key in x for x in r['errors']),r)

    def test_baseline_git_identity_not_release_approval(self):
        x=self.run_gate();self.assertTrue(x['exact_code_and_test_checkout_attested'],x)
        self.assertFalse(x['eligible']);self.assertFalse(x['publication_approved']);self.assertFalse(x['qualified_safety_approved'])
        self.assertFalse(x['tests_executed_by_this_gate'])
    def test_deterministic_receipt(self):self.assertEqual(self.run_gate(),self.run_gate())
    def test_no_mutation(self):
        before=cmd(self.repo,'status','--porcelain');self.run_gate();self.assertEqual(before,cmd(self.repo,'status','--porcelain'))
    def test_head_is_full_40_digit_sha(self):self.assertEqual(len(self.head),40)
    def test_expected_real_docket_pin_constant(self):self.assertEqual(gate.PIN,'86d22a1d504c93db7689b914e2202a7845b648e2')
    def test_default_real_pin_rejects_synthetics(self):
        self.assertIn('R426_DOCKET_GIT_BLOB_MISMATCH',gate.check(self.repo,self.docket_raw,self.r,expected_head=self.head)['errors'])
    def test_default_real_head_rejects_synthetics(self):
        self.assertIn('R426_RECEIPT_IDENTITY_OR_HEAD_MISMATCH',gate.check(self.repo,self.docket_raw,self.r,expected_pin=self.pin)['errors'])
    def test_dirty_tracked_file_rejected(self):
        (self.repo/gate.FILES[0]).write_text('changed');self.has('DIRTY_TRACKED_WORKTREE')
    def test_symlink_file_rejected(self):
        p=self.repo/gate.FILES[0];p.unlink();p.symlink_to(self.repo/gate.FILES[1]);self.has('FILE_UNAVAILABLE')
    def test_missing_file_rejected(self):
        (self.repo/gate.FILES[1]).unlink();self.has('FILE_UNAVAILABLE')
    def test_unavailable_git_repo(self):
        shutil.rmtree(self.repo/'.git');self.has('GIT_WORKTREE_UNAVAILABLE')
    def test_changed_branch_pointer(self):
        cmd(self.repo,'update-ref','-d','refs/heads/review/preparedness-cluster-01');self.has('BRANCH_UNAVAILABLE')
    def test_checkout_not_exact_head(self):
        cmd(self.repo,'commit','--allow-empty','-qm','new SHA');self.has('CHECKOUT_HEAD_NOT_PR_HEAD')
    def test_file_sha256_replacement(self):
        self.r['files'][0]['tested_sha256']='a'*64;self.has('EXECUTED_BYTES_NOT_COMMITTED')
    def test_file_git_blob_replacement(self):
        self.r['files'][0]['git_blob']='a'*40;self.has('CHECKOUT_VERSUS_TREE_BLOB_DRIFT')
    def test_docket_not_utf8(self):self.docket_raw=b'\xff';self.has('INVALID_DOCKET')
    def test_cli_always_hard_hold(self):
        (self.root/'docket.json').write_bytes(self.docket_raw)
        (self.root/'receipt.json').write_text(json.dumps(self.r))
        path=Path(gate.__file__)
        p=subprocess.run([sys.executable,'-I',str(path),str(self.repo),str(self.root/'docket.json'),str(self.root/'receipt.json')],capture_output=True,text=True)
        self.assertEqual(p.returncode,2,p.stderr);self.assertFalse(json.loads(p.stdout)['eligible'])


def modify(key,mutator):
    def test(self):
        mutator(self);self.has(key)
    return test

MUTATIONS={
 'docket_wrong_issue':('DOCKET_IDENTITY_OR_APPROVAL_DRIFT',lambda t:t.set_docket('issue',820)),
 'docket_wrong_schema':('DOCKET_IDENTITY_OR_APPROVAL_DRIFT',lambda t:t.set_docket('schema',2)),
 'docket_no_approval_flag':('DOCKET_IDENTITY_OR_APPROVAL_DRIFT',lambda t:t.del_docket('publication_approved')),
 'docket_fake_safety':('DOCKET_IDENTITY_OR_APPROVAL_DRIFT',lambda t:t.set_docket('qualified_safety_approved',True)),
 'docket_fake_live':('DOCKET_IDENTITY_OR_APPROVAL_DRIFT',lambda t:t.set_docket('release_state','LIVE')),
 'docket_one_article_missing':('THIRTY_FIVE_ARTICLES_REQUIRED',lambda t:t.pop_docket('original_articles')),
 'docket_one_branch_missing':('NINE_BRANCH_PINS_REQUIRED',lambda t:t.pop_docket('branch_pins')),
 'docket_duplicate_branch':('NINE_BRANCH_PINS_REQUIRED',lambda t:t.dupe_docket_branch()),
 'docket_invalid_branch_sha':('NINE_BRANCH_PINS_REQUIRED',lambda t:t.set_docket_pin(0,'sha','notsha')),
 'docket_wrong_branch_commit':('BRANCH_SHA_MISMATCH',lambda t:t.set_docket_pin(0,'sha','b'*40)),
 'docket_missing_branch_name':('NINE_BRANCH_PINS_REQUIRED',lambda t:t.set_docket_pin(0,'branch',None)),
 'receipt_schema_2':('RECEIPT_IDENTITY_OR_HEAD_MISMATCH',lambda t:t.r.update(schema=2)),
 'receipt_schema_bool':('RECEIPT_IDENTITY_OR_HEAD_MISMATCH',lambda t:t.r.update(schema=True)),
 'receipt_wrong_issue':('RECEIPT_IDENTITY_OR_HEAD_MISMATCH',lambda t:t.r.update(issue=820)),
 'receipt_bad_state':('RECEIPT_IDENTITY_OR_HEAD_MISMATCH',lambda t:t.r.update(release_state='LIVE')),
 'receipt_approval_true':('RECEIPT_IDENTITY_OR_HEAD_MISMATCH',lambda t:t.r.update(approved=True)),
 'receipt_extra_sales':('RECEIPT_IDENTITY_OR_HEAD_MISMATCH',lambda t:t.r.update(paid_orders=2)),
 'receipt_missing_field':('RECEIPT_IDENTITY_OR_HEAD_MISMATCH',lambda t:t.r.pop('approved')),
 'receipt_wrong_head':('RECEIPT_IDENTITY_OR_HEAD_MISMATCH',lambda t:t.r.update(head_sha='e'*40)),
 'receipt_missing_rows':('REQUIRED_CODE_AND_TEST_PATHS',lambda t:t.r['files'].pop()),
 'receipt_extra_rows':('REQUIRED_CODE_AND_TEST_PATHS',lambda t:t.r['files'].append(dict(t.r['files'][0]))),
 'receipt_duplicate_path':('REQUIRED_CODE_AND_TEST_PATHS',lambda t:t.r['files'][1].update(path=gate.FILES[0])),
 'receipt_wrong_file':('REQUIRED_CODE_AND_TEST_PATHS',lambda t:t.r['files'][0].update(path='preparedness/tools/unsafe.py')),
 'receipt_bogus_blob':('INVALID_FILE_HASHES',lambda t:t.r['files'][0].update(git_blob='unverified')),
 'receipt_bogus_digest':('INVALID_FILE_HASHES',lambda t:t.r['files'][0].update(tested_sha256='unverified')),
 'receipt_empty_blob':('INVALID_FILE_HASHES',lambda t:t.r['files'][1].update(git_blob='')),
 'receipt_empty_sha256':('INVALID_FILE_HASHES',lambda t:t.r['files'][1].update(tested_sha256='')),
 'receipt_unknown_row_field':('FILE_ROW_INVALID',lambda t:t.r['files'][0].update(published=True)),
 'receipt_missing_row_field':('FILE_ROW_INVALID',lambda t:t.r['files'][1].pop('git_blob')),
 'different_docket_hash':('DOCKET_GIT_BLOB_MISMATCH',lambda t:setattr(t,'docket_raw',t.docket_raw+b' ')),
 'commit_moved':('CHECKOUT_HEAD_NOT_PR_HEAD',lambda t:cmd(t.repo,'commit','--allow-empty','-qm','moved')),
 'branch_deleted_02':('BRANCH_UNAVAILABLE',lambda t:cmd(t.repo,'update-ref','-d','refs/heads/review/preparedness-cluster-02')),
 'branch_deleted_08':('BRANCH_UNAVAILABLE',lambda t:cmd(t.repo,'update-ref','-d','refs/heads/review/preparedness-cluster-08')),
 'test_file_changed':('DIRTY_TRACKED_WORKTREE',lambda t:(t.repo/gate.FILES[1]).write_text('new tested code')),
 'source_file_changed':('DIRTY_TRACKED_WORKTREE',lambda t:(t.repo/gate.FILES[0]).write_text('new source code')),
 'worktree_root_renamed':('DOCKET_GIT_BLOB_MISMATCH',lambda t:setattr(t,'docket_raw',t.docket_raw+b' ')),
}

def edit_docket(self, fn):
    x=json.loads(self.docket_raw);fn(x)
    self.docket_raw=json.dumps(x,sort_keys=True,separators=(',',':')).encode()
ExactGitTests.edit_docket=edit_docket
ExactGitTests.set_docket=lambda self,k,v:self.edit_docket(lambda x:x.__setitem__(k,v))
ExactGitTests.del_docket=lambda self,k:self.edit_docket(lambda x:x.pop(k))
ExactGitTests.pop_docket=lambda self,k:self.edit_docket(lambda x:x[k].pop())
ExactGitTests.dupe_docket_branch=lambda self:self.edit_docket(lambda x:x['branch_pins'][0].update(branch=x['branch_pins'][1]['branch']))
ExactGitTests.set_docket_pin=lambda self,n,k,v:self.edit_docket(lambda x:x['branch_pins'][n].update({k:v}))
for name,(key,fn) in MUTATIONS.items():setattr(ExactGitTests,'test_mutation_'+name,modify(key,fn))

if __name__=='__main__':unittest.main()
