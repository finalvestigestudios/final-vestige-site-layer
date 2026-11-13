#!/usr/bin/env python3
"""R336: actual Chromium accessibility-tree + NASA rights/commerce contract gate.
Runs *real* R281 PHP in the version-pinned WordPress lifecycle stub. Offline only.
Not axe-core, WCAG certification, a screen reader, installed WP or production CWV.
"""
from __future__ import annotations
import hashlib, json, re, subprocess
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PHP = ROOT / 'apollo-r281/apollo-source-experience.php'
CSS = ROOT / 'apollo-r281/assets/apollo-source-experience.css'
STUB = ROOT / 'apollo-r320/qa/wp_late_shortcodes.php'
OUTPUT = ROOT / 'apollo-r336/QA'
PINS = {PHP: 'f59a083de8d0774ed7210bfe4e18726feea73f76',
        CSS: '577a5d33518baec6e1beff1517779264d342bc50',
        STUB: 'f8987327fd6b49afcf8996c695100e3e7471c831'}
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
MEDIA_IDS = ('S67-15717', 'S66-58038', 'S67-21294', 'KSC-20170124-PH_KLS01_0090')
CONFIGS = [(w, 16, True, False, False) for w in (320,360,390,768,1024,1440,1920)]
CONFIGS += [(w,16,False,False,False) for w in (320,390,1440)]
CONFIGS += [(320,64,True,False,False),(390,16,True,True,True),(1440,16,True,False,True)]


def git_blob(p: Path) -> str:
    b = p.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(b)).encode() + b'\0' + b).hexdigest()


def html_fixture(instances=1, style=True):
    data = subprocess.check_output(['php',str(STUB),'late-dynamic',str(instances)],text=True)
    html = data.split('<!--R320_QUEUE:',1)[0]
    # No actual web server is involved. The real CSS bytes are injected, while
    # the plugin's body fallback link is removed from the offline test fixture.
    html = re.sub(r'<link rel="stylesheet" href="/assets/apollo-source-experience.css[^\"]*">','',html)
    if style:
        html = html.replace('</head>','<style>'+CSS.read_text()+'</style></head>')
    return html


def ax_tree(page):
    session = page.context.new_cdp_session(page)
    try:
        data = session.send('Accessibility.getFullAXTree')
        return [node for node in data['nodes'] if not node.get('ignored')]
    finally:
        session.detach()


def role(node):
    return node.get('role',{}).get('value','')


def name(node):
    return node.get('name',{}).get('value','').strip()


def contract(page, instances=1, expand=True):
    if expand:
        page.locator('section.fv-r281 details').evaluate_all('(elements)=>elements.forEach(e=>e.open=true)')
    dom=page.locator('section.fv-r281').evaluate_all('''sections=>{
      const links=[...document.querySelectorAll('section.fv-r281 a')];
      const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
      return {sections:sections.length, headings:sections.map(s=>s.querySelector('h2')?.textContent),
        ctas:sections.flatMap(s=>[...s.querySelectorAll('a[data-fv-cta]')].map(e=>e.href)),
        src:[...document.querySelectorAll('section.fv-r281 a[data-fv-link-purpose="official-evidence-source"]')].map(e=>e.href),
        media:[...document.querySelectorAll('section.fv-r281 [data-fv-media-record]')].map(e=>({id:e.getAttribute('data-fv-media-record'),role:e.getAttribute('data-fv-evidence-role'),rights:e.getAttribute('data-fv-image-rights'),proof:e.getAttribute('data-fv-claim-proof')})),
        allLinks:links.map(e=>({href:e.href,text:e.textContent.trim()})),
        ids,geos:document.querySelectorAll('[data-geo-lat],[data-geo-lng],[data-map-edge],[data-geo-pin]').length,
        overflowing:document.documentElement.scrollWidth-window.innerWidth,
        details:document.querySelectorAll('section.fv-r281 details').length,
        loadedImages:document.querySelectorAll('section.fv-r281 img,section.fv-r281 picture').length};
    }''')
    assert dom['sections'] == instances, ('regions-dom',dom['sections'])
    assert len(dom['ids']) == len(set(dom['ids'])), 'duplicate DOM IDs'
    assert len(dom['ctas']) == instances and all(url == FREE for url in dom['ctas']), 'editorial CTA contract'
    assert len(dom['src']) == 13*instances, ('documentary official link count',len(dom['src']))
    assert all(urlparse(u).scheme == 'https' and urlparse(u).hostname in ('www.nasa.gov','sma.nasa.gov') for u in dom['src']), 'external documentary origin'
    assert len(dom['media']) == 4*instances, ('media',len(dom['media']))
    assert all((m['id'] in MEDIA_IDS and m['role']=='contextual-media-only' and
                m['rights']=='not-cleared-for-reuse' and m['proof']=='no') for m in dom['media']), 'source/rights classification'
    assert dom['geos'] == 0 and dom['loadedImages'] == 0, 'invented geography or unreviewed downloaded media'
    assert dom['details'] == 7*instances, 'native disclosure controls missing'
    assert dom['overflowing'] <= 1, ('horizontal overflow',dom['overflowing'])
    # Source links are not commerce links. An outbound CTA to an unknown
    # merchant cannot be silently substituted for editorial continuation.
    assert all(not any(term in u['href'].lower() for term in ('payhip.com','checkout','affiliat','amazon.')) for u in dom['allLinks']), 'unauthorized merchant destination'
    nodes=ax_tree(page)
    controls=[n for n in nodes if role(n) in ('link','button','DisclosureTriangle')]
    empty=[{'role':role(n),'nodeId':n.get('nodeId')} for n in controls if not name(n)]
    assert not empty, ('unnamed controls in actual Chromium AX tree',empty[:5])
    axlinks=[n for n in nodes if role(n)=='link']
    assert len(axlinks)==39*instances,('AX link count',len(axlinks))
    assert len([n for n in nodes if role(n)=='DisclosureTriangle'])==7*instances, 'native disclosure tree roles'
    regions=[name(n) for n in nodes if role(n)=='region']
    chronologies=[name(n) for n in nodes if role(n)=='navigation']
    assert len(regions)==instances and len(set(regions))==instances and all('What the record establishes' in n and 'atlas instance' in n for n in regions), ('accessible regions',regions)
    assert len(chronologies)==instances and len(set(chronologies))==instances and all('Apollo 1 chronology' in n for n in chronologies), ('accessible chronology rails',chronologies)
    return {'instances':instances,'accessibleLinks':len(axlinks),'accessibleDisclosures':7*instances,
            'accessibleRegions':regions,'accessibleChronologies':chronologies,
            'namedControls':len(controls),'documentaryLinks':len(dom['src']),
            'contextMedia':len(dom['media']),'horizontalOverflow':dom['overflowing']}


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    assert all(git_blob(path)==digest for path,digest in PINS.items()), 'SOURCE BLOB DRIFT — REVIEW FIRST'
    subprocess.run(['php','-l',str(PHP)], check=True, capture_output=True)
    html=html_fixture()
    cases=[]; negatives=[]
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for width,font,js,forced,reduce in CONFIGS:
                print('RUN',width,font,js,forced,reduce,flush=True)
                page=browser.new_page(viewport={'width':width,'height':900},
                    java_script_enabled=js,has_touch=width<=390,
                    forced_colors='active' if forced else 'none',
                    reduced_motion='reduce' if reduce else 'no-preference')
                page.set_content(html)
                if font!=16: page.add_style_tag(content=f'html{{font-size:{font}px!important}}')
                result=contract(page)
                # Keyboard: a closed native source disclosure must open with Enter.
                page.locator('details').first.evaluate('(e)=>e.open=false')
                s=page.locator('details summary').first
                s.focus(); page.keyboard.press('Enter')
                assert page.locator('details').first.evaluate('(e)=>e.open'), 'keyboard disclosure failure'
                if (width,font,js) in ((320,64,True),(390,16,False),(1440,16,True)) and not forced:
                    page.screenshot(path=str(OUTPUT / f"r336-ax-{width}-font{font}-{'js' if js else 'nojs'}.png"), full_page=(font == 16))
                cases.append({'width':width,'rootFontPx':font,'javaScript':js,'forcedColors':forced,'reducedMotion':reduce,**result})
                page.close()
            # Multi-shortcode instance: independent accessible names and DOM anchors.
            print('RUN multi',flush=True)
            page=browser.new_page(viewport={'width':390,'height':900},java_script_enabled=False)
            page.set_content(html_fixture(instances=2))
            double=contract(page,2)
            cases.append({'case':'two-instances','javaScript':False,**double})
            page.close()
            # Unstyled no-JS means informational access, not numeric reflow compliance.
            print('RUN naked',flush=True)
            page=browser.new_page(viewport={'width':390,'height':900},java_script_enabled=False)
            page.set_content(html_fixture(style=False))
            naked=contract(page,1)
            cases.append({'case':'unstyled-nojs','javaScript':False,**naked})
            page.close()
            # Prove the gate fails closed on exact, independent adversarial mutations.
            variants=[
                ('unlabeled-source-link', "document.querySelector('section.fv-r281 a[data-fv-link-purpose]').textContent='';"),
                ('wrong-media-rights', "document.querySelector('[data-fv-media-record]').setAttribute('data-fv-image-rights','licensed-for-commerce');"),
                ('merchant-source-link', "document.querySelector('section.fv-r281 a[data-fv-link-purpose]').href='https://payhip.com/b/fake';"),
                ('duplicate-dom-id', "document.querySelector('section.fv-r281 h3').id=document.querySelector('section.fv-r281 h2').id;"),
                ('phantom-geo', "document.querySelector('section.fv-r281').setAttribute('data-geo-pin','invented');"),
                ('extra-cta', "let a=document.querySelector('a[data-fv-cta]');a.after(a.cloneNode(true));"),
                ('unnamed-region', "document.querySelector('section.fv-r281').removeAttribute('aria-labelledby');"),
            ]
            for key,mutation in variants:
                print('RUN NEG',key,flush=True)
                page=browser.new_page();page.set_content(html)
                page.locator('details').evaluate_all('(xs)=>xs.forEach(x=>x.open=true)')
                page.evaluate('() => {'+mutation+'}')
                detected=False;reason=''
                try: contract(page)
                except AssertionError as error:
                    detected=True;reason=str(error)[:200]
                assert detected, ('unsafe mutation evaded guard',key)
                negatives.append({'mutation':key,'detected':detected,'reason':reason})
                page.close()
        finally: browser.close()
    receipt={'sprint':'R336','classification':'BUILD+LOCAL TEST ONLY; NO RELEASE','timestampUTC':'2026-11-13T13:43:00Z',
        'browser':'system Chromium via Playwright CDP Accessibility.getFullAXTree (offline PHP-rendered DOM)',
        'contexts':len(cases),'passedContexts':len(cases),'negativeControls':negatives,'results':cases,
        'sourceBlobs':{str(path.relative_to(ROOT)):digest for path,digest in PINS.items()},
        'NASAImageRights':'link only; individual commercial media/endorsement review outstanding',
        'axeCore':'NOT EXECUTED — package not installed or downloadable in this environment',
        'independentScreenReader':'NOT EXECUTED','FirefoxSafari':'NOT EXECUTED','installedWordPress':False,
        'productionCWV':None,'merchantSale':None,'netRevenuePer1000QualifiedHumanSessions':None,
        'releaseGate':'HARD HOLD'}
    (OUTPUT/'r336-ax-results.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(f"PASS R336 {len(cases)} actual Chromium CDP AX contexts; {len(negatives)} adversarial mutations rejected. Not axe-core or production QA.")

if __name__=='__main__':
    main()
