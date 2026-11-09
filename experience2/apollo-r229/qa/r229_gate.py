#!/usr/bin/env python3
"""R229 pinned Apollo rendered-content accessibility regression, local component QA only."""
import argparse, hashlib, json
from pathlib import Path
from playwright.sync_api import sync_playwright

PIN='28f1427da6d096c801927ac8e1e8dd8a53f14ff3f6fcb014089ada2bdd662413'
CTA='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
WIDTHS=(320,390,768,1440,1920)
AUDIT=r'''() => {
const faults=[];const require=(ok,code)=>{if(!ok)faults.push(code)};
const displayed=e=>e.getClientRects().length>0&&getComputedStyle(e).visibility!=='hidden';
const ids=[...document.querySelectorAll('[id]')].map(x=>x.id), known=new Set(ids);
require(ids.length===known.size,'duplicate-id');
for(const a of document.querySelectorAll('a')){
 const href=a.getAttribute('href');require(!!href,'empty-href');
 if(href&&href.startsWith('#'))require(known.has(decodeURIComponent(href.slice(1))),'broken-fragment');
 if(displayed(a))require(!!(a.getAttribute('aria-label')||a.textContent||'').trim(),'unnamed-link');
}
for(const e of document.querySelectorAll('[aria-labelledby],[aria-describedby],[aria-controls]')){
 for(const key of ['aria-labelledby','aria-describedby','aria-controls']){
  const raw=e.getAttribute(key);if(raw)for(const id of raw.trim().split(/\s+/))require(known.has(id),'broken-aria');
 }
}
const headings=[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(displayed);
require(headings.filter(x=>x.tagName==='H1').length===1,'h1-count');
let last=0;for(const h of headings){let level=+h.tagName[1];require(!last||level<=last+1,'heading-skip');last=level}
const ctas=[...document.querySelectorAll('a[href="__CTA__"]')];require(ctas.length===1,'cta-count');
if(ctas.length){let e=ctas[0],r=e.getBoundingClientRect();require(displayed(e),'cta-hidden');require(!!e.textContent.trim(),'cta-unnamed');require(r.width>=44&&r.height>=44,'cta-target');}
require(document.querySelectorAll('script').length===0,'script-injected');
require(document.querySelectorAll('[data-lat],[data-lng],[data-latitude],[data-longitude]').length===0,'invented-geo');
require(document.querySelectorAll('details>summary').length>=4,'missing-native-disclosures');
require(!!document.querySelector('a.skip[href^="#"]'),'missing-skip-link');
for(const im of document.querySelectorAll('img'))require(im.hasAttribute('alt'),'image-missing-alt');
const overflow=document.documentElement.scrollWidth-document.documentElement.clientWidth;
require(overflow<=1,'horizontal-overflow');
const color=s=>{let m=s.match(/rgba?\(([^)]+)\)/);if(!m)return null;let x=m[1].split(/[, ]+/).filter(Boolean).map(Number);return [...x.slice(0,3),x.length>3?x[3]:1]};
const lum=v=>v.slice(0,3).map(n=>{n/=255;return n<=.04045?n/12.92:((n+.055)/1.055)**2.4}).reduce((a,b,i)=>a+b*[.2126,.7152,.0722][i],0);
let ratios=[];const iter=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);
while(iter.nextNode()){
 const t=iter.currentNode;if(!t.nodeValue.trim())continue;
 const e=t.parentElement;if(!e||!displayed(e)||e.closest('script,style,template,svg'))continue;
 const style=getComputedStyle(e),fore=color(style.color);if(!fore)continue;
 let chain=[],n=e;for(;n;n=n.parentElement)chain.unshift(n);
 let bg=[255,255,255];for(const a of chain){const x=color(getComputedStyle(a).backgroundColor);if(x)bg=bg.map((v,i)=>v*(1-x[3])+x[i]*x[3]);}
 const fg=fore.slice(0,3).map((v,i)=>v*fore[3]+bg[i]*(1-fore[3]));
 const l=lum(fg),b=lum(bg),ratio=(Math.max(l,b)+.05)/(Math.min(l,b)+.05);
 const px=parseFloat(style.fontSize),bold=(parseInt(style.fontWeight)||400)>=700;
 require(ratio>=((px>=24||(px>=18.66&&bold))?3:4.5),'low-text-contrast');ratios.push(ratio);
}
require(ratios.length>=65,'insufficient-text-samples');
return {pass:faults.length===0,faults:[...new Set(faults)].sort(),text_samples:ratios.length,
  lowest_contrast:Math.round(Math.min(...ratios)*100)/100,link_count:document.querySelectorAll('a').length,
  heading_count:headings.length,overflow_px:overflow};
}'''.replace('__CTA__',CTA)

def sha(p):return hashlib.sha256(p).hexdigest()
def encode(o):return (json.dumps(o,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
def run(dist,out):
 assert sha((dist/'manifest.json').read_bytes())==PIN,'R228 manifest mismatch'
 files=json.loads((dist/'manifest.json').read_text())['files']
 for rel,hash_value in files.items():assert sha((dist/rel).read_bytes())==hash_value,'R228 file altered: '+rel
 css=(dist/'assets/atlas-scoped.css').read_text();html=(dist/'templates/atlas-fragment.html').read_text()
 doc='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>'
 out.mkdir(parents=True,exist_ok=True);rows=[];controls={}
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);version=browser.version
  for width in WIDTHS:
   for js in (False,True):
    ctx=browser.new_context(viewport={'width':width,'height':840},java_script_enabled=js,is_mobile=width<=390,has_touch=width<=390,
       reduced_motion='reduce' if width==320 else 'no-preference',forced_colors='active' if width==768 else 'none')
    page=ctx.new_page();requests=[];page.on('request',lambda r:requests.append(r.url));page.set_content(doc)
    result=page.evaluate(AUDIT);assert result['pass'],f'{width} JS={js}: {result["faults"]}'
    assert requests==[],f'Unexpected outbound requests: {requests}'
    shot=out/(str(width)+('-js' if js else '-nojs')+'.png');page.screenshot(path=str(shot),full_page=True,animations='disabled')
    ax=ctx.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
    roles={n.get('role',{}).get('value') for n in ax};assert 'heading' in roles and 'link' in roles
    disclosure=page.locator('details>summary').first
    if width<=390:disclosure.tap()
    else:disclosure.focus();page.keyboard.press('Enter')
    assert disclosure.evaluate('(x)=>x.parentElement.open'),'Native disclosure failed'
    rows.append(dict(width=width,javascript=js,**result,ax_heading=True,ax_link=True,disclosure=True,remote_requests=0,screenshot_sha256=sha(shot.read_bytes())))
    ctx.close()
  ctx=browser.new_context(viewport={'width':390,'height':840});pg=ctx.new_page()
  mutations={
    'duplicate-id':"document.querySelector('[id]').id=document.querySelectorAll('[id]')[1].id",
    'bad-fragment':"document.querySelector('a[href^=\"#\"]').href='#missing-record'",
    'hidden-cta':"document.querySelector('a.cta').style.display='none'",
    'unnamed-cta':"document.querySelector('a.cta').textContent=''",
    'low-contrast':"document.querySelector('.fv-apollo-atlas p').style.color='#111111'",
    'missing-h1':"document.querySelector('h1').remove()",
    'script-injection':"document.body.appendChild(document.createElement('script'))",
    'speculative-geo':"document.querySelector('.fv-apollo-atlas').setAttribute('data-lat','0')",
    'missing-img-alt':"let x=document.createElement('img');document.querySelector('.fv-apollo-atlas').appendChild(x)"}
  for key,mutation in mutations.items():
   pg.set_content(doc);pg.evaluate(mutation);check=pg.evaluate(AUDIT)
   assert not check['pass'],f'Missed adversarial edit: {key}';controls[key]=check['faults']
  ctx.close();browser.close()
 receipt=dict(status='PASS_LOCAL_ONLY',input_manifest_sha256=PIN,parent_head='4c7d903f0ac8e4a310fb97b3aed89edb60c3b426',
    chromium_version=version,contexts=rows,negative_controls=controls,axe_core='NOT_EXECUTED',installed_wordpress='NOT_TESTED',
    http_navigation='ADMIN_BLOCKED',field_lcp_cls='NOT_MEASURED',commercial='FREE investigation only; no approved paid Apollo offer',release='STAGING_HOLD')
 (out/'receipt.json').write_bytes(encode(receipt));return receipt

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--dist',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 a=p.parse_args();r=run(a.dist,a.out);print('PASS',len(r['contexts']),'Chromium contexts',len(r['negative_controls']),'mutation controls SHA',sha((a.out/'receipt.json').read_bytes()))
