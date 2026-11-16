"""R462: ambiguous private CI receipts must never pass six-app source gates."""
from __future__ import annotations

import json
import unittest

from offline_json_receipt_r462 import PrivateReceiptJSONError, load_private_receipt
import offline_regression_gate_r459 as gate
import offline_smoke_receipt_r460 as smoke
import offline_source_binding_r461 as binding

GOOD = 'a' * 64
APPS = ('ledger', 'invoices', 'spend', 'policy', 'grants', 'procurement')


def regression():
    return b'{"tests":13,"failures":0,"errors":0,"skipped":0,"expected":13}'


def six_apps():
    return {'schema': 'fvs-source-smoke-r408-v1', 'source_sha256': GOOD,
            'evidence': 'SOURCE_ONLY_NOT_WINDOWS_BINARY', 'passed': 12,
            'required': 12, 'release_authorized': False,
            'tests': [{'app': app, 'normal': 'pass', 'optimized': 'pass'}
                      for app in APPS]}


def encoded(item):
    return json.dumps(item, separators=(',', ':')).encode('ascii')


class StrictPrivateReceiptR462(unittest.TestCase):
    def reject(self, data):
        with self.assertRaises(PrivateReceiptJSONError) as captured:
            load_private_receipt(data)
        self.assertEqual(str(captured.exception),
                         'Ambiguous private source receipt rejected')
        self.assertIsNone(captured.exception.__cause__)

    def test_valid_small_regression_json(self):
        self.assertEqual(load_private_receipt(regression())['expected'], 13)

    def test_valid_six_app_nested_json(self):
        self.assertEqual(len(load_private_receipt(encoded(six_apps()))['tests']), 6)

    def test_duplicate_top_level_same_value_rejected(self):
        self.reject(b'{"passed":12,"passed":12}')

    def test_duplicate_top_level_opposing_values_rejected(self):
        self.reject(b'{"release_authorized":true,"release_authorized":false}')

    def test_duplicate_nested_app_rejected(self):
        self.reject(b'{"tests":[{"app":"grants","app":"ledger"}]}')

    def test_duplicate_nested_mode_rejected(self):
        self.reject(b'{"tests":[{"normal":"fail","normal":"pass"}]}')

    def test_duplicate_deeply_nested_rejected(self):
        self.reject(b'{"a":{"b":[{"c":1,"c":2}]}}')

    def test_escaped_key_duplicate_rejected(self):
        self.reject(b'{"source_sha256":"a","source\u005fsha256":"b"}')

    def test_nul_payload_safe_fixed_failure(self):
        self.reject(b'{"PRIVATE_ACCOUNT_213":1}\x00')

    def test_nonfinite_nan_rejected(self):
        self.reject(b'{"tests":NaN}')

    def test_nonfinite_infinity_rejected(self):
        self.reject(b'{"tests":Infinity}')

    def test_negative_infinity_rejected(self):
        self.reject(b'{"tests":-Infinity}')

    def test_invalid_utf8_rejected(self):
        self.reject(b'{"private":"\xff"}')

    def test_trailing_json_rejected(self):
        self.reject(b'{}{}')

    def test_partial_json_rejected(self):
        self.reject(b'{"tests":')

    def test_nonbyte_inputs_rejected(self):
        for raw in ('{}', bytearray(b'{}'), None, memoryview(b'{}')):
            with self.subTest(type=type(raw).__name__):
                self.reject(raw)

    def test_case_distinct_fields_not_wrongly_collapsed(self):
        self.assertEqual(load_private_receipt(b'{"A":1,"a":2}'), {'A': 1, 'a': 2})

    def test_regression_consumer_accepts_valid_exact_receipt(self):
        self.assertEqual(gate._validate_receipt(regression()), 13)

    def test_regression_consumer_rejects_duplicate_failure_count(self):
        data = regression().replace(b'"failures":0',
                                    b'"failures":1,"failures":0')
        with self.assertRaises(gate.LocalGateError):
            gate._validate_receipt(data)

    def test_regression_consumer_rejects_duplicate_discovery_count(self):
        data = regression().replace(b'"tests":13', b'"tests":0,"tests":13')
        with self.assertRaises(gate.LocalGateError):
            gate._validate_receipt(data)

    def test_smoke_consumer_accepts_exact_six_apps(self):
        self.assertEqual(smoke.require_six_app_smokes(encoded(six_apps())), 12)

    def test_smoke_consumer_rejects_duplicate_release_flag(self):
        data = encoded(six_apps()).replace(
            b'"release_authorized":false',
            b'"release_authorized":true,"release_authorized":false')
        with self.assertRaises(smoke.SourceSmokeReceiptError):
            smoke.require_six_app_smokes(data)

    def test_smoke_consumer_rejects_duplicate_nested_status(self):
        data = encoded(six_apps()).replace(
            b'"normal":"pass"', b'"normal":"fail","normal":"pass"', 1)
        with self.assertRaises(smoke.SourceSmokeReceiptError):
            smoke.require_six_app_smokes(data)

    def test_binding_consumer_rejects_duplicate_digest(self):
        data = encoded(six_apps()).replace(
            b'"source_sha256":"' + GOOD.encode() + b'"',
            b'"source_sha256":"' + b'b'*64 + b'","source_sha256":"' + GOOD.encode() + b'"')
        with self.assertRaises(binding.SourceBindingError):
            binding.require_bound_six_app_smokes(data, GOOD)

    def test_binding_consumer_accepts_exact_digest(self):
        self.assertEqual(binding.require_bound_six_app_smokes(
            encoded(six_apps()), GOOD), 12)


if __name__ == '__main__':
    unittest.main()
