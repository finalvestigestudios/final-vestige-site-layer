#!/usr/bin/env python3
"""R424: original-source-adjacent social/post identity and 7/30 cohort custody.

READ-ONLY synthetic/reviewer preflight. No remote post lookup, seller authentication,
source-to-claim adjudication or safety/QD approval is performed. ALWAYS HARD HOLD.
Parent: R423; never replaces R409-R420 manuscript/citation safety checks.
"""
from __future__ import annotations

import argparse
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import re
import stat
import sys
from urllib.parse import parse_qs, urlsplit

HERE = Path(__file__).resolve().parent
SPEC = spec_from_file_location('r423_campaign_merchant_boundary_gate', HERE / 'r423_campaign_merchant_boundary_gate.py')
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('R423 predecessor unavailable')
r423 = module_from_spec(SPEC)
SPEC.loader.exec_module(r423)

YT_EXACT = re.compile(r'[A-Za-z0-9_-]{11}\Z')
PUBLISHER_IDS = {
    'tiktok': re.compile(r'[0-9]{12,24}\Z'),
    'instagram': re.compile(r'[A-Za-z0-9_-]{6,40}\Z'),
    'facebook': re.compile(r'[0-9]{6,30}\Z'),
}
MEASURES = ('qualified_human_sessions', 'verified_paid_orders', 'gross_cents',
            'refund_cents', 'fees_cents')


def publication_id(platform, url):
    """Derive a candidate publisher post ID; never assert post existence/rights.

    A Grok asset_id is an independent creator identifier, NOT necessarily the
    native publisher ID. Return both in a binding receipt rather than falsely
    requiring equality or treating either as external authentication.
    """
    if not r423.publisher_query_ok(platform, url):
        return None
    u = urlsplit(url)
    parts = [p for p in u.path.split('/') if p]
    q = parse_qs(u.query, keep_blank_values=True, strict_parsing=True)
    identifier = None
    if platform == 'youtube':
        if u.hostname == 'youtu.be' and len(parts) == 1:
            identifier = parts[0]
        elif parts == ['watch']:
            identifier = q.get('v', [None])[0]
        elif len(parts) == 2 and parts[0] in ('shorts', 'live'):
            identifier = parts[1]
        if not isinstance(identifier, str) or not YT_EXACT.fullmatch(identifier):
            return None
    elif platform == 'tiktok' and len(parts) == 3 and parts[1] == 'video':
        identifier = parts[2]
    elif platform == 'instagram' and len(parts) == 2 and parts[0] in ('reel', 'p'):
        identifier = parts[1]
    elif platform == 'facebook':
        if parts == ['watch']:
            identifier = q.get('v', [None])[0]
        elif len(parts) >= 2 and parts[0] == 'reel':
            identifier = parts[1]
        elif len(parts) == 3 and parts[1] == 'videos':
            identifier = parts[2]
    if platform != 'youtube':
        pattern = PUBLISHER_IDS.get(platform)
        if not isinstance(identifier, str) or pattern is None or not pattern.fullmatch(identifier):
            return None
    return identifier


def binding_digest(campaign, publisher_id):
    """Deterministic intent crosswalk, explicitly not publication or rights proof."""
    fields = [campaign['topic'], campaign['platform'], publisher_id,
              campaign['asset_id'], campaign['mobile_destination'],
              campaign['utm_campaign'], campaign['utm_content']]
    if not all(isinstance(s, str) for s in fields):
        return None
    raw = json.dumps(fields, ensure_ascii=True, separators=(',', ':')).encode('ascii')
    return hashlib.sha256(b'FV-PREP-R424-PROPOSED-CROSSWALK\0' + raw).hexdigest()


def validate(receipt):
    """Never elevate a syntactically plausible receipt into a commercial claim."""
    try:
        parent = r423.validate(receipt)
    except (ValueError, KeyError, IndexError, TypeError, AttributeError, OverflowError) as exc:
        parent = r423.r422.r421.outcome(['R424_PARENT_EXCEPTION_' + type(exc).__name__], [])
    errors = set(parent['errors'])
    holds = set(parent['holds'])
    candidate = None
    if isinstance(receipt, dict):
        camp = receipt.get('campaign')
        if isinstance(camp, dict) and camp.get('status') == 'PROPOSED_MATCH':
            platform = camp.get('platform')
            post_id = publication_id(platform, camp.get('post_url'))
            if not post_id:
                errors.add('R424_PUBLISHER_POST_ID_INVALID_OR_UNEXTRACTABLE')
            elif not r423.r422.r421.TOKEN.fullmatch(camp.get('asset_id', '') if isinstance(camp.get('asset_id'), str) else ''):
                errors.add('R424_CREATOR_ASSET_ID_INVALID')
            else:
                digest = binding_digest(camp, post_id)
                if digest is None:
                    errors.add('R424_CAMPAIGN_BINDING_FIELDS_INVALID')
                else:
                    candidate = {
                        'platform': platform,
                        'publisher_post_id': post_id,
                        'creator_asset_id': camp['asset_id'],
                        'candidate_binding_sha256': digest,
                        'authentication': 'UNVERIFIED_REVIEW_ONLY',
                    }
            holds.add('R424_CREATOR_PUBLISHER_ID_BINDING_NOT_INDEPENDENTLY_ATTESTED')
            holds.add('R424_FREE_GUIDE_OFFICIAL_LINKS_NOT_SOURCE_ADJUDICATED')
        cohorts = receipt.get('cohorts')
        if isinstance(cohorts, list):
            indexed = {}
            for c in cohorts:
                if isinstance(c, dict) and type(c.get('days')) is int and c['days'] in (7, 30):
                    indexed.setdefault(c['days'], c)
            if cohorts:
                holds.add('R424_UNDATED_COHORT_WINDOWS_AND_MERCHANT_SETTLEMENT_UNVERIFIED')
            if 7 in indexed and 30 in indexed:
                # Even an arithmetically consistent record lacks a common end-date
                # field and independent cohort/merchant authentication. HOLD remains.
                a, b = indexed[7], indexed[30]
                for field in MEASURES:
                    x, y = a.get(field), b.get(field)
                    if type(x) is int and type(y) is int and x >= 0 and y >= 0 and x > y:
                        errors.add('R424_NESTED_7D_EXCEEDS_30D_' + field.upper())
                if a.get('merchant_receipt_sha256') == b.get('merchant_receipt_sha256'):
                    holds.add('R424_IDENTICAL_AGGREGATE_HASHES_REQUIRE_INDEPENDENT_REVIEW')
    parent.update(errors=sorted(errors), holds=sorted(holds),
                  structural_integrity_ok=not errors,
                  proposed_post_binding=candidate,
                  release_state='DRAFT_HARD_HOLD', eligible=False,
                  publication_approved=False, safety_qd_approved=False,
                  paid_activation_approved=False, verified_paid_orders=None,
                  net_revenue_per_1000_qualified_humans=None,
                  revenue_status='NOT_COMPUTABLE_OR_INDEPENDENTLY_VERIFIED')
    return parent


def bounded_receipt(path):
    """Single-link, no-follow, bounded read; reject non-standard JSON literals."""
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or not 0 < before.st_size <= r423.r422.r421.MAX_BYTES:
        raise ValueError('unsafe receipt type, link count or size')
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0))
    with os.fdopen(fd, 'rb') as f:
        opened = os.fstat(f.fileno())
        if not stat.S_ISREG(opened.st_mode) or opened.st_nlink != 1:
            raise ValueError('unsafe opened receipt')
        data = f.read(r423.r422.r421.MAX_BYTES + 1)
    if len(data) > r423.r422.r421.MAX_BYTES or (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns):
        raise ValueError('receipt changed during guarded read')
    def reject_constant(v):
        raise ValueError('nonstandard JSON number ' + v)
    return json.loads(data.decode('utf-8'), object_pairs_hook=r423.r422.r421.unique_pairs,
                      parse_constant=reject_constant)


def main(argv=None):
    parser = argparse.ArgumentParser(description='R424 offline post/cohort crosswalk; ALWAYS HARD HOLD')
    parser.add_argument('receipt', type=Path)
    args = parser.parse_args(argv)
    try:
        result = validate(bounded_receipt(args.receipt))
    except (OSError, ValueError, UnicodeError, TypeError, KeyError) as exc:
        result = r423.r422.r421.outcome(['R424_READ_FAILED_' + type(exc).__name__], [])
        result['proposed_post_binding'] = None
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2


if __name__ == '__main__':
    sys.exit(main())
