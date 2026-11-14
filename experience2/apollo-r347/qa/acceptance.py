#!/usr/bin/env python3
"""Real Chromium fixture, source-controlled R347 index; print, no-JS, touch, keyboard, reduced-motion and CSS QA."""
from pathlib import Path
import json,subprocess,hashlib
import fitz
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
R347=ROOT/'apollo-r347'; OUT=R347/'QA';OUT.mkdir(exist_ok=True)
php=R347/'source-index.php'
markup=subprocess.check_output(['php','-r',"define('ABSPATH',true);require '"+str(php)+"';echo fv_apollo_r347_experience_shortcode();"],text=True)
css='\n'.join((ROOT/x).read_text() for x in ('apollo-r339/assets/chronology-rail.css','apollo-r340/assets/accession-gallery.css','apollo-r345/evidence-plate.css','apollo-r347/assets/source-index.css'))
js=(R347/'assets/source-index.js').read_text()
assert markup.count('data-fv-apollo-entry=')==13
assert markup.count('data-fv-r339-cta="editorial"')==1
assert markup.count('data-fv-apollo-source-link=')==13
assert '<img' not in markup and 'payhip.com' not in markup and 'data-geo-pin' not in markup
assert len(set(__import__('re').findall(r'data-fv-apollo-source-link="([^"]+)"',markup)))==4
RESULTS=[]
with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  cases=[(320,False,16,False,False,False),(390,True,16,True,False,False),(768,True,16,False,True,False),(1440,True,16,False,False,False),(1920,True,16,False,False,False),(320,True,64,False,False,False),(390,False,16,False,False,False),(768,True,16,False,False,True)]
  for width,enable_js,font,touch,reduced,forced in cases:
    c=browser.new_context(viewport={'width':width,'height':900},java_script_enabled=enable_js,has_touch=touch,is_mobile=touch,reduced_motion='reduce' if reduced else 'no-preference',forced_colors='active' if forced else 'none')
    page=c.new_page()
    page.set_content('<!doctype html><html lang="en"><head><meta charset="utf-8"><style>html{font-size:'+str(font)+'px}body{margin:0}'+css+'</style></head><body>'+markup+'</body></html>',wait_until='load')
    if enable_js:page.add_script_tag(content=js)
    assert page.locator('[data-fv-apollo-entry]').count()==13
    assert page.locator('a[data-fv-apollo-source-link]').count()==13
    assert page.locator('[data-fv-r339-cta="editorial"]').count()==1
    assert page.locator('[data-fv-apollo-source-index] [data-fv-apollo-group]').count()==4
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'),f'overflow {width}/{font}'
    assert page.locator('[data-fv-apollo-source-index] a').count()==13
    hrefs=page.locator('[data-fv-apollo-source-index] a').evaluate_all('(links)=>links.map(x=>x.href)')
    assert all(x.startswith('https://www.nasa.gov/') for x in hrefs)
    assert len(set(hrefs))==8,f'expected 8 unique NASA URLs; got {len(set(hrefs))}'
    if enable_js:
      buttons=page.locator('.fv-apollo-r347__filters button');assert buttons.count()==5
      photos=page.get_by_role('button',name='Photographs').first;photos.focus();page.keyboard.press('Enter')
      assert photos.get_attribute('aria-pressed')=='true'
      assert page.locator('.fv-apollo-r347__group:visible').count()==1
      assert page.locator('.fv-apollo-r347__group:visible [data-fv-apollo-entry]').count()==4
      assert '4 of 13' in page.locator('[data-fv-apollo-status]').inner_text()
      # Even if filtered, print must expose every classified record, not just the selected subset.
      if width==390 or font==64:
        pdf=page.pdf(format='A4',print_background=True)
        doc=fitz.open(stream=pdf,filetype='pdf')
        words=' '.join(' '.join(d.get_text().split()) for d in doc)
        assert 'Board findings' in words and 'Later NASA history' in words and 'Contextual photographs' in words
        assert 'S67-21294' in words
        links=[a.get('uri','') for d in doc for a in d.get_links() if a.get('kind')==2]
        assert any('nasa.gov/' in x for x in links)
        if width==390:(OUT/'r347-390-source-index.pdf').write_bytes(pdf)
        doc.close()
      page.get_by_role('button',name='All records').first.click()
      assert page.locator('.fv-apollo-r347__group:visible').count()==4
    else:
      assert page.locator('.fv-apollo-r347__filters:visible').count()==0
      assert page.locator('.fv-apollo-r347__group:visible').count()==4
    if width in (320,390,1440) and font==16 and not forced:
      page.screenshot(path=str(OUT/f"r347-{width}-{'js' if enable_js else 'nojs'}.png"),full_page=True)
    if font==64:page.screenshot(path=str(OUT/'r347-320-font64.png'),full_page=True)
    RESULTS.append(dict(width=width,js=enable_js,root_font=font,touch=touch,reduced_motion=reduced,forced_colors=forced,source_links=13,unique_NASA_pages=8,overflow=False,passed=True))
    c.close()
  # Same page: two source indexes retain separate instance IDs and independent filter state.
  c=browser.new_context(viewport={'width':390,'height':900});page=c.new_page()
  pair=subprocess.check_output(['php','-r',"define('ABSPATH',true);require '"+str(php)+"';echo fv_apollo_r347_experience_shortcode();echo fv_apollo_r347_experience_shortcode();"],text=True)
  page.set_content('<html lang="en"><head><style>'+css+'</style></head><body>'+pair+'</body></html>')
  page.add_script_tag(content=js)
  ids=page.locator('[id]').evaluate_all('(xs)=>xs.map(x=>x.id)');assert len(ids)==len(set(ids))
  buttons=page.get_by_role('button',name='Photographs');assert buttons.count()==2;buttons.first.click()
  assert page.locator('[data-fv-apollo-source-index]').nth(0).locator('.fv-apollo-r347__group:visible').count()==1
  assert page.locator('[data-fv-apollo-source-index]').nth(1).locator('.fv-apollo-r347__group:visible').count()==4
  c.close();browser.close()
receipt={'result':'PASS','browser':'system Chromium via Playwright','contexts':RESULTS,'duplicate_instance_ids':'PASS','isolated_filter_state':'PASS','native_pdf':'PASS subset (390px and 320px/400% root text)','limitations':['local set_content fixture, not installed WordPress','no axe-core or independent screen reader','no live LCP/CLS or hosted CI','no social or merchant attribution']}
(OUT/'r347-acceptance.json').write_text(json.dumps(receipt,indent=2)+'\n')
print('PASS 8 real Chromium configurations, duplicate instances, 13 canonical records, 8 unique NASA pages, 1 editorial CTA, native PDF source retention')
