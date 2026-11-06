#!/usr/bin/env python3
"""Draft-only Preparedness source -> social -> offer admission. Never activates a funnel.

The authentic mode invokes R156's frozen source chain, checks local draft bodies
and metadata, and reads *only* a proposed JSON contract. A valid contract does
not grant source, safety, QD, marketing, commerce, or publication approval.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, parse_qsl

SOURCE_GATE = 'preparedness/tools/r156_family_review_workorders.py'
SOURCE_BLOB = '050bbf14761c12a666250a4da633c19b979f3c81'
SCHEMA = 'fv-preparedness-r157-draft-funnel-contract-v1'
GUIDE = 'household-emergency-plan'
CARD = 'family-reunification-card'
EXPECTED = {'guide': '/preparedness/start-here/household-emergency-plan/',
            'card': '/preparedness/field-tools/family-reunification-card/'}
PLATFORMS = {'youtube', 'tiktok', 'instagram', 'facebook', 'pinterest', 'x', 'bluesky'}
ALLOWED_CTA = {'caption', 'pinned_sources_comment', 'profile_bio'}
ASSET_ID = re.compile(r'^[a-zA-Z0-9][a-zA-Z0-9_-]{5,79}$')


def need(test, why):
    if not test:
        raise ValueError(why)


def blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def safe_url(url, *, expected=None):
    need(isinstance(url, str), 'non-string or absent URL')
    p = urlsplit(url)
    need(p.scheme == 'https' and p.netloc == 'finalvestige.com' and not p.username
         and not p.password and not p.fragment and not p.query
         and '\\' not in url and '%' not in p.path and '//' not in p.path
         and p.path.startswith('/preparedness/'), 'unsafe/noncanonical FV destination')
    if expected:
        need(p.path == expected, 'destination differs from exact verified guide/card path')
    return p.path


def proposed_contract():
    """Only unknown values: no invented Grok media IDs, merchant SKUs or orders."""
    return {'schema': SCHEMA, 'topic': 'school-pickup-and-family-reunification',
        'audience': 'households-with-school-age-children',
        'guide_url': 'https://finalvestige.com' + EXPECTED['guide'],
        'card_url': 'https://finalvestige.com' + EXPECTED['card'],
        'guide_requires_signup': False, 'guide_requires_payment': False,
        'card_label': 'Optional free printable — not reviewed for publication',
        'social': {'platform': None, 'asset_id': None, 'published_post_url': None,
                   'cta_placement': None, 'utm_campaign': None},
        'merchant': {'sku': None, 'checkout_url': None, 'rights_verified': False,
                     'listing_live_verified': False, 'delivery_verified': False,
                     'refund_terms_verified': False, 'paid_cta_enabled': False},
        'evidence': {'source_review_approved': False, 'independent_qd_pass': False,
                     'browser_privacy_print_pass': False, 'founder_release_approved': False},
        'metrics': {'qualified_human_sessions': None, 'verified_paid_orders': None,
                    'gross': None, 'fees': None, 'refunds': None,
                    'realized_net_revenue_per_1000': None}}


def admission(contract, *, source_report=None, guide_meta=None, card_meta=None):
    """Immutable admission assessment. Nulls mean unknown, not zero."""
    need(type(contract) is dict and contract.get('schema') == SCHEMA, 'contract schema mismatch')
    need(contract.get('topic') == 'school-pickup-and-family-reunification'
         and contract.get('audience') == 'households-with-school-age-children', 'intent/audience drift')
    safe_url(contract.get('guide_url'), expected=EXPECTED['guide'])
    safe_url(contract.get('card_url'), expected=EXPECTED['card'])
    need(contract.get('guide_requires_signup') is False
         and contract.get('guide_requires_payment') is False, 'essential guidance must remain ungated')
    need(contract.get('card_label') == 'Optional free printable — not reviewed for publication',
         'unreviewed printable must not be advertised as approved')
    social, merchant, evidence, metrics = (contract.get(x) for x in ('social','merchant','evidence','metrics'))
    need(all(type(x) is dict for x in (social, merchant, evidence, metrics)), 'missing contract sections')
    need(set(social) == {'platform','asset_id','published_post_url','cta_placement','utm_campaign'},
         'unrecognized social measurement contract')
    known = [social[k] is not None for k in ('platform','asset_id','published_post_url','cta_placement','utm_campaign')]
    if any(known):
        need(all(known), 'partial/unverified creator asset cannot be marked attributed')
        need(social['platform'] in PLATFORMS and type(social['asset_id']) is str
             and ASSET_ID.fullmatch(social['asset_id']) is not None
             and social['cta_placement'] in ALLOWED_CTA, 'invalid or prohibited creator attribution')
        p = urlsplit(social['published_post_url'])
        need(p.scheme == 'https' and p.netloc and p.hostname != 'finalvestige.com'
             and not p.username and not p.password, 'unverified social post URL')
        need(social['utm_campaign'] == 'preparedness_pilot_2026_11', 'unexpected campaign')
    need(set(merchant) == {'sku','checkout_url','rights_verified','listing_live_verified',
                           'delivery_verified','refund_terms_verified','paid_cta_enabled'}, 'merchant contract drift')
    need(merchant['paid_cta_enabled'] is False, 'no paid CTA allowed in draft gate')
    for key in ('rights_verified','listing_live_verified','delivery_verified','refund_terms_verified'):
        need(merchant[key] is False, 'unverified merchant approval asserted: '+key)
    need(merchant['sku'] is None and merchant['checkout_url'] is None,
         'do not introduce speculative SKU or checkout link')
    need(set(evidence) == {'source_review_approved','independent_qd_pass',
                            'browser_privacy_print_pass','founder_release_approved'}
         and all(v is False for v in evidence.values()), 'fabricated review or founder release approval')
    need(set(metrics) == {'qualified_human_sessions','verified_paid_orders','gross','fees',
                          'refunds','realized_net_revenue_per_1000'}
         and all(v is None for v in metrics.values()), 'unverified commercial measurement asserted')
    if source_report is not None:
        need(type(source_report) is dict and source_report.get('status') == 'DRAFT_HARD_HOLD'
             and source_report.get('family_source_relationships') == 11
             and source_report.get('family_citation_occurrences') == 16
             and source_report.get('other_review_tasks_still_pending') == 64
             and source_report.get('critical_source_scope') == 2
             and source_report.get('blocked_retrieval_not_link_death') == 6
             and source_report.get('source_safety_qd_approved') is False
             and source_report.get('public_release_allowed') is False
             and len(source_report.get('workorders', [])) == 11,
             'R156 source review chain not in the expected hard-hold condition')
    for slug, meta in ((GUIDE,guide_meta),(CARD,card_meta)):
        if meta is not None:
            need(type(meta) is dict and meta.get('slug') == slug
                 and meta.get('status',{}).get('publish') != 'published'
                 and meta.get('status',{}).get('publish') == 'draft',
                 'source article/tool metadata changed or was published: '+slug)
    return {'schema':SCHEMA,'status':'DRAFT_HARD_HOLD',
        'source_review_required':True,'independent_qd_required':True,
        'creator_asset_observed':all(known),'paid_offer_authenticated':False,
        'free_guide_restricted':False,'free_card_only_if_qualified_review':True,
        'public_release_allowed':False,'marketing_allowed':False,
        'confirmed_sales':None,'net_revenue_per_1000_qualified_sessions':None,
        'blocking_steps':['independent source/safety and QD review',
                          'draft-only browser/mobile/print and privacy QA',
                          'Grok/Praxxis published media ID and destination confirmation',
                          'existing rights-cleared purchasable SKU with merchant proof',
                          'merchant-confirmed orders, fees, refunds, qualified session cohort',
                          'founder-specific production and posting approvals']}


def authentic(root, contract):
    root = root.resolve(strict=True)
    f = root / SOURCE_GATE
    need(f.is_file() and not f.is_symlink() and blob(f.read_bytes()) == SOURCE_BLOB,
         'R156 frozen source gate unavailable or drifted')
    spec = importlib.util.spec_from_file_location('r156_pinned_r157', f)
    need(spec is not None and spec.loader is not None, 'R156 frozen source gate unloadable')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    report = mod.authentic_reconcile(root)
    g = root / 'preparedness/content/articles/household-emergency-plan.meta.json'
    c = root / 'preparedness/content/tools/family-reunification-card.meta.json'
    for file in (g,c):
        need(file.is_file() and not file.is_symlink(), 'missing article/tool metadata')
        need(file.with_name(file.name.replace('.meta.json','.body.html')).is_file(),
             'missing authentic reading body')
    return admission(contract, source_report=report,
                     guide_meta=json.loads(g.read_text(encoding='utf-8')),
                     card_meta=json.loads(c.read_text(encoding='utf-8')))


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path('.'))
    parser.add_argument('--manifest',type=Path,help='Read-only proposed JSON; omission uses explicitly unknown proposal')
    args=parser.parse_args(argv)
    try:
        contract=json.loads(args.manifest.read_text(encoding='utf-8')) if args.manifest else proposed_contract()
        print(json.dumps(authentic(args.repo,contract),sort_keys=True))
    except (OSError,TypeError,KeyError,ValueError,json.JSONDecodeError) as e:
        print(json.dumps({'status':'INVALID_HARD_HOLD','error':str(e),'public_release_allowed':False}))
    return 2  # Never success-as-release; source/safety gate remains closed.


if __name__=='__main__':
    raise SystemExit(main())
