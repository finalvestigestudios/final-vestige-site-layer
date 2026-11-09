#!/usr/bin/env python3
"""Fail-closed EX2 archival-media loading admission; no production requests.

Usage:
 python verify_belowfold_media.py /path/to/experience2/home-flagship/index.html
 python verify_belowfold_media.py --browser-fixtures

Static audit is against tracked source. Browser fixtures demonstrate only Chromium's
native loading behavior with synthetic positions and mocked images, NOT actual FV CWV.
"""
import argparse
import json
from pathlib import Path
import re
import sys

PHOTO = 'https://finalvestige.com/wp-content/uploads/2026/08/s67-19766.webp'
FRANKLIN = 'https://finalvestige.com/wp-content/uploads/2026/08/Franklinexpeditionnote.jpg'
NYPL = 'edit-017-v02-nypl-5003296-original.jpg'

def validate(source: str):
    errors=[]
    tags = re.findall(r'<img\b[^>]*>', source, flags=re.I | re.S)
    apollo=[x for x in tags if PHOTO in x]
    franklin=[x for x in tags if FRANKLIN in x]
    nypl=[x for x in tags if NYPL in x]
    if not (len(tags)==3 and len(apollo)==1 and len(franklin)==1 and len(nypl)==1):
        errors.append('Expected exactly three intact, unique archival images')
    if source.count('id="fv-hf-evidence"')!=1 or not source.index('<main') < source.index('id="fv-hf-evidence"') < source.index(PHOTO):
        errors.append('Apollo is not provably below the opening and chronicle sections')
    if apollo:
        tag=apollo[0]
        if 'loading="lazy"' not in tag or 'fetchpriority="high"' in tag or 'loading="eager"' in tag:
            errors.append('Below-fold Apollo must be lazy and must not be high-priority')
        if not all(x in tag for x in ('width="1041"', 'height="810"','decoding="async"','data-fv-archive-img', 'alt="Apollo 1 astronauts')):
            errors.append('Apollo geometry, origin, textual fallback or accessibility attributes changed')
    for t in franklin+nypl:
        if 'loading="lazy"' not in t:
            errors.append('Other below-fold archive images lost lazy-loading')
        if 'alt="' not in t or 'width="' not in t or 'height="' not in t:
            errors.append('Archival media lost alt/geometry')
    for i in ['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title']:
        if f'href="#{i}"' not in source:
            errors.append('Broken no-JS chapter anchor '+i)
    if source.count('https://finalvestige.com/focus/')<1:
        errors.append('Missing existing Focus Fieldbook destination')
    if source.count('data-fv-home-flagship')<1:
        errors.append('Lost flagship root')
    return errors

def browser_fixtures():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError('Playwright unavailable: browser gate FAILS CLOSED') from exc
    import base64
    payload=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQEBAQDtFg7DAAAAAElFTkSuQmCC')
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
        try:
            for width in (320,390,1440):
                for js in (True,False):
                    for mode in ('eager','lazy'):
                        page=browser.new_page(viewport={'width':width,'height':780},java_script_enabled=js)
                        hits=[]
                        def serve(route):
                            hits.append(route.request.url)
                            route.fulfill(status=200,body=payload,content_type='image/png')
                        page.route('https://fv.test/archive.png',serve)
                        priority = ' fetchpriority="high"' if mode=='eager' else ''
                        html=f'<!doctype html><html><body><main><h1>Original evidence</h1><div style="height:6500px">Seven chapter study fixture — no remote content</div><img src="https://fv.test/archive.png" width="500" height="300" loading="{mode}"{priority} alt="Synthetic case image"></main></body></html>'
                        page.set_content(html,wait_until='load')
                        page.wait_for_timeout(400)
                        initial=len(hits)
                        page.locator('img').scroll_into_view_if_needed()
                        page.wait_for_timeout(300)
                        after=len(hits)
                        # Chromium deliberately does not defer lazy images with JS disabled.
                        expected_initial = 1 if (mode=='eager' or not js) else 0
                        ok=(initial==expected_initial) and after==1
                        results.append({'width':width,'javascript_enabled':js,'policy':mode,'initial_network_requests':initial,'after_scroll_requests':after,'pass':ok})
                        page.close()
        finally:browser.close()
    if not all(r['pass'] for r in results):
        raise AssertionError('Chromium image priority fixture failed: '+json.dumps(results))
    return results

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('html',nargs='?',type=Path)
    parser.add_argument('--browser-fixtures',action='store_true')
    args=parser.parse_args()
    receipt={'gate':'EX2_BELOW_FOLD_ARCHIVE_PRIORITY','source':'not_inspected','browser':'not_run','pass':False}
    if args.html:
        source=args.html.read_text(encoding='utf-8')
        errors=validate(source)
        receipt['source']={'file':str(args.html),'errors':errors,'pass':not errors}
        if errors:
            print(json.dumps(receipt,indent=2));return 2
    if args.browser_fixtures:
        receipt['browser']={'evidence_scope':'MOCKED fixture, not WordPress or field CWV','results':browser_fixtures()}
    receipt['pass']=(not args.html or receipt['source']['pass'])
    print(json.dumps(receipt,indent=2))
    return 0
if __name__=='__main__':sys.exit(main())
