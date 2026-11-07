"""R266: exercise real CPython background failure hooks on synthetic data.

Every source integration test is process-isolated; the offline audit hook is
permanent. No network, personal records, premium license or GUI is required.
These are source tests, NOT packaged Windows binary acceptance evidence.
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
SECRET = "C:/private/CUSTOMER_PAYROLL_2026.csv"
THREAD = "Final Vestige Labs background task failed; private diagnostics suppressed\n"
CLEANUP = "Final Vestige Labs cleanup failed; private diagnostics suppressed\n"
BOOT = "Final Vestige Labs security startup failed; no private diagnostics printed"


def isolate(source: str):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run([sys.executable, "-c", textwrap.dedent(source)],
                          env=env, capture_output=True, text=True,
                          check=False, timeout=15)


def script_for(app: str, failure: str) -> str:
    return f''' 
import sys, types, threading, gc
from fvs_suite.launcher import launch
SECRET = {SECRET!r}
def run(app):
    {failure}
fake = types.ModuleType('fvs_suite.app')
fake.run = run
sys.modules['fvs_suite.app'] = fake
sys.argv = ['app.exe']
launch({app!r})
'''


class BackgroundPrivacyR266(unittest.TestCase):
    def test_unprotected_thread_hook_exposes_financial_filename(self):
        out = isolate(f'''
import threading
thread = threading.Thread(target=lambda: (_ for _ in ()).throw(ValueError({SECRET!r})))
thread.start(); thread.join()
''')
        self.assertIn(SECRET, out.stderr)
        self.assertIn("Exception in thread", out.stderr)

    def test_unprotected_unraisable_hook_exposes_financial_filename(self):
        out = isolate(f'''
import sys
sys.unraisablehook(type('Args', (), dict(exc_type=OSError, exc_value=OSError({SECRET!r}),
    exc_traceback=None, err_msg=None, object=None))())
''')
        self.assertIn(SECRET, out.stderr)

    def test_all_six_gui_launchers_redact_actual_thread_exceptions(self):
        action = 't = threading.Thread(target=lambda: (_ for _ in ()).throw(ValueError(SECRET))); t.start(); t.join()'
        for app in APPS:
            with self.subTest(app=app):
                out = isolate(script_for(app, action))
                self.assertEqual(out.returncode, 0, out.stderr)
                self.assertEqual(out.stderr, THREAD)
                self.assertEqual(out.stdout, "")

    def test_all_six_gui_launchers_redact_actual_unraisable_exceptions(self):
        action = '''class Broken:\n        def __del__(self): raise OSError(SECRET)\n    x = Broken(); del x; gc.collect()'''
        for app in APPS:
            with self.subTest(app=app):
                out = isolate(script_for(app, action))
                self.assertEqual(out.returncode, 0, out.stderr)
                self.assertEqual(out.stderr, CLEANUP)
                self.assertEqual(out.stdout, "")

    def test_both_hooks_are_active_before_gui_entry(self):
        out = isolate(script_for('ledger', '''from fvs_suite.background_privacy import _thread_exception, _unraisable_exception\n    assert threading.excepthook is _thread_exception\n    assert sys.unraisablehook is _unraisable_exception'''))
        self.assertEqual(out.returncode, 0, out.stderr)

    def test_install_is_idempotent(self):
        out = isolate('''
import threading, sys
from fvs_suite.background_privacy import install_background_privacy, _thread_exception, _unraisable_exception
install_background_privacy(); install_background_privacy()
assert threading.excepthook is _thread_exception
assert sys.unraisablehook is _unraisable_exception
''')
        self.assertEqual(out.returncode, 0, out.stderr)

    def test_systemexit_thread_remains_silent(self):
        out = isolate(script_for('ledger', 't = threading.Thread(target=lambda: (_ for _ in ()).throw(SystemExit(6))); t.start(); t.join()'))
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stderr, "")

    def test_keyboardinterrupt_thread_is_redacted(self):
        out = isolate(script_for('ledger', 't = threading.Thread(target=lambda: (_ for _ in ()).throw(KeyboardInterrupt(SECRET))); t.start(); t.join()'))
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stderr, THREAD)

    def test_exception_type_never_formatted(self):
        out = isolate('''
from fvs_suite.background_privacy import install_background_privacy
import threading
class Sensitive(Exception):
    def __str__(self): raise AssertionError('never stringify private exceptions')
install_background_privacy()
t = threading.Thread(target=lambda: (_ for _ in ()).throw(Sensitive()))
t.start(); t.join()
''')
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stderr, THREAD)

    def test_unraisable_args_not_inspected(self):
        out = isolate('''
import sys
from fvs_suite.background_privacy import install_background_privacy
class Hostile:
    def __getattribute__(self, name): raise AssertionError('no payload access')
    def __str__(self): raise AssertionError('no payload formatting')
install_background_privacy()
sys.unraisablehook(Hostile())
''')
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stderr, CLEANUP)

    def test_write_failure_does_not_restore_default_hook(self):
        out = isolate('''
import sys
from fvs_suite.background_privacy import install_background_privacy
class Writer:
    def write(self, content): raise OSError('private source path')
install_background_privacy(); sys.stderr = Writer()
sys.unraisablehook(None)
sys.stderr = sys.__stderr__
''')
        self.assertEqual(out.returncode, 0)
        self.assertEqual(out.stdout, '')

    def test_thread_hostile_args_cannot_leak(self):
        out = isolate('''
import threading
from fvs_suite.background_privacy import install_background_privacy
class Hostile:
    def __getattribute__(self, name): raise OSError('CUSTOMER_PRIVATE_PATH')
install_background_privacy()
threading.excepthook(Hostile())
''')
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(out.stderr, THREAD)
        self.assertNotIn('CUSTOMER_PRIVATE_PATH', out.stderr)

    def test_version_and_smoke_startup_still_work(self):
        for flags in ('["--version"]', '["--smoke-test"]'):
            with self.subTest(flags=flags):
                out = isolate(f'''
import sys, types
from fvs_suite.launcher import launch
sys.modules['fvs_suite.smoke'] = types.SimpleNamespace(run_smoke=lambda _: True)
sys.argv=['app.exe']+{flags}
launch('ledger')
''')
                self.assertEqual(out.returncode, 0, out.stderr)

    def test_hook_bootstrap_failure_does_not_load_gui(self):
        out = isolate(f'''
import sys, types
from fvs_suite import launcher
launcher.install_background_privacy = lambda: (_ for _ in ()).throw(ValueError({SECRET!r}))
sys.modules['fvs_suite.app'] = types.SimpleNamespace(run=lambda _: print('UNSAFE'))
sys.argv=['app.exe']
launcher.launch('grants')
''')
        self.assertNotEqual(out.returncode, 0)
        self.assertEqual(out.stderr.strip(), BOOT)
        self.assertEqual(out.stdout, '')

    def test_installation_error_has_no_exception_chain(self):
        out = isolate(f'''
from fvs_suite import background_privacy as bg
class Deny:
    def __setattr__(self, attr, value): raise OSError({SECRET!r})
bg.sys = Deny()
try: bg.install_background_privacy()
except RuntimeError as exc:
    assert str(exc) == bg.INSTALL_DIAGNOSTIC
    assert exc.__cause__ is None and exc.__context__ is None
else: raise AssertionError('Failed to deny broken hook setup')
''')
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertNotIn(SECRET, out.stderr)

    def test_silent_hook_assignment_rejected(self):
        out = isolate('''
from fvs_suite import background_privacy as bg
class NoOp:
    unraisablehook = object()
    def __setattr__(self, name, value): pass
bg.sys = NoOp()
try: bg.install_background_privacy()
except RuntimeError as exc:
    assert str(exc) == bg.INSTALL_DIAGNOSTIC
else: raise AssertionError('Silent drop accepted')
''')
        self.assertEqual(out.returncode, 0, out.stderr)


if __name__ == '__main__':
    unittest.main()
