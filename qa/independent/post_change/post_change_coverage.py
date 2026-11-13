#!/usr/bin/env python3
"""Offline, read-only assessment of post-change Jetpack backup/scan evidence.

Input is a manually prepared, sanitized JSON snapshot of read-only site metadata.
There are no network calls, WordPress writes, email sends, paid API calls or imports.
"""
from __future__ import annotations
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def utc(value):
    """Return an aware UTC timestamp or None; never substitute now()."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        result = datetime.fromisoformat(value.strip().replace('Z', '+00:00'))
    except ValueError:
        return None
    return result.astimezone(timezone.utc) if result.tzinfo else None


def finding(code, status, detail):
    return {'code': code, 'status': status, 'detail': detail}


def inspect(snapshot):
    """Report evidence coverage, not security or recovery guarantees."""
    results = []
    changes = snapshot.get('changes', [])
    if not isinstance(changes, list):
        changes = []
    good = []
    invalid = 0
    for record in changes:
        t = utc(record.get('at')) if isinstance(record, dict) else None
        if t is None:
            invalid += 1
        else:
            good.append(t)
    if invalid:
        results.append(finding('INVALID_CHANGE_TIME', 'HOLD',
                               f'{invalid} change timestamp(s) are missing, invalid or not timezone-aware.'))
    if not good:
        results.append(finding('NO_CHANGE_BASELINE', 'HOLD',
                               'No valid deployment/activation timestamp; do not infer scan or backup coverage.'))
    if good and not invalid:
        latest = max(good)
        iso = latest.isoformat().replace('+00:00', 'Z')
        scan = snapshot.get('scan') or {}
        last_scan = scan.get('last_scan') or {}
        scan_started = utc(last_scan.get('started_at'))
        if scan_started is None:
            results.append(finding('POST_CHANGE_SCAN', 'HOLD', 'No usable Jetpack scan start time.'))
        elif scan_started <= latest:
            results.append(finding('POST_CHANGE_SCAN', 'HOLD',
                                   f'Latest scan started before or at last change ({iso}); a clean result is pre-change evidence.'))
        elif last_scan.get('error') is not False or last_scan.get('progress') != 100 or scan.get('state') not in ('idle', None):
            results.append(finding('POST_CHANGE_SCAN', 'HOLD',
                                   'Post-change scan not independently reported finished successfully.'))
        else:
            results.append(finding('POST_CHANGE_SCAN', 'COVERED',
                                   'Jetpack scan started after change and reports completion; not a code/security audit.'))
        backup = (snapshot.get('backup') or {}).get('backups') or {}
        backup_at = utc(backup.get('last_backup_when'))
        if backup_at is None or backup_at <= latest:
            results.append(finding('POST_CHANGE_BACKUP', 'HOLD',
                                   f'No verified snapshot newer than change ({iso}); last-attempt success alone is insufficient.'))
        elif backup.get('last_attempt_failed') is True or backup.get('last_attempt_status') != 'finished':
            results.append(finding('POST_CHANGE_BACKUP', 'HOLD',
                                   'Post-change snapshot exists but most recent backup attempt is not reported successful.'))
        else:
            results.append(finding('POST_CHANGE_BACKUP', 'COVERED',
                                   'Jetpack reports a post-change backup and successful latest attempt; restore not proven.'))
    restore = snapshot.get('restore') or {}
    last_restore = restore.get('last_restore') or {}
    preflight = (snapshot.get('backup') or {}).get('restore_preflight_status')
    if preflight is None or not last_restore.get('has_restore_record'):
        results.append(finding('RESTORE_PROOF', 'HOLD',
                               'No verified restore preflight and successful restoration rehearsal; never run one as a test on production.'))
    else:
        results.append(finding('RESTORE_PROOF', 'REVIEW',
                               'Restore evidence exists; verify timestamps, scope and actual completed outcome independently.'))
    warnings = snapshot.get('backup_log_warnings') or []
    charsets = [w for w in warnings if isinstance(w, dict) and
                'connection encoding and table charset mismatch' in str(w.get('message', '')).lower()]
    if charsets:
        results.append(finding('BACKUP_CHARSET_WARNING', 'REVIEW',
                               f'{len(charsets)} backup log warning(s) describe connection/table charset mismatches; '+
                               'no data loss is established. Ask backup owner to validate safe restore fidelity.'))
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('snapshot', type=Path)
    ap.add_argument('--strict', action='store_true', help='Return 2 if any HOLD finding exists.')
    args = ap.parse_args(argv)
    payload = json.loads(args.snapshot.read_text(encoding='utf-8'))
    findings = inspect(payload)
    print(json.dumps({'scope': 'LOCAL_SNAPSHOT_ONLY', 'findings': findings}, indent=2))
    return 2 if args.strict and any(f['status'] == 'HOLD' for f in findings) else 0


if __name__ == '__main__':
    raise SystemExit(main())
