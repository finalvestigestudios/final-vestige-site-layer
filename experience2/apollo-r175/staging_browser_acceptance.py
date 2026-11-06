"""R175 reproducible Chromium gate. Default uses the exact R174 GitHub HTML.

--fixture only allows offline illustrative fixtures. Neither mode represents an
installed WordPress acceptance test. Optional --axe-js needs genuine axe-core.
"""
import argparse
import hashlib
import json
from pathlib import Path
from playwright.sync_api import sync_playwright
from verified_catalog_label import rewrite,blob

WIDTHS=(320,360,390,768,1440,1920)

def check(source:Path,out:Path,fixture=False,axe_js=None):
    raw=source.read_text(encoding='utf-8')
    content,audit=rewrite(raw,expected_blob=blob(raw) if fixture else 'b23879150024b3b667679ff4dd7faae1e37cfc07')
    css=Path(__file__).with_name('verified_catalog_label.css').read_text()
    if '</style>' in content:
        content=content.replace('</style>',css+'</style>',1)
    else:
        # Actual PR #158 shortcode CSS and JS, exercised without WordPress.
        desk=Path(__file__).resolve().parents[1]/'research-desk'/'assets'
        base_css=(desk/'source-ledger.css').read_text()
        base_js=(desk/'source-ledger.js').read_text()
        r174_css=(Path(__file__).resolve().parents[1]/'apollo-r174'/'nasa_media_custody.css').read_text()
        content='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>R175 staging-only lab</title><style>'+base_css+r174_css+css+'</style><body>'+content+'<script>'+base_js+'</script></body></html>'
    out.mkdir(parents=True,exist_ok=True)
    (out/'R175_BROWSER_FIXTURE_NOT_INSTALLED.html').write_text(content)
    paths=[];errors=[];results=[];axe_results=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            ctx=browser.new_context(viewport={'width':width,'height':900},device_scale_factor=1,reduced_motion='reduce' if width==390 else 'no-preference')
            page=ctx.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
            page.evaluate('''window.__r175p={lcp:0,cls:0};
              new PerformanceObserver(l=>{for(const e of l.getEntries()) window.__r175p.lcp=Math.max(window.__r175p.lcp,e.startTime)}).observe({type:'largest-contentful-paint',buffered:true});
              new PerformanceObserver(l=>{for(const e of l.getEntries()) if(!e.hadRecentInput) window.__r175p.cls+=e.value}).observe({type:'layout-shift',buffered:true});''')
            page.set_content(content,wait_until='load');page.wait_for_timeout(250)
            assert page.locator('[data-fvx-r175-catalog-review="unverified"]').count()==1
            assert 'Not verified' in page.locator('[data-fvx-r175-catalog-review]').inner_text()
            assert page.locator('[data-fvx-r174-media-custody]').count()==6
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
            assert page.locator('a[href="https://www.nasa.gov/image-detail/apollo-1-crew-honored/"]').count()==1
            assert page.locator('a[href="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"]').count()==1
            inp=page.locator('input[data-fvx-search]');assert inp.is_visible()
            inp.fill('record 01' if fixture else 'S67-19766')
            assert page.locator('[data-fvx-record]:visible').count()==1
            inp.fill('');assert page.locator('[data-fvx-record]:visible').count()==6
            if axe_js:
                page.add_script_tag(path=str(axe_js))
                res=page.evaluate('''async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}});return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))}}''')
                axe_results.append({'width':width,**res})
            metrics=page.evaluate('window.__r175p')
            p=out/f'chromium-{width}.png';page.screenshot(path=str(p),full_page=True,animations='disabled');paths.append(p)
            results.append({'width':width,'fixture_only':True,'lab_lcp_ms':metrics['lcp'],'lab_cls':metrics['cls']})
            ctx.close()
        c=browser.new_context(viewport={'width':390,'height':844},java_script_enabled=False)
        page=c.new_page();page.set_content(content)
        assert page.locator('[data-fvx-r175-catalog-review]').count()==1
        assert page.locator('[data-fvx-record]:visible').count()==6
        assert page.locator('[data-fvx-tools]').is_hidden()
        c.close()
        c=browser.new_context(viewport={'width':390,'height':844},has_touch=True,forced_colors='active',reduced_motion='reduce')
        page=c.new_page();page.set_content(content)
        assert page.locator('.fv-ex2-catalog-warning').is_visible()
        page.locator('article[data-fvx-record] details summary').first.tap()
        assert page.locator('article[data-fvx-record] details').first.get_attribute('open') is not None
        c.close();browser.close()
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    record={'source_blob':audit['base_blob'],'fixture_mode':fixture,'viewport_results':results,'screenshots':hashes,'page_errors':errors,'axe':axe_results if axe_js else 'NOT_EXECUTED_AXE_CORE_NOT_PROVIDED','installed_WordPress':'NOT_TESTED','production_LCP_CLS':'NOT_MEASURED','source_links_added':audit['links_added']}
    assert not errors
    if axe_js: assert not any(item['violations'] for item in axe_results),'WCAG axe violations present'
    (out/'acceptance.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    return record

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('source',type=Path)
    p.add_argument('output',type=Path)
    p.add_argument('--fixture',action='store_true')
    p.add_argument('--axe-js',type=Path)
    a=p.parse_args();r=check(a.source,a.output,fixture=a.fixture,axe_js=a.axe_js)
    print(json.dumps({'widths':[x['width'] for x in r['viewport_results']],'errors':r['page_errors'],'axe':r['axe'],'fixture_mode':r['fixture_mode']}))
