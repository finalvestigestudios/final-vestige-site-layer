"""Dispatch R172. Offline, replay-safe candidate enrollment audit; NEVER a source of live signups.

The provider's native per-subscriber status report, not a browser URL or UI message,
remains the authority. This tool only deduplicates *reviewed* redacted change records.
Any PII must be rejected; local checkpoints must never be committed to GitHub.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

HOLD = 'HOLD_UNSENT'
EMAIL = re.compile(r'(?i)[\w.+-]+@[\w.-]+\.[a-z]{2,}')
OPAQUE = re.compile(r'^evt_[A-Za-z0-9_-]{16,80}$')
PROOF = re.compile(r'^proof:[A-Za-z0-9._-]{8,120}$')
ALLOWED_BEFORE = {'Not confirmed', 'Not subscribed'}
RESUMED_BEFORE = {'Emails paused', 'Not sending'}
SALT = 'FV_DISPATCH_R172_EVENT_ID_V1'


def _no_pii(obj):
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=True)
    if EMAIL.search(raw) or re.search(r'(?i)"(?:email|name|subscriber_id|phone|ip|address|token)"\s*:', raw):
        raise ValueError('PII/identity fields are forbidden; use synthetic IDs only')
    if len(raw) > 200_000:
        raise ValueError('Oversized payload')


def reconcile(batch, checkpoint=None):
    """Dry-run classified candidate count and a NEW checkpoint; caller controls writes.

    This cannot prove the attestation itself; independently verify proof_ref in WordPress
    provider interface before calling. Checkpoint stores hashes of synthetic/provider
    event tokens, not subscriber addresses; it is still restricted internal data.
    """
    _no_pii(batch)
    checkpoint = checkpoint if checkpoint is not None else {'version': 1, 'seen': []}
    _no_pii(checkpoint)
    if not isinstance(batch, dict) or batch.get('source') != 'Jetpack Subscriber Email subscription column':
        raise ValueError('Source must be authoritative provider status column')
    if batch.get('observation') != 'read_only_provider_status_change' or batch.get('environment') != 'manually_attested':
        raise ValueError('No page-click or browser-only evidence accepted')
    if not isinstance(batch.get('records'), list):
        raise ValueError('Records must be list')
    if checkpoint.get('version') != 1 or not isinstance(checkpoint.get('seen'), list):
        raise ValueError('Invalid checkpoint')
    old = checkpoint['seen']
    if len(set(old)) != len(old) or any(not re.fullmatch('[a-f0-9]{64}', x) for x in old):
        raise ValueError('Checkpoint corrupted')
    seen = set(old)
    newly_attested = 0
    duplicates = 0
    rejected = 0
    reactivated = 0
    for r in batch['records']:
        if not isinstance(r, dict) or set(r) != {'event_key', 'before', 'after', 'proof_ref', 'observed_via'}:
            raise ValueError('Unrecognized record fields')
        if not OPAQUE.fullmatch(r['event_key']) or not PROOF.fullmatch(r['proof_ref']):
            raise ValueError('Invalid opaque event key or proof pointer')
        if r['observed_via'] != 'provider_status_change' or r['before'] not in (ALLOWED_BEFORE | RESUMED_BEFORE) or r['after'] != 'Subscribed':
            rejected += 1
            continue
        digest = hashlib.sha256((SALT + ':' + r['event_key']).encode()).hexdigest()
        if digest in seen:
            duplicates += 1
        else:
            seen.add(digest)
            if r['before'] in RESUMED_BEFORE:
                reactivated += 1  # resuming email delivery != new signup
            else:
                newly_attested += 1
    result = {
        'type': 'candidate_signup_checkpoint', 'release': HOLD,
        'reviewed_new_provider_transitions': newly_attested,
        'duplicate_events_suppressed': duplicates,
        'previous_subscribers_resuming_email': reactivated,
        'other_events_excluded': rejected,
        'measured_site_signups': None, # not inferred from offline evidence
        'provider_eligible_email_recipients': None, # requires a separate live status export
        'customer_orders': None, 'net_revenue': None,
        'evidence_level': 'OFFLINE_ATTESTATION_CONSISTENCY_ONLY',
        'notes': 'No real recipient list, emails, metrics, or sending rights are accessed.'}
    return result, {'version': 1, 'seen': sorted(seen)}


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input_json', type=Path)
    p.add_argument('prior_checkpoint_json', type=Path)
    p.add_argument('output_report_json', type=Path)
    p.add_argument('output_checkpoint_json', type=Path)
    a = p.parse_args()
    batch = json.loads(a.input_json.read_text())
    prior = json.loads(a.prior_checkpoint_json.read_text()) if a.prior_checkpoint_json.exists() else None
    report, next_state = reconcile(batch, prior)
    a.output_report_json.write_text(json.dumps(report, indent=2) + '\n')
    a.output_checkpoint_json.write_text(json.dumps(next_state, indent=2) + '\n')
    print('HOLD_UNSENT: offline evidence consistency only, no audience contact')

if __name__ == '__main__':
    main()
