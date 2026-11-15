#!/usr/bin/env python3
"""Actual Chromium R374 source-custody regressions. Fixture ONLY, not WordPress acceptance."""
import hashlib
import json
from pathlib import Path
import subprocess
from playwright.sync_api import sync_playwright
from staging_acceptance import (
    r374_snapshot,r374_digest,R374_CUSTODY_SHA256,R374_CSS_SHA256,
    R374_STAGE_LINKS, EXPECTED_NASA,inspect_dom
)

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parents[1]/'QA'
OUT.mkdir(parents=True,exist_ok=True)
css=(ROOT/'experience2/apollo-r372/assets/evidence-path.css').read_bytes()
assert hashlib.sha256(css).hexdigest()==R374_CSS_SHA256
html=subprocess.check_output(['php',str(ROOT/'experience2/apollo-r372/qa/fixture.php')],text=True)
cases=[]
def check(p,name,ok):
    fingerprint=r374_digest(r374_snapshot(p))
    good=fingerprint==R374_CUSTODY_SHA256
    assert good==ok,(name,good,fingerprint)
    cases.append({'case':name,'integrity_pass':good,'digest':fingerprint})

with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    contexts=[
      ('mobile-320',320,False,False,False,False,False),
      ('mobile-390',390,False,False,False,False,False),
      ('tablet-768',768,False,False,False,False,False),
      ('desktop-1440',1440,False,False,False,False,False),
      ('wide-1920',1920,False,False,False,False,False),
      ('nojs-320',320,True,False,False,False,False),
      ('root4x-320',320,False,True,False,False,False),
      ('reduced-390',390,False,False,True,False,False),
      ('forced-320',320,False,False,False,True,False),
      ('touch-390',390,False,False,False,False,True),
    ]
    for name,width,nojs,root4x,reduced,forced,touch in contexts:
        ctx=browser.new_context(viewport={'width':width,'height':860},
            java_script_enabled=not nojs,has_touch=touch,
            reduced_motion='reduce' if reduced else 'no-preference',
            forced_colors='active' if forced else 'none')
        p=ctx.new_page()
        p.set_content(html)
        if root4x:p.add_style_tag(content='html{font-size:64px!important}')
        check(p,name,True)
        assert not p.evaluate('document.documentElement.scrollWidth>innerWidth+1'),name+' overflow'
        p.screenshot(path=str(OUT/(name+'.png')),full_page=True,animations='disabled')
        if name=='desktop-1440':
            p.emulate_media(media='print')
            p.pdf(path=str(OUT/'source-custody-print.pdf'),format='A4',print_background=True)
        ctx.close()
    p=browser.new_page()
    mutations=[
      ('swapped-source-order',"""let a=document.querySelectorAll('[data-fv-nasa-source]');[a[1].href,a[2].href]=[a[2].href,a[1].href]"""),
      ('reorder-event',"""let o=document.querySelector('.fv-apollo-r372__stages');o.insertBefore(o.children[2],o.children[0])"""),
      ('remove-event',"""document.querySelector('[data-fv-evidence-stage]').remove()"""),
      ('duplicate-event',"""let o=document.querySelector('.fv-apollo-r372__stages');o.append(o.children[0].cloneNode(true))"""),
      ('rewrite-probable-as-certain',"""document.querySelector('.fv-apollo-r372__claim').textContent='A definitive ignition source was proven'"""),
      ('erase-uncertainty',"""document.querySelector('.fv-apollo-r372__limit').textContent='No limits'"""),
      ('false-licensed-images',"""document.querySelector('.fv-apollo-r372__source').textContent='NASA photos commercially licensed'"""),
      ('remove-native-summary',"""document.querySelector('[data-fv-source-drawer]>summary').remove()"""),
      ('remove-print-citation',"""document.querySelector('[data-fv-evidence-stage] a[data-fv-print-source]').remove()"""),
      ('alter-retrospective',"""document.querySelector('[data-fv-nasa-context]').href='https://www.nasa.gov/'"""),
      ('alter-commerce-cta',"""document.querySelector('[data-fv-free-cta]').href='https://store.example/buy-now'"""),
      ('duplicate-cta',"""document.querySelector('.fv-apollo-r372__cta').append(document.querySelector('[data-fv-free-cta]').cloneNode(true))"""),
      ('delete-offer-disclosure',"""document.querySelector('.fv-apollo-r372__note').remove()"""),
      ('duplicate-entire-component',"""document.body.append(document.querySelector('[data-fv-apollo-path]').cloneNode(true))"""),
      ('outside-root-source-decoy',"""document.body.append(document.querySelector('[data-fv-nasa-source]'))"""),
    ]
    for name,mutation in mutations:
        p.set_content(html)
        p.evaluate('() => {'+mutation+'}')
        check(p,name,False)
        if name=='swapped-source-order':
            # Previous R373 unordered-URL membership test would miss this incorrect claim/source join.
            assert set(inspect_dom(p)['nasa_urls'])==EXPECTED_NASA
    browser.close()
report={'status':'LOCAL_CHROMIUM_CUSTODY_PASS_NOT_STAGING',
  'baseline_contexts':len(contexts),'adversarial_rejections':len(mutations),
  'checks':len(cases),'axe_core':'NOT_EXECUTED','WordPress_Assembler':'NOT_EXECUTED',
  'HTTP_CSP':'NOT_EXECUTED','net_revenue':'NOT VERIFIED','cases':cases}
(OUT/'results.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
print(report['status'],report['checks'],'cases')
