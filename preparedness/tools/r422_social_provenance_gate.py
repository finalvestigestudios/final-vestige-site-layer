#!/usr/bin/env python3
"""Read-only, fail-closed R422 provenance wrapper for R421 Preparedness funnel receipts.

A plausible public platform URL is NOT proof of a post, its actual contents,
creative rights, approval, delivery, qualified visits, or commercial settlement.
No network, publishing, analytics, commerce, or filesystem writes. Always HOLD.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, urlsplit, unquote

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('r421_funnel_evidence_gate', HERE/'r421_funnel_evidence_gate.py')
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('R421 parent unavailable')
r421 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r421)

STABLE_ID = re.compile(r'[A-Za-z0-9_-]{6,128}\Z')
YT_ID = re.compile(r'[A-Za-z0-9_-]{6,64}\Z')
TIKTOK_USER = re.compile(r'@[A-Za-z0-9._]{2,40}\Z')
TIKTOK_VIDEO = re.compile(r'[0-9]{12,24}\Z')
INSTA_ID = re.compile(r'[A-Za-z0-9_-]{6,40}\Z')
FB_ID = re.compile(r'[0-9]{6,30}\Z')

PLATFORM_HOSTS = {
    'youtube': {'www.youtube.com', 'youtube.com', 'm.youtube.com', 'youtu.be'},
    'tiktok': {'www.tiktok.com', 'tiktok.com', 'm.tiktok.com'},
    'instagram': {'www.instagram.com', 'instagram.com'},
    'facebook': {'www.facebook.com', 'facebook.com', 'm.facebook.com'},
}


def platform_post_url_ok(platform, url):
    """Conservative stable-post shape; intentionally excludes opaque share/redirect URLs."""
    if platform not in PLATFORM_HOSTS or not r421.safe_url(url):
        return False
    u = urlsplit(url)
    if u.hostname not in PLATFORM_HOSTS[platform]:
        return False
    # Percent-encoded slashes, dot navigation, backslashes and double slash paths can
    # disagree with CDN/router interpretation; do not attest an opaque URL as a post.
    if ('%' in u.path or '\\' in u.path or '//' in u.path or
        any(x in ('.', '..') for x in u.path.split('/')) or
        unquote(u.path) != u.path):
        return False
    path = u.path.split('/')[1:]
    if not path or not path[0]:
        return False
    try:
        q = parse_qs(u.query, keep_blank_values=True, strict_parsing=True, max_num_fields=20)
    except ValueError:
        return False
    # No open-redirect or foreign-content exchange arguments; a publisher-side share
    # query may remain present, but it cannot be interpreted as proof of publication.
    bad = {'url', 'u', 'redirect', 'redirect_uri', 'next', 'dest', 'destination',
           'continue', 'return', 'target', 'to', 'app_link'}
    if any(k.lower() in bad for k in q):
        return False
    if platform == 'youtube':
        if u.hostname == 'youtu.be':
            return len(path) == 1 and bool(YT_ID.fullmatch(path[0])) and not q.get('v')
        if path == ['watch']:
            return len(q.get('v', [])) == 1 and bool(YT_ID.fullmatch(q['v'][0]))
        return len(path) == 2 and path[0] in ('shorts','live') and bool(YT_ID.fullmatch(path[1]))
    if platform == 'tiktok':
        return (len(path) == 3 and bool(TIKTOK_USER.fullmatch(path[0])) and
                path[1] == 'video' and bool(TIKTOK_VIDEO.fullmatch(path[2])))
    if platform == 'instagram':
        return len(path) in (2, 3) and path[0] in ('reel','p') and bool(INSTA_ID.fullmatch(path[1])) and (len(path) == 2 or path[2] == '')
    if platform == 'facebook':
        if path in (['watch'], ['watch', '']):
            return len(q.get('v', [])) == 1 and bool(FB_ID.fullmatch(q['v'][0]))
        if len(path) in (2,3) and path[0] == 'reel' and bool(FB_ID.fullmatch(path[1])) and (len(path)==2 or path[2]==''):
            return True
        return (len(path) in (3,4) and path[1]=='videos' and
                bool(FB_ID.fullmatch(path[2])) and (len(path)==3 or path[3]=='') and
                bool(re.fullmatch(r'[A-Za-z0-9._-]{2,80}',path[0])))
    return False


def validate(receipt):
    try:
        result = r421.validate(receipt)
    except (ValueError, AttributeError, TypeError, KeyError, IndexError) as exc:
        result = r421.outcome(['R422_PARENT_RECEIPT_EXCEPTION_'+type(exc).__name__], [])
    errors = set(result['errors'])
    holds = set(result['holds'])
    if isinstance(receipt, dict) and isinstance(receipt.get('campaign'), dict):
        c = receipt['campaign']
        if c.get('status') == 'PROPOSED_MATCH':
            if not platform_post_url_ok(c.get('platform'), c.get('post_url')):
                errors.add('R422_SOCIAL_POST_PLATFORM_OR_PERMALINK_INVALID')
            holds.add('R422_POST_URL_IS_NOT_INDEPENDENT_PUBLICATION_OR_RIGHTS_PROOF')
            holds.add('R422_PUBLISHER_UTM_CANNOT_ESTABLISH_HUMAN_VISITS')
        else:
            holds.add('R422_NO_VERIFIED_MATCHED_POST')
    else:
        errors.add('R422_INVALID_CAMPAIGN_RECORD')
    if isinstance(receipt, dict) and isinstance(receipt.get('paid_offer'), dict):
        if receipt['paid_offer'].get('status') == 'REVIEW_CANDIDATE':
            holds.add('R422_SELF_ATTESTED_SELLER_HASHES_NOT_EXTERNAL_ORDER_PROOF')
    result['errors'] = sorted(errors)
    result['holds'] = sorted(holds)
    result['structural_integrity_ok'] = not errors
    # Explicit safety firewall, independent of any new URL/receipt evidence.
    result.update(release_state='DRAFT_HARD_HOLD',eligible=False,
                  publication_approved=False,safety_qd_approved=False,
                  paid_activation_approved=False,verified_paid_orders=None,
                  net_revenue_per_1000_qualified_humans=None,
                  revenue_status='NOT_COMPUTABLE_OR_INDEPENDENTLY_VERIFIED')
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description='R422 social provenance guard (read-only, always HOLD)')
    p.add_argument('receipt',type=Path)
    args = p.parse_args(argv)
    try:
        if args.receipt.is_symlink(): raise ValueError('symlink not permitted')
        b = args.receipt.read_bytes()
        if not 0 < len(b) <= r421.MAX_BYTES: raise ValueError('invalid receipt size')
        receipt = json.loads(b.decode('utf-8'),object_pairs_hook=r421.unique_pairs)
        outcome = validate(receipt)
    except (OSError,UnicodeError,ValueError,TypeError,KeyError) as exc:
        outcome = r421.outcome(['R422_READ_FAILED_'+type(exc).__name__],[])
    print(json.dumps(outcome,indent=2,sort_keys=True))
    return 2


if __name__ == '__main__':
    sys.exit(main())
