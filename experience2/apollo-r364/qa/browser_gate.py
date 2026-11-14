#!/usr/bin/env python3
"""Actual local Chromium/Playwright on real PHP output; NOT WordPress or axe-core."""
import json, subprocess, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz
R=Path(__file__).resolve().parents[3];EX=R/'experience2'; OUT=EX/'apollo-r364'/'QA';OUT.mkdir(parents=True,exist_ok=True)
php=EX/'apollo-r363'/'custody-guard.php'
cmd='define("ABSPATH",true); require '+json.dumps(str(php))+'; echo fv_apollo_r363_shortcode();'
body=subprocess.check_output(['php','-r',cmd],text=True)
style_path=EX/'apollo-r362'/'assets'/'research-crosswalk.css'
assert subprocess.check_output(['git','hash-object',str(style_path)],text=True).strip()=='600c2eb6a435f818262a26c39dad9142bb48ec94'
style=style_path.read_text()
assert body.count('data-fv-r363-source')==4 and body.count('data-fv-r363-editorial-cta')==1
fixture='<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Apollo R364</title><style>'+style+'</style></head><body><main>'+body+'</main></body></html>'
cases=[('nojs-320',320,False,16,'reduce','none',False),('zoom-320',320,True,64,'reduce','none',False),('touch-390',390,True,16,'reduce','none',True),('keyboard-768',768,True,16,'no-preference','none',False),('desktop-1440',1440,True,16,'no-preference','none',False),('forced-1920',1920,True,16,'reduce','active',False)]
results=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for name,width,js,font,motion,colors,touch in cases:
  ctx=b.new_context(viewport={'width':width,'height':900},java_script_enabled=js,reduced_motion=motion,forced_colors=colors,has_touch=touch)
  if js:
   ctx.add_init_script('''window.__vitals={cls:0,lcp:null}; try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(!e.hadRecentInput)window.__vitals.cls+=e.value}).observe({type:'layout-shift',buffered:true});new PerformanceObserver(l=>{for(const e of l.getEntries())window.__vitals.lcp=e.startTime}).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}''')
  page=ctx.new_page();page.set_content(fixture,wait_until='load')
  if font!=16:page.evaluate('(size)=>document.documentElement.style.fontSize=size+"px"',font)
  assert page.locator('[data-fv-r363-custody]').count()==1,name
  assert page.locator('[data-fv-r363-details]').count()==4,name
  assert page.locator('[data-fv-r363-source]').count()==4,name
  assert page.locator('[data-fv-r363-editorial-cta]').count()==1,name
  assert page.locator('img,iframe,video,script,form').count()==0,name
  assert not page.evaluate('document.documentElement.scrollWidth>window.innerWidth+1'),name
  summaries=page.locator('summary'); summaries.first.focus(); assert summaries.first.evaluate('(x)=>document.activeElement===x'),name
  if touch:
   summaries.first.tap();assert page.locator('details').first.get_attribute('open') is not None,name
  else:
   page.keyboard.press('Enter');assert page.locator('details').first.get_attribute('open') is not None,name
  sources=page.locator('[data-fv-r363-source]')
  assert all((z.get_attribute('href') or '').startswith('https://www.nasa.gov/') for z in sources.all()),name
  cdp=ctx.new_cdp_session(page);nodes=cdp.send('Accessibility.getFullAXTree')['nodes']
  named=[n.get('name',{}).get('value','') for n in nodes if n.get('role',{}).get('value')=='link' and not n.get('ignored')]
  # Only the expanded <details> link plus a free CTA should be AX-exposed.
  assert len(named)==2 and len(set(named))==2,name+':'+str(named)
  measures=page.evaluate('window.__vitals||null') if js else None
  page.screenshot(path=str(OUT/(name+'.png')),full_page=False)
  results.append({'name':name,'width':width,'js':js,'root_font_px':font,'touch':touch,'reduced_motion':motion,'forced_colors':colors,'ax_active_link_names':named,'horizontal_overflow':False,'local_fixture_vitals':measures,'pass':True})
  ctx.close()
 ctx=b.new_context(java_script_enabled=False,viewport={'width':390,'height':900});pg=ctx.new_page();pg.set_content(fixture,wait_until='load');pg.emulate_media(media='print')
 pdf=OUT/'r364-print-source.pdf';pdf.write_bytes(pg.pdf(format='A4',print_background=True));ctx.close()
 # Chromium meta-CSP enforcement: an INLINE injection must be blocked; proves meta only, not HTTP CSP.
 ctx=b.new_context();pg=ctx.new_page();viols=[];pg.on('console',lambda m:viols.append(m.text) if 'Content Security Policy' in m.text else None)
 pg.set_content('<html><head><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'none\'"></head><body><script>window.__unsafeExecuted=1</script></body></html>')
 assert pg.evaluate('window.__unsafeExecuted||0')==0,'meta CSP inline script blocked'
 ctx.close();b.close()
 printed=fitz.open(pdf)
 hrefs={x.get('uri') for page in printed for x in page.get_links() if (x.get('uri') or '').startswith('https://www.nasa.gov/')}
 ptext=' '.join(p.get_text() for p in printed)
 assert len(hrefs)==2,hrefs
 assert 'NOT CLEARED' in ptext and '102 deliberate ignitions' in ptext and '1967' in ptext and '2018' in ptext
 report={'pass':True,'chromium_cases':results,'pdf_pages':len(printed),'unique_pdf_nasa_links':len(hrefs),'r362_css_git_blob':'600c2eb6a435f818262a26c39dad9142bb48ec94','meta_csp_inline_script_blocked':True,'limitations':['No actual WordPress/Assembler','No native axe-core or independent screen reader','HTTP navigation blocked by execution environment: meta CSP is NOT HTTP-header CSP','Fixture vitals are NOT production Core Web Vitals','No authenticated merchant/paid conversion']}
 (OUT/'browser-result.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'chromium_cases':len(results),'pdf_pages':len(printed),'pdf_distinct_nasa_urls':len(hrefs),'meta_csp':True,'synthetic_lcp_ms':[z['local_fixture_vitals']['lcp'] for z in results if z['local_fixture_vitals']],'synthetic_cls':[z['local_fixture_vitals']['cls'] for z in results if z['local_fixture_vitals']]},indent=2))
