"""R145 adversarial tests; synthetic mutation tests do not confer safety/QD approval."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

HERE=Path(__file__).resolve().parent
TOOL = HERE.parent/'tools'/'r145_chain_integrity.py' if (HERE.parent/'tools'/'r145_chain_integrity.py').exists() else HERE/'r145_chain_integrity.py'
MANIFEST = HERE.parent/'docs'/'r145'/'r145_stack_manifest.json' if (HERE.parent/'docs'/'r145'/'r145_stack_manifest.json').exists() else HERE/'r145_stack_manifest.json'
spec=importlib.util.spec_from_file_location('r145_chain_integrity',TOOL)
gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
MASTER=json.loads(MANIFEST.read_text())

def fresh():return copy.deepcopy(MASTER)

class PlanTests(unittest.TestCase):
    def test_verified_static_manifest(self):
        result=gate.validate_plan(fresh())
        self.assertEqual(result['chain_stages'],12)
        self.assertEqual(result['expected_added_files'],41)
        self.assertEqual(result['last_review_commit'],gate.EXPECTED_HEADS[-1])
        self.assertFalse(result['publication_allowed'])
        self.assertEqual(result['independent_qd'],'NOT_APPROVED')

    def test_unavailable_real_checkout_is_hold(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(gate.Hold):gate.inspect_checkout(Path(folder),fresh())

    def test_failed_git_is_not_silently_approved(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(gate.Hold):gate.git(Path(folder),'rev-parse','HEAD')

    def test_missing_native_archive_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(gate.Hold):gate.run_native_snapshot(Path(folder),'does-not-exist')

    def test_check_output_cannot_be_promoted_to_release(self):
        x=gate.validate_plan(fresh())
        self.assertEqual(x['release'],'DRAFT_HOLD')
        self.assertNotIn('may_publish',x)

    def test_git_diff_detects_edits_not_additions(self):
        with mock.patch.object(gate,'git',return_value='M\tpreparedness/content/articles/go-bags.body.html\n'):
            with self.assertRaises(gate.Hold):gate._diff(Path('/tmp'),'x','y')

    def test_git_diff_detects_deletions(self):
        with mock.patch.object(gate,'git',return_value='D\tpreparedness/sources/register.json\n'):
            with self.assertRaises(gate.Hold):gate._diff(Path('/tmp'),'x','y')

    def test_git_diff_detects_rename(self):
        with mock.patch.object(gate,'git',return_value='R100\ta\tb\n'):
            with self.assertRaises(gate.Hold):gate._diff(Path('/tmp'),'x','y')

    def test_git_diff_detects_duplicate(self):
        with mock.patch.object(gate,'git',return_value='A\tpreparedness/a\nA\tpreparedness/a\n'):
            with self.assertRaises(gate.Hold):gate._diff(Path('/tmp'),'x','y')

    def test_git_diff_accepts_additions_only(self):
        with mock.patch.object(gate,'git',return_value='A\tpreparedness/tools/tool.py\n'):
            self.assertEqual(gate._diff(Path('/tmp'),'x','y'),{'preparedness/tools/tool.py':'A'})

    def test_can_compile_guard_without_repo_checkout(self):
        p=subprocess.run(['python','-I','-m','py_compile',str(TOOL)],capture_output=True)
        self.assertEqual(p.returncode,0,p.stderr)


def mutation_test(name, mutate):
    def t(self):
        data=fresh();mutate(data)
        with self.assertRaises(gate.Hold,msg=name):gate.validate_plan(data)
    t.__name__='test_'+name
    setattr(PlanTests,t.__name__,t)

for name, key, new_value in (
 ('bad_schema','schema','OTHER'),('missing_schema','schema',None),
 ('anchor_changed','anchor','0'*40),('rc_changed','frozen_rc','1'*40),
 ('release_approved','release','PUBLISHED'),('wrong_article_count','expected_articles',36),
 ('wrong_citation_count','expected_citations',1999),('no_issues','issues',[]),
 ('issue_owner_changed','issues',[136,818,820]),
 ('contributors_missing','contributors',{}),('qa_refs_missing','independent_refs',{}),
 ('chain_missing','chain',None),('chain_short','chain',[]),('chain_is_string','chain','fake'),
):mutation_test(name,lambda m,k=key,v=new_value:m.__setitem__(k,v))

for flag in ('may_publish','qd_pass','medical_safety_verified','merchant_offer_verified','automatic_merge'):
    mutation_test('forged_'+flag,lambda m,k=flag:m.__setitem__(k,True))
    mutation_test('omitted_'+flag,lambda m,k=flag:m.pop(k))

for idx in range(12):
    def at(i,field,value):return lambda m:m['chain'][i].__setitem__(field,value)
    mutation_test(f'r{133+idx}_head_shift',at(idx,'head','0'*40))
    mutation_test(f'r{133+idx}_parent_shift',at(idx,'parent','1'*40))
    mutation_test(f'r{133+idx}_pr_shift',at(idx,'pr',99999))
    mutation_test(f'r{133+idx}_round_shift',at(idx,'round',999))
    mutation_test(f'r{133+idx}_draft_false',at(idx,'draft',False))
    mutation_test(f'r{133+idx}_state_closed',at(idx,'state','closed'))
    mutation_test(f'r{133+idx}_files_empty',at(idx,'files',[]))
    mutation_test(f'r{133+idx}_files_bad',at(idx,'files',['preparedness/content/articles/go-bags.body.html']))
    mutation_test(f'r{133+idx}_stage_missing',lambda m,i=idx:m['chain'].pop(i))
    mutation_test(f'r{133+idx}_bad_doc_dir',lambda m,i=idx:m['chain'][i]['files'].__setitem__(0,'preparedness/docs/r900/fake.md'))
    mutation_test(f'r{133+idx}_duplicate_file',lambda m,i=idx:m['chain'][i]['files'].append(m['chain'][i]['files'][0]))

for idx, (branch,sha) in enumerate(gate.CONTRIBUTORS.items()):
    mutation_test(f'contributor_pin_{idx}',lambda m,b=branch:m['contributors'].__setitem__(b,'f'*40))
for idx,ref in enumerate(gate.INDEPENDENT_REFS):
    mutation_test(f'qa_ref_pin_{idx}',lambda m,k=ref:m['independent_refs'].__setitem__(k,'0'*40))
for idx,path in enumerate(('preparedness/docs/r133/../../evil.md','preparedness/docs/r133/a\\b.md',
                           'preparedness/tools/r133_exploit.sh','preparedness/tests/test_r133_x.py/evil',
                           'preparedness/tools/r134_false.py','preparedness/docs/r133/é.md')):
    mutation_test(f'path_escape_{idx}',lambda m,p=path:m['chain'][0]['files'].__setitem__(0,p))

if __name__=='__main__':unittest.main()
