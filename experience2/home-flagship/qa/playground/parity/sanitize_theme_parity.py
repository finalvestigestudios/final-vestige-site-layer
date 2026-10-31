#!/usr/bin/env python3
"""Prepare *public theme presentation only* for an isolated FV local WordPress.

Never retrieves or mutates WordPress data. Accepts a manually supplied read-only
snapshot and emits a script-free subset suitable for the local-only importer.
The original source snapshot must NOT be committed or bundled: it may include
production analytics identifiers and executable tracking JavaScript.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

BLOCK = re.compile(r'<!--\s*wp:html\s*-->(.*?)<!--\s*/wp:html\s*-->', re.I | re.S)
STYLE = re.compile(r'<style(?:\s+id=[\'\"][\w-]{1,64}[\'\"])?\s*>(.*?)</style\s*>', re.I | re.S)
DANGEROUS = re.compile(
    r'<\s*(?:script|iframe|object|embed|form|link|meta)\b|'
    r'\bon[a-z]{3,}\s*=|\bjavascript\s*:|\bdata\s*:\s*text/html|'
    r'<!--\s*wp:(?:shortcode|jetpack/)\b|'
    r'\b(?:posthog|googletagmanager|googletag|gtag\s*\(|dataLayer|phc_[A-Za-z0-9_]+)\b',
    re.I)
REMOTE_CSS = re.compile(r'@import\b|url\s*\(\s*[\'\"]?\s*(?:https?:|//|javascript:)', re.I)
EMAIL = re.compile(r'\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b', re.I)
MARKUP_IDS = {
    'page': 'assembler//page',
    'header': 'assembler//header',
    'footer': 'assembler//footer',
    'overlay': 'assembler//fv-archive-index-overlay',
}


def digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def safe_css(css: str) -> str:
    if not isinstance(css, str) or len(css) > 120_000 or '<' in css or REMOTE_CSS.search(css):
        raise ValueError('CSS contains markup, external requests or exceeds limit')
    if DANGEROUS.search(css):
        raise ValueError('CSS contains dangerous active content')
    return css


def safe_markup(raw: str) -> tuple[str, int]:
    if not isinstance(raw, str) or not 100 <= len(raw) <= 100_000:
        raise ValueError('Missing/implausible public template markup')
    removed = 0

    def sanitize_html_block(match: re.Match) -> str:
        nonlocal removed
        body = match.group(1)
        styles = list(STYLE.finditer(body))
        keep = []
        for style in styles:
            # Recreate each style tag without carrying untrusted attributes.
            keep.append('<style>' + safe_css(style.group(1)) + '</style>')
        # Strip every non-style fragment, including script and telemetry.
        remainder = STYLE.sub('', body).strip()
        if remainder:
            removed += 1
        if not keep:
            return '<!-- FV local parity: non-style custom HTML intentionally omitted -->'
        return '<!-- wp:html -->' + ''.join(keep) + '<!-- /wp:html -->'

    cleaned = BLOCK.sub(sanitize_html_block, raw)
    # A malformed/missing html closing comment must fail closed, not pass through.
    if DANGEROUS.search(cleaned) or EMAIL.search(cleaned):
        raise ValueError('Unsafe dynamic markup or personal/executable content remains')
    if len(re.findall(r'<!--\s*wp:html\s*-->', cleaned, re.I)) != len(re.findall(r'<!--\s*/wp:html\s*-->', cleaned, re.I)):
        raise ValueError('Unmatched custom HTML block')
    if '<script' in cleaned.lower() or 'token=' in cleaned.lower():
        raise ValueError('Script or token marker remains')
    return cleaned, removed


def prepare(snapshot: dict) -> tuple[dict, dict]:
    if set(snapshot) != {'site', 'theme', 'templates', 'global_styles'}:
        raise ValueError('Only explicitly allowlisted public presentation fields accepted')
    if snapshot['site'] != 'https://finalvestige.com':
        raise ValueError('Wrong source site')
    theme = snapshot['theme']
    if theme != {'stylesheet': 'assembler', 'version': '0.0.126'}:
        raise ValueError('Theme/version mismatch: re-review before preparing staging parity')
    templates = snapshot['templates']
    if set(templates) != set(MARKUP_IDS):
        raise ValueError('Expected page/header/footer/navigation-overlay snapshot only')
    result = {}
    hashes = {}
    removed = {}
    for name, expected_id in MARKUP_IDS.items():
        src = templates[name]
        if set(src) != {'id', 'content'} or src['id'] != expected_id:
            raise ValueError('Unexpected template ID or snapshot fields')
        result[name], removed[name] = safe_markup(src['content'])
        hashes[name] = digest(src['content'])
    styles = snapshot['global_styles']
    if set(styles) != {'settings', 'styles'}:
        raise ValueError('Unexpected global-style source fields')
    layout = styles['settings'].get('layout', {})
    if layout != {'contentSize': '760px', 'wideSize': '1440px'}:
        raise ValueError('Unexpected production layout tokens')
    css = safe_css(styles['styles'].get('css', ''))
    if not css:
        raise ValueError('Missing source global styles')
    output = {
        'schema': 'fv-local-assembler-parity-v1', 'release': 'HOLD',
        'source_theme': theme, 'local_only': True,
        'template_content': result,
        'global_styles': {'settings': {'layout': layout}, 'styles': {'css': css}},
    }
    report = {
        'release': 'HOLD', 'origin': 'READ_ONLY_PUBLIC_PRESENTATION',
        'source_site_id': 256784396,
        'source_template_sha256': hashes,
        'source_global_css_sha256': digest(css),
        'omitted_custom_html_blocks': removed,
        'staging_has_production_analytics': False,
        'import_performed': False, 'wordpress_parity_verified': False,
        'requires': ['official Assembler 0.0.126 theme', 'isolated WordPress Playground',
                     'localhost-only import', 'real Chromium/axe/Lighthouse',
                     'production Jetpack and CDN acceptance remain separate'],
    }
    return output, report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, required=True,
                    help='Read-only public presentation snapshot; DO NOT commit input')
    ap.add_argument('--out', type=Path, required=True,
                    help='New private output directory outside checkout')
    args = ap.parse_args()
    if args.out.exists():
        raise SystemExit('Refusing to overwrite existing output directory')
    data = json.loads(args.snapshot.read_text(encoding='utf-8'))
    sanitized, receipt = prepare(data)
    args.out.mkdir(parents=True)
    (args.out/'site-parity.safe.json').write_text(json.dumps(sanitized, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    (args.out/'LOCAL_PARITY_RECEIPT.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'output':str(args.out),'release':'HOLD','removed':receipt['omitted_custom_html_blocks']}))

if __name__ == '__main__':
    main()
