#!/usr/bin/env python3
"""R337: zoom-word reflow + actual Chromium AX/NASA/rights/commerce release gate.
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
OUTPUT = ROOT / 'apollo-r337/QA'
PINS = {PHP: 'fd9e384d26d3aee8e17bef17105fad9672136b0f',
        CSS: '2bf6b75cf59db310158212d0ed9b1b6e3f1a3b04',
        STUB: 'f8987327fd6b49afcf8996c695100e3e7471c831'}
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
MEDIA_IDS = ('S67-15717', 'S66-58038', 'S67-21294', 'KSC-20170124-PH_KLS01_0090')
CONFIGS = [(w, 16, True, False, False) for w in (320,360,390,768,1024,1440,1920)]
CONFIGS += [(w,16,False,False,False) for w in (320,390,1440)]
CONFIGS += [(320,64,True,False,False),(390,64,True,False,False),(1024,64,True,False,False),(390,16,True,True,True),(1440,16,True,False,True)]


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


def word_fragments(page):
    """Detect one *word* split across lines, invisible to scrollWidth tests."""
    return page.locator('section.fv-r281 details.fv-r281__drawer summary').first.evaluate(r'''summary => {
        const node = [...summary.childNodes].find(n => n.nodeType === 3 && n.textContent.includes('Inspect'));
        if (!node) throw Error('source disclosure label missing');
        const words = [...node.textContent.matchAll(/\b(Inspect|source|custody|record)\b/g)];
        return words.map(word => {
            const range = document.createRange();
            range.setStart(node,word.index); range.setEnd(node,word.index+word[0].length);
            return {word:word[0],fragments:range.getClientRects().length};
        });
    }''')


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
    if float(page.evaluate('parseFloat(getComputedStyle(document.documentElement).fontSize)')) >= 63:
        pieces = word_fragments(page)
        assert [x['word'] for x in pieces] == ['Inspect','source','custody','record'], pieces
        assert all(x['fragments'] == 1 for x in pieces), ('R337 split word in native NASA source disclosure', pieces)
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
    expected_version='r337-'+hashlib.sha256(CSS.read_bytes()).hexdigest()[:12]
    assert f"const FV_R294_STYLE_VERSION = '{expected_version}';" in PHP.read_text(), 'stale WordPress stylesheet cache key'
    cases=[]; negatives=[]; baseline_cases=[]
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(headless=True, executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            # Demonstrate the exact previous R331 styles fail this regression.
            old_style = CSS.read_text().split('/* R337: at 320',1)[0]
            assert old_style != CSS.read_text(), 'R331 baseline reconstruction failed'
            for baseline_width in (320,390,1024):
                baseline_page=browser.new_page(viewport={'width':baseline_width,'height':900})
                baseline_page.set_content(html.replace('<style>'+CSS.read_text()+'</style>','<style>'+old_style+'</style>'))
                baseline_page.add_style_tag(content='html{font-size:64px!important}')
                pieces=word_fragments(baseline_page)
                assert any(x['fragments']>1 for x in pieces), ('previous defect not reproduced',baseline_width,pieces)
                baseline_cases.append({'width':baseline_width,'rootFontPx':64,'splitWords':pieces})
                baseline_page.close()
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
                    page.screenshot(path=str(OUTPUT / f"r337-ax-{width}-font{font}-{'js' if js else 'nojs'}.png"), full_page=(font == 16))
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
    receipt={'sprint':'R337','classification':'BUILD+LOCAL TEST ONLY; NO RELEASE','timestampUTC':'2026-11-13T13:43:00Z',
        'browser':'system Chromium via Playwright CDP Accessibility.getFullAXTree (offline PHP-rendered DOM)',
        'contexts':len(cases),'passedContexts':len(cases),'baselineRegressionCases':baseline_cases,'negativeControls':negatives,'results':cases,
        'sourceBlobs':{str(path.relative_to(ROOT)):digest for path,digest in PINS.items()},
        'NASAImageRights':'link only; individual commercial media/endorsement review outstanding',
        'axeCore':'NOT EXECUTED — unavailable in offline test runtime',
        'independentScreenReader':'NOT EXECUTED','FirefoxSafari':'NOT EXECUTED','installedWordPress':False,
        'productionCWV':None,'merchantSale':None,'netRevenuePer1000QualifiedHumanSessions':None,
        'releaseGate':'HARD HOLD'}
    (OUTPUT/'r337-ax-results.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
    print(f"PASS R337 {len(cases)} Chromium CDP AX contexts, 3 reproduced prior word-split failures, {len(negatives)} safety mutations rejected. Not axe-core or production QA.")

if __name__=='__main__':
    main()
