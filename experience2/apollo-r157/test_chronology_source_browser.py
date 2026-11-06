#!/usr/bin/env python3
"""R157 source-bound offline Chromium smoke. Never establishes WordPress release acceptance."""
import argparse,hashlib,json,os,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
WIDTHS=(320,360,390,768,1440,1920)
BASE='7aea496f2a88a7d1eec8bb12e0161d6b34fdfe1797822f6fda333463a7f85ee4'
REVIEW='67b612be3dfb385fd03e952a59e9ec5088c25a89821a3420a5f199326da57c83'
def sha(b):return hashlib.sha256(b).hexdigest()
def main(a):
    base=Path(a.base).read_text();fragment=Path(a.fragment).read_text();review=Path(a.review).read_text()
    assert sha(base.encode())==BASE and sha(review.encode())==REVIEW,'Source changed: STOP'
    assert base.count('       <div class="fv-ex2-ledger__tools"')==1
    assert base.replace('       <div class="fv-ex2-ledger__tools"',fragment+'       <div class="fv-ex2-ledger__tools"')==review
    soup=BeautifulSoup(review,'html.parser')
    assert len(soup.select('[data-fvx-record]'))==6
    assert len(soup.select('[data-fvx-source-custody]'))==6
    assert len(soup.select('.fv-ex2-ledger__rail-list a'))==4
    assert len(soup.select('[data-fvx-record] .fv-ex2-ledger__recordlinks a[href^="https://www.nasa.gov/"]'))==12
    assert len(soup.select('a[href*="the-hatch-opened-inward-apollo-1"]'))==1
    assert not soup.select('[data-lat],[data-lng],[data-geopoint],a[href*="payhip"],a[href*="awin"]')
    for item in soup.select('.fv-ex2-ledger__rail-list a'):assert soup.select_one(item['href']),'Unresolved hash target'
    css='\n'.join(Path(path).read_text() for path in a.css)
    js=Path(a.js).read_text()
    out=Path(a.out)
    if out.exists():raise RuntimeError('Refusing to overwrite evidence')
    out.mkdir(parents=True)
    result={'scope':'R157_SOURCE_BOUND_OFFLINE_NOT_WORDPRESS','release':'STAGING_HOLD','axe':'NOT_EXECUTED' if not a.axe else 'ATTEMPTED',
      'base_sha256':BASE,'review_sha256':REVIEW,'css_sha256':sha(css.encode()),'js_sha256':sha(js.encode()),
      'checks':[],'screenshots':[],'axe_results':[],'errors':[]}
    def check(w,label,ok):result['checks'].append({'width':w,'name':label,'pass':bool(ok)})
    with sync_playwright() as p:
      browser=p.chromium.launch(executable_path=a.chromium,args=['--no-sandbox'])
      result['chromium']=browser.version
      for w in WIDTHS:
        ctx=browser.new_context(viewport={'width':w,'height':800},reduced_motion='reduce',has_touch=(w==390),service_workers='block')
        ctx.route('**/*',lambda route:route.abort())
        page=ctx.new_page()
        page.on('pageerror',lambda e,width=w:result['errors'].append([width,str(e)]))
        page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body style="margin:0"><main>'+review+'</main></body></html>')
        page.add_style_tag(content=css)
        check(w,'no_js_six_records',page.locator('[data-fvx-record]:visible').count()==6)
        check(w,'no_js_four_chronology_links',page.locator('.fv-ex2-ledger__rail-list a:visible').count()==4)
        check(w,'no_js_search_hidden',not page.locator('[data-fvx-tools]').is_visible())
        drawer=page.locator('[data-fvx-source-drawer]')
        drawer.locator('summary').focus();page.keyboard.press('Enter')
        check(w,'keyboard_native_source_drawer',drawer.get_attribute('open') is not None)
        check(w,'report_and_rights_links',drawer.locator('a[href^="https://www.nasa.gov/"]').count()==2)
        drawer.locator('summary').click()
        page.add_script_tag(content=js)
        inp=page.locator('input[data-fvx-search]')
        check(w,'compatible_search_activation',page.locator('[data-fvx-initialized="yes"]').count()==1)
        inp.fill('S66-58038')
        check(w,'search_filters_hatch',not page.locator('#fv-ex2-ledger-apollo1-record-04').is_visible())
        link=page.locator('a[href="#fv-ex2-ledger-apollo1-record-04"]').first
        if w==390:link.tap()
        else:link.click()
        page.wait_for_timeout(35)
        check(w,'rail_unhides_filtered_record',page.locator('#fv-ex2-ledger-apollo1-record-04').is_visible())
        check(w,'rail_restores_all_and_search',inp.input_value()=='' and page.locator('[data-fvx-record]:visible').count()==6)
        check(w,'rail_focuses_hash_target',page.evaluate('document.activeElement?.id')=='fv-ex2-ledger-apollo1-record-04')
        check(w,'native_hash_preserved',page.evaluate('location.hash')=='#fv-ex2-ledger-apollo1-record-04')
        check(w,'reduced_motion',page.evaluate('matchMedia("(prefers-reduced-motion:reduce)").matches'))
        check(w,'no_horizontal_overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
        check(w,'no_runtime_errors',not any(e[0]==w for e in result['errors']))
        if a.axe:
          page.add_script_tag(path=a.axe)
          ax=page.evaluate('async()=>axe.run(document.querySelector("[data-fvx-ledger]"))')
          result['axe_results'].append({'width':w,'violations':[x['id'] for x in ax['violations']],'incomplete':[x['id'] for x in ax['incomplete']]})
          check(w,'axe_complete_and_clean',not ax['violations'] and not ax['incomplete'])
        page.evaluate("""() => {document.querySelectorAll('details').forEach(n=>n.open=false); window.scrollTo(0,0); document.activeElement?.blur()}""")
        page.wait_for_timeout(120)
        name=f'r157-{w}.png';img=page.screenshot(path=str(out/name),full_page=True,animations='disabled')
        result['screenshots'].append({'width':w,'file':name,'sha256':sha(img)})
        ctx.close()
      browser.close()
    result['summary']={'passed':sum(c['pass'] for c in result['checks']),'failed':sum(not c['pass'] for c in result['checks']),
        'axe_executed':bool(a.axe),'wordpress_staging_accepted':False}
    (out/'receipt.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    (out/'SHA256SUMS').write_text(''.join(f"{s['sha256']}  {s['file']}\n" for s in result['screenshots']))
    print(json.dumps(result['summary'],sort_keys=True))
    return int(result['summary']['failed']!=0)
if __name__=='__main__':
    ap=argparse.ArgumentParser()
    for name in ['base','fragment','review','js','out']:ap.add_argument('--'+name,required=True)
    ap.add_argument('--css',action='append',required=True,help='repeat for base/review/compat/rail css')
    ap.add_argument('--axe',default=None,help='locally reviewed axe.min.js; missing audit never means WCAG pass')
    ap.add_argument('--chromium',default=os.getenv('FV_CHROMIUM','/usr/bin/chromium'))
    sys.exit(main(ap.parse_args()))
