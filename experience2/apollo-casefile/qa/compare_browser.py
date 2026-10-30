#!/usr/bin/env python3
"""Real Chromium smoke; set_content fixture only, never report field CWV."""
import json,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from render import render
html=render(json.loads((ROOT/'records.json').read_text()),json.loads((ROOT/'custody.json').read_text()))
result={"mode":"real local Chromium set_content; network navigation unavailable","tested":[],"axe":"NOT RUN"}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for w in (320,360,390,768,1024,1440,1920):
        page=browser.new_page(viewport={"width":w,"height":900})
        errors=[]
        page.on("pageerror",lambda error:errors.append(str(error)))
        page.set_content(html,wait_until="load")
        assert page.locator('[data-ex2-compare-tools]').is_visible()
        assert page.locator('[data-ex2-compare-pane="a"] [data-ex2-compare-id="02"]').count()==1
        assert page.locator('[data-ex2-compare-pane="b"] [data-ex2-compare-id="05"]').count()==1
        page.locator('[data-ex2-compare-a]').select_option("03")
        page.locator('[data-ex2-compare-b]').select_option("06")
        page.locator('[data-ex2-compare-swap]').click()
        assert page.locator('[data-ex2-compare-pane="a"] [data-ex2-compare-id="06"]').count()==1
        assert page.locator('[data-ex2-compare-pane="b"] [data-ex2-compare-id="03"]').count()==1
        page.locator('[data-ex2-compare-pane="a"] a[href="#source-06"]').focus()
        page.keyboard.press("Enter")
        assert page.locator('#source-06').evaluate("(e)=>e.open")
        assert page.evaluate("document.activeElement.tagName")=="SUMMARY"
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
        assert not errors,errors
        result['tested'].append(w)
        page.close()
    p0=browser.new_page(viewport={"width":390,"height":880},java_script_enabled=False)
    p0.set_content(html)
    assert p0.locator('[data-ex2-compare-tools]').is_hidden()
    assert p0.locator('[data-ex2-compare-pane="a"] [data-ex2-compare-id="02"]').is_visible()
    assert p0.locator('[data-ex2-compare-pane="b"] [data-ex2-compare-id="05"]').is_visible()
    p0.close()
    p1=browser.new_page(viewport={"width":390,"height":880})
    p1.evaluate("() => {Element.prototype.replaceChildren=function(){throw new Error('injected')};}")
    p1.set_content(html)
    assert p1.locator('[data-ex2-compare-tools]').is_hidden()
    assert p1.locator('[data-ex2-compare-pane="a"] [data-ex2-compare-id="02"]').is_visible()
    p1.close()
    p2=browser.new_page(viewport={"width":390,"height":900},reduced_motion="reduce")
    p2.set_content(html)
    p2.evaluate("document.body.style.zoom='2'")
    assert p2.evaluate("document.documentElement.scrollWidth<=innerWidth+1")
    p2.close()
    browser.close()
print("COMPARE_CHROMIUM_PASS:",result)
