#!/usr/bin/env python3
"""R221 Apollo 1 staging gate: exact upstream source, no-JS interactions, pinch and custody.

This is NOT a browser-zoom, axe-core, WordPress, field CWV, or commerce acceptance test.
Requires Python Playwright, local Chromium and PHP.  No network, CMS, or telemetry writes.
"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

PARENT_GIT_BLOB = 'e948d6a273b3d565b2126a4bc4dc4d39c4c580d8'
R219_GIT_BLOB = '99e4ee33e69ddeee011b33b25ab6c54fef8c8e89'
R217_MANIFEST = '90fb65624990bd8b8f7c4184b0e74c2b51ad6004e7643ebc5b0740b5305c6e72'
FREE = 'https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
WIDTHS = (320, 390, 768, 1440, 1920)
SOURCE_IDS = {'S66-58038', 'S67-15717', 'S67-21294', 'Apollo 204 Review Board'}

def sha256(raw): return hashlib.sha256(raw).hexdigest()
def git_blob(raw): return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def require(check, message):
    if not check: raise AssertionError(message)

def audit_dom(page, crosswalk):
    """Assertions are intentionally based on actual browser-resolved DOM, not regex HTML."""
    audit=page.evaluate('''() => {
      const root=document.querySelector('.fv-apollo-atlas');
      if(!root) return {error:'missing-Atlas'};
      const links=[...root.querySelectorAll('a[href]')];
      const ids=[...document.querySelectorAll('[id]')].map(e=>e.id);
      const controls=[...document.querySelectorAll('[aria-labelledby],[aria-describedby],[aria-controls]')];
      const broken=controls.flatMap(e=>['aria-labelledby','aria-describedby','aria-controls']
        .flatMap(key=>(e.getAttribute(key)||'').split(/\\s+/).filter(Boolean)
        .filter(id=>!document.getElementById(id))));
      const missingAnchors=links.filter(a=>a.getAttribute('href').startsWith('#') &&
        !ids.includes(decodeURIComponent(a.getAttribute('href').slice(1)))).map(a=>a.outerHTML);
      const sourceBindings=[...root.querySelectorAll('[data-source-id]')].map(a=>
        ({source_id:a.dataset.sourceId,url:a.href}));
      const external=links.filter(a=>!a.getAttribute('href').startsWith('#')).map(a=>a.href);
      const headings=[...root.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h=>({
        level:Number(h.tagName[1]),name:h.textContent.trim()}));
      const ctas=[...root.querySelectorAll('a.cta')].map(a=>({href:a.href,
        label:a.textContent.trim(),w:a.getBoundingClientRect().width,h:a.getBoundingClientRect().height,
        display:getComputedStyle(a).display,visibility:getComputedStyle(a).visibility}));
      return {ids,broken,missingAnchors,sourceBindings,external,headings,ctas,
        scripts:root.querySelectorAll('script,iframe,form,object,embed,video,canvas').length,
        images: [...root.querySelectorAll('img')].map(x=>x.getAttribute('alt')),
        geo:root.querySelectorAll('[data-lat],[data-lon],[data-longitude],.map-pin').length,
        htmlOverflow:document.documentElement.scrollWidth>innerWidth+3,
        printkey:root.querySelectorAll('.fv-apollo-lesson-key > div').length};
    }''')
    require(not audit.get('error'), 'Atlas missing')
    require(len(audit['ids'])==len(set(audit['ids'])), 'Duplicate IDs')
    require(not audit['broken'] and not audit['missingAnchors'], 'Broken ARIA or internal anchors')
    require(audit['scripts']==0 and audit['geo']==0, 'Unapproved script/map/geo/active content')
    require(all(x is not None for x in audit['images']), 'Uncaptioned image without alt attribute')
    require(len(audit['ctas'])==1 and audit['ctas'][0]['href']==FREE,
            'CTA missing, retargeted, or duplicated')
    require(audit['ctas'][0]['w']>=44 and audit['ctas'][0]['h']>=44 and
            audit['ctas'][0]['display']!='none' and audit['ctas'][0]['visibility']=='visible',
            'CTA touch sizing or visibility')
    require(all(urlsplit(u).scheme=='https' and urlsplit(u).netloc in
        ('www.nasa.gov','finalvestige.com') and not urlsplit(u).query for u in audit['external']),
        'Unapproved outbound host or query attribution')
    require(FREE in audit['external'], 'Original investigation lost')
    require(set(x['source_id'] for x in audit['sourceBindings'])==SOURCE_IDS,
        'NASA catalog identifiers drifted')
    require(all(x in crosswalk['source_bindings'] for x in audit['sourceBindings']),
        'NASA source identifier/URL does not match pinned provenance')
    require(len([h for h in audit['headings'] if h['level']==1])==1 and
        all(h['name'] for h in audit['headings']), 'Heading/accessibility names absent')
    require(not audit['htmlOverflow'], 'Horizontal overflow detected')
    require(audit['printkey']>=1,'Educational answer guide removed')
    return audit

def test_mutations(page, html, crosswalk):
    """Prove that the browser-resolved security contract actually detects unsafe edits."""
    probes={
      'wrong_nasa_source':('https://www.nasa.gov/image-detail/amf-s67-15717/',
                           'https://www.nasa.gov/image-detail/amf-s66-58038/'),
      'foreign_checkout':(FREE,'https://attacker.example/checkout?ref=unverified'),
      'phantom_map_pin':('</article>','<div class="map-pin" data-lat="0" data-lon="0"></div></article>'),
      'active_script':('</article>','<script>alert(1)</script></article>'),
      'duplicate_id':('</body>','<div id="fv-apollo-main">forgery</div></body>'),
      'invisible_cta':('<style>','<style>.fv-apollo-atlas a.cta{display:none!important}'),
      'broken_anchor':('href="#fv-apollo-chronology"','href="#missing-chronology"'),
      'affiliating_query':(FREE,FREE+'?utm_content=unverified'),
    }
    flagged=[]
    for label,(a,b) in probes.items():
        require(a in html,'Negative-control target missing '+label)
        mutated=html.replace(a,b,1)
        page.set_content(mutated,wait_until='domcontentloaded')
        try:
            audit_dom(page,crosswalk)
        except AssertionError:
            flagged.append(label)
    require(len(flagged)==len(probes), f'Negative controls not rejected: {set(probes)-set(flagged)}')
    return flagged

def run(workspace,output,skip_parent=False):
    output.mkdir(parents=True,exist_ok=True)
    r220=workspace/'r220/qa/semantic_gate.py'
    r219=workspace/'r219/qa/mobile_gate.py'
    require(git_blob(r220.read_bytes())==PARENT_GIT_BLOB,'R220 GitHub source drift')
    require(git_blob(r219.read_bytes())==R219_GIT_BLOB,'R219 GitHub source drift')
    spec=importlib.util.spec_from_file_location('fv_r220',r220)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    if not skip_parent:
        module.run(workspace,output/'r220-regression')  # exact upstream 26 Chromium contexts.
    dist=workspace/'apollo-r217/dist'
    require(sha256((dist/'manifest.json').read_bytes())==R217_MANIFEST,
            'R217 generated source not pinned')
    rendered=json.loads(subprocess.check_output(['php',str(dist/'wp-render-shim-r217.php'),
        str(dist/'fv-ex2-apollo-r217.php'),'normal'],text=True))
    require(not rendered['fallback'] and not rendered['js'],'PHP fallback unexpected')
    crosswalk=json.loads((dist/'source-url-crosswalk.json').read_text())
    css=(dist/'assets/atlas-scoped.css').read_text()
    doc=('<html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<style>'+css+'</style></head><body>'+rendered['html']+'</body></html>')
    rows=[]
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            for js in (False,True):
                mobile=width<=390
                ctx=b.new_context(viewport={'width':width,'height':844},is_mobile=mobile,
                    has_touch=mobile,device_scale_factor=1,java_script_enabled=js)
                page=ctx.new_page();faults=[];page.on('pageerror',lambda e:faults.append(str(e)))
                page.set_content(doc,wait_until='domcontentloaded');page.evaluate('document.fonts.ready')
                audit=audit_dom(page,crosswalk)
                page.keyboard.press('Tab')
                require(page.evaluate('document.activeElement.getAttribute("href")')=='#fv-apollo-main',
                        'Skip link not first keyboard control')
                page.keyboard.press('Enter')
                require(page.evaluate('location.hash')=='#fv-apollo-main','Native skip failed')
                require(page.evaluate('document.activeElement.id')=='fv-apollo-main',
                        'Skip changed hash but not focus')
                page.keyboard.press('Tab')
                require(page.evaluate('document.activeElement.tagName')=='A',
                        'Tab after skip did not reach a link')
                summary=page.locator('details summary').first
                if mobile: summary.scroll_into_view_if_needed();page.touchscreen.tap(**{
                   'x':round(summary.bounding_box()['x']+15),
                   'y':round(summary.bounding_box()['y']+15)})
                else: summary.focus();page.keyboard.press('Enter')
                require(summary.evaluate('e=>e.parentElement.open'),
                        'Native disclosure not operable on keyboard/touch')
                # True browser pinch-scale via Chrome CDP. NOT Ctrl+Plus browser zoom.
                pinch=None
                if mobile:
                    cdp=ctx.new_cdp_session(page)
                    cdp.send('Emulation.setPageScaleFactor',{'pageScaleFactor':2})
                    pinch=page.evaluate('visualViewport.scale')
                    require(1.95<=pinch<=2.05,'CDP mobile pinch scale not applied')
                    cdp.send('Emulation.setPageScaleFactor',{'pageScaleFactor':1})
                page.emulate_media(media='print')
                require(page.locator('.fv-apollo-lesson-key > div').first.evaluate(
                    'e=>e.getBoundingClientRect().height')>0,'Print answer guide hidden')
                page.emulate_media(media='screen')
                page.locator('a.cta').scroll_into_view_if_needed()
                require(page.locator('a.cta').get_attribute('href')==FREE,
                        'Contextual free reading path changed')
                require(not faults,'Page errors '+str(faults))
                img=output/f'{width}-{("js" if js else "nojs")}-pinch.png'
                page.screenshot(path=str(img),full_page=False,animations='disabled')
                rows.append({'width':width,'javascript':js,'pinch_scale':pinch,
                  'single_free_cta':True,'skip_focus':True,'print_answers':True,
                  'external_link_count':len(audit['external']),'screenshot_sha256':sha256(img.read_bytes())})
                ctx.close()
        ctx=b.new_context(viewport={'width':390,'height':844},java_script_enabled=False)
        p2=ctx.new_page();negatives=test_mutations(p2,doc,crosswalk);ctx.close();b.close()
    require(len(rows)==10,'Incomplete R221 matrix')
    receipt={'status':'STAGING_HOLD','GitHub_R220_blob':PARENT_GIT_BLOB,
      'GitHub_R219_blob':R219_GIT_BLOB,'R217_manifest_sha256':R217_MANIFEST,
      'R220_regression_browser_contexts':(0 if skip_parent else 26),'R221_browser_contexts':len(rows),
      'R221_malformed_markup_rejected':negatives,'real_2x_mobile_pinch':True,
      'ctrl_plus_browser_zoom':'NOT TESTED','axe_core':'NOT EXECUTED; LOCAL LIBRARY UNAVAILABLE',
      'NVDA_VoiceOver':'NOT TESTED','WordPress_staging':'NOT TESTED',
      'LCP_CLS':'R219 LOCAL FRAGMENT FIXTURE ONLY; NOT FIELD METRICS',
      'R198_canonical_ancestry':'NOT RECONCILED','verified_payments':'NONE IN THIS TEST',
      'revenue_per_1000_qualified_sessions':'NOT COMPUTABLE','published_Grok_Apollo_asset':'UNVERIFIED',
      'production_writes':False,'results':rows}
    (output/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(f'R221 PASS: {len(rows)} browser contexts; {len(negatives)} negative controls; true 2x mobile pinch; exact upstream R220 PASS')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--workspace',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--skip-parent',action='store_true',help='Use separately saved exact R220 QA receipts; do not rerun upstream gate')
    a=parser.parse_args();run(a.workspace.resolve(),a.output.resolve(),a.skip_parent)
