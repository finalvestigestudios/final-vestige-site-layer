"""R411: source-only gate rejects linked ancestors and stops on in-flight drift.

No financial source, customer data, Windows executable or premium entitlement is used.
"""
from __future__ import annotations

from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import offline_source_smoke_r408 as gate


class SourceContinuityR411(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'desktop'
        self.root.mkdir()
        (self.root / 'fvs_suite').mkdir()
        (self.root / 'launchers').mkdir()
        (self.root / 'fvs_suite' / '__init__.py').write_text('# synthetic\n', encoding='utf-8')
        (self.root / 'fvs_suite' / 'launcher.py').write_text(
            'import sys\n'
            'def launch(app):\n'
            "    if sys.argv[1:] != ['--smoke-test'] or app not in "
            "{'ledger','invoices','spend','policy','grants','procurement'}:\n"
            '        raise SystemExit(9)\n', encoding='utf-8')
        for app, filename in gate.PRODUCTS:
            (self.root / 'launchers' / filename).write_text(
                f'from fvs_suite.launcher import launch\nlaunch({app!r})\n', encoding='utf-8')
        (self.root / 'offline_source_smoke_r408.py').write_bytes(Path(gate.__file__).read_bytes())

    def no_spawn(self, root=None):
        with patch.object(gate.subprocess, 'run') as fake:
            with self.assertRaises(gate.SourceGateError):
                gate.run_gate(root if root is not None else self.root)
            fake.assert_not_called()

    def test_real_ancestor_symlink_denied_before_spawning(self):
        linked = self.root.parent / 'linked_parent'
        try:
            linked.symlink_to(self.root.parent, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('Filesystem does not permit symlink creation')
        self.no_spawn(linked / 'desktop')

    def test_linked_ancestor_without_python_files_denied(self):
        linked = self.root.parent / 'linked_parent'
        try:
            linked.symlink_to(self.root.parent, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('Filesystem does not permit symlink creation')
        self.no_spawn(linked / 'desktop')

    def test_parent_reparse_point_denied_even_with_valid_desktop(self):
        original = Path.lstat
        parent = self.root.parent
        def lstat(target):
            if target == parent:
                real = original(target)
                return SimpleNamespace(st_mode=real.st_mode,
                    st_file_attributes=stat.FILE_ATTRIBUTE_REPARSE_POINT)
            return original(target)
        with patch.object(Path, 'lstat', lstat):
            self.no_spawn()

    def test_relative_desktop_path_rejected_before_spawn(self):
        self.no_spawn(Path('relative-desktop'))

    def test_changing_suite_source_stops_after_first_child(self):
        path = self.root / 'fvs_suite' / 'launcher.py'
        def mutate(*a, **k):
            path.write_text('# altered\n', encoding='utf-8')
            return subprocess.CompletedProcess(args=a[0], returncode=0)
        with patch.object(gate.subprocess, 'run', side_effect=mutate) as fake:
            with self.assertRaisesRegex(gate.SourceGateError, 'changed during'):
                gate.run_gate(self.root)
        self.assertEqual(fake.call_count, 1)

    def test_changing_launcher_stops_before_optimized_mode(self):
        path = self.root / 'launchers' / 'LedgerDiffLite.py'
        def mutate(*a, **k):
            path.write_text('# invalidated\n', encoding='utf-8')
            return subprocess.CompletedProcess(args=a[0], returncode=0)
        with patch.object(gate.subprocess, 'run', side_effect=mutate) as fake:
            with self.assertRaises(gate.SourceGateError):
                gate.run_gate(self.root)
        self.assertEqual(fake.call_count, 1)

    def test_deleting_source_stops_after_first_child(self):
        path = self.root / 'fvs_suite' / 'launcher.py'
        def delete(*a, **k):
            path.unlink()
            return subprocess.CompletedProcess(args=a[0], returncode=0)
        with patch.object(gate.subprocess, 'run', side_effect=delete) as fake:
            with self.assertRaises(gate.SourceGateError):
                gate.run_gate(self.root)
        self.assertEqual(fake.call_count, 1)

    def test_changing_runner_stops_after_first_child(self):
        path = self.root / 'offline_source_smoke_r408.py'
        def mutate(*a, **k):
            path.write_text('# modified runner\n', encoding='utf-8')
            return subprocess.CompletedProcess(args=a[0], returncode=0)
        with patch.object(gate.subprocess, 'run', side_effect=mutate) as fake:
            with self.assertRaises(gate.SourceGateError):
                gate.run_gate(self.root)
        self.assertEqual(fake.call_count, 1)

    def test_prelaunch_drift_stops_without_spawning(self):
        real_digest = gate.source_digest
        source = self.root / 'fvs_suite' / 'launcher.py'
        def digest_with_intervening_change(desktop):
            output = real_digest(desktop)
            if source.read_text(encoding='utf-8').startswith('import sys'):
                source.write_text('# drift before first child\n', encoding='utf-8')
            return output
        with patch.object(gate, 'source_digest', side_effect=digest_with_intervening_change):
            self.no_spawn()

    def test_unchanged_real_synthetic_launcher_smokes_pass_all_twelve(self):
        result = gate.run_gate(self.root)
        self.assertEqual(result['passed'], 12)
        self.assertEqual(result['required'], 12)
        self.assertFalse(result['release_authorized'])
        self.assertEqual(result['evidence'], 'SOURCE_ONLY_NOT_WINDOWS_BINARY')

    def test_unchanged_mocked_processes_run_exactly_twelve(self):
        with patch.object(gate.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as fake:
            result = gate.run_gate(self.root)
        self.assertEqual(fake.call_count, 12)
        self.assertEqual(len(result['tests']), 6)

    def test_drift_errors_do_not_expose_private_source_data(self):
        source = self.root / 'fvs_suite' / 'launcher.py'
        def mutate(*a, **k):
            source.write_text('ACCOUNT_SECRET_123\n', encoding='utf-8')
            return subprocess.CompletedProcess(args=a[0], returncode=0)
        with patch.object(gate.subprocess, 'run', side_effect=mutate) as fake:
            with self.assertRaises(gate.SourceGateError) as context:
                gate.run_gate(self.root)
        self.assertEqual(fake.call_count, 1)
        self.assertNotIn('ACCOUNT_SECRET_123', str(context.exception))


if __name__ == '__main__':
    unittest.main()
