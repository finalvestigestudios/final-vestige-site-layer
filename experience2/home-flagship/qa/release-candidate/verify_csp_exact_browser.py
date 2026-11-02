#!/usr/bin/env python3
"""Strict offline Chromium CSP and interaction check on exact Git HEAD.

set_content + CSP meta is not a WordPress HTTP-header, cookies, iframe,
media-licensing, Safari, WCAG, Lighthouse/CWV or production release test.
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

CSS = ("flagship.css","chronicle.css","chronicle-lens.css","inquiry.css","observer-lab.css","reading-trail.css")
JS = ("flagship.js","observer-lab.js","chronicle-lens.js","reading-trail.js")
CHAPTERS = ("fv-hf-title","fv-hf-chronicle","fv-hf-evidence","fv-hf-inquiry",
            "fv-hf-method-title","fv-hf-observer","fv-hf-mind-title")
WIDTHS = (320,360,390,768,1024,1440,1920)
NONCE = "FVStaticNonceForOfflineBrowserQANotForDeployment"

def assemble(root):
    index=(root/"index.html").read_bytes()
    html=index.decode("utf-8")
    digest={"index.html":hashlib.sha256(index).hexdigest()}
    if "DO NOT DEPLOY AS THE WORDPRESS HOME PAGE" not in html or "data-fv-home-flagship" not in html:
        raise ValueError("Not the unpublished canonical index")
    if html.count("</body>")!=1:raise ValueError("Body delimiter must be unique")
    for name in CSS:
        b=(root/name).read_bytes();s=b.decode("utf-8")
        digest[name]=hashlib.sha256(b).hexdigest()
        tag='<link rel="stylesheet" href="./'+name+'">'
        if html.count(tag)!=1 or "</style" in s.lower():raise ValueError("Unsafe CSS "+name)
        html=html.replace(tag,'<style nonce="'+NONCE+'" data-ex2-style="'+name+'">'+s+"</style>")
    script_tail=""
    for name in JS:
        b=(root/name).read_bytes();s=b.decode("utf-8")
        digest[name]=hashlib.sha256(b).hexdigest()
        tag='<script src="./'+name+'" defer></script>'
        if html.count(tag)!=1 or "</script" in s.lower():raise ValueError("Unsafe JavaScript "+name)
        html=html.replace(tag,"")
        script_tail+='<script nonce="'+NONCE+'" data-ex2-script="'+name+'">'+s+"</script>"
    html=html.replace("</body>",script_tail+"</body>")
    if 'href="./' in html or 'src="./' in html:raise ValueError("Unbundled asset")
    csp=("default-src 'none'; script-src 'nonce-"+NONCE+"'; "
         "style-src 'nonce-"+NONCE+"' 'unsafe-inline'; "
         "img-src https://finalvestige.com https://i0.wp.com data:; "
         "connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'")
    html=html.replace("<head>",'<head><meta http-equiv="Content-Security-Policy" content="'+csp+'">',1)
    return html,digest

def check_clean(root,expected):
    if not re.fullmatch(r"[a-f0-9]{40}",expected or ""):
        raise ValueError("Missing exact expected Git HEAD SHA")
    repo=root.resolve().parents[1]
    actual=subprocess.check_output(["git","rev-parse","HEAD"],cwd=repo,text=True).strip()
    if actual!=expected:raise ValueError("Wrong checkout "+actual)
    tracked=["experience2/home-flagship/"+n for n in ("index.html",*CSS,*JS)]
    dirty=subprocess.check_output(["git","status","--porcelain","--untracked-files=no","--",*tracked],cwd=repo,text=True).strip()
    if dirty:raise ValueError("Canonical source dirty; cannot attest exact checkout")

def run_browser(html,output,chromium):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True,exist_ok=True)
    tests=[]
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=chromium,args=["--no-sandbox"])
        for width in WIDTHS:
            ctx=browser.new_context(viewport={"width":width,"height":900},reduced_motion="reduce")
            page=ctx.new_page();page.route("**/*",lambda route:route.abort())
            issues=[]
            page.on("pageerror",lambda error:issues.append(str(error)))
            page.on("console",lambda m:issues.append(m.text) if "Content Security Policy" in m.text or "Refused to" in m.text else None)
            page.set_content(html,wait_until="domcontentloaded");page.wait_for_timeout(65)
            assert page.locator("h1").count()==1
            assert all(page.locator("#"+c).count()==1 for c in CHAPTERS)
            assert page.locator("style[data-ex2-style]").count()==6
            assert page.locator("script[data-ex2-script]").count()==4
            assert page.locator(".fv-hf__studio-controls").is_visible()
            assert page.locator("[data-fv-case-buttons]").is_visible()
            assert page.locator("[data-fv-chronicle-lens]").is_visible()
            assert page.locator("[data-fv-observer-controls]").is_visible()
            assert not page.evaluate("document.documentElement.scrollWidth > innerWidth")
            assert not issues,issues
            page.locator('[data-fv-direction-choice="museum"]').click()
            assert page.locator("[data-fv-home-flagship]").get_attribute("data-fv-direction")=="museum"
            page.locator('[data-fv-case-button="franklin"]').click()
            assert page.locator('[data-fv-case="franklin"]').is_visible()
            assert not page.locator('[data-fv-case="apollo"]').is_visible()
            page.locator('[data-fv-chronicle-view="addition"]').click()
            assert page.locator(".fv-hf__chronicle").get_attribute("data-fv-chronicle-mode")=="addition"
            page.locator('[data-fv-observer-switch="b"]').click()
            assert page.locator('[data-fv-observer-frame="b"]').is_visible()
            assert not page.locator('[data-fv-observer-frame="a"]').is_visible()
            if width in (390,1440):page.screenshot(path=str(output/("exact-offline-"+str(width)+".png")),full_page=True)
            tests.append({"width":width,"pass":True,"interaction_checks":4,"csp_errors":0,"overflow":False})
            ctx.close()
        ctx=browser.new_context(java_script_enabled=False,viewport={"width":390,"height":844})
        page=ctx.new_page();page.route("**/*",lambda route:route.abort());page.set_content(html)
        assert page.locator("[data-fv-case]:visible").count()==3
        assert page.locator("[data-fv-observer-frame]:visible").count()==2
        assert not page.locator(".fv-hf__studio-controls").is_visible()
        assert not page.locator("[data-fv-case-buttons]").is_visible()
        assert not page.locator("[data-fv-chronicle-lens]").is_visible()
        assert not page.locator("[data-fv-observer-controls]").is_visible()
        tests.append({"negative":"no_js","pass":True,"historic_evidence_visible":True})
        ctx.close()
        # CSP must reject a script that lacks the nonce while leaving valid scripts active.
        tampered=html.replace("</body>","<script>window.FV_HACK=1</script></body>")
        ctx=browser.new_context();page=ctx.new_page();page.route("**/*",lambda route:route.abort())
        violations=[]
        page.on("console",lambda m:violations.append(m.text) if "Content Security Policy" in m.text or "Refused to" in m.text else None)
        page.set_content(tampered);page.wait_for_timeout(65)
        assert page.evaluate("window.FV_HACK !== 1")
        assert page.locator(".fv-hf__studio-controls").is_visible()
        assert violations
        tests.append({"negative":"unapproved_inline_script","pass":True,"blocked":True})
        ctx.close()
        swapped=html.replace('nonce="'+NONCE+'" data-ex2-script="flagship.js"',
                             'nonce="wrong" data-ex2-script="flagship.js"',1)
        assert swapped!=html
        ctx=browser.new_context();page=ctx.new_page();page.route("**/*",lambda route:route.abort())
        page.set_content(swapped);page.wait_for_timeout(65)
        assert not page.locator(".fv-hf__studio-controls").is_visible()
        assert page.locator("[data-fv-case]:visible").count()==3
        tests.append({"negative":"bad_flagship_nonce","pass":True,"evidence_fails_open":True})
        ctx.close();browser.close()
    return tests

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,required=True)
    parser.add_argument("--expected-head",required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--chromium",default=os.getenv("CHROMIUM_PATH","/usr/bin/chromium"))
    args=parser.parse_args()
    try:
        check_clean(args.root,args.expected_head)
        html,digest=assemble(args.root)
        tests=run_browser(html,args.output,args.chromium)
        report={"exact_head":args.expected_head,"source_sha256":digest,"chromium_source":"local executable",
                "tests":tests,"release":"HOLD",
                "scope":"Exact checkout in-memory Chromium with CSP meta; external assets deliberately blocked",
                "still_required":["real WordPress staging HTTP/CSP/cookies/iframe","loaded archival media/rights",
                "axe/WCAG/manual screen reader/Safari","field performance and Lighthouse","hosted CI and QD"]}
        (args.output/"offline-csp-browser-results.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({"pass":True,"head":args.expected_head,"checks":len(tests),"release":"HOLD"}))
    except Exception as error:
        print("FAIL CLOSED: "+repr(error),file=sys.stderr)
        raise SystemExit(2)

if __name__=="__main__":main()
