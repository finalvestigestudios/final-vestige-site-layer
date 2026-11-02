#!/usr/bin/env python3
"""R60 real R38/Atlas browser accessibility test and read-only private WP gate.

Local: actual SHA-pinned R38+Atlas PHP callbacks under R59's WP API simulator.
--wp-url: genuine pre-existing private WordPress page (HTTP GET only), requires
a caller-supplied SHA-256-pinned axe-core JS. Never confuses these two modes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

sys.path.insert(0,str(Path(__file__).resolve().parent))
from browser_r59_php_cohost import make_document

WIDTHS=(320,360,390,428,768,1024,1440,1920)
TARGETS=(
 '.fv-ex2-apollo-suite .fv-ex2-ledger__recordlinks a,'
 '.fv-ex2-apollo-suite .fv-ex2-ledger__footer a,'
 '.fv-ex2-apollo-suite .fv-ex2-ledger__fulltext summary,'
 '.fv-ex2-apollo-suite .fv-ex2-ledger__custody summary'
)
def run(output:Path,wp_url:str|None=None,axe_file:Path|None=None,axe_sha256:str|None=None):
    if bool(axe_file)!=bool(axe_sha256):
        raise ValueError('axe JS path AND SHA256 required together')
    if axe_file and hashlib.sha256(axe_file.read_bytes()).hexdigest()!=axe_sha256:
        raise ValueError('axe-core file SHA256 mismatch')
    if wp_url:
        u=urlparse(wp_url)
        if u.scheme not in ('http','https') or not u.hostname or u.username or u.password:
            raise ValueError('Invalid private staging URL')
        if not axe_file:raise ValueError('WordPress acceptance requires pinned axe-core')
    html,_=make_document() # abort on any original R38 or Atlas source-pin drift
    output.mkdir(parents=True,exist_ok=True)
    evidence={'schema':'fv.apollo.r60.accessibility.v1','release':'STAGING_HOLD',
      'scope':'PRIVATE_WORDPRESS_READ_ONLY' if wp_url else 'ORIGINAL_R38_PHP_WP_API_MOCK',
      'wordpress_tested':bool(wp_url),'axe_executed':bool(axe_file),
      'hosted_p75_cwv':'NOT_MEASURED','screenshots':{},'cases':[]}
    with sync_playwright() as p:
      browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
      for width in WIDTHS:
       for js in (False,True):
        context=browser.new_context(viewport={'width':width,'height':900},
          java_script_enabled=js,reduced_motion='reduce',
          is_mobile=width<=390,has_touch=width<=390)
        page=context.new_page()
        errors=[];requests=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        if not wp_url:page.on('request',lambda req:requests.append(req.url))
        if wp_url:
            response=page.goto(wp_url,wait_until='domcontentloaded',timeout=30000)
            assert response and response.ok,'WordPress staging URL unavailable'
            for handle in ('fv-ex2-research-desk','fv-ex2-evidence-atlas','fv-ex2-apollo-suite'):
                assert page.locator('head link#'+handle+'-css').count()==1,('missing pre-head CSS',handle)
            for handle in ('fv-ex2-research-desk','fv-ex2-evidence-atlas'):
                assert page.locator('script#'+handle+'-js').count()==1,('missing original script',handle)
        else:page.set_content(html)
        page.wait_for_timeout(75)
        assert not errors and not requests,(width,js,errors,requests)
        assert page.locator('.fv-ex2-apollo-suite').count()==1
        assert page.locator('[data-fvx-record]').count()==6
        assert page.locator('[data-fva-record]').count()==6
        assert page.locator('[data-fva-cite-id]').count()==6
        assert page.locator('img').count()==0,'photographs not cleared for use'
        assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'),width
        # CDP's actual accessibility tree: no empty name on interactive roles.
        tree=page.context.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
        unnamed=[node.get('role',{}).get('value') for node in tree
          if not node.get('ignored',True) and
          node.get('role',{}).get('value') in ('button','link','searchbox','textbox','DisclosureTriangle')
          and not node.get('name',{}).get('value','').strip()]
        assert not unnamed,('unnamed interactive controls',width,unnamed)
        boxes=page.eval_on_selector_all(TARGETS,'''nodes=>nodes.filter(e=>e.getClientRects().length)
            .map(e=>({width:e.getBoundingClientRect().width,
                      height:e.getBoundingClientRect().height}))''')
        assert len(boxes)>=24,(width,'missing targets',len(boxes))
        assert all(x['width']>=44 and x['height']>=44 for x in boxes),(width,'small hit area')
        summary=page.locator('.fv-ex2-apollo-suite .fv-ex2-ledger__custody summary').first
        assert summary.evaluate('(e)=>getComputedStyle(e).display')=='list-item'
        summary.focus()
        assert summary.evaluate('(e)=>getComputedStyle(e).outlineStyle')=='solid'
        was=summary.evaluate('(e)=>e.parentElement.open')
        summary.press('Enter')
        assert summary.evaluate('(e)=>e.parentElement.open')!=was
        summary.press('Enter')
        if js:
            page.locator('input[data-fvx-search]').fill('S67-19766')
            assert page.locator('[data-fvx-record]:visible').count()==1
            page.emulate_media(media='print')
            assert page.locator('[data-fvx-record]:visible').count()==6
            assert page.locator('.fv-ex2-ledger__custody dd:visible').count()==30
            assert page.locator('[data-fva-drawer] dd:visible').count()==54
            page.emulate_media(media='screen')
            page.locator('input[data-fvx-search]').fill('')
            if width<=390:
                touch=page.locator('.fv-ex2-apollo-suite .fv-ex2-ledger__fulltext summary').first
                state=touch.evaluate('(e)=>e.parentElement.open')
                touch.tap()
                assert touch.evaluate('(e)=>e.parentElement.open')!=state
            else:
                page.locator('[data-fva-filter="2017"]').click()
                assert page.locator('[data-fva-record]:visible').count()==2
                page.locator('[data-fva-reset]').click()
        if axe_file:
            page.add_script_tag(path=str(axe_file))
            ax=page.evaluate('''async()=>{let r=await axe.run(document,{
             runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
             return r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))}''')
            assert not ax,('axe-core violations',width,ax)
        if js and width in (390,1440):
            page.wait_for_timeout(220)
            png=page.screenshot(full_page=True,animations='disabled')
            assert png==page.screenshot(full_page=True,animations='disabled')
            name=f'r60-real-r38-{width}.png'
            (output/name).write_bytes(png)
            evidence['screenshots'][name]=hashlib.sha256(png).hexdigest()
        evidence['cases'].append({'width':width,'js':js,'pass':True,'targets':len(boxes),
                                  'min_height':round(min(x['height'] for x in boxes),2),
                                  'axe':'RUN' if axe_file else 'NOT_EXECUTED_NO_LOCAL_BUNDLE'})
        context.close()
      browser.close()
    (output/'R60_BROWSER_RECEIPT.json').write_text(json.dumps(evidence,sort_keys=True,indent=2)+'\n')
    print('PASS',len(evidence['cases']),'real-R38 browser cases;',
          'WordPress:',bool(wp_url),'axe-core:',bool(axe_file))
    return evidence

if __name__=='__main__':
    arg=argparse.ArgumentParser()
    arg.add_argument('--output',type=Path,required=True)
    arg.add_argument('--wp-url')
    arg.add_argument('--axe-file',type=Path)
    arg.add_argument('--axe-sha256')
    opts=arg.parse_args()
    try:run(opts.output,opts.wp_url,opts.axe_file,opts.axe_sha256)
    except (ValueError,FileNotFoundError) as exc:
      print('BLOCKED:',str(exc),file=sys.stderr)
      sys.exit(2)
