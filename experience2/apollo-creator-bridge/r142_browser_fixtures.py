#!/usr/bin/env python3
"""Apollo R142: REAL Chromium DOM fixtures only, NEVER production acceptance.
Offline (page.set_content) checks accessible names, no-JS focus and responsive overflow.
No NASA imagery, network request, purchased offer or visitor data.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

WIDTHS=(320,360,390,768,1440,1920)
ARTICLE="https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/"
CTA=f'<a id="reader" href="{ARTICLE}">Read the full investigation</a>'
BAD={
    "aria_hidden_text":f'<a id="reader" href="{ARTICLE}"><span aria-hidden="true">Read the full investigation</span></a>',
    "hidden_text":f'<a id="reader" href="{ARTICLE}"><span hidden>Read the full investigation</span></a>',
    "textarea":f'<textarea id="holder">{CTA}</textarea>',
    "title":f'<title>{CTA}</title>',
    "image_alt":f'<a id="reader" href="{ARTICLE}"><img alt="Buy now">Read the full investigation</a>',
    "closed_details":f'<details><summary>Read more</summary>{CTA}</details>'
}
HTML="""<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>html{color:#f3ead8;background:#0c0c09;font:16px/1.5 system-ui}body{margin:0}
main{max-width:1080px;padding:24px;margin:auto}h1{font:clamp(2rem,6vw,4rem)/1.1 Georgia,serif}
p{max-width:62ch}a{color:#f3c783;padding:12px 0;display:inline-block}
a:focus-visible{outline:3px solid #e9c58d;outline-offset:4px}
article{border:1px solid #a68b65;padding:24px;min-width:0;overflow-wrap:anywhere}</style>
</head><body><main><h1>Evidence and limits</h1><article><p>Static reader action — controlled test fixture, not NASA evidence.</p>
{markup}<p>Source continuity must survive when JavaScript is unavailable.</p></article></main></body></html>"""

def run(destination):
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    rows=[]
    with sync_playwright() as p:
        kw={"headless":True,"args":["--no-sandbox","--disable-dev-shm-usage"]}
        if os.path.isfile("/usr/bin/chromium"):kw["executable_path"]="/usr/bin/chromium"
        browser=p.chromium.launch(**kw)
        try:
            for width in WIDTHS:
                context=browser.new_context(viewport={"width":width,"height":880},java_script_enabled=False,reduced_motion="reduce")
                page=context.new_page()
                page.set_content(HTML.replace("{markup}",CTA),wait_until="domcontentloaded")
                assert page.get_by_role("link",name="Read the full investigation").count()==1
                page.keyboard.press("Tab")
                focused=page.evaluate("document.activeElement && document.activeElement.id")
                assert focused=="reader",(width,focused)
                assert page.locator("#reader").is_visible()
                style=page.evaluate("getComputedStyle(document.activeElement).outlineWidth")
                assert float(style.replace("px",""))>=2,(width,style)
                overflow=page.evaluate("document.documentElement.scrollWidth>window.innerWidth")
                assert not overflow,width
                screenshot=destination/f"r142_nojs_{width}.png"
                page.screenshot(path=str(screenshot),full_page=True)
                rows.append({"kind":"positive_fixture","width":width,"keyboard_focus":focused,"outline_width":style,"overflow":overflow,"screenshot_sha256":hashlib.sha256(screenshot.read_bytes()).hexdigest()})
                context.close()
            for key,markup in BAD.items():
                context=browser.new_context(viewport={"width":390,"height":850},java_script_enabled=False,reduced_motion="reduce")
                page=context.new_page()
                page.set_content(HTML.replace("{markup}",markup),wait_until="domcontentloaded")
                matches=page.get_by_role("link",name="Read the full investigation",exact=True).count()
                # Hidden text lacks a computed label, textarea/title lack a DOM anchor,
                # image alt changes the name, and closed-details link is not exposed.
                assert matches==0,(key,matches)
                rows.append({"kind":"negative_fixture","case":key,"accessible_reader_role_count":matches,"expected_source_gate":"REVIEW_REQUIRED"})
                context.close()
        finally:
            browser.close()
    receipt={"schema":"fv.apollo.r142.chromium-fixtures.v1","test_type":"PLAYWRIGHT_SET_CONTENT_SYNTHETIC_ONLY","navigation":"NOT_ACTUAL_APOLLO","axe":"NOT_RUN","actual_lcp_cls":"NOT_MEASURED","photo_rights":"NOT_APPROVED","release":"STAGING_HOLD","cases":rows}
    (destination/"r142_browser_fixture_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    return receipt

if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--out",default="r142_artifacts");args=parser.parse_args()
    result=run(args.out)
    print(f"PASS {len(result['cases'])} controlled Chromium cases — NOT Apollo actual-page acceptance")
