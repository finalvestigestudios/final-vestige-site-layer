#!/usr/bin/env python3
"""R232 browser behavior gate: synthetic DOM, exact standalone R232 JS. NOT WordPress/exact NASA template QA."""
import argparse, hashlib, json, re
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS=(320,390,768,1440,1920)
SOURCE='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
CTA='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

# A static fixture with the R231 selection/control contract. This is deliberately
# NOT presented as NASA template or WordPress installation acceptance.
def fixture():
    cards=[]
    for i in range(1,7):
        specific='NASA S66-58038 documents altitude-chamber training, not telemetry.' if i==3 else ('The oxygen pressure finding is established by the Review Board.' if i==2 else 'Historical record with open limitations.')
        cards.append(f'''<article data-fvx-record id="evidence-{i}"><h2>Evidence {i}</h2>
          <p>Visible summary for record {i}.</p><details><summary>Review underlying finding</summary>
          <p>{specific} Instrument chronology is an interpretation, not photographic proof.</p></details>
          <a href="{SOURCE}" rel="noopener noreferrer" target="_blank">Read NASA source {i}</a></article>''')
    return '''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>body{font:16px system-ui;margin:0;color:#eee;background:#151515}section{max-width:65rem;padding:1rem;margin:auto}
    article{border:1px solid #ccc;padding:1rem;margin:1rem 0}a,summary,input{min-height:44px;display:inline-flex;align-items:center;color:#ffdfaa}
    input{color:#111;background:#fff;min-width:0;max-width:100%;width:100%}article[hidden],[hidden]{display:none!important}
    :focus-visible{outline:3px solid #fff;outline-offset:2px}</style></head><body><section data-fvx-ledger>
    <h1>Apollo 1 Research Desk</h1><div data-fvx-tools hidden><label for="query">Search sources</label>
    <input id="query" type="search" data-fvx-search aria-controls="records"><span role="status" aria-live="polite" data-fvx-status></span></div>
    <div id="records">'''+''.join(cards)+f'''</div><p data-fvx-empty hidden>No records match.</p>
    <a href="{CTA}">Read original investigation</a></section></body></html>'''

def checksum(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def run(out, js_path):
    out.mkdir(parents=True,exist_ok=True)
    script=js_path.read_text()
    results=[]; hashes={}; failures=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        version=browser.version
        for width in WIDTHS:
            for js in (False,True):
                context=browser.new_context(viewport={'width':width,'height':820},java_script_enabled=js,
                    has_touch=width<=390,is_mobile=width<=390,
                    reduced_motion='reduce' if width==320 else 'no-preference',
                    forced_colors='active' if width==768 else 'none')
                page=context.new_page(); requests=[];page.on('request',lambda r: requests.append(r.url))
                page.set_content(fixture());
                if js: page.add_script_tag(content=script)
                assert page.locator('[data-fvx-record]').count()==6
                assert page.locator('a[href="'+CTA+'"]').count()==1
                assert not requests,requests
                assert page.locator('[data-fvx-record]:visible').count()==6
                if js:
                    assert page.locator('[data-fvx-tools]').is_visible()
                    assert page.locator('[data-fvx-status]').inner_text()=='6 of 6 evidence records'
                    query=page.locator('[data-fvx-search]')
                    # Multi-token search (AND), spelling-neutral accent normalization.
                    query.fill('ALTITUDE-CHAMBER telemetry')
                    assert page.locator('[data-fvx-record]:visible').count()==1
                    assert page.locator('#evidence-3 details').evaluate('(x)=>x.open')
                    assert page.locator('[data-fvx-status]').inner_text()=='1 of 6 evidence records'
                    query.fill('unknown-term')
                    assert page.locator('[data-fvx-record]:visible').count()==0
                    assert page.locator('[data-fvx-empty]').is_visible()
                    query.fill('')
                    assert page.locator('[data-fvx-record]:visible').count()==6
                    assert not page.locator('#evidence-3 details').evaluate('(x)=>x.open')
                    assert not page.locator('[data-fvx-empty]').is_visible()
                else:
                    assert not page.locator('[data-fvx-tools]').is_visible()
                    assert page.locator('[data-fvx-record]:visible').count()==6
                summary=page.locator('#evidence-1 summary')
                if width<=390: summary.tap()
                else: summary.focus();page.keyboard.press('Enter')
                assert page.locator('#evidence-1 details').evaluate('(x)=>x.open')
                state=page.evaluate('''() => ({width:innerWidth,overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
                duplicates:[...document.querySelectorAll('[id]')].map(x=>x.id).filter((id,i,a)=>a.indexOf(id)!==i).length,
                sourceLinks:[...document.querySelectorAll('a[href*="nasa.gov"]')].length})''')
                assert state['overflow']<=1,state
                assert state['duplicates']==0,state
                assert state['sourceLinks']==6,state
                shot=out/f'{width}-{"js" if js else "nojs"}.png'
                page.screenshot(path=str(shot),full_page=True,animations='disabled')
                hashes[shot.name]=checksum(shot)
                results.append({'width':width,'js':js,'state':state})
                context.close()
        browser.close()
    receipt={'status':'PASS_SYNTHETIC_JS_CONTRACT','scope':'R232 exact JS on synthetic six-card DOM, not NASA full HTML or WordPress',
       'chromium':version,'source_sha256':hashlib.sha256(script.encode()).hexdigest(),
       'contexts':results,'screenshots':hashes,'axe':'NOT_EXECUTED','LCP_CLS':'NOT_MEASURED','release':'STAGING_HOLD'}
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print('PASS: ',len(results),'Chromium fixtures. Receipt:',checksum(out/'receipt.json'))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--js',type=Path,required=True)
    a=ap.parse_args();run(a.out,a.js)
