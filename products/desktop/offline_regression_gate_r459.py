"""Independent source-only regression gate when GitHub-hosted runners cannot start.

Runs R455-R458 actual unittest modules in normal and optimized Python, then
invokes the existing six-launcher R408 smoke gate. Neither result is a Windows
executable, Defender, accessibility, entitlement, QD or distribution approval.
No paths, customer data or subprocess logs are emitted to the operator.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from offline_json_receipt_r462 import PrivateReceiptJSONError, load_private_receipt
from offline_smoke_receipt_r460 import MAX_RECEIPT_BYTES
from offline_source_binding_r461 import (
    SourceBindingError, verified_six_app_digest, require_bound_six_app_smokes,
)

TESTS = (
    "test_csv_negative_decimal_zero_copy_r455.py",
    "test_csv_safe_cell_zero_copy_r456.py",
    "test_csv_incremental_render_budget_r457.py",
    "test_csv_bounded_utf8_witness_r458.py",
    "test_source_digest_binding_r461.py",
    "test_private_json_receipt_r462.py",
)
SOURCE_INPUTS = (
    "offline_regression_gate_r459.py",
    "offline_smoke_receipt_r460.py",
    "offline_source_binding_r461.py",
    "offline_json_receipt_r462.py",
    "offline_source_smoke_r408.py",
    "fvs_suite/atomic_reports.py",
    "fvs_suite/engine.py",
    *("tests/" + name for name in TESTS),
    "tests/test_offline_regression_gate_r459.py",
    "tests/test_offline_smoke_receipt_r460.py",
    "tests/test_source_digest_binding_r461.py",
)
TIMEOUT_TEST_SECONDS = 120
TIMEOUT_SMOKE_SECONDS = 330
# The child is confined to this exact, local Git checkout. Do not propagate
# financial credentials, network proxy variables, arbitrary PYTHONPATH, or
# process-specific application settings into its environment.
_ALLOWED_ENV = frozenset({
    "PATH", "PATHEXT", "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR",
})

# The only output from each child test interpreter is a private, tiny, fixed-
# schema JSON receipt. unittest diagnostic traces are sent to DEVNULL, never
# captured/replayed into this gate or its final operator-facing JSON.
_TEST_CHILD = r'''
import io,json,sys,unittest
from pathlib import Path
root=Path(sys.argv[1]); pattern=sys.argv[2]; receipt=Path(sys.argv[3])
sys.path.insert(0,str(root))
try:
    suite=unittest.TestLoader().discover(start_dir=str(root/'tests'),pattern=pattern)
    expected=suite.countTestCases()
    if not expected: raise RuntimeError('no tests discovered')
    result=unittest.TextTestRunner(stream=io.StringIO(),verbosity=0).run(suite)
    info={'tests':result.testsRun,'failures':len(result.failures),
          'errors':len(result.errors),'skipped':len(result.skipped),
          'expected':expected}
    with receipt.open('x',encoding='ascii') as output:
        json.dump(info,output,separators=(',',':'))
    sys.exit(0 if result.wasSuccessful() and result.testsRun==expected
             and not result.skipped else 2)
except Exception:
    sys.exit(3)
'''


class LocalGateError(ValueError):
    """Redacted fail-closed error without the test runner's private details."""


def _child_env() -> dict[str, str]:
    return {key: val for key, val in os.environ.items() if key.upper() in _ALLOWED_ENV}


def _source_fingerprint(desktop: Path) -> str:
    """Bind this receipt to the local test files; not a signed source audit."""
    digest = hashlib.sha256()
    for relative in SOURCE_INPUTS:
        path = desktop / relative
        try:
            if path.is_symlink() or not path.is_file() or path.stat().st_size > 2_000_000:
                raise LocalGateError("Local source regression inventory rejected")
            source = path.read_bytes()
            if not source:
                raise LocalGateError("Local source regression inventory rejected")
        except OSError:
            raise LocalGateError("Local source regression inventory rejected") from None
        digest.update(relative.encode('ascii') + b'\0')
        digest.update(len(source).to_bytes(8, 'big'))
        digest.update(hashlib.sha256(source).digest())
    return digest.hexdigest()


def _validate_receipt(raw: bytes) -> int:
    """Never treat a zero-test, skipped, partial or forged success as PASS."""
    if len(raw) > 1024:
        raise LocalGateError("Local source regression receipt rejected")
    try:
        item = load_private_receipt(raw)
    except PrivateReceiptJSONError:
        raise LocalGateError("Local source regression receipt rejected") from None
    if (type(item) is not dict or set(item) != {
            'tests', 'failures', 'errors', 'skipped', 'expected'}
            or any(type(item[key]) is not int for key in item)
            or not 1 <= item['tests'] == item['expected'] <= 10000
            or any(item[key] != 0 for key in ('failures', 'errors', 'skipped'))):
        raise LocalGateError("Local source regression receipt rejected")
    return item['tests']


def _run_tests(desktop: Path) -> tuple[int, int]:
    methods = 0
    executions = 0
    # Use an owner-private disposable folder, not a source/destination folder.
    with tempfile.TemporaryDirectory(prefix='fvs-r459-') as temp:
        for pattern in TESTS:
            for optimized in (False, True):
                receipt = Path(temp) / ('receipt-' + str(executions) + '.json')
                command = [sys.executable, '-I', '-B', '-W', 'error']
                if optimized:
                    command.append('-OO')
                command.extend(['-c', _TEST_CHILD, str(desktop), pattern, str(receipt)])
                try:
                    result = subprocess.run(
                        command, cwd=desktop, env=_child_env(),
                        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL, timeout=TIMEOUT_TEST_SECONDS,
                        check=False)
                    if result.returncode != 0:
                        raise LocalGateError("Local source regression test failed")
                    # Read at most 1,025 bytes even if a buggy child wrote a huge receipt.
                    with receipt.open('rb') as response:
                        methods += _validate_receipt(response.read(1025))
                except (OSError, subprocess.TimeoutExpired):
                    raise LocalGateError("Local source regression could not execute") from None
                executions += 1
    return executions, methods


def _run_smokes(desktop: Path, expected_digest: str) -> int:
    """Prove R408's twelve actual statuses from a bounded private JSON receipt."""
    command = [sys.executable, '-I', '-B', '-W', 'error',
               str(desktop / 'offline_source_smoke_r408.py')]
    try:
        # Never PIPE untrusted application output into an unbounded buffer.
        # The temporary file is owner-private and never exposed as a public artifact.
        with tempfile.TemporaryFile(mode='w+b') as response:
            completed = subprocess.run(
                command, cwd=desktop, env=_child_env(),
                stdin=subprocess.DEVNULL, stdout=response,
                stderr=subprocess.DEVNULL, timeout=TIMEOUT_SMOKE_SECONDS,
                check=False)
            if completed.returncode != 0:
                raise LocalGateError("Local six-app source smoke failed")
            response.seek(0)
            raw = response.read(MAX_RECEIPT_BYTES + 1)
    except (OSError, subprocess.TimeoutExpired):
        raise LocalGateError("Local source smoke could not execute") from None
    try:
        return require_bound_six_app_smokes(raw, expected_digest)
    except SourceBindingError:
        raise LocalGateError("Local six-app source smoke receipt rejected") from None


def _six_source_digest(desktop: Path) -> str:
    """Attest R408's full import-root + six-launcher inventory, not a subset."""
    try:
        return verified_six_app_digest(desktop)
    except SourceBindingError:
        raise LocalGateError("Local six-app source inventory rejected") from None


def run_gate(desktop: Path) -> dict[str, object]:
    if not desktop.is_absolute() or desktop.is_symlink() or not desktop.is_dir():
        raise LocalGateError("Local source regression directory rejected")
    before = _source_fingerprint(desktop)
    full_before = _six_source_digest(desktop)
    modes, tests = _run_tests(desktop)
    if (_source_fingerprint(desktop) != before or
            _six_source_digest(desktop) != full_before):
        raise LocalGateError("Local regression sources changed during tests")
    smokes = _run_smokes(desktop, full_before)
    if (_source_fingerprint(desktop) != before or
            _six_source_digest(desktop) != full_before):
        raise LocalGateError("Local regression sources changed during smoke checks")
    return {
        'schema': 'fvs-offline-regression-r459-v1',
        'source_sha256': before,
        'regression_mode_runs': modes,
        'regression_methods_passed': tests,
        'launcher_source_smokes_passed': smokes,
        'launcher_source_smokes_required': 12,
        'evidence': 'SOURCE_ONLY_NOT_WINDOWS_BINARY',
        'release_authorized': False,
    }


def main() -> int:
    desktop = Path(os.path.abspath(__file__)).parent
    try:
        result = run_gate(desktop)
    except LocalGateError:
        print('{"status":"HOLD","reason":"Local source regression gate failed","release_authorized":false}')
        return 1
    print(json.dumps(result, sort_keys=True, separators=(',', ':')))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
