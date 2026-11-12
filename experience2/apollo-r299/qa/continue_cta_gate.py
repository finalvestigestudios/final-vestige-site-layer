#!/usr/bin/env python3
"""R299: Playwright actual PHP/no-JS one-CTA source-to-story contract.
Offline fixture only. Never equate this with axe, network CSP, WP or field CWV.
"""
import json,re,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
base=Path(__file__).resolve().parents[2]
markup=subprocess.check_output(['php','-r','parse_str("instances=2", $_GET);include $argv[1];',str(base/'apollo-r294/qa/local_http_fixture.php')],text=True)
css=(base/'apollo-r281/assets/apollo-source-experience.css').read_text()
markup=re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>','',markup).replace('</head>','<style>'+css+'</style></head>')
counts={'contexts':0,'native_keyboard':0,'negative_controls':0}
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for w in [320,390,768,1440,1920]:
  for js in [False,True]:
   page=browser.new_page(viewport={'width':w,'height':900},java_script_enabled=js,reduced_motion='reduce',has_touch=True)
   page.set_content(markup)
   assert page.locator('section.fv-r281').count()==2
   assert page.locator('footer.fv-r281__next a').count()==2
   assert page.locator('script,iframe,form').count()==0
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   ids=page.locator('[id]').evaluate_all('(xs)=>xs.map(x=>x.id)')
   assert len(ids)==len(set(ids))
   for section in page.locator('section.fv-r281').all():
    # Only one relevant next action: free investigation after 3 plates,
    # before the longer NASA source appendix and catalogue.
    assert section.locator('.fv-r281__plate').count()==3
    assert section.locator('a[href^="https://finalvestige.com/"]').count()==1
    assert section.locator('a[href*="nasa.gov/"]').count()>=12
    good=section.evaluate('s=>{const x=q=>s.querySelector(q);return !!(x(".fv-r281__plate:last-child").compareDocumentPosition(x("footer.fv-r281__next"))&4)&&!!(x("footer.fv-r281__next").compareDocumentPosition(x(".fv-r281__reconciliation"))&4)&&!!(x(".fv-r281__reconciliation").compareDocumentPosition(x(".fv-r281__gallery"))&4)}')
    assert good,'CTA after source appendix, rather than after chronology'
    cta=section.locator('footer.fv-r281__next a');cta.focus()
    assert cta.evaluate('(a)=>document.activeElement===a') and cta.is_visible()
    source=section.locator('.fv-r281__drawer').first
    source.locator('summary').focus();page.keyboard.press('Enter')
    assert source.get_attribute('open') is not None
    page.keyboard.press('Space');assert source.get_attribute('open') is None
    counts['native_keyboard']+=2
   # Negative control: deliberately relocate the first CTA after its source
   # catalogue and require the same placement predicate to reject it.
   page.locator('section.fv-r281').first.evaluate('s=>s.appendChild(s.querySelector("footer.fv-r281__next"))')
   bad=page.locator('section.fv-r281').first.evaluate('s=>!!(s.querySelector("footer.fv-r281__next").compareDocumentPosition(s.querySelector(".fv-r281__reconciliation"))&4)')
   assert not bad
   counts['negative_controls']+=1
   counts['contexts']+=1;page.close()
 browser.close()
print(json.dumps({'result':'PASS OFFLINE','counts':counts,'axe':'NOT EXECUTED','network_http_csp':'BLOCKED','wp':'NOT TESTED','field_cwv':'NOT TESTED'},sort_keys=True))
