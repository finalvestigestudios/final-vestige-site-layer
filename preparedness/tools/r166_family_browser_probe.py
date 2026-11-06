#!/usr/bin/env python3
"""R166: offline Chromium preflight of the exact, still-unapproved Family Card draft.

A local HTML sandbox is not WordPress privacy, print, safety, source, or QD approval.
It requires R165's complete source/citation custody before an authentic probe.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import shutil
import tempfile
from urllib.parse import urlsplit

SCHEMA = 'fv-preparedness-r166-family-browser-preflight-v1'
WIDTHS = (360, 390, 768, 1440)
FORM_FIELDS = ('hhName', 'hhPhone', 'outName', 'outPhone', 'meet1', 'meet2',
               'school', 'schoolPlan', 'pickup', 'careName', 'carePhone', 'access', 'reviewed')
SENTINEL = 'ZZ-SYNTHETIC-NOT-A-PERSON-0426'
SENSITIVE = ('school', 'schoolPlan', 'pickup', 'careName', 'carePhone', 'access', 'meet2')


def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def valid_card(html: str) -> None:
    """Pre-browser invariants, not a substitute for R165's authentic custody."""
    need(isinstance(html, str) and len(html) > 200, 'empty preview')
    need(html.count('<script>') == 1 and html.count('</script>') == 1, 'script count drift')
    need('{{inline-js:' not in html, 'unexpanded source dependency')
    need('{{cite:' in html, 'source identifiers lost from pre-rendered preview')
    need('id="rc"' in html and 'onsubmit="return false"' in html, 'form contract changed')
    for key in FORM_FIELDS:
        need(f'id="rc-{key}"' in html, f'missing original field: {key}')
    need('id="rc-minimal"' in html and 'id="rc-reset"' in html, 'privacy controls removed')
    need('id="rc-print"' in html and 'id="rc-sheet"' in html, 'print controls removed')
    need('A printed card can be lost' in html, 'printed-card privacy notice missing')
    need(not re.search(r'<script[^>]*\bsrc\s*=|<iframe\b|<base\b|<form[^>]*\baction\s*=', html, re.I),
         'active third-party resource/submit endpoint')
    need(not re.search(r'\b(?:https?:)?//[^\s"\']+\.(?:js|css)', html, re.I),
         'external script/style dependency')


def offline_preview(html: str, *, widths=WIDTHS, browser_type=None) -> dict:
    """Ephemeral synthetic-input checks. Every potentially external request is blocked.

    Network attempts are recorded without request bodies/headers or personal values.
    Exits hard-hold on ANY error; no real personal information is ever supplied.
    """
    valid_card(html)
    from playwright.sync_api import sync_playwright
    checks = []
    with tempfile.TemporaryDirectory(prefix='fv-r166-local-') as tmp:
        path = Path(tmp) / 'review-only.html'
        path.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                        '<meta name="viewport" content="width=device-width,initial-scale=1">'
                        '</head><body><main class="pa-article"><div class="pa-shell">'
                        '<div class="pa-body">'+html+'</div></div></main></body></html>', encoding='utf-8')
        with sync_playwright() as pw:
            engine = browser_type or pw.chromium
            need(bool(shutil.which('chromium') or shutil.which('chromium-browser')), 'Chromium executable unavailable')
            browser = engine.launch(headless=True, executable_path=shutil.which('chromium') or shutil.which('chromium-browser'), args=['--no-sandbox'])
            try:
                for width in widths:
                    external = []
                    errors = []
                    context = browser.new_context(viewport={'width': width, 'height': 900},
                                                  service_workers='block', accept_downloads=False)
                    try:
                        page = context.new_page()
                        def route_handler(route):
                            scheme = urlsplit(route.request.url).scheme.lower()
                            if scheme not in ('file', 'data', 'about'):
                                external.append(scheme)
                                route.abort()
                            else:
                                route.continue_()
                        page.route('**/*', route_handler)
                        page.on('pageerror', lambda exc: errors.append(type(exc).__name__))
                        page.set_content(path.read_text(encoding='utf-8'), wait_until='load')
                        need(not errors, 'script error during page load')
                        need(page.locator('#rc-live').evaluate('(e) => !e.hidden'), 'preview did not initialize')
                        need(page.locator('#rc-print').is_visible(), 'print control unavailable')
                        need(page.locator('#rc-reset').is_visible(), 'clear control unavailable')
                        need(page.locator('#rc input[name]').count() == 0, 'named data fields')
                        page.locator('#rc-outName').fill(SENTINEL)
                        page.locator('#rc-school').fill('Synthetic School Name')
                        page.locator('#rc-careName').fill('Synthetic Caregiver')
                        page.locator('#rc-meet2').fill('Synthetic Second Place')
                        need(SENTINEL[:24] in page.locator('#rc-preview').inner_text(),
                             'contact did not render in preview')
                        page.locator('#rc-minimal').check()
                        page.locator('#rc-copies').select_option('4')
                        need(page.locator('#rc-sheet .pa-foldcard').count() == 4,
                             'print copies not reflected')
                        card_text = page.locator('#rc-sheet').inner_text()
                        for private in ('Synthetic School Name','Synthetic Caregiver', 'Synthetic Second Place'):
                            need(private not in card_text and private not in page.locator('#rc-preview').inner_text(),
                                 'minimal card retains private field')
                        page.emulate_media(media='print')
                        display = page.locator('#rc-sheet').evaluate('(e) => getComputedStyle(e).display')
                        need(display != 'none', 'print sheet invisible in print media')
                        need(page.locator('#rc').evaluate('(e) => getComputedStyle(e).display') == 'none',
                             'data entry form leaked into print')
                        page.emulate_media(media='screen')
                        page.locator('#rc-reset').click()
                        need(all(page.locator('#rc-'+k).input_value() == '' for k in FORM_FIELDS),
                             'clear did not wipe card fields')
                        need(not page.locator('#rc-minimal').is_checked() and page.locator('#rc-copies').input_value() == '1',
                             'clear failed to reset control states')
                        need(SENTINEL[:24] not in page.locator('#rc-sheet').inner_text(),
                             'clear retained sentinel in printed preview')
                        persisted = page.evaluate('''() => {
                            let local=0,session=0;
                            try{local=localStorage.length}catch(e){}
                            try{session=sessionStorage.length}catch(e){}
                            return {local,session};}''')
                        need(persisted == {'local':0,'session':0}, 'browser storage populated')
                        need(not external, 'external network request attempted')
                        need(page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1'),
                             'horizontal viewport overflow detected')
                        need(not errors, 'uncaught browser exception')
                        checks.append({'viewport':width,'status':'OFFLINE_DOM_ONLY_PASS',
                                       'external_attempts':len(external),'synthetic_fields_cleared':len(FORM_FIELDS)})
                    finally:
                        context.close()
            finally:
                browser.close()
    return {'schema':SCHEMA, 'state':'DRAFT_HARD_HOLD', 'local_chromium_preflight':checks,
            'real_wordpress_runtime_test':False,'privacy_verified':False,
            'source_review_pass':False,'independent_qd_pass':False,
            'publication_authorized':False,'paid_cta_authorized':False}


def authentic(root: Path) -> dict:
    import sys
    path = root / 'preparedness' / 'tools'
    sys.path.insert(0, str(path))
    import r165_inline_dependency_custody as old
    prior = old.audit(root)
    need(prior.get('state') == 'DRAFT_HARD_HOLD', 'R165 source custody did not pass')
    template = (root / old.STAGED).read_text(encoding='utf-8')
    scripts = {n: (path / n).read_text(encoding='utf-8') for n in old.EXPECTED}
    html, expanded = old.expand_checked(template, scripts)
    need(expanded.get('expanded_sha256') == prior.get('expanded_sha256'),
         'expanded script identity changed')
    return {**offline_preview(html), 'r165_dependency_hash':expanded['expanded_sha256'],
            'complete_source_custody_checked':True}


def main(argv=None) -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path('.'))
    p.add_argument('--report', type=Path, default=None)
    opts=p.parse_args(argv)
    try:
        report=authentic(opts.repo.resolve(strict=True))
    except Exception as exc:  # browser missing or any inconclusive probe => hard hold
        report={'schema':SCHEMA,'state':'INVALID_HARD_HOLD',
                'reason':type(exc).__name__+': '+str(exc)[:250],
                'publication_authorized':False,'privacy_verified':False}
    result=json.dumps(report,sort_keys=True)
    if opts.report:
        opts.report.write_text(result+'\n', encoding='utf-8')
    print(result)
    return 2  # even a passing local browser test does not grant release

if __name__=='__main__':
    raise SystemExit(main())
