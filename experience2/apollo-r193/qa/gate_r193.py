#!/usr/bin/env python3
"""Apollo R193 isolated, real Chromium/Playwright accessibility custody gate.
No outbound requests, WordPress writes, paid service or unreviewed deployment.
Tests PHP-generated shortcode content under a clearly identified WP-function shim;
this is NOT an installed-site test nor axe-core/assistive-technology certification.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
R191 = ROOT.parent/'apollo-r191'
sys.path.insert(0,str(ROOT))
from build_r193 import build, EXPECTED

EXPECTED_LABELS = [value for _,value in EXPECTED]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def get_php_html():
    original_shim=(R191/'qa/wp_render_shim.php').read_text()
    # The parent shim is test-only: derive an R193 copy in memory without
    # mutating the independent Research Desk or R191/R192 source trees.
    shim=original_shim.replace('r191','r193').replace('R191','R193')
    shim_path=ROOT/'dist/wp-render-shim-r193.php'
    shim_path.write_text(shim)
    result=subprocess.run(['php',str(shim_path),str(ROOT/'dist/fv-ex2-apollo-r193.php'),'normal'],capture_output=True,text=True,check=True)
    loaded=json.loads(result.stdout)
    assert not loaded['fallback'] and loaded['chronology']==4 and loaded['details']==8 and loaded['js']
    return loaded['html']

def verify_browser(out: Path):
    out.mkdir(parents=True,exist_ok=True)
    manifest=build()
    assert manifest['printed_source_count']==8
    html=get_php_html()
    legacy=(R191/'dist/templates/atlas-fragment.html').read_text()
    css=(ROOT/'dist/assets/atlas-scoped.css').read_text()
    # Mutation control: old source disclosure labels are not uniquely named.
    assert legacy.count('<summary>Examine source custody</summary>')==4
    assert legacy.count('<summary>Open source details</summary>')==4
    assert [value for _,value in EXPECTED]==EXPECTED_LABELS
    assert all(html.count('<summary>'+value+'</summary>')==1 for value in EXPECTED_LABELS)
    assert html.count('https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/')==1
    assert html.count('<time datetime=')==4
    assert 'No conclusively identified ignition source' in html
    assert 'not certified for commercial promotion' in html
    assert 'Read original investigation' in html
    assert 'fv-apollo-print-custody' in html
    receipt={'release':'R193','source_sha256':manifest['files'],'contexts':[],'notes':[], 'assertions':0}
    target_contexts=[('320',320,False,False,False),('360',360,False,False,False),('390',390,False,False,False),('768',768,False,False,False),('1440',1440,False,False,False),('1920',1920,False,False,False),('390-nojs',390,False,False,True),('390-reduced',390,True,False,False),('390-forced',390,False,True,False)]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for name,width,reduced,forced,nojs in target_contexts:
            context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=not nojs,reduced_motion='reduce' if reduced else 'no-preference',forced_colors='active' if forced else 'none',device_scale_factor=1)
            page=context.new_page()
            errors=[]
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>',wait_until='load')
            page.locator('.fv-apollo-atlas').wait_for()
            found=[v.strip() for v in page.locator('.fv-apollo-atlas summary').all_text_contents()]
            assert found==EXPECTED_LABELS,(name,found)
            assert page.get_by_role('region').count()==5
            assert page.get_by_role('heading',level=1).count()==1
            assert page.locator('.fv-apollo-atlas details').count()==8
            assert page.locator('.fv-apollo-atlas a.cta').count()==1
            assert page.locator('.fv-apollo-atlas .fv-apollo-print-custody li').count()==8
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth + 1'),name
            # The native summaries are keyboard-and-pointer operable
            # disclosure buttons, not visual-only toggles.
            for idx,value in enumerate(EXPECTED_LABELS):
                summary=page.locator('.fv-apollo-atlas summary').nth(idx)
                assert summary.is_visible()
                summary.focus()
                if not nojs:
                    page.keyboard.press('Enter')
                else:
                    page.keyboard.press('Space')
                assert page.locator('.fv-apollo-atlas details').nth(idx).get_attribute('open') is not None, (name,value)
                assert summary.evaluate("el=>getComputedStyle(el).outlineStyle")!='none', (name,value)
                summary.click()
                assert page.locator('.fv-apollo-atlas details').nth(idx).get_attribute('open') is None
            assert not errors,errors
            if reduced: assert page.locator('.fv-apollo-atlas').evaluate("el=>getComputedStyle(el).scrollBehavior")=='auto'
            if not nojs:
                # Real Chromium accessibility tree (CDP); NOT fake axe-core.
                session=context.new_cdp_session(page)
                ax=session.send('Accessibility.getFullAXTree')['nodes']
                names=[node.get('name',{}).get('value','') for node in ax if node.get('role',{}).get('value') in ('button','DisclosureTriangle')]
                for label in EXPECTED_LABELS:
                    assert label in names,(name,label,names)
            path=out/(name+'.png')
            page.screenshot(path=str(path),full_page=True,animations='disabled')
            receipt['contexts'].append({'name':name,'width':width,'sha256':digest(path),'labels':len(found),'details_keyboard_pointer':'pass','horizontal_overflow':False})
            receipt['assertions']+=7+8*4+ (8 if not nojs else 0)
            context.close()
        browser.close()
    receipt['notes']=['Real Playwright/Chromium via page.set_content; network navigation blocked by sandbox; no installed WP test','Real Chromium CDP AX names; genuine axe-core not installed, not claimed','No real-user LCP/CLS or merchant conversion validation; release remains blocked']
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':'PASS','contexts':len(receipt['contexts']),'assertions_estimate':receipt['assertions'],'receipt':str(out/'receipt.json')},indent=2))
    return receipt

if __name__ == '__main__':
    verify_browser(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'evidence')
