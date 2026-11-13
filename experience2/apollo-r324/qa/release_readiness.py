#!/usr/bin/env python3
"""Apollo R324 independent release gate. Real Chromium; no WordPress production writes.

Run with: python experience2/apollo-r324/qa/release_readiness.py
Optional genuine axe engine: AXE_CORE_JS=/path/to/official/axe.min.js python ...
An absent axe engine is a BLOCKED release gate, NOT an accessibility pass.
"""
import hashlib, io, json, os, re, subprocess
from pathlib import Path
from urllib.parse import urlsplit
from pypdf import PdfReader
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PHP = ROOT / 'apollo-r281/apollo-source-experience.php'
CSS = ROOT / 'apollo-r281/assets/apollo-source-experience.css'
JS = ROOT / 'apollo-r281/assets/apollo-cache-continuation.js'
STUB = ROOT / 'apollo-r320/qa/wp_late_shortcodes.php'
OUTPUT = ROOT / 'apollo-r324/QA'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
CAMPAIGN = 'utm_source=youtube&utm_medium=organic_social&utm_campaign=history_pilot_2026_11&utm_content=apollo1_yt_longform001'
SHA = {'php':'bd1d71d60ddee92dc0cc362923101692372ed577',
       'css':'7c0e58782a8ec7b23f28da784a84c827f117914a',
       'js':'f85617e5f12ba747908ac507261f69c377369de7'}
NASA = {'https://www.nasa.gov/mission/apollo-1/',
        'https://www.nasa.gov/history/Apollo204/proceed.html',
        'https://www.nasa.gov/history/Apollo204/narr.html',
        'https://www.nasa.gov/history/Apollo204/15.html',
        'https://sma.nasa.gov/sma-disciplines/accllp/apollo-1',
        'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
        'https://www.nasa.gov/image-detail/amf-s67-15717/',
        'https://www.nasa.gov/image-detail/amf-s66-58038/',
        'https://www.nasa.gov/image-detail/amf-s67-21294/',
        'https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/'}

def git_blob(path):
    raw=path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def fixture():
    raw=subprocess.check_output(['php',str(STUB),'late-dynamic','1'], text=True)
    html, tail=raw.split('<!--R320_QUEUE:')
    assert json.loads(tail.split('-->')[0])['calls']==1
    return html.replace('</head>', '<style>'+CSS.read_text()+'</style></head>')

def external_links(page):
    links=page.locator('section.fv-r281 a[href^="https://"]').evaluate_all('(els) => els.map(e => e.href)')
    return links

def assert_custody(page):
    assert page.locator('section.fv-r281').count()==1
    assert page.locator('.fv-r281__plate').count()==3
    assert page.locator('.fv-r281__source-list > li').count()==3
    assert page.locator('[data-fv-claim-proof="no"]').count()==4
    assert page.locator('[data-fv-image-rights="not-cleared-for-reuse"]').count()==4
    assert page.locator('a[data-fv-cta]').count()==1
    assert page.locator('a[href^="http://"]').count()==0
    assert page.locator('[data-lat],[data-lng],[data-longitude],[data-geo-edge]').count()==0
    assert page.locator('img,video,iframe').count()==0
    assert page.locator('section.fv-r281 [data-fv-conversion-kind*="purchase"]').count()==0
    links=external_links(page)
    assert set(links)==NASA | {FREE}, set(links).symmetric_difference(NASA | {FREE})
    assert not any('utm_' in u or '?' in urlsplit(u).query for u in links)
    assert page.evaluate('''() => [...document.querySelectorAll('section.fv-r281 a[href^="#"]')]
      .every(a => !!document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1))))''')
    assert page.locator('section.fv-r281').inner_text().count('Editorial review remains pending') >= 1

def hrefs_in_pdf(payload):
    urls=[]
    for pg in PdfReader(io.BytesIO(payload)).pages:
        for ref in pg.get('/Annots',[]):
            action=ref.get_object().get('/A')
            if action:
                assert str(action.get('/S')) == '/URI'
                urls.append(str(action.get('/URI')))
    return urls

def check_ax_names(page):
    client=page.context.new_cdp_session(page)
    tree=client.send('Accessibility.getFullAXTree')['nodes']
    relevant=[n for n in tree if not n.get('ignored') and n.get('role',{}).get('value') in
              ('link','button','checkbox','combobox','searchbox','textbox')]
    unnamed=[n for n in relevant if not str(n.get('name',{}).get('value','')).strip()]
    assert not unnamed, 'Unnamed interactive AX nodes: '+repr(unnamed[:2])
    return len(relevant)

def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for k,p in [('php',PHP),('js',JS),('css',CSS)]:
        assert git_blob(p)==SHA[k], f'{k} source identity mismatch'
    subprocess.run(['php','-l',str(PHP)],check=True,capture_output=True)
    subprocess.run(['node','--check',str(JS)],check=True,capture_output=True)
    html=fixture(); axe_path=os.environ.get('AXE_CORE_JS','')
    if os.environ.get('REQUIRE_AXE')=='1' and not axe_path:
        raise SystemExit('R324 RELEASE BLOCKED: genuine axe-core bundle is required (set AXE_CORE_JS)')
    if axe_path:
        assert Path(axe_path).is_file(), 'AXE_CORE_JS specified but file missing: fail closed'
    rows=[]; axe_observations=[]; negatives=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        try:
            for width in (320,360,390,768,1024,1440,1920):
                for js in (True,False):
                    ctx=browser.new_context(viewport={'width':width,'height':920},java_script_enabled=js,
                         reduced_motion='reduce',has_touch=width<=390)
                    page=ctx.new_page()
                    page.goto('about:blank?'+CAMPAIGN)
                    page.evaluate('''() => { window.__lcp = []; window.__cls=0;
                     new PerformanceObserver(l => l.getEntries().forEach(x=>window.__lcp.push(x.startTime)))
                       .observe({type:'largest-contentful-paint',buffered:true});
                     new PerformanceObserver(l=>l.getEntries().forEach(x=>{
                       if(!x.hadRecentInput)window.__cls+=x.value;}))
                       .observe({type:'layout-shift',buffered:true}); }''')
                    page.set_content(html)
                    if js: page.add_script_tag(content=JS.read_text())
                    assert_custody(page)
                    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                    assert page.evaluate('getComputedStyle(document.querySelector("section.fv-r281")).visibility')=='visible'
                    assert page.locator('section.fv-r281 a').count()>=20
                    ax_names=check_ax_names(page)
                    source=page.locator('a[href$="source-1"]').first
                    source.click()
                    assert page.evaluate('location.hash').endswith('source-1')
                    assert page.evaluate('document.activeElement.id').endswith('source-1')
                    jump=page.locator('a[href$="authority-1"]').first
                    jump.click()
                    assert page.locator('.fv-r291__authority-disclosure').first.evaluate('(e)=>e.open')
                    assert page.evaluate('document.activeElement.id').endswith('authority-1')
                    cta=page.locator('a[data-fv-cta]')
                    cta.focus(); page.keyboard.press('Shift+F10')
                    if js: assert 'utm_campaign=' in cta.get_attribute('href')
                    else: assert cta.get_attribute('href')==FREE
                    # Print must scrub staged campaign identifiers from clickable PDF URI annotations.
                    pdf=page.pdf(format='A4',print_background=True)
                    urls=hrefs_in_pdf(pdf)
                    assert set(urls)==NASA | {FREE} and urls.count(FREE)==1
                    assert not any('utm_' in u for u in urls)
                    assert cta.get_attribute('href')==FREE
                    if axe_path and js:
                        page.add_script_tag(path=axe_path)
                        result=page.evaluate('''async () => {
                          const r=await axe.run(document.querySelector('section.fv-r281'),
                            {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa','best-practice']}});
                          return {version:axe.version,violations:r.violations.map(x=>({id:x.id,impact:x.impact,
                            nodes:x.nodes.map(y=>y.target)})),incomplete:r.incomplete.map(x=>x.id),passes:r.passes.length}; }''')
                        axe_observations.append({'width':width,**result})
                    if width in (390,1440) and js:
                        page.screenshot(path=str(OUTPUT/f'r324-{width}-chromium.png'),full_page=True)
                        (OUTPUT/f'r324-{width}-source-audit.pdf').write_bytes(pdf)
                    page.wait_for_timeout(140)
                    perf=page.evaluate('({lcp:window.__lcp.at(-1)??null,cls:window.__cls})')
                    rows.append({'width':width,'js':js,'axInteractiveNamed':ax_names,
                                 'sourceLinkCount':len(urls),'offlineFixture':perf})
                    ctx.close()
            # A deliberate source tamper MUST be detected; this exercises the custody gate.
            ctx=browser.new_context();page=ctx.new_page();page.goto('about:blank');page.set_content(html)
            page.locator('[data-fv-image-rights]').first.evaluate('(e)=>e.setAttribute("data-fv-image-rights","commercially-cleared")')
            try:assert_custody(page)
            except AssertionError: negatives.append('unreviewed-commercial-media-rights')
            else:raise AssertionError('Media-rights mutation was not rejected')
            page.set_content(html)
            page.locator('a[data-fv-cta]').first.evaluate('(e)=>e.href="https://merchant.example/checkout"')
            try:assert_custody(page)
            except AssertionError:negatives.append('unapproved-merchant-cta')
            else:raise AssertionError('Merchant mutation was not rejected')
            page.set_content(html)
            page.locator('section.fv-r281').first.evaluate('(e)=>{const i=document.createElement("i"); i.setAttribute("data-lat","28");e.append(i)}')
            try:assert_custody(page)
            except AssertionError:negatives.append('invented-geopin')
            else:raise AssertionError('Invented pin was not rejected')
            page.set_content(html)
            # AX tree is independent from source-link custody; fail unnamed link by explicit mutation.
            page.locator('section.fv-r281 a[data-fv-cta]').evaluate('(e)=>{e.textContent="";e.setAttribute("aria-label","")}')
            try:check_ax_names(page)
            except AssertionError:negatives.append('unnamed-accessible-link')
            else:raise AssertionError('Unnamed accessible link was not rejected')
            ctx.close()
        finally:browser.close()
    if axe_observations:
        assert not any(r['violations'] for r in axe_observations), 'Genuine axe violations: '+json.dumps(axe_observations)
    receipt={'component':'Apollo Evidence Atlas','reviewedBaseCommit':'9734ecb401a91d184f2a7bc8779845bc119942b5',
             'sourceBlobs':SHA,'browser':'Chromium / Playwright','contexts':rows,
             'negativeControls':negatives,'axeCoreExecuted':bool(axe_observations),
             'axeResults':axe_observations,'axeStatus':'EXECUTED' if axe_observations else 'BLOCKED: actual axe-core bundle unavailable, never substituted with custom assertions',
             'realHttpBrowser':'BLOCKED: Chromium net::ERR_BLOCKED_BY_ADMINISTRATOR on 127.0.0.1',
             'installedWordPress':'NOT TESTED','performanceScope':'OFFLINE about:blank fixture; NOT field CWV',
             'revenue':'NOT COMPUTABLE; no verified paid orders/qualified human sessions'}
    (OUTPUT/'r324-qa-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(f'R324 PASS {len(rows)}/{len(rows)} actual Chromium contexts; {len(negatives)} negative controls; AXE={receipt["axeStatus"]}')

if __name__=='__main__':main()
