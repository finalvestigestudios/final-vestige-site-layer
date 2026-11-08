"""Fail-closed source-gate execution tests. No external network or CMS writes."""
import hashlib
import importlib.util
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('r225_frozen_custody_under_test', ROOT / 'tools' / 'r220_full_slate_draft_custody.py')
custody = importlib.util.module_from_spec(spec)
spec.loader.exec_module(custody)

ONE = (b'def verify_authorities(*args):\n    return {"status": "DRAFT_HARD_HOLD"}\n'
       b'def verify_routes(*args):\n    return None\n')
TWO = b'def check_bundle(*args):\n    return {"status": "DRAFT_HARD_HOLD"}\n'


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


class AuthorityBindingTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory(prefix='fv-r225-synthetic-')
        self.addCleanup(self.dir.cleanup)
        self.root = pathlib.Path(self.dir.name)
        (self.root / 'tools').mkdir()
        self.one = self.root / custody.R221_AUTHORITY_PATH
        self.two = self.root / custody.R222_BUNDLE_PATH
        self.one.write_bytes(ONE)
        self.two.write_bytes(TWO)

    def call_one(self, data=ONE):
        return custody.load_frozen_gate(self.root, custody.R221_AUTHORITY_PATH,
                                        git_blob(data), 'fv_r225_authority_test',
                                        ('verify_authorities', 'verify_routes'))

    def call_two(self, data=TWO):
        return custody.load_frozen_gate(self.root, custody.R222_BUNDLE_PATH,
                                        git_blob(data), 'fv_r225_bundle_test',
                                        ('check_bundle',))

    def test_authority_bound_code_executes(self):
        self.assertEqual(self.call_one().verify_authorities()['status'], 'DRAFT_HARD_HOLD')

    def test_bundle_bound_code_executes(self):
        self.assertEqual(self.call_two().check_bundle()['status'], 'DRAFT_HARD_HOLD')

    def test_delegate_authority(self):
        with patch.object(custody, 'R221_AUTHORITY_BLOB', git_blob(ONE)):
            self.assertEqual(custody.load_r221_authority(self.root).verify_authorities()['status'], 'DRAFT_HARD_HOLD')

    def test_delegate_bundle(self):
        with patch.object(custody, 'R222_BUNDLE_BLOB', git_blob(TWO)):
            self.assertEqual(custody.load_r222_bundle(self.root).check_bundle()['status'], 'DRAFT_HARD_HOLD')

    def test_poisoned_module_cache_ignored(self):
        import types
        impostor = types.ModuleType('fv_r225_authority_test')
        impostor.verify_authorities = lambda *_: {'status': 'QD PASS'}
        with patch.dict(sys.modules, {'fv_r225_authority_test': impostor}):
            loaded = self.call_one()
        self.assertIsNot(loaded, impostor)
        self.assertEqual(loaded.verify_authorities()['status'], 'DRAFT_HARD_HOLD')

    def test_existing_build_import_ignored(self):
        import types
        with patch.dict(sys.modules, {'build': types.ModuleType('build')}):
            self.assertEqual(self.call_one().verify_authorities()['status'], 'DRAFT_HARD_HOLD')

    def test_no_module_cache_registration(self):
        name = 'fv_r225_authority_test'
        before = sys.modules.get(name)
        self.call_one()
        self.assertIs(sys.modules.get(name), before)

    def test_no_sys_path_mutation(self):
        before = list(sys.path)
        self.call_one()
        self.assertEqual(before, sys.path)

    def test_changed_gate_code_rejected(self):
        self.one.write_bytes(ONE+b'\n#substitution\n')
        with self.assertRaisesRegex(ValueError, 'before execution'):
            self.call_one()

    def test_changed_bundle_code_rejected(self):
        self.two.write_bytes(TWO+b'\n#substitution\n')
        with self.assertRaisesRegex(ValueError, 'before execution'):
            self.call_two()

    def test_invalid_receipt_rejected(self):
        with self.assertRaisesRegex(ValueError, 'malformed pinned'):
            custody.load_frozen_gate(self.root, custody.R221_AUTHORITY_PATH,
                                     'bad', 'x', ('verify_authorities',))

    def test_missing_gate_rejected(self):
        self.one.unlink()
        with self.assertRaises(ValueError): self.call_one()

    def test_symlinked_gate_rejected(self):
        target=self.root/'real.py'; target.write_bytes(ONE)
        self.one.unlink(); self.one.symlink_to(target)
        with self.assertRaises(ValueError): self.call_one()

    def test_symlinked_tools_folder_rejected(self):
        fake=self.root/'realtools'; fake.mkdir()
        (fake/self.one.name).write_bytes(ONE)
        self.one.unlink(); self.two.unlink(); (self.root/'tools').rmdir()
        (self.root/'tools').symlink_to(fake)
        with self.assertRaises(ValueError): self.call_one()

    def test_missing_required_function_rejected(self):
        raw=b'pass\n'; self.one.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'required API'):
            self.call_one(raw)

    def test_non_callable_function_rejected(self):
        raw=b'verify_authorities="OK"\nverify_routes=lambda: None\n'; self.one.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'required API'):
            self.call_one(raw)

    def test_syntax_error_rejected(self):
        raw=b'def verify_authorities(:\n'; self.one.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'cannot be compiled'):
            self.call_one(raw)

    def test_invalid_unicode_encoding_rejected(self):
        raw=b'\xff\xfe\x80'; self.one.write_bytes(raw)
        with self.assertRaises((ValueError, SyntaxError)):
            self.call_one(raw)

    def test_during_binding_substitution_rejected(self):
        raw=(b'from pathlib import Path\nPath(__file__).write_text("tampered")\n'
             b'def verify_authorities(*args): return None\n'
             b'def verify_routes(*args): return None\n')
        self.one.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'during execution'):
            self.call_one(raw)

    def test_function_results_do_not_infer_release(self):
        self.assertEqual(self.call_two().check_bundle()['status'], 'DRAFT_HARD_HOLD')


def _make_mutant_test(index):
    def test(self):
        index_byte = index % len(ONE)
        tampered = bytearray(ONE)
        tampered[index_byte] ^= (1 + index // len(ONE))
        self.one.write_bytes(tampered)
        with self.assertRaisesRegex(ValueError, 'before execution'):
            self.call_one()
    test.__name__ = f'test_source_byte_mutation_{index:02d}'
    return test


for _n in range(48):
    setattr(AuthorityBindingTests, f'test_source_byte_mutation_{_n:02d}', _make_mutant_test(_n))


if __name__ == '__main__':
    unittest.main()
