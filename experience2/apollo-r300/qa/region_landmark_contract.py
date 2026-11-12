#!/usr/bin/env python3
"""R300 actual-PHP isolated Chromium region naming test, no network or WordPress.

Run from any working directory. A local PHP fixture and the source-controlled CSS
are rendered offline; no production traffic, WP writes, fake accessibility scans.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

EX = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[3] / 'QA'
OUT.mkdir(parents=True, exist_ok=True)
php = EX / 'apollo-r294/qa/local_http_fixture.php'
css = (EX/'apollo-r281/assets/apollo-source-experience.css').read_text(encoding='utf-8')
html = subprocess.check_output(['php', '-r', 'parse_str("instances=2", $_GET);include $argv[1];', str(php)], text=True)
# The fixture is sourced directly from the actual PHP, without synthetic markup.
assert 'What the record establishes<span class="fv-r298__sr-only">' in html
assert html.count('data-fv-evidence-status=') == 2
html = re.sub(r'<link\b[^>]*rel="stylesheet"[^>]*>', '', html)
html = html.replace('</head>', '<style>' + css + '</style></head>')
regions = []
receipts = {'test': 'R300 PHP-backed Chromium accessible region landmarks',
            'status': 'PASS OFFLINE', 'contexts': 0, 'regions': 0,
            'native_keyboard': 0, 'source_focus': 0, 'negative_controls': 0,
            'screenshots': [], 'axe': 'NOT EXECUTED (package unavailable)',
            'http_csp': 'NOT BROWSER-VERIFIED',
            'installed_wordpress': 'NOT EXECUTED',
            'field_lcp_cls_inp': 'NOT MEASURED',
            'fixture_cwv': []}

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width in [320, 390, 768, 1440, 1920]:
        for js in [False, True]:
            page = browser.new_page(viewport={'width': width, 'height': 860},
                                       java_script_enabled=js, reduced_motion='reduce',
                                       has_touch=True)
            page.goto('about:blank')
            page.evaluate('''() => {
                window.__r300Vitals = {lcp: [], cls: []};
                new PerformanceObserver(list => window.__r300Vitals.lcp.push(...list.getEntries().map(e => e.startTime))).observe({type: 'largest-contentful-paint', buffered: true});
                new PerformanceObserver(list => window.__r300Vitals.cls.push(...list.getEntries().filter(e => !e.hadRecentInput).map(e => e.value))).observe({type: 'layout-shift', buffered: true});
            }''')
            page.set_content(html, wait_until='load')
            page.wait_for_timeout(180)
            sections = page.get_by_role('region', name=re.compile('What the record establishes'))
            assert sections.count() == 2, f'{width}/{js}: region count wrong'
            names = sections.evaluate_all('xs => xs.map(x => x.querySelector("h2").textContent.trim())')
            assert len(set(names)) == 2, f'{width}/{js}: duplicate region names {names}'
            assert names == ['What the record establishes — atlas instance 1',
                             'What the record establishes — atlas instance 2'], names
            # Exercise Chromium's real accessibility tree; DOM text alone is not an AT receipt.
            cdp = page.context.new_cdp_session(page)
            ax = cdp.send('Accessibility.getFullAXTree')['nodes']
            names_ax = [n.get('name', {}).get('value') for n in ax
                        if n.get('role', {}).get('value') == 'region'
                        and 'What the record establishes' in (n.get('name', {}).get('value') or '')]
            assert len(names_ax) == 2 and len(set(names_ax)) == 2, names_ax
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'), f'overflow {width}/{js}'
            ids = page.locator('[id]').evaluate_all('els => els.map(el => el.id)')
            assert len(ids) == len(set(ids))
            for section in sections.all():
                assert section.locator('h2').is_visible()
                assert section.locator('a[href^="https://finalvestige.com/"]').count() == 1
                assert section.locator('a[href*="nasa.gov/"]').count() >= 12
                # Native keyboard control and subsequent source deep-link focus.
                disclosure = section.locator('.fv-r281__drawer').first
                disclosure.locator('summary').focus()
                page.keyboard.press('Enter')
                assert disclosure.get_attribute('open') is not None
                page.keyboard.press('Space')
                assert disclosure.get_attribute('open') is None
                receipts['native_keyboard'] += 2
                source_link = section.locator('.fv-r281__source-jump a').first
                source_link.click()
                target = section.locator('.fv-r281__source-list li').first
                assert target.evaluate('(el) => document.activeElement === el'), 'native anchor focus failed'
                receipts['source_focus'] += 1
                # Existing one-action placement must not regress.
                order = section.evaluate('s => { const q = x=>s.querySelector(x); return !!(q(".fv-r281__plate:last-child").compareDocumentPosition(q("footer.fv-r281__next"))&4) && !!(q("footer.fv-r281__next").compareDocumentPosition(q(".fv-r281__reconciliation"))&4); }')
                assert order
            vital = page.evaluate('window.__r300Vitals')
            receipts['fixture_cwv'].append({'width': width, 'javascript': js,
                'lcp_ms': round(max(vital['lcp']), 1) if vital['lcp'] else None,
                'cls': round(sum(vital['cls']), 5)})
            # Negative control from the *same* PHP-rendered output: remove only
            # instance name nodes. The legacy DOM remains structurally identical
            # but the accessibility tree must now expose duplicate region names.
            page.locator('h2 > .fv-r298__sr-only').evaluate_all('xs => xs.forEach(el => el.remove())')
            ax_bad = cdp.send('Accessibility.getFullAXTree')['nodes']
            bad = [n.get('name', {}).get('value') for n in ax_bad
                   if n.get('role', {}).get('value') == 'region'
                   and 'What the record establishes' in (n.get('name', {}).get('value') or '')]
            assert len(bad) == 2 and len(set(bad)) == 1, f'control did not reproduce defect: {bad}'
            receipts['negative_controls'] += 1
            # Restore from authentic source before screenshot.
            page.set_content(html)
            if not js:
                fname = f'r300-{width}-nojs.png'
                page.screenshot(path=str(OUT/fname), full_page=True, animations='disabled')
                receipts['screenshots'].append({'file': fname, 'sha256': hashlib.sha256((OUT/fname).read_bytes()).hexdigest()})
                if width == 390:
                    pdf = OUT/'r300-390-print.pdf'
                    page.pdf(path=str(pdf), print_background=True, prefer_css_page_size=True,
                             format='A4')
                    # Chromium's default PDF metadata embeds the current clock;
                    # normalize it for deterministic evidence distribution.
                    # Print hyperlinks survive the rewrite and are rechecked.
                    tmp_pdf = OUT/'r300-390-print-normalized.pdf'
                    w = PdfWriter(); w.append(str(pdf))
                    w.add_metadata({'/Title': 'Apollo Evidence Atlas R300 offline QA',
                                    '/Creator': 'FV R300 reproducible fixture',
                                    '/CreationDate': 'D:19800101000000Z',
                                    '/ModDate': 'D:19800101000000Z'})
                    with tmp_pdf.open('wb') as f: w.write(f)
                    tmp_pdf.replace(pdf)
                    annotations = sum(len(pg.get('/Annots', [])) for pg in PdfReader(str(pdf)).pages)
                    assert annotations >= 50, f'print lost NASA hyperlinks: {annotations}'
                    receipts['print_pdf'] = {'file': pdf.name, 'sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(), 'pages': len(PdfReader(str(pdf)).pages), 'annotations': annotations}
            receipts['contexts'] += 1
            receipts['regions'] += 2
            page.close()
    # CSS absent: fail-open hidden instance text becomes visible, not omitted.
    p2=browser.new_page(viewport={'width':390,'height':850}, java_script_enabled=False)
    p2.set_content(re.sub(r'<style>.*?</style>', '', html, count=1, flags=re.S))
    assert p2.locator('h2 .fv-r298__sr-only').first.is_visible()
    receipts['css_fail_open'] = 'PASS'
    p2.close()
    browser.close()

assert receipts['contexts'] == 10
assert receipts['native_keyboard'] == 40
assert receipts['negative_controls'] == 10
(OUT/'r300-browser-receipt.json').write_text(json.dumps(receipts, indent=2, sort_keys=True)+'\n')
print(json.dumps({k:v for k,v in receipts.items() if k not in ('screenshots','print_pdf','fixture_cwv')}, sort_keys=True))
print('OFFLINE FIXTURE browser PerformanceObserver LCP/CLS (not field CWV):', json.dumps(receipts['fixture_cwv']))
