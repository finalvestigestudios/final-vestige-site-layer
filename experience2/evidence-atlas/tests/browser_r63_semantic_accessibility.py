#!/usr/bin/env python3
"""R63: pinned-source Apollo Research Desk + Atlas Chromium semantic regression.

This is real Chromium/CDP testing against original R38 source files and the
source-built Atlas under a PHP WordPress API simulator, not an installed CMS.
CDP accessibility checks are not axe-core or screen-reader certification.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from playwright.sync_api import sync_playwright
from browser_r59_php_cohost import make_document

WIDTHS=(320,360,390,428,768,1024,1440,1920)
INTERACTIVE={'button','link','textbox','searchbox','combobox','checkbox','radio','switch'}

def audit_axe(page, path:Path, sha:str):
    actual=hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != sha:
        raise ValueError('Refusing unverified axe-core: SHA-256 mismatch')
    page.add_script_tag(path=str(path))
    result=page.evaluate('''async () => {
      if (typeof axe === 'undefined' || typeof axe.run !== 'function') throw new Error('axe-core not loaded');
      const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
      return {version:axe.version,violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))};
    }''')
    if result['violations']:
        raise AssertionError(('axe violations',result['violations']))
    return result

def run(output:Path, axe_path:Path|None=None, axe_sha256:str|None=None):
    if (axe_path is None) != (axe_sha256 is None):
        raise ValueError('Both --axe-path and --axe-sha256 are required')
    if axe_path and hashlib.sha256(axe_path.read_bytes()).hexdigest()!=axe_sha256:
        raise ValueError('axe-core digest mismatch: refusing certification')
    html,manifest=make_document()
    output.mkdir(parents=True,exist_ok=True)
    receipt={'schema':'fv.apollo.r63.cdp-semantic-a11y.v1',
             'environment':'real-R38-and-built-Atlas/PHP-WordPress-API-simulation/Chromium',
             'wordpress':'NOT_INSTALLED', 'axe':'VERIFIED_AND_RUN' if axe_path else 'NOT_RUN_NO_CHECKSUM_VERIFIED_BUNDLE',
             'screenreader':'NOT_RUN','hosted_cwv':'NOT_MEASURED',
             'crosswalk_git_blob':manifest['source_crosswalk_blob'],
             'cases':[],'screenshots':{},'axe_results':[],'lab_metrics':[]}
    with sync_playwright() as p:
      browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
      for width in WIDTHS:
       for js in (False,True):
        for forced in (False,True):
          context=browser.new_context(viewport={'width':width,'height':900},
            java_script_enabled=js, reduced_motion='reduce',
            forced_colors='active' if forced else 'none',
            is_mobile=width<=390,has_touch=width<=390)
          page=context.new_page();page.set_default_timeout(6000);errors=[];requests=[]
          page.on('pageerror',lambda e:errors.append(str(e)))
          page.on('request',lambda e:requests.append(e.url))
          page.set_content(html)
          assert not errors and not requests,(width,js,forced,errors,requests)
          assert page.locator('[data-fvx-record]').count()==6
          assert page.locator('[data-fva-record]').count()==6
          assert page.locator('[data-fva-cite-id]').count()==6
          assert page.locator('img').count()==0  # No photo-use approvals.
          assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2')
          assert page.evaluate('''() => {
            const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);
            return ids.length===new Set(ids).size && [...document.querySelectorAll('a[href^="#"]')].every(a=>{
              const hash=a.getAttribute('href');
              return hash==='#' || document.getElementById(decodeURIComponent(hash.slice(1)));
            });
          }'''),(width,js,forced,'duplicate IDs or broken anchors')
          tree=context.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
          unnamed=[(n.get('role',{}).get('value'),n.get('backendDOMNodeId')) for n in tree
             if not n.get('ignored',False) and n.get('role',{}).get('value') in INTERACTIVE
             and not n.get('name',{}).get('value','').strip()]
          assert not unnamed,(width,js,forced,'unnamed accessible controls',unnamed)
          if not js:
            assert page.locator('[data-fvx-record]:visible').count()==6
            assert page.locator('[data-fva-record]:visible').count()==6
            assert page.locator('[data-fva-controls]').is_hidden()
          else:
            assert page.locator('[data-fva-atlas]').get_attribute('data-fva-ready')=='yes'
            # Keyboard-operated native custody drawer with real focus state.
            summary=page.locator('.fv-ex2-ledger__custody summary').first
            summary.focus();assert summary.evaluate('(e)=>e===document.activeElement')
            summary.press('Enter')
            assert summary.evaluate('(e)=>e.parentElement.open')
            summary.press('Enter')
            assert not summary.evaluate('(e)=>e.parentElement.open')
            # Both filter systems remain operable and cannot erase printed custody.
            page.locator('input[data-fvx-search]').fill('S67-19766')
            page.locator('[data-fva-filter="2017"]').click()
            assert page.locator('[data-fvx-record]:visible').count()==1
            assert page.locator('[data-fva-record]:visible').count()==2
            page.emulate_media(media='print')
            assert page.locator('[data-fvx-record]:visible').count()==6
            assert page.locator('.fv-ex2-ledger__custody dd:visible').count()==30
            assert page.locator('[data-fva-record]:visible').count()==6
            assert page.locator('[data-fva-drawer] dd:visible').count()==54
            page.emulate_media(media='screen')
            page.locator('input[data-fvx-search]').fill('')
            page.locator('[data-fva-reset]').click()
            if forced:
              for selector in ('.fv-ex2-ledger__recordlinks a','[data-fva-filter="1967"]'):
                element=page.locator(selector).first
                page.keyboard.press('Tab');element.focus()
                display=element.evaluate('''e => {
                  let s=getComputedStyle(e),r=e.getBoundingClientRect();
                  return {width:parseFloat(s.outlineWidth),style:s.outlineStyle,height:r.height,focused:e.matches(':focus-visible')};
                }''')
                assert display['focused'] and display['width']>=2 and display['style']!='none',(selector,display)
            if axe_path and not forced:
              receipt['axe_results'].append({'width':width,**audit_axe(page,axe_path,axe_sha256)})
            if not forced:
              receipt['lab_metrics'].append({'width':width,**page.evaluate('window.__fv_r53_lab||{}')})
              if width in (390,1440):
                page.wait_for_timeout(120)
                png=page.screenshot(full_page=True,animations='disabled')
                assert png==page.screenshot(full_page=True,animations='disabled')
                name=f'r63-real-source-{width}.png';(output/name).write_bytes(png)
                receipt['screenshots'][name]=hashlib.sha256(png).hexdigest()
          # Reflow test: text-only enlargement, independent of physical DPR.
          # JS-off retains CSS intact and all six records; JS-on tests 200% reflow.
          if js:
            page.evaluate("document.documentElement.style.setProperty('font-size','200%','important')")
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+2'),(width,js,forced,'text reflow')
          assert not errors and not requests,(width,js,forced,errors,requests)
          receipt['cases'].append({'width':width,'js':js,'forced_colors':forced,'passed':True,
                 'accessible_interactive_nodes':sum(1 for n in tree if not n.get('ignored',False) and n.get('role',{}).get('value') in INTERACTIVE)})
          context.close()
      browser.close()
    dest=output/'R63_SEMANTIC_BROWSER_RECEIPT.json'
    dest.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('PASS',len(receipt['cases']),'real-source Chromium/CDP configurations; axe:',receipt['axe'])
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--axe-path',type=Path)
    parser.add_argument('--axe-sha256')
    args=parser.parse_args()
    run(args.output,args.axe_path,args.axe_sha256)
