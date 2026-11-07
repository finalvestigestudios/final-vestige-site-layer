#!/usr/bin/env python3
"""R196 genuine Chromium/CDP accessibility-tree + negative-control custody gate.
Offline actual PHP-rendered shim (not installed WordPress); no axe-core claim.
"""
from __future__ import annotations
import json, re, subprocess, sys
from pathlib import Path
from html.parser import HTMLParser
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from build_r196 import build, sha, NASA_BOARD, NASA_PHOTO
DEST = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
WIDTHS = (320,360,390,768,1440,1920)
CASES = [(str(w),w,False,False,False,False) for w in WIDTHS] + [
    ('390-nojs',390,True,False,False,False),
    ('390-reduced',390,False,True,False,False),
    ('390-forced-colors',390,False,False,True,False),
    ('390-touch',390,False,False,False,True)]

class SourceParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids=[];self.ctas=[];self.nasa=[];self.bad=[];self.links=[]
    def handle_starttag(self,tag, attrs):
        d = dict(attrs)
        if len(d)!=len(attrs): self.bad.append('duplicate HTML attribute')
        if d.get('id'): self.ids.append(d['id'])
        if tag in ('img','script','iframe','form','video','canvas'):
            self.bad.append('unreviewed active/media element: '+tag)
        if tag=='a':
            href=d.get('href','');self.links.append(href)
            if 'cta' in d.get('class','').split():self.ctas.append(href)
            if href.startswith('https://www.nasa.gov/'):
                self.nasa.append(href)
            elif href.startswith('https://') and href != DEST:
                self.bad.append('unreviewed external destination: '+href)

def custody_gate(html):
    p=SourceParser();p.feed(html)
    assert len(p.ids)==len(set(p.ids)), 'Duplicate document ID'
    assert not p.bad, p.bad
    assert p.ctas==[DEST], 'Free CTA changed or multiplied'
    assert len(p.nasa)>=8 and NASA_BOARD in p.nasa and NASA_PHOTO in p.nasa, 'NASA bibliography missing'
    for needle in ('<aside class="fv-apollo-method"','id="fv-apollo-method-title"',
                   '01 / Review Board determination','02 / Recorded sequence',
                   '03 / Archival photograph','It did not conclusively identify',
                   'It records the aftermath','No NASA promotional endorsement'):
        assert needle in html, 'Missing source/rights boundary: '+needle
    assert html.count('class="fv-apollo-method"')==1
    assert html.count('<details>')==8 and html.count('<time datetime=')==4
    return p

def render(dist, mode='normal'):
    return json.loads(subprocess.check_output(['php',str(dist/'wp-render-shim-r196.php'),
        str(dist/'fv-ex2-apollo-r196.php'),mode],text=True))

def run(out):
    out.mkdir(parents=True,exist_ok=True)
    manifest=build();dist=ROOT/'dist'
    for name,digest in manifest['files'].items(): assert sha((dist/name).read_bytes())==digest
    subprocess.run(['php','-l',str(dist/'fv-ex2-apollo-r196.php')],check=True,capture_output=True)
    raw=render(dist)
    assert not raw['fallback'] and raw['details']==8 and raw['chronology']==4
    assert not render(dist,'printed')['fallback'] and render(dist,'late')['fallback']
    html=raw['html'];css=(dist/'assets/atlas-scoped.css').read_text()
    parsed=custody_gate(html)
    mutants={
      'switch-paid-cta': html.replace(DEST,'https://payhip.com/b/imaginary',1),
      'erase-ignition-uncertainty': html.replace('It did not conclusively identify','It conclusively identified',1),
      'replace-photo-source': html.replace(NASA_PHOTO,'https://example.com/unverified',1),
      'inject-marketing-pixel': html.replace('</aside>','<img src="https://ad.example/track"></aside>',1),
      'duplicate-landmark': html.replace('id="fv-apollo-method-title"','id="fv-apollo-page-title"',1),
    }
    caught=[]
    for name,bad in mutants.items():
        try: custody_gate(bad)
        except AssertionError: caught.append(name)
    assert len(caught)==len(mutants), 'Mutation not rejected: '+str(set(mutants)-set(caught))
    receipt={'release':'R196','source':'actual PHP shortcode output in controlled WordPress-function shim',
       'status':'LOCAL_STAGING_FIXTURE_PASS; NOT_INSTALLED_WORDPRESS',
       'parent_head':manifest['parent_head'],'source_manifest':manifest['files'],
       'negative_controls':caught,'case_results':[],
       'limits':['no installed WordPress/Gutenberg or actual theme/CSP/CDN',
        'CDP accessibility tree is genuine Chromium but not axe-core nor NVDA/VoiceOver',
        'page.set_content fixture; navigation to hosted site not validated',
        'no paid product, qualified-human denominator, order ledger or realized revenue']}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for name,width,nojs,reduced,forced,touch in CASES:
            ctx=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,
                  java_script_enabled=not nojs,has_touch=touch,is_mobile=touch,
                  reduced_motion='reduce' if reduced else 'no-preference',
                  forced_colors='active' if forced else 'none')
            page=ctx.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+html+'</body></html>',wait_until='load')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),name
            guide=page.get_by_role('complementary',name='Three kinds of evidence. Three different limits.')
            assert guide.count()==1,('missing named aside landmark',name)
            assert guide.locator('dt').count()==3
            assert guide.locator('a').count()==3
            assert guide.locator('a').nth(0).get_attribute('href')==NASA_BOARD
            assert guide.locator('a').nth(2).get_attribute('href')==NASA_PHOTO
            assert page.get_by_role('link',name='Read original investigation →').get_attribute('href')==DEST
            assert page.locator('.fv-apollo-atlas details').count()==8
            cdp=ctx.new_cdp_session(page)
            ax=cdp.send('Accessibility.getFullAXTree')['nodes']
            named=[(n.get('role',{}).get('value',''),n.get('name',{}).get('value','')) for n in ax if not n.get('ignored')]
            assert ('complementary','Three kinds of evidence. Three different limits.') in named,name
            for phrase in ("Read the Board's findings",'Examine the recorded chronology','Verify the photo record'):
                assert ('link',phrase) in named,('unavailable AX link',name,phrase)
            # Native disclosure must work without enhancement JS and remain readable.
            native=page.locator('.fv-apollo-atlas details').first
            native.locator('summary').focus();page.keyboard.press('Enter')
            assert native.get_attribute('open') is not None
            native.locator('summary').click();assert native.get_attribute('open') is None
            if touch: native.locator('summary').tap();assert native.get_attribute('open') is not None
            if reduced: assert guide.evaluate('e=>getComputedStyle(e.closest(".fv-apollo-atlas")).scrollBehavior')=='auto'
            assert not errors,errors
            perf={'lcp_ms':None,'cls':None} if nojs else page.evaluate("""async () => {
              let out={lcp_ms:null,cls:0};
              try { const po=new PerformanceObserver(list=>{for(const e of list.getEntries()){out.lcp_ms=e.startTime}});
                    po.observe({type:'largest-contentful-paint',buffered:true}); } catch(e) {}
              try { const po2=new PerformanceObserver(list=>{for(const e of list.getEntries()){if(!e.hadRecentInput)out.cls+=e.value}});
                    po2.observe({type:'layout-shift',buffered:true}); } catch(e) {}
              await new Promise(r=>setTimeout(r,50)); return out;
            }""")
            path=out/(name+'.png');page.screenshot(path=str(path),full_page=True,animations='disabled',timeout=20000)
            receipt['case_results'].append({'name':name,'width':width,'no_js':nojs,
              'named_ax_landmark':True,'named_ax_source_links':3,'disclosure':True,
              'horizontal_overflow':False,'css_zoom_200':'zoom200' in name,
              'fixture_performance_observer':perf,'screenshot_sha256':sha(path.read_bytes())})
            ctx.close()
        browser.close()
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'PASS','cases':len(CASES),'mutation_rejections':len(caught),
                      'cdp_ax_named_landmarks':len(CASES),'sha':sha((out/'receipt.json').read_bytes())}))

if __name__=='__main__':run(Path(sys.argv[1] if len(sys.argv)>1 else '/tmp/apollo-r196-evidence'))
