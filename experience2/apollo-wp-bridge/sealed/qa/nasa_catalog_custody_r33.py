#!/usr/bin/env python3
"""Apollo R33: editorial NASA catalog crosswalk and static, no-JS source drawer.

The six NASA URLs were checked manually 2026-10-31; this tool is OFFLINE.
NASA pages may change. This is not image-use licensing or a hosted staging test.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from html import escape
import json
from pathlib import Path
from urllib.parse import urlsplit

# Exact-source custody: source identity and event dates are not mutable via JSON alone.
EXPECTED = (
    ('01', '1967-01', 'https://www.nasa.gov/image-detail/apollo-1-crew-honored/'),
    ('02', '1967-01-03', 'https://www.nasa.gov/image-detail/amf-s67-15717/'),
    ('03', '1966-10-18', 'https://www.nasa.gov/image-detail/amf-s66-58038/'),
    ('04', '2017-01-24', 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/'),
    ('05', '1967-01-28', 'https://www.nasa.gov/image-detail/amf-s67-21294/'),
    ('06', '2017-01-24', 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/'),
)
FIELDS = {'id','catalog','date','date_label','source','credit','kind','finding','limitation','identity_status'}


def require(ok: bool, message: str):
    if not ok: raise ValueError(message)


def validate_registry(reg: dict) -> None:
    require(set(reg) == {'schema','checked_on','source_policy','release_status','records'}, 'unexpected registry fields')
    require(reg['schema']=='fv.apollo.nasa_catalog_source_review.v1', 'schema drift')
    require(reg['checked_on']=='2026-10-31' and reg['release_status']=='HOLD', 'unapproved date/release change')
    require(reg['source_policy']=='https://www.nasa.gov/nasa-brand-center/', 'missing official rights policy')
    records=reg['records']
    require(isinstance(records,list) and len(records)==6, 'six records required')
    for row, (number, date, url) in zip(records, EXPECTED):
        require(isinstance(row,dict) and set(row)==FIELDS, 'unexpected record fields')
        require((row['id'],row['date'],row['source'])==(number,date,url), 'NASA catalog or event date changed')
        parts=urlsplit(row['source'])
        require(parts.scheme=='https' and parts.hostname=='www.nasa.gov' and not parts.query and not parts.fragment, 'non-NASA source')
        for field in FIELDS:
            require(isinstance(row[field],str) and row[field].strip(),f'missing {field}')
        require('HOLD' in row['identity_status'], 'image rights hold removed')
        if number=='01':
            require('S67-19766' in row['identity_status'] and 'unconfirmed' in row['catalog'], 'catalog ambiguity hidden')
        if date.startswith('2017'):
            require('2017' in row['date_label'] and '1967' in row['limitation'], 'retrospective date context missing')
    require(len({x['source'] for x in records})==6, 'duplicate source link')
    forbidden=('latitude','longitude','coordinates','geojson','pin','map_edge')
    require(not any(x in json.dumps(reg).lower() for x in forbidden), 'geospatial claim requires separate admission review')


def verify_casefile(html: str, reg: dict) -> None:
    """Verify compiled sealed PHP response, not a guessed DOM fixture."""
    from bs4 import BeautifulSoup
    doc=BeautifulSoup(html,'html.parser')
    concordance=doc.select('#source-concordance [data-concordance-record]')
    rights=doc.select('#fv-ex2-media-rights [data-media-review]')
    require(len(concordance)==len(rights)==6, 'six aligned concordance and rights records required')
    for row, c, r in zip(reg['records'],concordance,rights):
        ident=row['id'];url=row['source']
        require(c.get('data-concordance-record')==ident and r.get('data-media-review')==ident, 'record order changed')
        c_urls=[a.get('href') for a in c.select('a[href^="https://www.nasa.gov/image-detail/"]')]
        r_urls=[a.get('href') for a in r.select('a[href^="https://www.nasa.gov/image-detail/"]')]
        require(c_urls==r_urls==[url],f'record {ident} NASA identity mismatch')
        require(r.get('data-media-hold')=='true', f'record {ident} reuse hold removed')
        require(row['catalog'].split(' ')[0] in c.get_text(' ',strip=True) or ident=='01',f'record {ident} caption missing catalog ID')
        if row['date'].startswith('2017'):
            require('2017' in c.get_text(' ',strip=True),f'record {ident} misleading pre-fire date')
    require(len(doc.select('[data-crosswalk-review="hold"]'))==1 and 'S67-19766' in html, 'identity crosswalk hold missing')
    require(len(doc.select('#atlas[data-lat], #atlas[data-lon], #atlas [data-lat], #atlas [data-lon]'))==0, 'unreviewed Atlas positions')
    require(not doc.select('img'), 'media links only until individual rights review')


CSS = (Path(__file__).resolve().with_name('nasa_catalog_annex_r33.css').read_text(encoding='utf-8'))


def render(reg: dict) -> str:
    """Accessible, informational-only source drawer. All data escaped. Native details need no JS."""
    validate_registry(reg)
    parts=['<!doctype html><html lang="en"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width,initial-scale=1">',
           '<meta name="robots" content="noindex,nofollow">',
           '<title>Apollo 1 | NASA Source Custody Annex — Private Staging</title>',
           '<style>'+CSS+'</style></head><body>',
           '<a class="skip" href="#main">Skip to source records</a><main id="main">',
           '<p class="kicker">Final Vestige Studios / Research Desk / Private evidence preview</p>',
           '<h1>The source is not the story.</h1>',
           '<p class="lead">Six NASA image catalog pages, six distinct dates or contexts, and six reasons not to overclaim what a photograph proves.</p>',
           '<aside class="warning" role="note"><strong>HOLD — NOT FOR PUBLICATION.</strong> All images remain external links. ' +
           'Individual reuse, third-party rights, identifiable people, credit and non-endorsement require editorial review. ' +
           'The proposed S67-19766 alias is unverified by the directly linked NASA record. No geographic pins or relationships are asserted.</aside>',
           '<section class="records" aria-label="NASA catalog source records">']
    for row in reg['records']:
        e=lambda name:escape(row[name],quote=True)
        parts.append('<article id="catalog-'+e('id')+'"><p class="stamp">NASA source '+e('id')+' · '+e('date_label')+'</p>')
        parts.append('<h2>'+e('catalog')+'</h2><p>'+e('kind')+'</p>')
        parts.append('<p><a href="'+e('source')+'" rel="noopener noreferrer" target="_blank">Open NASA primary catalog record '+e('id')+' (new tab)</a></p>')
        parts.append('<details><summary>What the photograph establishes</summary><p>'+e('finding')+'</p></details>')
        parts.append('<details><summary>What it cannot establish</summary><p>'+e('limitation')+'</p></details>')
        parts.append('<p class="small"><strong>Source credit:</strong> '+e('credit')+'</p>')
        parts.append('<p class="small"><strong>Review status:</strong> '+e('identity_status')+'</p></article>')
    parts.append('</section><footer><p>NASA use policy: <a href="'+escape(reg['source_policy'],quote=True)+'" rel="noopener noreferrer" target="_blank">Read NASA brand and media-use guidance (new tab)</a>.</p>')
    parts.append('<p class="small">Source pages reviewed '+escape(reg['checked_on'])+'. Archival page content may change; this is not a reuse licence, authenticated NASA certification or a production release.</p>')
    parts.append('</footer></main></body></html>')
    return ''.join(parts)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--registry',required=True,type=Path)
    p.add_argument('--casefile',required=True,type=Path)
    p.add_argument('--out',required=True,type=Path)
    p.add_argument('--receipt',required=True,type=Path)
    args=p.parse_args()
    raw=args.registry.read_bytes();reg=json.loads(raw);validate_registry(reg)
    case=args.casefile.read_bytes();verify_casefile(case.decode('utf-8'),reg)
    html=render(reg).encode('utf-8');args.out.write_bytes(html)
    receipt={'status':'STAGING_HOLD','registry_sha256':sha256(raw).hexdigest(),
             'casefile_sha256':sha256(case).hexdigest(),'annex_sha256':sha256(html).hexdigest(),
             'sources':6,'rights_holds':6,'identity_holds':1,'atlas_geo_positions':0,
             'checked_on':reg['checked_on']}
    args.receipt.write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':main()
