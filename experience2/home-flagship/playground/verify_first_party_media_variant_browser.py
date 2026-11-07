#!/usr/bin/env python3
"""Read-only Chromium media-source selection audit on pinned WordPress Playground Blueprints.

Measures selected URL hostname ONLY. Routes abort deliberately, so response bytes, actual
network, first-party infrastructure, WordPress integration and Lighthouse remain UNTESTED.
Requires Playwright and a Chromium executable.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from make_first_party_media_variant import derive, git_blob, BASE_BLOB, VARIANT_BLOB

WIDTHS = [320,360,390,768,1440,1920]
ASSETS = {
    "s67-19766.webp": (1041,810),
    "Franklinexpeditionnote.jpg": (960,1526),
}

def extract(data):
    plugin = data['steps'][2]['data']
    markup = re.search(r"return <<<'FVPG_HTML_END'\n(.*?)\nFVPG_HTML_END;",plugin,re.S)
    css = re.search(r"<<<'FVPG_CSS_END'\n(.*?)\nFVPG_CSS_END",plugin,re.S)
    if not markup or not css: raise ValueError('Exact PHP payload missing')
    return markup.group(1),css.group(1)

def verify_image_source(page, first_party):
    selected = page.locator('img[data-fv-archive-img]').evaluate_all(
        '(imgs)=>imgs.map(x=>({src:x.src,currentSrc:x.currentSrc,srcset:x.getAttribute("srcset"),width:x.getAttribute("width"),height:x.getAttribute("height"),alt:x.alt}))'
    )
    if len(selected) != 2: raise AssertionError('Missing archival evidence images')
    for im in selected:
        url=im['currentSrc'] or im['src']
        host=urlparse(url).hostname
        expect='finalvestige.com' if first_party else 'i0.wp.com'
        if host!=expect: raise AssertionError(f'Expected {expect}, got {host}: {url}')
        name=urlparse(im['src']).path.split('/')[-1]
        if name not in ASSETS: raise AssertionError('Unexpected evidence image')
        if (int(im['width']),int(im['height']))!=ASSETS[name]:raise AssertionError('Image dimensions changed')
        if not im['alt']: raise AssertionError('Missing evidence image alt')
        if first_party and im['srcset'] is not None:raise AssertionError('Non-origin source candidates remain')
    return [x['currentSrc'] for x in selected]

def run(path):
    original=Path(path).read_bytes()
    if git_blob(original)!=BASE_BLOB: raise ValueError('Wrong exact parent source')
    variant=derive(original)
    if git_blob(variant)!=VARIANT_BLOB: raise AssertionError('Unexpected derived source')
    original_html,original_css=extract(json.loads(original))
    changed_html,changed_css=extract(json.loads(variant))
    if original_css!=changed_css: raise AssertionError('CSS changed')
    if original_html.count('/focus/')!=changed_html.count('/focus/'):raise AssertionError('Focus path changed')
    for marker in ('fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method','fv-hf-observer','fv-hf-mind'):
        if marker not in changed_html:raise AssertionError('Chapter marker lost: '+marker)
    first_party_receipts=[]
    with sync_playwright() as p:
        executable='/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None
        browser=p.chromium.launch(headless=True,executable_path=executable, args=['--no-sandbox'] if executable else [])
        for js in (True,False):
            for dpr in (1,2):
                for width in WIDTHS:
                    ctx=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=dpr,java_script_enabled=js,reduced_motion='reduce')
                    page=ctx.new_page()
                    requests=[]
                    def block(route):
                        requests.append(route.request.url)
                        route.abort()
                    page.route('**/*',block)
                    page.set_content('<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+changed_css+'</style></head><body>'+changed_html+'</body></html>',wait_until='domcontentloaded')
                    for img in page.locator('img[data-fv-archive-img]').all():
                        img.scroll_into_view_if_needed(timeout=10000)
                    chosen=verify_image_source(page,True)
                    first_party_receipts.append({'width':width,'dpr':dpr,'js':js,'browser_selected_urls':chosen,'requests_observed':requests[:6]})
                    ctx.close()
        # Independent negative control: CURRENT parent selects WordPress image CDN.
        ctx=browser.new_context(viewport={'width':390,'height':900},device_scale_factor=2,java_script_enabled=False)
        page=ctx.new_page()
        page.route('**/*',lambda route:route.abort())
        page.set_content('<!doctype html><html><head><style>'+original_css+'</style></head><body>'+original_html+'</body></html>',wait_until='domcontentloaded')
        for img in page.locator('img[data-fv-archive-img]').all():img.scroll_into_view_if_needed()
        cdn=verify_image_source(page,False)
        ctx.close()
        browser.close()
    return {'status':'PASS_SELECTED_URLS_ONLY','scenarios':len(first_party_receipts),
        'origin_image_selections':len(first_party_receipts)*2,'negative_control_cdn':cdn,
        'parent_blob':BASE_BLOB,'derived_blob':VARIANT_BLOB,'real_network_bytes':'NOT_TESTED',
        'wordpress_assembler':'NOT_TESTED','lighthouse_cwv':'NOT_TESTED','wcag':'NOT_TESTED',
        'release_decision':'HOLD','results':first_party_receipts}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('canonical');parser.add_argument('--output')
    args=parser.parse_args()
    try:
        result=run(args.canonical)
    except Exception as ex:
        print('RELEASE HOLD / TEST FAILURE:',ex,file=sys.stderr)
        sys.exit(2)
    if args.output:Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))
