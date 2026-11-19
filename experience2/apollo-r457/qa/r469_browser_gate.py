#!/usr/bin/env python3
"""R469 real local Chromium rendering, interactions, print/PDF custody.
Uses set_content due browser policy blocking HTTP/file navigations. Never presents
LCP/CLS as navigated or genuine axe-core as executed in this environment.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json,subprocess,hashlib
import fitz
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'QA'/'r469'
OUT.mkdir(parents=True,exist_ok=True)
markup=subprocess.check_output(['php','-r',f'require {json.dumps(str(ROOT/"apollo_rights_gallery.php"))};echo fv457_render();'],text=True)
html='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head><body style="margin:0">'+markup+'</body></html>'
soup=BeautifulSoup(html,'html.parser')
assert not soup.find('a',href='https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129')
assert len(soup.select('details'))==12
assert all(item.find('summary') for item in soup.select('details'))
assert len(set(tag.get('id') for tag in soup.select('[id]')))==len(soup.select('[id]'))
results={'method':'Playwright Chromium, locally rendered PHP injected via set_content; NOT an installed WP staging URL',
         'navigated_lcp':'HOLD_NOT_RUN: navigation to 127.0.0.1, file and data URLs blocked by administrator',
         'navigated_cls':'HOLD_NOT_RUN: no successful navigation',
         'axe_core':'HOLD_NOT_RUN: pinned genuine axe bundle not present; manual DOM assertions are not axe',
         'cases':[]}
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-background-networking'])
 for width in (320,360,390,768,1024,1440,1920):
  for js in (False,True):
   ctx=b.new_context(viewport={'width':width,'height':900},device_scale_factor=1,java_script_enabled=js,has_touch=(width==390),reduced_motion='reduce',forced_colors='active' if width==768 else 'none')
   page=ctx.new_page();errors=[];page.on('pageerror',lambda x:errors.append(str(x)))
   page.set_content(html,wait_until='domcontentloaded');page.wait_for_timeout(35)
   assert not errors,errors
   assert page.locator('[data-fv457-card]').count()==6
   assert page.locator('[data-fv457-plate]').count()==3
   assert page.locator('.fv457__moment').count()==3
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(width,js)
   assert not page.locator('a[href="https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129"]').count()
   assert page.get_by_text('UNVERIFIED CATALOGUE LINK WITHHELD.').count()==1
   assert page.locator('a.fv457__cta').count()==0 # CTA is a paragraph wrapping one real link
   assert page.locator('.fv457__cta a').count()==1
   if js:
    button=page.get_by_role('button',name='NASA ID confirmed (4)')
    (button.tap() if width==390 else button.click())
    assert page.locator('[data-fv457-card]:visible').count()==4
    assert button.get_attribute('aria-pressed')=='true'
    page.get_by_role('button',name='Not in Atlas (3)').click()
    assert page.locator('[data-fv457-card]:visible').count()==3
    page.get_by_role('button',name='All six').focus();page.keyboard.press('Enter')
    assert page.locator('[data-fv457-card]:visible').count()==6
   else:
    assert page.locator('[data-fv457-card]:visible').count()==6
    assert not page.locator('[data-fv457-controls]').is_visible()
   if width in (390,1440):
    # Neutralize focus scroll/hover state before deterministic full-page capture.
    page.evaluate('document.activeElement instanceof HTMLElement && document.activeElement.blur(); window.scrollTo(0,0)')
    if js:page.mouse.move(1,1)
    page.wait_for_timeout(80)
    img=OUT/f'{width}-js{int(js)}.png';page.screenshot(path=str(img),full_page=True,animations='disabled')
   if width==390 and js:
    page.get_by_role('button',name='NASA ID confirmed (4)').click()
    page.emulate_media(media='print')
    pdf=OUT/'390-after-filter-print.pdf';pdf.write_bytes(page.pdf(print_background=True,format='A4',prefer_css_page_size=True))
    # Chromium embeds wall-clock creation dates: normalize metadata and trailer ID
    # before deterministic archival, without altering link annotations.
    unnormalized=fitz.open(pdf)
    meta={k: v for k,v in unnormalized.metadata.items() if k in ('title','author','subject','keywords','creator','producer','creationDate','modDate')}
    meta.update({'title':'FV Apollo Source Custody — R469 staging QA','creationDate':"D:20261118000000+00'00'",'modDate':"D:20261118000000+00'00'"})
    unnormalized.set_metadata(meta)
    normalized=OUT/'r469-normalized.tmp.pdf';unnormalized.save(normalized,garbage=4,deflate=True,no_new_id=1)
    unnormalized.close();normalized.replace(pdf)
    doc=fitz.open(pdf)
    urls={link.get('uri','') for pg in doc for link in pg.get_links() if link.get('kind')==fitz.LINK_URI}
    nasa={u for u in urls if 'nasa.gov' in u}
    assert len(nasa)==8,(len(nasa),sorted(nasa))
    assert 'https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129' not in urls
    assert 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/' in urls
    pdf_text=' '.join(pg.get_text() for pg in doc)
    assert 'UNVERIFIED CATALOGUE LINK WITHHELD.' in pdf_text
    assert 'KSC-20170124-PH_KLS01_0129' in pdf_text
    results['pdf']={'unique_verified_or_article_nasa_urls':len(nasa),'held_url_unlinked':True,'free_investigation_link_count':sum('finalvestige.com/' in u for u in urls),'page_count':doc.page_count}
    doc.close()
   results['cases'].append({'width':width,'js':js,'touch':width==390,'reduced_motion':'reduce','forced_colors':width==768,'result':'PASS'})
   ctx.close()
 b.close()
results['sha256']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(OUT.glob('*.png'))}
(OUT/'results.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
print('PASS R469: 14/14 browser contexts, PDF 8 NASA links + 1 free CTA, held source unlinked; axe/nav metrics HOLD_NOT_RUN')
