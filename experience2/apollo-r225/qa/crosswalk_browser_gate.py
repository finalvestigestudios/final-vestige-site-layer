#!/usr/bin/env python3
"""Exact-source R225 staging QA: crosswalk, PHP fallbacks, Chromium; not WP or axe."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
from playwright.sync_api import sync_playwright

WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok, msg):
    if not ok: raise AssertionError(msg)

def run(parent, builder, output):
    output.mkdir(parents=True, exist_ok=True)
    spec = importlib.util.spec_from_file_location('build_r225', builder)
    build = importlib.util.module_from_spec(spec); spec.loader.exec_module(build)
    dist = output / 'dist'
    receipt = build.build(parent, dist)
    manifest = json.loads((dist / 'manifest.json').read_text())
    for rel, digest in manifest['files'].items():
        require(sha(dist / rel) == digest, 'unverified dist: ' + rel)
    require(receipt['reconciled_counts']['external_links'] == 56, 'anchor census')
    require(receipt['reconciled_counts']['source_bindings'] == 6, 'source IDs')
    require(receipt['reconciled_counts']['chronology_dates'][-1] == '1967-04', 'report month')
    php = dist / 'fv-ex2-apollo-r224.php'
    require('No syntax errors' in subprocess.check_output(['php','-l',str(php)],text=True),'PHP lint')
    shim = ['php',str(dist/'wp-render-shim-r224.php'),str(php)]
    render = {mode: json.loads(subprocess.check_output(shim+[mode],text=True)) for mode in ('normal','printed','late')}
    require(not render['normal']['fallback'] and not render['printed']['fallback'] and render['late']['fallback'],'PHP fallback regression')
    require(FREE in render['late']['html'] and not render['normal']['js'],'free fallback and zero JS')
    crosswalk = dist / 'source-url-crosswalk.json'
    original = crosswalk.read_bytes()
    try:
        crosswalk.write_bytes(original+b' ')
        tampered=json.loads(subprocess.check_output(shim+['normal'],text=True))
        require(tampered['fallback'] and FREE in tampered['html'],'render custody mutation not rejected')
    finally:
        crosswalk.write_bytes(original)
    baseline = (parent / 'templates/atlas-fragment.html').read_text()
    dangerous = {
       'forged NASA source': ('https://www.nasa.gov/apollo-1-resources/', 'https://www.nasa.gov.evil.example/apollo-1-resources/'),
       'new commercial URL': (FREE, 'https://unreviewed-checkout.example/'),
       'unsupported precise day': ('<li data-evidence-kind="retrospective-report"><time datetime="1967-04"', '<li data-evidence-kind="retrospective-report"><time datetime="1967-04-19"'),
       'invented map coordinates': ('id="fv-apollo-chronology"','id="fv-apollo-chronology" data-lat="38.1"'),
       'active script': ('</section>', '<script>window.injected=1</script></section>'),
    }
    rejects=[]
    for label,(before,after) in dangerous.items():
        require(before in baseline, 'fixture mutation missing marker: '+label)
        if label=='active script': mutant=baseline.replace(before,after,1)
        else: mutant=baseline.replace(before,after,1)
        sample = build.AtlasHTML();sample.feed(mutant)
        reasons=[]
        if sample.forbidden: reasons.append('unsafe-element')
        if sample.dates != build.EXPECTED_DATES: reasons.append('date-drift')
        if set(sample.links) != set(json.loads((parent/'source-url-crosswalk.json').read_text())['external_urls']): reasons.append('link-drift')
        if sum(h==FREE for h in sample.links)!=1: reasons.append('CTA-drift')
        require(bool(reasons),'mutation slipped through semantic census: '+label)
        rejects.append({'mutation':label,'detected_by':reasons})
    css=(dist/'assets/atlas-scoped.css').read_text()
    doc='<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>'+css+'</style></head><body>'+render['normal']['html']+'</body></html>'
    screenshots=[]; metrics=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            for javascript in (False, True):
                ctx=browser.new_context(viewport={'width':width,'height':850},java_script_enabled=javascript,is_mobile=width<=390,has_touch=width<=390,reduced_motion='reduce')
                page=ctx.new_page();page.set_content(doc,wait_until='domcontentloaded')
                state=page.evaluate(`\x60() => { const root=document.querySelector('.fv-apollo-atlas'); const anchors=[...root.querySelectorAll('a[href^="http"]')];const bound=[...root.querySelectorAll('a[data-source-id]')];const ids=[...root.querySelectorAll('[id]')].map(e=>e.id);return {count:anchors.length,bound:bound.length,urls:new Set(anchors.map(a=>a.href)).size,dates:[...root.querySelectorAll('#fv-apollo-chronology ol.rail time')].map(t=>t.getAttribute('datetime')),brokenIds:ids.length!==new Set(ids).size,overflow:document.documentElement.scrollWidth>innerWidth+2,cta:[...root.querySelectorAll('a.cta')].map(a=>a.href),scripts:root.querySelectorAll('script,iframe,form').length}}\x60`)
                require(state['count']==56 and state['bound']==6 and state['urls']==11, 'DOM source census at '+str(width))
                require(state['dates']==build.EXPECTED_DATES,'rendered chronology drift')
                require(not state['brokenIds'] and not state['overflow'] and state['scripts']==0, 'a11y or active markup')
                require(state['cta']==[FREE], 'CTA changed')
                details=page.locator('#fv-apollo-source-drawer summary');details.scroll_into_view_if_needed()
                if width<=390:
                    box=details.bounding_box();page.touchscreen.tap(box['x']+15,box['y']+box['height']/2)
                else: details.focus();page.keyboard.press('Enter')
                require(page.locator('#fv-apollo-source-drawer').evaluate('el=>el.open'),'native no-JS/touch disclosure')
                page.locator('#fv-apollo-chronology').scroll_into_view_if_needed()
                screenshot=output / (str(width) + ('-js' if javascript else '-nojs') + '.png')
                page.screenshot(path=str(screenshot),animations='disabled')
                screenshots.append({'width':width,'javascript':javascript,'sha256':sha(screenshot)})
                metrics.append({'width':width,'javascript':javascript,'cls_observed':None,'lcp_observed_ms':None,
                                'reason':'Page.set_content fixture; no field or HTTP origin measurement'})
                ctx.close()
        special=browser.new_context(viewport={'width':390,'height':850},forced_colors='active',reduced_motion='reduce')
        page=special.new_page();page.set_content(doc)
        require(page.locator('#fv-apollo-source-drawer summary').is_visible(),'forced colors hide drawer')
        special.close();browser.close()
    report={'status':'LOCAL_PASS_STAGING_HOLD','generated_manifest_sha256':sha(dist/'manifest.json'),
            'crosswalk_sha256':sha(crosswalk),'responsive_contexts':len(screenshots),
            'screenshots':screenshots,'semantic_mutations':rejects,'performance':metrics,
            'genuine_axe':'NOT_EXECUTED','wordPress':'NOT_TESTED','localhost':'ERR_BLOCKED_BY_ADMINISTRATOR',
            'screen_readers':'NOT_TESTED','realized_revenue':'NOT_COMPUTABLE','live':False}
    (output/'qa-receipt.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    return report

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--parent',type=Path,required=True);a.add_argument('--builder',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    z=a.parse_args();r=run(z.parent,z.builder,z.out);print('R225 QA PASS',r['responsive_contexts'],'contexts, 5 mutations, manifest',r['generated_manifest_sha256'])
