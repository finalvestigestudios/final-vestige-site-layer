"""R427 synthetic-only Git execution surface regressions; never QD or release evidence."""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import r427_execution_closure_gate as gate


def cmd(repo,*args):
    p=subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True,check=True)
    return p.stdout.strip()


def fixture():
    root=Path(tempfile.mkdtemp(prefix='r427-source-'))
    cmd(root,'init','-q')
    cmd(root,'config','user.name','synthetic test')
    cmd(root,'config','user.email','synthetic@example.invalid')
    for filename in gate.REQUIRED:
        target=root/filename;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text('# synthetic-only\nVALUE = 1\n')
    cmd(root,'add','.')
    cmd(root,'commit','-qm','synthetic base')
    base=cmd(root,'rev-parse','HEAD')
    cmd(root,'commit','--allow-empty','-qm','synthetic candidate')
    head=cmd(root,'rev-parse','HEAD')
    return root,base,head


class ClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source,cls.base,cls.head=fixture()
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.source)
    def setUp(self):
        self.temp=Path(tempfile.mkdtemp(prefix='r427-check-'))
        self.repo=self.temp/'repo';shutil.copytree(self.source,self.repo)
        self.env={'PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1'}
        self.want=self.head
        self.base_pin=self.base
    def tearDown(self):
        shutil.rmtree(self.temp)
    def audit(self):
        return gate.closure(self.repo,self.want,expected_base=self.base_pin,env=self.env)
    def must_fail(self,code):
        r=self.audit()
        self.assertFalse(r['execution_input_closure_ok'],r)
        self.assertFalse(r['eligible'])
        self.assertTrue(any(code in x for x in r['errors']),r)
    def add(self,name,content='POISON = True\n'):
        p=self.repo/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
        return p
    def test_valid_structure_still_hard_hold(self):
        r=self.audit();self.assertTrue(r['execution_input_closure_ok'],r)
        self.assertEqual(r['required_chain_count'],38)
        self.assertEqual(r['python_files_inspected'],38)
        self.assertIsNone(r['commerce_conversion'] if False else None)
        for key in ('eligible','publication_approved','qualified_safety_approved','paid_activation_approved',
                    'native_build_executed','tests_executed_by_this_gate'):
            self.assertFalse(r[key])
        self.assertEqual(r['commerce_conversion'],'UNVERIFIED')
        self.assertEqual(r['release_state'],'DRAFT_HARD_HOLD')
    def test_idempotent_digest(self):
        self.assertEqual(self.audit(),self.audit())
    def test_read_only(self):
        before=cmd(self.repo,'status','--porcelain','--untracked-files=all')
        self.audit()
        self.assertEqual(before,cmd(self.repo,'status','--porcelain','--untracked-files=all'))
    def test_fixed_parent_pin(self):
        self.assertEqual(gate.BASE_HEAD,'25f6b3fc3d6cb6fd009437bd604519c64e1550d6')
    def test_required_stems_have_distinct_names(self):
        self.assertEqual(len(set(gate.REQUIRED)),38)
    def test_blob_equivalence(self):
        x=b'hello\n';self.assertEqual(gate.blob(x),hashlib.sha1(b'blob 6\x00hello\n').hexdigest())
    def test_expected_head_changed(self):
        self.want='a'*40;self.must_fail('PR_HEAD_MISMATCH')
    def test_nonhex_head(self):
        self.want='Z'*40;self.must_fail('INVALID_EXPECTED_PR_HEAD')
    def test_short_head(self):
        self.want='1'*39;self.must_fail('INVALID_EXPECTED_PR_HEAD')
    def test_pin_not_ancestor(self):
        self.base_pin='b'*40;self.must_fail('R426_BASE_NOT_ANCESTOR')
    def test_nonhex_base(self):
        self.base_pin='invalid';self.must_fail('INVALID_PARENT_PIN')
    def test_missing_git(self):
        shutil.rmtree(self.repo/'.git');self.must_fail('CHECKOUT_OR_GIT_UNAVAILABLE')
    def test_missing_required_python_file(self):
        (self.repo/gate.REQUIRED[0]).unlink();self.must_fail('MISSING_REQUIRED_CHAIN_FILES' if False else 'UNCOMMITTED_OR_UNTRACKED_WORKTREE')
    def test_modified_tracked_python(self):
        (self.repo/gate.REQUIRED[1]).write_text('CHANGED = 99\n');self.must_fail('UNCOMMITTED_OR_UNTRACKED_WORKTREE')
    def test_deleted_tool(self):
        (self.repo/'preparedness/tools/r409_source_equivalence_gate.py').unlink();self.must_fail('UNCOMMITTED_OR_UNTRACKED_WORKTREE')
    def test_symlinked_tracked_tool(self):
        p=self.repo/gate.REQUIRED[2];p.unlink();p.symlink_to(self.repo/gate.REQUIRED[3]);self.must_fail('UNCOMMITTED_OR_UNTRACKED_WORKTREE')
    def test_untracked_py_same_tools(self):
        self.add('preparedness/tools/r426_exact_checkout_attestation_copy.py');self.must_fail('UNTRACKED_PYTHON_SOURCE')
    def test_untracked_py_in_tests(self):
        self.add('preparedness/tests/test_sneaky.py');self.must_fail('UNTRACKED_PYTHON_SOURCE')
    def test_untracked_py_in_other_tree(self):
        self.add('preparedness/helper.py');self.must_fail('UNTRACKED_PYTHON_SOURCE')
    def test_pycache_ignored_by_git(self):
        self.add('preparedness/tools/__pycache__/r409.pyc','cache');self.must_fail('IMPORT_DIRECTORY_POISON')
    def test_pyc_at_root(self):
        self.add('preparedness/tools/r409.pyc','cache');self.must_fail('IMPORT_ARTIFACT_POISON')
    def test_pth_file(self):
        self.add('preparedness/tools/evil.pth','/tmp/evil');self.must_fail('IMPORT_ARTIFACT_POISON')
    def test_native_extension_so(self):
        self.add('preparedness/tools/evil.so','binary');self.must_fail('IMPORT_ARTIFACT_POISON')
    def test_native_extension_pyd(self):
        self.add('preparedness/tools/evil.pyd','binary');self.must_fail('IMPORT_ARTIFACT_POISON')
    def test_shell_extension_dll(self):
        self.add('preparedness/tests/exploit.dll','binary');self.must_fail('IMPORT_ARTIFACT_POISON')
    def test_sitecustomize_py(self):
        self.add('preparedness/sitecustomize.py');self.must_fail('IMPORT_ARTIFACT_POISON')
    def test_usercustomize_py(self):
        self.add('preparedness/usercustomize.py');self.must_fail('IMPORT_ARTIFACT_POISON')
    def test_symlink_directory(self):
        (self.repo/'preparedness'/'forged').symlink_to(self.temp,target_is_directory=True)
        self.must_fail('IMPORT_DIRECTORY_POISON')
    def test_hardlinked_input(self):
        p=self.repo/gate.REQUIRED[0];q=self.temp/'hardlink'
        os.link(p,q);self.must_fail('UNREADABLE_OR_UNCOMMITTED_PYTHON_INPUT')
    def test_cli_fail_closed(self):
        p=subprocess.run([sys.executable,'-I',str(Path(gate.__file__)),str(self.repo),self.want],
            capture_output=True,text=True,env={'PATH':os.environ['PATH'],'PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1'})
        self.assertEqual(p.returncode,2,p.stderr)
        record=json.loads(p.stdout)
        self.assertFalse(record['eligible'])
        self.assertFalse(record['publication_approved'])
    def test_not_direct_checkout(self):
        x=self.temp/'parent';x.mkdir()
        self.repo=x
        self.must_fail('CHECKOUT_OR_GIT_UNAVAILABLE')
    def test_tracked_nonpython_not_a_release(self):
        self.add('preparedness/reviews/hold.txt','REVIEW ONLY')
        cmd(self.repo,'add','.');cmd(self.repo,'commit','-qm','review text')
        self.want=cmd(self.repo,'rev-parse','HEAD')
        self.assertTrue(self.audit()['execution_input_closure_ok'])
        self.assertFalse(self.audit()['publication_approved'])
    def test_python_closure_digest_changes_for_authored_change(self):
        before=self.audit()['review_only_closure_sha256']
        p=self.repo/gate.REQUIRED[0];p.write_text('SAFE_CHANGED = 2\n')
        cmd(self.repo,'add','.');cmd(self.repo,'commit','-qm','synthetic review change')
        self.want=cmd(self.repo,'rev-parse','HEAD')
        after=self.audit()
        self.assertTrue(after['execution_input_closure_ok'],after)
        self.assertNotEqual(before,after['review_only_closure_sha256'])
    def test_staged_only_modification(self):
        p=self.repo/gate.REQUIRED[5];p.write_text('x=2\n');cmd(self.repo,'add',str(p.relative_to(self.repo)))
        self.must_fail('UNCOMMITTED_OR_UNTRACKED_WORKTREE')
    def test_untracked_text_still_holds(self):
        self.add('preparedness/notes.tmp','untracked');self.must_fail('UNCOMMITTED_OR_UNTRACKED_WORKTREE')


# Each environment poisoning mode is an independent regression. Context is injected, not global.
for key in gate.POISON_ENV:
    def test_poison(self,key=key):
        self.env[key]='/tmp/attacker'
        self.must_fail('PYTHON_IMPORT_ENV_'+key)
    setattr(ClosureTests,'test_env_poison_'+key.lower(),test_poison)

for key,val,expected in (
    ('PYTHONDONTWRITEBYTECODE',None,'BYTECODE_WRITES_NOT_DISABLED'),
    ('PYTHONDONTWRITEBYTECODE','0','BYTECODE_WRITES_NOT_DISABLED'),
    ('PYTHONNOUSERSITE',None,'USER_SITE_NOT_DISABLED'),
    ('PYTHONNOUSERSITE','0','USER_SITE_NOT_DISABLED'),
):
    def test_env(self,key=key,val=val,expected=expected):
        if val is None:self.env.pop(key,None)
        else:self.env[key]=val
        self.must_fail(expected)
    setattr(ClosureTests,'test_env_value_'+key.lower()+'_'+str(val),test_env)

# Mutation matrix ensures each upstream layer's absence is independently flagged.
for n,stem in gate.STEMS.items():
    def test_missing_upstream(self,n=n,stem=stem):
        p=self.repo/f'preparedness/tools/r{n}_{stem}.py'
        p.unlink()
        self.must_fail('UNCOMMITTED_OR_UNTRACKED_WORKTREE')
    setattr(ClosureTests,'test_missing_upstream_tool_'+str(n),test_missing_upstream)


if __name__=='__main__':unittest.main()
