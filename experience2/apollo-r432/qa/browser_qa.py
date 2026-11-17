"""Authentic PHP-rendered offline Chromium QA; NEVER reports WordPress/axe/LCP as passed."""
import json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parents[1]
OUT=HERE/'QA';SHOTS=OUT/'screenshots';SHOTS.mkdir(parents=True,exist_ok=True)
WIDTHS=(320,360,390,768,1024,1440,1920)
checks=0
def ok(condition,message):
 global checks
 assert condition,message
 checks+=1

def main():
 html=subprocess.run(['php',str(HERE/'qa/fixture.php')],check=True,capture_output=True).stdout.decode()
 (OUT/'fixture.html').write_text(html)
 entries=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
  try:
   for width in WIDTHS:
    context=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,accept_downloads=True)
    page=context.new_page();page.set_content(html,wait_until='load')
    ok(page.locator('[data-fv-r432]').count()==2,f'{width}: two real PHP instances')
    ok(page.locator('[data-fv-r432] .fv-r429__plate').count()==6,f'{width}: exact source chronology')
    ok(page.locator('[data-fv-r432] .fv-r430__question').count()==6,f'{width}: real educator worksheet')
    ok(page.locator('[data-fv-r432] .fv-r429__cta').count()==2,f'{width}: single CTA per instance')
    ok(page.locator('[data-fv-r432] [data-fv-r431-actions]:not([hidden])').count()==2,f'{width}: tools initialized')
    ok(page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'),f'{width}: no overflow')
    ok(page.evaluate('''() => { const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return ids.length===new Set(ids).size}'''),f'{width}: duplicate-safe IDs')
    ok(page.locator('[data-fv-r432] .fv-r432__rights summary').count()==2,f'{width}: source & rights disclosures')
    ok(page.locator('a[href*="payhip.com"],a[href*="checkout"]').count()==0,f'{width}: no unapproved merchant link')
    url=page.locator('[data-fv-r432] .fv-r429__cta').first.get_attribute('href')
    ok('utm_content=apollo_documentary_001' in url and 'utm_source=youtube' in url,f'{width}: approved campaign continuity')
    ok(page.locator('[data-fv-r432] .fv-r429__cta').last.get_attribute('href').find('utm_content=')<0,f'{width}: untagged second instance')
    page.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True)
    entries.append({'width':width,'html':'actual PHP output, no HTTP navigation','overflow':False,'axe':'HOLD','navigated_lcp':'HOLD','navigated_cls':'HOLD'})
    context.close()
   context=browser.new_context(viewport={'width':390,'height':900},accept_downloads=True)
   page=context.new_page();page.set_content(html)
   root=page.locator('[data-fv-r432]').first
   root.locator('.fv-r432__rights summary').focus();page.keyboard.press('Enter')
   ok(root.locator('.fv-r432__rights').evaluate('(e)=>e.open'),'keyboard source-rights disclosure')
   field=root.locator('.fv-r430__question textarea').first
   field.fill('A grounded answer from an educator.');
   ok(root.locator('.fv-r431__progress').inner_text()=='1 of 3 answers drafted','input change updates progress')
   with page.expect_download() as download:
    root.locator('[data-fv-r431-export]').click()
   saved=OUT/'sample-notes.txt';download.value.save_as(str(saved))
   ok('A grounded answer from an educator.' in saved.read_text(),'real download has local note')
   ok('https://www.nasa.gov/' in saved.read_text(),'real download has primary source')
   ok('utm_content' not in saved.read_text(),'export excludes campaign metadata')
   page.emulate_media(media='print')
   ok(root.locator('.fv-r431__print-answer').first.evaluate("(x)=>getComputedStyle(x).display!=='none'"),'print carries user answers')
   page.screenshot(path=str(SHOTS/'390-print.png'),full_page=True)
   page.emulate_media(media='screen');page.screenshot(path=str(SHOTS/'390-filled.png'),full_page=True)
   context.close()
   context=browser.new_context(java_script_enabled=False,viewport={'width':390,'height':900})
   page=context.new_page();page.set_content(html)
   root=page.locator('[data-fv-r432]').first
   ok(root.locator('[data-fv-r431-actions]:visible').count()==0,'no-JS inert actions hidden')
   ok(root.locator('.fv-r430__question').count()==3,'no-JS questions remain')
   root.locator('.fv-r432__rights summary').click()
   ok(root.locator('.fv-r432__rights').evaluate('(e)=>e.open'),'no-JS native rights disclosure')
   ok(root.locator('.fv-r429__cta').count()==1,'no-JS free investigation CTA')
   page.screenshot(path=str(SHOTS/'390-nojs.png'),full_page=True);context.close()
   context=browser.new_context(viewport={'width':320,'height':900},forced_colors='active',reduced_motion='reduce')
   page=context.new_page();page.set_content(html)
   ok(page.evaluate('document.documentElement.scrollWidth <= innerWidth'),'forced colors/reduced motion fit 320')
   page.screenshot(path=str(SHOTS/'320-forcedcolors-reducedmotion.png'),full_page=True);context.close()
   context=browser.new_context(viewport={'width':320,'height':900})
   page=context.new_page();page.set_content(html);page.add_style_tag(content='html{font-size:200%}')
   ok(page.evaluate('document.documentElement.scrollWidth <= innerWidth'),'200% text fits 320')
   page.screenshot(path=str(SHOTS/'320-text200.png'),full_page=True);context.close()
   context=browser.new_context(viewport={'width':390,'height':900},has_touch=True,is_mobile=True)
   page=context.new_page();page.set_content(html)
   page.locator('[data-fv-r432] .fv-r432__rights summary').first.tap()
   ok(page.locator('[data-fv-r432] .fv-r432__rights').first.evaluate('(e)=>e.open'),'real touch disclosure')
   page.screenshot(path=str(SHOTS/'390-touch.png'),full_page=True);context.close()
  finally:browser.close()
 result={'status':'PASS_OFFLINE_BROWSER_ONLY','assertions':checks,'screenshots':len(list(SHOTS.glob('*.png'))),'actual_rendering':'PHP source-verified R429/R430/R431/R432 loaded using Playwright set_content', 'real_http_navigation':'BLOCKED_BY_ADMINISTRATOR','wordpress_staging':'NOT TESTED','axe_core':'NOT RUN — bundle not approved/present','navigated_lcp_cls':'NOT MEASURED','field_cwv':'NOT MEASURED','paid_sales':'NOT MEASURED','viewport_results':entries}
 (OUT/'browser-report.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(f'PASS {checks} offline browser assertions; {result["screenshots"]} screenshots; real staging/axe/LCP/CLS HOLD')
if __name__=='__main__':main()
