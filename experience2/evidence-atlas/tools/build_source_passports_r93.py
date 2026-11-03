#!/usr/bin/env python3
"""Apollo R93 source passports: custody-verified, text-only, printable source references.

Staging only. Derives data from generated R92 Research Reading Room and Hub;
never invents catalog associations, image permissions, chronology or geospatial data.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re
from html.parser import HTMLParser
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

def sha(p:Path)->str: return hashlib.sha256(p.read_bytes()).hexdigest()
def clean(s:str)->str: return ' '.join(html.unescape(re.sub(r'<[^>]+>',' ',s)).split())

VIEW={
    'R89_REVIEW_HUB.html':'r89-source-',
    'R88_READING_ROOM.html':'r88-',
    'R87_PHOTOGRAPH_DATE_RAIL.html':'r87-record-',
    'R85_NASA_SOURCE_REVIEW.html':'r85-source-',
}

class Cards(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cards={};self.card=None;self.boundary=False;self.buff=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='article' and re.fullmatch(r'r88-0[1-6]',a.get('id','')):
            n=a['id'][-2:]
            if n in self.cards or self.card: raise ValueError('R93_DUPLICATE_SOURCE')
            self.card={'id':n,'title':a.get('data-title'),'catalog':a.get('data-catalog'),
                       'date':a.get('data-date'),'limit':a.get('data-limit'),
                       'boundaries':[],'nasa':[]}
        if self.card and tag=='p' and 'boundary' in a.get('class','').split():
            self.boundary=True;self.buff=[]
        if self.card and tag=='a' and a.get('href','').startswith('https://www.nasa.gov/image-detail/'):
            self.card['nasa'].append(a['href'])
    def handle_data(self,data):
        if self.boundary: self.buff.append(data)
    def handle_endtag(self,tag):
        if self.card and tag=='p' and self.boundary:
            self.card['boundaries'].append(' '.join(''.join(self.buff).split()))
            self.boundary=False
        if self.card and tag=='article':
            self.cards[self.card['id']]=self.card;self.card=None

def verified_records(src:Path)->list[dict]:
    r92=json.loads((src/'R92_RECIPROCAL_ROUTES_RECEIPT.json').read_text())
    r89=json.loads((src/'R89_INTEGRITY_RECEIPT.json').read_text())
    if (r92.get('release')!='STAGING_HOLD' or r92.get('photographic_rights_cleared')!=0
        or r92.get('source_bindings')!=24 or r92.get('verified_new_reciprocal_routes')!=54
        or r89.get('photo_rights_cleared')!=0 or r89.get('geo_pins')!=0
        or r89.get('inferred_edges')!=0 or len(r89.get('record_source_bindings',{}))!=24):
        raise ValueError('R93_BASE_CUSTODY_UNVERIFIED')
    for name,digest in r92['files'].items():
        if '/' in name or not (src/name).is_file() or sha(src/name)!=digest:
            raise ValueError('R93_BASE_HASH_MISMATCH:'+name)
    parser=Cards();parser.feed((src/'R88_READING_ROOM.html').read_text());parser.close()
    if set(parser.cards)!={f'{i:02}' for i in range(1,7)}:
        raise ValueError('R93_INCOMPLETE_PASSports')
    nasa=r89['source_urls_by_id']
    if len(nasa)!=6: raise ValueError('R93_NASA_REGISTER_MISSING')
    hub=(src/'R89_REVIEW_HUB.html').read_text()
    records=[]
    for n,rec in sorted(parser.cards.items()):
        matches=re.findall(r'<article\b[^>]*id="r89-source-'+n+r'"[^>]*>(.*?)</article>',hub,re.S|re.I)
        if len(matches)!=1:raise ValueError('R93_HUB_RECORD_MISSING:'+n)
        part=matches[0]
        expressions={'title':r'<h3\b[^>]*>(.*?)</h3>',
          'catalog':r'<strong>NASA catalog claim:</strong>\s*(.*?)</p>',
          'date':r'<strong>Photograph date:</strong>\s*(.*?)</p>',
          'limit':r'<strong>Evidence limitation:</strong>\s*(.*?)</p>'}
        for field,regex in expressions.items():
            found=re.search(regex,part,re.S)
            if not found or clean(found.group(1))!=rec[field]:
                raise ValueError('R93_CROSS_VIEW_DISAGREEMENT:'+n+'/'+field)
        if rec['nasa']!=[nasa[n]]:raise ValueError('R93_NASA_LINK_CHANGED:'+n)
        b=rec['boundaries']
        if (len(b)!=2 or not b[0].startswith('What it can establish:')
            or not b[1].startswith('What it cannot establish:')
            or b[1].removeprefix('What it cannot establish:').strip()!=rec['limit']):
            raise ValueError('R93_EVIDENCE_LIMIT_CHANGED:'+n)
        if 'INDIVIDUAL REVIEW REQUIRED' not in part:
            raise ValueError('R93_RIGHTS_GATE_CHANGED:'+n)
        if n=='01' and (rec['catalog']!='S67-19766' or
                         rec['date']!='January 1967 — day unconfirmed' or 'provisional' not in part.lower()):
            raise ValueError('R93_PROVISIONAL_SOURCE_PRETENDED_CERTAIN')
        rec.update(url=nasa[n],can=b[0].removeprefix('What it can establish:').strip(),
                   cannot=rec['limit'],rights='INDIVIDUAL REVIEW REQUIRED',provisional=n=='01')
        records.append(rec)
    if [r['date'] for r in records if r['id'] in ('04','06')]!=['January 24, 2017']*2:
        raise ValueError('R93_TRIBUTE_SEQUENCE_INVENTED')
    return records

def citation(r:dict)->str:
    return ('NASA · '+r['title']+' · Photograph date: '+r['date']+
      ' · Catalog claim: '+r['catalog']+' · '+r['url']+
      ' · Photo reuse: INDIVIDUAL REVIEW REQUIRED'+
      (' · Catalog association provisional' if r['provisional'] else ''))

CSS=""":root{color-scheme:dark;--ink:#ece4d6;--gold:#d5b96c;--muted:#c8bfae;--line:#6d6658}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;background:#171a1b;color:var(--ink);font:16px/1.65 system-ui,sans-serif}
a{color:var(--gold);text-underline-offset:.2em;overflow-wrap:anywhere}
a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid var(--gold);outline-offset:4px}
.wrap{width:min(1120px,calc(100% - 2rem));margin:auto}.skip{position:absolute;top:-10rem;left:1rem;background:#fff;color:#111;padding:1rem}.skip:focus{top:1rem}
header{padding:clamp(3rem,8vw,7rem) 0 2rem;border-bottom:1px solid var(--line)}
.kicker{font-size:.78rem;letter-spacing:.12em;text-transform:uppercase;color:var(--gold);font-weight:700}
h1{font:normal clamp(2.6rem,6vw,5.1rem)/1.1 Georgia,serif;max-width:920px}
h2{font:normal clamp(1.7rem,3vw,2.5rem)/1.2 Georgia,serif}
h3{font:normal 1.55rem/1.25 Georgia,serif}
.lead{max-width:760px;color:var(--muted);font-size:1.15rem}
.hold{padding:1rem 1.25rem;background:#343029;border-left:4px solid var(--gold)}
nav.jump,nav.routes{display:flex;flex-wrap:wrap;gap:.6rem;margin:1.5rem 0}
nav.jump a,nav.routes a,.download a,button{display:inline-flex;min-height:44px;align-items:center;padding:.6rem .85rem;border:1px solid var(--line)}
main{padding:2rem 0 5rem}.download{background:#2a2d2b;padding:1.2rem;border:1px solid var(--line)}
.download a{margin:.3rem .5rem .3rem 0}.cards{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1rem}
.card{background:#222526;border:1px solid var(--line);padding:clamp(1rem,2.5vw,2rem);min-width:0;scroll-margin-top:1rem}
.card:target{outline:2px solid var(--gold);outline-offset:3px}
.card dl{display:grid;grid-template-columns:auto minmax(0,1fr);gap:.2rem 1rem}
.card dd{margin:0;overflow-wrap:anywhere}.card dt{color:var(--muted)}
.boundary{padding-top:.9rem;border-top:1px solid var(--line)}.boundary strong{color:var(--gold)}
details{border:1px solid var(--line);padding:.8rem}summary{cursor:pointer;min-height:44px;padding:.6rem;font-weight:700}
.copy{display:none;background:var(--gold);color:#151817;cursor:pointer;font-weight:700}
.r93-js .copy{display:inline-flex}.copy-state{color:var(--gold);min-height:1.5em}.print-source{display:none}
footer{border-top:1px solid var(--line);padding:2rem 0;color:var(--muted)}
@media(max-width:700px){.cards{grid-template-columns:minmax(0,1fr)}
.card dl{grid-template-columns:minmax(0,1fr)}.card dt{font-weight:700}
nav.routes{display:grid;grid-template-columns:minmax(0,1fr)}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{animation:none!important;transition:none!important}}
@media(forced-colors:active){.card,.hold,.download{border-color:CanvasText}a{color:LinkText}.copy{background:ButtonFace;color:ButtonText}}
@media print{:root{color-scheme:light}html,body,.card,.hold{background:#fff!important;color:#000!important}
header{padding:0}h1{font-size:28pt}.wrap{width:100%}.cards{display:block}
.card{break-inside:avoid;margin:1rem 0;padding:.75rem;border:1px solid #777}
nav,.download,details,.copy,.copy-state,.skip,footer{display:none!important}
.print-source{display:block!important;color:#000!important;overflow-wrap:anywhere}
.kicker,.boundary,.lead{color:#000!important}}
"""
JS='''"use strict";(()=>{if(!navigator.clipboard||!navigator.clipboard.writeText)return;
document.documentElement.classList.add("r93-js");
for(const card of document.querySelectorAll(".card")){
const button=card.querySelector("button.copy"),status=card.querySelector(".copy-state");
button.addEventListener("click",async()=>{try{
await navigator.clipboard.writeText(card.dataset.citation);
status.textContent="Reference copied for source "+card.dataset.source+". No image rights conveyed.";
}catch(_){status.textContent="Clipboard unavailable. Use the visible NASA link or reference download.";}});}
})();'''

def render(records:list[dict])->str:
    blocks=[]
    for r in records:
        n=r['id']
        routes=''.join('<a href="'+html.escape(page+'#'+prefix+n,quote=True)+'">'+html.escape(label)+'</a>'
             for page,prefix,label in [
             ('R89_REVIEW_HUB.html','r89-source-','Evidence Hub'),
             ('R88_READING_ROOM.html','r88-','Reading Room'),
             ('R87_PHOTOGRAPH_DATE_RAIL.html','r87-record-','Photo-date rail'),
             ('R85_NASA_SOURCE_REVIEW.html','r85-source-','Rights review')])
        blocks.append('<article class="card" id="passport-'+n+'" aria-labelledby="title-'+n+
          '" data-source="'+n+'" data-citation="'+html.escape(citation(r),quote=True)+'">'+
          '<p class="kicker">Evidence passport '+n+' / 06 · IMAGE REUSE HOLD</p>'+
          '<h3 id="title-'+n+'">'+html.escape(r['title'])+'</h3><dl>'+
          '<dt>Catalog claim</dt><dd>'+html.escape(r['catalog'])+
          (' (provisional)' if r['provisional'] else '')+
          '</dd><dt>Photograph date</dt><dd>'+html.escape(r['date'])+
          '</dd><dt>Reuse status</dt><dd><strong>INDIVIDUAL REVIEW REQUIRED</strong></dd></dl>'+
          '<p class="boundary"><strong>What it can establish:</strong> '+html.escape(r['can'])+'</p>'+
          '<p class="boundary"><strong>What it cannot establish:</strong> '+html.escape(r['cannot'])+'</p>'+
          '<details><summary>SourceDrawer · reference and same-record views</summary>'+
          '<p>Primary source: <a href="'+html.escape(r['url'],quote=True)+'" rel="noopener noreferrer" target="_blank">'+html.escape(r['url'])+'</a></p>'+
          '<p>Different presentations of this same source, not invented historical connections:</p>'+
          '<nav class="routes" aria-label="Other views of source '+n+'">'+routes+'</nav></details>'+
          '<p><a href="'+html.escape(r['url'],quote=True)+'" rel="noopener noreferrer" target="_blank">NASA primary source '+n+' ↗</a></p>'+
          '<button class="copy" type="button">Copy reference '+n+'</button><p class="copy-state" role="status" aria-live="polite"></p>'+
          '<p class="print-source"><strong>NASA:</strong> '+html.escape(r['url'])+
          '<br><strong>Photo reuse:</strong> INDIVIDUAL REVIEW REQUIRED</p></article>')
    jump=''.join('<a href="#passport-'+str(i).zfill(2)+'">Source '+str(i).zfill(2)+'</a>' for i in range(1,7))
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+
     '<meta name="robots" content="noindex,nofollow"><title>Apollo 1 · Source Passports · STAGING HOLD</title>'+
     '<link rel="stylesheet" href="source_passports_r93.css"><script src="source_passports_r93.js" defer></script></head><body>'+
     '<a class="skip" href="#passports">Skip to evidence passports</a><div class="wrap"><header>'+
     '<p class="kicker">Final Vestige Studios / Apollo Evidence Studio</p><h1>Carry the evidence.<br>Keep its limits.</h1>'+
     '<p class="lead">Six NASA source passports derived from the Research Desk and Evidence Atlas, each retaining what the photograph can and cannot establish.</p>'+
     '<p class="hold" role="note">STAGING HOLD · NOT FOR PUBLICATION. Zero of six photograph-specific rights reviews completed. S67-19766 remains provisional. Photograph dates do not reconstruct the Apollo 1 fire.</p>'+
     '<nav class="jump" aria-label="Jump to source passports">'+jump+'</nav></header><main id="passports">'+
     '<h2>Source passport shelf</h2><p>Reference order is register order, not accident chronology. No NASA photographs are embedded.</p>'+
     '<div class="download"><strong>Portable research references — metadata only, not image-use permission.</strong><br>'+
     '<a href="R93_NASA_REFERENCES.txt" download>Download reference text</a>'+
     '<a href="R93_SOURCE_PASSPORTS.json" download>Download JSON records</a></div>'+
     '<div class="cards">'+''.join(blocks)+'</div></main><footer>'+
     'Source links do not imply NASA endorsement or photographic reuse clearance. No geographic or causal links inferred.'+
     '</footer></div></body></html>')

def build(src:Path,out:Path,archive:Path|None=None)->dict:
    if out.exists() and any(out.iterdir()):raise ValueError('R93_OUTPUT_EXISTS')
    if archive and archive.exists():raise ValueError('R93_ARCHIVE_EXISTS')
    records=verified_records(src);out.mkdir(parents=True,exist_ok=True)
    for p in sorted(src.iterdir()):
        if p.is_file():(out/p.name).write_bytes(p.read_bytes())
    public=[{k:r[k] for k in ('id','title','catalog','date','can','cannot','url','rights','provisional')} for r in records]
    files={'R93_SOURCE_PASSPORTS.html':render(records),
        'source_passports_r93.css':CSS,
        'source_passports_r93.js':JS,
        'R93_SOURCE_PASSPORTS.json':json.dumps({'schema':'fv.apollo.r93.passports.v1','release':'STAGING_HOLD','photo_reuse_approved':False,'records':public},sort_keys=True,indent=2)+'\n',
        'R93_NASA_REFERENCES.txt':'APOLLO 1 / NASA SOURCE REFERENCES / STAGING HOLD\nNOT PHOTO REUSE PERMISSION; NOT AN ACCIDENT CHRONOLOGY\n\n'+'\n\n'.join(citation(r) for r in records)+'\n'}
    for name,data in files.items():(out/name).write_text(data)
    receipt={'schema':'fv.apollo.r93.build.v1','release':'STAGING_HOLD','photographic_rights_cleared':0,
      'publication_approved':False,'hosted_wordpress_verified':False,'manual_screen_reader_verified':False,
      'verified_source_passports':6,'new_geo_pins':0,'new_historical_edges':0,
      'source_r92_receipt_sha256':sha(src/'R92_RECIPROCAL_ROUTES_RECEIPT.json'),
      'files':{name:sha(out/name) for name in sorted(files)}}
    (out/'R93_PASSPORT_RECEIPT.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    if archive:
        archive.parent.mkdir(parents=True,exist_ok=True)
        with ZipFile(archive,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
            for p in sorted(out.iterdir()):
                zi=ZipInfo(p.name,date_time=(1980,1,1,0,0,0));zi.compress_type=ZIP_DEFLATED
                zi.external_attr=0o100644<<16;zi.create_system=3
                z.writestr(zi,p.read_bytes())
    return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--src',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--archive',type=Path)
    a=p.parse_args();print(json.dumps(build(a.src,a.out,a.archive),sort_keys=True))
