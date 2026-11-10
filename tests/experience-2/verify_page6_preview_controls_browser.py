#!/usr/bin/env python3
"""Offline Chromium acceptance for decoupled preview controls, not WordPress QA.

Requires: pip install playwright; Chromium installed. Uses only pinned local
sources. Never visits WordPress or submits data. No image-network assertions.
"""
from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    'fv_ex2_scoped', ROOT / 'tools/experience-2/compose_page6_flagship.py')
m = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = m
SPEC.loader.exec_module(m)
CONTENT = m.stage_payload(ROOT / 'experience2/home-flagship')
WIDTHS = (320, 360, 390, 768, 1024, 1440, 1920)
CHAPTERS = m.CHAPTERS
# Synthetic header and original-content markers. NOT WordPress/Jetpack runtime.
SHELL = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
         '<meta name="viewport" content="width=device-width, initial-scale=1">'
         '<style>body{margin:0;background:#101b1b}'
         '.test-header{height:74px;background:#1d2726;color:#eee6d8;'
         'display:flex;align-items:center;padding:0 22px;'
         'font:600 14px system-ui}</style></head><body>'
         '<header class="test-header">Simulated theme header only</header>'
         + CONTENT + '<div class="synthetic-outside">'
         + ''.join('<span class="fv-margin-strip__item">synthetic %d</span>' % i
                   for i in range(72))
         + '</div><section class="fv-focus-cta"><a class="fv-focus-cta__button" '
         'href="/focus/">Original Focus link</a></section></body></html>')


def inspect(page):
    return page.evaluate("""() => {
      const root=document.querySelector('.fv-hf');
      const rail=root.querySelector('.fv-hf__focus-rail a');
      const size=rail.getBoundingClientRect();
      return {
        hasStudio:!!root.querySelector('.fv-hf__studio'),
        direction:root.dataset.fvDirection,
        enhanced:root.classList.contains('fv-hf--enhanced'),
        chapters:%s.every(id=>!!root.querySelector('#'+id)),
        originalMargins:document.querySelectorAll('.fv-margin-strip__item').length,
        originalFocus:document.querySelector('.fv-focus-cta__button')?.getAttribute('href'),
        railHref:rail.getAttribute('href'), railHeight:size.height,
        hiddenCases:[...root.querySelectorAll('[data-fv-case]')].filter(x=>x.hidden).length,
        overflow:document.documentElement.scrollWidth > innerWidth
      };
    }""" % json.dumps(CHAPTERS))


def main():
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        for width in WIDTHS:
            for enabled in (False, True):
                page = browser.new_page(
                    viewport={'width': width, 'height': 900},
                    java_script_enabled=enabled, reduced_motion='reduce')
                failures=[]
                page.on('pageerror', lambda error: failures.append(str(error)))
                page.route('**/*', lambda r: r.abort())
                page.set_content(SHELL, wait_until='domcontentloaded')
                page.wait_for_timeout(80)
                data=inspect(page)
                assert not failures, (width, enabled, failures)
                assert not data['hasStudio'] and data['chapters']
                assert data['originalMargins']==72 and data['originalFocus']=='/focus/'
                assert data['railHref']=='https://finalvestige.com/focus/'
                assert data['railHeight']>=44 and not data['overflow']
                assert data['enhanced']==enabled
                assert data['hiddenCases']==(2 if enabled else 0)
                if enabled:
                    button=page.locator('[data-fv-case-button="franklin"]')
                    button.click()
                    assert button.get_attribute('aria-pressed')=='true'
                    assert page.locator('[data-fv-case="franklin"]').is_visible()
                    assert page.locator('[data-fv-case="apollo"]').is_hidden()
                results.append({'width':width,'javascript':enabled,**data})
                page.close()
        for d in ('dossier','museum','observatory'):
            page=browser.new_page(viewport={'width':390,'height':900})
            page.route('**/*', lambda r: r.abort())
            alternate=SHELL.replace('data-fv-direction="dossier"',
                                    'data-fv-direction="'+d+'"', 1)
            page.set_content(alternate, wait_until='domcontentloaded')
            assert inspect(page)['direction']==d
            page.close()
        browser.close()
    print(json.dumps({'status':'PASS','scenarios':len(results),
                      'art_directions':'3/3 preserved','results':results},
                     indent=2))


if __name__=='__main__':
    main()
