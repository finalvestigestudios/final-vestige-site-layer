#!/usr/bin/env python3
"""Reflow proxy: exact checkout, scoped 7-chapter Gutenberg payload, real Chromium.

Run: python tests/experience-2/verify_page6_reflow_proxy.py
Narrow CSS viewports model available layout width after user zoom, but do NOT
represent actual browser zoom, WordPress/Assembler, live image fetches or WCAG
certification. No network or CMS writes.
"""
import importlib.util
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
COMPOSER = ROOT / "tools/experience-2/compose_page6_flagship.py"
SOURCE = ROOT / "experience2/home-flagship"
WIDTHS = (320, 360, 384, 390, 480, 720, 768, 960, 1440, 1920)
DIRECTIONS = ("dossier", "museum", "observatory")

def main():
    spec = importlib.util.spec_from_file_location("fv_composer", COMPOSER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = module.stage_payload(SOURCE)  # fail closed on 11 pinned source blobs
    shell = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
             '<meta name="viewport" content="width=device-width,initial-scale=1">'
             '</head><body><header style="height:75px;background:#172323;color:white">'
             'SIMULATED ASSEMBLER SHELL — NOT WORDPRESS</header>')
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
        for width in WIDTHS:
            for direction in DIRECTIONS:
                for js in (False, True):
                    page = browser.new_page(viewport={"width": width, "height": 900},
                                            java_script_enabled=js, reduced_motion="reduce")
                    page.route("**/*", lambda route: route.abort())
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.set_content(shell + payload + "</body></html>")
                    page.evaluate("(d)=>document.querySelector('.fv-hf').setAttribute('data-fv-direction',d)", direction)
                    page.wait_for_timeout(40)
                    facts = page.evaluate("""() => {
                      const root=document.querySelector('.fv-hf');
                      const ids=['fv-hf-title','fv-hf-chronicle','fv-hf-evidence',
                        'fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'];
                      const focus=root.querySelector('.fv-hf__focus-rail a');
                      const active=e=>{
                        const s=getComputedStyle(e),r=e.getBoundingClientRect();
                        return !e.closest('[hidden],[inert]') && s.visibility!=='hidden' &&
                          s.display!=='none' && r.width>0 && r.height>0;
                      };
                      const bad=[...root.querySelectorAll('a,button,summary')].filter(active)
                        .map(e=>({label:e.textContent.trim().slice(0,45),
                          width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height}))
                        .filter(e=>e.width<24 || e.height<24);
                      return {overflow:Math.max(0,document.documentElement.scrollWidth-innerWidth),
                        chapters:ids.every(id=>!!root.querySelector('#'+id)),
                        focusUrl:focus.getAttribute('href'),focusHeight:focus.getBoundingClientRect().height,
                        badTargets:bad};
                    }""")
                    facts.update(width=width, direction=direction, js=js, pageErrors=errors)
                    results.append(facts)
                    assert not errors, (width, direction, js, errors)
                    assert facts["chapters"] and facts["overflow"]==0, facts
                    assert facts["focusUrl"]=="https://finalvestige.com/focus/" and facts["focusHeight"]>=44
                    assert not facts["badTargets"], facts
                    if js and width in (320, 384, 720):
                        d = page.locator(".fv-hf__case-actions summary").first
                        d.focus()
                        d.press("Enter")
                        assert page.locator(".fv-hf__case-actions details").first.get_attribute("open") is not None
                    page.close()
        browser.close()
    outfile = ROOT / "page6-reflow-proxy-local-results.json"
    outfile.write_text(json.dumps({"method":"narrow CSS viewport, not native browser zoom",
                                   "wordPress":"NOT TESTED","scenarios":results},indent=2))
    print(f"PASS {len(results)}/{len(results)} exact-source reflow proxy cases; "
          "not actual browser zoom, hosted WordPress, axe, or Lighthouse")

if __name__ == "__main__":
    main()
