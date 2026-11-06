#!/usr/bin/env python3
"""Chromium review of source embedded in the exact five-step FV Playground Blueprint.

This is extracted-source evidence, NOT WordPress/Assembler staging, WCAG
certification, live production, native zoom, or verified Jetpack delivery.
No remote writes, subscriptions, telemetry, or publishing occur.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
from playwright.sync_api import sync_playwright

CHAPTERS = ('fv-hf-title', 'fv-hf-chronicle', 'fv-hf-evidence',
            'fv-hf-inquiry', 'fv-hf-method-title', 'fv-hf-observer', 'fv-hf-mind-title')
WIDTHS = (320, 360, 390, 768, 1440, 1920)


def extract_blueprint(raw: bytes):
    bp = json.loads(raw)
    if len(bp.get('steps', [])) != 5:
        raise ValueError('Expected the five-step integrated Blueprint')
    theme = bp['steps'][0]
    if theme.get('step') != 'installTheme' or theme.get('options', {}).get('targetFolderName') != 'assembler':
        raise ValueError('Pinned Assembler directory admission failed')
    step = bp['steps'][2]
    if step.get('step') != 'writeFile' or step.get('path') != '/wordpress/wp-content/mu-plugins/fv-ex2-playground-review.php':
        raise ValueError('Expected sealed isolated-review MU-plugin')
    plugin = step['data']
    if "if (get_option('fv_ex2_playground_review_only', '') !== 'FV_EX2_LOCAL_PLAYGROUND_2026_11_05_V1')" not in plugin:
        raise ValueError('Accidental-copy fence absent')

    def region(tag):
        match = re.search(r"<<<'" + re.escape(tag) + r"'\n(.*?)\n" + re.escape(tag) + r"(?:;)?\n", plugin, re.S)
        if not match or len(match.group(1)) < 100:
            raise ValueError('Missing or truncated actual source: ' + tag)
        return match.group(1)

    css, js, markup = [region(tag) for tag in ('FVPG_CSS_END', 'FVPG_JS_END', 'FVPG_HTML_END')]
    if markup.count('class="fv-margin-strip__item"') != 72:
        raise ValueError('Missing public Margins items')
    for chapter in CHAPTERS:
        if markup.count('id="' + chapter + '"') != 1:
            raise ValueError('Missing or duplicate chapter: ' + chapter)
    if markup.count('<img ') != 2 or '<main>' in markup:
        raise ValueError('Image/WordPress nested main source mismatch')
    if 'https://finalvestige.com/focus/' not in markup:
        raise ValueError('Free Focus path missing')
    if 'wp:jetpack/subscriptions' in markup or '<script' in markup.lower():
        raise ValueError('Unexpected subscription or executable code in markup')
    return css, js, markup


def build_preview(css, js, markup):
    if '</style' in css.lower() or '</script' in js.lower():
        raise ValueError('Unsafe inline tag terminator in extracted assets')
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="robots" content="noindex,nofollow,noarchive">'
            '<title>FV — extracted source only — NOT WordPress staging</title>'
            '<style>' + css + '</style></head><body>' + markup + '<script>' + js + '</script></body></html>')


def run_probe(blueprint: Path, output: Path, expected_sha: str, axe_path: Path | None):
    raw = blueprint.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha and digest.lower() != expected_sha.lower():
        raise ValueError('Blueprint SHA-256 does not match supplied exact source')
    css, js, markup = extract_blueprint(raw)
    output.mkdir(parents=True, exist_ok=True)
    preview = output / 'EXTRACTED-SOURCE-NOT-WORDPRESS.html'
    preview.write_text(build_preview(css, js, markup), encoding='utf-8')
    report = {'scope': 'EXTRACTED_SOURCE_NOT_WORDPRESS_ASSEMBLER_STAGING',
              'source_sha256': digest, 'source_path': str(blueprint),
              'html_bytes': len(markup.encode()), 'css_bytes': len(css.encode()),
              'js_bytes': len(js.encode()), 'actual_wp_render': False,
              'jetpack_signup_verified': False, 'native_zoom_tested': False,
              'field_cwv_measured': False, 'axe_available': bool(axe_path and axe_path.is_file()),
              'viewports': [], 'release_qualified': False}
    with sync_playwright() as pw:
        binary = shutil.which('chromium') or shutil.which('chromium-browser')
        browser = pw.chromium.launch(headless=True, executable_path=binary,
                                     args=['--no-sandbox'] if binary else [])
        for width in WIDTHS:
            for javascript, reduced in ((True, False), (False, True)):
                context = browser.new_context(viewport={'width': width, 'height': 850},
                                              device_scale_factor=1, java_script_enabled=javascript,
                                              reduced_motion='reduce' if reduced else 'no-preference')
                page = context.new_page()
                broken = []
                page.on('requestfailed', lambda request: broken.append({'url': request.url, 'error': request.failure}))
                page.set_content(preview.read_text(encoding='utf-8'), wait_until='domcontentloaded', timeout=30000)
                page.wait_for_timeout(500)
                state = page.evaluate('''() => ({
                  chapters: ['fv-hf-title','fv-hf-chronicle','fv-hf-evidence','fv-hf-inquiry','fv-hf-method-title','fv-hf-observer','fv-hf-mind-title'].map(id => ({id, present: !!document.getElementById(id)})),
                  marginCount: document.querySelectorAll('.fv-margin-strip__item').length,
                  visibleMarginCount: [...document.querySelectorAll('.fv-margin-strip__item')].filter(x => {const r=x.getBoundingClientRect(),s=getComputedStyle(x); return r.width>0 && r.height>0 && s.visibility!=='hidden' && s.display!=='none' && +s.opacity>0}).length,
                  horizontalOverflow: document.documentElement.scrollWidth > innerWidth + 2,
                  focusLinks: [...document.querySelectorAll('a[href="https://finalvestige.com/focus/"]')].map(x=>({text:x.textContent.trim().slice(0,80), h: Math.round(x.getBoundingClientRect().height), inFirstScreen:x.getBoundingClientRect().top < innerHeight && x.getBoundingClientRect().bottom > 0})),
                  images: [...document.querySelectorAll('img')].map(x=>({src: x.getAttribute('src'), selected: x.currentSrc, srcset:x.getAttribute('srcset'), complete:x.complete, decoded:x.naturalWidth>0, width:x.naturalWidth, height:x.naturalHeight}))
                })''')
                shot = f'home_{width}_{"js" if javascript else "nojs_reduced"}.png'
                page.screenshot(path=str(output / shot), full_page=False)
                state.update({'width': width, 'javascript': javascript,
                              'reduced_motion': reduced, 'screenshot': shot,
                              'failed_requests': broken[:15]})
                if axe_path and axe_path.is_file():
                    page.add_script_tag(path=str(axe_path))
                    state['axe'] = page.evaluate('''async () => { if(!window.axe) return {error:'axe unavailable'}; const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}});return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),incomplete:r.incomplete.length} }''')
                else:
                    state['axe'] = {'status': 'NOT RUN - fail closed'}
                report['viewports'].append(state)
                context.close()
        browser.close()
    (output / 'evidence.json').write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('blueprint', type=Path, help='Exact private GitHub Blueprint downloaded locally')
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--expected-sha256', default='')
    p.add_argument('--axe-core', type=Path, default=None, help='Locally installed official axe-core JS; absence is a HOLD')
    a = p.parse_args()
    try:
        result = run_probe(a.blueprint, a.output, a.expected_sha256, a.axe_core)
    except Exception as exc:
        p.exit(2, 'EXACT BLUEPRINT REVIEW FAIL: ' + str(exc) + '\n')
    print(json.dumps({'source_sha256': result['source_sha256'], 'scenarios': len(result['viewports']), 'output': str(a.output),
                      'release_qualified': False, 'qualification': 'HOLD — not actual WordPress or axe if unavailable'}))


if __name__ == '__main__':
    main()
