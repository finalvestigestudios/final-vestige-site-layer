#!/usr/bin/env python3
"""Real Chromium smoke: claims, layout, JS/no-JS, keyboard, reset and failure injection."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
HTML=(ROOT/'index.html').read_text(encoding='utf8')
WIDTHS=(320,360,390,768,1024,1440,1920)
result={'test':'Playwright Chromium set_content; offline, not WordPress','viewports':{},'fail_open':{}}
def check(x,why):
    if not x: raise AssertionError(why)
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for w in WIDTHS:
        page=browser.new_page(viewport={'width':w,'height':900})
        page.set_content(HTML,wait_until='load')
        state=page.evaluate("""() => {
          const style=s=>getComputedStyle(document.querySelector(s));
          return {
            visibleClaims:document.querySelectorAll('[data-ex2-claim-item]:not([hidden])').length,
            overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth+1,
            ledgerCols:style('.ex2-ledger__grid').gridTemplateColumns.split(' ').length,
            caseDisplay:style('.ex2-case__layout').display,
            atlasCols:style('.ex2-atlas__grid').gridTemplateColumns.split(' ').length,
            researchCols:style('.ex2-custody__grid').gridTemplateColumns.split(' ').length
          } }""")
        check(state['visibleClaims']==6 and not state['overflow'],f'missing/overflow {w}: {state}')
        check(state['ledgerCols']==(1 if w<=760 else 2),f'ledger layout {w}: {state}')
        if w<=760:check(state['caseDisplay']=='block',f'mobile chronology {w}: {state}')
        if w>=1440:check(state['caseDisplay']=='grid' and state['atlasCols']==3 and state['researchCols']==3,f'desktop breakpoint regression {w}: {state}')
        if w in (390,1440):
            control=page.locator('#claim-filter')
            for option,count in (('timing',2),('uncertain',1),('response',1)):
                control.select_option(option)
                check(page.locator('[data-ex2-claim-item]:visible').count()==count,f'claim filter {w}/{option}')
            page.locator('[data-ex2-claim-reset]').click()
            check(page.locator('[data-ex2-claim-item]:visible').count()==6,'reset')
            check(page.evaluate('document.activeElement.id')=='claim-filter','focus restore')
            page.locator('#custody-05 summary').focus()
            page.keyboard.press('Enter')
            check(page.locator('#custody-05 details').evaluate('(e)=>e.open'),'keyboard source')
        result['viewports'][str(w)]=state
        page.close()
    page=browser.new_page(viewport={'width':390,'height':900},java_script_enabled=False)
    page.set_content(HTML)
    check(page.locator('[data-ex2-claim-item]:visible').count()==6,'noJS content')
    check(not page.locator('[data-ex2-claim-tools]').is_visible(),'noJS inactive controls')
    page.locator('#custody-04 summary').click()
    check(page.locator('#custody-04 details').evaluate('(e)=>e.open'),'noJS native disclosure')
    result['fail_open']['no_javascript']='pass'
    page.close()
    page=browser.new_page(viewport={'width':390,'height':900})
    page.evaluate("""() => {let original=Element.prototype.addEventListener;Element.prototype.addEventListener=function(type,...args){if(this.matches?.('[data-ex2-claim-filter]'))throw Error('injected');return original.call(this,type,...args)}}""")
    page.set_content(HTML)
    check(page.locator('[data-ex2-claim-item]:visible').count()==6,'injection hides evidence')
    check(not page.locator('[data-ex2-claim-tools]').is_visible(),'failed enhancement controls visible')
    result['fail_open']['exception_injection']='pass'
    page.close()
    browser.close()
(ROOT/'qa'/'CUSTODY_BROWSER_QA.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf8')
print('CLAIM_BROWSER_PASS seven viewports + keyboard/noJS/failure injection')
