"""Adversarial filesystem-custody tests; all archives are disposable synthetic fixtures."""
from __future__ import annotations
from io import BytesIO
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile, ZIP_DEFLATED

TOOL = Path(__file__).resolve().parents[1] / 'tools' / 'r402_external_editorial_custody.py'
spec = importlib.util.spec_from_file_location('r402_for_r403', TOOL)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def archive(members):
    out = BytesIO()
    with ZipFile(out, 'w', ZIP_DEFLATED) as z:
        for name, data in members:
            z.writestr(name, data)
    return out.getvalue()


def synthetic():
    return archive([(gate.ARTICLE_MEMBER, b'<main><h1>synthetic nonpublishable</h1></main>')])


class BoundedCustody(unittest.TestCase):
    def test_read_single_regular_file(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)/'sample.zip'; p.write_bytes(synthetic())
            self.assertEqual(gate.read_bounded_original(p), p.read_bytes())

    def test_missing_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(OSError):
                gate.read_bounded_original(Path(t)/'missing.zip')

    def test_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises((ValueError, OSError)):
                gate.read_bounded_original(Path(t))

    def test_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t); target = root/'source.zip'; target.write_bytes(synthetic())
            alias = root/'symlink.zip'; alias.symlink_to(target)
            with self.assertRaises((ValueError, OSError)):
                gate.read_bounded_original(alias)

    def test_hardlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t); target = root/'source.zip'; target.write_bytes(synthetic())
            alias = root/'hardlink.zip'; os.link(target, alias)
            with self.assertRaises(ValueError):
                gate.read_bounded_original(alias)

    def test_empty_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)/'empty.zip'; p.touch()
            with self.assertRaises(ValueError):
                gate.read_bounded_original(p)

    def test_sparse_huge_file_is_rejected_before_read(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)/'huge.zip'
            with p.open('wb') as out:
                out.truncate(gate.MAX_ZIP + 1)
            with self.assertRaises(ValueError):
                gate.read_bounded_original(p)

    def test_size_at_limit_can_be_read_bounded(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)/'limit.bin'
            with p.open('wb') as out:
                out.truncate(gate.MAX_ZIP)
            self.assertEqual(len(gate.read_bounded_original(p)), gate.MAX_ZIP)

    def test_main_fails_closed_on_symlink(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t); p = root/'original.zip'; p.write_bytes(synthetic())
            alias = root/'alias.zip'; alias.symlink_to(p)
            import contextlib, io, json
            with contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = gate.main(['--e395-zip', str(alias)])
            self.assertEqual(rc, 2)
            self.assertFalse(json.loads(stdout.getvalue())['eligible'])

    def test_original_hash_mismatch_remains_hold(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t)/'synthetic.zip'; p.write_bytes(synthetic())
            r = gate.inspect(gate.read_bounded_original(p))
            self.assertFalse(r['archive_sha256_matched'])
            self.assertEqual(r['release'], 'DRAFT_HARD_HOLD')




NAMES = [
    '../article.html', '/etc/passwd.html', 'folder/../article.html',
    'folder/./article.html', 'C:\\windows\\article.html', 'C:article.html',
    'folder\\article.html', 'folder//article.html', '.hidden/article.html',
    'folder/.hidden.html', 'folder/control\x00.html', 'folder/control\x1f.html',
    'folder/control\x7f.html', 'folder/bad.html.exe', 'folder/run.py',
    'folder/active.js', 'folder/active.sh', 'folder/active.php',
    'folder/active.msi', 'folder/active.bat', 'folder/active.ps1',
    'folder/active.command', 'folder/active.jar', 'folder/active.iso',
    'folder/active.dll', 'folder/active.exe', 'folder/active.htm.js',
    'folder/active.svgx', 'folder/active.zip', 'folder/noextension',
    'folder/.env', 'folder/..hidden.txt', 'folder/space\nname.html',
    'folder/tab\tname.html', 'folder/unix\rname.html',
]


def unsafe_name_case(name):
    def case(self):
        self.assertFalse(gate.safe_name(name))
    return case

for i, name in enumerate(NAMES):
    setattr(BoundedCustody, f'test_unsafe_archive_filename_{i:02d}', unsafe_name_case(name))

if __name__ == '__main__':
    unittest.main()
