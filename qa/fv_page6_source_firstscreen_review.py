#!/usr/bin/env python3
"""Read-only Page 6 editor-HTML comparison; NOT a WordPress/Assembler staging test."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from playwright.sync_api import sync_playwright

WIDTHS = (320, 360, 390, 768, 1440, 1920)
IDS = ('fv-hf-title', 'fv-hf-chronicle', 'fv-hf-evidence', 'fv-hf-inquiry',
       'fv-hf-method-title', 'fv-hf-observer', 'fv-hf-mind-title')
OLD = '<a class="fv-hf__text-link" href="https://finalvestige.com/blog/">Read the investigations <span aria-hidden="true">↗</span></a>'
NEW = '<a class="fv-hf__text-link" href="https://finalvestige.com/focus/">Explore the free 52-page Focus Fieldbook <span aria-hidden="true">↗</span></a>'


def validate(raw):
    indices = [int(i) for i in re.findall(r'<span class="fv-margin-strip__item" style="--i:(\d+)">', raw)]
    gates = (indices == list(range(72)), raw.count('<div class="fv-hf fv-hf--wp alignfull" data-fv-home-flagship>') == 1,
             all(raw.count(f'id="{i}"') == 1 for i in IDS), raw.count(OLD) == 1,
             NEW not in raw, raw.count('jetpack/subscriptions') == 1,
             raw.count('<!-- wp:html -->') >= 2,
             raw.count('<!-- wp:html -->') == raw.count('<!-- /wp:html -->'),
             'https://finalvestige.com/focus/' in raw, '<style>' in raw)
    if not all(gates):
        raise ValueError('Page 6 source contract changed; fail closed')


def run(raw, out):
    validate(raw)
    if out.exists():
        raise ValueError('Refusing to overwrite previous receipts')
    out.mkdir(parents=True)
    proposed = raw.replace(OLD, NEW, 1)
    assert proposed.replace(NEW, OLD, 1) == raw
    receipt = {'status':'SOURCE_HTML_LAB_ONLY_NOT_WP_INTEGRATION',
               'source_sha256':hashlib.sha256(raw.encode()).hexdigest(),
               'source_utf8_bytes':len(raw.encode()), 'release_ready':False,
               'limitations':['no WordPress/Assembler theme shell or Jetpack',
                  'external resources blocked; not real image delivery',
                  'not WCAG 2.2 AA, Lighthouse/CWV, Safari or real native browser zoom',
                  'no verified leads/orders or net revenue'], 'variants':{}}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path='/usr/bin/chromium', headless=True,
                                     args=['--no-sandbox'])
        try:
            for name, markup in [('current',raw),('focus_proposal',proposed)]:
                ctx=browser.new_context(viewport={'width':390,'height':844},
                                        reduced_motion='reduce',java_script_enabled=False)
                ctx.route('**/*',lambda route: route.abort())
                page=ctx.new_page()
                page.set_content('<!doctype html><html lang="en"><head>'
                  '<meta name="viewport" content="width=device-width,initial-scale=1">'
                  '</head><body>'+markup+'</body></html>',wait_until='domcontentloaded')
                receipt['variants'][name]={}
                for width in WIDTHS:
                    page.set_viewport_size({'width':width,'height':844})
                    page.wait_for_timeout(80)
                    info=page.evaluate('''() => {
                      const a=document.querySelector('.fv-hf__opening-actions .fv-hf__text-link');
                      const b=a?.getBoundingClientRect();
                      return {href:a?.getAttribute('href'), text:a?.textContent.trim(),
                        top:b?.top??null, bottom:b?.bottom??null,
                        hit_target_44px:!!b && b.height>=44 && b.width>=44,
                        in_first_screen:!!b && b.top>=0 && b.bottom<=844,
                        horizontal_overflow:document.documentElement.scrollWidth>innerWidth+2,
                        visible_margins:[...document.querySelectorAll('.fv-margin-strip__item')]
                          .filter(n=>getComputedStyle(n).display!=='none').length,
                        reduced_motion:matchMedia('(prefers-reduced-motion: reduce)').matches};
                    }''')
                    path=f'{name}_{width}.png'
                    page.screenshot(path=str(out/path),full_page=False)
                    receipt['variants'][name][str(width)]=dict(info,screenshot=path)
                ctx.close()
        finally:
            browser.close()
    receipt['observations']={
      'focus_route_matches':all(x['href']=='https://finalvestige.com/focus/'
               for x in receipt['variants']['focus_proposal'].values()),
      'focus_above_fold_320_360_390':all(receipt['variants']['focus_proposal'][str(w)]['in_first_screen'] for w in (320,360,390)),
      'focus_touch_target_320_360_390':all(receipt['variants']['focus_proposal'][str(w)]['hit_target_44px'] for w in (320,360,390)),
      'all_72_margins_visible_reduced_motion':all(x['visible_margins']==72 for v in receipt['variants'].values() for x in v.values())}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--editor-source',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--output',type=Path,required=True)
    a=parser.parse_args()
    blob=a.editor_source.read_bytes()
    if not re.fullmatch('[0-9a-f]{64}',a.expected_sha256) or hashlib.sha256(blob).hexdigest()!=a.expected_sha256:
        parser.error('Source SHA-256 does not match the independently obtained export')
    r=run(blob.decode('utf-8'),a.output)
    print(json.dumps({'status':r['status'],'observations':r['observations'],'release_ready':False}))
