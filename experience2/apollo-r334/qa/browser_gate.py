#!/usr/bin/env python3
"""R334 actual standalone PHP-rendered browser QA. No installed WordPress or axe-core assertion."""
import hashlib, json, subprocess, os
from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=ROOT/'QA'
WIDTHS=[320,390,768,1440,1920]
PHOTO=['S67-19766','S67-15717','S66-58038','KSC-20170124-PH_KLS01_0164','S67-21294','KSC-20170124-PH_KLS01_0090']
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def main():
    OUT.mkdir(exist_ok=True)
    php=ROOT/'apollo-custody-crosswalk.php'
    css=ROOT/'assets/custody.css'
    subprocess.run(['php','-l',str(php)],check=True,stdout=subprocess.PIPE)
    raw=subprocess.check_output(['php',str(HERE/'render.php')],text=True)
    assert len(raw)>8000 and all(x in raw for x in PHOTO)
    style=css.read_text()
    styled=raw.replace('<link rel="stylesheet" href="/custody.css">','<style>'+style+'</style>')
    cases=[]; screenshots=[]; pdfinfo={}; fails=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for js in (False,True):
                for width in (WIDTHS if js else (320,390)):
                    for font in ([16,64] if width==320 and js else [16]):
                        print('START',js,width,font,flush=True)
                        page=browser.new_page(viewport={'width':width,'height':900},java_script_enabled=js,has_touch=width<=390,reduced_motion='reduce',forced_colors='active' if width==390 else 'none')
                        page.set_content(styled.replace('</head>',f'<style>html {{font-size:{font}px}}</style></head>'),wait_until='load')
                        root=page.locator('section.fv-r334'); assert root.count()==1
                        items=root.locator('li[data-fv-record]'); assert items.count()==6
                        assert items.evaluate_all('els => els.map(e=>e.dataset.fvRecord)')==[f'{i:02d}' for i in range(1,7)]
                        assert root.locator('a[data-fv-source-role="contextual-photo"]').count()==6
                        assert root.locator('a[data-fv-source-role="documentary-source"]').count()==6
                        assert root.locator('a[data-fv-cta]').count()==1
                        assert root.locator('a[data-fv-cta]').get_attribute('href')==FREE
                        assert root.locator('[data-lat],[data-lng],[data-map-pin],[data-geo-edge]').count()==0
                        root.locator('details').evaluate_all('els=>els.forEach(e=>e.open=true)')
                        links=root.locator('a').evaluate_all('els=>els.map(a=>({href:a.href,text:a.innerText,rect:{x:a.getBoundingClientRect().x,right:a.getBoundingClientRect().right,width:a.getBoundingClientRect().width,height:a.getBoundingClientRect().height}}))')
                        assert all(l['text'].strip() for l in links)
                        assert len(links)==13
                        photos=root.locator('a[data-fv-source-role="contextual-photo"]').evaluate_all('els=>els.map(a=>a.href)')
                        docs=root.locator('a[data-fv-source-role="documentary-source"]').evaluate_all('els=>els.map(a=>a.href)')
                        assert len(set(photos))==6 and all(u.startswith('https://www.nasa.gov/image-detail/') for u in photos)
                        assert docs[0]=='https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/'
                        assert all(u=='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/' for u in docs[1:])
                        assert 'not a Review Board report identifier' in root.text_content()
                        assert all(l['rect']['width']>0 for l in links)
                        # Narrow 400% text must not hide controls or introduce horizontal scrolling.
                        over=page.evaluate('document.documentElement.scrollWidth-innerWidth')
                        assert over<=1, ('overflow',js,width,font,over)
                        assert all(l['rect']['x']>=-1 and l['rect']['right']<=width+1 for l in links),(js,width,font,links)
                        # Native disclosure works for keyboard with scripting forbidden.
                        summary=root.locator('summary').first
                        root.locator('details').first.evaluate('(e)=>e.open=false')
                        summary.focus()
                        assert summary.evaluate('(e)=>e===document.activeElement')
                        summary.press('Enter')
                        assert root.locator('details').first.get_attribute('open') is not None
                        assert root.locator('a[data-fv-source-role="contextual-photo"]').first.is_visible()
                        if width==390 and js:
                            root.locator('details').evaluate_all('els=>els.forEach(e=>e.open=true)')
                            page.emulate_media(media='print')
                            pdf=page.pdf(format='A4',print_background=True)
                            f=OUT/'r334-source-roles-print.pdf';f.write_bytes(pdf)
                            document=fitz.open(stream=pdf,filetype='pdf');uris=[a['uri'] for p in document for a in p.get_links() if a.get('uri')];pdfinfo={'pages':len(document),'urls':len(uris),'utmLeaks':sum('utm_' in u for u in uris)};document.close()
                            assert len(uris)>=13 and pdfinfo['utmLeaks']==0
                            page.emulate_media(media='screen')
                        if (js,width,font) in [(True,390,16),(True,1440,16),(False,320,16)]:
                            name=f'r334-{width}-font{font}-'+('js' if js else 'nojs')+'.png'
                            page.screenshot(path=str(OUT/name),full_page=True);screenshots.append(name)
                        cases.append({'jsEnabled':js,'width':width,'rootFont':font,'sourceLinks':12,'overflow':over})
                        page.close()
            # Real browser failure probes: forged merchant, invented geo, fake media clearance.
            for change in ['merchant','geo','rights']:
                bad=browser.new_page()
                tampered=styled.replace('data-fv-image-rights="not-cleared-for-reuse"','data-fv-image-rights="commercial-cleared"',1) if change=='rights' else (styled.replace('<section class="fv-r334"','<section data-map-pin="invented" class="fv-r334"',1) if change=='geo' else styled.replace(FREE,'https://payhip.com/unknown-product',1))
                bad.set_content(tampered)
                def release_ok(p):
                    r=p.locator('section.fv-r334')
                    return r.get_attribute('data-map-pin') is None and r.locator('[data-map-pin]').count()==0 and r.locator('[data-fv-image-rights="commercial-cleared"]').count()==0 and r.locator('a[data-fv-cta]').get_attribute('href')==FREE
                assert not release_ok(bad),change
                fails.append(change);bad.close()
        finally: browser.close()
    receipt={'run':'R334','contextsPassed':len(cases),'cases':cases,'screenshots':screenshots,'pdf':pdfinfo,'adversarialRejected':fails,'sourceGitSnapshot':{'PR158TemplateBlob':'403d128c57b9bc82dac7c619651689070edef86c'},'sourceFilesSHA256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (php,css)},'wordPress':'NOT TESTED','axeCore':'NOT RUN','realHTTP':'NOT TESTED','lcp':'NOT PRODUCTION MEASURED','cls':'NOT PRODUCTION MEASURED','merchant':'NOT AUTHENTICATED','release':'HARD HOLD'}
    (OUT/'r334-browser-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('R334 PASS',len(cases),'actual Chromium PHP-rendered cases;',len(fails),'unsafe mutations rejected; PDF:',pdfinfo)
if __name__=='__main__':main()
