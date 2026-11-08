"""R273 source-receipt decoder regressions; source-only, never Windows EXE QA."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "scripts" / "strict_source_receipt_r273.py"
spec = importlib.util.spec_from_file_location("strict_r273", MODULE)
strict = importlib.util.module_from_spec(spec)
spec.loader.exec_module(strict)


class StrictReceiptTests(unittest.TestCase):
    def rejected(self, payload):
        with self.assertRaises(strict.ReceiptJSONRejected) as caught:
            strict.loads_strict_receipt(payload)
        self.assertEqual(str(caught.exception), strict.SAFE_ERROR)
        self.assertIsNone(caught.exception.__cause__)
        self.assertIsNone(caught.exception.__context__)

    def test_valid_source_receipt(self):
        data = {"scope": "SOURCE_ONLY", "approved": False, "tests": [1, 2],
                "nested": {"count": 6, "status": "PASS"}}
        self.assertEqual(strict.loads_strict_receipt(json.dumps(data).encode()), data)

    def test_bytearray_supported_for_guard_read(self):
        self.assertEqual(strict.loads_strict_receipt(bytearray(b'{"x":1}')), {"x": 1})

    def test_empty_rejected(self):
        self.rejected(b"")

    def test_trailing_material_rejected(self):
        self.rejected(b'{"released":false} true')

    def test_top_level_duplicate_release_flag_rejected(self):
        self.rejected(b'{"released":true,"released":false}')

    def test_nested_duplicate_source_results_rejected(self):
        self.rejected(b'{"source_smoke":{"all_six_passed":false,"all_six_passed":true}}')

    def test_array_nested_duplicate_rejected(self):
        self.rejected(b'{"applications":[{"status":"FAILED","status":"PASS"}]}')

    def test_escaped_equivalent_field_names_rejected(self):
        self.rejected(b'{"released":true,"rele\\u0061sed":false}')

    def test_nonstandard_nan_rejected(self):
        self.rejected(b'{"test_count":NaN}')

    def test_nonstandard_positive_infinity_rejected(self):
        self.rejected(b'{"test_count":Infinity}')

    def test_nonstandard_negative_infinity_rejected(self):
        self.rejected(b'{"test_count":-Infinity}')

    def test_invalid_utf8_rejected(self):
        self.rejected(b'{"x":"\\xff"}')

    def test_private_path_not_reflected_in_error(self):
        secret = b'C:/private/customer/payroll-2026.csv'
        with self.assertRaises(strict.ReceiptJSONRejected) as caught:
            strict.loads_strict_receipt(b'{"private":"' + secret + b'","private":null}')
        self.assertNotIn(secret.decode(), str(caught.exception))
        self.assertIsNone(caught.exception.__context__)

    def test_non_byte_inputs_rejected(self):
        for bad in ('{}', {}, None, [], memoryview(b'{}')):
            with self.subTest(type=type(bad).__name__):
                self.rejected(bad)

    def test_valid_unicode_key_is_accepted(self):
        self.assertEqual(strict.loads_strict_receipt('{"café": 2}'.encode()), {'café': 2})

    def test_root_json_scalar_decoded_for_caller_schema_gate(self):
        self.assertEqual(strict.loads_strict_receipt(b'0'), 0)


if __name__ == "__main__":
    unittest.main()
