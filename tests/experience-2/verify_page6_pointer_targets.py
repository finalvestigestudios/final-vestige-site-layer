#!/usr/bin/env python3
"""Fail-closed isolated Chromium target-size audit for Page 6 integration.

Synthetic theme header, NOT actual WordPress/Assembler/axe or WCAG certification.
Requires playwright + Chromium. External network intentionally blocked.
"""
import importlib.util
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'experience2/home-flagship'
spec = importlib.util.spec_from_file_location('ex2_composer', ROOT / 'tools/experience-2/compose_page6_flagship.py')
composer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(composer)
payload = composer.stage_payload(SOURCE)  # all eleven exact pinned source blobs
shell = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
         '<meta name="viewport" content="width=device-width,initial-scale=1">'
         '</head><body><header style="height:75px;background:#172323;color:#fff;padding:20px">'
         'Simulated theme header (not Assembler)</header>' + payload + '</body></html>')
probe = """() => {
  const root = document.querySelector('.fv-hf');
  const visible = [...root.querySelectorAll('a,button,summary')].filter(e => {
    const r = e.getBoundingClientRect(), c = getComputedStyle(e);
    return r.width > 0 && r.height > 0 && c.display !== 'none' &&
      c.visibility !== 'hidden' && !e.closest('[hidden]');
  });
  const small = visible.flatMap(e => {
    const r = e.getBoundingClientRect();
    return (r.width < 24 || r.height < 24) ? [{
      tag: e.tagName, label: (e.textContent || '').trim().slice(0,60),
      width: +r.width.toFixed(2), height: +r.height.toFixed(2)
    }] : [];
  });
  return {
    undersized: small, count: visible.length,
    focusHeight: root.querySelector('.fv-hf__focus-rail a').getBoundingClientRect().height,
    sourceSummaryHeight: root.querySelector('.fv-hf__case-actions summary').getBoundingClientRect().height,
    overflow: document.documentElement.scrollWidth - innerWidth,
    chapters: ['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry',
      'fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'].every(id => !!root.querySelector('#'+id))
  };
}"""
results = []
with sync_playwright() as p:
    binary = '/usr/bin/chromium' if Path('/usr/bin/chromium').exists() else None
    browser = p.chromium.launch(executable_path=binary, headless=True, args=['--no-sandbox'])
    for width in (320, 360, 390, 768, 1024, 1440, 1920):
        for javascript in (True, False):
            page = browser.new_page(viewport={'width': width, 'height': 900},
                                    java_script_enabled=javascript, reduced_motion='reduce')
            page.route('**/*', lambda route: route.abort())
            errors = []
            page.on('pageerror', lambda err: errors.append(str(err)))
            page.set_content(shell)
            page.wait_for_timeout(80)
            data = page.evaluate(probe)
            assert not errors, (width, javascript, errors)
            assert data['count'] >= 45, (width, javascript, data)
            assert not data['undersized'], (width, javascript, data['undersized'])
            assert data['sourceSummaryHeight'] >= 44, (width, javascript, data)
            assert data['focusHeight'] >= 44, (width, javascript, data)
            assert data['overflow'] == 0 and data['chapters'], (width, javascript, data)
            if javascript and width in (320, 390):
                control = page.locator('.fv-hf__case-actions summary').first
                control.focus()
                control.press('Enter')
                assert page.locator('.fv-hf__case-actions details').first.get_attribute('open') is not None
            results.append({'width': width, 'javascript': javascript, 'result': 'PASS', **data})
            page.close()
    browser.close()
report = {'status': 'PASS', 'scenarios': len(results),
          'environment': 'real Chromium, synthetic theme shell, external network aborted',
          'not_verified': ['WordPress/Assembler', 'axe/WCAG 2.2 AA', 'manual 200% zoom',
                           'real image loads', 'Jetpack subscription', 'Lighthouse/CWV', 'CI/QD'],
          'results': results}
Path('ex2_pointer_target_results.json').write_text(json.dumps(report, indent=2), 'utf-8')
print(f"PASS {len(results)}/{len(results)} source-pinned offline Chromium scenarios; NOT WordPress acceptance")
