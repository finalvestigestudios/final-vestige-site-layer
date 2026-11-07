"""R251: locally executed output-contract checks and source-owned GUI wiring.

All filesystem fixtures are synthetic and private to TemporaryDirectory.
The GUI callback is compiled from the actual repository source without Tk.
"""
from __future__ import annotations

import ast
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))
from fvs_suite.report_completion import confirm_report_files
from fvs_suite.ui_errors import safe_error_message


class ReportCompletionContractR251(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.file = self.root / 'report.csv'
        self.file.write_text('id,amount\nA,1.00\n', encoding='utf-8')

    def test_existing_regular_file_is_verified(self):
        self.assertEqual(confirm_report_files([self.file]), (self.file,))

    def test_tuple_inventory_is_verified(self):
        second = self.root / 'second.csv'
        second.write_text('id\nA\n', encoding='utf-8')
        self.assertEqual(confirm_report_files((self.file, second)), (self.file, second))

    def test_repeated_calls_are_deterministic(self):
        self.assertEqual(confirm_report_files([self.file]), confirm_report_files([self.file]))

    def test_empty_none_and_scalar_rejected(self):
        for inventory in (None, [], (), self.file, str(self.file), 1, False, {}, {self.file}):
            with self.subTest(inventory=type(inventory).__name__), self.assertRaises(ValueError):
                confirm_report_files(inventory)

    def test_reject_oversize_and_bool_subclass_count_tricks(self):
        with self.assertRaises(ValueError):
            confirm_report_files([self.file] * 17)

    def test_missing_report_does_not_create_file(self):
        missing = self.root / 'missing.csv'
        with self.assertRaises(FileNotFoundError):
            confirm_report_files([missing])
        self.assertFalse(missing.exists())

    def test_directory_rejected(self):
        with self.assertRaises(ValueError):
            confirm_report_files([self.root])

    def test_empty_regular_file_rejected(self):
        blank = self.root / 'blank.csv'
        blank.touch()
        with self.assertRaises(ValueError):
            confirm_report_files([blank])

    def test_symlink_rejected_without_touching_target(self):
        link = self.root / 'link.csv'
        try:
            link.symlink_to(self.file)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f'Symlink creation unavailable: {type(error).__name__}')
        with self.assertRaises(ValueError):
            confirm_report_files([link])
        self.assertEqual(self.file.read_text(encoding='utf-8'), 'id,amount\nA,1.00\n')

    def test_duplicate_path_rejected(self):
        with self.assertRaises(ValueError):
            confirm_report_files([self.file, self.file])

    def test_malformed_mixed_inventory_rejected(self):
        with self.assertRaises(ValueError):
            confirm_report_files([self.file, 'foreign.csv'])

    def test_subclass_path_not_trusted(self):
        class CustomPath(type(self.file)):
            @property
            def name(self):
                raise RuntimeError('PRIVATE_CUSTOMER')
        disguised = CustomPath(self.file)
        with self.assertRaises(ValueError):
            confirm_report_files([disguised])

    def test_stat_error_propagates_for_fixed_ui_redaction(self):
        missing = self.root / 'PRIVATE_CUSTOMER_LEDGER.csv'
        try:
            confirm_report_files([missing])
        except FileNotFoundError as error:
            message = safe_error_message(error, operation='generate')
            self.assertNotIn('PRIVATE_CUSTOMER', message)
        else:
            self.fail('Expected missing report failure')

    def test_never_modifies_original_on_failure(self):
        before = self.file.read_bytes()
        with self.assertRaises(ValueError):
            confirm_report_files([self.file, self.root])
        self.assertEqual(self.file.read_bytes(), before)


class ReportCompletionGuiR251(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = (DESKTOP / 'fvs_suite' / 'app.py').read_text(encoding='utf-8')
        tree = ast.parse(source)
        run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
        cls.callback = next(n for n in run.body if isinstance(n, ast.FunctionDef) and n.name == 'execute')

    def _execute(self, action, *, premium=False, authorize=True, output_folder=None):
        events = []
        statuses = []
        selected_report = ['old-report.csv']
        messages = SimpleNamespace(
            showwarning=lambda *a, **kw: events.append(('warning', a[1])),
            showerror=lambda *a, **kw: events.append(('error', a[1])),
            showinfo=lambda *a, **kw: events.append(('info', a[1])))
        namespace = {
            'clear_auto_review_target': lambda slot: slot.__setitem__(0, None),
            'last_report': selected_report,
            'premium': premium,
            '_require_current_premium_entitlement': lambda *a: authorize,
            'root': object(), 'app_id': 'grants' if premium else 'spend',
            'entitlement_source': object(),
            'selected': [SimpleNamespace(get=lambda: 'synthetic-input.csv')],
            'output': SimpleNamespace(get=lambda: output_folder if output_folder is not None else 'synthetic-output'),
            'action': action,
            'safe_error_message': safe_error_message,
            'confirm_report_files': confirm_report_files,
            'status': SimpleNamespace(set=statuses.append),
            'messagebox': messages,
        }
        node = copy.deepcopy(self.callback)
        module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
        exec(compile(module, '<committed-app-execute>', 'exec'), namespace)
        namespace['execute']()
        return selected_report, statuses, events

    def test_unexpected_runtime_failure_redacts_and_revokes(self):
        selected, status, events = self._execute(lambda *a: (_ for _ in ()).throw(RuntimeError('PRIVATE_CUSTOMER')))
        self.assertEqual(selected, [None])
        self.assertEqual([e[0] for e in events], ['error'])
        self.assertNotIn('PRIVATE_CUSTOMER', repr((status, events)))
        self.assertIn('Inspect', status[0])

    def test_failed_post_write_verification_keeps_file_for_inspection(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'report.csv'
            file.write_text('id\nA\n', encoding='utf-8')
            selected, _, events = self._execute(lambda *a: [file, Path(temp)])
            self.assertEqual(selected, [None])
            self.assertTrue(file.exists())
            self.assertEqual(events[0][0], 'error')

    def test_none_is_not_a_successful_report(self):
        selected, _, events = self._execute(lambda *a: None)
        self.assertEqual(selected, [None])
        self.assertEqual([e[0] for e in events], ['error'])

    def test_valid_output_generates_success(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / 'spend-map-20261107-005400-123456.csv'
            file.write_text('id\nA\n', encoding='utf-8')
            selected, status, events = self._execute(lambda *a: [file], output_folder=temp)
            self.assertEqual(selected, [None])  # free apps never select premium reviews
            self.assertTrue(status[0].startswith('Created: '))
            self.assertEqual([e[0] for e in events], ['info'])

    def test_premium_denial_is_before_action(self):
        def forbidden(*a):
            raise AssertionError('Engine should not be called')
        selected, _, events = self._execute(forbidden, premium=True, authorize=False)
        self.assertEqual(selected, [None])
        self.assertEqual(events, [])

    def test_generated_reports_attested_before_premium_selection(self):
        with tempfile.TemporaryDirectory() as temp:
            bundle = Path(temp) / ('grant-evidence-20261107T085400Z-' + 'a' * 32)
            bundle.mkdir()
            files = [bundle / f'{stem}-20261107-005400-123456.{suffix}' for stem, suffix in (
                ('grant-audit-exceptions', 'csv'), ('grant-budget-check', 'csv'),
                ('evidence-manifest', 'txt'))]
            for file in files:
                file.write_text('synthetic evidence\n', encoding='utf-8')
            selected, _, events = self._execute(
                lambda *a: files, premium=True, authorize=True, output_folder=temp)
            self.assertEqual(selected, [str(files[0])])
            self.assertEqual(events[0][0], 'info')


if __name__ == '__main__':
    unittest.main()
