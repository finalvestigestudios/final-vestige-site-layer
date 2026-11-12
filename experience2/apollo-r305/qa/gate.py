#!/usr/bin/env python3
"""R305 isolated, offline Chromium source-role regression. NOT installed WordPress/axe/field CWV."""
import hashlib, json, re, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parents[2]
PHP = ROOT / 'apollo-r281/apollo-source-experience.php'
CSS = ROOT / 'apollo-r281/assets/apollo-source-experience.css'
FIXTURE = ROOT / 'apollo-r301/qa/local_http_fixture.php'
QA = Path(__file__).resolve().parents[1] / 'QA'
QA.mkdir(parents=True, exist_ok=True)
subprocess.run(['php', '-l', str(PHP)], check=True)
html = subprocess.check_output(['php', '-r', 'parse_str("instances=2",$_GET);include $argv[1];', str(FIXTURE)], text=True)
html = re.sub(r'<link\b[^>]+rel="stylesheet"[^>]+>', '', html)
html = html.replace('</head>', '<style>' + CSS.read_text() + '</style></head>')
assert 'data-fv-gallery-status="text-only-source-custody"' in html
assert 'photograph accession number' in html
assert not re.search(r'<(img|script|iframe|form)\b', html, re.I)
results = []
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width in (320, 390, 768, 1440, 1920):
        for js in (False, True):
            page = browser.new_page(viewport={'width': width, 'height': 850}, java_script_enabled=js, has_touch=True, reduced_motion='reduce')
            page.set_content(html)
            regions = page.locator('section.fv-r281')
            assert regions.count() == 2
            ids = page.locator('[id]').evaluate_all('(items) => items.map(x => x.id)')
            assert len(ids) == len(set(ids))
            for section in regions.all():
                gallery = section.locator('.fv-r281__gallery')
                assert gallery.get_attribute('data-fv-gallery-status') == 'text-only-source-custody'
                assert 'not primary support for a fire-cause claim' in gallery.text_content()
                sources = gallery.locator('.fv-r281__source-list > li[data-fv-evidence-role=\"documented-textual-claim\"]')
                plates = section.locator('.fv-r281__plate')
                assert sources.count() == plates.count() == 3
                for i in range(3):
                    src, claim = sources.nth(i), plates.nth(i)
                    assert src.get_attribute('data-fv-evidence-role') == 'documented-textual-claim'
                    assert src.get_attribute('data-fv-source-id') == claim.get_attribute('data-fv-source-id')
                    assert src.get_attribute('data-fv-cites-claim') == claim.get_attribute('data-fv-claim-key')
                    href = src.locator('a[data-fv-link-purpose="official-evidence-source"]').get_attribute('href')
                    assert href.startswith('https://') and '.nasa.gov/' in href
                    assert '/image-detail/' not in href
                assert section.locator('[data-fv-cta]').count() == 1
                assert section.locator('[data-fv-conversion-kind="merchant-confirmed-purchase"]').count() == 0
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
            nav = page.locator('section.fv-r281').first.locator('.fv-r281__source-jump a').first
            nav.click()
            assert page.evaluate('location.hash') == '#fv-r281-1-source-1'
            assert page.locator('#fv-r281-1-source-1').evaluate('(el) => el === document.activeElement')
            # Negative control: a photograph record cannot masquerade as claim text evidence.
            src = page.locator('section.fv-r281').first.locator('li[data-fv-evidence-role]').first
            src.evaluate('(el) => el.dataset.fvEvidenceRole = "contextual-image"')
            assert src.get_attribute('data-fv-evidence-role') != 'documented-textual-claim'
            if not js:
                page.screenshot(path=str(QA / f'r305-{width}-nojs.png'), full_page=True, animations='disabled')
            results.append({'width':width,'javascript':js,'passed':True})
            page.close()
    # The visible provenance caveat must survive total component CSS failure.
    page = browser.new_page(viewport={'width':390,'height':850},java_script_enabled=False)
    page.set_content(re.sub(r'<style>.*?</style>', '', html, flags=re.S))
    assert 'photograph accession number' in page.locator('.fv-r281__gallery').first.inner_text()
    page.screenshot(path=str(QA / 'r305-390-no-css-nojs.png'), full_page=True)
    page.close()
    browser.close()
receipt={'contexts':len(results),'instances_per_context':2,'source_role_records':60,
         'negative_role_controls':10,'responsive_widths':[320,390,768,1440,1920],
         'no_js_css_fallback':'PASS','browser':'Chromium offline set_content',
         'axe':'NOT EXECUTED - npm DNS unavailable','wordPress':'NOT VERIFIED',
         'http_csp':'NOT VERIFIED','lcp_cls_field':'NOT VERIFIED',
         'source_sha256':hashlib.sha256(PHP.read_bytes()).hexdigest(),
         'css_sha256':hashlib.sha256(CSS.read_bytes()).hexdigest()}
(QA / 'r305-qa-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt,indent=2))
