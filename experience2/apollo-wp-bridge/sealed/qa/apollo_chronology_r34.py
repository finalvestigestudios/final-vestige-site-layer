#!/usr/bin/env python3
"""Apollo R34 source-photo chronology; not Apollo 204 telemetry. Staging HOLD."""
import argparse
import hashlib
import json
from pathlib import Path
from bs4 import BeautifulSoup
from nasa_catalog_custody_r33 import render as r33_render,validate_registry

COUNTS={'1966':1,'1967':3,'2017':2}
PERIOD_COUNTS=COUNTS
PANEL='''<section class="r34-chronology" aria-labelledby="r34-title">
<p class="r34-eyebrow">Photographic source chronology · Not an accident reconstruction</p>
<h2 id="r34-title">When the surviving photographs were made</h2>
<p>These dates describe the <strong>photograph or retrospective exhibit</strong>, not the time of the Apollo 1 fire. The crew image is dated only to <strong>January 1967</strong>; its day and its proposed S67-19766 alias remain unverified. The two 2017 photographs document later memorial displays, not the 1967 accident scene.</p>
<ol class="r34-period-index" aria-label="Documented photograph dates">
<li><strong>1966</strong> — 1 training photograph</li><li><strong>1967</strong> — 3 context, preparation, or post-fire photographs (not all day-resolved)</li><li><strong>2017</strong> — 2 memorial photographs</li></ol>
<div class="r34-controls" data-r34-controls hidden aria-label="Filter NASA photographs by documented year">
<p class="r34-label">Show photographic records</p><div class="r34-filters" role="group" aria-label="Documented image year">
<button type="button" data-r34-year="all" aria-pressed="true" aria-controls="apollo-r34-records">All six</button>
<button type="button" data-r34-year="1966" aria-pressed="false" aria-controls="apollo-r34-records">1966 · 1</button>
<button type="button" data-r34-year="1967" aria-pressed="false" aria-controls="apollo-r34-records">1967 · 3</button>
<button type="button" data-r34-year="2017" aria-pressed="false" aria-controls="apollo-r34-records">2017 · 2</button></div>
<p class="r34-status" role="status" aria-live="polite" aria-atomic="true" data-r34-status>Showing all 6 NASA photographic source records.</p></div>
<p class="r34-caveat"><strong>Evidence boundary:</strong> These images provide historical context. The Apollo 204 Review Board's instrument chronology is a separate primary source. This grouping does not interpolate readings or establish an ignition cause.</p></section>'''

def verify(html,reg):
    validate_registry(reg);s=BeautifulSoup(html,'html.parser')
    cards=s.select('#apollo-r34-records>article[data-source-period]')
    if len(cards)!=6 or len(s.select('a[href^="https://www.nasa.gov/image-detail/"]'))!=6: raise ValueError('missing original source records')
    if s.select('img,iframe,script[src],[data-lat],[data-lon],[data-map-edge]'):raise ValueError('unapproved media, code or geo')
    if len(s.select('script[data-r34-enhancement]'))!=1:raise ValueError('missing enhancement script')
    if [b.get('data-r34-year') for b in s.select('[data-r34-controls] button')]!=['all','1966','1967','2017']:raise ValueError('changed period controls')
    if 'hidden' not in s.select_one('[data-r34-controls]').attrs:raise ValueError('no-JS controls visible')
    ids=[x['id'] for x in s.select('[id]')]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate IDs')
    for row,card in zip(reg['records'],cards):
        if (card['id'],card['data-source-period'],card['data-photo-date'],card['data-date-precision'])!=('catalog-'+row['id'],row['date'][:4],row['date'],'month' if len(row['date'])==7 else 'day'):raise ValueError('date/precision invented')
        if card.select_one('a[href^="https://www.nasa.gov/image-detail/"]')['href']!=row['source'] or 'HOLD' not in card.get_text(' ',strip=True):raise ValueError('source or rights drift')

def build(reg,css,js):
    validate_registry(reg)
    if '</style' in css.lower() or '</script' in js.lower():raise ValueError('unsafe inline delimiter')
    soup=BeautifulSoup(r33_render(reg),'html.parser')
    cards=soup.select('section.records>article')
    if len(cards)!=6:raise ValueError('incomplete R33 card source')
    for card,row in zip(cards,reg['records']):
        if card.get('id')!='catalog-'+row['id'] or card.get('data-source-period'):raise ValueError('unexpected source card')
        card['data-source-period']=row['date'][:4];card['data-photo-date']=row['date']
        card['data-date-precision']='month' if len(row['date'])==7 else 'day'
    if {y:sum(c['data-source-period']==y for c in cards) for y in COUNTS}!=COUNTS:raise ValueError('photo period drift')
    section=soup.select_one('section.records');section['id']='apollo-r34-records'
    section.insert_before(BeautifulSoup(PANEL,'html.parser').section)
    style=soup.new_tag('style',attrs={'data-r34-style':''});style.string=css;soup.head.append(style)
    script=soup.new_tag('script',attrs={'data-r34-enhancement':''});script.string=js;soup.body.append(script)
    html=str(soup);verify(html,reg);return html

def output(registry,css,js,destination,receipt):
    raw=registry.read_bytes();html=build(json.loads(raw),css.read_text(),js.read_text()).encode()
    destination.write_bytes(html)
    stamp={'release':'HOLD','source_registry_sha256':hashlib.sha256(raw).hexdigest(),
           'staging_html_sha256':hashlib.sha256(html).hexdigest(),'source_photo_records':6,
           'photo_reuse_holds':6,'unverified_alias':'S67-19766','atlas_pins':0,'atlas_edges':0,
           'word_press_staging':'NOT_INSTALLED'}
    receipt.write_text(json.dumps(stamp,indent=2,sort_keys=True)+'\n');return stamp

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('registry','css','js','out','receipt'):p.add_argument('--'+n,required=True,type=Path)
    a=p.parse_args();print(json.dumps(output(a.registry,a.css,a.js,a.out,a.receipt),sort_keys=True))
