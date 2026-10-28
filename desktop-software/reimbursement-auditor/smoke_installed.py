"""Windows acceptance smoke for the installed ReimbursementAuditor.exe.

Tests actual executable CLI behavior and report contents, not GUI navigation.
Never uses client data or makes network requests.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def write_packet(root: Path) -> tuple[Path, Path, Path]:
    folder = root / 'attachments'
    folder.mkdir()
    (folder / 'receipt.txt').write_text('FICTIONAL supporting note\n', encoding='utf-8')
    claims = root / 'claims.csv'
    support = root / 'support.csv'
    claims.write_text('vendor,invoice,amount\nFictional Vendor,INV-1,25.00\n', encoding='utf-8')
    support.write_text('vendor,invoice,amount,file\nFictional Vendor,INV-1,25.00,receipt.txt\n', encoding='utf-8')
    return claims, support, folder


def check_run(exe: Path, claims: Path, support: Path, folder: Path,
              report: Path, expected_code: int, expected_status: str | None) -> None:
    process = subprocess.run([str(exe), str(claims), str(support), str(folder),
                              '--report', str(report)],
                             timeout=90, capture_output=True, text=True)
    if process.returncode != expected_code:
        raise AssertionError(f'Expected exit {expected_code}, received {process.returncode}. '
                             f'stderr={process.stderr[:400]}')
    if expected_status is not None:
        if not report.is_file():
            raise AssertionError('Executable returned without writing expected report')
        result = json.loads(report.read_text(encoding='utf-8'))
        if result.get('status') != expected_status:
            raise AssertionError(f'Unexpected report status {result.get("status")!r}')
        if 'sha256' not in result.get('snapshot', {}).get('sources', {}).get('claims', {}):
            raise AssertionError('Report missing claims SHA-256 fingerprint')


def main() -> int:
    if len(sys.argv) != 2:
        print('Usage: python smoke_installed.py C:/path/ReimbursementAuditor.exe', file=sys.stderr)
        return 2
    exe = Path(sys.argv[1]).resolve(strict=True)
    if not exe.is_file():
        raise ValueError('Installed executable not found')
    with tempfile.TemporaryDirectory(prefix='fvs-reimbursement-smoke-') as temporary:
        root = Path(temporary)
        claims, support, folder = write_packet(root)
        report = root / 'clean.json'
        check_run(exe, claims, support, folder, report, 0, 'NO_FILE_OR_INDEX_EXCEPTIONS')
        original = report.read_bytes()
        check_run(exe, claims, support, folder, report, 2, None)
        if report.read_bytes() != original:
            raise AssertionError('Existing report was modified by executable')
        (folder / 'receipt.txt').unlink()
        check_run(exe, claims, support, folder, root / 'missing.json', 1, 'REVIEW')
        claims.write_text('vendor,invoice,invoice number,amount\nA,1,1,25.00\n',
                          encoding='utf-8')
        rejected = root / 'invalid.json'
        check_run(exe, claims, support, folder, rejected, 2, None)
        if rejected.exists():
            raise AssertionError('Invalid input unexpectedly produced a report')
    print('PASS: installed CLI, clean/report, overwrite defense, missing evidence, invalid columns')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
