#!/usr/bin/env python3
"""Fail-closed *read-only* R38 Research Desk ↔ R47 Atlas source-custody parity.

Invoke with --ledger pointing at the independently checked-out Research Desk
`templates/ledger.html`. This does not modify either component and makes no
claim that the two plugins were installed into WordPress or share a UX.
"""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import build_atlas

class ResearchDeskReader(HTMLParser):
    def __init__(self):
        super().__init__();self.current=None;self.records={};self.recordid=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='article' and 'data-fvx-record' in a:
            if self.current is not None:raise ValueError('Nested source plates')
            ident=a.get('id','').removeprefix('fv-ex2-ledger-apollo1-record-')
            if ident not in build_atlas.IDS or ident in self.records:raise ValueError('Unexpected Research Desk record')
            self.current=ident;self.records[ident]={'catalog':'','hrefs':[],'photo_id':None}
        if self.current and tag=='div' and 'fv-ex2-ledger__recordid' in a.get('class','').split():
            self.recordid=True
        if self.current and tag=='details' and 'data-fvx-photo-record' in a:
            v=a['data-fvx-photo-record']
            if self.records[self.current]['photo_id'] is not None:raise ValueError('Repeated photo custody')
            self.records[self.current]['photo_id']=v
        if self.current and tag=='a' and a.get('href','').startswith('https://www.nasa.gov/image-detail/'):
            self.records[self.current]['hrefs'].append(a['href'])
    def handle_data(self,data):
        if self.current and self.recordid:self.records[self.current]['catalog']+=data
    def handle_endtag(self,tag):
        if tag=='div' and self.recordid:self.recordid=False
        if tag=='article' and self.current:self.current=None


def verify_ledger(html:str)->dict:
    ledger=ResearchDeskReader();ledger.feed(html)
    custody=build_atlas.validate_custody()
    if set(ledger.records)!=set(build_atlas.IDS):raise ValueError('Six complete Research Desk records required')
    results=[]
    for r in custody['records']:
        card=ledger.records[r['id']]
        if card['photo_id']!=r['id'] or card['hrefs']!=[r['photo_url']]:
            raise ValueError('Research Desk photo custody/link mismatch: '+r['id'])
        if r['catalog'] not in card['catalog']:
            raise ValueError('Research Desk catalog mismatch: '+r['id'])
        results.append({'id':r['id'],'catalog':r['catalog'],'photo_url':r['photo_url'],
                        'media_rights':'INDIVIDUAL_REVIEW_REQUIRED'})
    return {'schema':'fv.ex2.apollo.r47.readonly-concordance.v1',
            'research_desk_records':len(results),'atlas_records':len(custody['records']),
            'identity_and_photo_url_parity':'PASS',
            'historical_claim_parity':'NOT_ASSESSED',
            'image_rights':'UNREVIEWED','wordpress_integration':'NOT_TESTED',
            'records':results}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ledger',type=Path,required=True)
    args=p.parse_args()
    if not args.ledger.is_file():raise SystemExit('HOLD: supply the exact checked-out Research Desk ledger.html')
    print(json.dumps(verify_ledger(args.ledger.read_text(encoding='utf-8')),indent=2,sort_keys=True))
