#!/usr/bin/env python3
"""Actual Chromium R33 staging annex QA. It does not navigate WordPress."""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from nasa_catalog_custody_r33 import validate_registry,render

WIDTHS=(320,360,390,768,1024,1440,1920)

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def run(registry:Path, shots:Path, receipt:Path):
    data=json.loads(registry.read_text());validate_registry(data)
    html=render(data)
    shots.mkdir(parents=True,exist_ok=True)
    results=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in WIDTHS:
            context=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce',java_script_enabled=False)
            page=context.new_page();errors=[];outbound=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.on('request',lambda request:outbound.append(request.url))
            page.set_content(html,wait_until='load')
            assert not errors and not outbound,(errors,outbound)
            base=page.evaluate('''() => ({width:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,
               cards:document.querySelectorAll('article').length,details:document.querySelectorAll('details').length,
               sources:document.querySelectorAll('a[href^="https://www.nasa.gov/image-detail/"]').length,
               images:document.querySelectorAll('img').length,scripts:document.querySelectorAll('script').length,
               mapPositions:document.querySelectorAll('[data-lat],[data-lon]').length,
               language:document.documentElement.lang,heading:document.querySelector('h1').textContent.trim()})''')
            assert (base['cards'],base['details'],base['sources'],base['images'],base['scripts'],base['mapPositions'])==(6,12,6,0,0,0),base
            assert base['scroll']<=base['width']+1,base
            assert base['language']=='en'
            summary=page.locator('#catalog-03 details summary').first
            summary.scroll_into_view_if_needed();summary.focus();page.keyboard.press('Enter')
            assert page.locator('#catalog-03 details').first.evaluate('(e)=>e.open'), 'keyboard disclosure failed'
            summary.click()
            assert not page.locator('#catalog-03 details').first.evaluate('(e)=>e.open'), 'pointer toggle failed'
            if width in (390,1440):
                path=shots/f'r33-nasa-custody-{width}.png'
                page.screenshot(path=str(path),full_page=True,animations='disabled')
                base['screenshot_sha256']=sha(path)
            base['viewport']=width
            results.append(base)
            context.close()
        browser.close()
    result={'status':'STAGING_HOLD','browser':'Chromium','widths':results,'screenshot_label':'private no-JS rendering, NOT WordPress','axe':'NOT_RUN',
            'LCP':'NOT_MEASURED_NOT_HOSTED','CLS':'NOT_MEASURED_NOT_HOSTED',
            'source_snapshot_date':data['checked_on']}
    receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--registry',type=Path,required=True);p.add_argument('--shots',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True)
    args=p.parse_args(); result=run(args.registry,args.shots,args.receipt)
    print('R33 real Chromium source annex:',len(result['widths']),'responsive widths, release HOLD')
