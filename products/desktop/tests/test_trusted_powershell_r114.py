"""Synthetic Windows shell path-hijack protections, not a real AV scan."""
from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'trusted_powershell_r114.py'
spec = importlib.util.spec_from_file_location('trusted_powershell_r114', SCRIPT)
trust = importlib.util.module_from_spec(spec)
spec.loader.exec_module(trust)


class NativePowerShellR114(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'System32'
        self.binary = self.root / 'WindowsPowerShell' / 'v1.0' / 'powershell.exe'
        self.binary.parent.mkdir(parents=True)
        self.binary.write_bytes(b'MZ' + b'synthetic PE placeholder')

    def test_absolute_system32_image_admitted(self):
        self.assertEqual(trust._validate_system_powershell(self.root), self.binary)

    def test_path_hijack_not_consulted(self):
        forged = Path(self.temp.name) / 'powershell.exe'
        forged.write_bytes(b'MZ forged')
        with patch.dict(os.environ, {'PATH': self.temp.name, 'SystemRoot': self.temp.name,
                                     'windir': self.temp.name}):
            self.assertEqual(trust._validate_system_powershell(self.root), self.binary)

    def test_missing_image_fails_closed(self):
        self.binary.unlink()
        with self.assertRaises(trust.PowerShellHold):
            trust._validate_system_powershell(self.root)

    def test_unexpected_non_pe_fails_closed(self):
        self.binary.write_bytes(b'#! not powershell')
        with self.assertRaises(trust.PowerShellHold):
            trust._validate_system_powershell(self.root)

    def test_non_regular_image_fails_closed(self):
        self.binary.unlink()
        self.binary.mkdir()
        with self.assertRaises(trust.PowerShellHold):
            trust._validate_system_powershell(self.root)

    def test_symlink_binary_fails_closed(self):
        self.binary.unlink()
        target = Path(self.temp.name) / 'elsewhere.exe'
        target.write_bytes(b'MZ elsewhere')
        try:
            self.binary.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest('symlinks not available to this test process')
        with self.assertRaises(trust.PowerShellHold):
            trust._validate_system_powershell(self.root)

    def test_symlink_directory_fails_closed(self):
        self.binary.unlink()
        self.binary.parent.rmdir()
        elsewhere = Path(self.temp.name) / 'elsewhere'
        elsewhere.mkdir()
        (elsewhere / 'powershell.exe').write_bytes(b'MZ elsewhere')
        try:
            (self.root / 'WindowsPowerShell' / 'v1.0').symlink_to(elsewhere, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('symlinks not available to this test process')
        with self.assertRaises(trust.PowerShellHold):
            trust._validate_system_powershell(self.root)

    def test_relative_directory_denied(self):
        with self.assertRaises(trust.PowerShellHold):
            trust._validate_system_powershell(Path('System32'))

    def test_wrong_system_directory_denied(self):
        with self.assertRaises(trust.PowerShellHold):
            trust._validate_system_powershell(Path(self.temp.name))

    def test_malformed_directory_denied(self):
        for item in ('System32', None, 3, b'System32'):
            with self.subTest(item=repr(item)), self.assertRaises(trust.PowerShellHold):
                trust._validate_system_powershell(item)

    def test_native_nonwindows_denied(self):
        with patch.object(trust.os, 'name', 'posix'):
            with self.assertRaises(trust.PowerShellHold):
                trust._native_system_directory()

    def test_native_32bit_denied(self):
        with patch.object(trust.os, 'name', 'nt'), patch.object(trust.sys, 'maxsize', 2**31-1):
            with self.assertRaises(trust.PowerShellHold):
                trust._native_system_directory()

    def test_resolver_fails_closed_if_winapi_unavailable(self):
        with patch.object(trust, '_native_system_directory', side_effect=trust.PowerShellHold('private')):
            with self.assertRaises(trust.PowerShellHold):
                trust.require_system_powershell()

    def test_resolver_uses_exact_native_system_path(self):
        with patch.object(trust, '_native_system_directory', return_value=self.root):
            self.assertEqual(trust.require_system_powershell(), self.binary)

    def test_error_never_leaks_user_path(self):
        self.binary.unlink()
        with self.assertRaises(trust.PowerShellHold) as captured:
            trust._validate_system_powershell(self.root)
        self.assertNotIn(self.temp.name, str(captured.exception))


if __name__ == '__main__':
    unittest.main()
