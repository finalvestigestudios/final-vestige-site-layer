#!/usr/bin/env python3
"""Integrated *real Chromium* QA for an Experience 2.0 source checkout.

Read-only. External network is deliberately disabled; media failure reveals
textual fallback. Reports local lab metrics separately from real-user CWV.
Requires: pip-installed playwright and installed Chromium; standard CI should
run it against the exact PR commit, NOT an isolated component fixture.
"""
from __future__ import annotations
import argparse
import json
import hashlib
import os
from pathlib import Path
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

WIDTHS=(320,360,390,600,768,1024,1440,1920)
CHAPTERS=["fv-hf-title", "fv-hf-chronicle", "fv-hf-evidence", "fv-hf-inquiry", "fv-hf-method-title", "fv-hf-observer", "fv-hf-mind-title"]
CASE_IDS=("apollo","franklin","malbone")


def run(root:Path, out:Path, chromium_path: str|None=None):
    from check_contract import scan
    static_checks,static_observations,static_errors=scan(root)
    if static_errors:
        raise RuntimeError("Source contract FAILED; refusing to present browser results: "+"; ".join(static_errors))
    out.mkdir(parents=True,exist_ok=True)
    report={"scope":"complete unpublished index.html + byte-exact local CSS/JS, inlined only for sandbox browser transport; deliberately blocked external media", "time_utc":datetime.now(timezone.utc).isoformat(),"git_head_expected_sha":"SET_BY_CALLER", "source_hashes":static_observations["asset_sha256"],"external_requests_allowed":False,"viewport_results":[],"no_js_results":[],"zoom_results":[],"checks":{},"failures":[],"limits":["Not public WordPress/theme integration or production visitor data", "Synthetic browser timing only, not field p75 Core Web Vitals", "Not WCAG 2.2 AA certification: manual screen-reader/axe/Safari validation still needed", "Media deliberately blocked; appearance of remote archive photographs and rights not validated", "CSS and JS are inlined into a throwaway browser document because file:// is sandbox-blocked; WordPress/real-URL asset routing remains untested"]}
    failures=report["failures"]
    def ck(key,condition,context=""):
        report["checks"][key]=bool(condition)
        if not condition:failures.append({"check":key,"context":context})
    with sync_playwright() as p:
        kwargs={"headless":True}
        if chromium_path:kwargs["executable_path"]=chromium_path
        browser=p.chromium.launch(**kwargs)
        # Chromium in our offline execution sandbox blocks file:// navigation.
        # Inline the EXACT checked-out asset bytes into a throwaway document,
        # preserving CSS order and defer-script execution *after* the document.
        # The repository files remain unchanged; this does not validate HTTP asset routing.
        from check_contract import STYLES,SCRIPTS
        original=(root/"index.html").read_text(encoding="utf-8")
        doc=original
        for name in STYLES:
            needle=f'<link rel="stylesheet" href="./{name}">'
            if doc.count(needle)!=1:raise RuntimeError("Missing/duplicate CSS link: "+name)
            doc=doc.replace(needle,"<style data-fv-inline-test-asset=\""+name+"\">\n"+(root/name).read_text(encoding="utf-8")+"\n</style>",1)
        for name in SCRIPTS:
            needle=f'<script src="./{name}" defer></script>'
            if doc.count(needle)!=1:raise RuntimeError("Missing/duplicate deferred script: "+name)
            doc=doc.replace(needle,"",1)
        scripts='\n'.join('<script data-fv-inline-test-asset="'+name+'">\n'+(root/name).read_text(encoding="utf-8")+'\n</script>' for name in SCRIPTS)
        if '</body>' not in doc:raise RuntimeError('No closing body tag')
        doc=doc.replace('</body>',scripts+'\n</body>',1)
        report["browser_transport"]="file source exact bytes, CSS+JS inlined for Chromium set_content only; paths not HTTP-loaded"
        for width in WIDTHS:
            context=browser.new_context(viewport={"width":width,"height":900},reduced_motion="reduce" if width==390 else "no-preference")
            page=context.new_page()
            errors=[];blocked=[]
            page.on("pageerror",lambda error: errors.append(str(error)))
            page.route("**/*",lambda route: route.continue_() if route.request.url.startswith("file:") or route.request.url.startswith("data:") else (blocked.append(route.request.url),route.abort())[1])
            page.set_content(doc,wait_until="load",timeout=20000)
            page.wait_for_timeout(220)
            measurements=page.evaluate("""() => ({
              rootOverflow:document.documentElement.scrollWidth-innerWidth,
              bodyOverflow:document.body.scrollWidth-innerWidth,
              navVisible:(()=>{const n=document.querySelector('.fv-hf__nav');return !!n && getComputedStyle(n).display!=='none' && n.getBoundingClientRect().height>0})(),
              headings:[...document.querySelectorAll('h1')].map(x=>x.textContent.trim()),
              connectedStyles:[...document.styleSheets].length,
              enhanced:document.querySelector('.fv-hf')?.classList.contains('fv-hf--enhanced'),
              caseControls:[...document.querySelectorAll('[data-fv-case-button]')].map(x=>({id:x.dataset.fvCaseButton,visible:x.getBoundingClientRect().height>0,height:x.getBoundingClientRect().height})),
              evidenceVisible:[...document.querySelectorAll('[data-fv-case]')].filter(x=>!!x.getBoundingClientRect().height).length,
              lensMode:document.querySelector('.fv-hf__chronicle')?.getAttribute('data-fv-chronicle-mode'),
              lensVisible:!!document.querySelector('[data-fv-chronicle-lens]') && !document.querySelector('[data-fv-chronicle-lens]').hidden,
              observerFrames:[...document.querySelectorAll('[data-fv-observer-frame]')].filter(x=>!!x.getBoundingClientRect().height).length,
              reducedMotion:matchMedia('(prefers-reduced-motion: reduce)').matches,
              resources:performance.getEntriesByType('resource').filter(r=>r.name.startsWith('file:')).map(r=>({name:r.name.split('/').pop(),transferSize:r.transferSize,duration:r.duration})),
              navigation:performance.getEntriesByType('navigation').map(r=>({domContentLoaded:r.domContentLoadedEventEnd,load:r.loadEventEnd})),
              imageFailures:[...document.querySelectorAll('[data-fv-archive-img]')].filter(i=>i.naturalWidth===0).length
            })""")
            result={"width":width,"measurements":measurements,"page_errors":errors,"remote_media_requests_blocked":len(blocked)}
            report["viewport_results"].append(result)
            ck(f"width_{width}_no_horizontal_overflow",measurements["rootOverflow"]<=1 and measurements["bodyOverflow"]<=1,str(measurements))
            ck(f"width_{width}_nav_visible",measurements["navVisible"])
            ck(f"width_{width}_three_css_enhanced_cases",measurements["enhanced"] and measurements["evidenceVisible"]==1)
            ck(f"width_{width}_observer_enhanced",measurements["observerFrames"]==1)
            ck(f"width_{width}_chronicle_lens",measurements["lensMode"]=="both" and measurements["lensVisible"])
            ck(f"width_{width}_no_exceptions",not errors,str(errors))
            ck(f"width_{width}_all_styles_present",measurements["connectedStyles"]>=5)
            for key in CHAPTERS:
                ck(f"width_{width}_chapter_{key}",page.locator("#"+key).count()==1)
            # Genuine user actions on the combined page; no isolated fixture substitutions.
            page.locator('[data-fv-case-button="franklin"]').click()
            ck(f"width_{width}_franklin_selected",page.locator('[data-fv-case-button="franklin"]').get_attribute('aria-pressed')=="true" and page.locator('[data-fv-case="franklin"]').is_visible())
            page.locator('[data-fv-case-button="franklin"]').focus()
            page.keyboard.press('ArrowRight')
            ck(f"width_{width}_arrow_switches_to_malbone",page.locator('[data-fv-case-button="malbone"]').get_attribute('aria-pressed')=="true" and page.locator('[data-fv-case="malbone"]').is_visible())
            page.locator('[data-fv-chronicle-view="original"]').click()
            ck(f"width_{width}_original_selected",page.locator('.fv-hf__chronicle').get_attribute('data-fv-chronicle-mode')=="original" and page.locator('.fv-hf__chronicle-entry--first').is_visible() and not page.locator('.fv-hf__chronicle-entry--second').is_visible())
            page.locator('[data-fv-chronicle-view="addition"]').click()
            ck(f"width_{width}_addition_selected",page.locator('.fv-hf__chronicle').get_attribute('data-fv-chronicle-mode')=="addition" and not page.locator('.fv-hf__chronicle-entry--first').is_visible() and page.locator('.fv-hf__chronicle-entry--second').is_visible())
            page.locator('[data-fv-chronicle-view="both"]').click()
            ck(f"width_{width}_both_return",page.locator('.fv-hf__chronicle').get_attribute('data-fv-chronicle-mode')=="both" and page.locator('.fv-hf__chronicle-entry--first').is_visible() and page.locator('.fv-hf__chronicle-entry--second').is_visible())
            page.locator('[data-fv-observer-switch="b"]').click()
            ck(f"width_{width}_observer_b",page.locator('[data-fv-observer-switch="b"]').get_attribute('aria-pressed')=="true" and page.locator('[data-fv-observer-frame="b"]').is_visible() and not page.locator('[data-fv-observer-frame="a"]').is_visible())
            page.locator('[data-fv-direction-choice="museum"]').click()
            ck(f"width_{width}_museum_direction",page.locator('[data-fv-home-flagship]').get_attribute('data-fv-direction')=="museum")
            if width in (390,1440):
                page.screenshot(path=str(out/f"complete-home-{width}-enhanced.png"),full_page=True,animations="disabled")
            context.close()
        for width in (390,1440):
            context=browser.new_context(viewport={"width":width,"height":880},java_script_enabled=False,reduced_motion="reduce")
            page=context.new_page();errors=[]
            page.on("pageerror",lambda e:errors.append(str(e)))
            page.route("**/*",lambda route:route.continue_() if route.request.url.startswith("file:") or route.request.url.startswith("data:") else route.abort())
            page.set_content(doc,wait_until="load")
            counts={"case_visible":page.locator('[data-fv-case]:visible').count(),"observer_frames_visible":page.locator('[data-fv-observer-frame]:visible').count(),"lens_controls_visible":page.locator('[data-fv-chronicle-lens]:visible').count(),"original_visible":page.locator('.fv-hf__chronicle-entry--first').is_visible(),"addition_visible":page.locator('.fv-hf__chronicle-entry--second').is_visible(),"natural_details":page.locator('details').count(),"root_overflow":page.evaluate('document.documentElement.scrollWidth-innerWidth')}
            report["no_js_results"].append({"width":width,**counts})
            ck(f"nojs_{width}_all_evidence_visible",counts["case_visible"]==3 and counts["observer_frames_visible"]==2 and counts["original_visible"] and counts["addition_visible"])
            ck(f"nojs_{width}_no_dead_lens_controls",counts["lens_controls_visible"]==0)
            ck(f"nojs_{width}_native_source_disclosures",counts["natural_details"]>=6)
            ck(f"nojs_{width}_no_overflow",counts["root_overflow"]<=1)
            first=page.locator('details').first
            first.locator('summary').click()
            ck(f"nojs_{width}_disclosure_works",first.get_attribute('open') is not None)
            if width==390:page.screenshot(path=str(out/"complete-home-390-nojs.png"),full_page=True)
            context.close()
        context=browser.new_context(viewport={"width":390,"height":900},device_scale_factor=1)
        page=context.new_page();page.route("**/*",lambda route:route.continue_() if route.request.url.startswith("file:") or route.request.url.startswith("data:") else route.abort())
        page.set_content(doc,wait_until="load")
        page.evaluate("document.documentElement.style.zoom='2'")
        zoom={"inner_width":page.evaluate('innerWidth'),"html_client_width":page.evaluate('document.documentElement.clientWidth'),"root_overflow":page.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')}
        report["zoom_results"].append(zoom)
        # CSS zoom is a supplementary reflow observation, not conformance proof.
        ck("zoom_200_no_horizontal_overflow",zoom["root_overflow"]<=1,str(zoom))
        page.screenshot(path=str(out/"complete-home-390-zoom200.png"),full_page=True)
        context.close();browser.close()
    report["passed"]=not failures;report["check_count"]=len(report["checks"]);report["pass_count"]=sum(report["checks"].values())
    (out/"FULL_HOME_BROWSER_RESULTS.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"passed":report["passed"],"checks":report["check_count"],"passed_checks":report["pass_count"],"failures":failures[:12],"results":str(out/"FULL_HOME_BROWSER_RESULTS.json")},indent=2))
    if failures:raise SystemExit(1)

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2]);parser.add_argument("--out",type=Path,default=Path("qa/integration/results"));parser.add_argument("--chromium",default=None);args=parser.parse_args();run(args.root,args.out,args.chromium)
