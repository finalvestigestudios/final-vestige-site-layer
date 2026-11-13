#!/usr/bin/env python3
"""R334 reproducible OFFLINE WordPress-stub / Chromium gate.
Uses actual R334 PHP/CSS; does not claim production, remote NASA fetches,
axe-core, screen-reader or deployed WordPress acceptance.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse
import fitz
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parents[1]
PHP=HERE/'fv-apollo-custody-bridge.php'
CSS=HERE/'assets/fv-apollo-custody.css'
STUB=HERE/'qa/wp_stub.php'
OUT=HERE/'QA'
FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
BOARD='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
HISTORY='https://www.nasa.gov/history/55-years-ago-tragedy-on-the-launch-pad/'
MEDIA=[
 'https://www.nasa.gov/image-detail/apollo-1-crew-honored/',
 'https://www.nasa.gov/image-detail/amf-s67-15717/',
 'https://www.nasa.gov/image-detail/amf-s66-58038/',
 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/',
 'https://www.nasa.gov/image-detail/amf-s67-21294/',
 'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/',
]
WIDTHS=(320,360,390,768,1024,1440,1920)

def blob(path):
    v=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(v)).encode()+b'\0'+v).hexdigest()

def fixture(instances=1, styled=True):
    s=subprocess.check_output(['php',str(STUB),str(instances)],text=True)
    if styled:
        s=s.replace('</head>', '<style>'+CSS.read_text()+'</style></head>')
    s=re.sub(r'<link rel="stylesheet" href="/r334/assets/fv-apollo-custody.css">','',s)
    return s

def scan(page, instances=1, styled=True):
    data=page.evaluate('''() => {
      const sections=[...document.querySelectorAll('section.fv-r334')];
      const controls=[...document.querySelectorAll('section.fv-r334 a,section.fv-r334 summary')];
      return {count:sections.length,sections:sections.map(s=>({
          records:[...s.querySelectorAll('[data-fv-record]')].map(x=>x.dataset.fvRecord),
          review:[...s.querySelectorAll('[data-fv-review="review"]')].map(x=>x.dataset.fvRecord),
          docs:[...s.querySelectorAll('a[data-fv-source-kind="document"]')].map(x=>x.href),
          media:[...s.querySelectorAll('a[data-fv-source-kind="contextual-media"]')].map(x=>x.href),
          ctas:[...s.querySelectorAll('a[data-fv-cta]')].map(x=>x.href),
          images:s.querySelectorAll('img,picture,video,iframe').length,
          geo:s.querySelectorAll('[data-lat],[data-lng],[data-map-pin],[data-geo-edge]').length,
          rights:s.dataset.fvRights,
          status:s.dataset.fvCustodyStatus
      })),controls:controls.map(e=>{const r=e.getBoundingClientRect();return {
       name:e.textContent.trim(),tag:e.tagName,rect:[r.left,r.right,r.width,r.height],
       visible:getComputedStyle(e).visibility!=='hidden' && r.width>0 && r.height>0};}),
       overflow:document.documentElement.scrollWidth-innerWidth};}''')
    assert data['count']==instances
    assert data['overflow']<=1 or not styled, data['overflow']
    for s in data['sections']:
        assert s['records']==['01','02','03','04','05','06']
        assert s['review']==['02','03','04','06']
        assert s['docs']==[HISTORY]+[BOARD]*5
        assert s['media']==MEDIA
        assert s['ctas']==[FREE]
        assert s['images']==s['geo']==0
        assert s['rights']=='link-only-not-cleared'
        assert s['status']=='staging-editorial-review'
    assert len(data['controls'])==instances*19, len(data['controls'])
    assert all(x['name'] for x in data['controls'])
    if styled:
        for e in data['controls']:
            # Closed details hide media links. Open them before scan in caller.
            assert e['rect'][2]>=12 and e['rect'][3]>=24, e
            assert e['rect'][0]>=-1 and e['rect'][1]<=page.viewport_size['width']+1, e
    return data

def negative_checks(html):
    # Mutations are independently generated here; neither the rendered source
    # nor tests are modified or silently accepted in a fallback path.
    expressions=[
        ('unauthorized merchant', html.replace('data-fv-cta="apollo-free-investigation"','data-fv-cta="apollo-free-investigation" data-merchant="unverified"',1)),
        ('false rights clearance',html.replace('data-fv-rights="link-only-not-cleared"','data-fv-rights="cleared-for-commercial-use"',1)),
        ('fabricated geo',html.replace('data-fv-geo="none"','data-map-pin="invented"',1)),
        ('document link replaced by photo',html.replace('data-fv-source-kind="document" href="'+HISTORY+'"','data-fv-source-kind="document" href="'+MEDIA[0]+'"',1)),
        ('second editorial CTA',html.replace('data-fv-cta="apollo-free-investigation"','data-fv-cta="extra-paid-offer"',1)),
        ('review flag erased',html.replace('data-fv-review="review"','data-fv-review="context"',1)),
    ]
    def audit(s):
        from html.parser import HTMLParser
        class Tags(HTMLParser):
            def __init__(self):super().__init__();self.all=[]
            def handle_starttag(self,name,attrs):self.all.append((name,dict(attrs)))
        t=Tags();t.feed(s)
        sections=[d for tag,d in t.all if tag=='section' and d.get('class')=='fv-r334']
        assert len(sections)==1 and sections[0].get('data-fv-rights')=='link-only-not-cleared'
        assert len([1 for _,d in t.all if d.get('data-map-pin')])==0
        assert len([1 for _,d in t.all if d.get('data-merchant')])==0
        ctas=[d for tag,d in t.all if tag=='a' and d.get('data-fv-cta')]
        assert len(ctas)==1 and ctas[0]['data-fv-cta']=='apollo-free-investigation' and ctas[0]['href']==FREE
        docs=[d['href'] for tag,d in t.all if tag=='a' and d.get('data-fv-source-kind')=='document']
        assert docs==[HISTORY]+[BOARD]*5
        assert len([1 for tag,d in t.all if tag=='li' and d.get('data-fv-review')=='review'])==4
    audit(html)
    caught=[]
    for label,s in expressions:
        try:audit(s)
        except AssertionError:caught.append(label)
    assert len(caught)==len(expressions),caught
    return caught

def main():
    OUT.mkdir(exist_ok=True)
    for path in (PHP,STUB):subprocess.run(['php','-l',str(path)],check=True,capture_output=True)
    assert len(MEDIA)==6 and len(set(MEDIA))==6
    html=fixture()
    controls=[];screens=[];pdf_result={};timings=[]
    caught=negative_checks(html)
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for js in (True,False):
                for width in WIDTHS:
                    fonts=(16,64) if width==320 else (16,)
                    for font in fonts:
                        print('case',js,width,font,flush=True)
                        page=browser.new_page(viewport={'width':width,'height':900},java_script_enabled=js,
                           reduced_motion='reduce',has_touch=width<=390,forced_colors='active' if width==390 else 'none')
                        requests=[];page.on('request',lambda r:requests.append(r.url))
                        page.goto('about:blank')
                        page.set_content(html.replace('</head>',f'<style>html{{font-size:{font}px}}</style></head>'))
                        # Evidence is visible and linkable even when JS is disabled.
                        page.locator('.fv-r334 details').evaluate_all('(els)=>els.forEach(e=>e.open=true)')
                        result=scan(page)
                        assert not requests
                        # One NASA documentation link and one media record link per card.
                        assert page.locator('[data-fv-source-kind="document"]').count()==6
                        assert page.locator('[data-fv-source-kind="contextual-media"]').count()==6
                        assert page.locator('a[data-fv-cta]').count()==1
                        if (js,width,font) in ((True,320,64),(True,390,16),(True,1440,16),(False,390,16)):
                            name=f'r334-{width}-font{font}-'+('js' if js else 'nojs')+'.png'
                            page.screenshot(path=str(OUT/name),full_page=True);screens.append(name)
                        if js and width==390:
                            b=page.pdf(format='A4',print_background=True)
                            (OUT/'r334-source-crosswalk.pdf').write_bytes(b)
                            doc=fitz.open(stream=b,filetype='pdf');links=[x['uri'] for q in doc for x in q.get_links() if x.get('uri')]
                            text=' '.join(q.get_text() for q in doc)
                            assert FREE in links and BOARD in links and HISTORY in links
                            assert all(k in text.lower() for k in ('apollo 1','review board','source audit'))
                            assert not any('utm_' in l or 'payhip.com' in l for l in links)
                            pdf_result={'pages':len(doc),'uriAnnotations':len(links),'mediaLinks':sum(k in links for k in MEDIA),'utmLeaks':0}
                            doc.close()
                        controls.append({'width':width,'font':font,'js':js,'controls':len(result['controls']),'overflow':result['overflow']})
                        page.close()
            # Second shortcode copy must have unique landmark ID and headings.
            dupe=browser.new_page(viewport={'width':1440,'height':900});dupe.set_content(fixture(2));dupe.locator('details').evaluate_all('(els)=>els.forEach(e=>e.open=true)')
            scan(dupe,2)
            ids=dupe.locator('[id]').evaluate_all('(e)=>e.map(x=>x.id)');assert len(ids)==len(set(ids))
            dupe.close()
            # Native keyboard disclosure is a real interactive operation, not
            # merely setting details.open via evaluate().
            key=browser.new_page();key.set_content(html)
            summary=key.locator('summary').first
            summary.focus();assert summary.evaluate('(e)=>document.activeElement===e')
            summary.press('Enter');assert summary.evaluate('(e)=>e.parentElement.open')
            assert key.locator('a[data-fv-source-kind="contextual-media"]').first.is_visible()
            key.close()
            # CSS-disabled no-JS semantics remain readable even without our stylesheet.
            plain=browser.new_page(java_script_enabled=False,viewport={'width':320,'height':900})
            plain.set_content(fixture(styled=False));assert plain.locator('section.fv-r334').is_visible()
            assert plain.locator('a[data-fv-cta]').count()==1
            plain.locator('summary').first.click();assert plain.locator('details').first.get_attribute('open') is not None
            plain.close()
        finally:browser.close()
    result={'sprint':'R334','status':'staging-only-not-live','actualPhp':blob(PHP),'actualCss':blob(CSS),
        'sourceResearchDeskBlob':'403d128c57b9bc82dac7c619651689070edef86c',
        'sourceResearchDeskPr':158,'sourceReviewNeeded':['02','03','04','06'],
        'cases':controls,'chromiumContexts':len(controls)+3,'negativeMutations':caught,
        'screenshots':screens,'pdf':pdf_result,'installedWordPress':False,
        'axeCore':'NOT AVAILABLE / NOT EXECUTED','screenReaders':'NOT EXECUTED',
        'otherBrowsers':'NOT AVAILABLE','productionLcp':None,'productionCls':None,
        'verifiedPaidOrders':None,'revenuePer1000QualifiedSessions':None,'release':'HARD HOLD'}
    (OUT/'r334-result.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS R334: '+str(len(controls))+' real Chromium viewport/JS/font cases; 3 semantic/keyboard/dual-instance checks; 6 unsafe mutations detected; PDF',pdf_result)

if __name__=='__main__':main()
