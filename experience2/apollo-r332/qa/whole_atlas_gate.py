#!/usr/bin/env python3
"""R332 whole-Atlas interaction audit: real offline Chromium, no live traffic.

Requires Python Playwright and installed Chromium at /usr/bin/chromium.
Run: python experience2/apollo-r332/qa/whole_atlas_gate.py
This is NOT axe-core, screen-reader, HTTP/CSP, WordPress or production CWV QA.
"""
import copy
import hashlib
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
PHP=ROOT/'apollo-r281/apollo-source-experience.php'
CSS=ROOT/'apollo-r281/assets/apollo-source-experience.css'
JS=ROOT/'apollo-r281/assets/apollo-cache-continuation.js'
HARNESS=ROOT/'apollo-r320/qa/wp_late_shortcodes.php'
OUT=ROOT/'apollo-r332/QA'
PINS={PHP:'f59a083de8d0774ed7210bfe4e18726feea73f76',
      CSS:'577a5d33518baec6e1beff1517779264d342bc50',
      JS:'f85617e5f12ba747908ac507261f69c377369de7'}
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
WIDTHS=(320,360,390,768,1024,1440,1920)

def git_blob(path):
    b=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def capture(page):
    return page.locator('section.fv-r281').evaluate('''root=>{
      const targets=[...root.querySelectorAll('a,summary')].map(el=>{
        const r=el.getBoundingClientRect();
        return {text:el.textContent.trim(),left:r.left,right:r.right,width:r.width,height:r.height};
      });
      const ids=[...root.querySelectorAll('[id]')].map(x=>x.id);
      return {targets,uniqueIds:ids.length===new Set(ids).size,
        fragments:[...root.querySelectorAll('a[href^="#"]')].every(
          a=>root.querySelector('#'+CSS.escape(a.getAttribute('href').slice(1)))),
        documentRoles:[...root.querySelectorAll('.fv-r281__source-list>li')].map(x=>x.dataset.fvEvidenceRole),
        mediaRoles:[...root.querySelectorAll('[data-fv-media-record]')].map(x=>[x.dataset.fvEvidenceRole,x.dataset.fvImageRights,x.dataset.fvClaimProof]),
        ctas:[...root.querySelectorAll('a[data-fv-cta]')].map(x=>x.href),
        outbound:[...root.querySelectorAll('a[data-fv-link-purpose]')].map(x=>x.href),
        geo:root.querySelectorAll('[data-map-pin],[data-geo-edge],[data-lat],[data-lng]').length,
        overflow:document.documentElement.scrollWidth-innerWidth};
    }''')

def validate(s,width):
    assert len(s['targets'])==46
    assert s['uniqueIds'] and s['fragments'] and s['overflow']<=1
    assert all(t['text'] and t['width']>=12 and t['height']>=24 and
               t['left']>=-1 and t['right']<=width+1 for t in s['targets'])
    assert s['documentRoles']==['documented-textual-claim']*3
    assert s['mediaRoles']==[['contextual-media-only','not-cleared-for-reuse','no']]*4
    assert s['ctas']==[FREE] and len(s['outbound'])==17
    assert all(x.startswith(('https://www.nasa.gov/','https://sma.nasa.gov/')) for x in s['outbound'])
    assert s['geo']==0

def negatives(original):
    cases={
      'paid-source-link':lambda x:x['outbound'].__setitem__(0,'https://payhip.com/unauthorized'),
      'invented-geo':lambda x:x.__setitem__('geo',1),
      'missing-document':lambda x:x['documentRoles'].pop(),
      'false-image-clearance':lambda x:x['mediaRoles'][0].__setitem__(1,'cleared'),
      'second-cta':lambda x:x['ctas'].append('https://payhip.com/unauthorized'),
      'zero-width-link':lambda x:x['targets'][0].__setitem__('width',0),
      'offscreen-target':lambda x:x['targets'][0].__setitem__('right',500),
      'broken-fragment':lambda x:x.__setitem__('fragments',False),
    }
    for name,mutate in cases.items():
        s=copy.deepcopy(original);mutate(s)
        try:validate(s,320)
        except AssertionError:continue
        raise AssertionError('Mutation escaped release gate: '+name)
    return sorted(cases)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for p,sha in PINS.items():assert git_blob(p)==sha,(str(p),git_blob(p))
    subprocess.run(['php','-l',str(PHP)],check=True,capture_output=True)
    subprocess.run(['node','--check',str(JS)],check=True,capture_output=True)
    html=subprocess.check_output(['php',str(HARNESS),'late-dynamic','1'],text=True).split('<!--R320_QUEUE:',1)[0]
    css=CSS.read_text();js=JS.read_text()
    receipts=[];screens=[];first=None
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for js_enabled in (True,False):
                for width in WIDTHS:
                    for font in (16,32,64):
                        page=browser.new_page(viewport={'width':width,'height':850},
                            java_script_enabled=js_enabled,reduced_motion='reduce',
                            has_touch=width<=390,
                            forced_colors='active' if width==390 and font==32 else 'none')
                        requests=[];page.on('request',lambda req:requests.append(req.url))
                        page.set_content(html.replace('</head>','<style>'+css+'</style></head>'))
                        if js_enabled:page.add_script_tag(content=js)
                        page.evaluate('(n)=>document.documentElement.style.fontSize=n+"px"',font)
                        page.locator('details').evaluate_all('els=>els.forEach(x=>x.open=true)')
                        s=capture(page);validate(s,width);assert not requests,requests
                        if width==320 and font==16 and js_enabled:first=s
                        if (width,font,js_enabled) in ((320,64,True),(390,16,True),(1440,16,True),(1920,16,False)):
                            filename=f'r332-{width}-font{font}-'+('js' if js_enabled else 'nojs')+'.png'
                            page.screenshot(path=str(OUT/filename),full_page=True);screens.append(filename)
                        if width in (320,1440) and font==16 and js_enabled:
                            for selector in ('.fv-r281__rail a','.fv-r281__source-list a[data-fv-link-purpose]'):
                                el=page.locator(selector).first;el.focus()
                                assert el.evaluate('e=>document.activeElement===e')
                            tree=page.context.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
                            names=[x.get('name',{}).get('value','') for x in tree]
                            assert any('Read the free Apollo 1 investigation' in n for n in names)
                        receipts.append({'width':width,'font':font,'js':js_enabled,'interactiveTargets':len(s['targets'])})
                        page.close()
        finally:browser.close()
    mutations=negatives(first)
    result={'sprint':'R332','contextsPassed':len(receipts),'targetsChecked':sum(x['interactiveTargets'] for x in receipts),
      'mutationsRejected':mutations,'screenshots':screens,
      'sourceBlobs':{str(k.relative_to(ROOT)):v for k,v in PINS.items()},
      'axe': 'NOT EXECUTED','screenReader':'NOT EXECUTED','nativeHTTP':'BLOCKED',
      'installedWordPress':False,'productionLCP':None,'productionCLS':None,
      'verifiedPaidOrders':None,'release':'HARD HOLD'}
    (OUT/'r332-result.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print('R332 PASS',len(receipts),'real Chromium contexts,',result['targetsChecked'],
          'interactive target checks,',len(mutations),'mutation rejects')

if __name__=='__main__':main()
