#!/usr/bin/env python3
"""Apollo R218: reproduce *committed* R217 source, not the divergent local R217 reference.
STAGING ONLY; no WordPress installation, sales, or external post attribution.
Requires a separately staged, pinned R216 dist. Do not claim a canonical R198 ancestry.
"""
import hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
R217=ROOT/'apollo-r217'
R216=ROOT/'apollo-r216'
OUT=HERE.parent/'evidence'
HEAD='5d40d61149838eb3c36d0c8a5a15ba22e31c71da'
BUILDER_BLOB='769b574c14a37220d522e37ceaea01044630e3e7'
PARENT_SHA='a7546ae18c7970183c003ddcc4ac1bbc13f14cb87933982e6113a8792bec0128'
EXACT_SHA='90fb65624990bd8b8f7c4184b0e74c2b51ad6004e7643ebc5b0740b5305c6e72'
DIVERGENT_REFERENCE_SHA='b29e28a0413e8c05294111c078c876ba8cfd5ab5bbab7d7e31b0d6505643c486'
CTA='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
WIDTHS=(320,360,390,600,768,1024,1440,1920)
def sha(b):return hashlib.sha256(b).hexdigest()
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
def expect(x,m):
    if not x:raise AssertionError(m)
def cmd(*a):return subprocess.check_output(a,text=True,stderr=subprocess.STDOUT).strip()
def php(mode,dist):
    return json.loads(cmd('php',str(dist/'wp-render-shim-r217.php'),str(dist/'fv-ex2-apollo-r217.php'),mode))
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    expect(blob((R217/'build_r217.py').read_bytes())==BUILDER_BLOB,'Not byte-exact R217 GitHub builder')
    expect(sha((R216/'dist/manifest.json').read_bytes())==PARENT_SHA,'Unpinned R216 input')
    cmd('python',str(R217/'build_r217.py'))
    dist=R217/'dist'
    actual=sha((dist/'manifest.json').read_bytes())
    expect(actual==EXACT_SHA,'Exact GitHub builder output mismatch')
    manifest=json.loads((dist/'manifest.json').read_text())
    for name,expected in manifest['files'].items():
        expect(sha((dist/name).read_bytes())==expected,'Artifact altered: '+name)
    for field in ('creator_attribution_verified','approved_purchase_offer','media_commercial_rights_cleared',
                  'installed_WordPress_accepted','upstream_R198_reconciled','axe_core_accepted','commercial_release_allowed'):
        expect(manifest[field] is False,'Unsafe release switch: '+field)
    expect(cmd('php','-l',str(dist/'fv-ex2-apollo-r217.php')).startswith('No syntax errors'),'PHP syntax')
    normal=php('normal',dist)
    expect(normal['fallback'] is False and normal['js'] is False and CTA in normal['html'],'Free Atlas unavailable')
    expect(php('late',dist)['fallback'] is True,'Missing-CSS fail-open broken')
    expect(php('printed',dist)['css']=='done','Print CSS unregistered')
    helper=php('tamper-helper',dist)
    expect(helper.get('valid_original') and helper.get('tamper_rejected'),'Same-byte helper defective')
    with tempfile.TemporaryDirectory() as scratch:
        altered=Path(scratch)/'dist';shutil.copytree(dist,altered)
        for name in ('source-url-crosswalk.json','custody-ledger.json','commercial-offer-gate.json'):
            path=altered/name;original=path.read_bytes();path.write_bytes(original+b' ')
            expect(php('normal',altered)['fallback'] is True,'Tampered '+name+' accepted')
            path.write_bytes(original)
    html=normal['html']
    css=(dist/'assets/atlas-scoped.css').read_text()
    screenshots=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        for width in WIDTHS:
            small=width<=390
            context=browser.new_context(viewport={'width':width,'height':850},
                device_scale_factor=1,is_mobile=small,has_touch=small,reduced_motion='reduce')
            page=context.new_page()
            page.set_content(html,wait_until='domcontentloaded')
            page.add_style_tag(content=css)
            geom=page.evaluate("""() => ({
              scroll:document.documentElement.scrollWidth,view:innerWidth,
              ids:[...document.querySelectorAll('[id]')].map(x=>x.id),
              missing:[...document.querySelectorAll('[aria-controls],[aria-labelledby]')].flatMap(x=>
                ['aria-controls','aria-labelledby'].flatMap(k=>(x.getAttribute(k)||'').split(/\\s+/)
                  .filter(Boolean).filter(id=>!document.getElementById(id)))),
              actions:[...document.querySelectorAll('a.cta')].map(x=>x.href),
              active:document.querySelectorAll('script,iframe,form').length})""")
            expect(geom['scroll']<=geom['view']+2,'Horizontal overflow: '+str(width))
            expect(len(geom['ids'])==len(set(geom['ids'])) and not geom['missing'],'Broken IDs/ARIA')
            expect(geom['actions']==[CTA] and geom['active']==0,'Unexpected CTA or active content')
            details=page.locator('details')
            if details.count():
                summary=details.first.locator('summary')
                summary.focus();page.keyboard.press('Enter')
                expect(details.first.get_attribute('open') is not None,'Keyboard disclosure failed')
                summary.click()
                expect(details.first.get_attribute('open') is None,'Disclosure close failed')
            screenshot=OUT/(str(width)+'.png')
            page.screenshot(path=str(screenshot),full_page=True,animations='disabled')
            screenshots.append({'viewport':width,'sha256':sha(screenshot.read_bytes()),'overflow':False,
                'one_free_CTA':True,'keyboard_disclosure':True,'tap_browser_context':small})
            context.close()
        browser.close()
    receipt={'status':'STAGING_HOLD','r217_github_head':HEAD,'exact_builder_blob':BUILDER_BLOB,
      'parent_r216_manifest_sha256':PARENT_SHA,'exact_r217_manifest_sha256':actual,
      'older_reference_manifest_sha256':DIVERGENT_REFERENCE_SHA,
      'older_reference_was_exact_head':False,'screenshots':screenshots,
      'axe_core':'NOT TESTED','javascript_disabled_browser':'NOT TESTED',
      'installed_wordpress':'NOT TESTED','r198_source_chain':'NOT RECONCILED',
      'lcp_cls_production':'NOT MEASURED','grok_asset_id':'NOT VERIFIED',
      'paid_sku':'NOT VERIFIED','orders_and_net_revenue':'NOT COMPUTABLE',
      'no_live_writes':True}
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print('R218 EXACT R217 BUILDER PASS',HEAD,actual,len(screenshots),'widths')
if __name__=='__main__':main()
