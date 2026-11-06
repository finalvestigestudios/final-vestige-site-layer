#!/usr/bin/env python3
"""R169: read-only, fail-closed Preparedness source-to-offer admission review.

Source custody is structural, not safety or citation adjudication. Submitted
merchant/creator evidence is never independently authenticated by this tool.
No release, sale, lead, tracking, CMS or publisher state can be granted.
"""
from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit, parse_qs

SCHEMA = 'fv-preparedness-r169-offer-source-admission-v1'
HOLD = 'DRAFT_HARD_HOLD'
CTA = 'Make a free household emergency contact and pickup plan.'
GUIDE = 'household-emergency-plan'
TOPIC = 'school-pickup-reunification'
PLATFORMS = {'youtube': {'youtube.com', 'www.youtube.com', 'youtu.be'},
 'tiktok': {'www.tiktok.com', 'tiktok.com'},
 'instagram': {'www.instagram.com', 'instagram.com'},
 'facebook': {'www.facebook.com', 'facebook.com'},
 'pinterest': {'www.pinterest.com', 'pinterest.com'},
 'x': {'x.com', 'www.x.com'},
 'bluesky': {'bsky.app'}}
TOKEN = re.compile(r'[a-z0-9][a-z0-9_-]{2,79}\Z')


def need(test: bool, reason: str) -> None:
    if not test:
        raise ValueError(reason)


def fields(value: object, keys: set[str], label: str) -> dict:
    need(type(value) is dict and set(value) == keys, label + ' keys not canonical')
    return value


def public_url(value: object, hosts: set[str], *, youtube_watch: bool = False) -> str:
    need(type(value) is str and len(value) <= 400, 'invalid evidence URL')
    u = urlsplit(value)
    need(u.scheme == 'https' and u.hostname in hosts and
         not u.username and not u.password and not u.fragment and
         bool(u.path) and '\\' not in value and not any(c.isspace() for c in value),
         'untrusted evidence URL')
    if u.query:
        qs=parse_qs(u.query, strict_parsing=True)
        need(youtube_watch and u.path == '/watch' and set(qs) == {'v'} and
             len(qs['v']) == 1 and bool(TOKEN.fullmatch(qs['v'][0])),
             'unreviewed evidence URL query')
    return value


def evaluate(candidate: dict, metadata: dict, custody: dict, *, synthetic: bool = True) -> dict:
    fields(candidate, {'schema', 'topic', 'guide', 'tool', 'paid_product',
                       'social', 'measurement'}, 'candidate')
    need(candidate['schema'] == SCHEMA and candidate['topic'] == TOPIC,
         'campaign scope changed')
    need(custody.get('state') == HOLD and custody.get('articles') == 35 and
         custody.get('routes') == 35 and custody.get('publication_authorized') is False and
         custody.get('independent_qd_pass') is False,
         'original 35-article custody missing')
    need(metadata.get('slug') == GUIDE and
         metadata.get('status', {}).get('publish') == 'draft' and
         type(metadata.get('source_use')) is dict and bool(metadata['source_use']) and
         metadata.get('section') == 'start-here',
         'original ungated guide identity/source state drift')
    guide = fields(candidate['guide'], {'slug','route','ungated','price_usd','cta'}, 'guide')
    need(guide == {'slug': GUIDE, 'route': '/preparedness/start-here/'+GUIDE+'/',
                   'ungated': True, 'price_usd': 0, 'cta': CTA},
         'free guide CTA/route/ungated status changed')
    card = fields(candidate['tool'], {'name', 'state', 'public_url', 'paid'}, 'tool')
    need(card == {'name':'Family Reunification Card','state':HOLD,
                  'public_url':None,'paid':False},
         'unreviewed printable cannot be a public/paid tool')
    paid = candidate['paid_product']
    if paid is not None:
        paid = fields(paid, {'sku','listing','rights_receipt','delivery_receipt',
                             'refund_receipt','offer_name'}, 'paid offer')
        need(type(paid['sku']) is str and bool(TOKEN.fullmatch(paid['sku'])),
             'invalid SKU receipt')
        need(type(paid['offer_name']) is str and 5 <= len(paid['offer_name']) <= 100 and
             'water resilience' not in paid['offer_name'].lower() and
             'water field manual' not in paid['offer_name'].lower(),
             'retired or invalid offer')
        public_url(paid['listing'], {'payhip.com', 'www.payhip.com'})
        need('/b/' in urlsplit(paid['listing']).path, 'not a Payhip product listing')
        for k in ('rights_receipt', 'delivery_receipt','refund_receipt'):
            need(type(paid[k]) is str and bool(re.fullmatch(r'[a-f0-9]{64}',paid[k])),
                 'missing or malformed evidence digest: '+k)
        # A digest is an inventory pointer, NOT an independent rights audit.
    social = candidate['social']
    if social is not None:
        social = fields(social, {'asset_id','platform','post_url','destination','utms'}, 'social')
        platform = social['platform']
        need(type(platform) is str and platform in PLATFORMS,
             'unapproved social platform')
        need(type(social['asset_id']) is str and TOKEN.fullmatch(social['asset_id']),
             'missing Grok asset ID')
        public_url(social['post_url'], PLATFORMS[platform],youtube_watch=platform=='youtube')
        need(social['destination'] == 'https://finalvestige.com'+guide['route'],
             'unapproved landing destination')
        params = fields(social['utms'], {'utm_source','utm_medium','utm_campaign',
                                        'utm_content'}, 'utm')
        need(params == {'utm_source':platform,'utm_medium':'organic_social',
                        'utm_campaign':'preparedness_pilot_2026_11',
                        'utm_content':social['asset_id']},
             'mismatched campaign attribution')
    measure = fields(candidate['measurement'], {'qualified_human_sessions',
          'confirmed_leads','merchant_confirmed_orders','affiliate_confirmed_sales',
          'realized_net_usd','cohort_7d','cohort_30d'}, 'measurement')
    need(all(x is None for x in measure.values()),
         'unverified counters must not be asserted as conversions')
    return {'schema':SCHEMA,'state':HOLD,'synthetic_fixture':synthetic,
        'original_35_articles_structurally_checked':not synthetic,
        'source_claims_independently_adjudicated':False,
        'source_relationships_recorded_not_adjudicated':len(metadata['source_use']),
        'free_guide':'DRAFT_UNGATED','printable':'DRAFT_PRIVACY_QD_HOLD',
        'merchant_evidence':'SUBMITTED_UNVERIFIED' if paid else 'ABSENT',
        'social_evidence':'SUBMITTED_UNVERIFIED' if social else 'ABSENT',
        'paid_cta_authorized':False,'checkout_verified':False,
        'delivery_verified':False,'independent_qd_pass':False,
        'publication_authorized':False,'attributed_sales_verified':False,
        'realized_net_per_1000_qualified_sessions':None}


def authentic(root: Path, candidate: dict) -> dict:
    sys.path.insert(0,str(root/'preparedness'/'tools'))
    r161 = importlib.import_module('r161_body_custody_gate')
    custody = r161.verify(root)
    # R161 checks the Git identities of all 35 original body/metadata pairs.
    meta_path = root/'preparedness'/'content'/'articles'/f'{GUIDE}.meta.json'
    need(meta_path.is_file() and not meta_path.is_symlink(), 'original guide absent')
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    return evaluate(candidate,meta,custody,synthetic=False)


def main(argv=None) -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',type=Path,default=Path('.'))
    ap.add_argument('--candidate',type=Path,required=True)
    args=ap.parse_args(argv)
    try:
        need(args.candidate.is_file() and not args.candidate.is_symlink(), 'candidate absent')
        candidate=json.loads(args.candidate.read_text(encoding='utf-8'))
        output=authentic(args.repo.resolve(strict=True),candidate)
    except Exception as exc:
        output={'schema':SCHEMA,'state':'INVALID_HARD_HOLD',
                'error_kind':type(exc).__name__,'publication_authorized':False,
                'paid_cta_authorized':False,'independent_qd_pass':False,
                'realized_net_per_1000_qualified_sessions':None}
    print(json.dumps(output,sort_keys=True))
    return 2  # No self-attested release, merchant admission, QD or revenue state.


if __name__=='__main__':
    raise SystemExit(main())
