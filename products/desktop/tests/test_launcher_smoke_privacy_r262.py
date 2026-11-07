"""R262: never print customer paths or exception chains from private smoke runs.

Every case runs a disposable Python interpreter: the offline audit hook is
process-global and deliberately cannot be uninstalled between test cases.
These are source-level checks, NOT genuine Windows packaged-EXE evidence.
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
MESSAGE = "Final Vestige Labs smoke test failed; no private diagnostics printed"
SECRET = "C:/Customers/Private Account 789/SECRET_GRANT_LEDGER_2026.csv"


def isolate(source: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run([sys.executable, "-c", textwrap.dedent(source)],
                          env=env, capture_output=True, text=True, timeout=20,
                          check=False)


def smoke_script(expression: str, app: str = "ledger") -> str:
    return """
import sys, types
from fvs_suite.launcher import launch
fake = types.ModuleType('fvs_suite.smoke')
def run_smoke(app_id):
    if app_id != %r: raise AssertionError('incorrect app dispatch')
    %s
fake.run_smoke = run_smoke
sys.modules['fvs_suite.smoke'] = fake
sys.argv = ['FinalVestige.exe', '--smoke-test']
launch(%r)
""" % (app, expression, app)


class LauncherSmokePrivacyR262(unittest.TestCase):
    def assert_private_failure(self, source: str) -> None:
        result = isolate(source)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stderr.strip(), MESSAGE)
        self.assertEqual(result.stdout, "")
        self.assertNotIn(SECRET, result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_all_six_launchers_redact_private_runtime_errors(self):
        for app in APPS:
            with self.subTest(app=app):
                self.assert_private_failure(smoke_script("raise RuntimeError(%r)" % SECRET, app))

    def test_oserror_file_path_is_not_printed(self):
        self.assert_private_failure(smoke_script("raise OSError(5, 'access denied', %r)" % SECRET))

    def test_unicode_error_private_bytes_are_not_printed(self):
        self.assert_private_failure(smoke_script("raise UnicodeError(%r)" % SECRET))

    def test_exception_cause_private_data_not_printed(self):
        self.assert_private_failure(smoke_script("raise RuntimeError('public') from ValueError(%r)" % SECRET))

    def test_empty_output_remains_failure_without_traceback(self):
        self.assert_private_failure(smoke_script("return []"))

    def test_none_output_remains_failure_without_traceback(self):
        self.assert_private_failure(smoke_script("return None"))

    def test_untrusted_output_bool_error_redacted(self):
        self.assert_private_failure(smoke_script("return type('Unsafe', (), {'__bool__': lambda self: (_ for _ in ()).throw(ValueError(%r))})()" % SECRET))

    def test_import_error_from_missing_smoke_module_redacted(self):
        source = """
import sys
from fvs_suite.launcher import launch
sys.argv = ['FinalVestige.exe', '--smoke-test']
launch('ledger')
"""
        self.assert_private_failure(source)

    def test_success_path_exits_zero_without_error_logging(self):
        result = isolate(smoke_script("return ['synthetic-report.csv']"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_real_offline_guard_active_inside_smoke(self):
        result = isolate(smoke_script("""import sys
    try:
        sys.audit('subprocess.Popen', %r)
    except PermissionError:
        return ['synthetic-report.csv']
    raise AssertionError('process was not blocked')""" % SECRET))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_version_still_prints_public_version(self):
        result = isolate("""
import sys
from fvs_suite.launcher import launch
sys.argv = ['LedgerDiffLite.exe', '--version']
launch('ledger')
""")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "0.1.0-dev")

    def test_bad_cli_arguments_still_fail_closed(self):
        result = isolate("""
import sys
from fvs_suite.launcher import launch
sys.argv = ['LedgerDiffLite.exe', '--publish']
launch('ledger')
""")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Unsupported arguments', result.stderr)

    def test_keyboard_interrupt_is_not_consumed(self):
        result = isolate(smoke_script("raise KeyboardInterrupt()"))
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(MESSAGE, result.stderr)

    def test_system_exit_is_not_converted_to_success(self):
        result = isolate(smoke_script("raise SystemExit(47)"))
        self.assertEqual(result.returncode, 47)

    def test_failure_exit_context_is_empty(self):
        result = isolate("""
import sys, types
from fvs_suite.launcher import launch
fake=types.ModuleType('fvs_suite.smoke')
def run_smoke(_):
    raise RuntimeError('TOPSECRET')
fake.run_smoke=run_smoke
sys.modules['fvs_suite.smoke']=fake
sys.argv=['app.exe','--smoke-test']
try: launch('ledger')
except SystemExit as e:
    if e.__context__ is not None or e.__cause__ is not None:
        raise RuntimeError('Exception context retained')
    if str(e) != 'Final Vestige Labs smoke test failed; no private diagnostics printed':
        raise RuntimeError('Unexpected error text')
else: raise AssertionError('Did not fail')
""")
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
