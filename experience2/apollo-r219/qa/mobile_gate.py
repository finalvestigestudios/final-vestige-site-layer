#!/usr/bin/env python3
"""R219: deterministic viewport-correct, no-JavaScript Apollo staging browser gate.
Only exercises PHP-generated fixtures. Not installed WordPress or field Core Web Vitals.
"""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

BLOB = "769b574c14a37220d522e37ceaea01044630e3e7"
PARENT = "a7546ae18c7970183c003ddcc4ac1bbc13f14cb87933982e6113a8792bec0128"
BUILT = "90fb65624990bd8b8f7c4184b0e74c2b51ad6004e7643ebc5b0740b5305c6e72"
FREE = "https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"
WIDTHS = (320, 360, 390, 600, 768, 1024, 1440, 1920)

def hash256(b): return hashlib.sha256(b).hexdigest()
def blob(b): return hashlib.sha1(b"blob " + str(len(b)).encode() + b"\0" + b).hexdigest()
def ensure(ok, msg):
    if not ok: raise AssertionError(msg)

def php(dist, mode):
    return json.loads(subprocess.check_output(["php", str(dist/"wp-render-shim-r217.php"),
        str(dist/"fv-ex2-apollo-r217.php"), mode], text=True))

def run(workspace, output):
    output.mkdir(parents=True, exist_ok=True)
    r216 = workspace/"apollo-r216"
    r217 = workspace/"apollo-r217"
    ensure(blob((r217/"build_r217.py").read_bytes()) == BLOB, "GitHub R217 builder mismatch")
    ensure(hash256((r216/"dist/manifest.json").read_bytes()) == PARENT, "R216 input mismatch")
    subprocess.run(["python",str(r217/"build_r217.py")],check=True)
    dist=r217/"dist"
    ensure(hash256((dist/"manifest.json").read_bytes())==BUILT,"Exact-source output differs")
    manifest=json.loads((dist/"manifest.json").read_text())
    for file,digest in manifest["files"].items():
        ensure(hash256((dist/file).read_bytes())==digest,"File drift "+file)
    for gate in ("commercial_release_allowed","creator_attribution_verified",
                 "approved_purchase_offer","axe_core_accepted","upstream_R198_reconciled"):
        ensure(manifest[gate] is False,"Unsafe release switch "+gate)
    subprocess.run(["php","-l",str(dist/"fv-ex2-apollo-r217.php")],
                   check=True,capture_output=True)
    normal=php(dist,"normal")
    ensure(not normal["fallback"] and not normal["js"] and FREE in normal["html"],"PHP render")
    ensure(php(dist,"late")["fallback"] and php(dist,"printed")["css"]=="done",
           "PHP late fail-open / print")
    css=(dist/"assets/atlas-scoped.css").read_text()
    # The WP shortcode is a fragment. Use a complete document WITH viewport meta.
    page_html=('<html lang="en"><head><meta name="viewport" '
        'content="width=device-width, initial-scale=1"><style>'+css+
        '</style></head><body>'+normal["html"]+'</body></html>')
    results=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path="/usr/bin/chromium",
                                   args=["--no-sandbox"])
        for width in WIDTHS:
            for js_enabled in (False,True):
                mobile=width<=390
                context=browser.new_context(viewport={"width":width,"height":844},
                    is_mobile=mobile,has_touch=mobile,device_scale_factor=1,
                    java_script_enabled=js_enabled,reduced_motion="reduce")
                page=context.new_page()
                faults=[]
                page.on("pageerror",lambda error:faults.append(str(error)))
                page.set_content(page_html,wait_until="domcontentloaded")
                page.evaluate("document.fonts.ready")
                metrics=None
                if js_enabled:
                    metrics=page.evaluate("""() => new Promise(resolve => {
                      let lcp=null,cls=0;
                      const a=new PerformanceObserver(list=>{for(const e of list.getEntries())lcp=e.startTime});
                      const b=new PerformanceObserver(list=>{for(const e of list.getEntries())
                        if(!e.hadRecentInput)cls+=e.value});
                      a.observe({type:'largest-contentful-paint',buffered:true});
                      b.observe({type:'layout-shift',buffered:true});
                      setTimeout(()=>{a.disconnect();b.disconnect();resolve({lcp_ms:lcp,cls:cls})},180);
                    })""")
                measured=page.evaluate("""() => ({
                   width:innerWidth,scroll:document.documentElement.scrollWidth,
                   ids:[...document.querySelectorAll('[id]')].map(x=>x.id),
                   missing:[...document.querySelectorAll('[aria-controls],[aria-labelledby],[aria-describedby]')]
                     .flatMap(x=>['aria-controls','aria-labelledby','aria-describedby']
                       .flatMap(k=>(x.getAttribute(k)||'').split(/\\s+/)
                         .filter(Boolean).filter(v=>!document.getElementById(v)))),
                   ctas:[...document.querySelectorAll('a.cta')].map(x=>({
                     url:x.href,height:x.getBoundingClientRect().height,width:x.getBoundingClientRect().width})),
                   active:document.querySelectorAll('script,iframe,form,object,embed').length
                 })""")
                ensure(measured["width"]==width and measured["scroll"]<=width+2,
                       "Mobile layout/overflow: "+str((width,js_enabled,measured)))
                ensure(len(set(measured["ids"]))==len(measured["ids"]) and not measured["missing"],
                       "Broken ARIA/duplicate IDs")
                ensure(measured["active"]==0 and len(measured["ctas"])==1 and
                       measured["ctas"][0]["url"]==FREE,"Unapproved active content/CTA")
                ensure(measured["ctas"][0]["width"]>=44 and measured["ctas"][0]["height"]>=44,
                       "Touch target under 44px")
                summary=page.locator("details summary").first
                summary.focus()
                page.keyboard.press("Enter")
                ensure(page.locator("details").first.get_attribute("open") is not None,
                       "Keyboard disclosure failed")
                summary.click()
                ensure(page.locator("details").first.get_attribute("open") is None,
                       "Touch/pointer disclosure failed")
                answer=page.locator(".fv-apollo-lesson-key > div").first
                ensure(answer.count()==1 and not faults,"Lesson/console error")
                page.emulate_media(media="print")
                height=answer.evaluate("el=>el.getBoundingClientRect().height")
                ensure(height>0,"Printed source-based answers hidden")
                page.emulate_media(media="screen")
                name=f"{width}-{'js' if js_enabled else 'nojs'}.png"
                screenshot=output/name
                page.screenshot(path=str(screenshot),full_page=True,animations="disabled")
                results.append({"width":width,"javascript":js_enabled,
                  "sha256":hash256(screenshot.read_bytes()),"no_overflow":True,
                  "print_answers_visible":True,"fixture_metrics":metrics})
                context.close()
        browser.close()
    ensure(len(results)==16,"Incomplete browser matrix")
    ensure(results[2]["sha256"]!=results[4]["sha256"],
           "360 and 390 mobile screenshots incorrectly identical")
    receipt={"status":"STAGING_HOLD","exact_r217_builder_git_blob":BLOB,
       "exact_r217_manifest_sha256":BUILT,"r216_manifest_sha256":PARENT,
       "browser_contexts":16,"true_mobile_viewport":True,
       "js_disabled_contexts":8,"lcp_cls":"LOCAL FRAGMENT FIXTURE ONLY",
       "axe_core":"NOT TESTED","installed_wordpress":"NOT TESTED",
       "r198_chain":"NOT RECONCILED","merchant_orders":"NOT VERIFIED",
       "net_revenue_per_1000_qualified_sessions":"NOT COMPUTABLE",
       "grok_published_asset":"NOT VERIFIED","production_writes":False,
       "results":results}
    (output/"receipt.json").write_text(json.dumps(receipt,sort_keys=True,indent=2)+"\n")
    print("R219 PASS: 16 true-viewport browser contexts / 8 genuine no-JS contexts")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--workspace",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    run(a.workspace.resolve(),a.output.resolve())
