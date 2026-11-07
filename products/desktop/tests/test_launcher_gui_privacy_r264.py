"""R264: real GUI entry failures must not print private financial data.

A fresh Python process is used for every case because the R260/R261 CPython
network/process audit hook is permanent. Synthetic paths only; these are source
regressions, NOT native Windows binary or screen-reader acceptance tests.
"""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import textwrap
import unittest

ROOT = Path(__file__).resolve().parents[1]
APPS = ("ledger", "invoices", "spend", "policy", "grants", "procurement")
SECRET = "C:/Customers/Private Budget/SECRET_CLIENT_PAYROLL_2026.csv"
MESSAGE = "Final Vestige Labs application failed; no private diagnostics printed"


def isolate(source: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(source)],
        env=env, capture_output=True, text=True, check=False, timeout=15,
    )


def gui_script(action: str, app: str = "ledger") -> str:
    return f'''
import sys, types
from fvs_suite.launcher import launch
fake = types.ModuleType('fvs_suite.app')
def run(app_id):
    if app_id != {app!r}: raise AssertionError('wrong dispatch')
    {action}
fake.run = run
sys.modules['fvs_suite.app'] = fake
sys.argv = ['FinalVestige.exe']
launch({app!r})
'''


class GuiDiagnosticPrivacyR264(unittest.TestCase):
    def assert_redacted(self, script: str) -> None:
        out = isolate(script)
        self.assertNotEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertEqual(out.stderr.strip(), MESSAGE)
        self.assertEqual(out.stdout, "")
        self.assertNotIn(SECRET, out.stdout + out.stderr)
        self.assertNotIn("Traceback", out.stderr)

    def test_all_six_launchers_redact_gui_failures(self):
        for app in APPS:
            with self.subTest(app=app):
                self.assert_redacted(gui_script(f"raise RuntimeError({SECRET!r})", app))

    def test_oserror_with_customer_path_redacted(self):
        self.assert_redacted(gui_script(f"raise OSError(5, 'could not read', {SECRET!r})"))

    def test_private_unicode_exception_redacted(self):
        self.assert_redacted(gui_script(f"raise UnicodeError({SECRET!r})"))

    def test_private_exception_chaining_redacted(self):
        self.assert_redacted(gui_script(f"raise RuntimeError('GUI initialization failed') from ValueError({SECRET!r})"))

    def test_private_exception_context_redacted(self):
        self.assert_redacted(gui_script(f"\n    try: raise ValueError({SECRET!r})\n    except ValueError: raise RuntimeError('gui launch failed')"))

    def test_import_time_failure_redacted(self):
        source = f'''
import builtins, sys
from fvs_suite.launcher import launch
original_import = builtins.__import__
def injected_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name == 'app' and level == 1:
        raise ImportError({SECRET!r})
    return original_import(name, globals, locals, fromlist, level)
builtins.__import__ = injected_import
sys.argv = ['FinalVestige.exe']
launch('ledger')
'''
        self.assert_redacted(source)

    def test_exception_exit_has_no_private_context_or_cause(self):
        output = isolate(gui_script(f"raise OSError(5, 'could not open', {SECRET!r})").replace(
            "launch('ledger')", f'''try: launch('ledger')
except SystemExit as exc:
    assert str(exc) == {MESSAGE!r}, repr(str(exc))
    assert exc.__context__ is None and exc.__cause__ is None
else: raise AssertionError('GUI exception silently allowed')'''
        ))
        self.assertEqual(output.returncode, 0, output.stderr)
        self.assertNotIn(SECRET, output.stdout + output.stderr)

    def test_normal_gui_launch_all_six_preserves_dispatch(self):
        for app in APPS:
            with self.subTest(app=app):
                result = isolate(gui_script("print('GUI_OK')", app))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), "GUI_OK")

    def test_return_none_is_not_a_gui_failure(self):
        result = isolate(gui_script("return None"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")

    def test_keyboard_interrupt_preserved(self):
        result = isolate(gui_script("raise KeyboardInterrupt()"))
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(MESSAGE, result.stdout + result.stderr)

    def test_system_exit_code_preserved(self):
        result = isolate(gui_script("raise SystemExit(47)"))
        self.assertEqual(result.returncode, 47)
        self.assertNotIn(MESSAGE, result.stdout + result.stderr)

    def test_real_network_and_child_process_guard_active_in_gui(self):
        result = isolate(gui_script('''import sys
    for event in ('socket.__new__', 'subprocess.Popen'):
        try: sys.audit(event, 'SYNTHETIC_PRIVATE_SOURCE')
        except PermissionError: pass
        else: raise AssertionError('offline guard missing')'''))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_security_guard_failure_still_takes_priority(self):
        result = isolate(f'''
import sys, types
from fvs_suite import launcher
launcher.install_offline_guard = lambda: (_ for _ in ()).throw(RuntimeError({SECRET!r}))
sys.modules['fvs_suite.app'] = types.SimpleNamespace(run=lambda _: print('GUI_UNSAFE'))
sys.argv = ['app.exe']
launcher.launch('ledger')
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr.strip(), "Final Vestige Labs security startup failed; no private diagnostics printed")
        self.assertEqual(result.stdout, "")

    def test_smoke_failure_behavior_unchanged(self):
        result = isolate('''
import sys, types
from fvs_suite.launcher import launch
sys.modules['fvs_suite.smoke'] = types.SimpleNamespace(run_smoke=lambda _: False)
sys.argv = ['app.exe', '--smoke-test']
launch('ledger')
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr.strip(), 'Final Vestige Labs smoke test failed; no private diagnostics printed')

    def test_version_mode_does_not_load_gui(self):
        result = isolate('''
import sys, types
from fvs_suite.launcher import launch
sys.modules['fvs_suite.app'] = types.SimpleNamespace(run=lambda _: print('GUI_UNSAFE'))
sys.argv = ['app.exe', '--version']
launch('ledger')
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), '0.1.0-dev')

    def test_invalid_cli_arguments_do_not_load_gui(self):
        result = isolate('''
import sys, types
from fvs_suite.launcher import launch
sys.modules['fvs_suite.app'] = types.SimpleNamespace(run=lambda _: print('GUI_UNSAFE'))
sys.argv = ['app.exe', '--publish']
launch('ledger')
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn('Unsupported arguments', result.stderr)


if __name__ == '__main__':
    unittest.main()
