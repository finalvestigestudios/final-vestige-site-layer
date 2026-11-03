#!/usr/bin/env python3
"""R93 Apollo source-register export. Isolated staging, no media, no CMS writes.

Build from R92's audited four-view output (normal CI) or from a separately
verified exact R92 artifact (--reviewed-r92 for offline inspection only).
"""
from __future__ import annotations
import argparse
import csv
from html import escape, unescape
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE_FILES = (
    'experience2/evidence-atlas/tools/build_citations_r93.py',
    'experience2/evidence-atlas/tests/test_citations_r93.py',
    'experience2/evidence-atlas/tests/browser_citations_r93.py',
    'experience2/evidence-atlas/R93_CITATION_REGISTER_STAGING_HOLD.md',
    '.github/workflows/ex2-apollo-r93-citations.yml',
)
VIEWS = (
    ('R89_REVIEW_HUB.html', 'r89-source-', 'Evidence Hub'),
    ('R88_READING_ROOM.html', 'r88-', 'Research Desk'),
    ('R87_PHOTOGRAPH_DATE_RAIL.html', 'r87-record-', 'Photograph dates'),
    ('R85_NASA_SOURCE_REVIEW.html', 'r85-source-', 'Rights review'),
)
CARD = re.compile(r'<article\s+class="record"\s+id="r88-(0[1-6])"(?P<attrs>[^>]+)>(?P<body>.*?)</article>', re.S)
BOUNDARY = re.compile(r'<p\s+class="boundary"><strong>What it (can|cannot) establish:</strong>\s*([^<]+)</p>')
NASA = re.compile(r'<a\s+class="source"\s+href="(https://www\.nasa\.gov/image-detail/[^" ]+/)"')
FIELDS = ('source_id','title','catalog_id','photograph_date','date_certainty','can_establish','cannot_establish','nasa_source_url','image_rights_status','catalog_identity_status')
CSS = '''/* R93 isolated source-register index; no remote dependencies. */
:root{color-scheme:dark;--bg:#101310;--panel:#1b211d;--ink:#f3f0e7;--sub:#d4d1c7;--gold:#e3bb7b;--rule:#797c72;font:17px/1.65 system-ui,sans-serif}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink)}a{color:var(--gold);overflow-wrap:anywhere;text-underline-offset:.2em}a:focus-visible,button:focus-visible,input:focus-visible{outline:3px solid #ffe18e;outline-offset:3px}.wrap{width:min(1200px,calc(100% - 2rem));margin:auto}.skip{position:absolute;left:-99999px;top:12px;background:#fff;color:#111;padding:.7rem}.skip:focus{left:12px}.eyebrow{font-size:.78rem;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);font-weight:750}header{padding:clamp(2rem,6vw,6rem) 0;border-bottom:1px solid var(--rule)}h1,h2,h3{font-family:Georgia,serif;line-height:1.14}h1{font-size:clamp(2.6rem,7vw,6rem);max-width:19ch;margin:.5em 0}h1 em{font-weight:400;color:var(--gold)}h2{font-size:clamp(1.8rem,4vw,2.6rem)}h3{font-size:1.45rem}.lead{max-width:70ch;font-size:1.15rem}.hold{border:2px solid var(--gold);padding:1rem 1.2rem;background:#302f25;max-width:85ch}.routes{display:flex;flex-wrap:wrap;gap:.7rem;margin:1.5rem 0}.routes a,.view-links a,.download{display:inline-flex;align-items:center;min-height:44px;padding:.55rem .8rem;border:1px solid var(--gold);max-width:100%}.download{font-weight:700;background:var(--gold);color:#161810}main{padding:2rem 0}.filter-panel{display:flex;flex-wrap:wrap;gap:.8rem;padding:1rem 0;border-block:1px solid var(--rule)}.filter-panel[hidden]{display:none}.filter-panel fieldset{border:0;padding:0;display:flex;gap:.7rem;flex-wrap:wrap}.filter-panel label{display:inline-flex;align-items:center;min-height:44px;gap:.4rem;border:1px solid var(--rule);padding:.4rem .65rem;cursor:pointer}.filter-panel input{width:20px;height:20px;accent-color:var(--gold)}.count{min-height:2rem;margin-top:1rem;color:var(--gold);font-weight:650}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1.3rem;padding:1rem 0 3rem}.item{min-width:0;border:1px solid var(--rule);background:var(--panel);padding:clamp(1rem,3vw,2rem);scroll-margin-top:1rem}.item[hidden]{display:none!important}.meta{font-size:.8rem;color:var(--gold);letter-spacing:.08em;font-weight:800}.boundary{border-left:3px solid var(--gold);padding-left:1rem}.boundary strong{color:var(--ink)}.view-links{display:flex;flex-wrap:wrap;gap:.65rem;padding:1rem 0}.view-links a{font-size:.9rem}.raw{word-break:break-all;font-size:.9rem}.warning{font-weight:700;color:#ffe8bb}.method{max-width:78ch;border-top:1px solid var(--rule);padding:2rem 0}footer{border-top:1px solid var(--rule);padding:2rem 0 3rem;color:var(--sub)}
@media(max-width:730px){.grid{grid-template-columns:1fr}.wrap{width:min(100% - 1.2rem,1200px)}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
@media(forced-colors:active){.hold,.item,.view-links a,.routes a{border-color:CanvasText}.download{forced-color-adjust:auto}}
@media print{:root{color-scheme:light}body{background:#fff;color:#000;font:10pt/1.45 system-ui,sans-serif}.wrap{width:100%}header{padding:0}.grid{display:block}.item{background:#fff;color:#000;border:1pt solid #444;break-inside:avoid;margin:0 0 10pt;padding:10pt}.meta,.warning{color:#000}.hold{background:#fff;color:#000;border:1pt solid #000}.boundary{border-color:#000}a{color:#000}.view-links,.routes,.filter-panel,.download,.skip{display:none!important}.raw{font-size:8pt}h1{font-size:31pt}h2{font-size:18pt}h3{font-size:13pt}footer{color:#000}}
'''
JS = '''/* R93 optional simple period lens; all cards and source links remain visible without JS. */
(()=>{'use strict';const root=document.querySelector('#r93-register');const controls=document.querySelector('#r93-filter');const status=document.querySelector('#r93-count');if(!root||!controls||!status)return;const cards=[...root.querySelectorAll('article.item[data-period]')];if(cards.length!==6||new Set(cards.map(x=>x.id)).size!==6)return;const radios=[...controls.querySelectorAll('input[name="r93-period"]')];if(radios.length!==4)return;const apply=()=>{const checked=radios.find(x=>x.checked);if(!checked)return;let visible=0;for(const card of cards){const show=checked.value==='all'||card.dataset.period===checked.value;card.hidden=!show;if(show)visible++}status.textContent=visible+' of 6 source records shown. This is a photograph-date grouping, not an accident chronology.'};for(const radio of radios)radio.addEventListener('change',apply);controls.hidden=false;apply()})();
'''

def sha(b:bytes)->str:return hashlib.sha256(b).hexdigest()

def audit_reviewed_r92(stage:Path)->dict:
    """Never treat an unaudited file directory as verified source material."""
    r92=json.loads((stage/'R92_RECIPROCAL_ROUTES_RECEIPT.json').read_text('utf8'))
    r89=json.loads((stage/'R89_INTEGRITY_RECEIPT.json').read_text('utf8'))
    if any((r92.get('release')!='STAGING_HOLD',r92.get('deployment_allowed') is not False,
            r92.get('source_bindings')!=24,r92.get('verified_new_reciprocal_routes')!=54,
            r92.get('photographic_rights_cleared')!=0,
            len(r89.get('source_urls_by_id',{}))!=6,
            len(r89.get('record_source_bindings',{}))!=24,
            r89.get('photo_rights_cleared')!=0)):
        raise ValueError('R93_PARENT_CUSTODY_NOT_APPROVED')
    for filename,checksum in r92.get('files',{}).items():
        if '/' in filename or '\\' in filename or sha((stage/filename).read_bytes())!=checksum:
            raise ValueError('R93_PARENT_HASH_MISMATCH:'+filename)
    if len(r92['files'])!=8:raise ValueError('R93_PARENT_FILE_INVENTORY')
    return r89

def extract(stage:Path)->list[dict]:
    r89=audit_reviewed_r92(stage)
    html=(stage/'R88_READING_ROOM.html').read_text('utf8')
    cards=list(CARD.finditer(html))
    if len(cards)!=6:raise ValueError('R93_SIX_RECORDS_REQUIRED')
    result=[]
    for number,match in enumerate(cards,1):
        ident=f'{number:02}'
        if match.group(1)!=ident:raise ValueError('R93_RECORD_ORDER')
        attrs=dict(re.findall(r'\bdata-(record|title|catalog|date|limit)="([^"]*)"',match.group('attrs')))
        if set(attrs)!={'record','title','catalog','date','limit'} or attrs['record']!=ident:
            raise ValueError('R93_RECORD_ATTRIBUTES')
        bounds=BOUNDARY.findall(match.group('body'))
        links=NASA.findall(match.group('body'))
        if [b[0] for b in bounds]!=['can','cannot'] or len(links)!=1 or links[0]!=r89['source_urls_by_id'][ident]:
            raise ValueError('R93_SOURCE_OR_EVIDENCE_BOUNDARY')
        title=unescape(attrs['title']);catalog=unescape(attrs['catalog']);date=unescape(attrs['date'])
        can=unescape(bounds[0][1]);cannot=unescape(bounds[1][1]);limit=unescape(attrs['limit'])
        if cannot!=limit or not all((title,catalog,date,can,cannot)):
            raise ValueError('R93_EVIDENCE_LIMIT_MISMATCH')
        # Explicit, editorially reviewed meaning of the existing photo-date labels.
        if ident=='01':
            if date!='January 1967 — day unknown' and date!='January 1967 — day unconfirmed':
                raise ValueError('R93_PORTRAIT_DAY_MUST_BE_UNKNOWN')
            certainty='Month only; day unknown; catalog association provisional';group='uncertain'
            if catalog!='S67-19766':raise ValueError('R93_PROVISIONAL_CATALOG')
            catalog_status='Provisional page-to-catalog association; verify before publication'
        else:
            if not re.fullmatch(r'(October 18, 1966|January 3, 1967|January 28, 1967|January 24, 2017)',date):
                raise ValueError('R93_UNREVIEWED_PHOTOGRAPH_DATE')
            certainty='Day-specific photograph date, not accident-event chronology'
            group='retrospective' if date.endswith('2017') else 'contemporary'
            catalog_status='Catalog identifier in source register; image reuse not cleared'
        item=dict(source_id=ident,title=title,catalog_id=catalog,photograph_date=date,
            date_certainty=certainty,can_establish=can,cannot_establish=cannot,
            nasa_source_url=links[0],image_rights_status='INDIVIDUAL REVIEW REQUIRED',
            catalog_identity_status=catalog_status,group=group)
        result.append(item)
    if [x['group'] for x in result].count('uncertain')!=1 or [x['group'] for x in result].count('retrospective')!=2:
        raise ValueError('R93_PERIOD_INTEGRITY')
    return result

def render(records:list[dict])->str:
    parts=['''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><title>Apollo 1 · Source Register · STAGING HOLD</title><link rel="stylesheet" href="source_register_r93.css"><script src="source_register_r93.js" defer></script></head><body><a class="skip" href="#r93-register">Skip to the six source records</a><div class="wrap"><header><p class="eyebrow">FINAL VESTIGE STUDIOS / APOLLO EVIDENCE ATLAS / STAGING REVIEW</p><h1>A source record<br><em>you can carry.</em></h1><p class="lead">Six NASA-linked research entries, with their photographic dates, documented limits and reuse restrictions. Download the source register as a portable CSV or navigate each record through all four research views.</p><p class="hold"><strong>NOT FOR PUBLICATION · STAGING HOLD.</strong> No photograph is reproduced or cleared for reuse. S67-19766 remains a provisional association. Photograph dates are not a reconstruction of the January 27, 1967 fire. These are source citations, not NASA endorsement.</p><nav class="routes" aria-label="Other Apollo research views"><a href="R89_REVIEW_HUB.html">Evidence Hub</a><a href="R88_READING_ROOM.html">Research Desk</a><a href="R87_PHOTOGRAPH_DATE_RAIL.html">Photograph-date rail</a><a href="R85_NASA_SOURCE_REVIEW.html">Rights review</a></nav><p><a class="download" href="R93_APOLLO_SOURCE_REGISTER.csv" download="apollo-1-source-register-STAGING-HOLD.csv">Download six-source citation CSV</a></p></header><main id="r93-register"><h2>Evidence Atlas · source custody</h2><p>Grouping is by <strong>photographic date certainty and era</strong>, never by cause, severity or unsupported geographic relationship. All six records remain visible without JavaScript.</p><div id="r93-filter" class="filter-panel" hidden><fieldset><legend>Show sources by photograph-date grouping</legend><label><input type="radio" name="r93-period" value="all" checked>All six</label><label><input type="radio" name="r93-period" value="contemporary">1966–67 dated</label><label><input type="radio" name="r93-period" value="retrospective">2017 retrospective</label><label><input type="radio" name="r93-period" value="uncertain">Uncertain day</label></fieldset></div><p id="r93-count" class="count" aria-live="polite">Six sources available. All source records are displayed.</p><div class="grid">''']
    for r in records:
        def e(field):return escape(r[field],quote=True)
        parts.append(f'''<article class="item" id="r93-source-{r['source_id']}" data-period="{r['group']}" aria-labelledby="r93-title-{r['source_id']}"><p class="meta">SOURCE {r['source_id']} / 06 · {r['group'].upper()} · MEDIA RIGHTS HOLD</p><h3 id="r93-title-{r['source_id']}">{e('title')}</h3><p><strong>Catalog identity:</strong> {e('catalog_id')}</p><p><strong>Photograph date:</strong> {e('photograph_date')}</p><p><strong>Certainty:</strong> {e('date_certainty')}</p><p class="boundary"><strong>Can establish:</strong> {e('can_establish')}</p><p class="boundary"><strong>Cannot establish:</strong> {e('cannot_establish')}</p><p><strong>Catalog status:</strong> {e('catalog_identity_status')}</p><p class="warning">Image reuse: INDIVIDUAL REVIEW REQUIRED. Source listing is not media permission.</p><nav class="view-links" aria-label="Reviewed evidence views for source {r['source_id']}">''')
        for path,prefix,label in VIEWS:
            parts.append(f'<a href="{path}#{prefix}{r["source_id"]}">{escape(label)} · {r["source_id"]}</a>')
        parts.append(f'''</nav><p class="raw"><strong>NASA image-detail page:</strong> <a href="{e('nasa_source_url')}" target="_blank" rel="noopener noreferrer">{e('nasa_source_url')}</a></p></article>''')
    parts.append('''</div><section class="method"><h2>Method and limitations</h2><p>The downloadable CSV is created from the same six source-controlled Research Desk evidence plates and checked against the 24 NASA source bindings in the Evidence Hub, ChronologyRail, rights-review board and Research Desk. Every record includes a complete NASA image-detail destination, the date certainty, the claim it supports and a claim it cannot establish. No third-party images or externally loaded scripts are included.</p><p>NASA publishes separate <a href="https://www.nasa.gov/nasa-brand-center/">media usage and brand guidelines</a>. Linking to a NASA page does not clear photograph-specific rights, personality/third-party restrictions or imply endorsement. Validate all six individual reuse decisions before any publication.</p></section></main><footer><strong>STAGING HOLD / DO NOT DEPLOY.</strong> No reviewed geographic coordinates, inferred edges, hosted WordPress acceptance or photograph-specific reuse clearance.</footer></div></body></html>''')
    return ''.join(parts)

def make_csv(records:list[dict])->str:
    stream=io.StringIO(newline='')
    writer=csv.DictWriter(stream,fieldnames=FIELDS,lineterminator='\n')
    writer.writeheader()
    for item in records:
        row={k:item[k] for k in FIELDS}
        if any(re.match(r'^\s*[=+@\-\t\r]',v) for v in row.values()):
            raise ValueError('R93_SPREADSHEET_FORMULA_HAZARD')
        writer.writerow(row)
    return stream.getvalue()

def assemble(stage:Path,out:Path,archive:Path|None=None)->dict:
    if out.exists() and any(out.iterdir()):raise ValueError('R93_OUTPUT_NOT_EMPTY')
    if archive and archive.exists():raise ValueError('R93_ARCHIVE_EXISTS')
    records=extract(stage)
    out.mkdir(parents=True,exist_ok=True)
    for existing in sorted(stage.iterdir()):
        if existing.is_file():shutil.copyfile(existing,out/existing.name)
    payload={'R93_SOURCE_REGISTER.html':render(records).encode('utf8'),
             'source_register_r93.css':CSS.encode('utf8'),
             'source_register_r93.js':JS.encode('utf8'),
             'R93_APOLLO_SOURCE_REGISTER.csv':make_csv(records).encode('utf8')}
    for name,data in payload.items():(out/name).write_bytes(data)
    parent=json.loads((stage/'R92_RECIPROCAL_ROUTES_RECEIPT.json').read_text('utf8'))
    receipt={'schema':'fv.apollo.r93.citation-export.v1','release':'STAGING_HOLD','deployment_allowed':False,
             'nasa_photographs_reproduced':0,'reviewed_geographic_pins':0,'inferred_historical_edges':0,
             'photo_rights_cleared':0,'record_count':len(records),'source_view_bindings':24,
             'csv_fields':list(FIELDS),'date_groups':{g:sum(r['group']==g for r in records) for g in ('uncertain','contemporary','retrospective')},
             'parent_r92_sha256':sha((stage/'R92_RECIPROCAL_ROUTES_RECEIPT.json').read_bytes()),
             'generated_files':{k:sha(v) for k,v in sorted(payload.items())}}
    (out/'R93_CITATION_RECEIPT.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n','utf8')
    if archive:
        pack={'built/'+p.name:p.read_bytes() for p in sorted(out.iterdir()) if p.is_file()}
        for f in SOURCE_FILES:pack['source/'+f]=(ROOT/f).read_bytes()
        pack['SHA256_MANIFEST.json']=(json.dumps({'release':'STAGING_HOLD','deployment_allowed':False,
            'files':{k:sha(v) for k,v in sorted(pack.items())}},sort_keys=True,indent=2)+'\n').encode()
        archive.parent.mkdir(parents=True,exist_ok=True)
        with ZipFile(archive,'w',compression=ZIP_DEFLATED,compresslevel=9) as z:
            for name,data in sorted(pack.items()):
                info=ZipInfo(name,date_time=(1980,1,1,0,0,0));info.compress_type=ZIP_DEFLATED
                info.external_attr=0o100644<<16;info.create_system=3
                z.writestr(info,data)
    return receipt

def build(out:Path,archive:Path|None=None,reviewed_r92:Path|None=None)->dict:
    if reviewed_r92 is not None:return assemble(reviewed_r92,out,archive)
    import importlib.util
    builder=HERE/'build_reciprocal_routes_r92.py'
    spec=importlib.util.spec_from_file_location('apollo_r92_readonly',builder)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix='apollo-r93-trusted-r92-') as temp:
        stage=Path(temp)/'r92';module.build(stage)
        return assemble(stage,out,archive)

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('out',type=Path);cli.add_argument('archive',nargs='?',type=Path)
    cli.add_argument('--reviewed-r92',type=Path,help='Offline QA only: prior R92 artifact with exact checksums')
    args=cli.parse_args()
    try:print(json.dumps(build(args.out,args.archive,args.reviewed_r92),sort_keys=True))
    except Exception as e:
        print('R93_STAGING_HOLD: source-register export failed ('+type(e).__name__+')',file=sys.stderr)
        raise SystemExit(1)
