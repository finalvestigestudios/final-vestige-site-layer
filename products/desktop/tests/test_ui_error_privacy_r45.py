"""R45: private data must never be copied from an exception into a GUI error."""
from __future__ import annotations

import ast
from pathlib import Path
import unittest

from fvs_suite.ui_errors import safe_error_message


OPERATIONS = ("generate", "report", "review", "export", "backup", "restore")
SECRETS = (
    r"C:\\Users\\client\\Documents\\merger-secret.csv",
    "/home/customer/Tax Return 2026/top-secret.csv",
    "account=4123-PRIVATE-9999",
    "user@client.example / holder name",
    "=HYPERLINK(\"https://attacker.example/secret\")",
    "grant recipient name\nprivate-field",
)


class HostileError(ValueError):
    def __str__(self):
        raise AssertionError("The error renderer must never stringify exceptions")

    def __repr__(self):
        raise AssertionError("The error renderer must never repr exceptions")


class UiErrorPrivacyR45(unittest.TestCase):
    def test_every_action_uses_static_remediation(self):
        messages = [safe_error_message(ValueError("private"), operation=op)
                    for op in OPERATIONS]
        self.assertEqual(len(set(messages)), len(OPERATIONS))
        for message in messages:
            self.assertTrue(message.endswith("."))
            self.assertLess(len(message), 300)

    def test_secret_payloads_never_reach_any_dialog(self):
        for operation in OPERATIONS:
            for secret in SECRETS:
                for kind in (ValueError, OSError, UnicodeError):
                    with self.subTest(operation=operation, kind=kind.__name__):
                        message = safe_error_message(kind(secret), operation=operation)
                        self.assertNotIn(secret, message)
                        self.assertNotIn("PRIVATE", message)
                        self.assertNotIn("attacker.example", message)

    def test_no_exception_stringification(self):
        for operation in OPERATIONS:
            self.assertIn("validation", safe_error_message(HostileError(), operation=operation))

    def test_value_error_payload_invariance(self):
        for operation in OPERATIONS:
            a = safe_error_message(ValueError("row=1 secret"), operation=operation)
            b = safe_error_message(ValueError("row=2 secret"), operation=operation)
            self.assertEqual(a, b)

    def test_large_customer_value_is_not_processed(self):
        message = safe_error_message(ValueError("SENSITIVE" * 100_000), operation="generate")
        self.assertLess(len(message), 300)

    def test_known_validation_type(self):
        self.assertIn("validation", safe_error_message(ValueError("s"), operation="generate"))

    def test_unknown_type_returns_safe_general_diagnostic(self):
        self.assertIn("could not be completed", safe_error_message(RuntimeError("s"), operation="report"))

    def test_encoding_before_value_error(self):
        self.assertIn("UTF-8", safe_error_message(UnicodeDecodeError("utf-8", b"\xff", 0, 1, "bad"), operation="generate"))

    def test_missing_file_before_os_error(self):
        self.assertIn("not found", safe_error_message(FileNotFoundError("s"), operation="report"))

    def test_permission_before_os_error(self):
        self.assertIn("permissions", safe_error_message(PermissionError("s"), operation="backup"))

    def test_directory_before_os_error(self):
        self.assertIn("directory", safe_error_message(IsADirectoryError("s"), operation="report"))

    def test_other_os_error_does_not_echo_errno_path(self):
        error = OSError(5, "customer secret", "/tmp/private-payroll.csv")
        self.assertNotIn("private-payroll", safe_error_message(error, operation="export"))

    def test_action_whitelist_is_strict(self):
        for value in ("", "report../secret", "Generate", "unknown", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                safe_error_message(ValueError("secret"), operation=value)

    def test_repeatable(self):
        for operation in OPERATIONS:
            self.assertEqual(safe_error_message(ValueError("X"), operation=operation),
                             safe_error_message(ValueError("X"), operation=operation))

    def test_source_never_formats_raw_exception(self):
        source = Path(__file__).resolve().parents[1] / "fvs_suite" / "ui_errors.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        func = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "safe_error_message")
        for node in ast.walk(func):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, ("str", "repr", "format"))

    def test_application_and_review_dialogs_use_renderer(self):
        base = Path(__file__).resolve().parents[1] / "fvs_suite"
        if not all((base / name).is_file() for name in ("app.py", "review_ui.py")):
            self.skipTest("Requires full repository GUI sources; focused offline subset only")
        for file, expected in (("app.py", 2), ("review_ui.py", 5)):
            with self.subTest(file=file):
                source = (base / file).read_text(encoding="utf-8")
                ast.parse(source)
                self.assertIn("from .ui_errors import safe_error_message", source)
                self.assertNotIn("str(exc)", source)
                self.assertGreaterEqual(source.count("safe_error_message(exc,"), expected)


if __name__ == "__main__":
    unittest.main()
