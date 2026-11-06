#!/usr/bin/env python3
"""Fail-closed Chromium review of the exact PHP-embedded EX2 Blueprint source.

NOT WordPress/Assembler runtime, axe WCAG certification, real image loading, or CWV.
Runs with local Playwright and Chromium; aborts external requests.
"""
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

ANCHORS = ('fv-hf-evidence', 'fv-hf-title', 'fv-hf-chronicle',
           'fv-hf-inquiry', 'fv-hf-method-title', 'fv-hf-observer',
           'fv-hf-mind-title')
WIDTHS = (320, 360, 390, 768, 1440, 1920)

def extract(path):
    raw = Path(path).read_bytes()
    obj = json.loads(raw)
    assert len(obj['steps']) == 5, 'unexpected Blueprint step count'
    step = obj['steps'][2]
    assert step['step'] == 'writeFile' and step['path'].endswith('/fv-ex2-playground-review.php')
    plugin = step['data']
    def take(start, end):
        assert plugin.count(start) == 1 and plugin.count(end) == 1, 'source marker mismatch'
        return plugin.split(start, 1)[1].split(end, 1)[0]
    css = take("<<<'FVPG_CSS_END'\n", '\nFVPG_CSS_END\n')
    js = take("<<<'FVPG_JS_END'\n", '\nFVPG_JS_END\n')
    markup = take("<<<'FVPG_HTML_END'\n", '\nFVPG_HTML_END;')
    assert 'EX2 independent pointer-target review' in css, 'target fix missing'
    assert all(('id="' + a + '"') in markup for a in ANCHORS), 'chapter missing'
    assert markup.count('class="fv-margin-strip__item"') == 72, 'Margins mismatch'
    assert markup.count('href="https://finalvestige.com/focus/"') == 5, 'Focus mismatch'
    return css, js, markup, hashlib.sha256(raw).hexdigest()

def inspect(page):
    return page.evaluate("""() => {
      const elems=[...document.querySelectorAll('.fv-hf a,.fv-hf button,.fv-hf summary,.fv-hf input')];
      const short=elems.filter(e=>{
        const r=e.getBoundingClientRect(),s=getComputedStyle(e);
        return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'&&
          (r.width<23.5||r.height<23.5);
      }).map(e=>({element:e.tagName, text:(e.textContent||e.getAttribute('aria-label')||'').trim().slice(0,45)}));
      return {short, overflow:document.documentElement.scrollWidth>innerWidth+1,
        chapters:['fv-hf-evidence','fv-hf-title','fv-hf-chronicle','fv-hf-inquiry',
          'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'].filter(id=>document.getElementById(id)).length,
        margins:document.querySelectorAll('.fv-margin-strip__item').length,
        focus:document.querySelectorAll('a[href="https://finalvestige.com/focus/"]').length,
        heroFocusHeight:document.querySelector('.fv-hf__opening-actions .fv-hf__text-link--focus')?.getBoundingClientRect().height||0};
    }""")

def run():
    ap=argparse.ArgumentParser()
    ap.add_argument('--blueprint',required=True)
    ap.add_argument('--output',required=True)
    args=ap.parse_args()
    css,js,markup,sha=extract(args.blueprint)
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    receipt={'sha256':sha,'environment':'exact-source Chromium static fixture; NOT WordPress',
             'runs':[]}
    with sync_playwright() as p:
        chromium_bin=os.getenv('FV_CHROMIUM') or shutil.which('chromium') or shutil.which('chromium-browser')
        launch={'headless':True, 'args':['--no-sandbox']}
        if chromium_bin: launch['executable_path']=chromium_bin
        browser=p.chromium.launch(**launch)
        for width in WIDTHS:
            for mode in ('standard','nojs','reduce'):
                ctx=browser.new_context(viewport={'width':width,'height':900},
                    java_script_enabled=mode!='nojs',
                    reduced_motion='reduce' if mode=='reduce' else 'no-preference')
                page=ctx.new_page()
                page.route('**/*',lambda route:route.abort())
                html=('<!doctype html><html><head><meta name="viewport" '
                      'content="width=device-width,initial-scale=1"><style>'+css+
                      '</style></head><body>'+markup+
                      (('<script>'+js+'</script>') if mode!='nojs' else '')+'</body></html>')
                page.set_content(html, wait_until='domcontentloaded')
                page.wait_for_timeout(80)
                result=inspect(page)
                if result['short'] or result['overflow'] or result['heroFocusHeight'] < 43.5 or (result['chapters'],result['margins'],result['focus'])!=(7,72,5):
                    raise AssertionError(str((width,mode,result)))
                receipt['runs'].append({'width':width,'mode':mode,'small_targets':0,'passed':True})
                if width in (390,1440) and mode=='standard':
                    page.screenshot(path=str(out/('firstscreen_'+str(width)+'.png')))
                ctx.close()
        ctx=browser.new_context(viewport={'width':390,'height':900})
        page=ctx.new_page()
        page.route('**/*',lambda route:route.abort())
        page.set_content('<!doctype html><html><style>'+css+'</style>'+markup+'<script>'+js+'</script>',
                         wait_until='domcontentloaded')
        page.evaluate('document.body.style.zoom="2"')
        z=inspect(page)
        if z['overflow']:
            raise AssertionError('200% CSS zoom horizontal overflow')
        receipt['css_zoom_200']={'passed':True,'note':'CSS zoom fixture; not WordPress browser zoom'}
        ctx.close();browser.close()
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2))
    print('PASS: 18 exact-source Chromium viewport/mode runs; 200% CSS zoom. WP integration still HOLD.')
    print('Blueprint SHA256:',sha)

if __name__=='__main__':
    run()
