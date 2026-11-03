#!/usr/bin/env python3
"""R85 real Chromium/axe source review board gate, no WordPress or NASA requests."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import fitz
from playwright.sync_api import sync_playwright

WIDTHS = (320, 390, 768, 1440, 1920)
EXPECTED = ("S67-19766", "S67-15717", "S66-58038",
            "KSC-20170124-PH_KLS01_0164", "S67-21294",
            "KSC-20170124-PH_KLS01_0090")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(src: Path, out: Path, axe: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    assert axe.is_file(), "R85_AXE_MISSING"
    assert (src / "R85_NASA_SOURCE_REVIEW.html").is_file(), "R85_BOARD_MISSING"
    cases, screenshots, violations = [], {}, []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for width in WIDTHS:
            for js in (False, True):
                context = browser.new_context(viewport={"width":width,"height":900},
                    java_script_enabled=js, reduced_motion="reduce",
                    is_mobile=width<=390,has_touch=width<=390)
                if js:
                    context.add_init_script("""(()=>{
                      window.__fv_r85_perf={lcp:null,cls:0};
                      try{new PerformanceObserver(l=>{
                        const e=l.getEntries(); if(e.length)
                        window.__fv_r85_perf.lcp=e[e.length-1].startTime;
                      }).observe({type:'largest-contentful-paint',buffered:true})}catch(_){}
                      try{new PerformanceObserver(l=>{
                        for(const e of l.getEntries())if(!e.hadRecentInput)
                          window.__fv_r85_perf.cls+=e.value;
                      }).observe({type:'layout-shift',buffered:true})}catch(_){}
                    })();""")
                page = context.new_page()
                outgoing, errors = [], []
                page.on("pageerror",lambda err: errors.append("SCRIPT_ERROR"))
                def route(req):
                    if req.request.url.startswith(("https://","http://")):
                        outgoing.append("REMOTE_REQUEST")
                        req.abort()
                    else:
                        req.continue_()
                page.route("**/*",route)
                page.goto((src / "R85_NASA_SOURCE_REVIEW.html").resolve().as_uri(),
                          wait_until="load",timeout=25000)
                page.wait_for_timeout(200)
                assert not outgoing and not errors,"R85_NETWORK_OR_SCRIPT_ERROR"
                assert page.locator(".card").count()==6,"R85_CARDS_LOST"
                assert page.locator(".buttonlink").count()==6,"R85_NASA_LINK_COUNT"
                assert page.locator("img,iframe,[data-lat],[data-lon],[data-geo-edge]").count()==0,"R85_UNREVIEWED_MEDIA"
                assert page.locator("details summary").count()==6,"R85_NATIVE_DISCLOSURES"
                assert page.locator("nav.jump a").count()==6,"R85_JUMP_LINKS"
                links=page.locator(".buttonlink").evaluate_all(
                    "(a)=>a.map(e=>e.getAttribute('href'))")
                assert len(set(links))==6 and all(
                    u.startswith("https://www.nasa.gov/image-detail/") for u in links),"R85_LINK_IDENTITY"
                body=page.locator("body").inner_text()
                assert all(c in body for c in EXPECTED),"R85_CATALOG_LOST"
                assert "0 of 6 photographs" in body and "provisional" in body.lower(),"R85_HOLD_LOST"
                assert not page.evaluate("document.documentElement.scrollWidth>innerWidth+2"),"R85_OVERFLOW"
                page.locator("details summary").first.focus()
                page.keyboard.press("Enter")
                assert page.locator("details").first.evaluate("(e)=>e.open"),"R85_KEYBOARD_OPEN"
                page.keyboard.press("Enter")
                assert not page.locator("details").first.evaluate("(e)=>e.open"),"R85_KEYBOARD_CLOSE"
                page.locator("nav.jump a").nth(2).click()
                assert page.evaluate("location.hash")=="#r85-source-03","R85_ANCHOR"
                boxes=page.locator(".buttonlink").evaluate_all(
                    "(nodes)=>nodes.map(n=>({w:n.getBoundingClientRect().width,h:n.getBoundingClientRect().height}))")
                assert all(box["h"]>=43.5 and box["w"]>=43.5 for box in boxes),"R85_TOUCH_TARGET"
                assert page.locator(".card").first.evaluate(
                    "(e)=>getComputedStyle(e).backgroundColor")!="rgba(0, 0, 0, 0)","R85_CSS_MISSING"
                case={"width":width,"javascript_enabled":js,
                      "horizontal_overflow":False,"off_origin_requests":0,
                      "nasa_source_links":len(links),"source_records":6,
                      "keyboard_details":True,"touch_targets_44px":True,
                      "axe_violations":None,"lab_lcp_ms":None,"lab_cls":None}
                if js:
                    page.add_script_tag(path=str(axe))
                    audit=page.evaluate("""async()=>{
                      const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}});
                      return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,count:v.nodes.length})),passes:r.passes.length};
                    }""")
                    case["axe_violations"]=audit["violations"]
                    case["axe_rules_passed"]=audit["passes"]
                    violations.extend(audit["violations"])
                    perf=page.evaluate("window.__fv_r85_perf||null")
                    if perf:
                        case["lab_lcp_ms"]=perf["lcp"]
                        case["lab_cls"]=perf["cls"]
                        assert perf["cls"]<=0.1,"R85_LAB_CLS"
                if width in (390,1440) and js:
                    path=out / f"R85_RIGHTS_BOARD_{width}.png"
                    page.screenshot(path=str(path),full_page=True,animations="disabled")
                    screenshots[str(width)]=sha256(path)
                    if width==1440:
                        pdf=out/"R85_RIGHTS_BOARD_PRINT.pdf"
                        page.pdf(path=str(pdf),format="A4",print_background=True)
                        assert pdf.stat().st_size>5000,"R85_PRINT_PDF"
                        with fitz.open(pdf) as document:
                            printed = "".join(page.get_text() for page in document)
                            compact = "".join(printed.split())
                            for catalog in EXPECTED:
                                assert catalog in compact, "R85_PRINT_CATALOG_LOST"
                            for link in links:
                                assert "".join(link.split()) in compact, "R85_PRINT_URL_LOST"
                            assert "0of6photographs" in compact, "R85_PRINT_HOLD_LOST"
                            case["pdf_pages"] = len(document)
                            case["pdf_nasa_links_visible"] = 6
                cases.append(case)
                context.close()
        forced=browser.new_context(viewport={"width":390,"height":844},
            forced_colors="active",reduced_motion="reduce",java_script_enabled=True)
        forced_page=forced.new_page()
        forced_page.goto((src/"R85_NASA_SOURCE_REVIEW.html").resolve().as_uri())
        assert forced_page.locator(".card").count()==6,"R85_FORCED_COLORS_LOST"
        forced_page.locator("summary").first.focus()
        forced_page.keyboard.press("Enter")
        assert forced_page.locator("details").first.evaluate("(e)=>e.open"),"R85_FORCED_COLORS_KEYBOARD"
        forced_page.screenshot(path=str(out/"R85_FORCED_COLORS_390.png"),full_page=True)
        screenshots["forced_390"]=sha256(out/"R85_FORCED_COLORS_390.png")
        forced.close()
        browser.close()
    assert not violations,"R85_AXE_VIOLATIONS"
    receipt={
        "schema":"fv.apollo.r85.chromium-axe-review.v1","release":"STAGING_HOLD",
        "cases":cases,"browser":"chromium","axe_gate":"PASS",
        "screenshots_sha256":screenshots,"photographs_cleared":0,
        "hosted_wordpress_tested":False,"production_CWV":False,
        "no_website_writes":True
    }
    (out/"R85_CHROMIUM_RECEIPT.json").write_text(
        json.dumps(receipt,sort_keys=True,indent=2)+"\n",encoding="utf8")
    return receipt


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--src",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--axe",type=Path,required=True)
    args=parser.parse_args()
    result=run(args.src,args.out,args.axe)
    print("R85: Chromium",len(result["cases"]),"cases; axe PASS; STAGING_HOLD")
