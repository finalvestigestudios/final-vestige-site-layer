#!/usr/bin/env python3
"""R360 reproducible Chromium evidence: local PHP fixture, NOT WordPress or axe-core."""
import json,subprocess,re
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz
E=Path(__file__).resolve().parents[2];O=E/'apollo-r360/QA';O.mkdir(parents=True,exist_ok=True)
php='define("ABSPATH",true);require '+json.dumps(str(E/'apollo-r359/resolved-block-template-prehead.php'))+';echo fv_apollo_r357_full();'
markup=subprocess.check_output(['php','-r',php],text=True)
css='\n'.join((E/x).read_text() for x in ('apollo-r339/assets/chronology-rail.css','apollo-r340/assets/accession-gallery.css','apollo-r345/evidence-plate.css','apollo-r347/assets/source-index.css','apollo-r348/assets/source-custody.css','apollo-r355/postfire-ledger.css','apollo-r356/assets/print-proof.css'))
js=(E/'apollo-r347/assets/source-index.js').read_text()
html='<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0}'+css+'</style><body>'+markup+'</body></html>'
cases=[('nojs-320',320,False,False,16,'none'),('zoom-320',320,True,False,64,'none'),('touch-390',390,True,True,16,'none'),('keyboard-768',768,True,False,16,'none'),('desktop-1440',1440,True,False,16,'none'),('forced-1920',1920,True,False,16,'active')]
rows=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'],headless=True)
 for name,width,js_on,touch,font,forced in cases:
  ctx=b.new_context(viewport={'width':width,'height':900},java_script_enabled=js_on,has_touch=touch,forced_colors=forced,reduced_motion='reduce');page=ctx.new_page();page.set_content(html)
  if js_on: page.add_script_tag(content=js)
  if font!=16:page.evaluate('(x)=>document.documentElement.style.fontSize=x+"px"',font)
  assert page.locator('[data-fv-apollo-entry]').count()==13,name
  assert page.locator('[data-fv-custody-source]').count()==8,name
  assert page.locator('[data-fv-r339-cta="editorial"]').count()==1,name
  assert not page.evaluate('document.documentElement.scrollWidth>innerWidth+1'),name
  assert page.locator('img,iframe,video').count()==0,name
  ids=page.locator('[id]').evaluate_all('es=>es.map(e=>e.id)');assert len(ids)==len(set(ids)),name
  u=page.locator('a[href]').evaluate_all('es=>es.map(e=>e.href)');assert all(x.startswith('about:blank#') or re.match(r'^https://(www\.)?(nasa\.gov|finalvestige\.com)/',x) for x in u),name
  source=page.locator('.fv-apollo-r355__source summary');source.focus();page.keyboard.press('Enter');assert source.evaluate('e=>e.parentNode.open'),name
  link=page.locator('a[data-fv-r355-reviewed-source]');r=link.bounding_box();assert r and r['height']>=44,(name,r)
  if js_on:
   btns=page.locator('[data-fv-apollo-filters] button');assert btns.count()==5,name
   for text,count in [('Board findings',3),('Chronology',5),('Later history',1),('Photographs',4),('All records',13)]:
    btn=page.get_by_role('button',name=text,exact=True)
    if touch:btn.tap()
    else:btn.click()
    assert page.locator('[data-fv-apollo-entry]:visible').count()==count,name
    assert page.locator('[aria-pressed="true"]').count()==1,name
  else:assert page.locator('[data-fv-apollo-entry]:visible').count()==13,name
  ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes'];links=[n for n in ax if n.get('role',{}).get('value')=='link' and not n.get('ignored')]
  assert links and all(n.get('name',{}).get('value','').strip() for n in links),name
  page.screenshot(path=str(O/(name+'.png')),full_page=False)
  rows.append({'case':name,'source_target_height_css_px':r['height'],'named_links':len(links),'pass':True});ctx.close()
 page=b.new_page(viewport={'width':390,'height':900});page.set_content(html);page.add_script_tag(content=js)
 page.get_by_role('button',name='Photographs').click();page.emulate_media(media='print');pdf=O/'r360-print.pdf';pdf.write_bytes(page.pdf(format='A4',print_background=True));b.close()
with fitz.open(pdf) as d:
 t=' '.join(x.get_text() for x in d);assert '102 deliberate ignitions' in t and 'Evidence boundary' in t
 assert any('50-years-ago-apollo-flammability-tests' in (a.get('uri') or '') for x in d for a in x.get_links());pages=len(d)
(O/'compact-qa.json').write_text(json.dumps({'scope':'Real local Chromium/PHP fixture; not live WordPress, genuine axe-core, independent screen readers or production CWV','cases':rows,'print_pages':pages,'pass':True},indent=2)+'\n')
print('Chromium cases:',len(rows),'PASS; native PDF:',pages,'pages; 44px target PASS')
