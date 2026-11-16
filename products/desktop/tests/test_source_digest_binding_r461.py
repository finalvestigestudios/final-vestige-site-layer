"""R461: detect full import-tree drift and forged success from another checkout."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import offline_source_binding_r461 as binding
import offline_regression_gate_r459 as gate


GOOD = 'a' * 64
OTHER = 'b' * 64
APPS = ('ledger', 'invoices', 'spend', 'policy', 'grants', 'procurement')
LAUNCHERS = ('LedgerDiffLite.py', 'InvoiceTwinScout.py', 'SpendMapLite.py',
             'PolicyDeltaDesk.py', 'GrantAuditStudioPro.py',
             'ProcureGuardStudioPro.py')


def receipt(*, digest=GOOD, **updates):
    item = {'schema': 'fvs-source-smoke-r408-v1', 'source_sha256': digest,
            'evidence': 'SOURCE_ONLY_NOT_WINDOWS_BINARY',
            'tests': [{'app': app, 'normal': 'pass', 'optimized': 'pass'}
                      for app in APPS], 'passed': 12, 'required': 12,
            'release_authorized': False}
    item.update(updates)
    return json.dumps(item, separators=(',', ':')).encode('ascii')


class SourceDigestBindingR461(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='fvs-r461-')
        self.addCleanup(temporary.cleanup)
        self.desktop = Path(temporary.name)
        for sub in ('launchers', 'fvs_suite'):
            (self.desktop / sub).mkdir()
        (self.desktop / 'fvs_suite' / '__init__.py').write_text('# local\n')
        (self.desktop / 'fvs_suite' / 'launcher.py').write_text('def launch(app): pass\n')
        (self.desktop / 'offline_source_smoke_r408.py').write_text('# source\n')
        for app, name in zip(APPS, LAUNCHERS):
            (self.desktop / 'launchers' / name).write_text(
                'from fvs_suite.launcher import launch\n'
                'if __name__ == "__main__":\n'
                f'    launch("{app}")\n', encoding='utf-8')

    def test_native_six_source_digest_is_repeatable(self):
        before = binding.verified_six_app_digest(self.desktop)
        self.assertEqual(before, binding.verified_six_app_digest(self.desktop))
        self.assertEqual(len(before), 64)

    def test_change_to_unlisted_engine_changes_digest(self):
        before = binding.verified_six_app_digest(self.desktop)
        (self.desktop / 'fvs_suite' / 'new_engine.py').write_text('SENTINEL=1\n')
        self.assertNotEqual(before, binding.verified_six_app_digest(self.desktop))

    def test_change_to_launcher_changes_digest(self):
        before = binding.verified_six_app_digest(self.desktop)
        launcher = self.desktop / 'launchers' / LAUNCHERS[0]
        launcher.write_text(launcher.read_text() + '# changed\n')
        self.assertNotEqual(before, binding.verified_six_app_digest(self.desktop))

    def test_binary_import_artifact_rejected(self):
        (self.desktop / 'fvs_suite' / 'unhashed.pyc').write_bytes(b'not-trusted')
        with self.assertRaises(binding.SourceBindingError):
            binding.verified_six_app_digest(self.desktop)

    def test_symlink_import_rejected_when_supported(self):
        target = self.desktop / 'fvs_suite' / 'launcher.py'
        link = self.desktop / 'fvs_suite' / 'symlink.py'
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError):
            # Windows without symlink privilege: do not skip the entire
            # source-only regression gate, which rejects skipped methods.
            return
        with self.assertRaises(binding.SourceBindingError):
            binding.verified_six_app_digest(self.desktop)

    def test_private_source_failure_not_exposed(self):
        with patch.object(binding, 'source_digest',
                          side_effect=binding.SourceGateError('CLIENT_PRIVATE.csv')):
            with self.assertRaises(binding.SourceBindingError) as caught:
                binding.verified_six_app_digest(self.desktop)
        self.assertNotIn('CLIENT_PRIVATE', str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)

    def test_invalid_native_source_digests_fail_closed(self):
        for invalid in (None, True, 12, b'a' * 64, 'Z' * 64, 'a' * 63):
            with self.subTest(value=str(invalid)[:12]):
                with patch.object(binding, 'source_digest', return_value=invalid):
                    with self.assertRaises(binding.SourceBindingError):
                        binding.verified_six_app_digest(self.desktop)

    def test_six_app_receipt_bound_to_expected_source(self):
        self.assertEqual(binding.require_bound_six_app_smokes(receipt(), GOOD), 12)
        with self.assertRaises(binding.SourceBindingError):
            binding.require_bound_six_app_smokes(receipt(), OTHER)

    def test_child_digest_spoofed_from_old_checkout_rejected(self):
        with self.assertRaises(binding.SourceBindingError):
            binding.require_bound_six_app_smokes(receipt(digest=OTHER), GOOD)

    def test_invalid_expected_digest_rejected(self):
        for value in (True, 0, None, '', 'a' * 63, 'G' * 64):
            with self.subTest(value=str(value)[:12]):
                with self.assertRaises(binding.SourceBindingError):
                    binding.require_bound_six_app_smokes(receipt(), value)

    def test_failed_or_unreleased_modes_not_mistaken_for_pass(self):
        bad = json.loads(receipt())
        bad['tests'][5]['optimized'] = 'fail'
        with self.assertRaises(binding.SourceBindingError):
            binding.require_bound_six_app_smokes(json.dumps(bad).encode(), GOOD)
        with self.assertRaises(binding.SourceBindingError):
            binding.require_bound_six_app_smokes(receipt(release_authorized=True), GOOD)

    def test_malformed_and_oversized_private_receipts_safely_rejected(self):
        for raw in (b'', b'CLIENT_REPORT_PRIVATE', b'{' + b'x' * 5000):
            with self.assertRaises(binding.SourceBindingError) as caught:
                binding.require_bound_six_app_smokes(raw, GOOD)
            self.assertNotIn('CLIENT_REPORT_PRIVATE', str(caught.exception))

    def test_parent_passes_pre_test_digest_to_smoke_child(self):
        observed = []
        with patch.object(gate, '_source_fingerprint', return_value=OTHER), \
             patch.object(gate, 'verified_six_app_digest', return_value=GOOD), \
             patch.object(gate, '_run_tests', return_value=(10, 140)), \
             patch.object(gate, '_run_smokes', side_effect=lambda _, digest:
                          observed.append(digest) or 12):
            result = gate.run_gate(self.desktop)
        self.assertEqual(observed, [GOOD])
        self.assertEqual(result['regression_mode_runs'], 10)
        self.assertFalse(result['release_authorized'])

    def test_parent_rejects_engine_mutation_during_regressions(self):
        with patch.object(gate, '_source_fingerprint', return_value=OTHER), \
             patch.object(gate, 'verified_six_app_digest',
                          side_effect=[GOOD, OTHER]), \
             patch.object(gate, '_run_tests', return_value=(10, 140)), \
             patch.object(gate, '_run_smokes') as smoke:
            with self.assertRaises(gate.LocalGateError):
                gate.run_gate(self.desktop)
        smoke.assert_not_called()

    def test_parent_rejects_engine_mutation_during_smokes(self):
        with patch.object(gate, '_source_fingerprint', return_value=OTHER), \
             patch.object(gate, 'verified_six_app_digest',
                          side_effect=[GOOD, GOOD, OTHER]), \
             patch.object(gate, '_run_tests', return_value=(10, 140)), \
             patch.object(gate, '_run_smokes', return_value=12):
            with self.assertRaises(gate.LocalGateError):
                gate.run_gate(self.desktop)


if __name__ == '__main__':
    unittest.main()
