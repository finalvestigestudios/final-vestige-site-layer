"""R56 synthetic offline Windows packager provenance tests (no financial data)."""
from __future__ import annotations

from importlib import metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import toolchain_guard as gate


class FakeDistribution:
    def __init__(self, home: Path, name: str):
        self.home = home
        self.version = '1.0.0'
        self.files = [Path(name) / '__init__.py', Path(name + '-1.0.dist-info') / 'METADATA']
        for path in self.files:
            dest = home / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text('# synthetic package\n', encoding='utf-8')

    def locate_file(self, entry):
        return self.home / entry


class ToolchainCustodyR56Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='fvs-r56-synthetic-')
        self.addCleanup(tmp.cleanup)
        self.home = Path(tmp.name)
        self.root = self.home / 'checkout'
        self.root.mkdir()
        self.site = self.home / 'site-packages'
        self.site.mkdir()
        self.runtime = self.home / 'python.exe'
        self.runtime.write_bytes(b'synthetic interpreter')
        self.manifest = self.home / 'toolchain-custody.json'
        self.names = ('pyinstaller', 'crypto', 'hooks')
        self.required = ('pyinstaller', 'crypto')
        self.optional = ('hooks', 'gone')
        self.packages = {name: FakeDistribution(self.site, name) for name in self.names}
        self.lookup = self._lookup
        self.patchers = (patch.object(gate, 'REQUIRED', self.required),
                         patch.object(gate, 'OPTIONAL', self.optional))
        for p in self.patchers:
            p.start()
            self.addCleanup(p.stop)

    def _lookup(self, name):
        if name not in self.packages:
            raise metadata.PackageNotFoundError(name)
        return self.packages[name]

    def take(self):
        gate.capture(self.root, self.manifest, lookup=self.lookup, runtime=self.runtime)

    def verify(self):
        gate.check(self.root, self.manifest, lookup=self.lookup, runtime=self.runtime)

    def test_stable_toolchain_is_verified_without_absolute_paths(self):
        self.take()
        self.verify()
        payload = json.loads(self.manifest.read_text())
        self.assertEqual(payload['schema'], gate.SCHEMA)
        self.assertEqual(payload['distributions'][-1], {'name': 'gone', 'status': 'absent'})
        self.assertNotIn(str(self.home), self.manifest.read_text())
        for flag in ('released', 'qd_approved', 'windows_executables_verified',
                     'premium_download_authorized'):
            self.assertIs(payload[flag], False)

    def test_dependency_changes_bytes_after_capture_fail(self):
        self.take()
        (self.site / 'crypto' / '__init__.py').write_bytes(b'corrupted')
        with self.assertRaises(ValueError):
            self.verify()

    def test_dependency_same_bytes_metadata_change_fails(self):
        self.take()
        target = self.site / 'crypto' / '__init__.py'
        before = target.stat()
        os.utime(target, ns=(before.st_atime_ns, before.st_mtime_ns + 300000000))
        with self.assertRaises(ValueError):
            self.verify()

    def test_dependency_file_replacement_same_bytes_fails(self):
        self.take()
        target = self.site / 'crypto' / '__init__.py'
        data = target.read_bytes()
        target.unlink()
        target.write_bytes(data)
        with self.assertRaises(ValueError):
            self.verify()

    def test_runtime_interpreter_edit_fails(self):
        self.take()
        self.runtime.write_bytes(b'interpreter replaced')
        with self.assertRaises(ValueError):
            self.verify()

    def test_runtime_interpreter_hardlink_fails(self):
        alias = self.home / 'alias.exe'
        os.link(self.runtime, alias)
        with self.assertRaises(ValueError):
            gate.snapshot(self.root, lookup=self.lookup, runtime=self.runtime)

    def test_runtime_interpreter_symlink_fails(self):
        fake = self.home / 'alias.exe'
        try:
            fake.symlink_to(self.runtime)
        except OSError:
            self.skipTest('symlinks disallowed')
        with self.assertRaises(ValueError):
            gate.snapshot(self.root, lookup=self.lookup, runtime=fake)

    def test_optional_dependency_appearing_fails(self):
        self.take()
        self.packages['gone'] = FakeDistribution(self.site, 'gone')
        with self.assertRaises(ValueError):
            self.verify()

    def test_optional_dependency_disappearing_fails(self):
        self.take()
        del self.packages['hooks']
        with self.assertRaises(ValueError):
            self.verify()

    def test_version_change_fails(self):
        self.take()
        self.packages['pyinstaller'].version = '1.0.1'
        with self.assertRaises(ValueError):
            self.verify()

    def test_new_dependency_installed_file_fails(self):
        self.take()
        package = self.packages['pyinstaller']
        new = Path('pyinstaller') / 'malicious.py'
        (self.site / new).write_text('# new module')
        package.files.append(new)
        with self.assertRaises(ValueError):
            self.verify()

    def test_missing_required_package_fails_closed(self):
        del self.packages['pyinstaller']
        with self.assertRaises(ValueError):
            gate.snapshot(self.root, lookup=self.lookup, runtime=self.runtime)

    def test_distribution_local_to_checkout_fails(self):
        self.packages['crypto'] = FakeDistribution(self.root, 'crypto')
        with self.assertRaises(ValueError):
            gate.snapshot(self.root, lookup=self.lookup, runtime=self.runtime)

    def test_distribution_symlink_file_fails(self):
        target = self.site / 'crypto' / '__init__.py'
        copy = self.site / 'target.py'
        copy.write_bytes(target.read_bytes())
        target.unlink()
        try:
            target.symlink_to(copy)
        except OSError:
            self.skipTest('symlinks disallowed')
        with self.assertRaises(ValueError):
            gate.snapshot(self.root, lookup=self.lookup, runtime=self.runtime)

    def test_duplicate_distribution_entry_fails(self):
        self.packages['crypto'].files.append(self.packages['crypto'].files[0])
        with self.assertRaises(ValueError):
            gate.snapshot(self.root, lookup=self.lookup, runtime=self.runtime)

    def test_manifest_no_overwrite(self):
        self.take()
        old = self.manifest.read_bytes()
        with self.assertRaises(ValueError):
            self.take()
        self.assertEqual(self.manifest.read_bytes(), old)

    def test_manifest_inside_checkout_rejected(self):
        with self.assertRaises(ValueError):
            gate.capture(self.root, self.root / 'bad.json',
                         lookup=self.lookup, runtime=self.runtime)

    def test_manifest_release_flag_tamper_rejected(self):
        self.take()
        data = json.loads(self.manifest.read_text())
        data['released'] = True
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            self.verify()

    def test_manifest_extra_field_rejected(self):
        self.take()
        data = json.loads(self.manifest.read_text())
        data['premium_approved'] = True
        self.manifest.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            self.verify()

    def test_duplicate_manifest_json_field_rejected(self):
        self.take()
        self.manifest.write_bytes(b'{"schema":"a","schema":"b"}')
        with self.assertRaises(ValueError):
            self.verify()

    def test_manifest_symlink_rejected(self):
        self.take()
        alias = self.home / 'alias.json'
        try:
            alias.symlink_to(self.manifest)
        except OSError:
            self.skipTest('symlinks disallowed')
        with self.assertRaises(ValueError):
            gate.check(self.root, alias, lookup=self.lookup, runtime=self.runtime)

    def test_oversized_manifest_rejected(self):
        self.take()
        self.manifest.write_bytes(b'X' * (gate.MAX_MANIFEST_BYTES + 1))
        with self.assertRaises(ValueError):
            self.verify()

    def test_isolated_module_mode_blocks_checkout_module_hijack(self):
        # The build script must use -I with -m PyInstaller so a malicious
        # checkout-root PyInstaller.py cannot shadow the installed wheel.
        (self.root / 'fvs_rogue_builder.py').write_text('print("HIJACKED")\n')
        original = subprocess.run([sys.executable, '-m', 'fvs_rogue_builder'],
                                  cwd=self.root, capture_output=True, text=True)
        isolated = subprocess.run([sys.executable, '-I', '-m', 'fvs_rogue_builder'],
                                  cwd=self.root, capture_output=True, text=True)
        self.assertEqual(original.returncode, 0)
        self.assertIn('HIJACKED', original.stdout)
        self.assertNotEqual(isolated.returncode, 0)
        self.assertNotIn('HIJACKED', isolated.stdout)


if __name__ == '__main__':
    unittest.main()
