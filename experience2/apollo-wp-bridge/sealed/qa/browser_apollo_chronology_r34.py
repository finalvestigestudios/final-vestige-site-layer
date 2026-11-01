#!/usr/bin/env python3
"""Run real Chromium with JS on/off and optional separately acquired axe-core. No hosted claims.

Without --axe-js, axe status is BLOCKED_NO_AXE_CORE, never PASS.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS=[320,360,390,768,1024,1440,1920]

def digest(p):return sha256(p.read_bytes()).hexdigest()

def audit(html_path:Path, screenshots:Path, receipt:Path, axe_js:Path|None=None):
    page_html=html_path.read_text()
    if axe_js is not None:
        if not axe_js.exists() or 'axe.version' not in axe_js.read_text(errors='replace'):
            raise RuntimeError('axe-core engine missing or invalid; refusing false PASS')
    screenshots.mkdir(parents=True,exist_ok=True)
    checks=[]; violations=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in WIDTHS:
            for js_enabled in [False,True]:
                context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js_enabled,
                    reduced_motion='reduce',has_touch=(width<=390),is_mobile=(width<=390))
                page=context.new_page(); errors=[]; requests=[]
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.on('request',lambda r:requests.append(r.url))
                page.set_content(page_html,wait_until='load')
                assert not requests and not errors,(requests,errors)
                info=page.evaluate('''() => ({client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,
                  cards:document.querySelectorAll('#apollo-r34-records>article').length,
                  visible:[...document.querySelectorAll('#apollo-r34-records>article')].filter(x=>!x.hidden).length,
                  images:document.querySelectorAll('img').length, scripts:document.querySelectorAll('script').length,
                  atlasPositions:document.querySelectorAll('[data-lat],[data-lon],[data-map-edge]').length,
                  controlsHidden:document.querySelector('[data-r34-controls]').hidden,
                  reduced:matchMedia('(prefers-reduced-motion: reduce)').matches,
                  monthDate:document.querySelector('#catalog-01').dataset.photoDate,
                  monthPrecision:document.querySelector('#catalog-01').dataset.datePrecision})''')
                assert info['cards']==6 and info['visible']==6 and info['images']==0 and info['scripts']==1 and info['atlasPositions']==0,info
                assert info['scroll']<=info['client']+1,info
                assert (info['monthDate'],info['monthPrecision'])==('1967-01','month') and info['reduced'],info
                assert info['controlsHidden']==(not js_enabled),info
                source=page.locator('#catalog-03 details summary').first
                source.scroll_into_view_if_needed();source.focus();page.keyboard.press('Enter')
                assert page.locator('#catalog-03 details').first.evaluate('(x)=>x.open')
                source.click()
                assert not page.locator('#catalog-03 details').first.evaluate('(x)=>x.open')
                if js_enabled:
                    for period,count in [('1966',1),('1967',3),('2017',2),('all',6)]:
                        button=page.locator('[data-r34-year="'+period+'"]')
                        button.scroll_into_view_if_needed()
                        if width<=390: button.tap()
                        else: button.focus();page.keyboard.press('Space')
                        actual=page.locator('#apollo-r34-records > article:visible').count()
                        assert actual==count,(width,period,actual)
                        assert button.get_attribute('aria-pressed')=='true'
                        assert page.locator('[data-r34-status]').inner_text().find(str(count))>=0
                    if axe_js:
                        page.add_script_tag(path=str(axe_js))
                        result=page.evaluate('''async () => { const r=await axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}}); return {version:axe.version, violations:r.violations.map(v=>({id:v.id,impact:v.impact,targets:v.nodes.map(n=>n.target)})),incomplete:r.incomplete.length}; }''')
                        violations += [{'width':width,**v} for v in result['violations']]
                        info['axe_version']=result['version'];info['axe_incomplete']=result['incomplete']
                if width in (390,1440):
                    path=screenshots/f"r34-chronology-{width}-{'enhanced' if js_enabled else 'nojs'}.png"
                    page.screenshot(path=str(path),full_page=True,animations='disabled')
                    info['screenshot_sha256']=digest(path)
                info.update({'viewport':width,'javascript_enabled':js_enabled,'status':'PASS'})
                checks.append(info)
                context.close()
        # Deliberately abort listener installation to prove fail-open behavior.
        fail_context=browser.new_context(viewport={'width':390,'height':900})
        fail_page=fail_context.new_page()
        import re
        clean=re.sub(r'<script data-r34-enhancement="">.*?</script>', '', page_html, flags=re.S)
        if clean == page_html: raise AssertionError('could not isolate progressive enhancement')
        fail_page.set_content(clean,wait_until='load')
        fail_page.evaluate('''() => { const prev=Element.prototype.addEventListener; let n=0; Element.prototype.addEventListener=function(...args){ if(this.matches && this.matches('[data-r34-year]') && ++n===2)throw Error('simulated failure');return prev.apply(this,args); }; }''')
        fail_page.add_script_tag(content=page_html.split('<script data-r34-enhancement="">')[1].split('</script>')[0])
        fail_open=fail_page.evaluate('''() => ({hidden:document.querySelector('[data-r34-controls]').hidden,visible:[...document.querySelectorAll('#apollo-r34-records>article')].filter(x=>!x.hidden).length})''')
        assert fail_open=={'hidden':True,'visible':6},fail_open
        fail_context.close()
        browser.close()
    if violations:
        raise AssertionError('Real axe-core WCAG violations: '+json.dumps(violations))
    result={'release':'HOLD','browser':'Chromium','browser_modes':len(checks),'cases':checks,
       'axe_status':'PASS_NO_DETECTED_VIOLATIONS' if axe_js else 'BLOCKED_NO_AXE_CORE',
       'axe_violations':violations,'real_wordpress':'NOT_TESTED','real_http_csp':'NOT_TESTED',
       'LCP':'NOT_MEASURED_AT_HOSTED_URL','CLS':'NOT_MEASURED_AT_HOSTED_URL',
       'historical_context':'NASA photograph dates; not an Apollo 204 telemetry chronology',
       'simulated_enhancement_failure':'PASS_CONTROLS_HIDDEN_SIX_RECORDS_VISIBLE'}
    receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--html',required=True,type=Path);p.add_argument('--screenshots',required=True,type=Path);p.add_argument('--receipt',required=True,type=Path);p.add_argument('--axe-js',type=Path)
    a=p.parse_args();r=audit(a.html,a.screenshots,a.receipt,a.axe_js)
    print(json.dumps({'browser_cases':r['browser_modes'],'axe':r['axe_status'],'release':r['release']}))
