#!/usr/bin/env python3
"""Apollo R443: inspect explicit HTML snapshots, never visit/write a live site.

Input must be a saved, provenance-labelled source snapshot. This does NOT assert
that a screenshot/WordPress rendering is an approved staging installation.
"""
import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit

BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
TESTS = 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/'
INVESTIGATION = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
REQUIRED = ('the hatch opened inward', 'no single ignition source', 'most probable',
            'evidence boundary', 'review board')

class Document(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text=[]; self.hrefs=[]; self.ids=[]; self.images=[]
        self.live_scripts=[];self.staging_cards=0;self.staging_educator=0;self.geo_markers=0
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag in ('a','form'):
            self.hrefs.append(d.get('href') or d.get('action') or '')
        if tag == 'img':self.images.append(d)
        if tag == 'script' and d.get('src'):self.live_scripts.append(d['src'])
        if d.get('id'):self.ids.append(d['id'])
        if 'data-r438-card' in d:self.staging_cards+=1
        if 'data-r440-root' in d:self.staging_educator+=1
        if any(x in d for x in ('data-lat', 'data-lng', 'data-longitude', 'data-map-edge')):self.geo_markers+=1
    def handle_data(self, data):
        if data.strip():self.text.append(data)

def audit(html: str, provenance: str) -> dict:
    if provenance not in ('published_wp_read_only', 'approved_staging_snapshot', 'synthetic_test'):
        raise ValueError('source provenance must be explicit')
    d=Document();d.feed(html)
    txt=' '.join(d.text).lower();hrefs=d.hrefs
    unresolved=txt.count('atlas review status: not yet reviewed')
    has_board=any(u.startswith(BOARD) for u in hrefs)
    has_tests=any(u.startswith(TESTS) for u in hrefs)
    free=sum(u.split('?',1)[0].rstrip('/') == INVESTIGATION.rstrip('/') for u in hrefs)
    paid=[u for u in hrefs if any(s in u.lower() for s in ('payhip.com','stripe.com','paypal.com','/checkout','/buy-now'))]
    source_fail=[u for u in hrefs if u.startswith(('http:','https:')) and urlsplit(u).hostname in ('nasa.gov','www.nasa.gov') and not u.startswith('https://')]
    checks={
      'no_unresolved_atlas_review_labels':unresolved==0,
      'nasa_board_source_link':has_board,
      'nasa_followup_research_link':has_tests,
      'full_free_investigation_link':free>=1,
      'no_unauthorized_payment_destinations':not paid,
      'no_http_nasa_link':not source_fail,
      'chronological_claims_and_limits_present':all(x in txt for x in REQUIRED),
      'no_unverified_geo_markers':d.geo_markers==0,
      'unique_dom_ids':len(d.ids)==len(set(d.ids)),
      'image_alt_attribute_present':all('alt' in im for im in d.images),
    }
    # This component suite is not the currently published WordPress page.
    if provenance == 'approved_staging_snapshot':
        checks['five_staging_source_cards']=d.staging_cards>=5
        checks['one_original_educator_preview']=d.staging_educator==1
        checks['exactly_one_stage_investigation_cta']=free==1
    return {'schema':'fv-apollo-r443-source-trust-gate-v1', 'provenance':provenance,
        'sha256':hashlib.sha256(html.encode('utf-8')).hexdigest(),
        'status':'PASS_SOURCE_SNAPSHOT' if all(checks.values()) else 'HOLD_REVIEW',
        'checks':checks,'unresolved_review_labels':unresolved,'free_investigation_links':free,
        'staging_components':{'atlas_cards':d.staging_cards,'educator_preview':d.staging_educator},
        'caveat':'Snapshot-only source/presentation QA. No live browser navigation, axe, LCP, CLS, paid order, or user-session verification.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--html',type=Path,required=True)
    p.add_argument('--provenance',choices=('published_wp_read_only','approved_staging_snapshot','synthetic_test'),required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.html.is_symlink() or not a.html.is_file():p.error('regular local HTML snapshot required')
    raw=a.html.read_text(encoding='utf-8');result=audit(raw,a.provenance)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'failed':[k for k,v in result['checks'].items() if not v]}))
    return 0 if result['status']=='PASS_SOURCE_SNAPSHOT' else 3

if __name__=='__main__':raise SystemExit(main())
