#!/usr/bin/env python3
"""R302 extended archive-replay offline QA: real PHP, Chromium, no external requests.
Requires php, Python playwright, local Chromium. No WordPress or axe claims.
"""
import re
import json
import hashlib
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[2]
qa = root.parent / 'QA'
qa.mkdir(exist_ok=True)
php = root / 'apollo-r281/apollo-source-experience.php'
css = (root / 'apollo-r281/assets/apollo-source-experience.css').read_text()
fixture = root / 'apollo-r301/qa/local_http_fixture.php'
subprocess.run(['php', '-l', str(php)], check=True, capture_output=True)
html = subprocess.check_output(['php', '-r', 'parse_str("instances=2",$_GET);include $argv[1];', str(fixture)], text=True)
assert html.count('data-fv-evidence-status=') == 2
assert '<script' not in html.lower()
html = re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>', '', html)
html = html.replace('</head>', '<style>' + css + '</style></head>')
url = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
passes = 0
negative_controls = 0
source_checks = 0
source_negative_controls = 0
zoom_checks = 0
screenshots = []
allowed = {
 'https://www.nasa.gov/mission/apollo-1/',
 'https://www.nasa.gov/history/Apollo204/proceed.html',
 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/',
 'https://www.nasa.gov/history/Apollo204/narr.html',
 'https://www.nasa.gov/history/Apollo204/15.html',
 'https://sma.nasa.gov/sma-disciplines/accllp/apollo-1',
}
def require_sources(anchors):
    assert len(anchors)==13
    for a in anchors:
        assert a['href'] in allowed, 'unreviewed external egress URL'
        assert a['purpose']=='official-evidence-source'
        assert a['kind']=='noncommercial-source-reference', 'source is not a commercial event'
        assert a['cta'] is None and 'noreferrer' in a['rel']
def require_editorial(cta):
    assert cta.get_attribute('data-fv-conversion-kind') == 'editorial-continuation', 'non-editorial event category'
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width in (320, 390, 768, 1440, 1920):
        for js in (False, True):
            page = browser.new_page(viewport={'width':width, 'height':850}, java_script_enabled=js,
                                    reduced_motion='reduce', has_touch=True)
            page.set_content(html)
            sections = page.locator('section.fv-r281')
            assert sections.count() == 2
            names = []
            for section in sections.all():
                assert section.get_attribute('data-fv-experience') == 'apollo-1'
                assert section.get_attribute('data-fv-funnel-scope') == 'editorial-evidence'
                assert section.get_attribute('data-fv-evidence-status') == 'editorial-review-pending'
                assert section.locator('[data-fv-funnel-step="evidence-to-investigation"]').count() == 1
                cta = section.locator('[data-fv-cta]')
                assert cta.count() == 1
                assert cta.get_attribute('data-fv-cta') == 'apollo-read-free-investigation'
                require_editorial(cta)
                assert cta.get_attribute('href') == url
                links = section.locator('a[data-fv-link-purpose="official-evidence-source"]').evaluate_all('''els=>els.map(e=>({href:e.href, purpose:e.dataset.fvLinkPurpose,kind:e.dataset.fvConversionKind,cta:e.dataset.fvCta||null,rel:e.rel}))''')
                require_sources(links)
                source_checks += len(links)
                for change in ('kind','href','tracking'):
                    tampered = [dict(x) for x in links]
                    if change=='kind': tampered[0]['kind']='merchant-confirmed-purchase'
                    if change=='href': tampered[0]['href']='https://www.nasa.gov.evil.example/not-nasa'
                    if change=='tracking': tampered[0]['href'] += '?utm_source=unsupported'
                    try: require_sources(tampered)
                    except AssertionError: source_negative_controls += 1
                    else: raise AssertionError('corrupted source was accepted')
                assert section.locator('script,form').count() == 0
                names.append(section.locator('h2').inner_text())
                drawer = section.locator('.fv-r281__drawer').first
                drawer.locator('summary').focus()
                page.keyboard.press('Enter')
                assert drawer.get_attribute('open') is not None
                page.keyboard.press('Space')
                assert drawer.get_attribute('open') is None
                section.locator('.fv-r281__source-jump a').first.click()
                assert section.locator('.fv-r281__source-list li').first.evaluate('(e)=>document.activeElement===e')
                passes += 1
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            ids = page.locator('[id]').evaluate_all('(xs)=>xs.map(x=>x.id)')
            assert len(ids) == len(set(ids))
            ax = page.context.new_cdp_session(page).send('Accessibility.getFullAXTree')['nodes']
            regions = [n.get('name', {}).get('value') for n in ax if n.get('role', {}).get('value') == 'region'
                       and 'What the record establishes' in (n.get('name', {}).get('value') or '')]
            assert len(regions) == 2 and len(set(regions)) == 2
            # Deliberate policy failure: never count an editorial click as a sale.
            cta = sections.first.locator('[data-fv-cta]')
            cta.evaluate("e=>e.setAttribute('data-fv-conversion-kind','paid-order')")
            try:
                require_editorial(cta)
            except AssertionError as exc:
                assert str(exc) == 'non-editorial event category'
                negative_controls += 1
            else:
                raise AssertionError('false paid-order event was accepted')
            page.evaluate('document.documentElement.style.fontSize="200%"')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            zoom_checks += 1
            page.evaluate('document.documentElement.style.fontSize=""')
            if not js:
                page.evaluate('window.scrollTo(0,0)')
                output = qa / f'r302-{width}-nojs.png'
                page.screenshot(path=str(output),full_page=True,animations='disabled')
                screenshots.append(str(output.relative_to(root.parent)))
            page.close()
    # Actual browser print containing the complete disclosure and primary links.
    page = browser.new_page(viewport={'width':390,'height':850},java_script_enabled=False)
    page.set_content(html)
    # Normalize actual Chromium PDF metadata so independent runs produce the
    # same file digest; retain hyperlinks and historical content.
    import fitz
    pdf_doc = fitz.open(stream=page.pdf(format='A4',print_background=True),filetype='pdf')
    metadata = pdf_doc.metadata.copy()
    metadata['creationDate'] = 'D:19800101000000Z'
    metadata['modDate'] = 'D:19800101000000Z'
    pdf_doc.set_metadata(metadata)
    pdf_doc.save(str(qa/'r302-390-print.pdf'),garbage=4,deflate=1,no_new_id=1)
    pdf_doc.close()
    page.close()
    browser.close()
assert passes == 20 and negative_controls == 10 and source_checks == 260
assert source_negative_controls == 60 and zoom_checks == 10
import fitz
pdf = fitz.open(qa/'r302-390-print.pdf')
full_text=' '.join(page.get_text() for page in pdf)
assert 'January 31' in full_text and 'February 3' in full_text
links=sum(len(page.get_links()) for page in pdf)
assert len(pdf)==13 and links>=25
receipt = {'sprint':'R302','status':'STAGING_NOT_LIVE',
 'php_sha256':hashlib.sha256(php.read_bytes()).hexdigest(),
 'css_sha256':hashlib.sha256(css.encode()).hexdigest(),
 'chromium_contexts':10,'nasa_source_anchor_checks':source_checks,
 'negative_controls_rejected':source_negative_controls + negative_controls,
 'font_200pct_responsive_checks':zoom_checks,'screen_widths':[320,390,768,1440,1920],
 'javascript':[False,True],'screenshots':screenshots,
 'print_pdf_pages':len(pdf),'print_pdf_links':links,
 'genuine_axe_core':'NOT_EXECUTED','installed_wordpress':'NOT_VERIFIED',
 'browser_http_csp':'NOT_VERIFIED','field_web_vitals':'NOT_VERIFIED',
 'merchant_sales':'NOT_OBSERVABLE','grok_asset_id':'NOT_VERIFIED'}
(qa/'r302-browser-receipt.json').write_text(json.dumps(receipt,sort_keys=True,indent=2)+'\n')
print(json.dumps(receipt,sort_keys=True,indent=2))
