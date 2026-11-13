#!/usr/bin/env python3
"""R323 committed replay: local Chromium PDF URI custody, no installed WordPress."""
import hashlib, io, json, subprocess
from pathlib import Path
from urllib.parse import urlsplit
from pypdf import PdfReader
from playwright.sync_api import sync_playwright
BASE=Path(__file__).resolve().parents[2]
PHP=BASE/'apollo-r281/apollo-source-experience.php'
CSS=BASE/'apollo-r281/assets/apollo-source-experience.css'
JS=BASE/'apollo-r281/assets/apollo-cache-continuation.js'
STUB=BASE/'apollo-r320/qa/wp_late_shortcodes.php'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
QUERY='utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo1_yt_longform001'
ALLOWED={FREE,'https://www.nasa.gov/mission/apollo-1/',
'https://www.nasa.gov/history/Apollo204/proceed.html',
'https://www.nasa.gov/history/Apollo204/narr.html',
'https://www.nasa.gov/history/Apollo204/15.html',
'https://sma.nasa.gov/sma-disciplines/accllp/apollo-1',
'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
'https://www.nasa.gov/image-detail/amf-s67-15717/',
'https://www.nasa.gov/image-detail/amf-s66-58038/',
'https://www.nasa.gov/image-detail/amf-s67-21294/',
'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/'}
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def fixture():
    raw=subprocess.check_output(['php',str(STUB),'late-dynamic','1'],text=True)
    body,metadata=raw.split('<!--R320_QUEUE:')
    assert json.loads(metadata.split('-->')[0])['calls']==1
    return body.replace('</head>','<style>'+CSS.read_text()+'</style></head>')
def links(pdf):
    result=[]
    for page in PdfReader(io.BytesIO(pdf)).pages:
        for ref in page.get('/Annots',[]):
            action=ref.get_object().get('/A')
            if action:
                assert str(action.get('/S'))=='/URI'
                result.append(str(action.get('/URI')))
    return result
def run():
    subprocess.run(['php','-l',str(PHP)],check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['node','--check',str(JS)],check=True,stdout=subprocess.DEVNULL)
    assert blob(CSS.read_bytes())=='7c0e58782a8ec7b23f28da784a84c827f117914a'
    assert 'r323-print-neutral-20261112' in PHP.read_text()
    start=JS.read_text().index('  // R323: a visitor can open the native context menu')
    end=JS.read_text().index("  document.addEventListener('click', handleActivation, true);",start)
    old=JS.read_text()[:start]+JS.read_text()[end:]
    assert blob(old.encode())=='a3c858b51005495ebebb326086badc155c1b7e5a'
    passed=0
    with sync_playwright() as play:
        browser=play.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for width in (320,390,1440,1920):
                for js in (True,False):
                    ctx=browser.new_context(viewport={'width':width,'height':900},
                        java_script_enabled=js,reduced_motion='reduce',has_touch=width<=390)
                    page=ctx.new_page();page.goto('about:blank?'+QUERY);page.set_content(fixture())
                    if js:page.add_script_tag(content=JS.read_text())
                    assert page.locator('section.fv-r281').count()==1
                    assert page.locator('a[data-fv-cta]').count()==1
                    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                    cta=page.locator('a[data-fv-cta]').first
                    cta.focus();page.keyboard.press('Shift+F10')
                    if js:assert 'utm_campaign=' in cta.get_attribute('href')
                    else:assert cta.get_attribute('href')==FREE
                    pdf=page.pdf(format='A4',print_background=True)
                    uris=links(pdf)
                    assert set(uris)==ALLOWED and uris.count(FREE)==1
                    assert not any('utm_' in u for u in uris)
                    assert cta.get_attribute('href')==FREE
                    passed+=1;ctx.close()
            ctx=browser.new_context();page=ctx.new_page()
            page.goto('about:blank?'+QUERY);page.set_content(fixture());page.add_script_tag(content=old)
            page.locator('a[data-fv-cta]').focus();page.keyboard.press('Shift+F10')
            assert sum('utm_campaign=' in u for u in links(page.pdf(format='A4',print_background=True)))==1
            ctx.close()
        finally:browser.close()
    assert passed==8
    print('R323 PASS 8/8 real Chromium contexts, 8 PDF URI inventories, R322 contaminated-PDF negative control')
if __name__=='__main__':run()
