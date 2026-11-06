#!/usr/bin/env python3
"""Deterministic, offline Chromium integration test for staged R152 JS.

This is a controlled Research Desk DOM fixture, not WordPress rendering. It tests
an actual browser and exact local JavaScript bytes. No live URL or network I/O.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS=(320,360,390,768,1440,1920)
JS=Path(__file__).with_name('r152_source_ledger_hash_bridge.js')
CSS='''<style>
body{margin:0;background:#090a0a;color:#f4efe6;font:16px/1.6 system-ui,sans-serif}
main{max-width:1120px;margin:auto;padding:clamp(12px,4vw,40px)}
a{color:#e0c58b}button,input{font:inherit;padding:8px}
[data-fvx-ledger] [hidden]{display:none!important}
[data-fvx-record]{padding:16px;border:1px solid #8d7a59;margin:12px 0;min-width:0}
[data-fvx-record]:focus{outline:3px solid #eed49c}
form{display:grid;gap:12px}nav{display:flex;gap:8px;flex-wrap:wrap}
</style>'''

def fixture(n=6,malformed=False):
    records=[]
    for i in range(n):
        idx=i+1
        extra='' if not (malformed and idx==3) else ' data-missing-index="true"'
        indexed='' if (malformed and idx==3) else f'data-fvx-search="record-{idx} apollo nasa original archival report"'
        records.append(f'<article data-fvx-record id="r152-record-{idx}" {indexed} {extra}><h2>Record {idx}</h2><p>NASA archival record {idx}, limits of the evidence.</p><a href="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/">Original NASA report</a></article>')
    links=''.join(f'<a href="#r152-record-{i+1}" data-fvx-chrono-link>Find record {i+1}</a>' for i in range(n))
    one='''<section data-fvx-ledger><h1>Research Desk — Apollo 1</h1>
        <nav aria-label="Photograph chronology">''' + links + '''</nav>
        <form role="search" onsubmit="return false"><div data-fvx-tools hidden>
          <label>Find evidence <input data-fvx-search type="search"></label>
          <button data-fvx-clear hidden type="button">Clear search</button>
          <output data-fvx-status role="status" aria-live="polite"></output>
        </div></form><p data-fvx-empty hidden>No matching source records</p>''' + ''.join(records) + '</section>'
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'+CSS+'<body><main>'+one+'</main></body></html>'

def run(out:Path,script:Path=JS):
    if out.exists():raise ValueError('output must not exist')
    code=script.read_text(encoding='utf-8')
    if len(code)<1000:raise ValueError('source JS too short')
    out.mkdir(parents=True)
    result={'schema':'fv.apollo.r152.research-desk-browser.v1','scope':'CONTROLLED_DOM_NOT_WORDPRESS',
        'source_js_sha256':hashlib.sha256(code.encode()).hexdigest(),
        'browser':'CHROMIUM','axe':'NOT_EXECUTED','live_qa':'NOT_EXECUTED',
        'lcp_cls':'NOT_MEASURED','commercial_offer':'NOT_VERIFIED',
        'source_rights':'NASA_LINKS_NOT_MEDIA_LICENSE', 'approved_to_publish':False,
        'checks':[],'screenshots':[]}
    def check(w,name,ok,details=''):
        result['checks'].append({'width':w,'check':name,'pass':bool(ok),'detail':str(details)[:180]})
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path=os.getenv('FV_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
        result['chromium_version']=browser.version
        try:
            for w in WIDTHS:
                ctx=browser.new_context(viewport={'width':w,'height':820},reduced_motion='reduce',has_touch=(w==390))
                ctx.route('**/*',lambda route:route.abort('blockedbyclient'))
                page=ctx.new_page(); errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
                try:
                    page.set_content(fixture(),wait_until='domcontentloaded');page.add_script_tag(content=code)
                    section=page.locator('[data-fvx-ledger]');cards=section.locator('[data-fvx-record]')
                    tool=section.locator('[data-fvx-tools]');search=section.locator('input[data-fvx-search]')
                    check(w,'enhancement_ready',tool.is_visible() and section.get_attribute('data-fvx-initialized')=='yes')
                    search.fill('record-1');check(w,'query_filters',sum(cards.nth(i).is_visible() for i in range(6))==1)
                    # History navigation from an external link must restore hidden record 4.
                    page.evaluate('window.location.hash="#r152-record-4"')
                    page.wait_for_function('document.activeElement.id==="r152-record-4"',timeout=4000)
                    check(w,'hash_restores_hidden_target',all(cards.nth(i).is_visible() for i in range(6)) and search.input_value()=='' and page.evaluate('document.activeElement.id')=='r152-record-4')
                    search.fill('absent-phrase');check(w,'no_matches_status',section.locator('[data-fvx-empty]').is_visible())
                    search.press('Escape');check(w,'escape_restores',search.input_value()=='' and all(cards.nth(i).is_visible() for i in range(6)))
                    search.fill('record-2');section.get_by_role('button',name='Clear search').click()
                    check(w,'clear_restores_and_focuses',search.input_value()=='' and search.evaluate('(e)=>e===document.activeElement'))
                    search.fill('record-3');(section.get_by_role('link',name='Find record 5').tap() if w==390 else section.get_by_role('link',name='Find record 5').click())
                    check(w,'chronology_click_reveals',all(cards.nth(i).is_visible() for i in range(6)))
                    check(w,'no_runtime_error',not errors,';'.join(errors))
                    check(w,'no_horizontal_overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'))
                    filename=f'r152-browser-{w}.png';path=out/filename;page.screenshot(path=str(path),animations='disabled',full_page=True)
                    result['screenshots'].append({'file':filename,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
                except Exception as e:check(w,'browser_exception',False,repr(e))
                finally:ctx.close()
                ctx=browser.new_context(viewport={'width':w,'height':820},java_script_enabled=False)
                ctx.route('**/*',lambda route:route.abort('blockedbyclient'))
                page=ctx.new_page();page.set_content(fixture())
                check(w,'nojs_six_records',page.locator('[data-fvx-record]:visible').count()==6)
                check(w,'nojs_original_source_links',page.locator('[data-fvx-record] a[href*="nasa.gov"]').count()==6)
                check(w,'nojs_tools_hidden',page.locator('[data-fvx-tools]').is_hidden())
                check(w,'nojs_no_overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+2'))
                ctx.close()
            # Malformed source metadata must fail open instead of hiding records.
            ctx=browser.new_context(viewport={'width':390,'height':820});ctx.route('**/*',lambda r:r.abort('blockedbyclient'))
            page=ctx.new_page();page.set_content(fixture(malformed=True));page.add_script_tag(content=code)
            page.locator('input[data-fvx-search]').evaluate('(e)=>{e.value="record-1";e.dispatchEvent(new Event("input",{bubbles:true}))}')
            check(390,'malformed_metadata_fails_open',page.locator('[data-fvx-record]:visible').count()==6 and page.locator('[data-fvx-tools]').is_hidden())
            ctx.close()
        finally:browser.close()
    result['passed']=sum(x['pass'] for x in result['checks']);result['failed']=len(result['checks'])-result['passed']
    result['status']='MODEL_BROWSER_PASS_STAGING_HOLD' if result['failed']==0 else 'MODEL_BROWSER_FAIL_STAGING_HOLD'
    (out/'r152_browser_receipt.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    return result

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--out',type=Path,required=True);a.add_argument('--script',type=Path,default=JS);args=a.parse_args()
    r=run(args.out,args.script);print(json.dumps({k:r[k] for k in ('status','passed','failed','scope')}))
    raise SystemExit(0 if not r['failed'] else 2)
