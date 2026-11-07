"""R248: fail-closed premium entitlement proof and pre-window authorization."""
from __future__ import annotations

import ast
import contextlib
import io
from pathlib import Path
import sys
import unittest
from dataclasses import dataclass

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))
from fvs_suite.review_target import revalidate_or_revoke


@dataclass(frozen=True)
class Proof:
    product: str = "grants"


class AuthProofR248Tests(unittest.TestCase):
    def test_authoritative_proof_is_accepted_once(self):
        calls = []
        self.assertTrue(revalidate_or_revoke(
            lambda: calls.append("verify") or Proof(),
            lambda: calls.append("scrub")))
        self.assertEqual(calls, ["verify"])

    def test_explicit_true_is_accepted(self):
        calls = []
        self.assertTrue(revalidate_or_revoke(lambda: True,
                                             lambda: calls.append("scrub")))
        self.assertEqual(calls, [])

    def test_all_missing_and_falsey_proofs_deny(self):
        for proof in (False, None, 0, 0.0, "", [], {}, (), b""):
            with self.subTest(proof=repr(proof)):
                calls = []
                self.assertFalse(revalidate_or_revoke(
                    lambda: proof, lambda: calls.append("scrub")))
                self.assertEqual(calls, ["scrub"])

    def test_expected_and_unexpected_verifier_errors_deny(self):
        for kind in (ValueError, OSError, UnicodeError, RuntimeError, TypeError,
                     LookupError, PermissionError):
            with self.subTest(error=kind.__name__):
                calls = []
                def throw():
                    calls.append("verify")
                    raise kind("PRIVATE_CLIENT_PATH_AND_LICENSE")
                self.assertFalse(revalidate_or_revoke(throw, lambda: calls.append("scrub")))
                self.assertEqual(calls, ["verify", "scrub"])

    def test_hostile_truthiness_is_denied(self):
        class FaultyProof:
            def __bool__(self):
                raise RuntimeError("CUSTOMER_LICENSE_ID")
        calls = []
        self.assertFalse(revalidate_or_revoke(lambda: FaultyProof(),
                                               lambda: calls.append("scrub")))
        self.assertEqual(calls, ["scrub"])

    def test_malformed_boolean_protocol_is_denied(self):
        class BadTruth:
            def __bool__(self):
                return "yes"
        calls = []
        self.assertFalse(revalidate_or_revoke(lambda: BadTruth(),
                                               lambda: calls.append("scrub")))
        self.assertEqual(calls, ["scrub"])

    def test_expired_entitlement_scrubs_sensitive_view(self):
        view = {"path": "private.csv", "cases": ["client"], "reviewer": "name"}
        self.assertFalse(revalidate_or_revoke(lambda: None, view.clear))
        self.assertEqual(view, {})

    def test_positive_proof_does_not_scrub_existing_view(self):
        view = {"path": "synthetic.csv"}
        self.assertTrue(revalidate_or_revoke(lambda: Proof(), view.clear))
        self.assertEqual(view, {"path": "synthetic.csv"})

    def test_denial_never_emits_verifier_diagnostics(self):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            self.assertFalse(revalidate_or_revoke(
                lambda: (_ for _ in ()).throw(TypeError("TOP_SECRET_CLIENT")),
                lambda: None))
        self.assertEqual(output.getvalue() + errors.getvalue(), "")

    def test_scrub_failure_is_not_silently_accepted(self):
        def broken_scrub():
            raise RuntimeError("UI scrub failed")
        with self.assertRaisesRegex(RuntimeError, "UI scrub failed"):
            revalidate_or_revoke(lambda: None, broken_scrub)

    def test_invalid_callbacks_rejected_before_verification(self):
        for authorize, scrub in ((None, lambda: None), (lambda: True, None),
                                 ("license", lambda: None)):
            with self.subTest(authorize=repr(authorize)):
                with self.assertRaisesRegex(ValueError, "Invalid premium authorization callbacks"):
                    revalidate_or_revoke(authorize, scrub)

    def test_interruption_is_not_accidentally_swallowed(self):
        def interrupted():
            raise KeyboardInterrupt()
        with self.assertRaises(KeyboardInterrupt):
            revalidate_or_revoke(interrupted, lambda: None)


class EarlyWindowAuthorizationR248Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = DESKTOP / "fvs_suite" / "review_ui.py"
        cls.source = cls.path.read_text(encoding="utf-8")
        cls.tree = ast.parse(cls.source)
        cls.opener = next(node for node in ast.walk(cls.tree)
                          if isinstance(node, ast.FunctionDef) and node.name == "open_review_window")

    def test_early_guard_invoked_before_toplevel(self):
        calls = [(n.lineno, n.func.id if isinstance(n.func, ast.Name) else n.func.attr)
                 for n in ast.walk(self.opener) if isinstance(n, ast.Call) and
                 isinstance(n.func, (ast.Name, ast.Attribute))]
        checks = [ln for ln, name in calls if name == "revalidate_or_revoke"]
        tops = [ln for ln, name in calls if name == "Toplevel"]
        self.assertTrue(checks and tops)
        self.assertLess(min(checks), min(tops))

    def test_early_guard_denies_without_constructing_window(self):
        # Extract the pre-Toplevel executable statements directly from the real
        # GUI AST; no Tk display or licensing keys are needed for this check.
        prefix = []
        for stmt in self.opener.body:
            if isinstance(stmt, ast.Assign) and any(
                isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and
                n.func.attr == "Toplevel" for n in ast.walk(stmt)):
                break
            prefix.append(stmt)
        else:
            self.fail("No Tk top-level window found")
        self.assertGreaterEqual(len(prefix), 3)
        extracted = ast.FunctionDef(
            name="preflight", args=ast.arguments(posonlyargs=[], args=[ast.arg(arg="product"),
                ast.arg(arg="authorize")], vararg=None, kwonlyargs=[], kw_defaults=[],
                kwarg=None, defaults=[]), body=prefix + [ast.Return(value=ast.Constant(True))],
            decorator_list=[], returns=None, type_comment=None)
        module = ast.fix_missing_locations(ast.Module(body=[extracted], type_ignores=[]))
        namespace = {"revalidate_or_revoke": revalidate_or_revoke}
        exec(compile(module, "<review_ui_preflight>", "exec"), namespace)
        for proof in (None, False, 0):
            with self.subTest(proof=proof):
                with self.assertRaisesRegex(ValueError, "Premium entitlement denied"):
                    namespace["preflight"]("grants", lambda: proof)
        self.assertTrue(namespace["preflight"]("procurement", lambda: Proof("procurement")))


if __name__ == "__main__":
    unittest.main()
