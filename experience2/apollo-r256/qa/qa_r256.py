#!/usr/bin/env python3
"""R256 original-source Apollo print-provenance regression; offline Chromium, NOT WP/axe."""
import argparse, hashlib, json, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

SEAL='f5d1cf4e4e1be9b397563a6d9b25145f3b22d6dc5737774c1d27362869e3ed68'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
def sha(b):return hashlib.sha256(b).hexdigest()
def text(pdf):return subprocess.run(['pdftotext',str(pdf),'-'],capture_output=True,text=True,check=True).stdout

def run(a):
    a.out.mkdir(parents=True,exist_ok=True)
    manifest=(a.atlas/'manifest.json').read_bytes()
    assert sha(manifest)==SEAL
    for name,hash_ in json.loads(manifest)['files'].items():assert sha((a.atlas/name).read_bytes())==hash_, name
    proc=subprocess.run(['php',str(a.atlas/'wp-render-shim-r224.php'),str((a.atlas/'fv-ex2-apollo-r224.php').resolve()),'normal'],capture_output=True,text=True,check=True)
    html=json.loads(proc.stdout)['html']
    assert html==(a.atlas/'templates/atlas-fragment.html').read_text()
    css='\n'.join(p.read_text() for p in [a.atlas/'assets/atlas-scoped.css',a.r253,a.r254,a.r255])
    extra=a.overlay.read_text()
    assert '@media print' in extra and '::details-content' in extra
    assert all(x not in extra.lower() for x in ('payhip','awin1','checkout','@import','url('))
    def doc(styles):return '<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+styles+'</style></head><body>'+html+'</body></html>'
    base=doc(css); fixed=doc(css+'\n'+extra)
    receipt={'seal':SEAL,'overlay_sha256':sha(a.overlay.read_bytes()),'contexts':[]}
    with sync_playwright() as pw:
        b=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for w in (320,390,768,1440,1920):
            for js in (True,False):
                c=b.new_context(viewport={'width':w,'height':900},java_script_enabled=js,reduced_motion='reduce' if not js else 'no-preference',is_mobile=w<=390,has_touch=w<=390)
                p=c.new_page();requests=[];p.on('request',lambda r:requests.append(r.url))
                p.set_content(fixed)
                d=p.locator('#fv-apollo-source-drawer')
                assert not d.evaluate('e=>e.open')
                assert d.evaluate("e=>getComputedStyle(e,'::details-content').contentVisibility")=='hidden'
                assert p.locator('.fv-apollo-atlas [data-fv-plate-source]').count()==4
                assert p.locator('.fv-apollo-atlas a.cta').count()==1
                assert p.locator('.fv-apollo-atlas a.cta').get_attribute('href')==FREE
                assert p.evaluate('document.documentElement.scrollWidth-innerWidth')<=1
                assert not requests
                if w in (390,1440):
                    pixels=p.screenshot();p.set_content(base)
                    assert pixels==p.screenshot(), 'print-only overlay changed screen image'
                    (a.out/f'{w}-{int(js)}.png').write_bytes(pixels)
                p.set_content(fixed);s=p.locator('#fv-apollo-source-drawer summary')
                s.focus();s.press('Enter');assert d.evaluate('e=>e.open')
                s.press('Space');assert not d.evaluate('e=>e.open')
                receipt['contexts'].append({'width':w,'js':js,'pass':True})
                c.close()
        p=b.new_page()
        found=[]
        for label,page_html,expand in [('before',base,False),('closed',fixed,False),('expanded',fixed,True)]:
            p.set_content(page_html)
            if expand:p.locator('details').evaluate_all('es=>es.forEach(e=>e.open=true)')
            p.emulate_media(media='print')
            height=round(p.locator('#fv-apollo-source-drawer .fv-apollo-drawer-list').evaluate('e=>e.getBoundingClientRect().height'))
            pdf=a.out/f'{label}.pdf';p.pdf(path=str(pdf),print_background=True)
            raw=text(pdf);found.append((label,height,raw.count('Source kind')))
            if label!='before':
                assert all(t in raw for t in ('Report issued','Cannot establish','S66-58038','S67-15717','S67-21294'))
                assert 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/' in raw
        assert found[0][1:]==(0,0), 'negative control stopped reproducing'
        assert all(h>500 and k==4 for _,h,k in found[1:]), 'closed print omitted source records'
        receipt['print']=[{'state':s,'height_px':h,'source_kind_count':n} for s,h,n in found]
        b.close()
    (a.out/'receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(json.dumps(receipt,sort_keys=True))

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('atlas','r253','r254','r255','overlay','out'):p.add_argument('--'+n,type=Path,required=True)
    run(p.parse_args())
