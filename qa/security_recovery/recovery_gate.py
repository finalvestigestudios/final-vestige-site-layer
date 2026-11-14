#!/usr/bin/env python3
"""Offline, fail-closed Jetpack vulnerability-fix/recovery chronology acceptance.

Accepts a SANITIZED local JSON snapshot. No credentials, network, WordPress API
calls, file writes or site mutations. It is not a penetration or restore test.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc(raw):
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        v = datetime.fromisoformat(raw.strip().replace('Z', '+00:00'))
    except ValueError:
        return None
    return v.astimezone(timezone.utc) if v.tzinfo is not None else None


def version_tuple(raw):
    if not isinstance(raw, str):
        return None
    parts = raw.split('.')
    if not parts or not all(p.isdigit() for p in parts):
        return None
    return tuple(int(x) for x in parts)


def check(snapshot):
    """Return individual evidence-based gates, never infer restore fidelity."""
    if not isinstance(snapshot, dict):
        raise ValueError('expected a JSON object')
    plugin = snapshot.get('plugin') or {}
    scan = snapshot.get('scan') or {}
    backup = snapshot.get('backup') or {}
    activity = snapshot.get('activity') or []
    min_fixed = version_tuple(snapshot.get('fixed_version', '3.7.5'))
    installed = version_tuple(plugin.get('version'))
    if not min_fixed:
        raise ValueError('fixed_version must be a numeric dotted version')
    fixes = [f for f in scan.get('recent_fixes', []) if
             f.get('status') == 'fixed' and
             'burst-statistics' in str(f.get('description', '')).lower()]
    patch_at = max((d for d in (utc(f.get('fixed_on')) for f in fixes) if d), default=None)
    events = [e for e in activity if isinstance(e, dict)]
    completions = [d for d in (utc(e.get('date')) for e in events
                     if e.get('action') == 'backup_complete_full') if d]
    backup_completed = max(completions, default=None)
    last_scan = scan.get('last_scan') or {}
    scan_started = utc(last_scan.get('started_at'))
    # A timestamp and error=False alone do not prove the scan completed.
    # This strictly requires the Jetpack status snapshot's full progress and idle state.
    scan_complete = (scan.get('state') == 'idle'
                     and type(last_scan.get('progress')) is int
                     and last_scan['progress'] == 100
                     and last_scan.get('error') is False)
    last = backup.get('backups') or {}
    results = []

    def gate(code, passed, evidence, note):
        results.append({'gate': code, 'status': 'PASS' if passed else 'HOLD',
                        'evidence': evidence, 'note': note})

    gate('PATCHED_PLUGIN_ACTIVE', installed is not None and installed >= min_fixed
         and plugin.get('status') == 'active',
         f"installed={plugin.get('version', 'UNKNOWN')}, required>={snapshot.get('fixed_version', '3.7.5')}, status={plugin.get('status', 'UNKNOWN')}",
         'Only an authenticated installed-version snapshot, not merely a fixer log, establishes the version.')
    gate('NO_REPORTED_ACTIVE_THREAT', scan.get('threats') == [] and scan.get('ignored_threats') == [],
         f"active={len(scan.get('threats') or []) if 'threats' in scan else 'UNKNOWN'}; ignored={len(scan.get('ignored_threats') or []) if 'ignored_threats' in scan else 'UNKNOWN'}",
         'No reported threats is not forensic proof of no exploitation.')
    gate('FIX_EVENT_TIMESTAMPED', patch_at is not None,
         patch_at.isoformat() if patch_at else 'UNKNOWN',
         'A documented fix time is necessary to compare backup/scan chronology.')
    gate('POST_FIX_FULL_BACKUP', patch_at is not None and backup_completed is not None
         and backup_completed > patch_at and last.get('last_attempt_failed') is False
         and last.get('last_attempt_status') == 'finished',
         f"backup_completed={backup_completed.isoformat() if backup_completed else 'UNKNOWN'}; patch={patch_at.isoformat() if patch_at else 'UNKNOWN'}; last_attempt={last.get('last_attempt_status', 'UNKNOWN')}",
         'A pre-fix recovery point can restore a vulnerable plugin; independently check post-restore version.')
    gate('POST_FIX_CLEAN_SCAN', patch_at is not None and scan_started is not None
         and scan_started > patch_at and scan_complete
         and scan.get('threats') == [] and scan.get('ignored_threats') == [],
         f"scan_started={scan_started.isoformat() if scan_started else 'UNKNOWN'}; patch={patch_at.isoformat() if patch_at else 'UNKNOWN'}; state={scan.get('state', 'UNKNOWN')}; progress={last_scan.get('progress', 'UNKNOWN')}; error={last_scan.get('error', 'UNKNOWN')}",
         'Require a 100% complete, non-error, idle Jetpack scan started after the patch. A timestamp alone cannot prove completion.')
    return results


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('snapshot', type=Path, help='sanitized local JSON; NO customer/PII data')
    p.add_argument('--json', action='store_true', help='print machine-readable gate report')
    args = p.parse_args(argv)
    try:
        gates = check(json.loads(args.snapshot.read_text(encoding='utf-8')))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({'release_ready': all(g['status'] == 'PASS' for g in gates),
                          'gates': gates}, indent=2))
    else:
        for g in gates:
            print(f"{g['status']:4} {g['gate']}: {g['evidence']}")
    return 0 if all(g['status'] == 'PASS' for g in gates) else 1


if __name__ == '__main__':
    sys.exit(main())
