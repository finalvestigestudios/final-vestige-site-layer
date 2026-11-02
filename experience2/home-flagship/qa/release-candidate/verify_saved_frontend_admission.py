#!/usr/bin/env python3
"""Saved *native Gutenberg page* browser admission in disposable WordPress.

The private iframe is NOT equivalent to a saved WordPress page. Assertions
exercise the real saved draft inside the Assembler wrapper, and require real
axe-core, native keyboard events, responsive integrity and no-JS evidence.
No production CMS, users, subscriber records or secrets are accessed.
"""
from __future__ import annotations
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

CHAPTERS = ('fv-hf-title', 'fv-hf-chronicle', 'fv-hf-evidence', 'fv-hf-inquiry',
            'fv-hf-method-title', 'fv-hf-observer', 'fv-hf-mind-title')
CASES = ('apollo', 'franklin', 'malbone')


def validate_saved_preview(url: str, page_id: int) -> None:
    """Fail closed on production, arbitrary hosts, ports, tokens or wrong drafts."""
    try:
        p = urlsplit(url)
        query = parse_qs(p.query, strict_parsing=True)
        allowed = (p.scheme == 'http' and p.hostname == '127.0.0.1'
                   and p.port == 9400 and p.username is None and p.password is None
                   and p.path == '/' and not p.fragment
                   and type(page_id) is int and page_id > 0
                   and query == {'page_id': [str(page_id)], 'preview': ['true']})
    except (ValueError, TypeError):
        allowed = False
    if not allowed:
        raise ValueError('LOCAL_SAVED_FRONTEND_ORIGIN_REQUIRED')


def require_checks(checks: dict) -> None:
    if not checks or not all(type(value) is bool for value in checks.values()):
        raise ValueError('SAVED_PAGE_CHECKS_NOT_BOOLEAN')
    failures = sorted(k for k, value in checks.items() if not value)
    if failures:
        raise ValueError('SAVED_PAGE_BROWSER_GATE_FAILED:' + ','.join(failures))


def check_saved_frontend(page, page_id: int, axe_source: str, out: Path) -> dict:
    """A real browser page saved through the editor, not an iframe preview."""
    validate_saved_preview(page.url, page_id)
    if not axe_source or len(axe_source) < 100000 or 'axe' not in axe_source:
        raise ValueError('REAL_AXE_CORE_NOT_AVAILABLE')
    root = page.locator('[data-fv-home-flagship]')
    if root.count() != 1:
        raise ValueError('SAVED_PAGE_FLAGSHIP_ROOT_MISSING')
    out.mkdir(parents=True, exist_ok=True)
    report = {'environment': 'DISPOSABLE_LOCAL_WORDPRESS_SAVED_PAGE',
              'checks': {}, 'axe_violations': {}, 'screenshots': [],
              'hosted_wordpress_compatibility': 'NOT_TESTED',
              'manual_assistive_technology': 'NOT_TESTED',
              'production_writes': False}
    for width, height in ((390, 844), (1440, 900)):
        page.set_viewport_size({'width': width, 'height': height})
        page.evaluate('window.scrollTo(0,0)')
        key = str(width)
        report['checks']['viewport_' + key] = page.evaluate('innerWidth') == width
        report['checks']['seven_chapters_' + key] = all(
            page.locator('#' + ident).count() == 1 for ident in CHAPTERS)
        report['checks']['no_document_overflow_' + key] = bool(page.evaluate(
            'document.documentElement.scrollWidth <= innerWidth + 1'))
        report['checks']['three_evidence_cases_' + key] = root.locator('[data-fv-case]').count() == 3
        report['checks']['preserved_fieldbook_' + key] = root.locator(
            'a[href="https://finalvestige.com/focus/"]').count() >= 1
        for case_id in CASES:
            button = root.locator('[data-fv-case-button="' + case_id + '"]')
            panel = root.locator('[data-fv-case="' + case_id + '"]')
            if button.count() != 1 or panel.count() != 1:
                report['checks']['case_' + case_id + '_' + key] = False
                continue
            button.click(timeout=12000)
            report['checks']['case_' + case_id + '_' + key] = (
                button.get_attribute('aria-pressed') == 'true' and panel.is_visible())
            if case_id == 'malbone':
                report['checks']['nypl_image_absent_' + key] = panel.locator('img').count() == 0
                report['checks']['rights_safe_source_plate_' + key] = (
                    panel.locator('.fv-hf__source-plate[role="group"]').count() == 1)
        button = root.locator('[data-fv-case-button="franklin"]')
        button.focus()
        page.keyboard.press('Enter')
        report['checks']['keyboard_enter_' + key] = button.get_attribute('aria-pressed') == 'true'
        # Scope axe to the saved flagship. This is not a claim about WP theme
        # chrome/admin bar and is not manual WCAG 2.2 AA certification.
        page.evaluate(axe_source)
        violations = page.evaluate("""async () => {
          if (!window.axe || typeof window.axe.run !== 'function')
            throw Error('REAL_AXE_NOT_LOADED');
          const root = document.querySelector('[data-fv-home-flagship]');
          const result = await window.axe.run(root, {runOnly:{type:'tag',
            values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});
          return result.violations.map(v => ({id:v.id, impact:v.impact,
                                               count:v.nodes.length}));
        }""")
        report['axe_violations'][key] = violations
        report['checks']['axe_wcag_aa_' + key] = violations == []
        root.locator('[data-fv-case-button="apollo"]').click(timeout=12000)
        page.evaluate('window.scrollTo(0,0)')
        name = 'GUTENBERG_SAVED_AUDITED_' + key + '.png'
        page.screenshot(path=str(out / name), timeout=20000)
        report['screenshots'].append(name)
    # Use the existing disposable editor session for a genuine JavaScript-
    # disabled browser, never a mocked DOM or synthetic private shortcode.
    target_url = page.url
    validate_saved_preview(target_url, page_id)
    context = page.context.browser.new_context(
        storage_state=page.context.storage_state(),
        viewport={'width': 390, 'height': 844},
        java_script_enabled=False, service_workers='block', reduced_motion='reduce')
    try:
        nojs = context.new_page()
        response = nojs.goto(target_url, wait_until='domcontentloaded', timeout=45000)
        report['checks']['saved_nojs_http_200'] = response is not None and response.status == 200
        report['checks']['saved_nojs_root'] = nojs.locator('[data-fv-home-flagship]').count() == 1
        report['checks']['saved_nojs_seven_chapters'] = all(
            nojs.locator('#' + ident).count() == 1 for ident in CHAPTERS)
        report['checks']['saved_nojs_all_cases_visible'] = all(
            nojs.locator('[data-fv-case="' + case_id + '"]').is_visible()
            for case_id in CASES)
        fallback = nojs.locator('img[data-fv-noscript-archive]')
        report['checks']['saved_nojs_two_archives'] = fallback.count() == 2
        if fallback.count() == 2:
            try:
                nojs.wait_for_function("""() => [...document.querySelectorAll(
                  'img[data-fv-noscript-archive]')].every(e =>
                    e.complete && e.naturalWidth > 0 && e.naturalHeight > 0)""",
                    timeout=15000)
                report['checks']['saved_nojs_archives_loaded'] = True
            except Exception:
                report['checks']['saved_nojs_archives_loaded'] = False
        else:
            report['checks']['saved_nojs_archives_loaded'] = False
        report['checks']['saved_nojs_nypl_image_absent'] = (
            nojs.locator('[data-fv-case="malbone"] img').count() == 0)
        nojs.evaluate('window.scrollTo(0,0)')
        nojs.screenshot(path=str(out / 'GUTENBERG_SAVED_NOJS_390.png'),
                        timeout=20000)
        report['screenshots'].append('GUTENBERG_SAVED_NOJS_390.png')
    finally:
        context.close()
    require_checks(report['checks'])
    report['status'] = 'SAVED_PAGE_BROWSER_AXE_INTERACTION_NOJS_PASS_NOT_HOSTED_RELEASE'
    return report
