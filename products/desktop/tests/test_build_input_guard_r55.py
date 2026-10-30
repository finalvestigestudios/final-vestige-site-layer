"""R55: six-app packaging input custody, with synthetic files only."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import build_input_guard as guard


class BuildInputCustodyR55Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='fvs-r55-synthetic-')
        self.addCleanup(temp.cleanup)
        self.work = Path(temp.name)
        self.root = self.work / 'checkout'
        self.package = self.root / 'products' / 'desktop' / 'fvs_suite'
        self.launchers = self.root / 'products' / 'desktop' / 'launchers'
        self.scripts = self.root / 'products' / 'desktop' / 'scripts'
        for directory in (self.package, self.launchers, self.scripts,
                          self.root / '.github' / 'workflows'):
            directory.mkdir(parents=True)
        self.engine = self.package / 'engine.py'
        self.engine.write_text('# synthetic engine\n', encoding='utf-8')
        for name, _ in guard.source_gate.APPS:
            (self.launchers / f'{name}.py').write_text('# synthetic launcher\n', encoding='utf-8')
        self.wrapper = self.scripts / 'verify-windows-candidate.ps1'
        self.wrapper.write_text('# synthetic powershell\n', encoding='utf-8')
        self.workflow = self.root / '.github' / 'workflows' / 'desktop-build.yml'
        self.workflow.write_text('# synthetic workflow\n', encoding='utf-8')
        self.manifest = self.work / 'private-manifest.json'

    def capture(self):
        guard.capture(self.root, self.manifest)

    def test_unchanged_source_and_controls_validate(self):
        self.capture()
        guard.check(self.root, self.manifest)
        state = json.loads(self.manifest.read_text(encoding='utf-8'))
        self.assertEqual(state['schema'], guard.SCHEMA)
        self.assertEqual(len(state['inputs']), 9)  # six launchers, one engine, two controls
        for flag in ('released', 'qd_approved', 'windows_executables_verified',
                     'premium_download_authorized'):
            self.assertIs(state[flag], False)
        self.assertNotIn(str(self.work), self.manifest.read_text())

    def test_source_edit_after_capture_fails(self):
        self.capture()
        self.engine.write_text('# modified financial rule\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            guard.check(self.root, self.manifest)

    def test_same_byte_in_place_rewrite_is_detected(self):
        self.capture()
        old = self.engine.stat()
        os.utime(self.engine, ns=(old.st_atime_ns, old.st_mtime_ns + 100_000_000))
        with self.assertRaises(ValueError):
            guard.check(self.root, self.manifest)

    def test_same_byte_file_replacement_is_detected(self):
        self.capture()
        content = self.engine.read_bytes()
        self.engine.unlink()
        self.engine.write_bytes(content)
        with self.assertRaises(ValueError):
            guard.check(self.root, self.manifest)

    def test_added_engine_module_fails(self):
        self.capture()
        (self.package / 'injected.py').write_text('# unauthorized module\n')
        with self.assertRaises(ValueError):
            guard.check(self.root, self.manifest)

    def test_missing_launcher_fails(self):
        self.capture()
        (self.launchers / 'LedgerDiffLite.py').unlink()
        with self.assertRaises(ValueError):
            guard.check(self.root, self.manifest)

    def test_build_wrapper_changed_fails(self):
        self.capture()
        self.wrapper.write_text('# switched build command\n')
        with self.assertRaises(ValueError):
            guard.check(self.root, self.manifest)

    def test_workflow_changed_fails(self):
        self.capture()
        self.workflow.write_text('# switched upload policy\n')
        with self.assertRaises(ValueError):
            guard.check(self.root, self.manifest)

    def test_missing_control_file_fails_closed(self):
        self.workflow.unlink()
        with self.assertRaises(ValueError):
            self.capture()

    def test_manifest_cannot_be_overwritten(self):
        self.capture()
        original = self.manifest.read_bytes()
        with self.assertRaises(ValueError):
            self.capture()
        self.assertEqual(self.manifest.read_bytes(), original)

    def test_manifest_must_stay_outside_checkout(self):
        with self.assertRaises(ValueError):
            guard.capture(self.root, self.root / 'evidence.json')

    def test_manifest_symlink_fails(self):
        self.capture()
        alias = self.work / 'alias.json'
        try:
            alias.symlink_to(self.manifest)
        except (OSError, NotImplementedError):
            self.skipTest('filesystem disallows symlinks')
        with self.assertRaises(ValueError):
            guard.check(self.root, alias)

    def test_manifest_hardlink_alias_fails(self):
        self.capture()
        alias = self.work / 'alias.json'
        try:
            os.link(self.manifest, alias)
        except OSError:
            self.skipTest('filesystem disallows hardlinks')
        with self.assertRaises(ValueError):
            guard.check(self.root, self.manifest)

    def test_duplicate_manifest_json_keys_fail(self):
        self.capture()
        self.manifest.write_text('{"schema":"v1","schema":"v2"}', encoding='utf-8')
        with self.assertRaises(ValueError):
            guard.check(self.root, self.manifest)

    def test_oversized_manifest_fails_closed(self):
        self.capture()
        self.manifest.write_bytes(b'X' * (guard.MAX_MANIFEST_BYTES + 1))
        with self.assertRaises(ValueError):
            guard.check(self.root, self.manifest)

    def test_added_manifest_field_fails(self):
        self.capture()
        contents = json.loads(self.manifest.read_text())
        contents['approved'] = True
        self.manifest.write_text(json.dumps(contents))
        with self.assertRaises(ValueError):
            guard.check(self.root, self.manifest)

    def test_fake_release_flag_fails(self):
        self.capture()
        contents = json.loads(self.manifest.read_text())
        contents['released'] = True
        self.manifest.write_text(json.dumps(contents))
        with self.assertRaises(ValueError):
            guard.check(self.root, self.manifest)

    def test_symlinked_source_fails(self):
        self.capture()
        target = self.package / 'copy.py'
        try:
            target.symlink_to(self.engine)
        except (OSError, NotImplementedError):
            self.skipTest('filesystem disallows symlinks')
        with self.assertRaises(ValueError):
            guard.check(self.root, self.manifest)

    def test_capture_detects_mid_fingerprint_change(self):
        real_snapshot = guard.snapshot
        counter = [0]
        def mutate(root):
            counter[0] += 1
            state = real_snapshot(root)
            if counter[0] == 1:
                self.wrapper.write_text('# changed after first snapshot\n')
            return state
        with patch.object(guard, 'snapshot', side_effect=mutate):
            with self.assertRaises(ValueError):
                self.capture()
        self.assertFalse(self.manifest.exists())

    def test_private_cli_failure_is_redacted(self):
        with patch.object(guard, 'check', side_effect=ValueError('customer C:/secret/ledger.csv')):
            from io import StringIO
            stream = StringIO()
            with patch('sys.stderr', stream):
                result = guard.main(['check', str(self.manifest), '--root', str(self.root)])
            self.assertEqual(result, 1)
            self.assertEqual(stream.getvalue().strip(), guard.SAFE_ERROR)
            self.assertNotIn('customer', stream.getvalue())


if __name__ == '__main__':
    unittest.main()
