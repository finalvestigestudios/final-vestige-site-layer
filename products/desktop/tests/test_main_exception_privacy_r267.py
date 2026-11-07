"""R267: real uncaught main-thread exception privacy for all six launch paths.

Process-isolated CPython stderr assertions use synthetic private filenames;
source regressions do not certify Windows binaries or an OS sandbox.
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
MAIN = "Final Vestige Labs uncaught error; private diagnostics suppressed\n"
THREAD = "Final Vestige Labs background task failed; private diagnostics suppressed\n"
CLEANUP = "Final Vestige Labs cleanup failed; private diagnostics suppressed\n"
BOOT = "Final Vestige Labs security startup failed; no private diagnostics printed"


def isolate(source: str):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run([sys.executable, "-c", textwrap.dedent(source)],
                          env=env, capture_output=True, text=True,
                          check=False, timeout=15)


class MainExceptionPrivacyR267(unittest.TestCase):
    def test_unprotected_default_exposes_private_path(self):
        result = isolate(f"raise OSError({SECRET!r})")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(SECRET, result.stderr)

    def test_all_six_launch_paths_scrub_later_main_thread_exception(self):
        for app in APPS:
            with self.subTest(app=app):
                result = isolate(f'''
import sys, types
from fvs_suite.launcher import launch
sys.modules['fvs_suite.app'] = types.SimpleNamespace(run=lambda _app: None)
sys.argv = ['test-app.exe']
launch({app!r})
raise RuntimeError({SECRET!r})
''')
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stderr, MAIN)
                self.assertEqual(result.stdout, "")

    def test_direct_installer_redacts_chained_exception_and_traceback(self):
        result = isolate(f'''
from fvs_suite.background_privacy import install_background_privacy
install_background_privacy()
try:
    raise FileNotFoundError({SECRET!r})
except FileNotFoundError:
    raise OSError('wrapped private account')
''')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, MAIN)

    def test_keyboardinterrupt_never_includes_private_exception_text(self):
        result = isolate(f'''
from fvs_suite.background_privacy import install_background_privacy
install_background_privacy()
raise KeyboardInterrupt({SECRET!r})
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr, MAIN)

    def test_systemexit_preserves_exit_contract(self):
        result = isolate('''
from fvs_suite.background_privacy import install_background_privacy
install_background_privacy()
raise SystemExit(23)
''')
        self.assertEqual(result.returncode, 23)
        self.assertEqual(result.stderr, "")

    def test_payloads_never_inspected_or_formatted(self):
        result = isolate('''
import sys
from fvs_suite.background_privacy import install_background_privacy
class Hostile:
    def __str__(self): raise RuntimeError('private details')
    def __repr__(self): raise RuntimeError('private repr')
    def __getattribute__(self, key): raise RuntimeError('private attr')
install_background_privacy()
sys.excepthook(Hostile(), Hostile(), Hostile())
''')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, MAIN)

    def test_stderr_write_failure_does_not_restore_default(self):
        result = isolate('''
import sys
from fvs_suite.background_privacy import install_background_privacy
class Writer:
    def write(self, message): raise OSError('private path')
install_background_privacy()
sys.stderr = Writer()
sys.excepthook(OSError, OSError('private path'), None)
sys.stderr = sys.__stderr__
''')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")

    def test_idempotent_and_all_three_hooks_installed(self):
        result = isolate('''
import sys, threading
from fvs_suite.background_privacy import (install_background_privacy,
    _main_exception, _thread_exception, _unraisable_exception)
install_background_privacy(); install_background_privacy()
assert sys.excepthook is _main_exception
assert threading.excepthook is _thread_exception
assert sys.unraisablehook is _unraisable_exception
''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_thread_and_cleanup_regressions_not_weakened(self):
        result = isolate('''
import threading, sys
from fvs_suite.background_privacy import install_background_privacy
install_background_privacy()
t = threading.Thread(target=lambda: (_ for _ in ()).throw(ValueError('CUSTOMER_ACCOUNT')))
t.start(); t.join()
sys.unraisablehook(object())
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, THREAD + CLEANUP)

    def test_failed_main_hook_assignment_denies_setup_unchained(self):
        result = isolate(f'''
from fvs_suite import background_privacy as b
class Reject:
    excepthook = object()
    unraisablehook = object()
    def __setattr__(self, name, value):
        if name == 'excepthook': raise OSError({SECRET!r})
        object.__setattr__(self, name, value)
b.sys = Reject()
try:
    b.install_background_privacy()
except RuntimeError as e:
    assert str(e) == b.INSTALL_DIAGNOSTIC
    assert e.__cause__ is None and e.__context__ is None
else: raise AssertionError('installer unexpectedly allowed startup')
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(SECRET, result.stderr)

    def test_silent_drop_of_main_hook_denies_setup(self):
        result = isolate('''
from fvs_suite import background_privacy as b
class Drop:
    excepthook = object()
    unraisablehook = object()
    def __setattr__(self, name, value):
        if name != 'excepthook': object.__setattr__(self, name, value)
b.sys = Drop()
try: b.install_background_privacy()
except RuntimeError as e: assert str(e) == b.INSTALL_DIAGNOSTIC
else: raise AssertionError('discarded privacy hook accepted')
''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_launcher_denies_on_new_hook_bootstrap_error(self):
        result = isolate(f'''
import sys, types
from fvs_suite import launcher
launcher.install_background_privacy = lambda: (_ for _ in ()).throw(OSError({SECRET!r}))
sys.modules['fvs_suite.app'] = types.SimpleNamespace(run=lambda _: print('UNSAFE GUI'))
sys.argv = ['test-app.exe']
launcher.launch('procurement')
''')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stderr.strip(), BOOT)
        self.assertEqual(result.stdout, "")

    def test_version_flag_preserved(self):
        result = isolate('''
import sys
from fvs_suite.launcher import launch
sys.argv = ['test-app.exe', '--version']
launch('ledger')
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.strip())
        self.assertEqual(result.stderr, "")

    def test_no_network_or_files_touched_during_direct_install(self):
        result = isolate('''
from fvs_suite.background_privacy import install_background_privacy
install_background_privacy()
''')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
