#!/usr/bin/env python3
"""Apollo R161 WordPress page 2017 gallery REGRESSION fixture, not release acceptance.

Read-only live editor source inspected 2026-11-06; last modified 2026-11-05T18:19:45.
The production JS uses querySelectorAll (correct) rather than the old singular
querySelector (which silently leaves all three photographs visible). This runner
executes the inspected gallery-selection excerpt in an offline controlled
Chromium fixture; it does NOT execute the installed WordPress page or axe-core.
"""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS=(320,360,390,768,1440,1920)
GALLERY_LOGIC=r"""
const photos = box.querySelectorAll('[data-fvx-chrono-photo]');
if (photos.length === 3) {
  const index = t < 6 ? 0 : (t < 11.3 ? 1 : 2);
  photos.forEach((photo, i) => {
    photo.hidden = i !== index;
    photo.classList.toggle('is-current', i === index);
  });
  const position = $(box, '[data-fvx-chrono-position]');
  if (position) {
    position.hidden = false;
    position.textContent = 'Context photo ' + (index + 1) + ' of 3 · These photographs do not depict the marked seconds.';
  }
}
"""
MARKERS=((0,'First verbal report of fire'),(6,'First indication of a cabin pressure increase'),
         (11.3,'Pressure exceeded sensor range'),(14.7,'Command Module pressure vessel ruptured'))
PHOTO_IDS=('S66-58038','S67-15717','KSC-20170124-PH_KLS01_0129')

def fixture(logic=GALLERY_LOGIC):
    markers=''.join(f'<li data-t="{t}">{title}</li>' for t,title in MARKERS)
    photos=''.join(f'<figure data-fvx-chrono-photo="{i}"><div class="photo" role="img" aria-label="Offline placeholder: {id}"></div><figcaption>NASA {id}; contextual photograph only, not fire telemetry. <a href="https://www.nasa.gov/">Original NASA source</a></figcaption></figure>' for i,id in enumerate(PHOTO_IDS))
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R161 Apollo gallery contract</title>
<style>*{{box-sizing:border-box}}body{{margin:0;background:#0c0d0d;color:#f4efe6;font:16px/1.6 system-ui}}main{{max-width:70rem;margin:auto;padding:1.25rem}}h1{{font:clamp(2rem,6vw,4rem)/1.1 Georgia}}section{{border:1px solid #807053;padding:1rem}}figure{{margin:0}}.photo{{height:12rem;background:linear-gradient(135deg,#323025,#161511)}}a{{color:#e9c995}}input{{width:100%;min-height:2.75rem}}[hidden]{{display:none!important}}:focus-visible{{outline:3px solid #ffe2a0;outline-offset:3px}}@media(prefers-reduced-motion:reduce){{*,*::before,*::after{{animation:none!important;transition:none!important}}}}</style></head>
<body><main><h1>Apollo 1 archival context</h1><p>These historical photographs do not depict the events represented by the chronology slider.</p><section data-fvx-chronology><h2>Recorded timing and independent archival views</h2>
<div data-fvx-chrono-tool hidden><label for="range">Seconds after first report of fire</label><input type="range" id="range" min="0" max="15" step="0.1" value="0"><p role="status" aria-live="polite" data-fvx-chrono-readout></p></div>
<ol>{markers}</ol><div>{photos}</div><p data-fvx-chrono-position hidden>Context only.</p></section>
<p><a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read original investigation</a></p></main>
<script>(()=>{{'use strict';const box=document.querySelector('[data-fvx-chronology]'),tool=box.querySelector('[data-fvx-chrono-tool]'),range=tool.querySelector('input'),out=tool.querySelector('[data-fvx-chrono-readout]');const $=(r,s)=>r.querySelector(s);function update(){{const t=Number(range.value);out.textContent='+'+t+' seconds; the images are context only.';{logic}}}range.addEventListener('input',update);update();tool.hidden=false;}})();</script></body></html>'''

def run(directory,chromium):
    output=Path(directory)
    if output.exists(): raise FileExistsError('A fresh evidence directory is required')
    output.mkdir(parents=True)
    checks=[];screens=[];errors=[]
    def check(width,name,value):checks.append({'width':width,'check':name,'pass':bool(value)})
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path=chromium,args=['--no-sandbox'])
        for width in WIDTHS:
            ctx=browser.new_context(viewport={'width':width,'height':800},reduced_motion='reduce',has_touch=width==390)
            page=ctx.new_page()
            page.on('pageerror',lambda error,w=width:errors.append([w,str(error)]))
            page.set_content(fixture(),wait_until='load')
            photos=page.locator('[data-fvx-chrono-photo]')
            slider=page.locator('#range')
            check(width,'three_photos',photos.count()==3)
            check(width,'initial_first_only',photos.nth(0).is_visible() and page.locator('[data-fvx-chrono-photo]:visible').count()==1)
            check(width,'progressive_tool_enabled',page.locator('[data-fvx-chrono-tool]').is_visible())
            slider.fill('6')
            check(width,'second_at_6',photos.nth(1).is_visible() and page.locator('[data-fvx-chrono-photo]:visible').count()==1)
            slider.fill('11.3')
            check(width,'third_at_11_3',photos.nth(2).is_visible() and page.locator('[data-fvx-chrono-photo]:visible').count()==1)
            check(width,'explicit_no_fire_photo_claim','do not depict the marked seconds' in page.locator('[data-fvx-chrono-position]').inner_text())
            slider.focus();page.keyboard.press('Home')
            check(width,'keyboard_home',photos.nth(0).is_visible())
            page.keyboard.press('End')
            check(width,'keyboard_end',photos.nth(2).is_visible())
            check(width,'three_original_source_links',page.locator('figure a[href*="nasa.gov"]').count()==3)
            check(width,'no_checkout_or_utm',page.locator('a[href*="payhip"],a[href*="awin"],form').count()==0)
            check(width,'responsive_no_horizontal_overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
            check(width,'no_script_exception',not any(e[0]==width for e in errors))
            nojs=browser.new_context(viewport={'width':width,'height':800},java_script_enabled=False)
            bare=nojs.new_page();bare.set_content(fixture(),wait_until='load')
            check(width,'no_js_all_three_visible',bare.locator('[data-fvx-chrono-photo]:visible').count()==3)
            check(width,'no_js_control_hidden',not bare.locator('[data-fvx-chrono-tool]').is_visible())
            check(width,'no_js_no_horizontal_overflow',bare.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
            nojs.close()
            page.set_content(fixture(),wait_until='load')
            path=output/f'gallery-{width}.png';page.screenshot(path=str(path),full_page=True,animations='disabled')
            screens.append({'width':width,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
            ctx.close()
        bad=browser.new_page()
        bad.set_content(fixture(GALLERY_LOGIC.replace('box.querySelectorAll(', 'box.querySelector(')),wait_until='load')
        check('negative_control','old_selector_is_detected',
              bad.locator('[data-fvx-chrono-photo]:visible').count()==3 and bad.locator('[data-fvx-chrono-position]').is_hidden())
        bad.close()
        browser.close()
    receipt={'source':'Read-only WordPress editor Page 2017, modified 2026-11-05T18:19:45',
             'scope':'OFFLINE CHROMIUM EXCERPT FIXTURE; not a live or full WordPress page test',
             'passed':sum(c['pass'] for c in checks),'total':len(checks),'checks':checks,
             'screenshots':screens,'runtime_errors':errors,
             'axe':'NOT_EXECUTED','installed_wordpress':'NOT_TESTED',
             'real_page_lcp_cls':'NOT_MEASURED','release':'STAGING_HOLD'}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    (output/'SHA256SUMS').write_text(''.join(f'{s["sha256"]}  gallery-{s["width"]}.png\n' for s in screens))
    print(f"PASS {receipt['passed']}/{receipt['total']}; axe NOT_EXECUTED; STAGING_HOLD")
    if receipt['passed']!=receipt['total']:raise SystemExit(1)

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',required=True)
    ap.add_argument('--chromium',default='/usr/bin/chromium')
    args=ap.parse_args()
    run(args.out,args.chromium)
