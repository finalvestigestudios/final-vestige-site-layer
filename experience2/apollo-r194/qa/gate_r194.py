#!/usr/bin/env python3
"""R194: offline PHP output + real Chromium/Playwright isolated staging gate.

This is NOT installed WordPress or axe. Browser top-frame navigation is
restricted by the runner; CTA click-target behavior is verified without
claiming external navigation, sales, consent, or production CWV.
"""
from __future__ import annotations
import hashlib,json,subprocess,sys,tempfile,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r194 import build,sha

WIDTHS=[320,360,390,768,1440,1920]
CASES=[(str(w),w,False,False,False) for w in WIDTHS]+[
 ('390-nojs',390,True,False,False),('390-reduced',390,False,True,False),
 ('390-forced',390,False,False,True),('390-touch',390,False,False,False)]
DEST='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
NASA='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'

def render(plugin_dir,mode='normal'):
    cmd=['php',str(ROOT/'dist/wp-render-shim-r194.php'),str(plugin_dir/'fv-ex2-apollo-r194.php'),mode]
    return json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)

def run(out):
    out.mkdir(parents=True,exist_ok=True)
    manifest=build();dist=ROOT/'dist'
    for name,digest in manifest['files'].items():assert sha((dist/name).read_bytes())==digest,name
    good=render(dist)
    assert not good['fallback'] and good['chronology']==4 and good['details']==8
    assert good['css']=='enqueued' and good['js']
    assert not render(dist,'printed')['fallback']
    assert render(dist,'late')['fallback']
    with tempfile.TemporaryDirectory(prefix='apollo-r194-negative-') as td:
        scratch=Path(td)
        shutil.copytree(dist,scratch/'plugin')
        js=scratch/'plugin/assets/campaign-handoff.js'
        js.write_text(js.read_text()+'\n/* tampered test asset */')
        result=render(scratch/'plugin')
        assert not result['fallback'] and not result['js'] and result['details']==8, 'JS must fail open'
        html=scratch/'plugin/templates/atlas-fragment.html'
        html.write_text(html.read_text()+'\n<!-- tamper -->')
        assert render(scratch/'plugin')['fallback'], 'HTML tamper must fail closed to free investigation'
    html=good['html'];css=(dist/'assets/atlas-scoped.css').read_text()
    assert html.count('fv-apollo-source-boundary')==1
    assert html.count(DEST)==1 and html.count('class="cta"')==1
    assert html.count(NASA)>=6 and html.count('<details>')==8
    assert 'not a checkout' in html and 'cannot prove the ignition source' in html
    assert 'NASA photograph catalog entries' in html
    assert not any(s in html.lower() for s in ('add to cart','buy now','limited time offer','nasa approved'))
    r={'release':'R194','mode':'offline PHP shim and actual Chromium Playwright fixture',
       'source_sha256':manifest['files'],'contexts':[],'negative_controls':'optional JS tamper fail-open; core HTML tamper fallback; late shortcode fallback',
       'browser_assertions_per_run':0,'limitations':['not installed WordPress/Gutenberg or external browser navigation',
             'not genuine axe-core or screen-reader acceptance','no real-user Core Web Vitals, qualified human sessions, buyers, sales or attribution']}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for name,width,nojs,reduced,forced in CASES:
            ctx=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,
                 java_script_enabled=not nojs,reduced_motion='reduce' if reduced else 'no-preference',
                 forced_colors='active' if forced else 'none',has_touch=name=='390-touch',is_mobile=name=='390-touch')
            page=ctx.new_page();errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>',wait_until='load')
            assert page.locator('.fv-apollo-atlas').count()==1
            assert page.locator('.fv-apollo-atlas a.cta').count()==1
            assert page.locator('.fv-apollo-atlas a.cta').get_attribute('href')==DEST
            assert page.locator('.fv-apollo-source-boundary a').get_attribute('href')==NASA
            assert page.locator('.fv-apollo-atlas details').count()==8
            assert page.get_by_role('region').count()==5
            assert not page.evaluate('document.documentElement.scrollWidth > innerWidth + 1'),name
            assert page.locator('.fv-apollo-print-custody li').count()==8
            # Keyboard-operable source disclosure and on-page citations.
            details=page.locator('.fv-apollo-atlas details').first
            summary=details.locator('summary')
            summary.focus();page.keyboard.press('Enter')
            assert details.get_attribute('open') is not None
            assert details.get_by_role('link').count()>=1
            summary.click();assert details.get_attribute('open') is None
            assert page.get_by_role('heading',name='Continue into the full investigation.').count()==1
            if reduced: assert page.locator('.fv-apollo-atlas').evaluate('e=>getComputedStyle(e).scrollBehavior')=='auto'
            if forced: assert page.locator('.fv-apollo-source-boundary').is_visible()
            assert not errors,errors
            screenshot=out/(name+'.png');page.screenshot(path=str(screenshot),full_page=True,animations='disabled')
            r['contexts'].append({'name':name,'width':width,'screenshot_sha256':sha(screenshot.read_bytes()),
                                  'horizontal_overflow':False,'keyboard_pointer_details':'pass','free_cta':DEST})
            r['browser_assertions_per_run']+=12
            ctx.close()
        browser.close()
    (out/'receipt.json').write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':'PASS','cases':len(CASES),'assertions_per_run':r['browser_assertions_per_run'],'receipt':str(out/'receipt.json')},indent=2))
    return r
if __name__=='__main__':run(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'evidence')
