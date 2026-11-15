"""R459: independent regression fallback is genuine, private and fail-closed."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import offline_regression_gate_r459 as gate


class OfflineRegressionGateR459(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='fvs-r459-tests-')
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        for source in gate.SOURCE_INPUTS:
            path = self.root / source
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('synthetic checked content', encoding='utf-8')

    def receipt(self, **changes):
        item = dict(tests=13, failures=0, errors=0, skipped=0, expected=13)
        item.update(changes)
        return json.dumps(item).encode('ascii')

    def test_success_receipt_counts_methods(self):
        self.assertEqual(gate._validate_receipt(self.receipt()), 13)

    def test_zero_test_discovery_is_not_success(self):
        with self.assertRaises(gate.LocalGateError):
            gate._validate_receipt(self.receipt(tests=0, expected=0))

    def test_skipped_tests_are_not_success(self):
        with self.assertRaises(gate.LocalGateError):
            gate._validate_receipt(self.receipt(skipped=1))

    def test_partial_test_execution_is_not_success(self):
        with self.assertRaises(gate.LocalGateError):
            gate._validate_receipt(self.receipt(tests=12))

    def test_non_native_bool_count_is_not_success(self):
        with self.assertRaises(gate.LocalGateError):
            gate._validate_receipt(self.receipt(failures=True))

    def test_malformed_or_oversized_receipt_is_not_success(self):
        for raw in (b'not-json', b'{}', b'{' + b'x' * 1100, self.receipt(unexpected=1)):
            with self.subTest(raw=raw[:20]):
                with self.assertRaises(gate.LocalGateError):
                    gate._validate_receipt(raw)

    def test_local_source_fingerprint_repeatable(self):
        first = gate._source_fingerprint(self.root)
        self.assertEqual(first, gate._source_fingerprint(self.root))
        self.assertEqual(len(first), 64)
        (self.root / gate.SOURCE_INPUTS[-1]).write_text('changed', encoding='utf-8')
        self.assertNotEqual(first, gate._source_fingerprint(self.root))

    def test_missing_input_rejected(self):
        (self.root / gate.SOURCE_INPUTS[-1]).unlink()
        with self.assertRaises(gate.LocalGateError):
            gate._source_fingerprint(self.root)

    def test_symlink_source_rejected(self):
        path = self.root / gate.SOURCE_INPUTS[-1]
        path.unlink()
        try:
            path.symlink_to(self.root / gate.SOURCE_INPUTS[0])
        except (OSError, NotImplementedError):
            self.skipTest('Local OS cannot create symlinks')
        with self.assertRaises(gate.LocalGateError):
            gate._source_fingerprint(self.root)

    def test_exact_eight_child_interpreters_and_receipts(self):
        observed = []

        def fake_subprocess(command, **kwargs):
            observed.append((command, kwargs))
            Path(command[-1]).write_bytes(self.receipt())
            return SimpleNamespace(returncode=0)

        with patch.object(gate.subprocess, 'run', side_effect=fake_subprocess):
            modes, methods = gate._run_tests(self.root)
        self.assertEqual((modes, methods), (8, 104))
        self.assertEqual(sum('-OO' in command for command, _ in observed), 4)
        self.assertTrue(all('-I' in command and '-B' in command
                            and kwargs['stdout'] == subprocess.DEVNULL
                            and kwargs['stderr'] == subprocess.DEVNULL
                            and kwargs['stdin'] == subprocess.DEVNULL
                            and 'PYTHONPATH' not in kwargs['env']
                            for command, kwargs in observed))

    def test_actual_eight_isolated_interpreters_execute_real_unittest(self):
        fixture = ("import unittest\n"
                   "class SyntheticGateTest(unittest.TestCase):\n"
                   "    def test_native_source_gate(self):\n"
                   "        self.assertEqual(Decimal(\\\"0.10\\\") + Decimal(\\\"0.20\\\"), Decimal(\\\"0.30\\\"))\n")
        # A synthetic native Decimal import is explicit, never financial data.
        fixture = "from decimal import Decimal\n" + fixture
        for name in gate.TESTS:
            (self.root / 'tests' / name).write_text(fixture, encoding='utf-8')
        modes, methods = gate._run_tests(self.root)
        self.assertEqual((modes, methods), (8, 8))

    def test_actual_zero_discovery_fails_before_false_receipt(self):
        for name in gate.TESTS:
            (self.root / 'tests' / name).write_text('pass\n', encoding='utf-8')
        with self.assertRaises(gate.LocalGateError):
            gate._run_tests(self.root)

    def test_zero_method_child_false_positive_refused(self):
        def fake_subprocess(command, **kwargs):
            Path(command[-1]).write_bytes(self.receipt(tests=0, expected=0))
            return SimpleNamespace(returncode=0)
        with patch.object(gate.subprocess, 'run', side_effect=fake_subprocess):
            with self.assertRaises(gate.LocalGateError):
                gate._run_tests(self.root)

    def test_nonzero_test_child_does_not_claim_pass(self):
        with patch.object(gate.subprocess, 'run', return_value=SimpleNamespace(returncode=2)):
            with self.assertRaises(gate.LocalGateError):
                gate._run_tests(self.root)

    def test_source_smoke_requires_real_gate_success(self):
        with patch.object(gate.subprocess, 'run', return_value=SimpleNamespace(returncode=0)):
            self.assertEqual(gate._run_smokes(self.root), 12)
        with patch.object(gate.subprocess, 'run', return_value=SimpleNamespace(returncode=1)):
            with self.assertRaises(gate.LocalGateError):
                gate._run_smokes(self.root)

    def test_complete_gate_retains_release_hold(self):
        with patch.object(gate, '_run_tests', return_value=(8, 96)), \
             patch.object(gate, '_run_smokes', return_value=12):
            result = gate.run_gate(self.root)
        self.assertEqual(result['regression_methods_passed'], 96)
        self.assertEqual(result['launcher_source_smokes_passed'], 12)
        self.assertFalse(result['release_authorized'])
        self.assertIn('SOURCE_ONLY', result['evidence'])

    def test_source_change_mid_gate_fails_closed(self):
        def change_source(_):
            (self.root / gate.SOURCE_INPUTS[-1]).write_text('tampered', encoding='utf-8')
            return (8, 80)
        with patch.object(gate, '_run_tests', side_effect=change_source), \
             patch.object(gate, '_run_smokes', return_value=12):
            with self.assertRaises(gate.LocalGateError):
                gate.run_gate(self.root)

    def test_failed_child_error_message_contains_no_paths(self):
        with patch.object(gate.subprocess, 'run', side_effect=OSError('PRIVATE_CLIENT_123.csv')):
            with self.assertRaises(gate.LocalGateError) as captured:
                gate._run_tests(self.root)
        self.assertNotIn('PRIVATE_CLIENT_123', str(captured.exception))


if __name__ == '__main__':
    unittest.main()
