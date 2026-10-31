#!/usr/bin/env python3
"""R30 repository-native Apollo release gate. Source-controlled, fail-closed.

Execute on the COMPLETE exact Git checkout. Existing qa.browser_exact.get_fixture()
builds the private PHP candidate with hash-pinned source and a meta-CSP approximation.
This is NOT installed WordPress, HTTP CSP or a production accessibility audit.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from qa.browser_exact import get_fixture, INIT

WIDTHS=(320,360,390,768,1024,1440,1920)


def inspect_dom(page):
    return page.evaluate('''() => {
      let ids=new Map();for(let e of document.querySelectorAll('[id]'))ids.set(e.id,(ids.get(e.id)||0)+1);
      let anchors=[...document.querySelectorAll('a')];
      return {duplicate_ids:[...ids].filter(([,n])=>n!==1),
        missing_anchors:anchors.filter(a=>a.getAttribute('href')?.startsWith('#')&&!document.getElementById(decodeURIComponent(a.hash.slice(1)))).length,
        unnamed_links:anchors.filter(a=>!(a.textContent.trim()||a.getAttribute('aria-label')||a.querySelector('img[alt]'))).length,
        unsafe_links:anchors.filter(a=>a.href.startsWith('http:')||(a.target==='_blank'&&!a.rel.includes('noopener'))).length,
        unlabeled_fields:[...document.querySelectorAll('input,textarea,select')].filter(e=>!e.labels?.length&&!e.getAttribute('aria-label')&&!e.getAttribute('aria-labelledby')).length,
        doc_width:document.documentElement.scrollWidth,viewport_width:document.documentElement.clientWidth,
        nasa_records:document.querySelectorAll('#source-concordance [data-concordance-record]').length,
        catalog_holds:document.querySelectorAll('[data-crosswalk-review="hold"]').length,
        rights_holds:document.querySelectorAll('[data-media-hold="true"]').length,
        geo_pins:document.querySelectorAll('#atlas [data-lat],#atlas [data-lon]').length};
    }''')


def enforce(a):
    if (a['duplicate_ids'] or a['missing_anchors'] or a['unnamed_links'] or a['unsafe_links']
        or a['unlabeled_fields'] or a['geo_pins'] or a['doc_width']>a['viewport_width']+1
        or (a['nasa_records'],a['catalog_holds'],a['rights_holds'])!=(6,1,6)):
        raise RuntimeError('Apollo source, rights, navigation or accessibility contract failure: '+str(a))


def run(out,chromium,axe_path=None,axe_sha256=None):
    if bool(axe_path)!=bool(axe_sha256): raise ValueError('axe JS and pinned SHA must be supplied together')
    axe=None
    if axe_path:
        axe=Path(axe_path).read_bytes()
        if sha256(axe).hexdigest()!=axe_sha256 or len(axe)<100000:
            raise ValueError('axe-core pin mismatch / invalid bundle')
    html,plugin_sha=get_fixture()  # Reuses source-pinned PHP compiler, not a duplicate fixture.
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    receipts=[];screens=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=chromium,headless=True,args=['--no-sandbox'])
        for width in WIDTHS:
            ctx=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce' if width in (320,390) else 'no-preference')
            page=ctx.new_page();errors=[];requests=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda r:requests.append(r.url))
            page.add_init_script(INIT)
            page.set_content(html,wait_until='load')
            page.evaluate(INIT)
            a=inspect_dom(page);enforce(a)
            if errors or requests:raise RuntimeError(f'{width}px JS/network error {errors} {requests}')
            s=page.locator('#fv-ex2-research-desk-crosswalk>summary');s.focus();page.keyboard.press('Enter')
            if not page.locator('#fv-ex2-research-desk-crosswalk').evaluate('(e)=>e.open'):
                raise RuntimeError('native keyboard disclosure did not open')
            nested=page.locator('#fv-ex2-catalog-identity summary');nested.focus();page.keyboard.press('Enter')
            if not page.locator('#fv-ex2-catalog-identity details').evaluate('(e)=>e.open'):
                raise RuntimeError('nested keyboard disclosure did not open')
            if not page.locator('[data-secondary-source-status="not-first-party"]').is_visible():
                raise RuntimeError('disputed NASA identity warning not visible')
            axe_receipt=None
            if axe:
                nonce=page.locator('style[nonce]').first.get_attribute('nonce')
                if not nonce:raise RuntimeError('no CSP nonce for pinned axe injection')
                page.evaluate('''({js,nonce})=>{let s=document.createElement('script');s.setAttribute('nonce',nonce);
                    s.textContent=js;document.head.append(s)}''',{'js':axe.decode('utf8'),'nonce':nonce})
                axe_receipt=page.evaluate('''async()=>{if(!window.axe?.run)throw Error('axe missing');
                  let r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                  return {engine:r.testEngine.version,violations:r.violations.map(v=>({id:v.id,impact:v.impact,count:v.nodes.length}))}}''')
                if axe_receipt['violations']:raise RuntimeError('axe violations: '+str(axe_receipt))
            if width in (390,1440):
                path=out/f'r30-research-identity-{width}.png'
                page.locator('#fv-ex2-catalog-identity').screenshot(path=str(path),animations='disabled')
                screens.append({'name':path.name,'sha256':sha256(path.read_bytes()).hexdigest()})
            perf=page.evaluate('''()=>window.__fv_cwv||null''')
            receipts.append({'width':width,'dom':a,'keyboard':'PASS','axe':axe_receipt,
                             'laboratory_observation_only':perf,'errors':errors})
            ctx.close()
        ctx=browser.new_context(viewport={'width':390,'height':850},java_script_enabled=False)
        page=ctx.new_page();page.set_content(html)
        page.locator('#fv-ex2-research-desk-crosswalk>summary').click()
        page.locator('#fv-ex2-catalog-identity summary').click()
        enforce(inspect_dom(page))
        if not page.locator('[data-secondary-source-status="not-first-party"]').is_visible():
            raise RuntimeError('no-JS evidence missing')
        ctx.close()
        ctx=browser.new_context(viewport={'width':390,'height':850},has_touch=True,is_mobile=True)
        page=ctx.new_page();page.set_content(html)
        page.locator('#fv-ex2-research-desk-crosswalk>summary').tap()
        if not page.locator('#fv-ex2-research-desk-crosswalk').evaluate('(e)=>e.open'):
            raise RuntimeError('touch evidence disclosure failed')
        ctx.close();browser.close()
    report={'status':'LOCAL_BROWSER_PASS_RELEASE_HOLD','source_php_sha256':plugin_sha,
        'scope':'source-pinned PHP CLI + Playwright set_content, not actual WordPress or HTTP CSP',
        'axe_status':'VERIFIED_EXECUTION' if axe else 'BLOCKED_NO_PINNED_LOCAL_AXE',
        'field_cwv':'NOT_MEASURED','independent_qd':'OUTSTANDING','widths':WIDTHS,
        'checks':receipts,'screenshots':screens,'no_js':'PASS','touch':'PASS'}
    (out/'R30_REPO_BROWSER_RECEIPT.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--out',required=True)
    p.add_argument('--chromium',default='/usr/bin/chromium')
    p.add_argument('--axe-js')
    p.add_argument('--axe-sha256')
    a=p.parse_args();x=run(a.out,a.chromium,a.axe_js,a.axe_sha256)
    print('R30',len(x['checks']),'Chromium widths PASS; no-JS/touch PASS;',x['axe_status'],'RELEASE HOLD')
