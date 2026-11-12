#!/usr/bin/env python3
"""R303: adversarial source-integrity recovery, no WP/merchant/network writes.

Run from a checkout with PHP and Python Playwright/Chromium. Tests four
independent corruption classes via actual PHP, then Chromium at 320-1920px.
The fixture source is copied to a temp directory; the repository is unchanged.
"""
from pathlib import Path
import json
import re
import subprocess
import tempfile
from playwright.sync_api import sync_playwright

root=Path(__file__).resolve().parents[2]
src=(root/'apollo-r281/apollo-source-experience.php').read_text()
css=(root/'apollo-r281/assets/apollo-source-experience.css').read_text()
checks={
    'event-claim-digest': ('The pad test and fire', 'The pad test and fire [UNREVIEWED TEST]'),
    'nasa-url-allowlist': ("'source_url'=>FV_R281_NASA_MISSION", "'source_url'=>'https://example.invalid/hostile-replacement'"),
    'reconciliation-digest': ('Later NASA Safety and Mission Assurance summary', 'Changed NASA summary [UNREVIEWED TEST]'),
    'authority-ledger-digest': ('January 31 · dated memorandum received', 'Changed Jan 31 date [UNREVIEWED TEST]'),
}
# PHP's only WordPress dependency in these paths is the ABSPATH sentinel.
harness="""<?php
define('ABSPATH', __DIR__);
function plugins_url($path, $file) { return '/assets/' . basename($path); }
require __DIR__.'/candidate.php';
print '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body><main>';
print fv_r281_render(); print fv_r281_render();
print '</main></body></html>';
"""
responses={}
with tempfile.TemporaryDirectory() as td:
    d=Path(td);(d/'harness.php').write_text(harness)
    for label,(a,b) in checks.items():
        assert src.count(a)==1, (label,src.count(a))
        (d/'candidate.php').write_text(src.replace(a,b,1))
        subprocess.run(['php','-l',str(d/'candidate.php')],check=True,capture_output=True)
        html=subprocess.check_output(['php',str(d/'harness.php')],text=True)
        assert html.count('source-integrity-failed')==2, label
        assert 'The pad test and fire' not in html, label
        assert 'What the record establishes' not in html,label
        assert html.count('official-evidence-source')==2,label
        assert html.count('editorial-continuation')==2,label
        assert 'merchant-confirmed' not in html and '<script' not in html.lower(),label
        assert len(re.findall(r'aria-label="Apollo 1 source integrity recovery [12]"',html))==2,label
        responses[label]=html
    # A compliant unmodified source must render the full evidence atlas, not recovery.
    (d/'candidate.php').write_text(src)
    healthy=subprocess.check_output(['php',str(d/'harness.php')],text=True)
    assert healthy.count('data-fv-evidence-status="editorial-review-pending"')==2
    assert 'source-integrity-failed' not in healthy

browser_cases=0; link_asserts=0; keyboard_asserts=0; fallback_css_asserts=0
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for label,raw in responses.items():
        for width in (320,390,768,1440,1920):
            for js in (False,True):
                page=b.new_page(viewport={'width':width,'height':820},java_script_enabled=js,
                                reduced_motion='reduce',has_touch=True)
                page.set_content(raw)
                regions=page.locator('[data-fv-evidence-status="source-integrity-failed"]')
                assert regions.count()==2, (label,width,js)
                assert not page.locator('section.fv-r281').count()
                assert page.locator('img,script,form,iframe,[data-fv-conversion-kind="paid-order"]').count()==0
                for region in regions.all():
                    nasa=region.locator('a[data-fv-link-purpose="official-evidence-source"]')
                    assert nasa.count()==1
                    assert nasa.get_attribute('href')=='https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/'
                    assert nasa.get_attribute('data-fv-conversion-kind')=='noncommercial-source-reference'
                    assert 'noreferrer' in nasa.get_attribute('rel')
                    cta=region.locator('a[data-fv-cta="apollo-read-free-investigation"]')
                    assert cta.count()==1
                    assert cta.get_attribute('href')=='https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/'
                    assert cta.get_attribute('data-fv-conversion-kind')=='editorial-continuation'
                    assert region.get_attribute('data-fv-funnel-scope')=='editorial-recovery'
                    link_asserts+=2
                names=page.locator('[aria-label^="Apollo 1 source integrity recovery"]').evaluate_all('(x)=>x.map(e=>e.getAttribute("aria-label"))')
                assert len(set(names))==2
                page.keyboard.press('Tab');assert page.evaluate('document.activeElement.tagName')=='A'
                page.keyboard.press('Tab');assert page.evaluate('document.activeElement.tagName')=='A'
                keyboard_asserts+=2
                assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
                # No component stylesheet is required for readable recovery.
                assert page.locator('main aside').first.is_visible()
                fallback_css_asserts+=1
                if width in (390,1440) and not js and label=='event-claim-digest':
                    shot=Path(__file__).resolve().parents[1]/'QA'/f'r303-{width}-recovery-nojs.png'
                    shot.parent.mkdir(parents=True,exist_ok=True)
                    page.screenshot(path=str(shot),full_page=True,animations='disabled')
                browser_cases+=1
                page.close()
    b.close()
assert browser_cases==40 and link_asserts==160 and keyboard_asserts==80 and fallback_css_asserts==40
receipt={'version':'R303','corruption_classes':list(checks),'source_validation_status':'all mutations rejected','browser_contexts_passed':browser_cases,'link_contract_assertions':link_asserts,'keyboard_assertions':keyboard_asserts,'no_css_assertions':fallback_css_asserts,'genuine_axe':'NOT EXECUTED','installed_wordpress':'NOT VERIFIED','field_cwv':'NOT VERIFIED'}
(Path(__file__).resolve().parents[1]/'QA'/'r303-test-receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
print(json.dumps(receipt,indent=2))
