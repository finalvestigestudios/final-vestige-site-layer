#!/usr/bin/env python3
"""Offline computed-style companion to Page 6 raw/DOM custody.

Requires a public-only, rendered WordPress candidate HTML file and the existing
fingerprint manifest. This never connects to production or verifies Jetpack's
backend. A PASS is a Chromium lab preflight, NEVER release approval.
"""
import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from playwright.sync_api import sync_playwright
from verify_homepage_preservation import evaluate

WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
FOCUS = 'a[href="https://finalvestige.com/focus/"]'
SELECTORS = {'margin': '.fv-margin-strip', 'item': '.fv-margin-strip__item',
             'jetpack': '.wp-block-jetpack-subscriptions', 'focus': FOCUS,
             'flagship': '[data-fv-home-flagship]'}

COMPUTED = r"""(q) => {
  const all = key => [...document.querySelectorAll(q[key])];
  function visible(el) {
    if (!el || el.closest('[hidden],[inert],[aria-hidden="true"],template')) return false;
    let opacity=1;
    for(let n=el; n && n.nodeType===1; n=n.parentElement) {
      const s=getComputedStyle(n);
      if(s.display==='none'||s.visibility==='hidden'||s.visibility==='collapse'||
         s.contentVisibility==='hidden'||s.clipPath==='inset(100%)'||
         s.clipPath==='circle(0%)'||s.fontSize==='0px') return false;
      opacity *= Number(s.opacity || 0);
    }
    const r=el.getBoundingClientRect();
    return opacity>0.02 && r.width>0 && r.height>0;
  }
  const count = key => all(key).filter(visible).length;
  const actions=all('jetpack').flatMap(j=>[...j.querySelectorAll('input,button,a[href]')]);
  const controls=actions.filter(el=>visible(el)&&getComputedStyle(el).pointerEvents!=='none');
  const focus=all('focus').filter(el=>visible(el)&&getComputedStyle(el).pointerEvents!=='none');
  const errors=[];
  if(count('margin')<1)errors.push('margin_strip_computed_hidden');
  if(count('item')<1)errors.push('all_margin_records_computed_hidden');
  if(count('jetpack')!==1)errors.push('jetpack_computed_hidden');
  if(!controls.length)errors.push('jetpack_has_no_actionable_control');
  if(!focus.length)errors.push('focus_action_hidden_or_disabled');
  if(count('flagship')!==1)errors.push('flagship_computed_hidden');
  const overflow=Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth);
  if(overflow>2)errors.push('horizontal_overflow_px:'+overflow);
  const selfLinkCount=controls.filter(el=>el.tagName==='A'&&/[?&]p=6(?:&|$)/.test(el.getAttribute('href')||'')).length;
  return {errors, visible_margin_count:count('item'), visible_jetpack_count:count('jetpack'),
    jetpack_controls:controls.length, focus_actions:focus.length, visible_flagship_count:count('flagship'),
    horizontal_overflow_px:overflow, subscription_self_links_inconclusive:selfLinkCount};
}"""

class AssetPreflight(HTMLParser):
    """Fail closed if source needs styles/scripts that offline browser blocks."""
    def __init__(self):
        super().__init__()
        self.blocked = []
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag == 'link' and 'stylesheet' in (d.get('rel') or '').lower().split():
            self.blocked.append('external_stylesheet_not_loaded')
        if tag == 'script' and d.get('src'):
            self.blocked.append('external_script_not_loaded')


def verify(html, baseline, widths=WIDTHS):
    result={'gate':'HOLD','release_approved':False,'checks':[],'errors':[],
      'limitations':['Offline rendered candidate, not a WordPress/Assembler runtime',
      'Jetpack signup/confirmation and realized revenue not verified',
      'No axe/WCAG certification, media network transfer, Lighthouse, HTTP CSP or field CWV',
      'External network requests aborted; computed CSS depends on included styles']}
    static=evaluate(html,baseline)
    result['static_gate']=static['gate']
    if static['gate']!='PASS':
        result['errors'].append('Raw/DOM fingerprints HOLD: '+str(static['errors']))
        return result
    deps=AssetPreflight()
    deps.feed(html)
    deps.close()
    if re.search(r'@import\s', html, re.I):
        deps.blocked.append('stylesheet_import_not_loaded')
    if deps.blocked:
        result['errors'].append('Offline CSS/JS asset preflight HOLD: '+', '.join(sorted(set(deps.blocked))))
        return result
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',
          headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
        try:
            for width in widths:
                for js in (False,True):
                    ctx=browser.new_context(viewport={'width':width,'height':900},
                      java_script_enabled=js,reduced_motion='reduce')
                    ctx.route('**/*',lambda route:route.abort())
                    page=ctx.new_page()
                    page.set_content(html,wait_until='domcontentloaded')
                    metrics=page.evaluate(COMPUTED,SELECTORS)
                    result['checks'].append({'width':width,'js_enabled':js,**metrics})
                    if metrics['errors']:
                        result['errors'].append(f"{width}px JS={js}: "+', '.join(metrics['errors']))
                    ctx.close()
        finally:
            browser.close()
    if not result['errors']: result['gate']='PASS'
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--candidate',type=Path,required=True)
    ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--out',type=Path)
    args=ap.parse_args()
    r=verify(args.candidate.read_text('utf8'),json.loads(args.baseline.read_text('utf8')))
    data=json.dumps(r,indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(data+'\n',encoding='utf8')
    print(data)
    return 0 if r['gate']=='PASS' else 1

if __name__=='__main__': raise SystemExit(main())
