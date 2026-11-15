"""R451: detect stale CSV publication imports before six-app packaging.

Static, read-only contract check over checked-out Python sources. No imports
from untrusted application modules, customer data, filesystem writes or network.
"""
from __future__ import annotations

import ast
import errno
import unittest
from pathlib import Path

from fvs_suite.csv_publish_guard import private_csv_failure


_ROOT = Path(__file__).resolve().parents[1]
_GUARD = _ROOT / "fvs_suite" / "csv_publish_guard.py"


def _guard_exports():
    tree = ast.parse(_GUARD.read_text(encoding="utf-8"))
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for target in targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
    return names


class CSVGuardImportContractR451(unittest.TestCase):
    def test_error_builder_is_exported_not_legacy_raiser(self):
        exports = _guard_exports()
        self.assertIn("private_csv_failure", exports)
        self.assertNotIn("raise_private_csv_failure", exports)
        self.assertIn("require_free_destination", exports)
        self.assertIn("adopt_csv_descriptor", exports)

    def test_no_stale_csv_guard_imports_in_desktop_python_tree(self):
        exports = _guard_exports()
        checked = 0
        for path in sorted(_ROOT.rglob("*.py")):
            # AST parsing does not execute code or emit private data.
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom):
                    continue
                if node.module == "fvs_suite.csv_publish_guard" or (
                        node.level == 1 and node.module == "csv_publish_guard"):
                    checked += 1
                    for imported in node.names:
                        self.assertNotEqual(imported.name, "*", str(path))
                        self.assertIn(imported.name, exports,
                                      "stale CSV guard import in " + path.name)
        self.assertGreaterEqual(checked, 2,
                                "guard no longer exercised by source and tests")

    def test_private_os_error_built_inside_handler_has_no_hidden_chain(self):
        secret = "SYNTHETIC_PRIVATE_CUSTOMER_R451"
        source = PermissionError(errno.EACCES, secret, "/private/" + secret)
        source.__cause__ = ValueError(secret)
        try:
            raise source
        except OSError as caught:
            clean = private_csv_failure(caught)
        self.assertEqual(clean.errno, errno.EACCES)
        self.assertIsNone(clean.__context__)
        self.assertIsNone(clean.__cause__)
        self.assertNotIn(secret, repr(clean))


if __name__ == "__main__":
    unittest.main()
