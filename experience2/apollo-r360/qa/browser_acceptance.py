#!/usr/bin/env python3
"""Additional local Chromium computed contrast and timing preflight, NOT axe or production CWV."""
import json,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
E=Path(__file__).resolve().parents[2];O=E/'apollo-r360/QA';O.mkdir(parents=True,exist_ok=True)
code='define("ABSPATH",true); require '+json.dumps(str(E/'apollo-r359/resolved-block-template-prehead.php'))+'; echo fv_apollo_r357_full();'
markup=subprocess.check_output(['php','-r',code],text=True)
css='\n'.join((E/x).read_text() for x in ('apollo-r339/assets/chronology-rail.css','apollo-r340/assets/accession-gallery.css','apollo-r345/evidence-plate.css','apollo-r347/assets/source-index.css','apollo-r348/assets/source-custody.css','apollo-r355/postfire-ledger.css','apollo-r356/assets/print-proof.css'))
html='<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0}'+css+'</style><body>'+markup+'</body></html>'
audit=r'''() => {
 const rgb=c=>{const m=c.match(/rgba?\(([^)]+)\)/);return m?m[1].split(',').slice(0,3).map(Number):null};
 const lum=c=>{const a=c.map(x=>x/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return .2126*a[0]+.7152*a[1]+.0722*a[2]};
 const contrast=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
 let tested=0,fail=[],small=[],minimum=99;
 for(const e of document.querySelectorAll('h1,h2,h3,h4,p,li,a,button,summary,dt,dd,label,span,strong')){
  if(!e.getClientRects().length||!e.textContent.trim())continue;
  const cs=getComputedStyle(e),fg=rgb(cs.color);if(!fg)continue;
  let bg=null,p=e;while(p){const c=getComputedStyle(p).backgroundColor;if(c.startsWith('rgb(')){bg=rgb(c);break}p=p.parentElement}bg ||= [255,255,255];
  const n=contrast(fg,bg),f=parseFloat(cs.fontSize),w=Number(cs.fontWeight)||400,required=f>=24||(f>=18.66&&w>=700)?3:4.5;
  tested++;minimum=Math.min(minimum,n);if(n<required-.01)fail.push({text:e.textContent.slice(0,40),contrast:n,required});
  if(e.matches('a,button,summary')){const r=e.getBoundingClientRect();if(r.width<24||r.height<24)small.push({text:e.textContent.slice(0,40),height:r.height,width:r.width})}
 }
 return {text_nodes:tested,minimum_ratio:+minimum.toFixed(2),contrast_failures:fail,small_controls:small};
}'''
res=[]
with sync_playwright() as pl:
 b=pl.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'],headless=True)
 for width,root,forced in [(320,16,'none'),(320,64,'none'),(390,16,'none'),(768,16,'none'),(1440,16,'none'),(1920,16,'active')]:
  c=b.new_context(viewport={'width':width,'height':900},forced_colors=forced,reduced_motion='reduce');page=c.new_page();page.set_content(html)
  page.evaluate('''() => {window.timing={lcp:[],cls:0};try{new PerformanceObserver(l=>l.getEntries().forEach(e=>timing.lcp.push(e.startTime))).observe({type:'largest-contentful-paint',buffered:true})}catch(e){}try{new PerformanceObserver(l=>l.getEntries().forEach(e=>{if(!e.hadRecentInput)timing.cls+=e.value})).observe({type:'layout-shift',buffered:true})}catch(e){}}''')
  if root!=16:page.evaluate('(n)=>document.documentElement.style.fontSize=n+"px"',root)
  page.locator('.fv-apollo-r355__source summary').focus();page.keyboard.press('Enter')
  r=page.evaluate(audit);assert not r['small_controls'],(width,r['small_controls']);assert forced=='active' or not r['contrast_failures'],(width,r['contrast_failures'])
  page.wait_for_timeout(170);timing=page.evaluate('window.timing')
  res.append({'width':width,'root_font':root,'forced_colors':forced,'contrast':r,'local_lcp_ms':round(max(timing['lcp']),1) if timing['lcp'] else None,'local_cls':timing['cls'],'pass':True});c.close()
 b.close()
(O/'computed-acceptance.json').write_text(json.dumps({'scope':'Local PHP-rendered Chromium only; approximate computed-color sampler, not axe-core, manual screen-reader testing or production CWV','cases':res,'pass':True},indent=2)+'\n')
print(json.dumps({'pass':len(res),'min_contrast':min(x['contrast']['minimum_ratio'] for x in res if x['forced_colors']=='none'),'lcp_ms':[x['local_lcp_ms'] for x in res]},indent=2))
