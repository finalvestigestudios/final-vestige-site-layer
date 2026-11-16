#!/usr/bin/env python3
"""R409 review-only HTML custody acceptance. Never deploys or writes WordPress.

Static integrity is necessary but not sufficient for published historical accuracy.
Fail closed on missing original PR #158, absent installed-staging receipts, or source drift.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

REPO = 'finalvestigestudios/final-vestige-site-layer'
ARTICLE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
LATER = 'https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/'
EXPECTED_ORIGINAL_BLOB = '403d128c57b9bc82dac7c619651689070edef86c'
EXPECTED_HEADINGS = [
    'Three men. One ground test.', 'An atmosphere built for a different risk.',
    'Fourteen seconds changed the system.', 'The hatch opened inward.',
    'The spark was never conclusively identified.', 'Inward became outward.',
]
EXPECTED_ATLAS_CATEGORIES = ['conditions','conditions','sequence','conditions','investigation','aftermath']
FORBIDDEN = {'script','iframe','form','map','canvas','img','video','audio','object','embed'}

def git_blob(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.errors=[]; self.ids=[]; self.links=[]; self.atlas=[]; self.records=[]
        self.headings=[]; self._capture=[]; self._active_heading=None
        self.elements=[]; self.details=0; self.summaries=0
        self.assets=[]
    def handle_starttag(self, tag, attributes):
        attrs=dict(attributes)
        if len(attrs)!=len(attributes): self.errors.append('duplicate_attribute')
        if tag in FORBIDDEN: self.errors.append('forbidden_element:'+tag)
        if tag=='a': self.links.append(attrs.get('href'))
        if 'id' in attrs: self.ids.append(attrs['id'])
        if tag=='article' and 'data-fvx-record' in attrs: self.records.append(attrs)
        if tag=='li' and 'data-fv-r408-card' in attrs: self.atlas.append(attrs)
        if tag=='details': self.details+=1
        if tag=='summary': self.summaries+=1
        if tag in ('h2','h3'):
            self._capture.append((tag, []))
        for key in ('src','srcset','action','data-lat','data-lng','data-longitude','data-latitude'):
            if key in attrs: self.assets.append((tag,key,attrs[key]))
    def handle_data(self, data):
        if self._capture: self._capture[-1][1].append(data)
    def handle_endtag(self, tag):
        if self._capture and self._capture[-1][0]==tag:
            _,txt=self._capture.pop()
            self.headings.append(' '.join(''.join(txt).split()))

def allowable_link(url: str | None) -> bool:
    if not url or any(c.isspace() or ord(c)<32 for c in url): return False
    if url.startswith('#'):
        return bool(re.fullmatch(r'#[A-Za-z][A-Za-z0-9_-]{0,160}',url))
    u=urlsplit(url)
    if u.scheme!='https' or u.username is not None or u.password is not None or u.port is not None or u.fragment:
        return False
    if url==ARTICLE: return True
    return u.hostname=='www.nasa.gov' and u.netloc=='www.nasa.gov' and u.path.startswith('/')

def check_rendered(html: str, require_atlas: bool=True) -> dict:
    scan=Scan();scan.feed(html);scan.close()
    errors=list(scan.errors)
    if len(scan.ids)!=len(set(scan.ids)): errors.append('duplicate_ids')
    if scan.assets: errors.append('embedded_or_geo_assets')
    if not all(allowable_link(a) for a in scan.links):errors.append('unapproved_link')
    if scan.links.count(ARTICLE)!=1: errors.append('free_article_count')
    if scan.links.count(BOARD)<1 or scan.links.count(LATER)<1: errors.append('missing_source_publication')
    if len(scan.records)!=6: errors.append('record_count')
    if require_atlas:
        if len(scan.atlas)!=6: errors.append('atlas_count')
        if [a.get('data-fv-r408-kind') for a in scan.atlas] != EXPECTED_ATLAS_CATEGORIES:errors.append('atlas_categories')
        if scan.details<12 or scan.summaries<12: errors.append('native_source_disclosures')
    for h in EXPECTED_HEADINGS:
        if h not in scan.headings: errors.append('missing_heading:'+h)
    if 'not conclusively identified' not in html.lower():errors.append('unknown_ignition_disclaimer')
    if 'not evidence identifying the original ignition' not in html.lower():errors.append('later_tests_boundary')
    if scan.links.count(ARTICLE)==1 and any(k in html.lower() for k in ('payhip.com','?affiliate=','data-lat=')):
        errors.append('unexpected_commerce_or_geo')
    anchors=[a[1:] for a in scan.links if a and a.startswith('#')]
    for a in anchors:
        if scan.ids.count(a)!=1:errors.append('broken_anchor:'+a)
    return {'pass':not errors,'errors':sorted(set(errors)),'links':len(scan.links),'source_records':len(scan.records),
            'atlas_cards':len(scan.atlas),'native_details':scan.details,'unique_ids':len(set(scan.ids))}

def check_original(path: Path | None) -> dict:
    if path is None or not path.is_file():
        return {'pass':False,'error':'original_PR158_template_missing','expected_git_blob':EXPECTED_ORIGINAL_BLOB}
    data=path.read_bytes();actual=git_blob(data)
    if actual!=EXPECTED_ORIGINAL_BLOB:
        return {'pass':False,'error':'original_PR158_template_blob_drift','actual_git_blob':actual,'expected_git_blob':EXPECTED_ORIGINAL_BLOB}
    text=data.decode('utf-8');scan=Scan();scan.feed(text)
    headings=[h for h in EXPECTED_HEADINGS if h in scan.headings]
    return {'pass':len(headings)==6 and len(scan.records)==6,'actual_git_blob':actual,
            'headings_matched':headings,'source_record_count':len(scan.records)}

def release_review(rendered: str | None, original: Path | None, *, staging_receipt: Path | None=None,
                   axe_receipt: Path | None=None, cwvs_receipt: Path | None=None, approved: bool=False) -> dict:
    original_result=check_original(original)
    rendered_result=check_rendered(rendered) if rendered is not None else {'pass':False,'errors':['rendered_atlas_missing']}
    blocked=[]
    if not original_result['pass']:blocked.append('authentic_PR158_source_custody')
    if not rendered_result['pass']:blocked.append('rendered_Atlas_Chronology_Desk_contract')
    # Receipt existence is not passing independent acceptance: evidence must be reviewed.
    for key,file in [('installed_HTTPS_staging',staging_receipt),('genuine_axe_core',axe_receipt),('navigated_CWV',cwvs_receipt)]:
        if file is None or not file.is_file():blocked.append(key)
    if not approved:blocked.append('founder_and_independent_QD_approval')
    return {'status':'HOLD' if blocked else 'EVIDENCE_REVIEW_REQUIRED', 'release_authorized':False,
            'original':original_result,'rendered':rendered_result,'blockers':blocked,
            'note':'An available receipt is never proof of its validity. No live release is authorized by this script.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--rendered',type=Path);p.add_argument('--original',type=Path)
    p.add_argument('--staging-receipt',type=Path);p.add_argument('--axe-receipt',type=Path)
    p.add_argument('--cwvs-receipt',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args()
    html=a.rendered.read_text(encoding='utf-8') if a.rendered and a.rendered.is_file() else None
    report=release_review(html,a.original,staging_receipt=a.staging_receipt,axe_receipt=a.axe_receipt,cwvs_receipt=a.cwvs_receipt)
    result=json.dumps(report,sort_keys=True,indent=2)+'\n'
    if a.output: a.output.write_text(result,encoding='utf-8')
    print(result)
    return 0 if report['status']=='EVIDENCE_REVIEW_REQUIRED' else 2
if __name__=='__main__': sys.exit(main())
