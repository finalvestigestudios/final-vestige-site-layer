#!/usr/bin/env python3
"""R348 genuine Chromium fixture: source-custody, no-JS, native print and responsive/keyboard QA."""
from pathlib import Path
import json,subprocess,re
import fitz
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
HERE=ROOT/'apollo-r348';OUT=HERE/'QA';OUT.mkdir(exist_ok=True)
PHP=HERE/'source-custody.php'
def render(two=False):
    php="define('ABSPATH',true);require '"+str(PHP)+"';echo fv_apollo_r348_experience_shortcode();"
    if two: php+="echo fv_apollo_r348_experience_shortcode();"
    return subprocess.check_output(['php','-r',php],text=True)
markup=render()
assets=[
 'apollo-r339/assets/chronology-rail.css',
 'apollo-r340/assets/accession-gallery.css',
 'apollo-r345/evidence-plate.css',
 'apollo-r347/assets/source-index.css',
 'apollo-r348/assets/source-custody.css'
]
css='\n'.join((ROOT/x).read_text() for x in assets)
js=(ROOT/'apollo-r347/assets/source-index.js').read_text()
assert markup.count('data-fv-custody-source')==8
assert markup.count('data-fv-apollo-source-link=')==13
assert markup.count('data-fv-r339-cta="editorial"')==1
assert markup.count('data-fv-custody-print')==8
assert '<img' not in markup and 'data-geo-pin' not in markup and 'payhip.com' not in markup

out=[]
cases=[
 (320,False,16,False,False,False),
 (390,True,16,True,False,False),
 (768,True,16,False,True,False),
 (1440,True,16,False,False,False),
 (1920,True,16,False,False,False),
 (320,True,64,False,False,False),
 (390,False,16,False,False,False),
 (768,True,16,False,False,True),
 (320,True,16,False,False,False),
 (1920,False,16,False,False,False),
]
with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width,enable_js,font,touch,reduced,forced in cases:
    context=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enable_js,is_mobile=touch,has_touch=touch,reduced_motion='reduce' if reduced else 'no-preference',forced_colors='active' if forced else 'none')
    page=context.new_page()
    errors=[];page.on('pageerror',lambda exc:errors.append(str(exc)))
    
    page.set_content('<!doctype html><html lang="en"><head><meta charset="UTF-8"><style>html{font-size:'+str(font)+'px}body{margin:0}'+css+'</style></head><body>'+markup+'</body></html>',wait_until='load')
    page.evaluate("""() => { window.__perf={lcp:null,cls:0}; try{new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__perf.lcp=e.startTime)).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)window.__perf.cls+=e.value})).observe({type:'layout-shift',buffered:true});}catch(e){window.__perf.error=String(e)} }""")
    if enable_js:page.add_script_tag(content=js)
    assert page.locator('[data-fv-apollo-custody]').count()==1
    assert page.locator('[data-fv-custody-source]').count()==8
    assert page.locator('[data-fv-apollo-entry]').count()==13
    assert page.locator('[data-fv-custody-approval="review-required"]').count()==0
    assert page.locator('[data-fv-r339-cta="editorial"]').count()==1
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),f'horizontal overflow width={width},rootfont={font}'
    all_links=page.locator('[data-fv-custody-source]').evaluate_all('(xs)=>xs.map(x=>x.href)')
    assert len(set(all_links))==8 and all(x.startswith('https://www.nasa.gov/') for x in all_links)
    assert not errors,errors
    # Detail content is accessible via native <summary>, keyboard or touch without JS.
    details=page.locator('.fv-apollo-r348__detail').first
    summary=details.locator('summary')
    assert details.get_attribute('open') is None
    summary.focus();page.keyboard.press('Enter')
    assert details.get_attribute('open') is not None
    assert details.locator('li').count()>=1
    summary.focus();page.keyboard.press('Enter')
    assert details.get_attribute('open') is None
    # Mobile pointer/touch path and Print including CLOSED details.
    if touch:
      summary.tap()
      assert details.get_attribute('open') is not None
      summary.tap()
    if enable_js:
      buttons=page.locator('.fv-apollo-r347__filters button')
      assert buttons.count()==5
      buttons.last.click()
      assert page.locator('.fv-apollo-r347__group:visible').count()==1
      assert page.locator('.fv-apollo-r348__page:visible').count()==8, 'filter must not hide custody crosswalk'
    else:
      assert page.locator('.fv-apollo-r347__group:visible').count()==4
    if (width,font,enable_js)==(390,16,True):
      pdf=page.pdf(format='A4',print_background=True)
      (OUT/f'r348-{width}-custody-dossier.pdf').write_bytes(pdf)
      doc=fitz.open(stream=pdf,filetype='pdf')
      words=' '.join(' '.join(v.get_text().split()) for v in doc)
      assert words.count('Evidence boundary:')>=26,f'PDF lost evidence limits: {words.count("Evidence boundary:")}'
      assert 'Original Board source' in words or '1967 Review Board' in words
      assert 'Not a map' in words or 'speculative map' in words
      # Print source identity proof, even when the <details> stayed CLOSED.
      assert 'Reviewed NASA source-page address' in words
      assert all(label in words for label in ['1967 Review Board','S67-15717','S67-21294'])
      links=[a.get('uri','') for v in doc for a in v.get_links() if a.get('kind')==2]
      assert sum('www.nasa.gov/' in x for x in links)>=8
      doc.close()
    if width in (320,390,1440) and font==16 and not forced:
      page.screenshot(path=str(OUT/f"r348-{width}-{'js' if enable_js else 'nojs'}.png"),full_page=True)
    if font==64:page.screenshot(path=str(OUT/'r348-320-font64.png'),full_page=True)
    page.wait_for_timeout(250)
    perf=page.evaluate('window.__perf')
    out.append(dict(width=width,js=enable_js,root_font=font,touch=touch,reduced_motion=reduced,forced_colors=forced,approved_sources=8,source_references=13,overflow=False,keyboard_details=True,local_lcp_ms=perf['lcp'],observed_cls=perf['cls'],passed=True))
    context.close()
  # Duplicate instances: no shared IDs, native source disclosures independently toggle.
  ctx=browser.new_context(viewport={'width':390,'height':900})
  page=ctx.new_page()
  page.set_content('<html lang="en"><head><style>'+css+'</style></head><body>'+render(two=True)+'</body></html>')
  page.add_script_tag(content=js)
  ids=page.locator('[id]').evaluate_all('(xs)=>xs.map(x=>x.id)')
  assert len(ids)==len(set(ids)), 'duplicate HTML IDs'
  assert page.locator('[data-fv-apollo-custody]').count()==2
  first=page.locator('[data-fv-apollo-custody]').first.locator('summary').first
  first.click()
  assert page.locator('[data-fv-apollo-custody]').first.locator('details[open]').count()==1
  assert page.locator('[data-fv-apollo-custody]').nth(1).locator('details[open]').count()==0
  ctx.close()
  browser.close()
receipt={'result':'PASS','browser':'real installed /usr/bin/chromium via Python Playwright','contexts':out,'native_pdf':'PASS at 390px with closed source drawers and active Photos-only filter','duplicates':'PASS','limitations':['Chromium local PHP HTML fixture, not WordPress/Assembler/CDN','synthetic fixture LCP/CLS only','genuine axe-core, screen readers, Firefox and WebKit not executed','no production commerce or qualified-human revenue data']}
(OUT/'r348-acceptance.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS: 10 real Chromium contexts; 8 unique approved source pages; 13 references; keyboard/touch/no-JS; PDF custody; duplicate instances')
