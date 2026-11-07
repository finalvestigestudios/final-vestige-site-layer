"""R252 headless premium launch/Generate entitlement custody regressions.

The GUI test methods extract the actual top-level functions from app.py AST,
so they exercise their authentic control flow without creating Tk windows or
reading any customer data. No signing keys are generated or shipped.
"""
from __future__ import annotations

import ast
import copy
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch

DESKTOP = Path(__file__).resolve().parents[1]
if str(DESKTOP) not in sys.path:
    sys.path.insert(0, str(DESKTOP))
import fvs_suite
from fvs_suite.premium_launch_proof import has_verified_premium_proof


class _Entitlement:
    def __init__(self, product):
        self.product = product


class PremiumProofR252(unittest.TestCase):
    def test_grant_proof_accepted(self):
        self.assertTrue(has_verified_premium_proof(_Entitlement('grants'), 'grants', _Entitlement))

    def test_procurement_proof_accepted(self):
        self.assertTrue(has_verified_premium_proof(_Entitlement('procurement'), 'procurement', _Entitlement))

    def test_no_proof_rejected(self):
        for value in (None, False, True, '', 1, object(), {'product': 'grants'}):
            with self.subTest(value=type(value).__name__):
                self.assertFalse(has_verified_premium_proof(value, 'grants', _Entitlement))

    def test_other_product_denied(self):
        self.assertFalse(has_verified_premium_proof(_Entitlement('grants'), 'procurement', _Entitlement))

    def test_unknown_product_denied(self):
        self.assertFalse(has_verified_premium_proof(_Entitlement('ledger'), 'ledger', _Entitlement))

    def test_entitlement_subclass_denied(self):
        class Forged(_Entitlement):
            pass
        self.assertFalse(has_verified_premium_proof(Forged('grants'), 'grants', _Entitlement))

    def test_untrusted_expected_type_denied(self):
        for value in (None, 'type', 1, _Entitlement('grants')):
            self.assertFalse(has_verified_premium_proof(_Entitlement('grants'), 'grants', value))

    def test_non_native_product_denied(self):
        class Forged(str):
            pass
        self.assertFalse(has_verified_premium_proof(_Entitlement('grants'), Forged('grants'), _Entitlement))


class PremiumGuiProofR252(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = (DESKTOP / 'fvs_suite' / 'app.py').read_text(encoding='utf-8')
        tree = ast.parse(source)
        definitions = [copy.deepcopy(node) for node in tree.body
                       if isinstance(node, ast.FunctionDef) and node.name in (
                           '_select_premium_entitlement', '_require_current_premium_entitlement')]
        if len(definitions) != 2:
            raise AssertionError('Expected both source-owned premium GUI authorization functions')
        cls.code = compile(ast.fix_missing_locations(ast.Module(body=definitions, type_ignores=[])),
                           '<app-source-premium-authorization-r252>', 'exec')

    def _run(self, proof, *, picker='/private/selected.fvslicense', installed_error=None,
             picked_error=None, keys=True, operation='require'):
        dialogs = []
        calls = []
        license_module = types.ModuleType('fvs_suite.offline_entitlement')
        license_module.Entitlement = _Entitlement
        license_module.EntitlementError = ValueError
        license_module.TRUSTED_PUBLIC_KEYS = {'approved-public-only': b'public'} if keys else {}
        license_module.installed_license_path = lambda product: Path('/private/installed.fvslicense')

        def verify(source, product):
            calls.append(str(source))
            if str(source).endswith('installed.fvslicense') and installed_error:
                raise installed_error
            if str(source).endswith('selected.fvslicense') and picked_error:
                raise picked_error
            return proof(source, product) if callable(proof) else proof

        license_module.verify_license = verify
        dialog_module = types.SimpleNamespace(
            askopenfilename=lambda **kwargs: picker)
        messages = types.SimpleNamespace(showerror=lambda *a, **kw: dialogs.append((a, kw)))
        scope = {'__package__': 'fvs_suite', 'Path': Path,
                 'has_verified_premium_proof': has_verified_premium_proof,
                 'filedialog': dialog_module, 'messagebox': messages}
        exec(self.code, scope)
        with patch.object(fvs_suite, 'offline_entitlement', license_module, create=True):
            if operation == 'require':
                result = scope['_require_current_premium_entitlement'](object(), 'grants', '/private/installed.fvslicense')
            else:
                result = scope['_select_premium_entitlement'](object(), 'grants')
        return result, calls, dialogs

    def test_generate_accepts_exact_verified_proof(self):
        result, calls, dialogs = self._run(_Entitlement('grants'))
        self.assertTrue(result)
        self.assertEqual(len(calls), 1)
        self.assertEqual(dialogs, [])

    def test_generate_rejects_none(self):
        result, _, dialogs = self._run(None)
        self.assertFalse(result)
        self.assertEqual(len(dialogs), 1)

    def test_generate_rejects_truthy_sentinel(self):
        result, _, dialogs = self._run(True)
        self.assertFalse(result)
        self.assertEqual(len(dialogs), 1)

    def test_generate_rejects_wrong_product(self):
        result, _, dialogs = self._run(_Entitlement('procurement'))
        self.assertFalse(result)
        self.assertEqual(len(dialogs), 1)

    def test_generate_catches_unexpected_private_error(self):
        result, _, dialogs = self._run(None, installed_error=RuntimeError('/private/CLIENT_NAME'))
        self.assertFalse(result)
        self.assertNotIn('CLIENT_NAME', repr(dialogs))

    def test_installed_valid_license_does_not_open_file_picker(self):
        result, calls, dialogs = self._run(_Entitlement('grants'), operation='select')
        self.assertEqual(result, Path('/private/installed.fvslicense'))
        self.assertEqual(len(calls), 1)
        self.assertEqual(dialogs, [])

    def test_invalid_installed_proof_allows_only_valid_selected_proof(self):
        def chosen_only(source, product):
            return _Entitlement('grants') if str(source).endswith('selected.fvslicense') else None
        result, calls, dialogs = self._run(chosen_only, operation='select')
        self.assertEqual(result, Path('/private/selected.fvslicense'))
        self.assertEqual(len(calls), 2)
        self.assertEqual(dialogs, [])

    def test_invalid_picked_proof_never_opens_premium(self):
        result, calls, dialogs = self._run(True, operation='select')
        self.assertIsNone(result)
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(dialogs), 1)

    def test_unexpected_picker_verifier_error_is_private(self):
        result, calls, dialogs = self._run(None, operation='select',
                                          picked_error=RuntimeError('/private/CLIENT_NAME'))
        self.assertIsNone(result)
        self.assertEqual(len(calls), 2)
        self.assertNotIn('CLIENT_NAME', repr(dialogs))

    def test_empty_authority_never_checks_license(self):
        result, calls, dialogs = self._run(_Entitlement('grants'), keys=False, operation='select')
        self.assertIsNone(result)
        self.assertEqual(calls, [])
        self.assertEqual(len(dialogs), 1)

    def test_missing_file_dialog_keeps_premium_locked(self):
        result, calls, dialogs = self._run(None, picker='', operation='select')
        self.assertIsNone(result)
        self.assertEqual(len(calls), 1)
        self.assertEqual(dialogs, [])

    def test_expired_installed_and_picked_entitlement_fail_closed(self):
        result, calls, dialogs = self._run(None, operation='select',
                                          installed_error=ValueError('expired'),
                                          picked_error=ValueError('expired'))
        self.assertIsNone(result)
        self.assertEqual(len(calls), 2)
        self.assertEqual(len(dialogs), 1)


if __name__ == '__main__':
    unittest.main()
