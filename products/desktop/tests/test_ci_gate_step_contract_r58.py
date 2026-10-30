"""R58: source test string presence must never substitute for execution."""
from __future__ import annotations

import unittest

from ci_gate_step_contract import GateStepError, verify_gate_step


LINUX = '''      - name: Verify full normal/optimized source provenance and six smokes (R57)
        run: |
          mkdir -p "$RUNNER_TEMP/fvs-source"
          python products/desktop/scripts/offline_source_gate.py --report "$RUNNER_TEMP/fvs-source/offline-source-suite.json"'''
WINDOWS = '''      - name: Verify full normal/optimized source suite before packaging (R57)
        shell: pwsh
        run: |
          $env:PYTHONPATH = "products/desktop"
          python products/desktop/scripts/offline_source_gate.py
          if ($LASTEXITCODE -ne 0) { throw "R57 complete source and engine smoke verification FAILED" }'''


class CIExecutedGateContractR58(unittest.TestCase):
    def reject(self, changed, platform):
        with self.assertRaises(GateStepError):
            verify_gate_step(changed, platform)

    def test_valid_linux_step(self):
        self.assertIsNone(verify_gate_step(LINUX, 'linux'))

    def test_valid_windows_step(self):
        self.assertIsNone(verify_gate_step(WINDOWS, 'windows'))

    def test_original_r57_windows_fixture(self):
        self.assertIsNone(verify_gate_step(WINDOWS.replace(
            'R57 complete source and engine smoke verification FAILED',
            'Full source suite failed'), 'windows'))

    def test_linux_exit_before_mkdir(self):
        self.reject(LINUX.replace('          mkdir', '          exit 0\n          mkdir'), 'linux')

    def test_linux_exit_after_mkdir(self):
        self.reject(LINUX.replace('          python', '          exit 0\n          python'), 'linux')

    def test_linux_exit_after_verifier(self):
        self.reject(LINUX + '\n          exit 0', 'linux')

    def test_linux_here_doc(self):
        self.reject(LINUX.replace('          mkdir', "          cat <<'EOF'\n          mkdir") + '\n          EOF', 'linux')

    def test_linux_echo(self):
        self.reject(LINUX.replace('          mkdir', '          echo recorded\n          mkdir'), 'linux')

    def test_linux_conditional(self):
        self.reject(LINUX.replace('          python', '          if true; then\n          python'), 'linux')

    def test_linux_second_run_key(self):
        self.reject(LINUX + '\n        run: echo ok', 'linux')

    def test_linux_continue_on_error(self):
        self.reject(LINUX.replace('        run: |', '        continue-on-error: true\n        run: |'), 'linux')

    def test_linux_folded_run(self):
        self.reject(LINUX.replace('run: |', 'run: >'), 'linux')

    def test_linux_extra_command(self):
        self.reject(LINUX + '\n          :', 'linux')

    def test_windows_exit_before_env(self):
        self.reject(WINDOWS.replace('          $env:', '          exit 0\n          $env:'), 'windows')

    def test_windows_exit_before_verifier(self):
        self.reject(WINDOWS.replace('          python', '          exit 0\n          python'), 'windows')

    def test_windows_return_before_verifier(self):
        self.reject(WINDOWS.replace('          python', '          return\n          python'), 'windows')

    def test_windows_exit_after_verifier(self):
        self.reject(WINDOWS + '\n          exit 0', 'windows')

    def test_windows_missing_exitcode_guard(self):
        self.reject(WINDOWS.replace(
            '          if ($LASTEXITCODE -ne 0) { throw "R57 complete source and engine smoke verification FAILED" }',
            '          Write-Host "pass"'), 'windows')

    def test_windows_powershell_interpolation(self):
        self.reject(WINDOWS.replace('verification FAILED',
                                    'verification $([System.IO.File]::Delete("X")) FAILED'), 'windows')

    def test_windows_powershell_backtick(self):
        self.reject(WINDOWS.replace('verification FAILED',
                                    'verification ' + chr(96) + '" FAILED'), 'windows')

    def test_windows_shell_changed(self):
        self.reject(WINDOWS.replace('shell: pwsh', 'shell: cmd'), 'windows')

    def test_windows_here_string(self):
        self.reject(WINDOWS.replace('          $env:', "          @'\n          $env:"), 'windows')

    def test_windows_step_env(self):
        self.reject(WINDOWS.replace('        shell: pwsh',
                                    '        env:\n          SKIP: 1\n        shell: pwsh'), 'windows')

    def test_invalid_encoding_and_platform(self):
        self.reject(LINUX, 'powershell')
        self.reject(LINUX + '\x00', 'linux')
        self.reject(WINDOWS + '\r', 'windows')
        self.reject(LINUX + (' ' * 2048), 'linux')

    def test_missing_name(self):
        self.reject(LINUX.replace('- name:', '- uses:'), 'linux')


if __name__ == '__main__':
    unittest.main()
