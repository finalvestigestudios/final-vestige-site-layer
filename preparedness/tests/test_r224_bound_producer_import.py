"""R224 isolated binding tests: synthetic code only, no authentic archive writes."""
from __future__ import annotations
import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('r220_bound_import', HERE / 'tools' / 'r220_full_slate_draft_custody.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)
ORIGINAL = (b'class Library:\n    def __init__(self, root=None):\n'
            b'        self.root = root\n\n'
            b'def resolve_tokens(library, meta):\n    return ("text", [])\n\n'
            b'def word_count(text):\n    return len(text.split())\n')

class BoundProducerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fv-r224-bind-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'tools').mkdir()
        self.path = self.root / 'tools' / 'build.py'
        self.path.write_bytes(ORIGINAL)
        self.bundle = types.SimpleNamespace(PINNED={'tools/build.py': gate.git_blob(ORIGINAL)})
    def bind(self):
        return gate.load_frozen_builder(self.root, self.bundle)
    def test_git_known_vector(self):
        self.assertEqual(gate.git_blob(b'hello'), 'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')
    def test_valid_bound_producer(self):
        p = self.bind()
        self.assertEqual(p.resolve_tokens(None, None), ('text', []))
        self.assertEqual(p.word_count('hello world'), 2)
        self.assertEqual(p.Library(root=self.root).root, self.root)
    def test_no_global_module_cache_entry(self):
        p = self.bind()
        self.assertIsNot(p, sys.modules.get('build'))
        self.assertNotIn('fv_preparedness_custody_bound_build', sys.modules)
    def test_poisoned_sys_modules_build_ignored(self):
        poison = types.ModuleType('build')
        poison.Library = lambda root=None: 'POISONED'
        with patch.dict(sys.modules, {'build': poison}):
            p = self.bind()
            self.assertNotEqual(p.Library(root=self.root), 'POISONED')
            self.assertIs(sys.modules['build'], poison)
    def test_no_sys_path_leak(self):
        before = list(sys.path)
        self.bind()
        self.assertEqual(sys.path, before)
    def test_no_shared_state_between_calls(self):
        first = self.bind()
        first.Library = lambda root=None: 'CORRUPTED'
        second = self.bind()
        self.assertNotEqual(second.Library(root=self.root), 'CORRUPTED')
    def test_absent_build_source_rejected(self):
        self.path.unlink()
        with self.assertRaisesRegex(ValueError, 'missing or symlinked'): self.bind()
    def test_symlinked_build_source_rejected(self):
        target = self.root / 'real.py'
        self.path.rename(target)
        self.path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, 'missing or symlinked'): self.bind()
    def test_symlinked_tools_directory_rejected(self):
        (self.root / 'tools').rename(self.root / 'real_tools')
        (self.root / 'tools').symlink_to(self.root / 'real_tools', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink ancestor'): self.bind()
    def test_content_drift_after_preflight_rejected(self):
        self.path.write_bytes(ORIGINAL + b'\n# changed source\n')
        with self.assertRaisesRegex(ValueError, 'between preflight'): self.bind()
    def test_missing_pin_rejected(self):
        self.bundle.PINNED.clear()
        with self.assertRaisesRegex(ValueError, 'receipt'): self.bind()
    def test_short_pin_rejected(self):
        self.bundle.PINNED['tools/build.py'] = 'a' * 38
        with self.assertRaisesRegex(ValueError, 'receipt'): self.bind()
    def test_uppercase_pin_rejected(self):
        self.bundle.PINNED['tools/build.py'] = 'A' * 40
        with self.assertRaisesRegex(ValueError, 'receipt'): self.bind()
    def test_nonstr_pin_rejected(self):
        self.bundle.PINNED['tools/build.py'] = 23
        with self.assertRaisesRegex(ValueError, 'receipt'): self.bind()
    def test_changed_during_execution_rejected(self):
        payload = (ORIGINAL + b'\nfrom pathlib import Path\n'
                   b'Path(__file__).write_bytes(b"swapped during execution")\n')
        self.path.write_bytes(payload)
        self.bundle.PINNED['tools/build.py'] = gate.git_blob(payload)
        with self.assertRaisesRegex(ValueError, 'during module binding'): self.bind()
    def test_missing_required_function_rejected(self):
        broken = b'class Library: pass\ndef resolve_tokens(*a): pass\n'
        self.path.write_bytes(broken)
        self.bundle.PINNED['tools/build.py'] = gate.git_blob(broken)
        with self.assertRaisesRegex(ValueError, 'required API: word_count'): self.bind()
    def test_syntax_error_rejected(self):
        broken = b'def broken(:\n'
        self.path.write_bytes(broken)
        self.bundle.PINNED['tools/build.py'] = gate.git_blob(broken)
        with self.assertRaisesRegex(ValueError, 'cannot be compiled'): self.bind()
    def test_invalid_utf8_rejected(self):
        broken = b'\xff\xfe'
        self.path.write_bytes(broken)
        self.bundle.PINNED['tools/build.py'] = gate.git_blob(broken)
        with self.assertRaisesRegex(ValueError, 'cannot be compiled'): self.bind()

def mutation(i):
    def test(self):
        self.path.write_bytes(ORIGINAL + f'\n# unreviewed producer drift {i:02d}\n'.encode())
        with self.assertRaisesRegex(ValueError, 'between preflight'): self.bind()
    return test

for index in range(1, 43):
    setattr(BoundProducerTests, f'test_source_mutation_{index:02d}', mutation(index))

if __name__ == '__main__':
    unittest.main()
