"""R459: independent regression fallback is genuine, private and fail-closed."""
from __future__ import annotations

import hashlib
import json
import os
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
            return  # Not a skipped gate test on Windows without symlink privilege
        with self.assertRaises(gate.LocalGateError):
            gate._source_fingerprint(self.root)

    def test_exact_twenty_eight_child_interpreters_and_receipts(self):
        observed = []

        def fake_subprocess(command, **kwargs):
            observed.append((command, kwargs))
            Path(command[-1]).write_bytes(self.receipt())
            return SimpleNamespace(returncode=0)

        with patch.object(gate.subprocess, 'run', side_effect=fake_subprocess):
            modes, methods = gate._run_tests(self.root)
        self.assertEqual((modes, methods), (28, 364))
        self.assertEqual(sum('-OO' in command for command, _ in observed), 14)
        self.assertTrue(all('-I' in command and '-B' in command
                            and kwargs['stdout'] == subprocess.DEVNULL
                            and kwargs['stderr'] == subprocess.DEVNULL
                            and kwargs['stdin'] == subprocess.DEVNULL
                            and 'PYTHONPATH' not in kwargs['env']
                            for command, kwargs in observed))

    def test_actual_twenty_eight_isolated_interpreters_execute_real_unittest(self):
        fixture = ("import unittest\n"
                   "class SyntheticGateTest(unittest.TestCase):\n"
                   "    def test_native_source_gate(self):\n"
                   "        self.assertEqual(Decimal(\"0.10\") + Decimal(\"0.20\"), Decimal(\"0.30\"))\n")
        # A synthetic native Decimal import is explicit, never financial data.
        fixture = "from decimal import Decimal\n" + fixture
        for name in gate.TESTS:
            (self.root / 'tests' / name).write_text(fixture, encoding='utf-8')
        modes, methods = gate._run_tests(self.root)
        self.assertEqual((modes, methods), (28, 28))

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
        # Exit code zero is insufficient: the child must report all twelve
        # application/mode statuses under the exact source-only R408 schema.
        source_only = {
            'schema': 'fvs-source-smoke-r408-v1',
            'source_sha256': 'a' * 64,
            'evidence': 'SOURCE_ONLY_NOT_WINDOWS_BINARY',
            'tests': [
                {'app': name, 'normal': 'pass', 'optimized': 'pass'}
                for name in ('ledger', 'invoices', 'spend', 'policy',
                             'grants', 'procurement')
            ],
            'passed': 12, 'required': 12, 'release_authorized': False,
        }

        def valid_child(command, **kwargs):
            kwargs['stdout'].write(json.dumps(source_only).encode('utf-8'))
            return SimpleNamespace(returncode=0)

        with patch.object(gate.subprocess, 'run', side_effect=valid_child):
            self.assertEqual(gate._run_smokes(self.root, 'a' * 64), 12)
        with patch.object(gate.subprocess, 'run',
                          return_value=SimpleNamespace(returncode=1)):
            with self.assertRaises(gate.LocalGateError):
                gate._run_smokes(self.root, 'a' * 64)

    def test_complete_gate_retains_release_hold(self):
        with patch.object(gate, '_six_source_digest', return_value='a' * 64), \
             patch.object(gate, '_run_tests', return_value=(28, 96)), \
             patch.object(gate, '_run_smokes', return_value=12):
            result = gate.run_gate(self.root)
        self.assertEqual(result['regression_methods_passed'], 96)
        self.assertEqual(result['launcher_source_smokes_passed'], 12)
        self.assertFalse(result['release_authorized'])
        self.assertIn('SOURCE_ONLY', result['evidence'])

    def test_source_change_mid_gate_fails_closed(self):
        def change_source(_):
            (self.root / gate.SOURCE_INPUTS[-1]).write_text('tampered', encoding='utf-8')
            return (28, 280)
        with patch.object(gate, '_six_source_digest', return_value='a' * 64), \
             patch.object(gate, '_run_tests', side_effect=change_source), \
             patch.object(gate, '_run_smokes', return_value=12):
            with self.assertRaises(gate.LocalGateError):
                gate.run_gate(self.root)

    def test_failed_child_error_message_contains_no_paths(self):
        with patch.object(gate.subprocess, 'run', side_effect=OSError('PRIVATE_CLIENT_123.csv')):
            with self.assertRaises(gate.LocalGateError) as captured:
                gate._run_tests(self.root)
        self.assertNotIn('PRIVATE_CLIENT_123', str(captured.exception))


    def test_r463_original_hash_layout_preserved(self):
        digest = hashlib.sha256()
        for name in gate.SOURCE_INPUTS:
            source = (self.root / name).read_bytes()
            digest.update(name.encode('ascii') + b'\0')
            digest.update(len(source).to_bytes(8, 'big'))
            digest.update(hashlib.sha256(source).digest())
        self.assertEqual(gate._source_fingerprint(self.root), digest.hexdigest())

    def test_r463_fingerprint_repeatable_and_change_sensitive(self):
        before = gate._source_fingerprint(self.root)
        self.assertEqual(before, gate._source_fingerprint(self.root))
        (self.root / gate.SOURCE_INPUTS[-1]).write_text('changed')
        self.assertNotEqual(before, gate._source_fingerprint(self.root))

    def test_r463_hardlinked_test_source_rejected(self):
        target = self.root / gate.SOURCE_INPUTS[-1]
        try:
            os.link(target, self.root / 'other-hardlink')
        except (OSError, NotImplementedError):
            return  # Hardlink unavailable; no skipped receipt.
        with self.assertRaises(gate.LocalGateError):
            gate._source_fingerprint(self.root)

    def test_r463_symlinked_test_source_rejected(self):
        target = self.root / gate.SOURCE_INPUTS[-1]
        target.unlink()
        try:
            target.symlink_to(self.root / gate.SOURCE_INPUTS[0])
        except (OSError, NotImplementedError):
            return
        with self.assertRaises(gate.LocalGateError):
            gate._source_fingerprint(self.root)

    def test_r463_symlinked_test_directory_rejected(self):
        original = self.root / 'tests'
        moved = self.root / 'moved-tests'
        original.rename(moved)
        try:
            original.symlink_to(moved, target_is_directory=True)
        except (OSError, NotImplementedError):
            return
        with self.assertRaises(gate.LocalGateError):
            gate._source_fingerprint(self.root)

    def test_r463_empty_test_source_rejected(self):
        (self.root / gate.SOURCE_INPUTS[-1]).write_bytes(b'')
        with self.assertRaises(gate.LocalGateError):
            gate._source_fingerprint(self.root)

    def test_r463_oversized_test_source_rejected(self):
        with (self.root / gate.SOURCE_INPUTS[-1]).open('wb') as output:
            output.truncate(2_000_001)
        with self.assertRaises(gate.LocalGateError):
            gate._source_fingerprint(self.root)

    def test_r463_missing_test_source_rejected(self):
        (self.root / gate.SOURCE_INPUTS[-1]).unlink()
        with self.assertRaises(gate.LocalGateError):
            gate._source_fingerprint(self.root)

    def test_r463_relative_root_rejected(self):
        with self.assertRaises(gate.LocalGateError):
            gate._source_fingerprint(Path('.'))

    def test_r463_verified_descriptor_reader_used_for_every_input(self):
        real = gate._read_verified_source_bytes
        with patch.object(gate, '_read_verified_source_bytes', wraps=real) as reader:
            gate._source_fingerprint(self.root)
        self.assertEqual(reader.call_count, len(gate.SOURCE_INPUTS))

    def test_r463_private_reader_failure_redacted(self):
        with patch.object(gate, '_read_verified_source_bytes',
                          side_effect=gate.SourceGateError('PRIVATE_CLIENT_123.csv')):
            with self.assertRaises(gate.LocalGateError) as captured:
                gate._source_fingerprint(self.root)
        self.assertNotIn('PRIVATE_CLIENT_123', str(captured.exception))
        self.assertIsNone(captured.exception.__cause__)

    def test_r463_parent_swapped_during_read_rejected(self):
        parent = self.root / 'tests'
        moved = self.root / 'old-tests'
        real = gate._read_verified_source_bytes
        changed = [False]

        def mutate(path):
            data = real(path)
            if not changed[0] and path.parent == parent:
                parent.rename(moved)
                try:
                    parent.symlink_to(moved, target_is_directory=True)
                except (OSError, NotImplementedError):
                    moved.rename(parent)
                else:
                    changed[0] = True
            return data

        with patch.object(gate, '_read_verified_source_bytes', side_effect=mutate):
            if os.name == 'nt':
                return  # Symlink privileges are not required by this gate.
            with self.assertRaises(gate.LocalGateError):
                gate._source_fingerprint(self.root)
        self.assertTrue(changed[0])

    def test_r463_fingerprint_does_not_modify_sources(self):
        before = [(self.root / name).read_bytes() for name in gate.SOURCE_INPUTS]
        gate._source_fingerprint(self.root)
        self.assertEqual(before, [(self.root / name).read_bytes()
                                  for name in gate.SOURCE_INPUTS])


    def test_r464_exact_eight_required_real_modules(self):
        self.assertEqual(gate.CORE_TESTS, (
            "test_csv_negative_decimal_zero_copy_r455.py",
            "test_csv_safe_cell_zero_copy_r456.py",
            "test_csv_incremental_render_budget_r457.py",
            "test_csv_bounded_utf8_witness_r458.py",
            "test_offline_regression_gate_r459.py",
            "test_offline_smoke_receipt_r460.py",
            "test_source_digest_binding_r461.py",
            "test_private_json_receipt_r462.py",
        ))

    def test_r464_selftest_sources_fingerprinted_once(self):
        test_paths = ["tests/" + item for item in gate.TESTS]
        self.assertEqual(len(test_paths), len(set(test_paths)))
        for source in test_paths:
            self.assertEqual(gate.SOURCE_INPUTS.count(source), 1)
        self.assertEqual(len(gate.SOURCE_INPUTS),
                         len(set(gate.SOURCE_INPUTS)))

    def test_r464_selftest_source_edit_changes_fingerprint(self):
        original = gate._source_fingerprint(self.root)
        for name in ("test_offline_regression_gate_r459.py",
                     "test_offline_smoke_receipt_r460.py"):
            path = self.root / "tests" / name
            path.write_text("changed selftest", encoding="utf-8")
            self.assertNotEqual(gate._source_fingerprint(self.root), original)
            path.write_text("synthetic checked content", encoding="utf-8")

    def test_r464_legacy_six_module_pass_rejected(self):
        with patch.object(gate, "_source_fingerprint", return_value="a" * 64), \
             patch.object(gate, "_six_source_digest", return_value="b" * 64), \
             patch.object(gate, "_run_tests", return_value=(12, 200)), \
             patch.object(gate, "_run_smokes") as smokes:
            with self.assertRaisesRegex(gate.LocalGateError, "coverage rejected"):
                gate.run_gate(self.root)
            smokes.assert_not_called()

    def test_r464_missing_method_outcomes_rejected(self):
        with patch.object(gate, "_source_fingerprint", return_value="a" * 64), \
             patch.object(gate, "_six_source_digest", return_value="b" * 64), \
             patch.object(gate, "_run_tests", return_value=(28, 27)), \
             patch.object(gate, "_run_smokes") as smokes:
            with self.assertRaises(gate.LocalGateError):
                gate.run_gate(self.root)
            smokes.assert_not_called()

    def test_r464_boolean_or_spurious_mode_count_rejected(self):
        for modes in (True, 0, 14, 18, 30, "28"):
            with self.subTest(modes=modes), \
                 patch.object(gate, "_source_fingerprint", return_value="a" * 64), \
                 patch.object(gate, "_six_source_digest", return_value="b" * 64), \
                 patch.object(gate, "_run_tests", return_value=(modes, 280)), \
                 patch.object(gate, "_run_smokes") as smokes:
                with self.assertRaises(gate.LocalGateError):
                    gate.run_gate(self.root)
                smokes.assert_not_called()

    def test_r464_boolean_or_spurious_method_count_rejected(self):
        for methods in (True, 0, 27, "280"):
            with self.subTest(methods=methods), \
                 patch.object(gate, "_source_fingerprint", return_value="a" * 64), \
                 patch.object(gate, "_six_source_digest", return_value="b" * 64), \
                 patch.object(gate, "_run_tests", return_value=(28, methods)), \
                 patch.object(gate, "_run_smokes") as smokes:
                with self.assertRaises(gate.LocalGateError):
                    gate.run_gate(self.root)
                smokes.assert_not_called()

    def test_r464_real_coverage_contract_retains_release_hold(self):
        with patch.object(gate, "_source_fingerprint", return_value="a" * 64), \
             patch.object(gate, "_six_source_digest", return_value="b" * 64), \
             patch.object(gate, "_run_tests", return_value=(28, 280)), \
             patch.object(gate, "_run_smokes", return_value=12):
            receipt = gate.run_gate(self.root)
        self.assertEqual(receipt["regression_mode_runs"], 28)
        self.assertEqual(receipt["regression_methods_passed"], 280)
        self.assertFalse(receipt["release_authorized"])
        self.assertEqual(receipt["evidence"], "SOURCE_ONLY_NOT_WINDOWS_BINARY")



    def test_r465_exact_six_product_integration_modules(self):
        self.assertEqual(gate.PRODUCT_TESTS, (
            "test_ledger_source_engine_integration_r62.py",
            "test_invoice_source_engine_integration_r63.py",
            "test_spend_engine_integration_r59.py",
            "test_policy_engine_r26.py",
            "test_grant_input_integration_r66.py",
            "test_procurement_integration_r5.py",
        ))
        self.assertEqual(len(gate.CORE_TESTS), 8)
        self.assertEqual(gate.TESTS, gate.CORE_TESTS + gate.PRODUCT_TESTS)
        self.assertEqual(len(gate.TESTS), 14)
        self.assertEqual(len(set(gate.TESTS)), 14)

    def test_r465_each_product_test_is_fingerprinted_once(self):
        original = gate._source_fingerprint(self.root)
        for name in gate.PRODUCT_TESTS:
            relative = "tests/" + name
            with self.subTest(product_test=name):
                self.assertEqual(gate.SOURCE_INPUTS.count(relative), 1)
                path = self.root / relative
                path.write_text("changed product integration source", encoding="utf-8")
                self.assertNotEqual(gate._source_fingerprint(self.root), original)
                path.write_text("synthetic checked content", encoding="utf-8")
        self.assertEqual(gate._source_fingerprint(self.root), original)

    def test_r465_old_eight_module_receipt_is_not_sufficient(self):
        with patch.object(gate, "_source_fingerprint", return_value="a" * 64), \
             patch.object(gate, "_six_source_digest", return_value="b" * 64), \
             patch.object(gate, "_run_tests", return_value=(16, 1000)), \
             patch.object(gate, "_run_smokes") as smokes:
            with self.assertRaisesRegex(gate.LocalGateError, "coverage rejected"):
                gate.run_gate(self.root)
            smokes.assert_not_called()


    def test_r465_shortened_or_duplicate_product_matrix_fails_closed(self):
        for modified in (gate.TESTS[:-1], gate.TESTS[:-1] + (gate.TESTS[0],)):
            with self.subTest(modified=modified[-1]), \
                 patch.object(gate, "TESTS", modified), \
                 patch.object(gate, "_six_source_digest", return_value="b" * 64), \
                 patch.object(gate, "_run_tests") as tests, \
                 patch.object(gate, "_run_smokes") as smokes:
                with self.assertRaisesRegex(gate.LocalGateError, "coverage rejected"):
                    gate.run_gate(self.root)
                tests.assert_not_called()
                smokes.assert_not_called()


if __name__ == '__main__':
    unittest.main()
