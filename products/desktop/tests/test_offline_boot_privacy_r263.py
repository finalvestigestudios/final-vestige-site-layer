"""R263: an offline-guard startup fault must not leak client paths via traceback.

Every execution runs in its own Python child: audit hooks are process-global
and irrevocable. Only synthetic customer paths are used. These are CPython
source checks, not evidence of Windows x64 packaged execution.
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
SECRET = "C:/Private Finance/SECRET_CUSTOMER_LEDGER_2026.csv"
ERROR = "Final Vestige Labs security startup failed; no private diagnostics printed"
DIRECT_ERROR = "Offline network guard could not be installed"


def isolate(source: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run([sys.executable, "-c", textwrap.dedent(source)],
                          env=env, capture_output=True, text=True,
                          check=False, timeout=15)


def startup_script(app: str, argv: str = "[]", failure: str = "raise RuntimeError(SECRET)") -> str:
    return f'''
import sys, types
from fvs_suite import offline_network
from fvs_suite.launcher import launch
SECRET = {SECRET!r}
def broken(hook):
    {failure}
offline_network.sys.addaudithook = broken
sys.modules['fvs_suite.app'] = types.SimpleNamespace(run=lambda _: print('UNSAFE GUI LOADED'))
sys.modules['fvs_suite.smoke'] = types.SimpleNamespace(run_smoke=lambda _: print('UNSAFE SMOKE LOADED'))
sys.argv = ['app.exe'] + {argv}
launch({app!r})
'''


class OfflineBootstrapPrivacyR263(unittest.TestCase):
    def assert_private_boot_denied(self, code: str) -> None:
        result = isolate(code)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr.strip(), ERROR)
        self.assertEqual(result.stdout, "")
        self.assertNotIn(SECRET, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_all_six_gui_launchers_redact_registration_exceptions(self):
        for app in APPS:
            with self.subTest(app=app):
                self.assert_private_boot_denied(startup_script(app))

    def test_version_mode_still_requires_guard_first(self):
        self.assert_private_boot_denied(startup_script("ledger", '["--version"]'))

    def test_smoke_mode_still_requires_guard_first(self):
        self.assert_private_boot_denied(startup_script("grants", '["--smoke-test"]'))

    def test_private_oserror_registration_is_redacted(self):
        self.assert_private_boot_denied(startup_script("procurement", failure="raise OSError(5, 'denied', SECRET)"))

    def test_silent_audit_registration_suppression_is_denied(self):
        self.assert_private_boot_denied(startup_script("ledger", failure="return None"))

    def test_probe_failure_with_private_exception_is_redacted(self):
        self.assert_private_boot_denied(f'''
import sys, types
from fvs_suite import offline_network
from fvs_suite.launcher import launch
sys.modules['fvs_suite.app'] = types.SimpleNamespace(run=lambda _: print('UNSAFE GUI LOADED'))
offline_network.sys.addaudithook = lambda hook: None
offline_network.sys.audit = lambda event: (_ for _ in ()).throw(ValueError({SECRET!r}))
sys.argv = ['app.exe']
launch('ledger')
''')

    def test_direct_guard_registration_exception_is_privacy_safe_and_unchained(self):
        result = isolate(f'''
from fvs_suite import offline_network as guard
guard.sys.addaudithook = lambda hook: (_ for _ in ()).throw(RuntimeError({SECRET!r}))
try: guard.install_offline_guard()
except RuntimeError as exc:
    assert str(exc) == {DIRECT_ERROR!r}, repr(str(exc))
    assert exc.__context__ is None and exc.__cause__ is None
    assert guard._ENABLED is False
else: raise AssertionError('Unsafe installation success')
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(SECRET, result.stdout + result.stderr)

    def test_direct_guard_probe_exception_is_privacy_safe_and_unchained(self):
        result = isolate(f'''
from fvs_suite import offline_network as guard
guard.sys.addaudithook = lambda hook: None
guard.sys.audit = lambda event: (_ for _ in ()).throw(ValueError({SECRET!r}))
try: guard.install_offline_guard()
except RuntimeError as exc:
    assert str(exc) == {DIRECT_ERROR!r}, repr(str(exc))
    assert exc.__context__ is None and exc.__cause__ is None
    assert guard._ENABLED is False
else: raise AssertionError('Unsafe installation success')
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(SECRET, result.stdout + result.stderr)

    def test_launcher_failure_exit_has_no_hidden_exception_context(self):
        result = isolate(f'''
import sys
from fvs_suite import launcher
launcher.install_offline_guard = lambda: (_ for _ in ()).throw(ValueError({SECRET!r}))
sys.argv = ['app.exe']
try: launcher.launch('ledger')
except SystemExit as exc:
    assert str(exc) == {ERROR!r}, repr(str(exc))
    assert exc.__context__ is None and exc.__cause__ is None
else: raise AssertionError('Not blocked')
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn(SECRET, result.stdout + result.stderr)

    def test_boot_does_not_swallow_keyboard_interrupt(self):
        result = isolate(startup_script("ledger", failure="raise KeyboardInterrupt()"))
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(ERROR, result.stdout + result.stderr)

    def test_boot_does_not_swallow_system_exit(self):
        result = isolate(startup_script("ledger", failure="raise SystemExit(47)"))
        self.assertEqual(result.returncode, 47)
        self.assertNotIn(ERROR, result.stdout + result.stderr)

    def test_real_guard_blocks_network_and_process_events_after_boot(self):
        result = isolate('''
import sys
from fvs_suite.offline_network import install_offline_guard
install_offline_guard()
for event in ('socket.__new__','subprocess.Popen'):
    try: sys.audit(event, 'PRIVATE_PATH')
    except PermissionError as exc:
        if 'PRIVATE_PATH' in str(exc): raise AssertionError('Leaked sensitive data')
    else: raise AssertionError('Security fence unavailable')
''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_successful_gui_launch_all_six_apps(self):
        for app in APPS:
            with self.subTest(app=app):
                result = isolate(f'''
import sys, types
from fvs_suite.launcher import launch
sys.argv=['app.exe']
sys.modules['fvs_suite.app']=types.SimpleNamespace(run=lambda app_id: print('OK' if app_id == {app!r} else 'WRONG'))
launch({app!r})
''')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout.strip(), 'OK')

    def test_successful_smoke_remains_zero_exit(self):
        result = isolate('''
import sys, types
from fvs_suite.launcher import launch
sys.argv=['app.exe','--smoke-test']
sys.modules['fvs_suite.smoke']=types.SimpleNamespace(run_smoke=lambda app_id: ['safe-fixture.csv'])
launch('ledger')
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_successful_version_prints_without_gui(self):
        result = isolate('''
import sys
from fvs_suite.launcher import launch
sys.argv=['app.exe','--version']
launch('ledger')
''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), '0.1.0-dev')


if __name__ == "__main__":
    unittest.main()
