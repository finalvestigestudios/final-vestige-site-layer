#!/usr/bin/env python3
"""DOM-level proof of production operation 2: axe label-content-name-mismatch on the Focus CTA button
before and after removing its aria-label (the exact transformation in replacement-block-index2.html)."""
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
axe, url, out = sys.argv[1], sys.argv[2], Path(sys.argv[3])
with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome"); pg = b.new_page(viewport={"width": 1440, "height": 900}); pg.goto(url, wait_until="load"); pg.wait_for_timeout(1000)
    pg.add_style_tag(content=".fv-home-shell,.fv-enter-record{content-visibility:visible!important}")
    pg.add_script_tag(path=axe)
    run = "async()=>{const r=await axe.run('.fv-focus-cta__button',{runOnly:['label-content-name-mismatch']});return {violations:r.violations.length,passes:r.passes.length,name:document.querySelector('.fv-focus-cta__button').getAttribute('aria-label')}}"
    before = pg.evaluate(run)
    pg.evaluate("document.querySelector('.fv-focus-cta__button').removeAttribute('aria-label')")
    after = pg.evaluate(run)
    b.close()
res = {"rule": "label-content-name-mismatch (WCAG 2.5.3)", "before": before, "after_removing_aria_label": after}
out.write_text(json.dumps(res, indent=1)); print(json.dumps(res))
