"""R392: never expose synthetic unittest generator closures to pytest as globals."""
from __future__ import annotations
import ast
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
TARGETS = ('test_r388_source_url_alias_custody.py', 'test_r391_frozen_export_attestation.py')


def leaked_globals(source: str):
    """Report module-scoped test* functions whose first parameter is self."""
    tree = ast.parse(source)
    found = []
    def visit(node, nested=False):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not nested and node.name.startswith('test') and node.args.args and node.args.args[0].arg == 'self':
                found.append((node.name, node.lineno))
            return
        if isinstance(node, (ast.ClassDef, ast.Lambda)):
            return
        for child in ast.iter_child_nodes(node):
            visit(child, nested)
    visit(tree)
    return found


class R392CollectionTests(unittest.TestCase):
    def test_current_generator_modules_have_no_leaked_globals(self):
        for name in TARGETS:
            with self.subTest(file=name):
                self.assertEqual(leaked_globals((ROOT / name).read_text(encoding='utf-8')), [])

    def test_nested_for_body_leak_is_detected(self):
        self.assertEqual(leaked_globals('for i in range(3):\n    def test(self, i=i): pass\n'), [('test', 2)])

    def test_class_methods_are_not_false_positives(self):
        self.assertEqual(leaked_globals('class TestCase:\n    def test_example(self): pass\n'), [])

    def test_valid_global_pytest_function_not_flagged(self):
        self.assertEqual(leaked_globals('def test_status():\n    assert True\n'), [])

    def test_renamed_generator_function_is_safe(self):
        self.assertEqual(leaked_globals('for i in range(3):\n    def _case(self, i=i): pass\n'), [])

    def test_nested_helper_does_not_escape_scope(self):
        self.assertEqual(leaked_globals('def factory():\n    def test(self): pass\n    return test\n'), [])

    def test_multiple_generator_leaks_detected(self):
        self.assertEqual(len(leaked_globals('for i in range(2):\n    def test(self): pass\nfor j in range(2):\n    def test_case(self): pass\n')), 2)

    def test_async_leak_detected(self):
        self.assertEqual(leaked_globals('async def test_bad(self): pass\n'), [('test_bad', 1)])


if __name__ == '__main__':
    unittest.main()
