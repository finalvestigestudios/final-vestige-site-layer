#!/usr/bin/env python3
"""Exact generated-fragment Chromium QA; not installed WordPress or genuine axe."""
import argparse, json
from pathlib import Path
from playwright.sync_api import sync_playwright
from r236_patch import RECORDS, sha

def verify(out,qa):
 assert not qa.exists(),'Do not overwrite prior evidence'
 qa.mkdir(parents=True)
 fragment=(out/'templates/atlas-fragment.html').read_text()
 css=(out/'assets/atlas-scoped.css').read_text()
 doc='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+fragment+'</body></html>'
 results={}
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
  for width in (320,390,768,1440,1920):
   for js in (False,True):
    c=browser.new_context(viewport={'width':width,'height':900},reduced_motion='reduce',java_script_enabled=js,is_mobile=width<=390,has_touch=width<=390,device_scale_factor=1)
    page=c.new_page();requests=[]
    page.on('request',lambda r:requests.append(r.url))
    page.set_content(doc,wait_until='load')
    assert not requests and page.evaluate('document.documentElement.scrollWidth<=innerWidth')
    assert page.locator('a.cta[href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"]').count()==1
    drawer=page.locator('details.fv-apollo-source-drawer')
    assert drawer.get_attribute('open') is None
    if width<=390:drawer.locator('summary').tap()
    else:drawer.locator('summary').press('Enter')
    assert drawer.get_attribute('open') is not None
    needed=[]
    for key,name,url,target,_ in RECORDS:
     plate=page.locator(f'[data-fv-plate-source="{key}"]')
     for label,href in [(f'Verify at NASA: {name}',url),(f'Find {name} in the investigation',target)]:
      link=plate.get_by_role('link',name=label,exact=True)
      assert link.count()==1 and link.get_attribute('href')==href,(width,js,key,label)
      needed.append(label)
    ax=c.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
    actual={x.get('name',{}).get('value') for x in ax if x.get('role',{}).get('value')=='link'}
    assert set(needed).issubset(actual),'Native Chromium AX source names did not match'
    shot=qa/(f'{width}-'+('js' if js else 'nojs')+'.png')
    page.screenshot(path=str(shot),full_page=True,animations='disabled')
    results[shot.name]=sha(shot)
    c.close()
  browser.close()
 (qa/'receipt.json').write_text(json.dumps({'screenshots_sha256':results,'axe_core_executed':False,'installed_wordpress_tested':False,'local_http_nav':False},sort_keys=True,indent=2)+'\n')
 return sha(qa/'receipt.json')

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--out',required=True,type=Path);parser.add_argument('--qa',required=True,type=Path)
 args=parser.parse_args();print(json.dumps({'receipt_sha256':verify(args.out,args.qa),'contexts':10},sort_keys=True))
