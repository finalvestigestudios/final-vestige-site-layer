"""R261: process escape denial and inherited offline network behavior.

Each test executes its subject in a fresh interpreter. Audit hooks cannot be
uninstalled, so sharing a test interpreter would contaminate unrelated tests.
No network or external process is intentionally started by these tests.
"""
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DENIAL = "External process launch is disabled for Final Vestige Labs"


def child(source: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run([sys.executable, "-c", textwrap.dedent(source)],
                          capture_output=True, text=True, timeout=20, env=env,
                          check=False)


class OfflineProcessR261Tests(unittest.TestCase):
    def expect_ok(self, source: str) -> None:
        result = child(source)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_actual_subprocess_run_is_rejected_before_execution(self):
        self.expect_ok('''
            import subprocess, sys, tempfile
            from pathlib import Path
            from fvs_suite.offline_network import install_offline_guard
            with tempfile.TemporaryDirectory() as t:
                marker = Path(t) / 'unwanted.txt'
                install_offline_guard()
                try:
                    subprocess.run([sys.executable, '-c', 'open(' + repr(str(marker)) + ', "w").write("oops")'], check=True)
                except PermissionError as e:
                    if str(e) != 'External process launch is disabled for Final Vestige Labs': raise
                else: raise RuntimeError('Child process was launched')
                if marker.exists(): raise RuntimeError('Child process wrote file')
        ''')

    def test_actual_popen_is_rejected_even_when_preimported(self):
        self.expect_ok('''
            from subprocess import Popen
            import sys
            from fvs_suite.offline_network import install_offline_guard
            install_offline_guard()
            try: Popen([sys.executable, '--version'])
            except PermissionError as e:
                if 'External process launch is disabled' not in str(e): raise
            else: raise RuntimeError('Popen was allowed')
        ''')

    def test_actual_system_shell_is_rejected(self):
        self.expect_ok('''
            import os
            from fvs_suite.offline_network import install_offline_guard
            install_offline_guard()
            try: os.system('echo SHOULD_NOT_RUN')
            except PermissionError as e:
                if 'External process launch is disabled' not in str(e): raise
            else: raise RuntimeError('Shell was allowed')
        ''')

    def test_actual_spawnv_is_rejected_where_available(self):
        self.expect_ok('''
            import os, sys
            from fvs_suite.offline_network import install_offline_guard
            install_offline_guard()
            if hasattr(os, 'spawnv'):
                try: os.spawnv(os.P_WAIT, sys.executable, [sys.executable, '--version'])
                except PermissionError as e:
                    if 'External process launch is disabled' not in str(e): raise
                else: raise RuntimeError('Spawn was allowed')
        ''')

    def test_actual_posix_spawn_is_rejected_where_available(self):
        self.expect_ok('''
            import os, sys
            from fvs_suite.offline_network import install_offline_guard
            install_offline_guard()
            if hasattr(os, 'posix_spawn'):
                try: os.posix_spawn(sys.executable, [sys.executable, '--version'], os.environ)
                except PermissionError as e:
                    if 'External process launch is disabled' not in str(e): raise
                else: raise RuntimeError('posix_spawn was allowed')
        ''')

    def test_actual_execv_is_rejected_without_replacing_interpreter(self):
        self.expect_ok('''
            import os, sys
            from fvs_suite.offline_network import install_offline_guard
            install_offline_guard()
            try: os.execv(sys.executable, [sys.executable, '--version'])
            except PermissionError as e:
                if 'External process launch is disabled' not in str(e): raise
            else: raise RuntimeError('Interpreter was replaced')
        ''')

    def test_actual_fork_is_rejected_where_available(self):
        self.expect_ok('''
            import os
            from fvs_suite.offline_network import install_offline_guard
            install_offline_guard()
            if hasattr(os, 'fork'):
                try: pid = os.fork()
                except PermissionError as e:
                    if 'External process launch is disabled' not in str(e): raise
                else:
                    if pid == 0: os._exit(75)
                    os.waitpid(pid, 0)
                    raise RuntimeError('Fork was allowed')
        ''')

    def test_audit_event_matrix_rejects_all_process_creation_events(self):
        self.expect_ok('''
            import sys
            from fvs_suite.offline_network import install_offline_guard
            install_offline_guard()
            for event in ('subprocess.Popen', 'os.system', 'os.spawn',
                          'os.posix_spawn', 'os.exec', 'os.fork', 'os.forkpty',
                          'os.startfile', 'os.startfile/2'):
                try: sys.audit(event, 'PRIVATE_CUSTOMER_PATH')
                except PermissionError as e:
                    if str(e) != 'External process launch is disabled for Final Vestige Labs': raise
                    if 'PRIVATE_CUSTOMER_PATH' in str(e): raise RuntimeError('leaked')
                else: raise RuntimeError('Allowed ' + event)
        ''')

    def test_network_denial_still_holds_after_process_rules_added(self):
        self.expect_ok('''
            import socket
            from fvs_suite.offline_network import install_offline_guard
            install_offline_guard()
            try: socket.socket()
            except PermissionError as e:
                if str(e) != 'Network access is disabled for Final Vestige Labs': raise
            else: raise RuntimeError('Socket allowed')
        ''')

    def test_local_decimal_and_file_processing_still_work(self):
        self.expect_ok('''
            from pathlib import Path
            from tempfile import TemporaryDirectory
            from decimal import Decimal
            from fvs_suite.offline_network import install_offline_guard
            install_offline_guard()
            with TemporaryDirectory() as t:
                p = Path(t) / 'private.csv'
                p.write_text('amount\\n0.30\\n', encoding='utf-8')
                if p.read_text(encoding='utf-8') != 'amount\\n0.30\\n': raise RuntimeError('file blocked')
            if Decimal('0.10') + Decimal('0.20') != Decimal('0.30'): raise RuntimeError('money changed')
        ''')

    def test_process_denial_remains_active_after_double_installation(self):
        self.expect_ok('''
            import sys
            from fvs_suite.offline_network import install_offline_guard
            install_offline_guard()
            install_offline_guard()
            try: sys.audit('subprocess.Popen', 'PRIVATE')
            except PermissionError as e:
                if 'PRIVATE' in str(e): raise RuntimeError('leak')
            else: raise RuntimeError('Guard disabled on second call')
        ''')

    def test_unknown_audit_events_remain_allowed(self):
        self.expect_ok('''
            import sys
            from fvs_suite.offline_network import install_offline_guard
            install_offline_guard()
            sys.audit('fvs.example.local_event', {'count': 1})
        ''')

    def test_no_process_spawn_required_for_version_dispatch(self):
        self.expect_ok('''
            import sys
            from fvs_suite.launcher import launch
            sys.argv = ['LedgerDiffLite.exe', '--version']
            launch('ledger')
        ''')


if __name__ == '__main__':
    unittest.main()
