#!/usr/bin/env python3
"""FV EX2: offline PHP-rendered first-screen conversion acceptance.

Only accepts a local source-derived HTML file. Browser network is blocked.
Not a WordPress, Jetpack, WCAG, revenue, or Lighthouse certification.

Usage: python verify_short_phone_fold.py --html /path/to/php-rendered.html --css /path/to/flagship.css
"""
import argparse, json, pathlib
from playwright.sync_api import sync_playwright

VIEWPORTS = [(320,568),(360,640),(390,667),(768,1024),(1440,900),(1920,1080)]
JS = """() => {
const q=s=>document.querySelector(s), root=q('.fv-hf');
if(!root) throw Error('missing flagship');
const geo=e=>{let r=q(e)?.getBoundingClientRect();if(!r)throw Error('missing '+e);
 return {top:Math.round(r.top),bottom:Math.round(r.bottom),width:Math.round(r.width),height:Math.round(r.height)}};
return {hero:geo('.fv-hf__opening-actions .fv-hf__button'),
 header_focus:geo('.fv-hf__mast-cta'),contextual_focus:geo('.fv-hf__text-link--focus'),
 margins:root.querySelectorAll('.fv-margin-strip__item').length,
 chapters:root.querySelectorAll('.fv-hf__chapter-nav a').length,
 focus_links:[...root.querySelectorAll('a')].filter(a=>a.href==='https://finalvestige.com/focus/').length,
 overflow:Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth)};
}
"""

def validate(html, css):
    marker='/* FV EX2 — compact short-phone first-screen composition.'
    if marker not in css: raise AssertionError('exact CSS patch missing')
    css=css[css.rfind(marker):]
    if 'max-width: 360px' not in css or 'max-height: 700px' not in css:
        raise AssertionError('short-phone-specific CSS scope required')
    records=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page=browser.new_page()
        page.route('**/*', lambda request: request.abort())
        page.set_content(html,wait_until='domcontentloaded')
        for w,h in VIEWPORTS:
            page.set_viewport_size({'width':w,'height':h})
            before=page.evaluate(JS)
            sheet=page.add_style_tag(content=css)
            after=page.evaluate(JS)
            sheet.evaluate('(el)=>el.remove()')
            assert (after['margins'],after['chapters']) == (72,7),f'archive loss at {w}'
            assert after['focus_links']>=5, f'Focus funnel loss at {w}'
            assert after['overflow']==0,f'overflow at {w}'
            assert after['header_focus']['bottom']<=h,f'header Focus is hidden at {w}'
            if w==320:
                assert before['hero']['bottom']>h, 'baseline blocker no longer reproducible; rebase and review'
                assert after['hero']['bottom']<=h,'evidence room CTA remains below first fold'
            if w>=390:
                assert before['hero']==after['hero'],'unintended non-small-screen visual regression'
            records.append({'width':w,'height':h,'before':before,'after':after})
        browser.close()
    return records

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--html',required=True,type=pathlib.Path)
    parser.add_argument('--css',required=True,type=pathlib.Path)
    parser.add_argument('--out',type=pathlib.Path)
    args=parser.parse_args()
    results=validate(args.html.read_text(),args.css.read_text())
    if args.out: args.out.write_text(json.dumps(results,indent=2)+'\n')
    print('PASS:',len(results),'PHP-derived Chromium viewport comparisons; baseline 320px fails fold, proposed fits')
