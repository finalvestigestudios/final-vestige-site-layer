#!/usr/bin/env python3
"""Apollo R453 untrusted creator URL and commercial-proof boundary.
A syntactically plausible URL cannot establish publication, sales or attribution.
Additive overlay on R452, never amends or approves the commerce gate.
"""
from datetime import date
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import urlsplit, parse_qsl

ROOT = Path(__file__).resolve().parents[2]
R452 = ROOT / 'apollo-r452/qa/funnel_guard.py'
R452_BLOB = '86537e55ebb5b7da546e9361626adcc083d7e60b'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
LANDING = 'https://finalvestige.com/apollo-1-evidence-atlas/'
VIDEO_ID = re.compile(r'^[A-Za-z0-9_-]{11}$', re.ASCII)
TT_ID = re.compile(r'^[0-9]{15,25}$', re.ASCII)
TT_HANDLE = re.compile(r'^@[A-Za-z0-9._]{2,30}$', re.ASCII)
YT_HOSTS = {'www.youtube.com', 'youtube.com', 'm.youtube.com', 'youtu.be'}
TT_HOSTS = {'www.tiktok.com', 'tiktok.com'}

class Hold(ValueError):
    pass

def verified_r452_guard():
    """Read the exact reviewed R452 code; fail if base library is altered."""
    if not R452.is_file() or R452.is_symlink():
        raise Hold('R452 base is missing or symlinked')
    payload=R452.read_bytes()
    digest=hashlib.sha1(f'blob {len(payload)}\0'.encode()+payload).hexdigest()
    if digest != R452_BLOB:
        raise Hold('R452 reviewed Git blob identity mismatch')
    spec=importlib.util.spec_from_file_location('apollo_r452_guard_verified', R452)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def creator_video_url(url, platform):
    """Strict URL shape for specific YouTube/TikTok videos, not creator proof."""
    if not isinstance(url, str) or not isinstance(platform, str) or len(url)>350:
        return False
    if re.search(r'[\x00-\x20\\#]',url):
        return False
    try:
        u=urlsplit(url)
        if u.scheme!='https' or u.username or u.password or u.port or u.fragment or not u.hostname:
            return False
        if u.hostname != u.netloc.lower() or u.hostname.endswith('.'):
            return False
        path=u.path
        if platform == 'youtube' and u.hostname in YT_HOSTS:
            if u.hostname == 'youtu.be':
                return VIDEO_ID.fullmatch(path.lstrip('/')) is not None and path.count('/') == 1 and not u.query
            if path == '/watch':
                pairs=parse_qsl(u.query,keep_blank_values=True,strict_parsing=True)
                return len(pairs)==1 and pairs[0][0]=='v' and VIDEO_ID.fullmatch(pairs[0][1]) is not None
            if path.startswith(('/shorts/','/live/')):
                bits=path.split('/')
                return len(bits)==3 and bits[0]=='' and bits[1] in ('shorts','live') and VIDEO_ID.fullmatch(bits[2]) is not None and not u.query
            return False
        if platform=='tiktok' and u.hostname in TT_HOSTS:
            bits=path.split('/')
            return len(bits)==4 and bits[0]=='' and TT_HANDLE.fullmatch(bits[1]) is not None and bits[2]=='video' and TT_ID.fullmatch(bits[3]) is not None and not u.query
    except (ValueError, TypeError):
        return False
    return False

def assess(doc):
    if not isinstance(doc,dict): raise Hold('JSON object required')
    base=verified_r452_guard()
    try: inherited=base.assess(doc)
    except (base.Hold, ValueError, KeyError, TypeError) as e: raise Hold('R452 proof contract: '+str(e)) from e
    campaign=doc.get('campaign',{})
    platform=campaign.get('utm_source','') if isinstance(campaign,dict) else ''
    url=campaign.get('platform_post_url') if isinstance(campaign,dict) else None
    claimed=campaign.get('publication_proof_status')=='INDEPENDENTLY_CONFIRMED' if isinstance(campaign,dict) else False
    valid=creator_video_url(url,platform)
    if url is not None and not valid:
        raise Hold('creator URL is not a canonical video link for its declared platform')
    if claimed and (not valid or not campaign.get('praxxis_review_ref') or campaign.get('approved_landing_url') != LANDING):
        raise Hold('claimed publication proof lacks exact creator URL + independent review + approved landing')
    offer=doc.get('offer',{})
    if isinstance(offer,dict) and offer.get('checkout_url') is not None:
        # No arbitrary checkout host can be approved by this file. Real merchant trust
        # is an authenticated external business decision, not URL string matching.
        if offer.get('status')=='VERIFIED_PAYABLE' and not offer.get('founder_release_ref'):
            raise Hold('declared payable offer lacks founder release reference')
    if doc.get('commercial_cta_enabled') is not False:
        raise Hold('commercial CTA must remain disabled')
    return {'status':'HARD_HOLD','r452_status':inherited['status'],
        'creator_url_shape':('CANONICAL_SHAPE_ONLY_NOT_PUBLICATION_PROOF' if valid else 'UNVERIFIED'),
        'publication_independently_verified_by_this_tool':False,
        'merchant_approved_by_this_tool':False,'paid_revenue_independently_verified_by_this_tool':False,
        'realized_net_revenue_per_1000_qualified_sessions':None,
        'reviewed_source':'R452 Git blob '+R452_BLOB,
        'single_free_cta':FREE,'approved_landing':LANDING,
        'browser_navigation':'NOT_RUN_OR_REPORTED_SEPARATELY',
        'genuine_axe':'NOT_RUN','production_release':'HARD_HOLD',
        'note':'No unreviewed product, creator publication, NASA media rights or paid sales inferred.'}

def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('input',type=Path)
    p.add_argument('--out',type=Path)
    args=p.parse_args()
    try:
        result=assess(json.loads(args.input.read_text('utf-8')))
        rc=0
    except (ValueError,TypeError,OSError,json.JSONDecodeError) as exc:
        result={'status':'HARD_HOLD','invalid_evidence':str(exc),'realized_net_revenue_per_1000_qualified_sessions':None}
        rc=2
    payload=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.out: args.out.write_text(payload)
    print(payload,end='')
    return rc
if __name__=='__main__':raise SystemExit(main())
