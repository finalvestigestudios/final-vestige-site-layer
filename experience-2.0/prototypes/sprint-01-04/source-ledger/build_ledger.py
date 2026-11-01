#!/usr/bin/env python3
"""Build a WordPress-compatible, progressively-enhanced source ledger from approved editorial records.
No site writes. No external dependencies or remotely fetched content. For research/prototyping only.
"""
from __future__ import annotations
import json
import re
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parent
MANIFEST=ROOT.parent/'flagship-apollo1'/'source_manifest.json'
VALID_KINDS={'DOCUMENTED CONTEXT','PRIMARY REVIEW BOARD RECORD','INSTRUMENT CHRONOLOGY','HARDWARE AND DESIGN FINDING','EVIDENCE BOUNDARY','ENGINEERING RESPONSE'}
ALLOWED_HOSTS={'www.nasa.gov','nasa.gov','finalvestige.com'}

class BadRecord(ValueError): pass

def safe_https(url: str, *, hosts=ALLOWED_HOSTS) -> str:
    if not isinstance(url,str):raise BadRecord('URL must be string')
    u=urlsplit(url)
    if u.scheme!='https' or u.hostname not in hosts or u.username or u.password or not u.path or any(ord(x)<32 for x in url):
        raise BadRecord(f'Unsafe or unapproved source URL: {url!r}')
    return url

def load_and_validate() -> dict:
    m=json.loads(MANIFEST.read_text(encoding='utf8'))
    safe_https(m['canonical_article']['url'])
    safe_https(m['primary_report']['url'])
    assert len(m['records'])==6
    seen=set()
    for row in m['records']:
        if row['id'] in seen:raise BadRecord('Duplicate record id')
        seen.add(row['id'])
        if row['kind'] not in VALID_KINDS:raise BadRecord('Unreviewed evidence classification')
        for k in ('title','dek','detail','caution','asset','alt','caption','credit'):
            if not isinstance(row.get(k),str) or not row[k].strip():raise BadRecord(f'Missing required field {k} in {row["id"]}')
        if not row['caution'].strip():raise BadRecord('Every record requires a limitation/boundary')
        safe_https(row['record']);safe_https(row['report'])
    return m

CSS='''/* fv-ex2 Source Ledger: all selectors are scoped to allow safe WordPress prototype embedding. */
.fv-ex2-ledger{--fvx-ink:#090a0a;--fvx-surface:#151611;--fvx-raised:#1d1b17;--fvx-paper:#f4efe6;--fvx-muted:#b8b1a6;--fvx-gold:#c7a66c;--fvx-border:#514738;box-sizing:border-box;background:var(--fvx-ink);color:var(--fvx-paper);font-family:Inter,system-ui,sans-serif;font-size:16px;line-height:1.6;isolation:isolate}
.fv-ex2-ledger *, .fv-ex2-ledger *::before,.fv-ex2-ledger *::after{box-sizing:inherit}
.fv-ex2-ledger :focus-visible{outline:3px solid var(--fvx-gold);outline-offset:3px}
.fv-ex2-ledger [hidden]{display:none!important}
.fv-ex2-ledger a{color:var(--fvx-gold)}
.fv-ex2-ledger button,.fv-ex2-ledger input{font:inherit}
.fv-ex2-ledger button{cursor:pointer}
.fv-ex2-ledger__wrap{width:min(1400px,calc(100% - clamp(36px,8vw,136px)));margin:0 auto}
.fv-ex2-ledger__mast{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:25px 0;border-bottom:1px solid var(--fvx-border);font:700 11px/1.5 ui-monospace,monospace;letter-spacing:.11em;text-transform:uppercase;color:var(--fvx-gold)}
.fv-ex2-ledger__hero{padding:clamp(62px,9vw,125px) 0 clamp(46px,7vw,95px);display:grid;grid-template-columns:1.15fr .85fr;gap:clamp(24px,6vw,100px);align-items:end}
.fv-ex2-ledger__eyebrow{font:700 11px/1.5 ui-monospace,monospace;color:var(--fvx-gold);letter-spacing:.15em}
.fv-ex2-ledger h1{font:400 clamp(58px,9vw,130px)/.94 Georgia,serif;letter-spacing:-.05em;margin:24px 0;color:var(--fvx-paper)}
.fv-ex2-ledger h1 em{color:var(--fvx-gold);font-style:italic}
.fv-ex2-ledger__hero p{font-size:clamp(17px,1.6vw,22px);color:var(--fvx-muted);line-height:1.75;max-width:530px}
.fv-ex2-ledger__heroaside{border-top:1px solid var(--fvx-gold);padding:28px 0 0;font-size:14px;color:var(--fvx-muted)}
.fv-ex2-ledger__heroaside strong{color:var(--fvx-paper)}
.fv-ex2-ledger__tools{border-top:1px solid var(--fvx-border);display:flex;align-items:center;gap:20px;justify-content:space-between;padding:25px 0}
.fv-ex2-ledger__tools label{font:700 11px ui-monospace,monospace;color:var(--fvx-gold);white-space:nowrap}
.fv-ex2-ledger__tools input{background:var(--fvx-raised);color:var(--fvx-paper);border:1px solid #796d55;padding:13px 16px;width:min(520px,100%);border-radius:0}
.fv-ex2-ledger__status{font:12px/1.4 ui-monospace,monospace;color:var(--fvx-gold);min-width:130px;text-align:right}
.fv-ex2-ledger__grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;padding:0 0 75px}
.fv-ex2-ledger__card{min-width:0;background:linear-gradient(135deg,#1a1b17,#0f110e);border:1px solid var(--fvx-border);padding:clamp(23px,3vw,40px);display:flex;flex-direction:column;gap:12px}
.fv-ex2-ledger__cardhead{display:flex;gap:15px;justify-content:space-between;align-items:start}
.fv-ex2-ledger__number,.fv-ex2-ledger__kind{font:700 10px/1.6 ui-monospace,monospace;letter-spacing:.09em;color:var(--fvx-gold)}
.fv-ex2-ledger__kind{max-width:50%;text-align:right;color:#d9ccad}
.fv-ex2-ledger__card h2{font:400 clamp(27px,2.8vw,43px)/1.09 Georgia,serif;letter-spacing:-.02em;margin:9px 0 7px}
.fv-ex2-ledger__recordid{font:11px/1.5 ui-monospace,monospace;color:#c4bbab;overflow-wrap:anywhere}
.fv-ex2-ledger__summary{color:#ded8ce;font-size:15px;line-height:1.7;margin:9px 0}
.fv-ex2-ledger__boundary{padding:16px 19px;border-left:2px solid var(--fvx-gold);background:#c7a66c0c;margin-top:auto}
.fv-ex2-ledger__boundary strong{display:block;font:700 10px ui-monospace,monospace;color:var(--fvx-gold);letter-spacing:.12em}
.fv-ex2-ledger__boundary p{color:#ddd6ca;margin:9px 0 0;font-size:14px}
.fv-ex2-ledger__recordlinks{display:flex;flex-wrap:wrap;gap:18px;padding-top:8px;font-size:13px}
.fv-ex2-ledger__recordlinks a{text-decoration-thickness:1px;text-underline-offset:4px}
.fv-ex2-ledger__fulltext{color:var(--fvx-muted);border-top:1px solid var(--fvx-border);padding-top:15px}
.fv-ex2-ledger__fulltext summary{cursor:pointer;color:var(--fvx-paper);font-size:13px;font-weight:650}
.fv-ex2-ledger__fulltext p{font-size:14px;line-height:1.75}
.fv-ex2-ledger__empty{border:1px dashed var(--fvx-gold);padding:30px;color:var(--fvx-paper);font-size:15px;margin-bottom:50px}
.fv-ex2-ledger__footer{border-top:1px solid var(--fvx-border);padding:35px 0 70px;display:flex;justify-content:space-between;gap:30px;font-size:13px;color:var(--fvx-muted)}
@media(max-width:1000px){.fv-ex2-ledger__hero{grid-template-columns:1fr}.fv-ex2-ledger__heroaside{max-width:620px}}
@media(max-width:760px){.fv-ex2-ledger__grid{grid-template-columns:1fr}.fv-ex2-ledger__tools{align-items:stretch;flex-direction:column}.fv-ex2-ledger__tools input{width:100%}.fv-ex2-ledger__status{text-align:left}}
@media(max-width:480px){.fv-ex2-ledger h1{font-size:clamp(55px,14vw,75px)}.fv-ex2-ledger__mast{flex-wrap:wrap}.fv-ex2-ledger__wrap{width:calc(100% - 36px)}.fv-ex2-ledger__card{padding:20px}}
@media(prefers-reduced-motion:reduce){.fv-ex2-ledger *, .fv-ex2-ledger *::before,.fv-ex2-ledger *::after{scroll-behavior:auto!important;animation:none!important;transition:none!important}}
'''
JS='''/* Self-contained, optional progressive enhancement. No network, storage, third-party JS or HTML injection. */
(()=>{'use strict';
document.querySelectorAll('[data-fvx-ledger]').forEach(root=>{
 if(root.dataset.fvxInitialized==='yes')return;
 const search=root.querySelector('[data-fvx-search]');
 const tools=root.querySelector('[data-fvx-tools]');
 const status=root.querySelector('[data-fvx-status]');
 const cards=[...root.querySelectorAll('[data-fvx-record]')];
 const empty=root.querySelector('[data-fvx-empty]');
 if(!search||!tools||!status||!cards.length||!empty)return;
 try{
   const filter=()=>{
     const needle=search.value.trim().toLocaleLowerCase();
     let shown=0;
     cards.forEach(card=>{
       const visible=!needle||card.dataset.fvxSearch.toLocaleLowerCase().includes(needle);
       card.hidden=!visible;if(visible)shown++;
     });
     status.textContent=`${shown} of ${cards.length} evidence records`;
     empty.hidden=shown!==0;
   };
   search.addEventListener('input',filter);
   root.dataset.fvxInitialized='yes';
   filter();
   tools.hidden=false;
 }catch(_){
   root.dataset.fvxInitialized='';
   cards.forEach(card=>card.hidden=false);
   tools.hidden=true;
   empty.hidden=true;
 }
});
})();
'''

def render_content(m:dict, instance:str='apollo1')->str:
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', instance): raise BadRecord('Instance identifier must be lowercase ASCII slug')
    title_id=f'fv-ex2-ledger-{instance}-title'
    search_id=f'fv-ex2-ledger-{instance}-search'
    grid_id=f'fv-ex2-ledger-{instance}-grid'
    cards=[]
    for i,row in enumerate(m['records']):
        title=escape(row['title']);rid=escape(row['asset']);kind=escape(row['kind']);rid_target=escape(row['id'],quote=True)
        needle=escape(' '.join([row['title'],row['asset'],row['kind'],row['dek'],row['detail'],row['caution']]),quote=True)
        cards.append(f'''<article class="fv-ex2-ledger__card" id="fv-ex2-ledger-{instance}-{rid_target}" data-fvx-record data-fvx-search="{needle}">
          <div class="fv-ex2-ledger__cardhead"><span class="fv-ex2-ledger__number">EVIDENCE {i+1:02d} / 06</span><span class="fv-ex2-ledger__kind">{kind}</span></div>
          <div><h2>{title}</h2><div class="fv-ex2-ledger__recordid">{rid} · {escape(row['credit'])}</div></div>
          <p class="fv-ex2-ledger__summary">{escape(row['dek'])}</p>
          <div class="fv-ex2-ledger__boundary"><strong>EVIDENCE LIMITATION</strong><p>{escape(row['caution'])}</p></div>
          <details class="fv-ex2-ledger__fulltext"><summary>Review the underlying finding</summary><p>{escape(row['detail'])}</p></details>
          <div class="fv-ex2-ledger__recordlinks"><a href="{escape(safe_https(row['record']),quote=True)}" target="_blank" rel="noopener noreferrer">NASA archive record ↗</a><a href="{escape(safe_https(row['report']),quote=True)}" target="_blank" rel="noopener noreferrer">Institutional research ↗</a></div>
          </article>''')
    article=safe_https(m['canonical_article']['url'])
    report=safe_https(m['primary_report']['url'])
    return f'''<section class="fv-ex2-ledger" data-fvx-ledger aria-labelledby="{title_id}">
      <div class="fv-ex2-ledger__wrap">
       <div class="fv-ex2-ledger__mast"><span>FINAL VESTIGE STUDIOS / RESEARCH DESK</span><span>APOLLO 1 · 1967</span></div>
       <header class="fv-ex2-ledger__hero"><div><span class="fv-ex2-ledger__eyebrow">SIX HISTORICAL RECORDS · SIX LIMITATIONS</span><h1 id="{title_id}">The proof <em>and the gaps.</em></h1><p>Every claim has a history. Here are the records behind our Apollo 1 investigation—and what the surviving evidence does not allow us to say.</p></div><aside class="fv-ex2-ledger__heroaside"><strong>How to use this desk.</strong><p>Expand a finding for historical context. Follow the original NASA record to inspect its provenance. Our interpretation is not a substitute for that source.</p></aside></header>
       <div class="fv-ex2-ledger__tools" data-fvx-tools hidden><label for="{search_id}">SEARCH SOURCE RECORDS</label><input type="search" id="{search_id}" data-fvx-search placeholder="Ignition, hatch, oxygen, pressure…" autocomplete="off" aria-controls="{grid_id}"><span class="fv-ex2-ledger__status" role="status" aria-live="polite" data-fvx-status></span></div>
       <div class="fv-ex2-ledger__grid" id="{grid_id}">{''.join(cards)}</div>
       <p class="fv-ex2-ledger__empty" data-fvx-empty hidden>No matching evidence records. Try a different search.</p>
       <footer class="fv-ex2-ledger__footer"><span>FINAL VESTIGE · SOURCE-BACKED R&D CONCEPT · NOT LIVE</span><div><a href="{escape(article,quote=True)}">Read original investigation ↗</a> · <a href="{escape(report,quote=True)}">NASA Review Board ↗</a></div></footer>
      </div>
    </section>'''

def main():
    manifest=load_and_validate()
    (ROOT/'source-ledger.css').write_text(CSS,encoding='utf8')
    (ROOT/'source-ledger.js').write_text(JS,encoding='utf8')
    component=render_content(manifest)
    (ROOT/'wordpress-block.html').write_text('<!-- wp:html -->\n'+component+'\n<!-- /wp:html -->\n',encoding='utf8')
    (ROOT/'wp-staging-plugin'/'templates').mkdir(parents=True,exist_ok=True)
    (ROOT/'wp-staging-plugin'/'assets').mkdir(parents=True,exist_ok=True)
    (ROOT/'wp-staging-plugin'/'templates'/'ledger.html').write_text(component+'\n',encoding='utf8')
    (ROOT/'wp-staging-plugin'/'assets'/'source-ledger.css').write_text(CSS,encoding='utf8')
    (ROOT/'wp-staging-plugin'/'assets'/'source-ledger.js').write_text(JS,encoding='utf8')
    (ROOT/'index.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Source Ledger / Final Vestige Studios</title><style>'+CSS+'</style></head><body style="margin:0;background:#090a0a">'+component+'<script>'+JS+'</script></body></html>',encoding='utf8')
    print('PASS: six source records validated, standalone HTML, WordPress block markup, scoped CSS & JS generated')

if __name__=='__main__':main()
