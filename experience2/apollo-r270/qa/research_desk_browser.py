#!/usr/bin/env python3
"""Chromium acceptance of actual R270 PHP output against a semantic PR158 fixture.
This is NOT an installed WordPress or full original PR158 template test.
"""
import json, hashlib, pathlib, subprocess, sys
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
JS="""/* PR #158 source-ledger.js; blob 32e757cc4dc8708397ff65ac21e89dd319781d78 */
(()=>{'use strict';
document.querySelectorAll('[data-fvx-ledger]').forEach(root=>{
 if(root.dataset.fvxInitialized==='yes')return;
 const search=root.querySelector('[data-fvx-search]');
 const tools=root.querySelector('[data-fvx-tools]');
 const status=root.querySelector('[data-fvx-status]');
 const cards=[...root.querySelectorAll('[data-fvx-record]')];
 const empty=root.querySelector('[data-fvx-empty]');
 if(!search||!tools||!status||!cards.length||!empty)return;
 try{
   const filter=()=>{
     const needle=search.value.trim().toLocaleLowerCase();
     let shown=0;
     cards.forEach(card=>{
       const visible=!needle||card.dataset.fvxSearch.toLocaleLowerCase().includes(needle);
       card.hidden=!visible;if(visible)shown++;
     });
     status.textContent=`${shown} of ${cards.length} evidence records`;
     empty.hidden=shown!==0;
   };
   search.addEventListener('input',filter);
   root.dataset.fvxInitialized='yes';
   filter();
   tools.hidden=false;
 }catch(_){
   root.dataset.fvxInitialized='';
   cards.forEach(card=>card.hidden=false);
   tools.hidden=true;
   empty.hidden=true;
 }
});
})();
"""
CSS="""*{box-sizing:border-box}body{margin:0;background:#111;color:#eee;font:16px/1.5 system-ui} main{margin:auto;max-width:1100px;padding:16px}section{border:1px solid #9a7a47;margin:18px 0;padding:16px;min-width:0}h2{font-size:1.5rem}input{font:inherit;max-width:100%;width:100%}a{color:#f3d596}article{padding:10px;border-bottom:1px solid #555;overflow-wrap:anywhere}article[hidden],[hidden]{display:none!important}:focus-visible{outline:3px solid #fff;outline-offset:2px}summary{cursor:pointer} @media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}"""

def sha(b):return hashlib.sha256(b).hexdigest()
def run(out):
    out.mkdir(parents=True,exist_ok=True)
    p=subprocess.run(['php',str(ROOT/'qa/php-scope-gate.php')],capture_output=True,check=True)
    html=p.stdout.decode()
    cases=[]; screenshots={}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True, executable_path='/usr/bin/chromium', args=['--no-sandbox'])
        for width in (320,390,768,1440,1920):
            for enabled in (False,True):
                context=browser.new_context(viewport={'width':width,'height':800},java_script_enabled=enabled, reduced_motion='reduce', device_scale_factor=1, is_mobile=width<=390,has_touch=width<=390)
                page=context.new_page(); requests=[]
                page.on('request',lambda req:requests.append(req.url))
                dom=html.replace('</head>', '<style>'+CSS+'</style></head>').replace('</body>', ('<script>'+JS+'</script>' if enabled else '')+'</body>')
                page.set_content(dom,wait_until='load')
                ids=page.locator('[id]').evaluate_all('(x)=>x.map(e=>e.id)')
                assert len(ids)==27 and len(ids)==len(set(ids)),(width,enabled,'duplicate id')
                assert page.locator('[data-fvx-ledger]').count()==3
                for root in page.locator('[data-fvx-ledger]').all():
                    for attr,selector in [('for','label'),('aria-controls','input'),('aria-labelledby','section')]:
                        for element in root.locator(selector+'['+attr+']').all():
                            rid=element.get_attribute(attr)
                            assert root.locator('#'+rid).count()==1,(attr,rid)
                    assert root.locator('article[data-fvx-record]').count()==6
                assert page.locator('a[href^="https://www.nasa.gov/"]').count()==18
                assert not requests, requests
                assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1'),(width,enabled,'overflow')
                if enabled:
                    searches=page.locator('input[data-fvx-search]')
                    searches.nth(1).fill('record 3')
                    assert page.locator('[data-fvx-ledger]').nth(1).locator('article:visible').count()==1
                    assert page.locator('[data-fvx-ledger]').nth(0).locator('article:visible').count()==6
                    assert page.locator('[data-fvx-ledger]').nth(2).locator('article:visible').count()==6
                    searches.nth(1).fill('not-in-records')
                    assert page.locator('[data-fvx-ledger]').nth(1).locator('article:visible').count()==0
                    assert '0 of 6' in page.locator('[data-fvx-ledger]').nth(1).locator('[role=status], [data-fvx-status]').inner_text()
                    searches.nth(1).fill('')
                else:
                    assert page.locator('[data-fvx-ledger]').nth(1).locator('[data-fvx-tools]').is_hidden()
                    page.locator('summary').nth(1).click()
                    assert page.locator('details').nth(1).get_attribute('open') is not None
                if width in (390,1440):
                    name=f'{width}-'+('js' if enabled else 'nojs')+'.png'
                    page.screenshot(path=str(out/name),animations='disabled',full_page=True)
                    screenshots[name]=sha((out/name).read_bytes())
                cases.append({'width':width,'js':enabled,'status':'PASS'})
                context.close()
        browser.close()
    receipt={'fixture':'R270 PHP emitted 3 semantic PR158-aligned desks; NOT exact original ledger.html','contexts':cases,'screenshots':screenshots,'source_php_sha256':sha((ROOT/'rd-instance-scope.php').read_bytes()),'php_gate_sha256':sha((ROOT/'qa/php-scope-gate.php').read_bytes())}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'contexts':len(cases),'passes':sum(x['status']=='PASS' for x in cases),'receipt_sha256':sha((out/'receipt.json').read_bytes()),'screenshots':screenshots},sort_keys=True))
if __name__=='__main__':run(pathlib.Path(sys.argv[1]))
