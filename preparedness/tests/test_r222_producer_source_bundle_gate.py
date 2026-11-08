"""R222 synthetic producer/source preflight regressions. No real archive writes."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r222_bundle', HERE / 'r222_producer_source_bundle_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class FrozenSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='fv-r222-synthetic-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pins = {}
        for path in gate.PINNED:
            file = self.root / path
            file.parent.mkdir(parents=True, exist_ok=True)
            raw = ('original-preserved:' + path).encode('utf-8')
            file.write_bytes(raw)
            self.pins[path] = gate.git_blob(raw)
        self.patcher = patch.object(gate, 'PINNED', self.pins)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def safe_read(self, root, rel):
        current = root
        for segment in Path(rel).parts:
            if segment in ('.', '..') or current.is_symlink():
                raise ValueError('unsafe path')
            current = current / segment
        if current.is_symlink() or not current.is_file():
            raise ValueError('symlinked/missing file')
        return current.read_bytes()

    def check(self):
        return gate.check_bundle(self.root, self.safe_read)

    def test_valid_bundle_remains_hard_hold(self):
        value = self.check()
        self.assertEqual(value['files_verified'], 20)
        self.assertEqual(value['status'], 'DRAFT_HARD_HOLD')
        for key in ('independent_qd_pass', 'source_reading_approved', 'publication_authorized'):
            self.assertFalse(value[key])

    def test_known_git_blob_vector(self):
        self.assertEqual(gate.git_blob(b'hello'), 'b6fc4c620b67d95f953a5c1c1230aaab5db5a1b0')

    def test_extra_source_fragment_cannot_hide(self):
        (self.root / 'sources/fragments/injected.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'directory membership'): self.check()

    def test_extra_inline_script_cannot_hide(self):
        (self.root / 'tools/injected.js').write_text('alert(1)')
        with self.assertRaisesRegex(ValueError, 'directory membership'): self.check()

    def test_symlinked_fragment_directory(self):
        p = self.root / 'sources/fragments'
        p.rename(self.root / 'realf')
        p.symlink_to(self.root / 'realf', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlinked source bundle directory'): self.check()

    def test_symlinked_script_directory(self):
        p = self.root / 'tools'
        p.rename(self.root / 'realt')
        p.symlink_to(self.root / 'realt', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlinked source bundle directory'): self.check()

    def test_missing_fragment(self):
        (self.root / 'sources/fragments/start.json').unlink()
        with self.assertRaisesRegex(ValueError, 'directory membership'): self.check()

    def test_missing_script(self):
        (self.root / 'tools/fire_worksheet.js').unlink()
        with self.assertRaisesRegex(ValueError, 'directory membership'): self.check()

    def test_source_reader_cannot_skip_a_file(self):
        def broken(root, relative):
            if relative == 'tools/build.py': raise ValueError('read denied')
            return self.safe_read(root, relative)
        with self.assertRaisesRegex(ValueError, 'read denied'):
            gate.check_bundle(self.root, broken)


def mutation(path, mode):
    def test(self):
        p = self.root / path
        original = p.read_bytes()
        if mode == 'modified':
            p.write_bytes(original + b' replaced')
        elif mode == 'truncated':
            p.write_bytes(original[:5])
        elif mode == 'missing':
            p.unlink()
        elif mode == 'symlink':
            replacement = self.root / 'replaced-data'
            replacement.write_bytes(original)
            p.unlink()
            p.symlink_to(replacement)
        with self.assertRaises(ValueError): self.check()
    return test


for idx, path in enumerate(gate.PINNED, 1):
    for mode in ('modified', 'truncated', 'missing', 'symlink'):
        setattr(FrozenSourceTests, f'test_{idx:02d}_{mode}', mutation(path, mode))


if __name__ == '__main__': unittest.main()
