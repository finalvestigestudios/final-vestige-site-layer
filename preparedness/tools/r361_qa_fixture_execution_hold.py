#!/usr/bin/env python3
"""R361: isolated execution witness for #169 + dependent #2205 fixture QA.

Review-only: an executable local witness is NOT independent QD, medical,
privacy, publication, merchant, or WordPress clearance. Never executes the
synthetic tests against the original source tree. No network or CMS writes.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

SCHEMA = 'fv-preparedness-r361-fixture-isolation-v1'
PR_169_COMMIT = 'e9cd7766dac59d47ab467d8945269b9146c2aef5'
PR_2205_COMMIT = 'bbcf1859768624c611df4abadc564c18247cf32a'
PR_169_BLOB = 'e80d622c2fd32bf6c9752e375c1208c1d47d8e7c'
PR_2205_BLOB = 'b63e7f4dc9c84a4bef15dd581affe08ac81356af'
EXPECTED_TESTS = (
 'test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source',
 'test_register_fragments_cannot_duplicate_ids',
 'test_fixture_tests_never_write_or_unlink_in_canonical_checkout',
 'test_unverified_source_cannot_be_cited',
)
DISALLOWED_SUCCESS = ('qd_pass','may_publish','may_merge','safe_to_publish',
 'medical_safety_verified','privacy_review_complete','merchant_approved',
 'verified_sale','native_export_verified','publication_authorized')
HOLD = {key: False for key in DISALLOWED_SUCCESS}


def blob(data: bytes) -> str:
 return hashlib.sha1(b'blob '+str(len(data)).encode('ascii')+b'\0'+data).hexdigest()


def static_probe(test_bytes: bytes) -> dict:
 """Identify exactly which QA revision is present; never guess equivalence."""
 problems=[]
 if not isinstance(test_bytes, bytes) or len(test_bytes)>300_000:
  return {'identity':'UNKNOWN','errors':['INVALID_TEST_SOURCE']}
 digest=blob(test_bytes)
 identity=('FIX_2205' if digest==PR_2205_BLOB else
           'BASE_169_UNREMEDIATED' if digest==PR_169_BLOB else 'DRIFTED')
 if identity != 'FIX_2205': problems.append('REMEDIATED_TEST_BLOB_REQUIRED')
 try:
  tree=ast.parse(test_bytes.decode('utf-8'))
 except (UnicodeError,SyntaxError,ValueError):
  return {'identity':identity,'errors':problems+['INVALID_PYTHON_TEST']}
 classes=[x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='LibraryTests']
 if len(classes)!=1:
  problems.append('LIBRARY_TEST_CLASS_MISSING_OR_DUPLICATE')
  funcs={}
 else:
  funcs={n.name:n for n in classes[0].body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
 for name in EXPECTED_TESTS:
  if name not in funcs: problems.append('MISSING_FIXTURE_CASE:'+name)
 for name in EXPECTED_TESTS[:2]:
  if name in funcs:
   calls=[n for n in ast.walk(funcs[name]) if isinstance(n,ast.Call)]
   names={ast.unparse(c.func) for c in calls}
   if 'tempfile.TemporaryDirectory' not in names: problems.append('MISSING_SANDBOX:'+name)
   if 'shutil.copytree' not in names: problems.append('MISSING_SOURCE_COPY:'+name)
   if 'build.Library' not in names: problems.append('MISSING_LIBRARY_WITNESS:'+name)
 guard=funcs.get(EXPECTED_TESTS[2])
 if guard:
  names={ast.unparse(c.func) for c in ast.walk(guard) if isinstance(c,ast.Call)}
  if 'patch.object' not in names: problems.append('MISSING_RUNTIME_PATH_GUARD')
  for name in EXPECTED_TESTS[:2]:
   if 'self.'+name not in names: problems.append('GUARD_DOES_NOT_EXECUTE:'+name)
 return {'identity':identity,'source_blob':digest,'source_test_count':sum(x in funcs for x in EXPECTED_TESTS),
         'errors':sorted(set(problems))}


def _files(root: Path) -> dict[str,str]:
 """Content-only full recursive witness including source register and fragments."""
 if not root.is_dir() or root.is_symlink(): raise ValueError('ROOT_NOT_SAFE')
 out={}
 for dirpath, dirs, filenames in os.walk(root, followlinks=False):
  base=Path(dirpath)
  dirs[:]=[d for d in dirs if d not in ('__pycache__','build')]
  for d in dirs:
   p=base/d
   if p.is_symlink(): raise ValueError('SYMLINK_DIRECTORY')
  for name in filenames:
   if name.endswith(('.pyc','.pyo')): continue
   path=base/name
   if path.is_symlink() or not path.is_file(): raise ValueError('UNSAFE_PATH')
   if path.stat().st_size>5_000_000: raise ValueError('OVERSIZE_INPUT')
   out[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest()
  dirs.sort()
 return dict(sorted(out.items()))


def receipt(errors: list[str], *, source=None, witness=None) -> dict:
 invalid=bool(errors)
 return {'schema':SCHEMA,'status':'INVALID_HARD_HOLD' if invalid else 'REVIEW_REQUIRED_HARD_HOLD',
         'pr_169_commit':PR_169_COMMIT,'remediation_commit':PR_2205_COMMIT,
         'static_source':source, 'runtime_witness':witness,
         'errors':sorted(set(errors)), **HOLD}


def audit(repo_root: Path, *, timeout: int=35) -> dict:
 """Never runs tests on repo_root. Candidate must be pinned to #2205 bytes."""
 if Path(repo_root).is_symlink(): return receipt(['LINKED_CHECKOUT_ROOT'])
 root=Path(repo_root).resolve()
 p=root/'preparedness'
 if not (root/'.git').exists() or not p.is_dir():
  return receipt(['AUTHENTIC_CHECKOUT_MISSING'])
 test=p/'tests'/'test_preparedness.py'
 try:
  if test.is_symlink() or not test.is_file(): return receipt(['MISSING_OR_LINKED_QA_TEST'])
  source=static_probe(test.read_bytes())
  if source['errors']: return receipt(source['errors'],source=source)
  for needed in ('tools/build.py','tools/validate.py','sources/register.json'):
   if not (p/needed).is_file() or (p/needed).is_symlink():
    return receipt(['MISSING_NATIVE_DEPENDENCY:'+needed],source=source)
  before=_files(p)
  with tempfile.TemporaryDirectory(prefix='fv-r361-qa-witness-') as td:
   sandbox=Path(td)/'preparedness'
   shutil.copytree(p,sandbox,symlinks=False,ignore=shutil.ignore_patterns('__pycache__','build'))
   staged=_files(sandbox)
   if before!=staged:
    return receipt(['SANDBOX_INPUT_COPY_MISMATCH'],source=source)
   driver=Path(td)/'run_fixture_cases.py'
   driver.write_text("import sys,unittest\n"+
    "sys.path.insert(0, "+repr(str(sandbox/'tests'))+")\n"+
    "names="+repr(['test_preparedness.LibraryTests.'+x for x in EXPECTED_TESTS])+"\n"+
    "suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in names)\n"+
    "result=unittest.TextTestRunner(verbosity=1).run(suite)\n"+
    "raise SystemExit(0 if result.wasSuccessful() and result.testsRun==len(names) else 1)\n",encoding='utf-8')
   try:
    proc=subprocess.run([sys.executable,'-I',str(driver)],cwd=td,capture_output=True,text=True,
                        timeout=timeout,check=False,env={'PATH':os.environ.get('PATH','')})
    success=(proc.returncode==0)
    runner={'test_count_expected':len(EXPECTED_TESTS),'exit_code':proc.returncode,
            'output_sha256':hashlib.sha256((proc.stdout+'\n'+proc.stderr).encode()).hexdigest(),
            'test_pass':success}
   except (OSError,subprocess.SubprocessError,UnicodeError) as ex:
    runner={'test_pass':False,'execution_error':type(ex).__name__}
   after_staged=_files(sandbox)
  after=_files(p)
  errors=[]
  if not runner.get('test_pass'): errors.append('PINNED_FIXTURE_TEST_EXECUTION_FAILED')
  if staged!=after_staged: errors.append('SANDBOX_ORIGINAL_SOURCE_MUTATED')
  if before!=after: errors.append('CANONICAL_PREPAREDNESS_TREE_MUTATED')
  return receipt(errors,source=source,witness=runner)
 except (OSError,ValueError,UnicodeError) as ex:
  return receipt(['NATIVE_WITNESS_ERROR:'+type(ex).__name__])


if __name__=='__main__':
 arg=argparse.ArgumentParser()
 arg.add_argument('--repo-root',type=Path,default=Path(__file__).resolve().parents[2])
 doc=audit(arg.parse_args().repo_root)
 print(json.dumps(doc,indent=2,sort_keys=True))
 raise SystemExit(2)
