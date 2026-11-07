#!/usr/bin/env python3
"""R195 real Chromium keyboard/reflow gate on PHP-rendered WordPress-function fixture.

NOT installed WordPress, genuine axe-core, assistive-technology testing or
production performance. No external navigation, cookies, merchants or writes.
"""
import json, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from build_r195 import build, sha, TARGETS
WIDTHS = (320, 360, 390, 768, 1440, 1920)
CASES = [(str(w),w,False,False,False,False,False) for w in WIDTHS] + [
    ('390-nojs',390,True,False,False,False,False),
    ('390-reduced',390,False,True,False,False,False),
    ('390-forced',390,False,False,True,False,False),
    ('390-touch',390,False,False,False,True,False),
    ('320-zoom200',320,False,False,False,False,True),
    ('390-zoom200',390,False,False,False,False,True)]
NASA = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
DEST = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def render(dist, mode='normal'):
    return json.loads(subprocess.check_output([
        'php',str(dist/'wp-render-shim-r195.php'),str(dist/'fv-ex2-apollo-r195.php'),mode],text=True))

def run(out):
    out.mkdir(parents=True,exist_ok=True)
    m=build(); dist=ROOT/'dist'
    assert all(sha((dist/n).read_bytes())==d for n,d in m['files'].items())
    subprocess.run(['php','-l',str(dist/'fv-ex2-apollo-r195.php')],check=True,capture_output=True)
    base=render(dist)
    assert not base['fallback'] and base['chronology']==4 and base['details']==8
    assert render(dist,'late')['fallback'] and not render(dist,'printed')['fallback']
    html=base['html'];css=(dist/'assets/atlas-scoped.css').read_text()
    assert html.count('class="cta"')==1 and html.count(DEST)==1
    assert html.count('<details>')==8 and html.count('<time datetime=')==4
    assert 'not a checkout' in html and NASA in html
    receipt={'release':'R195','test':'Actual PHP shim output in real Chromium/Playwright; no installed WordPress',
        'build_files':m['files'],'cases':[],'assertions_per_run':0,
        'limits':['No genuine axe-core, assistive technology or deployed WordPress staging',
          'CSS zoom simulation is not actual browser zoom',
          'Offline LCP/CLS cannot certify live Core Web Vitals',
          'No verified paid orders, lead confirmations, qualified sessions or Grok asset']}
    with sync_playwright() as pw:
        b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for name,width,nojs,reduced,forced,touch,zoom in CASES:
            ctx=b.new_context(viewport={'width':width,'height':900},device_scale_factor=1,
                 java_script_enabled=not nojs,has_touch=touch,is_mobile=touch,
                 reduced_motion='reduce' if reduced else 'no-preference',
                 forced_colors='active' if forced else 'none')
            page=ctx.new_page();errors=[]
            page.on('pageerror',lambda err:errors.append(str(err)))
            page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>',wait_until='load')
            if zoom: page.evaluate("document.documentElement.style.zoom='2'")
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),name
            assert page.get_by_role('region').count()==5
            assert page.locator('.fv-apollo-atlas details').count()==8
            assert page.locator('.fv-apollo-print-custody li').count()==8
            assert page.locator('.fv-apollo-atlas a.cta').get_attribute('href')==DEST
            assert page.locator('.fv-apollo-source-boundary a').get_attribute('href')==NASA
            # Eight native same-page link journeys must focus their target, not BODY.
            for target in TARGETS:
                link=page.locator('a[href="#'+target+'"]').first
                assert link.count()==1 and page.locator('#'+target).count()==1
                link.focus();page.keyboard.press('Enter')
                assert page.evaluate('document.activeElement.id')==target,(name,target)
                assert page.evaluate('location.hash')=='#'+target,(name,target)
                assert page.locator('#'+target).get_attribute('tabindex')=='-1'
            # Still a single keyboard tab stop for the main CTA; -1 does not
            # inject eight extra sequential stops.
            assert page.locator('.fv-apollo-atlas [tabindex="0"]').count()==0
            first=page.locator('.fv-apollo-atlas details').first
            first.locator('summary').focus();page.keyboard.press('Enter')
            assert first.get_attribute('open') is not None
            first.locator('summary').click();assert first.get_attribute('open') is None
            if reduced:
                assert page.locator('.fv-apollo-atlas').evaluate('e=>getComputedStyle(e).scrollBehavior')=='auto'
            if touch: page.locator('.fv-apollo-atlas details').nth(1).locator('summary').tap()
            assert not errors,errors
            img=out/(name+'.png');page.screenshot(path=str(img),full_page=True,animations='disabled')
            receipt['cases'].append({'name':name,'width':width,'javascript':not nojs,
               'css_zoom_200':zoom,'hash':sha(img.read_bytes()),'focus_targets':len(TARGETS),
               'overflow':False})
            receipt['assertions_per_run']+=45
            ctx.close()
        b.close()
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':'PASS','cases':len(CASES),'focus_trials':len(CASES)*len(TARGETS),
                      'assertions_per_run':receipt['assertions_per_run']}))
    return receipt

if __name__=='__main__':
    run(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'evidence')
