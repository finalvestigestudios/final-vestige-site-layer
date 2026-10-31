#!/usr/bin/env python3
"""Apollo private staging release gate: exact data, provenance and HTML safety.

Read-only validator of generated, Git-pinned PR215 artifacts. Does not contact NASA,
prove image reuse rights, publish content, or replace axe/assistive-tech QA.
"""
from __future__ import annotations
import argparse
import csv
from html.parser import HTMLParser
import hashlib
import io
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

EXPECTED_IDS = [f'{i:02d}' for i in range(1,7)]
DOWNLOADS = ('evidence-export.csv','evidence-export.json','response-export.csv','response-export.json')
EXPECTED_PARTS = ('chronology','research-desk','claim-ledger','comparison-lab','response-audit','documentary-trails','source-gallery','atlas')
FORBIDDEN_HTML = {'script','style','iframe','object','embed','img','svg','math','link','base','meta','video','audio','applet'}
VALID_DOMAINS = {'www.nasa.gov','finalvestige.com'}
PLACEHOLDER = '{{FV_EX2_ASSET_BASE}}/'

class CustodyError(ValueError):
    pass

def require(truth, message):
    if not truth: raise CustodyError(message)

class SafeFragment(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=set(); self.refs=[]; self.external=[]; self.anchor_count=0; self.details=0;self.summary=0
        self.downloads=[]

    def handle_starttag(self, tag, attrs):
        require(tag not in FORBIDDEN_HTML, 'Unapproved active/media HTML element: '+tag)
        a=dict(attrs)
        require(len(a)==len(attrs),'Duplicate attributes: '+tag)
        for name, value in attrs:
            name=name.lower()
            require(not name.startswith('on') and name not in ('srcdoc','formaction','action'), 'Active HTML attribute '+name)
            if value:
                require(not re.search(r'\b(?:javascript|data|vbscript):',value,re.I), 'Forbidden URL scheme in '+name)
                if name in ('src','poster'):
                    raise CustodyError('Remote/subresource loading forbidden in Apollo fragment: '+name)
        if 'id' in a:
            require(a['id'] not in self.ids, 'Duplicate element ID: '+str(a['id']))
            self.ids.add(a['id'])
        for ref in ('for','aria-labelledby','aria-describedby','aria-controls'):
            if a.get(ref):
                self.refs.extend((name,ref) for name in a[ref].split())
        if tag in ('details','summary'):
            require('hidden' not in a and a.get('aria-hidden')!='true',
                    'Native no-JS source disclosure must remain available: '+tag)
        if tag=='a':
            self.anchor_count+=1
            url=a.get('href','')
            require(bool(url),'Anchor without href')
            if url.startswith('#'):
                require(bool(url[1:]),'Empty fragment anchor')
                self.refs.append((url[1:],'href'))
            elif url.startswith(PLACEHOLDER):
                self.downloads.append(url[len(PLACEHOLDER):])
            else:
                u=urlsplit(url)
                require(u.scheme=='https' and u.hostname in VALID_DOMAINS and not u.username and not u.password,
                    'Unapproved outbound domain or scheme: '+url)
                if u.hostname == 'www.nasa.gov' or a.get('target') == '_blank':
                    require(a.get('target')=='_blank' and {'noopener','noreferrer'}<=set(a.get('rel','').split()),
                        'NASA source/new-tab links must be isolated: '+url)
                self.external.append(url)
        elif tag=='details': self.details+=1
        elif tag=='summary': self.summary+=1

    def finish(self):
        missing=sorted({ref for ref,kind in self.refs if ref not in self.ids})
        require(not missing,'Broken internal/accessible ID reference(s): '+','.join(missing[:10]))
        require(self.details==self.summary and self.details>=6,'Source drawers must keep native summary access')
        require(sorted(self.downloads)==sorted(DOWNLOADS),'Four allowlisted export links not present exactly once')
        for anchor in EXPECTED_PARTS:
            require(anchor in self.ids,'Missing evidence experience region: '+anchor)
        return {'dom_ids':len(self.ids),'source_drawers':self.details,'anchors':self.anchor_count,
                'external_source_links':len(self.external),'download_links':self.downloads}


def check_assets(html, css, js):
    require('<main' not in html.lower() and '<body' not in html.lower(), 'Standalone document leaked into fragment')
    p=SafeFragment();p.feed(html);p.close();stats=p.finish()
    for bad in (r'<\s*/\s*style\b', r'@import\b',r'url\s*\(\s*[\'\"]?\s*(?:https?:|//|data:)',r'expression\s*\('):
        require(not re.search(bad,css,re.I),'Unsafe CSS escape/subresource pattern: '+bad)
    for bad in (r'<\s*/\s*script\b',r'\beval\s*\(',r'\bfetch\s*\(',r'\bXMLHttpRequest\b',r'\blocalStorage\b',r'\bsessionStorage\b'):
        require(not re.search(bad,js,re.I),'Unapproved executable or network JS: '+bad)
    return stats


def read_csv(data):
    text=data.decode('utf-8-sig')
    reader=csv.DictReader(io.StringIO(text,newline=''))
    require(reader.fieldnames and len(set(reader.fieldnames))==len(reader.fieldnames),'Duplicate or missing CSV columns')
    rows=list(reader)
    require(all(None not in row and all(v is not None for v in row.values()) for row in rows),'Malformed CSV field count')
    for row in rows:
        for field,value in row.items():
            # Spreadsheet injection needs to be rejected even when CSV values are quoted.
            require(not re.match(r'^\s*[=+@\-\t\r]',value),'Spreadsheet formula-like cell: '+field)
    return rows


def validate_payloads(files):
    evidence=json.loads(files['evidence-export.json'].decode('utf-8'))
    response=json.loads(files['response-export.json'].decode('utf-8'))
    erows=read_csv(files['evidence-export.csv'])
    rrows=read_csv(files['response-export.csv'])
    require(evidence.get('not_a_rights_clearance') is True and evidence.get('no_reproduced_images') is True and
            evidence.get('no_geographic_coordinates') is True,'Evidence dataset must preserve unresolved rights and map precision')
    require(response.get('not_a_completed_remediation_audit') is True and response.get('no_nasa_images') is True and
            response.get('no_geolocations') is True,'Response dataset may not imply completed corrective actions or invented geocodes')
    for key,jsonrows,csvrows in [('evidence',evidence.get('records',[]),erows),('response',response.get('rows',[]),rrows)]:
        require(len(jsonrows)==len(csvrows)==6,key+' row count must be six')
        require(jsonrows==csvrows,key+' CSV/JSON evidence divergence')
        id_field='claim_id' if key=='evidence' else 'id'
        require([row[id_field] for row in jsonrows]==EXPECTED_IDS,key+' record order/identity drift')
        for row in jsonrows:
            require(row.get('geometry') in ('not_assigned','none','unverified'),key+' invented geometry')
            if key=='evidence':
                require(row.get('media_status','').startswith('link_only_'), 'NASA media reused without review')
                require(row.get('image_evidence_limit') and row.get('board_locator'), 'Evidence boundary or Board locator omitted')
                domains={'www.nasa.gov'}
                for f in ('image_record_url','board_report_url','board_findings_url','rights_policy_url'):
                    u=urlsplit(row.get(f,''))
                    require(u.scheme=='https' and u.hostname in domains and not u.username, 'Unapproved source URL: '+f)
            else:
                require(row.get('response_locator') and row.get('board_locator'), 'Response/Board sources uncited')
                for f in ('board_url','response_url'):
                    u=urlsplit(row.get(f,''))
                    require(u.scheme=='https' and u.hostname=='www.nasa.gov','Unapproved response source URL: '+f)
                require(row.get('image_reuse') in ('none','link_only','not_reproduced','no_image','source_links_only'), 'Unexpected media reuse')
    return {'evidence_records':len(erows),'response_records':len(rrows),
            'source_geometry':'unassigned','image_reproduction':'none','csv_json_parity':True}


def check_directory(root:Path):
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    hashes=manifest.get('outputs_sha256',{})
    expected={'fragment.html','apollo.css','apollo.js',*DOWNLOADS}
    require(set(hashes)==expected and manifest.get('source_matches_pr215') is True and
            manifest.get('source_pin_mismatches')==[], 'Source pin and exact seven outputs required')
    files={name:(root/name).read_bytes() for name in expected}
    for name,raw in files.items():
        require(hashlib.sha256(raw).hexdigest()==hashes[name], 'Generated output SHA mismatch: '+name)
    stats=check_assets(files['fragment.html'].decode('utf-8'),
                       files['apollo.css'].decode('utf-8'),files['apollo.js'].decode('utf-8'))
    stats.update(validate_payloads(files))
    return {'status':'PASS','scope':'pinned staging output, not hosted WordPress or rights clearance',
            'pinned_head':manifest['pinned_head'], 'outputs_sha256':hashes, **stats}

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--generated',type=Path,required=True)
    ap.add_argument('--report',type=Path,required=True);args=ap.parse_args()
    report=check_directory(args.generated)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('APOLLO_CUSTODY_PASS',report['evidence_records'],report['response_records'],report['anchors'])
