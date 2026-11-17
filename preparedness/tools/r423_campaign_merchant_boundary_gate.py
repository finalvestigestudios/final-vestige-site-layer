#!/usr/bin/env python3
"""R423 private Preparedness attribution/merchant boundary preflight (ALWAYS HOLD).

Checks presentation-layer campaign URL and alleged merchant endpoints that older
synthetic evidence gates deliberately treated only as structurally valid.
No network, merchant queries, analytics, tracking or release actions. A syntactically
valid Payhip path is NEVER proof of FV ownership, rights, orders or refunds.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, parse_qsl, unquote_to_bytes

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('r422_social_provenance_gate', HERE / 'r422_social_provenance_gate.py')
if SPEC is None or SPEC.loader is None:
    raise RuntimeError('R422 parent unavailable')
r422 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(r422)

CAMPAIGN = re.compile(r'family_pilot_20(?:2[6-9]|3[0-5])_(?:0[1-9]|1[0-2])\Z')
PAYHIP_PRODUCT = re.compile(r'/b/[A-Za-z0-9_-]{4,60}/?\Z')
ALLOWED_QUERIES = {
    'youtube': {'v', 't', 'start', 'si', 'feature'},
    'tiktok': {'lang'},
    'instagram': {'igsh'},
    'facebook': {'v'},
}
BANNED_VALUE_PARTS = ('email', 'phone', 'address', 'session', 'token', 'passwd',
                      'password', 'secret', 'auth', 'cookie', 'client_id', 'user_id',
                      'access_key', 'referrer', 'visitor_id', 'gclid', 'fbclid')


def minimal_query(url, allow):
    """Reject unknown query fields, duplicates, empty values and opaque encodings."""
    if not isinstance(url, str) or not r422.r421.safe_url(url):
        return False
    u = urlsplit(url)
    if not u.query:
        return True
    if len(u.query) > 512 or any(c in u.query for c in ('\\', ';')):
        return False
    try:
        # Reject percent-decoded non-ASCII/control characters in key/value pairs.
        decoded = unquote_to_bytes(u.query)
        if any(c < 33 or c > 126 for c in decoded):
            return False
        pairs = parse_qsl(u.query, keep_blank_values=True,
                          strict_parsing=True, max_num_fields=12)
    except (ValueError, UnicodeError):
        return False
    if not pairs or len(pairs) > 8:
        return False
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)) or not set(keys) <= allow:
        return False
    for k, v in pairs:
        if not k or not v or len(v) > 128 or any(c in v.lower() for c in BANNED_VALUE_PARTS):
            return False
    return True


def publisher_query_ok(platform, url):
    if not r422.platform_post_url_ok(platform, url):
        return False
    if platform not in ALLOWED_QUERIES:
        return False
    if not minimal_query(url, ALLOWED_QUERIES[platform]):
        return False
    u = urlsplit(url)
    pairs = dict(parse_qsl(u.query, keep_blank_values=True, strict_parsing=True))
    if platform == 'youtube':
        if u.path == '/watch' and 'v' not in pairs:
            return False
        if u.path != '/watch' and 'v' in pairs:
            return False
    if platform == 'facebook' and u.path in ('/watch','/watch/') and 'v' not in pairs:
        return False
    return True


def merchant_candidate_ok(offer):
    """Only a constrained review candidate, never an authenticated paid offer."""
    if not isinstance(offer, dict) or offer.get('status') != 'REVIEW_CANDIDATE':
        return False
    checkout, refund = offer.get('merchant_checkout'), offer.get('refund_terms_url')
    if not (r422.r421.safe_url(checkout,host={'payhip.com','www.payhip.com'}) and
            r422.r421.safe_url(refund,host={'payhip.com','www.payhip.com'})):
        return False
    c, r = urlsplit(checkout), urlsplit(refund)
    if c.hostname != r.hostname or c.query or c.fragment or r.query or r.fragment:
        return False
    if not PAYHIP_PRODUCT.fullmatch(c.path):
        return False
    # The refund path is an asserted policy location, not an independently tested one.
    if not r.path.startswith('/') or '..' in r.path or '%' in r.path or '//' in r.path:
        return False
    if any(x in c.path.lower() + r.path.lower() for x in ('water-resilience-field-manual', 'old-water-guide')):
        return False
    return True


def validate(receipt):
    base = r422.validate(receipt)
    errors, holds = set(base['errors']), set(base['holds'])
    if isinstance(receipt, dict):
        camp = receipt.get('campaign')
        if isinstance(camp, dict) and camp.get('status') == 'PROPOSED_MATCH':
            if not isinstance(camp.get('utm_campaign'), str) or not CAMPAIGN.fullmatch(camp['utm_campaign']):
                errors.add('R423_UNBOUNDED_OR_PERSONALIZED_CAMPAIGN_ID')
            if not publisher_query_ok(camp.get('platform'),camp.get('post_url')):
                errors.add('R423_SOCIAL_QUERY_PRIVACY_OR_CONTEXT_DRIFT')
            if not minimal_query(camp.get('mobile_destination'), {'utm_source', 'utm_medium', 'utm_campaign', 'utm_content'}):
                errors.add('R423_MOBILE_QUERY_PRIVACY_OR_AMBIGUITY')
            holds.add('R423_CAMPAIGN_PRESENTATION_IS_NOT_POST_OR_RIGHTS_VERIFICATION')
        offer = receipt.get('paid_offer')
        if isinstance(offer,dict) and offer.get('status') == 'REVIEW_CANDIDATE':
            if not merchant_candidate_ok(offer):
                errors.add('R423_MERCHANT_ENDPOINT_NOT_APPROVED_REVIEW_SHAPE')
            holds.add('R423_PAYHIP_SHAPE_IS_NOT_VERIFIED_SELLER_PRODUCT_OR_SETTLEMENT')
    base['errors'], base['holds'] = sorted(errors),sorted(holds)
    base['structural_integrity_ok'] = not errors
    base.update(release_state='DRAFT_HARD_HOLD',eligible=False,publication_approved=False,
                safety_qd_approved=False,paid_activation_approved=False,
                verified_paid_orders=None,net_revenue_per_1000_qualified_humans=None,
                revenue_status='NOT_COMPUTABLE_OR_INDEPENDENTLY_VERIFIED')
    return base


def main(argv=None):
    parser=argparse.ArgumentParser(description='R423 privacy and merchant boundary: read-only, always HOLD')
    parser.add_argument('receipt',type=Path)
    args=parser.parse_args(argv)
    try:
        if args.receipt.is_symlink(): raise ValueError('symlink')
        data=args.receipt.read_bytes()
        if not 0<len(data)<=r422.r421.MAX_BYTES: raise ValueError('receipt size')
        obj=json.loads(data.decode('utf-8'),object_pairs_hook=r422.r421.unique_pairs)
        result=validate(obj)
    except (ValueError,OSError,UnicodeError,KeyError,TypeError) as exc:
        result=r422.r421.outcome(['R423_READ_FAILED_'+type(exc).__name__],[])
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2


if __name__ == '__main__':
    sys.exit(main())
