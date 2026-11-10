"""Offline Chromium smoke test of the proposed single-block Page 6 composition.

Requires playwright + system Chromium. All 72 Margins and Jetpack markup are
synthetic, and the Jetpack placeholder is NONFUNCTIONAL. This is not staging QA.
"""
import json
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(REPO/'tools/experience-2'))
sys.path.insert(0,str(REPO/'tests/experience-2'))
from compose_page6_flagship import compose, stage_payload
from test_page6_scoped_composer import synthetic_page

def main():
    raw=synthetic_page()
    payload=stage_payload(REPO/'experience2/home-flagship')
    combined,receipt=compose(raw,payload)
    combined=combined.replace(
        '<!-- wp:jetpack/subscriptions {"className":"is-style-split"} /-->',
        '<div class="wp-block-jetpack-subscriptions" role="group" aria-label="NONFUNCTIONAL synthetic signup">Synthetic Jetpack placeholder — no subscriber action</div>')
    combined=re.sub(r'<!-- /?wp:[^>]*-->','',combined)
    html=('<!doctype html><html lang="en"><head><meta charset="utf-8">'
          '<meta name="viewport" content="width=device-width,initial-scale=1">'
          '<title>OFFLINE SYNTHETIC FIXTURE — NOT WORDPRESS</title>'
          '<style>body{margin:0;background:#0a0b0d;color:#eee;font:16px system-ui}'
          '.fv-margin-strip{background:#13221e;color:#ecd3a3;display:flex;gap:12px;overflow-x:auto}'
          '.fv-margin-strip__item{display:block;flex:0 0 200px;padding:14px}'
          '.fv-focus-cta{padding:40px 7%}.wp-block-jetpack-subscriptions{padding:32px 7%;background:#e6dcc3;color:#121414}</style>'
          '</head><body><p role="note" style="background:#673d20;color:white;padding:10px;text-align:center">'
          'NON-PRODUCTION FIXTURE — SYNTHETIC MARGINS &amp; JETPACK — NO SIGNUP</p>'
          +combined+'</body></html>')
    checks=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in [320,360,390,768,1024,1440,1920]:
            for js in (True,False):
                page=browser.new_page(viewport={'width':width,'height':900},
                                      java_script_enabled=js,reduced_motion='reduce')
                errors=[]
                page.on('pageerror',lambda error:errors.append(str(error)))
                page.set_content(html,wait_until='domcontentloaded',timeout=12000)
                sample=page.evaluate("""() => {
                    const ids=['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry',
                    'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'];
                    const v=e=>!!(e&&e.getClientRects().length&&getComputedStyle(e).visibility!=='hidden');
                    const focus=[...document.querySelectorAll('a[href="https://finalvestige.com/focus/"]')];
                    return {chapters:ids.filter(id=>document.getElementById(id)).length,
                     margins:document.querySelectorAll('.fv-margin-strip__item').length,
                     visibleArchive:v(document.querySelector('[data-fv-home-flagship]')),
                     visibleMargins:v(document.querySelector('.fv-margin-strip__item')),
                     signupPlaceholder:!!document.querySelector('.wp-block-jetpack-subscriptions'),
                     visibleFocus:focus.filter(v).length,
                     overflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
                     chapterNav:document.querySelectorAll('.fv-hf__chapter-nav a').length};
                }""")
                ok=(sample['chapters']==7 and sample['margins']==72 and
                    sample['visibleArchive'] and sample['visibleMargins'] and
                    sample['signupPlaceholder'] and sample['visibleFocus']>=1 and
                    sample['overflow']<=0 and sample['chapterNav']==7 and not errors)
                checks.append({'width':width,'js':js,'pass':ok,'metrics':sample,'errors':errors})
                page.close()
        browser.close()
    print(json.dumps({'status':'PASS' if all(x['pass'] for x in checks) else 'HOLD',
      'synthetic_browser_checks':len(checks),
      'passed':sum(x['pass'] for x in checks),
      'integrated_wordpress':False,'jetpack_functional':False,
      'failures':[x for x in checks if not x['pass']]},indent=2))
    if not all(x['pass'] for x in checks):raise SystemExit(1)

if __name__=='__main__':
    main()
