"""R336 six-app release smoke fault isolation with synthetic runners only.

These tests never spawn a real EXE or make release/Defender/entitlement claims.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from smoke_runner_r336 import SmokeRunError, run_smoke_checked, select_smoke_runner


class SmokeRunnerR336(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="r336-secret-financial-path-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.exe = self.root / "GrantAuditStudioPro.exe"
        self.name = "GrantAuditStudioPro.exe"

    def run_case(self, runner, *, timeout=15):
        return run_smoke_checked(runner, self.exe, self.root,
                                 name=self.name, timeout=timeout)

    def assert_private_error(self, runner, contains):
        with self.assertRaises(SmokeRunError) as caught:
            self.run_case(runner)
        self.assertIn(contains, str(caught.exception))
        self.assertNotIn(str(self.root), str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)

    def test_none_selects_native_runner_only(self):
        self.assertIs(select_smoke_runner(None), subprocess.run)

    def test_falsy_injected_runner_is_used_not_bypassed(self):
        class FalsyCallable:
            def __bool__(self):
                return False
            def __call__(self, *args, **kwargs):
                return SimpleNamespace(returncode=0)
        injected = FalsyCallable()
        self.assertIs(select_smoke_runner(injected), injected)
        with patch('smoke_runner_r336.subprocess.run',
                   side_effect=AssertionError('unexpected native EXE launch')):
            self.run_case(select_smoke_runner(injected))

    def test_truthiness_trap_is_never_evaluated(self):
        class Trap:
            def __bool__(self):
                raise AssertionError('never evaluate injected runner truthiness')
            def __call__(self, *args, **kwargs):
                return SimpleNamespace(returncode=0)
        self.run_case(select_smoke_runner(Trap()))

    def test_zero_exit(self):
        self.run_case(lambda *_args, **_kw: SimpleNamespace(returncode=0))

    def test_exact_argument_and_private_stdio(self):
        runner = Mock(return_value=SimpleNamespace(returncode=0))
        self.run_case(runner)
        (args,), kw = runner.call_args
        self.assertEqual(args, [str(self.exe.resolve()), "--smoke-test"])
        self.assertEqual(kw['cwd'], str(self.root.resolve()))
        self.assertEqual(kw['timeout'], 15)
        self.assertIs(kw['check'], False)
        for key in ('stdin', 'stdout', 'stderr'):
            self.assertEqual(kw[key], subprocess.DEVNULL)

    def test_known_timeout(self):
        self.assert_private_error(Mock(side_effect=subprocess.TimeoutExpired(
            cmd=[str(self.exe)], timeout=15, output=b'private')),
            'timed out')

    def test_os_error_redacts_private_paths(self):
        self.assert_private_error(Mock(side_effect=OSError('sensitive ' + str(self.root))),
                                  'could not execute')

    def test_unexpected_subprocess_exception_redacted(self):
        self.assert_private_error(Mock(side_effect=subprocess.SubprocessError(
            'client secret ' + str(self.root))), 'could not execute')

    def test_unexpected_runtime_exception_redacted(self):
        self.assert_private_error(Mock(side_effect=RuntimeError(str(self.root))),
                                  'could not execute')

    def test_none_return_rejected(self):
        self.assert_private_error(lambda *_a, **_kw: None, 'invalid smoke result')

    def test_missing_returncode_rejected(self):
        self.assert_private_error(lambda *_a, **_kw: object(), 'invalid smoke result')

    def test_returncode_property_raises_redacted(self):
        class MaliciousResult:
            @property
            def returncode(self):
                raise ValueError('private ' + str(self_path))
        self_path = self.root
        self.assert_private_error(lambda *_a, **_kw: MaliciousResult(),
                                  'invalid smoke result')

    def test_boolean_true_rejected(self):
        self.assert_private_error(lambda *_a, **_kw: SimpleNamespace(returncode=True),
                                  'invalid smoke result')

    def test_boolean_false_rejected(self):
        self.assert_private_error(lambda *_a, **_kw: SimpleNamespace(returncode=False),
                                  'invalid smoke result')

    def test_string_zero_rejected(self):
        self.assert_private_error(lambda *_a, **_kw: SimpleNamespace(returncode='0'),
                                  'invalid smoke result')

    def test_fake_int_subclass_rejected(self):
        class PretendZero(int):
            pass
        self.assert_private_error(lambda *_a, **_kw: SimpleNamespace(returncode=PretendZero(0)),
                                  'invalid smoke result')

    def test_failed_numeric_exit_preserved(self):
        self.assert_private_error(lambda *_a, **_kw: SimpleNamespace(returncode=17),
                                  'exit code 17')

    def test_negative_exit_preserved(self):
        self.assert_private_error(lambda *_a, **_kw: SimpleNamespace(returncode=-9),
                                  'exit code -9')

    def test_timeout_bounds_checked_before_launch(self):
        for invalid in (-1, 0, 601, True, 1.5, '120', None):
            with self.subTest(invalid=invalid):
                runner = Mock()
                with self.assertRaises(SmokeRunError):
                    self.run_case(runner, timeout=invalid)
                runner.assert_not_called()

    def test_keyboard_interrupt_propagates(self):
        with self.assertRaises(KeyboardInterrupt):
            self.run_case(Mock(side_effect=KeyboardInterrupt()))

    def test_system_exit_propagates(self):
        with self.assertRaises(SystemExit):
            self.run_case(Mock(side_effect=SystemExit(73)))


if __name__ == "__main__":
    unittest.main()
