"""Headless premium GUI access checks, no real display or production keys."""
import ast
import inspect
import unittest
from unittest.mock import MagicMock, patch

from fvs_suite import app, review_ui


class PremiumAccessR11Tests(unittest.TestCase):
    def test_both_premium_windows_fail_closed_before_ui_when_no_authority(self):
        for product in ("grants", "procurement"):
            with self.subTest(product=product):
                with patch.object(app.tk, "Tk") as tk, \
                     patch.object(app.messagebox, "showerror") as error:
                    app.run(product)
                    tk.return_value.withdraw.assert_called_once()
                    tk.return_value.destroy.assert_called_once()
                    tk.return_value.title.assert_not_called()
                    error.assert_called_once()
                    self.assertIn("Premium preview locked", error.call_args.args[0])

    def test_review_window_never_opens_without_entitlement_callback(self):
        with patch.object(review_ui.tk, "Toplevel") as create:
            with self.assertRaisesRegex(ValueError, "verified entitlement"):
                review_ui.open_review_window(None, "grants")
            create.assert_not_called()

    def test_all_review_actions_start_with_license_revalidation(self):
        tree = ast.parse(inspect.getsource(review_ui.open_review_window))
        nested = {node.name: node for node in ast.walk(tree)
                  if isinstance(node, ast.FunctionDef)}
        for name in ("load_report", "choose_report", "log_review",
                     "export", "seal_archive", "restore_archive"):
            with self.subTest(action=name):
                body = nested[name].body
                self.assertIsInstance(body[0], ast.If)
                self.assertIn("_authorized", ast.unparse(body[0].test))

    def test_license_selection_failure_cannot_start_premium(self):
        with patch.object(app.tk, "Tk") as tk, \
             patch.object(app.messagebox, "showerror"), \
             patch("fvs_suite.offline_entitlement.TRUSTED_PUBLIC_KEYS",
                   {"test-issuer": b"1"*32}), \
             patch.object(app.filedialog, "askopenfilename", return_value=""):
            app.run("grants")
            tk.return_value.destroy.assert_called_once()
            tk.return_value.title.assert_not_called()


if __name__ == "__main__":
    unittest.main()
