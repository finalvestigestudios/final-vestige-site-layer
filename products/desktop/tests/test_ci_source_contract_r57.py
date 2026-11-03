"""R57: full normal/-OO source evidence must run before Windows packaging."""
from __future__ import annotations

import io
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
import tempfile
import unittest

import ci_source_contract as guard

GOOD = '''name: Desktop suite build (internal)
on:
  pull_request:
jobs:
  source-tests:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065
      - name: Verify mandatory two-mode CI source gate (R57)
        run: python products/desktop/ci_source_contract.py .github/workflows/desktop-build.yml
      - name: Run full normal and optimized source suite (R57)
        run: |
          mkdir -p "$RUNNER_TEMP/fvs-source"
          python products/desktop/scripts/offline_source_gate.py --report "$RUNNER_TEMP/fvs-source/offline-source-suite.json"
      - name: Upload internal source-only evidence
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02
        with:
          name: final-vestige-desktop-source-only
          path: ${{ runner.temp }}/fvs-source/offline-source-suite.json
  windows-build:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065
      - name: Verify mandatory two-mode CI source gate (R57)
        run: python products/desktop/ci_source_contract.py .github/workflows/desktop-build.yml
      - name: Verify full source suite before packaging (R57)
        shell: pwsh
        run: |
          $env:PYTHONPATH = "products/desktop"
          python products/desktop/scripts/offline_source_gate.py
          if ($LASTEXITCODE -ne 0) { throw "Full source suite failed" }
      - name: Build six standalone Windows executables
        shell: pwsh
        run: |
          python -I -m PyInstaller --noconfirm --onefile Example.py
      - name: Upload Windows evidence only
        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02
        with:
          name: final-vestige-desktop-windows-internal
          path: dist/SHA256SUMS.txt
'''


class SourceContractR57Tests(unittest.TestCase):
    def reject(self, changed):
        with self.assertRaises(guard.SourceContractError):
            guard.verify_workflow(changed)

    def test_two_validated_jobs(self):
        self.assertEqual(guard.verify_workflow(GOOD), 2)

    def test_linux_missing_two_mode_suite(self):
        self.reject(GOOD.replace('offline_source_gate.py --report', 'source_smoke_gate.py --report'))

    def test_windows_missing_complete_suite(self):
        self.reject(GOOD.replace('python products/desktop/scripts/offline_source_gate.py\n',
                                 'python -m unittest discover -s products/desktop/tests\n'))

    def test_fail_open_windows_exit_code(self):
        self.reject(GOOD.replace('if ($LASTEXITCODE -ne 0) { throw "Full source suite failed" }',
                                 'Write-Host "pass"'))

    def test_windows_gate_after_build(self):
        start = GOOD.index('      - name: Verify full source suite before packaging (R57)')
        end = GOOD.index('      - name: Build six standalone Windows executables', start)
        block = GOOD[start:end]
        self.reject(GOOD[:start] + GOOD[end:] + block)

    def test_linux_evidence_report_cannot_be_removed(self):
        self.reject(GOOD.replace(' --report "$RUNNER_TEMP/fvs-source/offline-source-suite.json"', ''))

    def test_missing_windows_ci_source_preflight(self):
        mark = GOOD.index('  windows-build:')
        self.reject(GOOD[:mark] + GOOD[mark:].replace('run: ' + guard.POLICY_CMD,
                                                       'run: echo ignored', 1))

    def test_reject_conditional_skipping(self):
        self.reject(GOOD.replace('    runs-on: windows-latest',
                                 '    runs-on: windows-latest\n    if: false'))

    def test_reject_continue_on_error(self):
        self.reject(GOOD.replace('    runs-on: ubuntu-24.04',
                                 '    runs-on: ubuntu-24.04\n    continue-on-error: true'))

    def test_reject_pipeline_fail_open(self):
        self.reject(GOOD.replace('offline_source_gate.py --report',
                                 'offline_source_gate.py || true --report'))

    def test_duplicate_ci_job_rejected(self):
        self.reject(GOOD + '\n  source-tests:\n    runs-on: ubuntu-24.04')

    def test_extra_ci_job_requires_review(self):
        self.reject(GOOD + '\n  new-unreviewed-job:\n    runs-on: ubuntu-24.04')

    def test_privacy_safe_error_output(self):
        with tempfile.TemporaryDirectory(prefix='private-customer-fvs-') as tmp:
            path = Path(tmp) / 'customer-invoices.yml'
            path.write_text('jobs: invalid', encoding='utf-8')
            err = io.StringIO()
            with redirect_stderr(err):
                self.assertEqual(guard.main([str(path)]), 1)
            self.assertNotIn('customer', err.getvalue())
            self.assertNotIn(str(path), err.getvalue())

    def test_cli_good_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'workflow.yml'
            path.write_text(GOOD, encoding='utf-8')
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(guard.main([str(path)]), 0)
            self.assertIn('NOT Windows EXE/QD/release approval', stdout.getvalue())

    def test_r58_linux_exit_before_required_verifier_rejected(self):
        self.reject(GOOD.replace(
            '          python products/desktop/scripts/offline_source_gate.py --report',
            '          exit 0\n          python products/desktop/scripts/offline_source_gate.py --report', 1))

    def test_r58_windows_exit_before_required_verifier_rejected(self):
        self.reject(GOOD.replace(
            '          python products/desktop/scripts/offline_source_gate.py\n',
            '          exit 0\n          python products/desktop/scripts/offline_source_gate.py\n', 1))

    def test_r58_windows_throw_does_not_permit_interpolation(self):
        self.reject(GOOD.replace(
            'Full source suite failed',
            'Full source suite $([Environment]::Exit(0)) failed', 1))

    def test_r58_linux_command_in_here_doc_rejected(self):
        self.reject(GOOD.replace(
            '          mkdir -p "$RUNNER_TEMP/fvs-source"',
            "          cat <<'EOF'\n          mkdir -p \"$RUNNER_TEMP/fvs-source\"", 1))

    def test_real_workflow_when_checkout_available(self):
        workflow = Path(__file__).resolve().parents[3] / '.github/workflows/desktop-build.yml'
        if not workflow.is_file():
            self.skipTest('Full Git checkout not locally available')
        self.assertEqual(guard.verify_workflow(workflow.read_text(encoding='utf-8')), 2)


if __name__ == '__main__':
    unittest.main()
