#!/usr/bin/env python3
"""Offline, fail-closed post-change protection-evidence checker. Never contacts WordPress."""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path


def instant(value):
    """Require an explicit timezone; normalize timestamps to comparable instants."""
    if not isinstance(value, str):
        raise ValueError('timestamp must be a string')
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise ValueError('invalid timestamp') from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError('timezone required')
    return parsed


def evaluate(snapshot):
    """Return narrow evidence result, never an overall production readiness verdict."""
    failures = []

    def fail(code):
        if code not in failures:
            failures.append(code)

    if not isinstance(snapshot, dict):
        return {'status': 'HOLD', 'failures': ['INVALID_SNAPSHOT']}
    change = snapshot.get('change') or {}
    backup = snapshot.get('backup') or {}
    scan = snapshot.get('scan') or {}
    if not all(isinstance(x, dict) for x in (change, backup, scan)):
        return {'status': 'HOLD', 'failures': ['INVALID_SNAPSHOT']}
    try:
        changed_at = instant(change.get('at'))
        if change.get('kind') not in {'plugin_activated', 'plugin_updated'}:
            fail('UNSUPPORTED_CHANGE')
        slug = change.get('slug')
        if not isinstance(slug, str) or not slug.strip():
            fail('MISSING_PLUGIN_IDENTITY')
    except ValueError:
        changed_at = None
        slug = None
        fail('INVALID_CHANGE_TIME')

    try:
        backup_started = instant(backup.get('started_at'))
        backup_completed = instant(backup.get('completed_at'))
        if backup_completed < backup_started:
            fail('BACKUP_TIME_ORDER')
        if changed_at and backup_started <= changed_at:
            fail('BACKUP_PRE_DATES_CHANGE')
    except ValueError:
        fail('INVALID_BACKUP_TIME')
    if backup.get('last_attempt_failed') is not False:
        fail('BACKUP_LAST_ATTEMPT_UNVERIFIED')
    if backup.get('type') != 'full':
        fail('FULL_BACKUP_UNVERIFIED')
    if not isinstance(backup.get('plugins'), list) or not slug or slug not in backup['plugins']:
        fail('PLUGIN_MISSING_FROM_BACKUP')
    if backup.get('errors') != [] or backup.get('warnings') != []:
        fail('BACKUP_ERRORS_OR_WARNINGS_UNVERIFIED')

    try:
        scan_started = instant(scan.get('started_at'))
        duration = scan.get('duration_seconds')
        if changed_at and scan_started <= changed_at:
            fail('SCAN_PRE_DATES_CHANGE')
        if type(duration) is not int or duration < 0:
            fail('INVALID_SCAN_DURATION')
    except ValueError:
        fail('INVALID_SCAN_TIME')
    if scan.get('error') is not False or scan.get('progress') != 100:
        fail('SCAN_INCOMPLETE_OR_FAILED')
    if scan.get('threats') != [] or scan.get('ignored_threats') != []:
        fail('SCAN_THREATS_NOT_CLEARED')

    return {'status': 'PASS' if not failures else 'HOLD', 'failures': failures,
            'scope': 'post-change backup and Jetpack Scan evidence only; not installed-byte identity or frontend acceptance'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path, help='sanitized local JSON; never send subscriber or access data')
    args = parser.parse_args(argv)
    try:
        data = json.loads(args.snapshot.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(str(exc))
    report = evaluate(data)
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
