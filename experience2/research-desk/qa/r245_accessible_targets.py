#!/usr/bin/env python3
"""R245 Research Desk PHP-to-Chromium target/print regression.
Default runs on protected NASA source; --fixture is synthetic and cannot approve release.
Requires php, bs4, Playwright, Chromium. No network, WP writes or paid service.
"""
import argparse, hashlib, json, os, shutil, subprocess, tempfile
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from r243_core import SHIM

ORIGINAL = '403d128c57b9bc82dac7c619651689070edef86c'
WIDTHS = (320, 390, 768, 1440, 1920)

def blob(b):
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--fixture',action='store_true')
    a=p.parse_args()
    source=a.source.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='apollo-r245-') as d:
        root=Path(d)
        shutil.copy2(source/'final-vestige-ex2-research-desk.php',root/'final-vestige-ex2-research-desk.php')
        css=(source/'assets/source-ledger.css').read_text(encoding='utf-8')
        (root/'assets').mkdir()
        (root/'assets/source-ledger.css').write_text(css,encoding='utf-8')
        shutil.copy2(source/'assets/source-ledger.js',root/'assets/source-ledger.js')
        (root/'templates').mkdir()
        if a.fixture:
            cards=''.join(f'<article data-fvx-record id="fv-ex2-ledger-apollo1-record-{i}"><h2>Fixture {i}</h2><details class="fv-ex2-ledger__fulltext"><summary>Review underlying finding</summary><p>Fixture finding {i}</p></details><div class="fv-ex2-ledger__recordlinks"><a href="https://www.nasa.gov/">Source {i}</a><a href="https://www.nasa.gov/">NASA {i}</a></div></article>' for i in range(6))
            html='<section class="fv-ex2-ledger" data-fvx-ledger><div class="fv-ex2-ledger__wrap"><div class="fv-ex2-ledger__grid">'+cards+'</div><a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read original investigation</a></div></section>'
            (root/'templates/ledger.html').write_text(html,encoding='utf-8')
        else:
            data=(source/'templates/ledger.html').read_bytes()
            assert blob(data)==ORIGINAL, 'Protected NASA source template mismatch'
            (root/'templates/ledger.html').write_bytes(data)
        (root/'shim.php').write_text(SHIM,encoding='utf-8')
        rendered=json.loads(subprocess.run(['php',str(root/'shim.php'),'late'],check=True,capture_output=True,text=True).stdout)['first']
        dom=BeautifulSoup(rendered,'html.parser')
        assert len(dom.select('[data-fvx-record]'))==6
        assert len(dom.select('.fv-ex2-ledger__recordlinks a'))==12
        failures=[];cases={}
        with sync_playwright() as pw:
            browser=pw.chromium.launch(executable_path=os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE','/usr/bin/chromium'),args=['--no-sandbox'])
            try:
                for width in WIDTHS:
                    for js in (False,True):
                        key=f'{width}-'+('js' if js else 'nojs')
                        ctx=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=js,is_mobile=width<400,has_touch=width<400,reduced_motion='reduce')
                        page=ctx.new_page();requests=[]
                        page.on('request',lambda r: requests.append(r.url))
                        page.set_content('<html lang="en"><head><meta charset="utf-8"><style>'+css+'</style></head><body>'+rendered+'</body></html>')
                        links=page.locator('.fv-ex2-ledger__recordlinks a')
                        summaries=page.locator('.fv-ex2-ledger__fulltext summary')
                        lh=min(links.nth(i).bounding_box()['height'] for i in range(links.count()))
                        sh=min(summaries.nth(i).bounding_box()['height'] for i in range(summaries.count()))
                        if min(lh,sh)<44:failures.append(key+': target below 44px')
                        summaries.first.focus();page.keyboard.press('Enter')
                        if page.locator('details').first.get_attribute('open')!='':failures.append(key+': keyboard disclosure failed')
                        page.keyboard.press('Enter')
                        page.locator('[data-fvx-record]').first.evaluate('(e)=>e.hidden=true')
                        page.emulate_media(media='print')
                        if page.locator('[data-fvx-record]').first.evaluate('(e)=>getComputedStyle(e).display')=='none':failures.append(key+': record hidden in print')
                        if not page.locator('.fv-ex2-ledger__fulltext p').first.is_visible():failures.append(key+': print lost finding')
                        style=links.first.evaluate('(e)=>({display:getComputedStyle(e).display,url:getComputedStyle(e,"::after").content})')
                        if style['display']!='inline' or 'nasa.gov' not in style['url']:failures.append(key+': printable NASA URL missing')
                        page.emulate_media(media='screen')
                        if page.evaluate('document.documentElement.scrollWidth>innerWidth+1'):failures.append(key+': horizontal overflow')
                        if requests:failures.append(key+': unexpected network request')
                        if key in ('390-js','390-nojs','1440-js','1440-nojs'):
                            page.screenshot(path=str(out/(key+'.png')),full_page=True,animations='disabled')
                        cases[key]={'min_link_px':round(lh,2),'min_summary_px':round(sh,2),'outbound_requests':len(requests)}
                        ctx.close()
            finally:browser.close()
    receipt={'status':'PASS' if not failures else 'FAIL','scope':'SYNTHETIC' if a.fixture else 'EXACT_NASA_TEMPLATE','contexts':len(cases),'cases':cases,'failures':failures,'installed_WP':False,'axe_core':False}
    (out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':receipt['status'],'scope':receipt['scope'],'contexts':len(cases),'failures':failures}))
    if failures:raise SystemExit(1)

if __name__=='__main__':
    main()
