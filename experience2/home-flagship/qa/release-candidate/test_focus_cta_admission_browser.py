"""Real Chromium + nine adversarial controls for Focus hero admission, offline only.

No WordPress writes, no affiliate/analytics activation, no customer data.
Fixture ≠ exact WordPress/Assembler qualification.
Run: python experience2/home-flagship/qa/release-candidate/test_focus_cta_admission_browser.py
"""
import json
import os
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
from focus_cta_admission import REQUIRED, inspect_focus_entry

OUT=Path(os.environ.get("FV_EX2_QA_OUT", str(Path(__file__).parent / "evidence")))
OUT.mkdir(parents=True,exist_ok=True)
CSS='''body{margin:0;background:#0b0b0a;color:#f4e7d5;font:16px Georgia,serif}
.fv-hf{width:100%;overflow:clip}.fv-hf__opening-actions{display:flex;flex-wrap:wrap;gap:18px;align-items:center;padding:6px 0}
.fv-hf__opening{padding:45px max(20px,7vw);max-width:1250px;min-height:480px}
h1{font-size:clamp(40px,6vw,88px);line-height:1.05;margin:20px 0}
p{max-width:580px;line-height:1.7}
a{color:#f9d58e;text-underline-offset:5px}.fv-hf__button{display:inline-flex;min-height:48px;padding:5px 15px;align-items:center;background:#c19b61;color:#130f0a}
.fv-hf__opening-copy{min-width:0}.fv-hf__text-link--focus{display:block;min-height:44px;min-width:0;max-width:100%;white-space:normal;overflow-wrap:anywhere;line-height:1.45}
@media(max-width:600px){.fv-hf__opening-actions{display:grid}.fv-hf__text-link--focus{width:100%}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}'''
BASE='''<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'''+CSS+'''</style><div class="fv-hf"><section class="fv-hf__opening"><div class="fv-hf__opening-copy"><p>Final Vestige Studios · primary evidence</p><h1>Find what <em>others miss.</em></h1><p>The record is still speaking. We follow its trail—and show our work.</p><div class="fv-hf__opening-actions"><a class="fv-hf__button" href="#fv-hf-evidence">Enter the evidence room ↗</a><a class="fv-hf__text-link--focus" href="https://finalvestige.com/focus/">Explore the free 52-page Focus Fieldbook ↗</a></div></div></section><section id="fv-hf-evidence" style="min-height:500px">Evidence room</section></div></html>'''

negatives={
'no_focus_action':lambda s:s.replace('<a class="fv-hf__text-link--focus" href="https://finalvestige.com/focus/">Explore the free 52-page Focus Fieldbook ↗</a>',''),
'wrong_destination':lambda s:s.replace('https://finalvestige.com/focus/','https://example.invalid/promo'),
'commercial_mislabel':lambda s:s.replace('free 52-page Focus Fieldbook','buy our brain-reprogramming product'),
'undersized_touch':lambda s:s.replace('min-height:44px;min-width:0','min-height:12px;min-width:0'),
'hidden_link':lambda s:s.replace('display:block;min-height:44px','display:none;min-height:44px'),
'extra_hero_link':lambda s:s.replace('</div></div></section>','<a href="/extra">Third action</a></div></div></section>'),
'focus_inert':lambda s:s.replace('class="fv-hf__text-link--focus"','inert class="fv-hf__text-link--focus"'),
'focus_obstructed':lambda s:s.replace('</style>','</style><style>body:after{content:"";position:fixed;inset:0;background:transparent;z-index:9999}</style>'),
'outside_viewport':lambda s:s.replace('width:100%}}','width:100%;transform:translateX(160vw)}}'),
}
results=[]
with sync_playwright() as p:
    b=p.chromium.launch(headless=True, executable_path=shutil.which('chromium'),args=['--no-sandbox'])
    for w in (320,360,390,768,1440,1920):
        c=b.new_context(viewport={'width':w,'height':900},reduced_motion='reduce',java_script_enabled=False)
        page=c.new_page();page.set_content(BASE)
        checks=inspect_focus_entry(page.main_frame,w)
        failed=[k for k,v in checks.items() if not v]
        results.append({'case':'positive','width':w,'checks':checks,'pass':not failed})
        if w in (390,1440):page.screenshot(path=str(OUT/f'focus-{w}.png'))
        print('POS',w,'PASS' if not failed else 'FAIL '+str(failed))
        c.close()
    for name,change in negatives.items():
        c=b.new_context(viewport={'width':390,'height':900},reduced_motion='reduce')
        page=c.new_page();page.set_content(change(BASE))
        checks=inspect_focus_entry(page.main_frame,390)
        rejected=not all(checks.values())
        results.append({'case':name,'width':390,'checks':checks,'pass':rejected})
        print('NEG',name,'REJECT' if rejected else 'FALSE_PASS')
        c.close()
    b.close()
(OUT/'results.json').write_text(json.dumps(results,indent=2))
assert all(x['pass'] for x in results),[x for x in results if not x['pass']]
print(f'{len(results)}/{len(results)} browser acceptance checks passed, including {len(negatives)} adversarial controls')
