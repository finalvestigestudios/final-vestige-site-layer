#!/usr/bin/env python3
"""R339 isolated PHP-rendered ChronologyRail browser + source custody acceptance.
Run from repository checkout: python experience2/apollo-r339/qa/chronology_gate.py
Writes screenshots & structured receipts to FV_R339_OUT or /tmp/fv-apollo-r339.
No WordPress installation, axe-core, paid endpoint, or external HTTP is exercised.
"""
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parents[1]
MODULE = HERE / 'chronology-rail.php'
CSS = HERE / 'assets/chronology-rail.css'
OUT = Path(os.environ.get('FV_R339_OUT', '/tmp/fv-apollo-r339'))
OUT.mkdir(parents=True, exist_ok=True)
BOARD = 'https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
AFTERMATH = 'https://www.nasa.gov/history/55-years-ago-the-apollo-1-fire-and-its-aftermath/'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
TIMES = ('23:31:04.7', 'About 23:31:12', '23:31:16.8', 'About 23:31:19', '23:31:22.4', 'Following the 1967 fire')


def digest(path):
    b = path.read_bytes()
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def custody(markup):
    errors = []
    soup = BeautifulSoup(markup, 'html.parser')
    roots = soup.select('section[data-fv-r339]')
    if len(roots) != 2: errors.append('expected two native instances')
    ids = [t['id'] for t in soup.select('[id]')]
    if len(ids) != len(set(ids)): errors.append('duplicate document IDs')
    for node in soup.select('[aria-labelledby]'):
        if any(i not in ids for i in node.get('aria-labelledby', '').split()):
            errors.append('unresolved accessible label')
    for root in roots:
        events = root.select('ol.fv-apollo-r339__events > li')
        if len(events) != 6: errors.append('missing or duplicated event')
        chrono = [e.get_text(' ', strip=True) for e in events]
        for i, time in enumerate(TIMES):
            if i >= len(chrono) or time not in chrono[i]: errors.append(f'event {i+1} sequence drift')
        target_ids = {x.get('id') for x in events}
        navlinks = root.select('nav a[href^="#"]')
        if len(navlinks) != 6 or any(a['href'][1:] not in target_ids for a in navlinks):
            errors.append('chronology native anchors broken')
        if len(navlinks) == 6 and any(t not in navlinks[i].get_text(' ', strip=True) for i, t in enumerate(TIMES)):
            errors.append('navigation timeline markers drifted')
        drawers = root.select('details.fv-apollo-r339__source')
        if len(drawers) != 6: errors.append('native source drawer missing')
        links = root.select('a[data-fv-r339-source]')
        if [a.get('href') for a in links] != [BOARD]*5 + [AFTERMATH]:
            errors.append('documentary source URL or chronology drift')
        if [a.get('data-fv-r339-source') for a in links] != ['original-board']*5 + ['later-nasa-history']:
            errors.append('later history incorrectly classed as contemporaneous')
        cta = root.select('a[data-fv-r339-cta="editorial"]')
        if len(cta) != 1 or cta[0].get('href') != FREE: errors.append('one existing free investigation continuation required')
        if 'most probable initiator' not in root.get_text(' ', strip=True) or 'did not conclusively' not in root.get_text(' ', strip=True):
            errors.append('Board uncertainty qualifier missing in this instance')
        if any(urlsplit(a['href']).hostname not in ('www.nasa.gov', 'finalvestige.com') for a in root.select('a[href^="http"]')):
            errors.append('unexpected external host')
    if any(p in markup.lower() for p in ('payhip.', 'data-geo-pin', 'data-map-edge', 'data-fv-r339-cta="purchase"')):
        errors.append('unapproved purchase or fabricated geography')
    if 'most probable initiator' not in markup or 'did not conclusively' not in markup:
        errors.append('Board probability qualifier absent')
    if re.search(r'<img\b|<iframe\b|<script\b', markup, re.I): errors.append('unapproved media/script')
    return errors


def fixture():
    php = '''<?php define('ABSPATH',__DIR__); function add_shortcode($x,$y){}; require %s; echo fv_apollo_r339_shortcode(); echo fv_apollo_r339_shortcode(); ?>''' % json.dumps(str(MODULE))
    result = subprocess.run(['php'], input=php, text=True, capture_output=True, check=True)
    assert not result.stderr, result.stderr
    body = result.stdout
    result = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+CSS.read_text()+'</style></head><body style="margin:0">'+body+'</body></html>'
    return body, result


def main():
    assert subprocess.run(['php', '-l', str(MODULE)], capture_output=True).returncode == 0
    body, page_html = fixture()
    assert not custody(body), custody(body)
    bad = [
        body.replace(BOARD, 'https://payhip.com/b/unverified', 1),
        body.replace('most probable initiator', 'proven initiator', 1),
        body.replace('data-fv-r339-cta="editorial"', 'data-fv-r339-cta="purchase"', 1),
        body.replace('data-fv-r339>', 'data-geo-pin="invented">', 1),
        body.replace('23:31:04.7', '23:31:09.7', 1),
        body.replace('data-fv-r339-source="later-nasa-history"', 'data-fv-r339-source="original-board"', 1),
    ]
    assert all(custody(x) for x in bad), 'negative-control escaped'
    cases, screenshots = [], []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.environ.get('CHROMIUM', '/usr/bin/chromium'), args=['--no-sandbox'])
        try:
            for width, js, root_px, contrast, motion in (
                [(w, True, 16, False, False) for w in (320, 360, 390, 768, 1024, 1440, 1920)] +
                [(w, False, 16, False, False) for w in (320, 390, 1440)] +
                [(320, True, 32, False, False), (320, True, 64, False, False),
                 (390, True, 16, True, True), (1440, True, 16, True, True)]
            ):
                page = browser.new_page(viewport={'width':width, 'height':900}, java_script_enabled=js, has_touch=width <= 390,
                    forced_colors='active' if contrast else 'none', reduced_motion='reduce' if motion else 'no-preference')
                try:
                    page.evaluate("""() => { window.__r339Perf={lcpMs:null,cls:0}; try {new PerformanceObserver(list => {for(const e of list.getEntries())window.__r339Perf.lcpMs=Math.round(e.startTime);}).observe({type:'largest-contentful-paint',buffered:true});new PerformanceObserver(list => {for(const e of list.getEntries())if(!e.hadRecentInput)window.__r339Perf.cls+=e.value;}).observe({type:'layout-shift',buffered:true});}catch(e){} }""")
                    page.set_content(page_html, wait_until='load')
                    if root_px != 16: page.add_style_tag(content=f'html{{font-size:{root_px}px!important}}')
                    data = page.evaluate("""() => {
                        const roots = [...document.querySelectorAll('[data-fv-r339]')];
                        const all = [...document.querySelectorAll('[id]')].map(e=>e.id);
                        const links = [...document.querySelectorAll('.fv-apollo-r339 a')].map(a=>{
                          const r=a.getBoundingClientRect();return {width:r.width,height:r.height,left:r.left,right:r.right};});
                        return {roots:roots.length,idsUnique:new Set(all).size===all.length,events:roots.map(r=>r.querySelectorAll('.fv-apollo-r339__event').length),
                          navs:roots.map(r=>r.querySelectorAll('nav a').length),sources:roots.map(r=>r.querySelectorAll('details a').length),
                          overflow:document.documentElement.scrollWidth-innerWidth,links,
                          cta:roots.map(r=>r.querySelectorAll('[data-fv-r339-cta=editorial]').length),
                          errors:[...document.querySelectorAll('[aria-labelledby]')].some(e=>!document.getElementById(e.getAttribute('aria-labelledby')))};
                    }""")
                    assert data['roots'] == 2 and data['events'] == [6,6] and data['navs'] == [6,6] and data['sources'] == [6,6] and data['cta'] == [1,1], data
                    assert data['idsUnique'] and not data['errors'] and data['overflow'] <= 1, data
                    assert all(a['height'] >= 43.5 and a['left'] >= -1 and a['right'] <= width+1 for a in data['links']), data
                    root = page.locator('[data-fv-r339]').first
                    item = root.locator('details').first
                    item.locator('summary').focus(); page.keyboard.press('Enter')
                    assert item.evaluate('(e)=>e.open'), 'keyboard source drawer failed'
                    root.locator('nav a').nth(3).click()
                    assert page.evaluate("location.hash.includes('-event-4')"), 'native chronological navigation failed'
                    assert root.locator('a[data-fv-r339-cta=editorial]').get_attribute('href') == FREE
                    if width in (320,390,1440) and not contrast and root_px == 16:
                        page.evaluate('window.scrollTo(0,0)')
                        name = f'r339-{width}-'+('js' if js else 'nojs')+'.png'
                        page.screenshot(path=str(OUT/name), full_page=False)
                        screenshots.append(name)
                    perf=page.evaluate('window.__r339Perf || {lcpMs:null,cls:null}')
                    cases.append({'width':width,'js':js,'rootFontPx':root_px,'forcedColors':contrast,'reducedMotion':motion,'horizontalOverflowPx':data['overflow'],'fixtureLCPms':perf.get('lcpMs'),'fixtureCLS':perf.get('cls'),'result':'PASS'})
                    print('PASS',width,js,root_px,contrast, flush=True)
                finally: page.close()
        finally: browser.close()
    receipts={'classification':'Real local Chromium on exact isolated R339 PHP-rendered fixture, NOT installed WP, axe-core, non-Chromium or field CWV',
              'sourceGitBlobs':{'chronology-rail.php':digest(MODULE),'assets/chronology-rail.css':digest(CSS),'qa/chronology_gate.py':digest(Path(__file__))},
              'negativeControlsRejected':len(bad),'cases':cases,'screenshots':screenshots,'release':'HARD HOLD'}
    (OUT/'r339-browser-receipt.json').write_text(json.dumps(receipts, indent=2)+'\n')
    print('R339 PASS', len(cases), 'real Chromium contexts; 6 deliberate corruption cases rejected. Not live.')

if __name__ == '__main__': main()
