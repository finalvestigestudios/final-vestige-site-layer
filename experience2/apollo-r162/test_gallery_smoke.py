#!/usr/bin/env python3
"""Source-pinned Chromium smoke checks for R162; offline fixture, NOT live WP QA."""
import base64, hashlib, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent
WIDTHS=(320,360,390,768,1440,1920)
EXPECTED='c814d0ce743a6f49caf16c66218702d9272d8b370ba965dc36b61a3b56df56df'
PNG=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9W3Bp8AAAAAASUVORK5CYII=')
HTML=(ROOT/'live_gallery_fragment.html').read_text()
JS=(ROOT/'gallery-fallback.js').read_text()
CSS=(ROOT/'gallery-fallback.css').read_text()
assert hashlib.sha256(HTML.encode()).hexdigest()==EXPECTED

def page_html():
    return ('<!doctype html><html lang="en"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<style>*{box-sizing:border-box}body{margin:0;background:#12110e;color:#f5f0e7;font:16px/1.6 system-ui}'
        'main{margin:auto;max-width:60rem;padding:1rem}figure{margin:0}.fvx-chrono-gallery__image{display:block;width:100%;height:auto;max-height:26rem;object-fit:contain}'
        'a{color:#f4cc82}[hidden]{display:none!important}'+CSS+'</style><main>'+HTML.replace('loading="lazy"','loading="eager"')+
        '<p><a href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/">Read original investigation</a></p></main><script>'+JS+'</script></html>')

def run(dest):
    dest=Path(dest);dest.mkdir(parents=True,exist_ok=False)
    checks=[];screens=[]
    def test(w,name,v):checks.append({'width':w,'check':name,'pass':bool(v)})
    def intercept(route):
        if 's67-15717.jpg' in route.request.url:route.abort('failed')
        else:route.fulfill(status=200,body=PNG,content_type='image/png')
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for w in WIDTHS:
            ctx=browser.new_context(viewport={'width':w,'height':820},reduced_motion='reduce',has_touch=w==390)
            p=ctx.new_page();p.route('**/wp-content/uploads/2026/11/*.jpg',intercept)
            p.set_content(page_html(),wait_until='load')
            p.wait_for_function("document.querySelectorAll('[data-fvx-image-fallback]').length===1")
            test(w,'three_source_figures',p.locator('[data-fvx-chrono-photo]').count()==3)
            test(w,'three_nasa_links',p.locator('figcaption a[href^="https://www.nasa.gov/"],figcaption a[href^="https://images.nasa.gov/"]').count()==3)
            test(w,'exactly_one_error',p.locator('[data-fvx-image-fallback]').count()==1)
            test(w,'missing_image_caption_and_source_survive',p.locator('[data-fvx-chrono-photo="1"] figcaption a').count()==1)
            test(w,'error_message_accessible',p.locator('[data-fvx-image-fallback]').get_attribute('role')=='status')
            test(w,'no_horizontal_overflow',p.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
            test(w,'original_investigation_cta',p.locator('a[href*="the-hatch-opened-inward-apollo-1"]').count()==1)
            test(w,'no_injected_commerce',p.locator('a[href*="awin"],a[href*="payhip"],form').count()==0)
            shot=dest/f'gallery-smoke-{w}.png';p.screenshot(path=str(shot),full_page=True,animations='disabled')
            screens.append({'name':shot.name,'sha256':hashlib.sha256(shot.read_bytes()).hexdigest()})
            ctx.close()
            nj=browser.new_context(viewport={'width':w,'height':820},java_script_enabled=False)
            q=nj.new_page();q.route('**/wp-content/uploads/2026/11/*.jpg',intercept);q.set_content(page_html(),wait_until='load')
            test(w,'no_js_all_three_sources',q.locator('figcaption a[href^="https://www.nasa.gov/"],figcaption a[href^="https://images.nasa.gov/"]').count()==3)
            test(w,'no_js_no_misleading_status',q.locator('[data-fvx-image-fallback]').count()==0)
            nj.close()
        browser.close()
    report={'passed':sum(x['pass'] for x in checks),'total':len(checks),'checks':checks,'screenshots':screens,'scope':'offline Chrome exact WP fragment; NOT installed WordPress','axe':'NOT_EXECUTED','release':'STAGING_HOLD'}
    (dest/'receipt.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (dest/'SHA256SUMS').write_text(''.join(x['sha256']+'  '+x['name']+'\n' for x in screens))
    print(report['passed'],'/',report['total'])
    if report['passed']!=report['total']:sys.exit(1)

if __name__=='__main__':run(sys.argv[1])
