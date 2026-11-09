#!/usr/bin/env python3
"""Read-only R242 Apollo contrast/print QA. Offline real Chromium, not WordPress or axe-core."""
import argparse,hashlib,json,subprocess
from pathlib import Path
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
PIN='f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
WIDTHS=(320,390,768,1440,1920)
CONTRAST=r'''() => {
 const rgb=s=>{let m=s.match(/rgba?\(([^)]+)\)/);if(!m)return [0,0,0,0];let v=m[1].split(',').map(Number);return [v[0],v[1],v[2],v[3]===undefined?1:v[3]]};
 const mix=(b,f)=>b.map((x,i)=>i<3?f[i]*f[3]+x*(1-f[3]):1);
 const lum=c=>{let v=c.slice(0,3).map(x=>{x/=255;return x<=.04045?x/12.92:Math.pow((x+.055)/1.055,2.4)});return .2126*v[0]+.7152*v[1]+.0722*v[2]};
 let w=document.createTreeWalker(document.querySelector('.fv-apollo-atlas'),NodeFilter.SHOW_TEXT),n,checked=0,worst=99,fail=[];
 while(n=w.nextNode()){if(!n.textContent.trim())continue;let e=n.parentElement,s=getComputedStyle(e),r=e.getBoundingClientRect();if(!r.height||!r.width||s.display==='none'||s.visibility==='hidden'||e.closest('details:not([open])'))continue;
 let a=[],q=e;while(q){a.unshift(q);q=q.parentElement}let bg=[255,255,255,1];for(const x of a)bg=mix(bg,rgb(getComputedStyle(x).backgroundColor));let fg=mix(bg,rgb(s.color));let x=lum(bg),y=lum(fg),ratio=(Math.max(x,y)+.05)/(Math.min(x,y)+.05);let size=parseFloat(s.fontSize),weight=parseInt(s.fontWeight)||400;let need=(size>=24||(size>=18.66&&weight>=700))?3:4.5;checked++;worst=Math.min(worst,ratio);if(ratio+.01<need)fail.push({text:n.textContent.trim().slice(0,70),ratio:Number(ratio.toFixed(2)),need}); }
 return {checked,worst:Number(worst.toFixed(2)),fail};
}'''
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--atlas',required=True,type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args();r=a.atlas
 assert sha((r/'manifest.json').read_bytes())==PIN
 manifest=json.loads((r/'manifest.json').read_text());assert manifest['not_live'] and manifest['status']=='STAGING_HOLD'
 for f,d in manifest['files'].items():assert sha((r/f).read_bytes())==d,f
 php=['php',str(r/'wp-render-shim-r224.php'),str((r/'fv-ex2-apollo-r224.php').resolve())]
 rendered=json.loads(subprocess.run(php+['normal'],check=True,capture_output=True,text=True).stdout)
 late=json.loads(subprocess.run(php+['late'],check=True,capture_output=True,text=True).stdout)
 assert rendered['html']==(r/'templates/atlas-fragment.html').read_text() and late['fallback']
 html=rendered['html'];s=BeautifulSoup(html,'html.parser');assert len(s.select('[data-fv-plate-source]'))==4 and len(s.select('a.cta'))==1
 assert len(s.select('.fv-apollo-print-custody a[href^="https://www.nasa.gov/"]'))>=8
 assert not s.select('script,svg,img,canvas,iframe,video,[data-latitude],[data-longitude]')
 dates=[t['datetime'] for t in s.select('#fv-apollo-chronology ol time[datetime]')];assert len(dates)>=5 and dates==sorted(dates)
 assert not a.out.exists(),'refuse overwrite';a.out.mkdir(parents=True)
 css=(r/'assets/atlas-scoped.css').read_text();doc='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style><body>'+html+'</body></html>'
 cases=[]
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width in WIDTHS:
   for js in (False,True):
    c=b.new_context(viewport={'width':width,'height':900},java_script_enabled=js,is_mobile=width<=390,has_touch=width<=390,reduced_motion='reduce',forced_colors='active' if width==768 else 'none')
    page=c.new_page();requests=[];page.on('request',lambda req:requests.append(req.url));page.set_content(doc)
    assert not requests and page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
    d=page.locator('.fv-apollo-source-drawer');d.locator('summary').click();assert d.evaluate('(e)=>e.open')
    page.locator('details').evaluate_all('(nodes)=>nodes.forEach(n=>n.open=true)')
    audit=page.evaluate(CONTRAST) if width!=768 else {'checked':0,'worst':None,'fail':[]}
    assert audit['checked']>=230 if width!=768 else True
    assert not audit['fail'],str(audit['fail'][:3])
    ax=c.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes'];links=[n.get('name',{}).get('value','') for n in ax if n.get('role',{}).get('value')=='link' and not n.get('ignored')]
    assert not [x for x in links if not x.strip()]
    for name in ('Apollo 204 Review Board','S66-58038','S67-15717','S67-21294'):assert any(name in x for x in links)
    page.emulate_media(media='print');assert page.locator('.fv-apollo-print-custody').is_visible()
    urls=page.locator('.fv-apollo-print-custody a').all_text_contents();assert len(urls)>=8 and all(u.startswith('https://www.nasa.gov/') for u in urls)
    page.emulate_media(media='screen');page.locator('details').evaluate_all('(nodes)=>nodes.forEach(n=>n.open=false)');page.mouse.move(0,0);page.evaluate('document.activeElement?.blur()');page.wait_for_timeout(120)
    shot=a.out/f'{width}-{"js" if js else "nojs"}.png';page.screenshot(path=str(shot),full_page=True,animations='disabled')
    cases.append({'width':width,'js':js,'checked':audit['checked'],'worst':audit['worst'],'source_links':len(links),'print_urls':len(urls),'screenshot_sha256':sha(shot.read_bytes())});c.close()
  version=b.version;b.close()
 result={'scope':'offline PHP-rendered R238 Apollo 1 Atlas contrast/print/native AX','browser':version,'manifest':PIN,'cases':cases,'release':'STAGING_HOLD','axe':'NOT_EXECUTED','installed_WP':'NOT_TESTED','live_http':'BLOCKED_BY_ADMINISTRATOR','real_zoom':'NOT_TESTED','field_CWV':'NOT_MEASURED','transactions':'NOT_VERIFIED'}
 (a.out/'receipt.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps({'cases':len(cases),'text_node_checks':sum(x['checked'] for x in cases),'receipt_sha256':sha((a.out/'receipt.json').read_bytes())}))
if __name__=='__main__':main()
