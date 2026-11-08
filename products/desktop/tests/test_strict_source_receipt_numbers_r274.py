"""R274: private source receipt JSON is integer-only; no float rounding or overflow.

Source-only synthetic regressions, not Windows PE, signing, malware or QD QA.
The actual producer emits only JSON integer counts and exact string hashes.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

DECODER = Path(__file__).resolve().parents[1] / "scripts" / "strict_source_receipt_r273.py"
spec = importlib.util.spec_from_file_location("strict_source_numbers_r274", DECODER)
strict = importlib.util.module_from_spec(spec)
spec.loader.exec_module(strict)


class SourceReceiptNumericTests(unittest.TestCase):
    def reject(self, value: bytes) -> None:
        with self.assertRaises(strict.ReceiptJSONRejected) as caught:
            strict.loads_strict_receipt(value)
        self.assertEqual(str(caught.exception), strict.SAFE_ERROR)
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)

    def test_integer_counts_preserved_exactly(self):
        self.assertEqual(strict.loads_strict_receipt(b'{"test_count":12345678901234567890}'),
                         {"test_count": 12345678901234567890})

    def test_zero_and_negative_integer_tokens_accepted_by_decoder(self):
        self.assertEqual(strict.loads_strict_receipt(b'{"a":0,"b":-17}'), {"a": 0, "b": -17})

    def test_boolean_flags_remain_boolean(self):
        self.assertEqual(strict.loads_strict_receipt(b'{"released":false,"qd_approved":false}'),
                         {"released": False, "qd_approved": False})

    def test_fractional_count_rejected(self):
        self.reject(b'{"test_count":0.5}')

    def test_decimal_form_whole_number_rejected(self):
        self.reject(b'{"test_count":18.0}')

    def test_positive_exponent_form_rejected(self):
        self.reject(b'{"test_count":1e2}')

    def test_negative_exponent_form_rejected(self):
        self.reject(b'{"test_count":1e-2}')

    def test_explicit_positive_exponent_rejected(self):
        self.reject(b'{"test_count":1E+2}')

    def test_float_overflow_positive_rejected(self):
        self.reject(b'{"synthetic_output_count":1e400}')

    def test_float_overflow_negative_rejected(self):
        self.reject(b'{"synthetic_output_count":-1e400}')

    def test_float_underflow_to_zero_rejected(self):
        self.reject(b'{"test_count":1e-9999}')

    def test_fractional_rounding_rejected(self):
        self.reject(b'{"test_count":0.12345678901234567890123456789012345}')

    def test_negative_zero_float_rejected(self):
        self.reject(b'{"test_count":-0.0}')

    def test_nested_ignored_metric_cannot_hide_float(self):
        self.reject(b'{"source_smoke":{"application_results":[{"synthetic_output_count":1e400}]}}')

    def test_plain_integer_in_nested_smoke_retained(self):
        self.assertEqual(strict.loads_strict_receipt(
            b'{"source_smoke":{"application_results":[{"synthetic_output_count":1}]}}'),
            {"source_smoke": {"application_results": [{"synthetic_output_count": 1}]}})

    def test_nonstandard_constant_still_rejected(self):
        self.reject(b'{"synthetic_output_count":NaN}')

    def test_duplicate_fields_still_rejected(self):
        self.reject(b'{"released":true,"released":false}')

    def test_private_numeric_error_never_echoes_payload(self):
        secret = b'C:/private/2026/customers.csv'
        with self.assertRaises(strict.ReceiptJSONRejected) as caught:
            strict.loads_strict_receipt(b'{"secret":"' + secret + b'","count":1e400}')
        self.assertNotIn(secret.decode('ascii'), str(caught.exception))
        self.assertIsNone(caught.exception.__context__)

    def test_isolated_child_uses_local_decoder_not_cwd_shadow(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "strict_source_receipt_r273.py").write_text(
                "raise RuntimeError('UNTRUSTED_IMPORT')\n", encoding="ascii")
            env = os.environ.copy()
            env["PYTHONPATH"] = tmp
            cmd = [sys.executable, "-I", "-c",
                   "import importlib.util,sys; "
                   "s=importlib.util.spec_from_file_location('trusted',sys.argv[1]); "
                   "m=importlib.util.module_from_spec(s); s.loader.exec_module(m); "
                   "print(m.loads_strict_receipt(b'{\"count\":7}')); "
                   "assert m.loads_strict_receipt(b'{\"count\":7}')=={'count':7}",
                   str(DECODER)]
            result = subprocess.run(cmd, cwd=tmp, env=env, stdin=subprocess.DEVNULL,
                                    capture_output=True, timeout=20, check=False)
            self.assertEqual(result.returncode, 0, "Isolated decoder child failed")
            self.assertIn(b"'count': 7", result.stdout)
            self.assertNotIn(b"UNTRUSTED_IMPORT", result.stderr)


if __name__ == "__main__":
    unittest.main()
