"""R260: six-launcher fail-closed network gate and local-only allowances.

Subprocess isolation is mandatory: CPython audit hooks are permanent, and a
unit-test worker must never install a global hook affecting unrelated tests.
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPS = ("ledger", "invoices", "spend", "policy", "grants", "procurement")


def child(source: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-c", textwrap.dedent(source)],
        text=True, capture_output=True, env=env, timeout=15,
        check=False,
    )


class OfflineNetworkR260Tests(unittest.TestCase):
    def test_socket_creation_blocked_even_with_preimported_socket(self):
        result = child('''
            import socket
            from fvs_suite.offline_network import install_offline_guard
            S = socket.socket
            install_offline_guard()
            try: S()
            except PermissionError as exc:
                if str(exc) != "Network access is disabled for Final Vestige Labs": raise RuntimeError("wrong privacy-safe denial")
            else: raise RuntimeError("socket allowed")
        ''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_dns_and_urllib_requests_blocked(self):
        for command in (
            "socket.getaddrinfo('example.invalid', 443)",
            "socket.gethostbyname('example.invalid')",
            "urllib.request.urlopen('https://example.invalid')",
        ):
            with self.subTest(command=command):
                result = child('''
                    import socket, urllib.request
                    from fvs_suite.offline_network import install_offline_guard
                    install_offline_guard()
                    try: ''' + command + '''
                    except PermissionError as exc:
                        if str(exc) != "Network access is disabled for Final Vestige Labs": raise RuntimeError("wrong privacy-safe denial")
                    else: raise RuntimeError("network allowed")
                ''')
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_audit_hook_bypasses_none_of_the_important_socket_events(self):
        result = child('''
            import sys
            from fvs_suite.offline_network import install_offline_guard
            install_offline_guard()
            for event in ("socket.__new__", "socket.bind", "socket.connect",
                          "socket.sendto", "socket.sendmsg", "socket.getaddrinfo",
                          "socket.getnameinfo", "socket.gethostbyname",
                          "socket.gethostbyaddr", "socket.gethostname", "urllib.Request"):
                try: sys.audit(event, "SECRET_CUSTOMER_HOSTNAME")
                except PermissionError as exc:
                    if "SECRET_CUSTOMER_HOSTNAME" in str(exc): raise RuntimeError("leaked hostname")
                else: raise RuntimeError("Allowed " + event)
        ''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_local_filesystem_and_decimal_arithmetic_are_untouched(self):
        result = child('''
            import tempfile
            from decimal import Decimal
            from pathlib import Path
            from fvs_suite.offline_network import install_offline_guard
            install_offline_guard()
            with tempfile.TemporaryDirectory() as root:
                p = Path(root)/'ledger.csv'
                p.write_text('id,amount\\nA,1.01\\n')
                if 'A,1.01' not in p.read_text(): raise RuntimeError('filesystem broke')
            if Decimal('0.1') + Decimal('0.2') != Decimal('0.3'): raise RuntimeError('Decimal broke')
        ''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_guard_is_idempotent(self):
        result = child('''
            from fvs_suite import offline_network as guard
            count = [0]
            original = guard.sys.addaudithook
            def counting(hook):
                count[0] += 1
                original(hook)
            guard.sys.addaudithook = counting
            guard.install_offline_guard()
            guard.install_offline_guard()
            if count != [1]: raise RuntimeError("hook installed twice")
        ''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_cannot_boot_gui_if_guard_installation_fails(self):
        result = child('''
            import sys, types
            from fvs_suite import offline_network as guard
            from fvs_suite.launcher import launch
            guard.sys.addaudithook = lambda hook: (_ for _ in ()).throw(RuntimeError('disabled'))
            sys.argv = ['LedgerDiffLite.exe']
            sys.modules['fvs_suite.app'] = types.SimpleNamespace(run=lambda app: (_ for _ in ()).throw(AssertionError('GUI LOADED')))
            try: launch('ledger')
            except SystemExit as exc:
                if str(exc) != 'Final Vestige Labs security startup failed; no private diagnostics printed': raise
                if exc.__cause__ is not None or exc.__context__ is not None: raise RuntimeError('private context retained')
            else: raise AssertionError('guard bypassed')
        ''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_silent_hook_suppression_fails_before_gui(self):
        # A previous audit hook can silently suppress sys.addaudithook.
        result = child('''
            import sys, types
            from fvs_suite import offline_network as guard
            from fvs_suite.launcher import launch
            guard.sys.addaudithook = lambda hook: None
            sys.argv = ['LedgerDiffLite.exe']
            sys.modules['fvs_suite.app'] = types.SimpleNamespace(run=lambda app: (_ for _ in ()).throw(RuntimeError('GUI LOADED')))
            try: launch('ledger')
            except SystemExit as exc:
                if str(exc) != 'Final Vestige Labs security startup failed; no private diagnostics printed': raise
                if exc.__cause__ is not None or exc.__context__ is not None: raise RuntimeError('private context retained')
            else: raise RuntimeError('guard bypassed')
        ''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_all_six_real_launch_entries_enforce_block_before_gui(self):
        for app in APPS:
            with self.subTest(app=app):
                result = child('''
                    import sys, types, socket
                    from fvs_suite.launcher import launch
                    def app_run(name):
                        if name != "''' + app + '''": raise RuntimeError("wrong product")
                        try: socket.socket()
                        except PermissionError as exc:
                            if "Network access is disabled" not in str(exc): raise RuntimeError("wrong denial")
                        else: raise AssertionError("Network reachable from GUI")
                    sys.modules['fvs_suite.app'] = types.SimpleNamespace(run=app_run)
                    sys.argv = ['test.exe']
                    launch("''' + app + '''")
                ''')
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_smoke_mode_enforces_offline_guard_too(self):
        result = child('''
            import sys, types, socket
            from fvs_suite.launcher import launch
            def run_smoke(name):
                try: socket.socket()
                except PermissionError: return ["synthetic-report.csv"]
                raise RuntimeError("Network allowed")
            sys.modules['fvs_suite.smoke'] = types.SimpleNamespace(run_smoke=run_smoke)
            sys.argv = ['test.exe', '--smoke-test']
            try: launch('ledger')
            except SystemExit as exc:
                if exc.code != 0: raise RuntimeError("smoke failed")
            else: raise RuntimeError("Missing smoke exit")
        ''')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_version_output_remains_available(self):
        result = child('''
            import sys
            from fvs_suite.launcher import launch
            sys.argv = ['test.exe', '--version']
            launch('ledger')
        ''')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('0.1.0-dev', result.stdout)


if __name__ == '__main__':
    unittest.main()
