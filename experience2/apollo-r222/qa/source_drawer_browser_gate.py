#!/usr/bin/env python3
"""Exact-source R222 native SourceDrawer Playwright acceptance; fixture not WordPress staging.

No internet, telemetry, merchant action, production write, or external asset requests.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, subprocess, shutil
from pathlib import Path
from playwright.sync_api import sync_playwright

FREE='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
MANIFEST='a4fc40dc270684686a879183a7e417bfb6e1d05a40e4e819fed603dc45d130a5'
WIDTHS=(320,360,390,768,1024,1440,1920)
NASA=('Apollo 204 Review Board','S66-58038','S67-15717','S67-21294')

def sha(buf):return hashlib.sha256(buf).hexdigest()
def check(v,msg):
    if not v:raise AssertionError(msg)

def assert_browser(page,record):
    result=page.evaluate('''() => {
       const root=document.querySelector('.fv-apollo-atlas');
       const d=root?.querySelector('#fv-apollo-source-drawer');
       const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
       const links=[...root.querySelectorAll('a[href]')];
       const missing=links.filter(a=>a.getAttribute('href').startsWith('#') && !document.getElementById(a.getAttribute('href').slice(1))).map(a=>a.outerHTML);
       const broken=[...root.querySelectorAll('[aria-describedby],[aria-labelledby],[aria-controls]')].flatMap(e => ['aria-describedby','aria-labelledby','aria-controls'].flatMap(a=>(e.getAttribute(a)||'').split(/\s+/).filter(Boolean).filter(id=>!document.getElementById(id))));
       const source=[...d?.querySelectorAll('[data-drawer-source]')||[]].map(e=>({id:e.getAttribute('data-drawer-source'),url:e.querySelector('a')?.href,lim:e.querySelector('[id]')?.textContent||''}));
       const cta=[...root.querySelectorAll('a.cta')].map(e=>({href:e.href,w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height,display:getComputedStyle(e).display}));
       return {d:!!d,open:d?.open,source,cta,ids,broken,missing,
          overflow:document.documentElement.scrollWidth>innerWidth+2,
          scripts:root.querySelectorAll('script,form,iframe,embed,object,canvas').length,
          geo:root.querySelectorAll('[data-lat],[data-lon],[data-longitude],.map-pin').length,
          print:root.querySelectorAll('.fv-apollo-print-custody li').length};
    }''')
    check(result['d'],'Drawer missing')
    check(not result['open'],'Drawer should start collapsed but remain operable without JS')
    check(len(result['ids'])==len(set(result['ids'])),'Duplicate element IDs')
    check(not result['broken'] and not result['missing'],'Broken accessible reference / link')
    check(len(result['source'])==4,'Source Drawer must have 4 source types')
    check(set(x['id'] for x in result['source'])==set(NASA),'Wrong sources')
    expected={x['id']:x['url'] for x in record['sources']}
    check(all(x['url']==expected[x['id']] and x['lim'].startswith('Limit:') for x in result['source']),
      'NASA custody record drift or missing visible uncertainty label')
    check(len(result['cta'])==1 and result['cta'][0]['href']==FREE,'Original reading CTA drift or duplicate')
    check(result['cta'][0]['w']>=44 and result['cta'][0]['h']>=44 and result['cta'][0]['display']!='none','CTA touch/accessibility sizing')
    check(not result['scripts'] and not result['geo'],'Active content or map coordinates')
    check(not result['overflow'],'Horizontal overflow')
    check(result['print']>=4,'Existing print-only NASA source list missing')
    return result

def negative_cases(page, doc, records):
    target=records['sources'][2]['url']
    probes={
       'forged_nasa_destination':(target,'https://www.nasa.gov/image-detail/amf-s66-58038/'),
       'fake_purchasable_offer':(FREE,'https://vendor.example/pay-now'),
       'phantom_map_pin':('<aside class="fv-apollo-reading-bridge"','<span data-lat="0" data-lon="0"></span><aside class="fv-apollo-reading-bridge"'),
       'embedded_script':('<aside class="fv-apollo-reading-bridge"','<script>window.X=42</script><aside class="fv-apollo-reading-bridge"'),
       'duplicate_source_identifier':('</body>','<div id="fv-apollo-source-drawer"></div></body>'),
       'hidden_cta':('<style>','<style>.fv-apollo-atlas .cta{display:none!important}'),
       'broken_limit_reference':('aria-describedby="fv-apollo-drawer-limit-s66-58038"','aria-describedby="forged-missing"'),
       'unapproved_campaign_query':(FREE,FREE+'?utm_content=unknown-asset'),
    }
    errors=[]
    for label,(old,new) in probes.items():
        check(old in doc,'Mutation target missing '+label)
        page.set_content(doc.replace(old,new,1),wait_until='domcontentloaded')
        try:assert_browser(page,records)
        except AssertionError:errors.append(label)
    check(len(errors)==len(probes),'Failed to detect negative controls: '+str(set(probes)-set(errors)))
    return errors

def run(parent, script, out):
    out.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('r222',script)
    build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
    generated=out/'generated'
    manifest=build.build(parent,generated)
    check(manifest==MANIFEST,'R222 manifest SHA drift')
    data=json.loads((generated/'source-drawer-records.json').read_text())
    for name,pin in json.loads((generated/'manifest.json').read_text())['files'].items():
        check(sha((generated/name).read_bytes())==pin,'R222 file checksum mismatch '+name)
    sh=['php',str(generated/'wp-render-shim-r222.php'),str(generated/'fv-ex2-apollo-r222.php')]
    variants={mode:json.loads(subprocess.check_output(sh+[mode],text=True)) for mode in ('normal','printed','late')}
    check(not variants['normal']['fallback'],'R222 PHP failed normal render')
    check('fv-apollo-source-drawer' in variants['normal']['html'],'Drawer not present in PHP output')
    check(not variants['normal']['js'],'Unexpected JS injected')
    check(not variants['printed']['fallback'] and 'fv-apollo-source-drawer' in variants['printed']['html'],'Print missing')
    check(variants['late']['fallback'] and FREE in variants['late']['html'],'Late-load safe fallback missing')
    # Explicit source custody mutation must trigger fail-open to original investigation, not unknown citations.
    tamper=generated/'source-drawer-records.json'; original=tamper.read_bytes()
    try:
        tamper.write_bytes(original+b'\n')
        f=json.loads(subprocess.check_output(sh+['normal'],text=True))
        check(f['fallback'] and FREE in f['html'],'Record tamper did not trigger safe PHP fallback')
    finally: tamper.write_bytes(original)
    css=(generated/'assets/atlas-scoped.css').read_text()
    doc='<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+variants['normal']['html']+'</body></html>'
    result=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (False,True):
                touch=width<=390
                ctx=browser.new_context(viewport={'width':width,'height':844},is_mobile=touch,
                     has_touch=touch,java_script_enabled=js,device_scale_factor=1, reduced_motion='reduce')
                page=ctx.new_page();js_errors=[];page.on('pageerror',lambda e:js_errors.append(str(e)))
                # No page network and no telemetry: only PHP-rendered local source.
                page.set_content(doc,wait_until='domcontentloaded');page.evaluate('document.fonts.ready')
                page.evaluate('''() => { window.__fvPerf={lcp:[],cls:[]};
                  new PerformanceObserver(list => {for(const e of list.getEntries())window.__fvPerf.lcp.push(e.startTime)}).observe({type:'largest-contentful-paint',buffered:true});
                  new PerformanceObserver(list => {for(const e of list.getEntries())window.__fvPerf.cls.push({value:e.value,hadRecentInput:e.hadRecentInput})}).observe({type:'layout-shift',buffered:true});
                }''')
                page.wait_for_timeout(140)
                audit=assert_browser(page,data)
                summary=page.locator('#fv-apollo-source-drawer summary')
                summary.scroll_into_view_if_needed()
                if touch:
                    box=summary.bounding_box();check(bool(box),'Summary not visible on mobile')
                    page.touchscreen.tap(box['x']+min(box['width']/2,90),box['y']+box['height']/2)
                else:
                    summary.focus();page.keyboard.press('Enter')
                check(page.locator('#fv-apollo-source-drawer').evaluate('e=>e.open'),'Native source drawer failed touch/keyboard')
                check(page.locator('#fv-apollo-source-drawer a').first.is_visible(),'Source link not visible after opening')
                check(not js_errors,'Browser JS errors')
                page.emulate_media(media='print')
                check(page.locator('.fv-apollo-print-custody li').first.evaluate('e=>e.getBoundingClientRect().height')>0,
                      'Source custody absent in print')
                page.emulate_media(media='screen', reduced_motion='reduce')
                screenshot=out/f'{width}-{"js" if js else "nojs"}-drawer.png'
                page.screenshot(path=str(screenshot),animations='disabled')
                # Locally observed browser fixture entries are not field Core Web Vitals.
                perf=page.evaluate('''() => ({lcp:window.__fvPerf.lcp, layoutShift:window.__fvPerf.cls})''')
                result.append({'width':width,'js':js,'native_drawer_opened':True,'print_sources':True,
                    'reduced_motion':True,'screenshot_sha256':sha(screenshot.read_bytes()),
                    'LCP_fixture_samples_ms':perf['lcp'], 'CLS_fixture_entries':perf['layoutShift']})
                ctx.close()
        ctx=browser.new_context(viewport={'width':390,'height':844},java_script_enabled=False)
        page=ctx.new_page();cases=negative_cases(page,doc,data);ctx.close()
        for settings in [{'forced_colors':'active'}, {'reduced_motion':'reduce'}]:
            ctx=browser.new_context(viewport={'width':390,'height':844},**settings)
            page=ctx.new_page();page.set_content(doc)
            audit=assert_browser(page,data)
            sm=page.locator('#fv-apollo-source-drawer summary');sm.focus();page.keyboard.press('Enter')
            check(page.locator('#fv-apollo-source-drawer').evaluate('e=>e.open'),'A11y context disclosure failed')
            ctx.close()
        browser.close()
    receipt={'status':'STAGING_HOLD','R222_manifest_sha256':manifest,'browser_engine':'system Chromium / Python Playwright',
        'tested_exact_local_source':True,'wordpress_staging':'NOT_TESTED','axe_core':'NOT_EXECUTED',
        'NVDA_VoiceOver':'NOT_TESTED','hosted_ci':'NOT_CHECKED','external_urls':'NOT_NAVIGATED',
        'published_grok_apollo_asset':'NOT_VERIFIED','paid_orders':'NOT_VERIFIED',
        'conversion_attribution':'NOT_COMPUTABLE','LCP_CLS':'LOCAL FIXTURE ONLY; NO FIELD PERFORMANCE',
        'contexts':len(result),'adversarial_rejections':cases,'results':result,'production_writes':False}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('R222 PASS:',len(result),'browser contexts,',len(cases),'negative controls; manifest',manifest)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--parent',required=True,type=Path);ap.add_argument('--builder',required=True,type=Path);ap.add_argument('--out',required=True,type=Path)
    a=ap.parse_args();run(a.parent,a.builder,a.out)
