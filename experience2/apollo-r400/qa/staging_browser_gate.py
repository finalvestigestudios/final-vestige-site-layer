#!/usr/bin/env python3
"""R400: read-only Apollo staging browser acceptance. Never permits release."""
import argparse, hashlib, json, re, sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from playwright.sync_api import sync_playwright

PRIMARY="https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/"
LATER="https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/"
FREE="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"
CSS={
 "/apollo-r384/assets/gallery.css":("r384-reviewed-1","4fe1595d790d22181c01038afd31c19e0839360458ded3c6098bd604d73035a9"),
 "/apollo-r395/assets/mobile-fit.css":("r395-reviewed-1","93da942bbfd37bd055c97150446a3124bc52d7b55b4e0ac968568343e5838756"),
}
CASES=[("320",320,False,False,False),("390-touch",390,True,False,False),("768",768,False,False,False),
       ("1440",1440,False,False,False),("1920",1920,False,False,False),
       ("320-nojs",320,False,True,False),("390-reduced",390,False,False,True)]

def safe_url(url, landing=False):
    if not isinstance(url,str) or len(url)>2048 or any(ord(c)<32 for c in url): return False
    if re.search(r'%(?:2e|2f|5c|00)',url,re.I): return False
    try: p=urlsplit(url)
    except ValueError: return False
    if p.scheme!="https" or not p.hostname or p.port is not None or p.username is not None or p.password is not None: return False
    if p.query or p.fragment or '\\' in url or '//' in p.path or '/../' in p.path or '/./' in p.path or p.path.endswith(('/..','/.')): return False
    if p.hostname.startswith("xn--") or p.hostname in ("localhost","127.0.0.1","0.0.0.0"): return False
    return not landing or p.path=="/apollo-1-evidence-atlas/"

def reviewed_css(url):
    try:
        p=urlsplit(url)
        if p.fragment:return None
        clean=urlunsplit((p.scheme,p.netloc,p.path,'',''))
        if not safe_url(clean):return None
        for suffix,(version,digest) in CSS.items():
            if p.path.endswith(suffix) and p.query=="ver="+version:return suffix
    except ValueError: pass
    return None

def permits(url,method,landing):
    if method not in ("GET","HEAD") or not safe_url(landing):return False
    if not (safe_url(url) or reviewed_css(url)):return False
    return urlsplit(url).hostname.lower()==urlsplit(landing).hostname.lower()

def redact(url):
    try:
        p=urlsplit(url)
        return p.scheme+"://"+(p.hostname or "[invalid]")+(p.path or "/")
    except ValueError:return "[invalid-url]"

def inspect(page):
    fields={"cards":page.locator(".fv-r384__card").count(),
            "publishers":page.locator("[data-fv-r384-publication]").count(),
            "rail":page.locator(".fv-r384__rail a").count(),
            "sources":page.locator("[data-fv-r384-nasa]").count(),
            "drawers":page.locator("details summary").count(),
            "cta":page.locator("[data-fv-free-cta]").count(),
            "overflow":max(0,page.evaluate("document.documentElement.scrollWidth-window.innerWidth"))}
    if [fields[k] for k in ("cards","publishers","rail","sources","drawers","cta")] != [6,2,3,6,6,1] or fields["overflow"]>1:
        raise AssertionError("structure/overflow "+str(fields))
    urls=page.locator("[data-fv-r384-publication]").evaluate_all("(els)=>els.map(x=>x.href)")
    if sorted(urls)!=sorted([PRIMARY,LATER]):raise AssertionError("NASA source substituted")
    if page.locator("[data-fv-free-cta]").first.get_attribute("href")!=FREE:raise AssertionError("unauthorized CTA")
    for link in page.locator(".fv-r384__rail a").all():
        h=link.get_attribute("href") or ""
        if not h.startswith("#") or page.locator(h).count()!=1:raise AssertionError("broken chronology")
    d=page.locator("details summary").first;d.focus();page.keyboard.press("Enter")
    if page.locator("details").first.get_attribute("open") is None:raise AssertionError("keyboard open")
    page.keyboard.press("Enter")
    if page.locator("details").first.get_attribute("open") is not None:raise AssertionError("keyboard close")
    fields["keyboard"]="PASS";return fields

def run(args):
    staging=bool(args.url)
    if staging==bool(args.fixture):raise ValueError("Supply exactly one of --url or --fixture")
    if staging and (not safe_url(args.url,True) or not args.host or urlsplit(args.url).hostname!=args.host):
        raise ValueError("staging URL and exact --host required, HTTPS, canonical landing route")
    if staging and (not args.axe or not args.axe_sha256):raise ValueError("actual staging requires independently pinned genuine axe-core")
    if args.axe:
        a=Path(args.axe)
        if not a.is_file() or not args.axe_sha256 or hashlib.sha256(a.read_bytes()).hexdigest()!=args.axe_sha256:
            raise ValueError("HOLD: axe-core file absent or SHA-256 mismatch")
        if b'axe-core' not in a.read_bytes() and b'axe.version' not in a.read_bytes():
            raise ValueError("HOLD: axe provenance needs independent review")
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    report={"scope":"INSTALLED_STAGING" if staging else "OFFLINE_FIXTURE",
            "status":"HOLD","release_allowed":False,"screens":[],"network":[],"blockers":[],
            "axe":"NOT_RUN","http_css_sha256":"NOT_TESTED","csp":"NOT_TESTED"}
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=args.chromium,args=["--no-sandbox"])
        try:
            for name,width,touch,nojs,reduced in CASES:
                ctx=browser.new_context(viewport={"width":width,"height":860},has_touch=touch,
                    java_script_enabled=not nojs,reduced_motion="reduce" if reduced else "no-preference",
                    service_workers="block",accept_downloads=False)
                page=ctx.new_page();seen=set();csp=[];errors=[]
                if staging:
                    def gate(route):
                        r=route.request;allowed=permits(r.url,r.method,args.url)
                        record={"url":redact(r.url),"method":r.method,"allowed":allowed}
                        report["network"].append(record)
                        if not allowed:route.abort("blockedbyclient");return
                        try:
                            resp=route.fetch(max_redirects=0,timeout=12000)
                            if 300<=resp.status<400 or resp.headers.get("location"):
                                record["allowed"]=False;record["redirect_denied"]=True
                                route.abort("blockedbyclient");return
                            if r.is_navigation_request() and r.resource_type=="document":
                                csp.append(resp.headers.get("content-security-policy",""))
                            key=reviewed_css(r.url)
                            if key:
                                if hashlib.sha256(resp.body()).hexdigest()!=CSS[key][1]:
                                    errors.append("CSS digest mismatch: "+key);route.abort("blockedbyclient");return
                                seen.add(key)
                            route.fulfill(response=resp)
                        except Exception as e:
                            errors.append(type(e).__name__);route.abort("blockedbyclient")
                    ctx.route("**/*",gate)
                    if hasattr(ctx,"route_web_socket"):
                        ctx.route_web_socket("**/*",lambda socket:socket.close())
                try:
                    if staging:page.goto(args.url,wait_until="domcontentloaded",timeout=15000)
                    else:
                        page.route("**/*",lambda route:route.abort("blockedbyclient"))
                        page.set_content(Path(args.fixture).read_text(encoding="utf-8"),wait_until="domcontentloaded")
                    page.wait_for_timeout(160)
                    field=inspect(page)
                    if touch:
                        page.locator("details summary").first.tap()
                        if page.locator("details").first.get_attribute("open") is None:raise AssertionError("touch drawer")
                        field["touch"]="PASS"
                    if staging:
                        if seen!=set(CSS):raise AssertionError("reviewed CSS HTTP bytes not verified")
                        if not csp or not all(csp):raise AssertionError("document CSP not delivered")
                        if errors:raise AssertionError("interception errors: "+str(errors))
                    if args.axe and not nojs:
                        page.add_script_tag(path=args.axe)
                        assessment=page.evaluate("""async()=>{if(!window.axe)throw Error('no real axe');
                          let x=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
                          return {version:axe.version,violations:x.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length}))}}""")
                        field["axe"]=assessment
                        if assessment["violations"]:raise AssertionError("axe violations "+str(assessment))
                        report["axe"]="PASS_GENUINE_ASSET"
                    field["context"]=name;field["width"]=width
                    page.screenshot(path=str(out/(name+".png")),full_page=True,animations="disabled")
                    report["screens"].append(field)
                except Exception as e:report["blockers"].append(name+": "+type(e).__name__+": "+str(e)[:240])
                finally:ctx.close()
        finally:browser.close()
    if not report["blockers"]:
        report["status"]="PASS_STAGING_BROWSER_GATE_ONLY" if staging else "PASS_LOCAL_FIXTURE_ONLY"
        if staging:report["http_css_sha256"]="MATCHED";report["csp"]="PRESENT"
    (out/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    g=parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--url");g.add_argument("--fixture")
    parser.add_argument("--host");parser.add_argument("--axe")
    parser.add_argument("--axe-sha256");parser.add_argument("--out",default="experience2/apollo-r400/QA")
    parser.add_argument("--chromium",default="/usr/bin/chromium")
    opts=parser.parse_args()
    try:
        result=run(opts)
        print(json.dumps({"status":result["status"],"screens":len(result["screens"]),"blockers":result["blockers"]}))
        sys.exit(0 if not result["blockers"] else 2)
    except Exception as e:
        print("HOLD: "+str(e),file=sys.stderr)
        sys.exit(2)
