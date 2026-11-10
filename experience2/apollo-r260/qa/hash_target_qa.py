#!/usr/bin/env python3
"""R260 original-PHP offline fragment acceptance; not installed WP or axe."""
import argparse,hashlib,json,subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
SEAL='f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
TARGETS=['fv-apollo-finding-oxygen','fv-apollo-finding-fire','fv-apollo-finding-hatch','fv-apollo-finding-chronology','fv-apollo-photo-aftermath','fv-apollo-source-drawer','fv-apollo-reading-bridge']
CSS=['apollo-r253/atlas-source-actions.css','apollo-r254/provenance-tap-continuity.css','apollo-r255/evidence-path-touch.css','apollo-r256/print-custody.css','apollo-r257/print-full-evidence.css','apollo-r260/hash-target-orientation.css']
def hash(b):return hashlib.sha256(b).hexdigest()
def insist(x,msg):
 if not x:raise AssertionError(msg)
def run(a):
 d=a.atlas.resolve();root=a.overlays.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
 insist(hash((d/'manifest.json').read_bytes())==SEAL,'sealed manifest drift')
 for p,expected in json.loads((d/'manifest.json').read_text())['files'].items():insist(hash((d/p).read_bytes())==expected,'sealed source drift '+p)
 html=json.loads(subprocess.run(['php',str(d/'wp-render-shim-r224.php'),str(d/'fv-ex2-apollo-r224.php'),'normal'],capture_output=True,text=True,check=True).stdout)['html']
 insist(html==(d/'templates/atlas-fragment.html').read_text(),'original PHP output drift')
 patch=(root/CSS[-1]).read_text();insist(patch.count(':target')>=3 and 'forced-colors' in patch and '@media print' in patch,'missing target CSS')
 insist(not any(x in patch.lower() for x in ('url(', '@import','javascript:','https:')),'external code dependency')
 css='\n'.join([(d/'assets/atlas-scoped.css').read_text()]+[(root/p).read_text() for p in CSS])
 doc='<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>'
 receipt={'manifest_sha256':SEAL,'php_html_sha256':hash(html.encode()),'css_sha256':hash(patch.encode()),'screenshots':{},'cases':[],'axe':'NOT EXECUTED','installed_wp':'NOT TESTED'}
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path=a.chromium,args=['--no-sandbox'])
  for w in (320,390,768,1440,1920):
   for js in (False,True):
    c=b.new_context(viewport={'width':w,'height':900},java_script_enabled=js,is_mobile=w<=390,has_touch=w<=390,reduced_motion='reduce');pg=c.new_page();req=[]
    pg.on('request',lambda r:req.append(r.url));pg.set_content(doc)
    insist(not req,'unexpected request');insist(pg.locator('a[href="'+FREE+'"]').count()==1,'free CTA drift')
    insist(pg.locator('a[href^="https://www.nasa.gov/"]').count()==55,'NASA custody drift')
    insist(pg.locator('a[href^="#"]').count()==31,'in-page link drift')
    for tid in TARGETS:
     pg.locator('a[href="#'+tid+'"]:visible').first.click()
     v=pg.evaluate("""id=>{let t=document.getElementById(id),s=getComputedStyle(t);return [location.hash==='#'+id,t.matches(':target'),document.activeElement===t,s.outlineWidth,s.boxShadow,document.documentElement.scrollWidth<=innerWidth+1]}""",tid)
     insist(v[0] and v[1] and (v[2] or tid=='fv-apollo-source-drawer') and v[3]=='3px' and v[4]!='none' and v[5],'fragment failure '+tid+str(v))
    if w in (390,1440):
     pg.locator('a[href="#fv-apollo-finding-fire"]:visible').first.click();img=pg.screenshot(animations='disabled');name=f'{w}-{int(js)}-target.png';(out/name).write_bytes(img);receipt['screenshots'][name]=hash(img)
    receipt['cases'].append({'width':w,'js':js,'targets_passed':len(TARGETS)});c.close()
  for w in (390,1440):
   c=b.new_context(viewport={'width':w,'height':900},forced_colors='active',reduced_motion='reduce');pg=c.new_page();pg.set_content(doc)
   pg.locator('a[href="#fv-apollo-finding-fire"]:visible').first.click()
   insist(pg.locator('#fv-apollo-finding-fire').evaluate('(e)=>getComputedStyle(e).boxShadow')=='none','forced-colors shadow dependence')
   insist(pg.locator('#fv-apollo-finding-fire').evaluate('(e)=>getComputedStyle(e).outlineWidth')=='3px','forced-colors outline')
   receipt['cases'].append({'width':w,'forced_colors':True,'passed':True});c.close()
  b.close()
 receipt['stable_sha256']=hash(json.dumps(receipt,sort_keys=True,separators=(',',':')).encode());(out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'passed':True,'contexts':len(receipt['cases']),'fragment_checks':72,'stable_sha256':receipt['stable_sha256']}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--atlas',type=Path,required=True);ap.add_argument('--overlays',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--chromium',default='/usr/bin/chromium');run(ap.parse_args())
