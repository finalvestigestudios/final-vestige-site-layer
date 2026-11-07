"""R247: premium review must clear displayed evidence when entitlement fails."""
from __future__ import annotations

import ast
from pathlib import Path
import sys
import unittest

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))
from fvs_suite.review_target import revalidate_or_revoke


class EntitlementRevocationR247Tests(unittest.TestCase):
    def test_valid_entitlement_does_not_scrub_or_repeat_check(self):
        calls = []
        proof = object()
        self.assertTrue(revalidate_or_revoke(
            lambda: calls.append("verify") or proof,
            lambda: calls.append("scrub")))
        self.assertEqual(calls, ["verify"])

    def test_explicit_false_denies_and_scrubs(self):
        events = []
        self.assertFalse(revalidate_or_revoke(lambda: False,
                                              lambda: events.append("scrub")))
        self.assertEqual(events, ["scrub"])

    def test_each_expected_verification_exception_denies(self):
        for kind in (ValueError, OSError, UnicodeError):
            with self.subTest(error=kind):
                events = []
                def deny():
                    events.append("verify")
                    raise kind("CLIENT_A_PRIVATE_PATH.csv")
                self.assertFalse(revalidate_or_revoke(deny,
                                                       lambda: events.append("scrub")))
                self.assertEqual(events, ["verify", "scrub"])

    def test_failed_entitlement_scrubs_existing_view(self):
        view = {"report": "secret.csv", "queue": ["private case"], "rationale": "personal"}
        def scrub():
            view.clear()
        self.assertFalse(revalidate_or_revoke(lambda: (_ for _ in ()).throw(
            ValueError("Private customer path")), scrub))
        self.assertEqual(view, {})

    def test_success_preserves_review_state(self):
        view = {"report": "synthetic.csv", "queue": ["a"]}
        self.assertTrue(revalidate_or_revoke(lambda: object(), view.clear))
        self.assertEqual(view, {"report": "synthetic.csv", "queue": ["a"]})

    def test_scrub_error_never_returns_authorized(self):
        def scrub():
            raise RuntimeError("UI scrub failed")
        with self.assertRaisesRegex(RuntimeError, "UI scrub failed"):
            revalidate_or_revoke(lambda: False, scrub)

    def test_unexpected_verifier_error_denies_and_scrubs(self):
        events = []
        def unexpected():
            raise TypeError("Programmer error")
        self.assertFalse(revalidate_or_revoke(
            unexpected, lambda: events.append("scrub")))
        self.assertEqual(events, ["scrub"])

    def test_noncallable_callbacks_fail_before_loading_customer_data(self):
        for authorize, scrub in ((None, lambda: None), (lambda: None, None),
                                 ("bad", lambda: None)):
            with self.subTest(authorize=authorize, scrub=scrub):
                with self.assertRaisesRegex(ValueError, "Invalid premium authorization callbacks"):
                    revalidate_or_revoke(authorize, scrub)

    def test_deny_does_not_emit_private_diagnostics(self):
        import contextlib, io
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertFalse(revalidate_or_revoke(
                lambda: (_ for _ in ()).throw(OSError("SECRET_CUSTOMER.csv")),
                lambda: None))
        self.assertEqual(out.getvalue() + err.getvalue(), "")


class ReviewWindowWiringR247Tests(unittest.TestCase):
    """Inspect the real GUI source without booting a Windows/Tk display."""
    @classmethod
    def setUpClass(cls):
        path = DESKTOP / "fvs_suite" / "review_ui.py"
        cls.source = path.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.functions = {n.name: n for n in ast.walk(cls.tree)
                         if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}

    def _calls(self, function_name, called_name):
        function = self.functions[function_name]
        return [n.lineno for n in ast.walk(function) if isinstance(n, ast.Call) and
                ((isinstance(n.func, ast.Name) and n.func.id == called_name) or
                 (isinstance(n.func, ast.Attribute) and n.func.attr == called_name))]

    def test_authorization_uses_revocation_guard(self):
        self.assertTrue(self._calls("_authorized", "revalidate_or_revoke"))
        self.assertTrue(self._calls("_revoke_review_view", "_reset_report_view"))

    def test_revoke_clears_sensitive_editor_controls(self):
        src = ast.get_source_segment(self.source, self.functions["_revoke_review_view"])
        self.assertIn('reviewer.set("")', src)
        self.assertIn('rationale.delete("1.0", "end")', src)

    def test_dangerous_actions_reverify_after_modals_and_before_write(self):
        for name, action in (("log_review", "append_review"),
                             ("export", "export_register"),
                             ("seal_archive", "seal_evidence"),
                             ("restore_archive", "restore_evidence")):
            with self.subTest(function=name):
                check = self._calls(name, "_authorized")
                side_effect = self._calls(name, action)
                self.assertTrue(side_effect)
                self.assertTrue(any(c < side_effect[0] for c in check))
                self.assertTrue(any(c > self.functions[name].lineno + 4 for c in check))

    def test_restore_revalidation_occurs_after_password_dialog(self):
        dialog = self._calls("restore_archive", "askstring")
        writes = self._calls("restore_archive", "restore_evidence")
        checks = self._calls("restore_archive", "_authorized")
        self.assertTrue(any(dialog[0] < c < writes[0] for c in checks))

    def test_seal_revalidation_occurs_after_password_dialog(self):
        dialogs = self._calls("seal_archive", "askstring")
        writes = self._calls("seal_archive", "seal_evidence")
        checks = self._calls("seal_archive", "_authorized")
        self.assertTrue(any(dialog[-1] < c < writes[0] for c in checks))

    def test_export_revalidation_occurs_after_folder_dialog(self):
        dialogs = self._calls("export", "askdirectory")
        writes = self._calls("export", "export_register")
        checks = self._calls("export", "_authorized")
        self.assertTrue(any(dialog[-1] < c < writes[0] for c in checks))


if __name__ == "__main__":
    unittest.main()
