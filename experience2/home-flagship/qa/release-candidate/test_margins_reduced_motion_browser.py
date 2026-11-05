"""Chromium reduced-motion release fixture (not WordPress/Assembler staging).
Run with python + playwright, local /usr/bin/chromium. No live CMS writes.
Factual note bodies are QA placeholders, never published historical claims.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

BASE = Path(__file__).resolve().parent
ORIGINAL = r'''
.fv-margin-strip{background:#0f100f;color:#d8d2c7;overflow:hidden}
.fv-margin-strip__inner{display:grid;grid-template-columns:auto minmax(0,1fr);align-items:center;gap:18px;max-width:1440px;margin:auto;padding:10px clamp(18px,4vw,44px)}
.fv-margin-strip__label{white-space:nowrap;color:#b8955e;font-size:10px;font-weight:800;letter-spacing:.16em;text-transform:uppercase}
.fv-margin-strip__window{position:relative;min-height:46px;overflow:hidden;padding-left:18px;border-left:1px solid #34322e}
.fv-margin-strip__item{position:absolute;left:18px;right:0;top:50%;transform:translateY(-38%);opacity:0;color:#d8d2c7;font-size:13px;line-height:1.35;filter:blur(7px);animation:fvMarginReveal 360s linear infinite;animation-delay:calc(var(--i)*5s)}
@keyframes fvMarginReveal{0%{opacity:0} .42%{opacity:1} 1.08%{opacity:1} 1.39%{opacity:0} 100%{opacity:0}}
@media(max-width:900px){.fv-margin-strip__inner{grid-template-columns:1fr;gap:7px;padding-top:12px;padding-bottom:12px}.fv-margin-strip__label{font-size:9px}.fv-margin-strip__window{min-height:58px;padding-left:16px}.fv-margin-strip__item{left:16px;font-size:12px}}
@media(max-width:520px){.fv-margin-strip__window{min-height:76px}.fv-margin-strip__item{line-height:1.4}}
@media(prefers-reduced-motion:reduce){.fv-margin-strip__window{height:auto;min-height:0;overflow:visible}.fv-margin-strip__item{position:relative;display:none;left:auto;right:auto;top:auto;transform:none;opacity:1;filter:none;animation:none;padding:2px 0 6px 16px}.fv-margin-strip__item:nth-child(1){display:block}}
'''

def fixture(patched):
    items=''.join(f'<span class="fv-margin-strip__item" style="--i:{i}">QA placeholder {i+1} of 72 — archival fragment visibility test.</span>' for i in range(72))
    add=(BASE/'margins_reduced_motion.css').read_text() if patched else ''
    return f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>html,body{{margin:0;background:#0a0a09;color:#eee;font:16px system-ui}}*{{box-sizing:border-box}}{ORIGINAL}\n{add}</style><main><h1 style="font-size:18px;padding:8px 16px">QA fixture — no WordPress installation</h1><div class="fv-margin-strip" role="region" aria-label="Hidden in the Margins"><div class="fv-margin-strip__inner"><div class="fv-margin-strip__label">Hidden in the Margins</div><div class="fv-margin-strip__window" tabindex="0" aria-label="Browse 72 archival notes">{items}</div></div></div></main></html>'''

def measure(page):
    return page.evaluate('''() => {
      const box=document.querySelector('.fv-margin-strip__window');
      const xs=[...document.querySelectorAll('.fv-margin-strip__item')];
      const visible=xs.filter(x=>getComputedStyle(x).display!=='none');
      return {total:xs.length,visible:visible.length,hidden:xs.length-visible.length,
        animations:[...new Set(xs.map(x=>getComputedStyle(x).animationName))],
        regionWidth:box.clientWidth,scrollWidth:box.scrollWidth,
        documentOverflow:document.documentElement.scrollWidth>window.innerWidth,
        position:getComputedStyle(xs[1]).position,
        focusable:box.tabIndex===0};
    }''')

def main():
    output=BASE/'reduced_motion_browser_evidence'
    output.mkdir(exist_ok=True)
    receipts=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        for width in [320,360,390,768,1279,1280,1440]:
            for patched in [False,True]:
                page=browser.new_page(viewport={'width':width,'height':900},reduced_motion='reduce',java_script_enabled=False)
                page.set_content(fixture(patched),wait_until='domcontentloaded')
                m=measure(page)
                assert m['total']==72 and not m['documentOverflow'],m
                assert m['focusable'] and m['visible']==(72 if patched else 1),m
                assert m['animations']==['none'],m
                if width in (390,1440):
                    page.screenshot(path=str(output/f'{"proposed" if patched else "published_css"}-{width}.png'))
                if patched:
                    assert m['scrollWidth']>m['regionWidth'],m
                    region=page.locator('.fv-margin-strip__window')
                    region.focus()
                    page.keyboard.press('ArrowRight')
                    page.wait_for_timeout(150)
                    assert page.evaluate("document.querySelector('.fv-margin-strip__window').scrollLeft")>0, 'keyboard cannot reach subsequent cards'
                receipts.append({'width':width,'variant':'proposed' if patched else 'published_source_reproduction','results':m,'result':'PASS'})
                page.close()
        page=browser.new_page(viewport={'width':390,'height':900},reduced_motion='no-preference',java_script_enabled=False)
        page.set_content(fixture(True))
        motion=measure(page)
        assert motion['position']=='absolute' and motion['animations']==['fvMarginReveal'],motion
        receipts.append({'width':390,'variant':'proposed_normal_motion_unchanged','results':motion,'result':'PASS'})
        page.close()
        browser.close()
    (output/'receipt.json').write_text(json.dumps({'source':'WordPress Page 6 modified 2026-11-04T14:39:24; source CSS reproduced; NOT a live-browser test','checks':receipts},indent=2))
    print('PASS:',len(receipts),'browser checks; reduced-motion published-source reproduction visible 1/72, proposed visible 72/72, keyboard ArrowRight passed on all seven widths')

if __name__=='__main__':
    main()
