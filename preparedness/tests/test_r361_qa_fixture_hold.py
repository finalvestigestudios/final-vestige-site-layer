"""Synthetic-only, no-network tests for R361 fail-closed fixture custody."""
import hashlib
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import r361_qa_fixture_execution_hold as gate


def sample(*, destructive=False, broken=False):
    target = 'ROOT' if destructive else 'sandbox'
    failed = 'self.fail("bad")' if broken else 'self.assertTrue(True)'
    return ('''import unittest,tempfile,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build
class LibraryTests(unittest.TestCase):
 def test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source(self):
  with tempfile.TemporaryDirectory() as td:
   sandbox=Path(td)/'preparedness'
   shutil.copytree(ROOT,sandbox)
   (''' + target + '''/'sources'/'fragments'/'fixture').write_text('{}')
   build.Library(root=sandbox)
 def test_register_fragments_cannot_duplicate_ids(self):
  with tempfile.TemporaryDirectory() as td:
   sandbox=Path(td)/'preparedness'
   shutil.copytree(ROOT,sandbox)
   build.Library(root=sandbox)
   ''' + failed + '''
 def test_fixture_tests_never_write_or_unlink_in_canonical_checkout(self):
  from unittest.mock import patch
  with patch.object(Path,'write_text',Path.write_text):
   self.test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source()
   self.test_register_fragments_cannot_duplicate_ids()
 def test_unverified_source_cannot_be_cited(self):
  self.assertTrue(True)
''').encode()


def setup(root, body):
    (root/'.git').mkdir()
    p=root/'preparedness'
    for d in ['tools','tests','sources/fragments']:
        (p/d).mkdir(parents=True)
    (p/'tools/build.py').write_text('class Library:\n def __init__(self,root=None):pass\n')
    (p/'tools/validate.py').write_text('def validate(x):return [],{}\n')
    (p/'sources/register.json').write_text('{"sources":[]}')
    (p/'tests/test_preparedness.py').write_bytes(body)
    return p


class GateTests(unittest.TestCase):
    def test_git_blob(self):
        self.assertEqual(gate.blob(b'x'),hashlib.sha1(b'blob 1\0x').hexdigest())
    def test_pins_are_distinct(self):
        self.assertNotEqual(gate.PR_169_BLOB,gate.PR_2205_BLOB)
    def test_unremediated_cannot_pass(self):
        body=sample()
        with patch.object(gate,'PR_169_BLOB',gate.blob(body)):
            self.assertIn('REMEDIATED_TEST_BLOB_REQUIRED',gate.static_probe(body)['errors'])
    def test_drift_cannot_pass(self):
        self.assertEqual(gate.static_probe(sample())['identity'],'DRIFTED')
    def test_pinned_synthetic_ast(self):
        body=sample()
        with patch.object(gate,'PR_2205_BLOB',gate.blob(body)):
            self.assertEqual(gate.static_probe(body)['errors'],[])
    def test_missing_checkout(self):
        with tempfile.TemporaryDirectory() as td:
            self.assertEqual(gate.audit(Path(td))['status'],'INVALID_HARD_HOLD')
    def test_exact_synthetic_runtime(self):
        body=sample()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);setup(root,body)
            with patch.object(gate,'PR_2205_BLOB',gate.blob(body)):
                result=gate.audit(root)
        self.assertEqual(result['status'],'REVIEW_REQUIRED_HARD_HOLD',result)
        self.assertTrue(result['runtime_witness']['test_pass'])
    def test_mutation_detected(self):
        body=sample(destructive=True)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);setup(root,body)
            with patch.object(gate,'PR_2205_BLOB',gate.blob(body)):
                result=gate.audit(root)
        self.assertIn('SANDBOX_ORIGINAL_SOURCE_MUTATED',result['errors'])
    def test_failed_fixture_detected(self):
        body=sample(broken=True)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);setup(root,body)
            with patch.object(gate,'PR_2205_BLOB',gate.blob(body)):
                result=gate.audit(root)
        self.assertIn('PINNED_FIXTURE_TEST_EXECUTION_FAILED',result['errors'])
    def test_snapshot_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            p=setup(Path(td),sample())
            (p/'sources/fragments/bad').symlink_to(p/'sources/register.json')
            with self.assertRaises(ValueError):gate._files(p)
    def test_snapshot_detects_revision(self):
        with tempfile.TemporaryDirectory() as td:
            p=setup(Path(td),sample());before=gate._files(p)
            (p/'sources/register.json').write_text('changed')
            self.assertNotEqual(gate._files(p),before)
    def test_all_approval_bits_false(self):
        for k in gate.DISALLOWED_SUCCESS:
            self.assertIs(gate.receipt([])[k],False)
            self.assertIs(gate.receipt(['error'])[k],False)


MUTANTS=[b'{}',b'[]',b'null',b'0',b'1',b'x',b'pass',b'print(1)',b'import os',
 b'import sys',b'import unittest',b'class LibraryTests:pass',b'def test():pass',
 b'#!/usr/bin/env python3',b'from pathlib import Path',b'if True:\n pass',
 b'not python',b'\\xff',b'\\x00',b'\\x20',b'\\r',b'\\t',b' ' * 10,
 b'x' * 100,b'x' * 1000,b'x' * 10000,b'class X:pass',b'import json',
 b'def x():\n return False',b'assert True',b'assert False',b'raise Exception()',
 b'__import__("os")',b'with x:pass',b'for x in []:pass',b'lambda:None',
 b'None',b'True',b'False',b'("qd_pass",True)']
for n,mutant in enumerate(MUTANTS):
    def factory(b):
        def case(self):
            outcome=gate.static_probe(b)
            self.assertNotEqual(outcome['identity'],'FIX_2205')
            self.assertTrue(outcome['errors'])
        return case
    setattr(GateTests,'test_mutant_%02d'%n,factory(mutant))

if __name__=='__main__':unittest.main()
