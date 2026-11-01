"""R39 Chromium QA against the actual deterministic Atlas build, not synthetic records.

No server navigation: Chromium in some environments blocks localhost requests.
As a result these results are NOT HTTP CSP, WordPress integration, field CWV or
axe/screen-reader acceptance. Optional --axe uses an existing, approved bundle.
"""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
import build_atlas

WIDTHS=(320,360,390,768,1024,1440,1920)

def require(cond,msg):
    if not cond: raise AssertionError(msg)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output',type=Path,required=True)
    ap.add_argument('--axe',type=Path,help='Preinstalled approved pinned axe-core, not fetched at runtime')
    args=ap.parse_args()
    if args.axe:require(args.axe.is_file(),'axe-core bundle missing')
    out=args.output;out.mkdir(parents=True,exist_ok=True)
    manifest=build_atlas.build(out)
    document=(out/'apollo-evidence-atlas.html').read_text(encoding='utf8')
    screenshots=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for js in (False,True):
            for width in WIDTHS:
                context=browser.new_context(viewport={'width':width,'height':900},
                   is_mobile=width<500,has_touch=width<500,java_script_enabled=js,
                   reduced_motion='reduce')
                page=context.new_page()
                requests=[];errors=[]
                page.on('request',lambda req:requests.append(req.url))
                page.on('pageerror',lambda e:errors.append(str(e)))
                page.set_content(document,wait_until='load')
                label=f'width={width}, js={js}: '
                require(not requests,label+'unexpected network request: '+str(requests))
                require(not errors,label+'JS exception: '+str(errors))
                cards=page.locator('[data-fva-record]')
                require(cards.count()==6,label+'missing NASA records')
                require(page.locator('[data-fva-record]:visible').count()==6,label+'evidence missing at initial render')
                require(page.locator('[data-fva-drawer]').count()==6,label+'source drawer missing')
                require(page.locator('img, picture, iframe, canvas, svg, video').count()==0,label+'media leakage')
                require(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 2'),label+'overflow')
                require(page.evaluate('''() => {const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);return ids.length===new Set(ids).size;}'''),label+'duplicate IDs')
                drawer=page.locator('[data-fva-drawer]').first
                drawer.locator('summary').focus()
                drawer.locator('summary').press('Enter')
                require(drawer.get_attribute('open') is not None,label+'keyboard disclosure failed')
                if js:
                    controls=page.locator('[data-fva-controls]')
                    require(controls.is_visible(),label+'enhancement unavailable')
                    b1967=page.locator('[data-fva-filter="1967"]')
                    require(b1967.evaluate('el => el.getBoundingClientRect().height')>=44,label+'button too small')
                    (b1967.tap() if width<500 else b1967.click())
                    require(page.locator('[data-fva-record]:visible').count()==3,label+'1967 photo count invalid')
                    require(b1967.get_attribute('aria-pressed')=='true',label+'filter state incorrect')
                    b2017=page.locator('[data-fva-filter="2017"]')
                    (b2017.tap() if width<500 else b2017.click())
                    require(page.locator('[data-fva-record]:visible').count()==2,label+'2017 exhibit count invalid')
                    input=page.locator('[data-fva-search]')
                    input.fill('kim shiflett')
                    require(page.locator('[data-fva-record]:visible').count()==2,label+'source credit search missing')
                    input.press('Escape')
                    require(page.locator('[data-fva-record]:visible').count()==6,label+'Escape fail-open reset')
                    input.fill('impossible unique token')
                    require(page.locator('[data-fva-record]:visible').count()==0,label+'search did not filter')
                    require(page.locator('[data-fva-empty]').is_visible(),label+'no search-empty notice')
                    reset=page.locator('[data-fva-reset]')
                    (reset.tap() if width<500 else reset.click())
                    require(page.locator('[data-fva-record]:visible').count()==6,label+'reset failed')
                    require(page.evaluate("document.activeElement.matches('[data-fva-search]')"),label+'focus not returned')
                else:
                    require(not page.locator('[data-fva-controls]').is_visible(),label+'noJS controls shown')
                    require(page.locator('[data-fva-record]:visible').count()==6,label+'noJS content hidden')
                if args.axe:
                    page.add_script_tag(content=args.axe.read_text(encoding='utf8'))
                    violations=page.evaluate('''async () => (await axe.run(document.querySelector('main'),
                       {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))''')
                    require(not violations,label+'axe violations: '+str(violations))
                page.evaluate('document.activeElement && document.activeElement.blur()')
                page.mouse.move(1,1)
                if width<500 and js:page.locator('h1').tap()
                page.evaluate('window.scrollTo(0,0)')
                shot=out/f'r39-atlas-{width}-{"js" if js else "nojs"}.png'
                page.screenshot(path=str(shot),full_page=True,animations='disabled')
                screenshots.append({'width':width,'javascript':js,'passed':True,'screenshot':shot.name,'sha256':sha(shot)})
                if js:
                    # Verify failure AFTER screenshot, so the screenshot documents
                    # the enhanced filter controls, not only the fallback state.
                    cards.nth(1).evaluate('el => el.removeAttribute("data-fva-id")')
                    input.fill('malformed')
                    require(page.locator('[data-fva-record]:visible').count()==6,label+'malformed record left evidence hidden')
                    require(not controls.is_visible(),label+'failed filter not disabled')
                context.close()
        version=browser.version
        browser.close()
    receipt={'schema':'fv.ex2.apollo.atlas.browser.r39.v1','source_kind':'ACTUAL_R37_CUSTODY_ATLAS_BUILD',
         'release':'STAGING_HOLD','chromium':version,'screenshots':screenshots,'source':manifest,
         'axe':'EXECUTED' if args.axe else 'BLOCKED_NO_APPROVED_AXE_BUNDLE',
         'CSP_HTTP':'NOT_TESTED_SET_CONTENT','authentic_WordPress':'NOT_TESTED',
         'LCP':'NOT_MEASURED_AS_HOSTED_NAVIGATION','CLS':'NOT_MEASURED_AS_HOSTED_NAVIGATION',
         'INP':'NOT_MEASURED','Safari_screenreader':'NOT_TESTED',
         'evidence_counts':'14/14 browser modes passed'}
    (out/'r39-browser-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf8',newline='\n')
    print('R39 14/14 Chromium real-build scenarios PASS; axe/WordPress/hosted CWV: HOLD')
    return receipt

if __name__=='__main__':main()
