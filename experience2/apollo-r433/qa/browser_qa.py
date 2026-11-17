"""Offline Playwright renderer; no claims of installed WP, axe, or navigated CWV."""
from pathlib import Path
import json, subprocess
from playwright.sync_api import sync_playwright
HERE=Path(__file__).resolve().parents[1]
QA=HERE/'QA';SHOTS=QA/'screenshots';SHOTS.mkdir(parents=True,exist_ok=True)
WIDTHS=(320,360,390,768,1024,1440,1920)
checks=0
def ok(v,desc):
 global checks
 assert v,desc
 checks+=1

def main():
 html=subprocess.run(['php',str(HERE/'qa/fixture.php')],check=True,capture_output=True).stdout.decode()
 (QA/'fixture.html').write_text(html)
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'],headless=True)
  try:
   for width in WIDTHS:
    context=b.new_context(viewport={'width':width,'height':900},accept_downloads=True)
    page=context.new_page();page.set_content(html)
    ok(page.locator('[data-fv-r433]').count()==2,f'{width} two genuine PHP-rendered instances')
    ok(page.locator('[data-fv-r433] .fv-r433__claim').count()==6,f'{width} six claims')
    ok(page.locator('[data-fv-r433] .fv-r429__cta').count()==2,f'{width} free CTA')
    ok(page.locator('[data-fv-r433] [data-fv-r431-actions]:not([hidden])').count()==2,f'{width} notebook initialized')
    ok(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),f'{width} no overflow')
    ok(page.evaluate("() => {let ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return ids.length===new Set(ids).size}"),f'{width} distinct IDs')
    ok(page.locator('a[href*="checkout"],a[href*="payhip"]').count()==0,f'{width} no sales link')
    page.screenshot(path=str(SHOTS/f'{width}.png'),full_page=True);context.close()
   context=b.new_context(viewport={'width':390,'height':900},accept_downloads=True)
   page=context.new_page();page.set_content(html)
   detail=page.locator('[data-fv-r433] .fv-r433__claim details').first
   detail.locator('summary').focus();page.keyboard.press('Enter')
   ok(detail.evaluate('(x)=>x.open'),'keyboard opens source boundary')
   input=page.locator('[data-fv-r433] textarea').first;input.fill('Source checked; exact wire remains unknown.')
   ok('1 of 3' in page.locator('[data-fv-r433] [data-fv-r431-progress]').first.inner_text(),'input note state')
   with page.expect_download() as d:page.locator('[data-fv-r433] [data-fv-r431-export]').first.click()
   target=QA/'local-notes.txt';d.value.save_as(str(target))
   ok('Source checked' in target.read_text(),'download actual user response')
   ok('nasa.gov' in target.read_text().lower(),'notes link original NASA source')
   page.screenshot(path=str(SHOTS/'390-notes.png'),full_page=True)
   page.emulate_media(media='print');ok(page.locator('.fv-r433__printlimit').first.evaluate("(x)=>getComputedStyle(x).display!=='none'"),'print shows claim limitation')
   page.screenshot(path=str(SHOTS/'390-print.png'),full_page=True);context.close()
   context=b.new_context(java_script_enabled=False,viewport={'width':390,'height':900})
   page=context.new_page();page.set_content(html)
   ok(page.locator('[data-fv-r431-actions]:visible').count()==0,'no-JS hides inert controls')
   ok(page.locator('[data-fv-r433] .fv-r429__cta').count()==2,'no-JS free article')
   page.locator('[data-fv-r433] .fv-r433__claim summary').first.click()
   ok(page.locator('[data-fv-r433] .fv-r433__claim details').first.evaluate('(x)=>x.open'),'no-JS source expands')
   page.screenshot(path=str(SHOTS/'390-nojs.png'),full_page=True);context.close()
   context=b.new_context(viewport={'width':320,'height':900},forced_colors='active',reduced_motion='reduce')
   page=context.new_page();page.set_content(html)
   ok(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'forced colors/reduced motion fit')
   page.screenshot(path=str(SHOTS/'320-forced-colors.png'),full_page=True);context.close()
   context=b.new_context(viewport={'width':320,'height':900},has_touch=True,is_mobile=True)
   page=context.new_page();page.set_content(html)
   page.locator('[data-fv-r433] .fv-r433__claim summary').first.tap()
   ok(page.locator('[data-fv-r433] .fv-r433__claim details').first.evaluate('(x)=>x.open'),'touch expands source')
   page.add_style_tag(content='html{font-size:200%}')
   ok(page.evaluate('document.documentElement.scrollWidth<=innerWidth'),'touch/200% fit')
   page.screenshot(path=str(SHOTS/'320-touch-200text.png'),full_page=True);context.close()
  finally:b.close()
 report={'status':'PASS_OFFLINE_PHP_CHROMIUM_ONLY','assertions':checks,'screenshots':len(list(SHOTS.glob('*.png'))),'actual_http_navigation':'BLOCKED_BY_ADMINISTRATOR','real_wordpress_staging':'NOT_EXECUTED','axe_core':'NOT_EXECUTED','navigated_lcp_cls':'NOT_MEASURED','field_p75':'NOT_MEASURED','source_media_licenses':'PER-ASSET REVIEW REQUIRED','merchant_paid_conversion':'NOT_MEASURED'}
 (QA/'browser-report.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print('PASS',checks,'offline Chromium checks;',report['screenshots'],'screenshots; real staging/axe/LCP/CLS HOLD')
if __name__=='__main__':main()
