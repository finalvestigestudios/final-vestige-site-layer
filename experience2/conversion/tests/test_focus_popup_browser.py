#!/usr/bin/env python3
"""Chromium fixture checks for FV Focus CTA. NOT actual WordPress/Jetpack acceptance."""
from pathlib import Path
import json
import os
import subprocess
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
HASHES={"focus-popup.html":"81bb038297e53ce92f7b75bf9f348d71c06af5c5",
        "focus-popup.css":"ce8b5a9a6e3352281d8a1b6bd45b4b02dd655500",
        "focus-popup.js":"5fdd7bebbca75d3cf6b167f8d4070f6364c675e2"}
for name,want in HASHES.items():
    assert subprocess.check_output(["git","hash-object",str(ROOT/name)],text=True).strip()==want,name
markup=(ROOT/"focus-popup.html").read_text()
css=(ROOT/"focus-popup.css").read_text()
js=(ROOT/"focus-popup.js").read_text()
marker='<!-- wp:jetpack/subscriptions {"submitButtonText":"Join & get the Fieldbook"} /-->'
assert marker in markup
form='<form action="#fixture"><label for="email">Email</label><input id="email" type="email"><button type="button">Join</button></form>'
results=[]

def fixture(browser,width=390,render_form=True,enable_js=True):
    ctx=browser.new_context(viewport={"width":width,"height":800},java_script_enabled=enable_js,
                            reduced_motion="reduce")
    page=ctx.new_page()
    html=markup.replace(marker,form if render_form else "<p>Form unavailable.</p>")
    page.set_content('<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{background:#090a0a;color:#f4efe6;margin:1rem;font-family:Arial}*,*:before,*:after{box-sizing:border-box}form{display:grid;gap:.5rem}input,form button{min-height:48px}</style><style>'+css+'</style></head><body>'+html+'</body></html>')
    if enable_js:page.add_script_tag(content=js)
    return page,ctx

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=os.environ.get("FV_CHROMIUM","/usr/bin/chromium"),
                              args=["--no-sandbox","--disable-dev-shm-usage"])
    for width in (320,360,390,768,1024,1440,1920):
        page,ctx=fixture(browser,width)
        assert page.get_by_role("button",name="Get the free Fieldbook").is_visible()
        assert not page.get_by_role("link",name="Explore the free Fieldbook").is_visible()
        page.get_by_role("button",name="Get the free Fieldbook").click()
        assert page.get_by_role("dialog",name="The Seven Day Focus Fieldbook").is_visible()
        assert page.locator("input[type=email]").evaluate("(e)=>document.activeElement===e")
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
        page.keyboard.press("Escape")
        assert not page.locator("dialog").evaluate("(e)=>e.open")
        assert page.locator(".fv-focus-invite__open").evaluate("(e)=>document.activeElement===e")
        page.locator(".fv-focus-invite__open").click()
        page.get_by_role("button",name="Close book signup").click()
        assert not page.locator("dialog").evaluate("(e)=>e.open")
        results.append({"test":"real_chromium_width_"+str(width),"pass":True})
        ctx.close()
    for name,form_ok,js_ok in (("missing_form",False,True),("no_js",True,False)):
        page,ctx=fixture(browser,render_form=form_ok,enable_js=js_ok)
        assert page.get_by_role("link",name="Explore the free Fieldbook").is_visible()
        assert not page.locator(".fv-focus-invite__open").is_visible()
        results.append({"test":name,"pass":True})
        ctx.close()
    browser.close()

print(json.dumps({"passed":len(results),"tests":results,"note":"Synthetic rendered-form fixture; not WP, real email delivery, axe, Safari or Lighthouse"},indent=2))
