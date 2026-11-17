"""Offline real Chromium screenshot/interaction QA against genuine byte-pinned R426 PHP output.
Not website navigation, HTTP/CSP, axe-core, field LCP/CLS or screen-reader evidence.
"""
import json
import os
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'QA'
SHOTS=QA/'screenshots'
SHOTS.mkdir(parents=True,exist_ok=True)
html=subprocess.check_output(['php',str(ROOT/'qa/render_fixture.php')],text=True)
results=[]

def report(name, ok, detail=''):
    results.append({'case':name,'status':'PASS' if ok else 'FAIL','detail':detail})
    if not ok:raise AssertionError(f'{name}: {detail}')

with sync_playwright() as p:
    for width in [320,360,390,768,1024,1440,1920]:
        browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':width,'height':800},device_scale_factor=1)
        page=context.new_page();page.set_content(html,wait_until='load')
        info=page.evaluate('''() => ({scroll:document.documentElement.scrollWidth, client:document.documentElement.clientWidth,
          ids:[...document.querySelectorAll('[id]')].map(el=>el.id),
          ctas:document.querySelectorAll('.fv-r426__cta').length,
          cards:document.querySelectorAll('.fv-r426__plate').length,
          reports:document.querySelectorAll('.fv-r427__context a[href*="apollo-204-review-board"]').length})''')
        report(f'{width}px responsive/source',info['scroll']<=info['client']+1 and len(info['ids'])==len(set(info['ids'])) and info['ctas']==2 and info['cards']==12 and info['reports']==2,str(info))
        page.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True,animations='disabled')
        browser.close()
    for name,kwargs in [
       ('no-js',{'java_script_enabled':False}),
       ('touch',{'has_touch':True,'is_mobile':True,'viewport':{'width':390,'height':844}}),
       ('reduced-motion',{'reduced_motion':'reduce'}),
       ('forced-colors',{'forced_colors':'active'}),
       ('zoomed-text',{}),
       ('print',{})]:
        browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,**{k:v for k,v in kwargs.items() if k!='viewport'})
        page=context.new_page()
        if name=='print':page.emulate_media(media='print')
        if name=='zoomed-text':page.add_style_tag(content='html{font-size:40px!important}')
        page.set_content(html,wait_until='load')
        if name=='zoomed-text':page.add_style_tag(content='html{font-size:40px!important}')
        if name=='touch':page.locator('.fv-r426__plate summary').first.tap()
        elif name!='no-js':page.locator('.fv-r426__plate summary').first.focus();page.keyboard.press('Enter')
        report(name,page.locator('.fv-r426__plate').count()==12 and (name=='no-js' or page.locator('.fv-r426__plate details').first.evaluate('(d)=>d.open')),
            f'plates={page.locator(".fv-r426__plate").count()}')
        page.screenshot(path=str(SHOTS/f'{name}.png'),full_page=True,animations='disabled')
        browser.close()
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    page=browser.new_page()
    try:
        page.goto('http://127.0.0.1:42700/',timeout=3000)
        navigation='NAVIGATION_SUCCEEDED_UNEXPECTEDLY'
    except Exception as exc:
        navigation='BLOCKED: '+str(exc).splitlines()[0]
    browser.close()
(QA/'browser_results.json').write_text(json.dumps({'checks':results,'count':len(results),'navigation':navigation,
 'axe_core':'NOT_EXECUTED_NOT_INSTALLED','lcp_cls':'NOT_MEASURED_NAVIGATION_BLOCKED',
 'hosted_staging':'NOT_TESTED','screenshots':len(list(SHOTS.glob('*.png')))},sort_keys=True,indent=2)+'\n')
print(f'PASS {len(results)}/{len(results)} offline Chromium scenarios; screenshots={len(list(SHOTS.glob("*.png")))}; {navigation}')
