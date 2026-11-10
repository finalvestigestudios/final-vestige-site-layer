#!/usr/bin/env python3
"""Offline-only Gutenberg Page 6 single-block replacement preview. Never writes to WordPress."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

HTML_BLOCK = re.compile(r'<!-- wp:html -->(.*?)<!-- /wp:html -->', re.S)
JETPACK = re.compile(r'<!-- wp:jetpack/subscriptions\b[^>]*?/>')
MARGINS = re.compile(r'class=["\'][^"\']*\bfv-margin-strip__item\b')
CHAPTERS = ('fv-hf-title', 'fv-hf-chronicle', 'fv-hf-evidence', 'fv-hf-inquiry',
            'fv-hf-method-title', 'fv-hf-observer', 'fv-hf-mind-title')
CSS = ('flagship.css', 'chronicle.css', 'chronicle-lens.css', 'inquiry.css',
       'observer-lab.css', 'reading-trail.css')
JS = ('flagship.js', 'observer-lab.js', 'chronicle-lens.js', 'reading-trail.js')
PINNED_GIT_BLOBS = {
    'index.html': 'a8f35d163f4e915406ec2597520b13b6b8b45eb0',
    'flagship.css': 'b0979e4c1a05c988aef3097625d81a2dd37c44a2',
    'chronicle.css': 'a779320ef6468b853a65a268502d15a19a9c1b64',
    'chronicle-lens.css': '97fb86e6469c98461f422d4a0a9629e757522146',
    'inquiry.css': '28c747679969374bf1bcda386899cde03197db60',
    'observer-lab.css': 'f01b336fe76470df88c8b748fd13321376f27aa2',
    'reading-trail.css': 'b86f944f25987c5324fdcf01d86b702d54e0de41',
    'flagship.js': '74ebffd83b6d394be8f0e323a1888b5d867bf4e0',
    'observer-lab.js': '9b69d69dc61909d3e802365e47ab5287108efa4e',
    'chronicle-lens.js': 'f22b5e3a4f0dfabfc29e0a9829d56dab4e697df2',
    'reading-trail.js': '3ec89c6f267d6ea8a2698b07fe3fc77d6809d54f',
}

class AdmissionError(ValueError):
    pass

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def stage_payload(source_dir: Path, pin: bool = True) -> str:
    parts = {}
    for filename, expected in PINNED_GIT_BLOBS.items():
        raw = (source_dir / filename).read_bytes()
        if pin and git_blob(raw) != expected:
            raise AdmissionError(f'unexpected source blob for {filename}: {git_blob(raw)} != {expected}')
        parts[filename] = raw.decode('utf-8')
    html = parts['index.html']
    if html.count('<body>') != 1 or html.count('</body>') != 1:
        raise AdmissionError('source does not contain a unique body')
    content = html.split('<body>', 1)[1].split('</body>', 1)[0]
    if content.count('data-fv-home-flagship') != 1:
        raise AdmissionError('source is not one isolated flagship root')
    for chapter in CHAPTERS:
        if content.count(f'id="{chapter}"') != 1:
            raise AdmissionError('missing or duplicate chapter destination ' + chapter)
    # WordPress/Assembler already supplies site-level header/main/footer landmarks.
    # Keep candidate's own chapter navigation and labels, not a nested main/banner.
    replacements = [
        ('<header class="fv-hf__masthead">', '<div class="fv-hf__masthead" role="group" aria-label="Archive navigation">'),
        ('</header>', '</div>'),
        ('<main id="fv-hf-main" tabindex="-1">', '<div id="fv-hf-main" tabindex="-1" role="region" aria-label="The living archive">'),
        ('</main>', '</div>'),
        ('<footer class="fv-hf__footer">', '<div class="fv-hf__footer">'),
        ('</footer>', '</div>'),
    ]
    for old, new in replacements:
        if content.count(old) != 1:
            raise AdmissionError(f'missing or multiple expected structural tags: {old}')
        content = content.replace(old, new, 1)
    if re.search(r'<(?:html|head|body|main|header|footer)(?:\s|>)', content, re.I):
        raise AdmissionError('unexpected document or site-level landmark in scoped payload')
    styles = []
    for filename in CSS:
        body = parts[filename]
        if '</style' in body.lower() or '<!-- /wp:' in body.lower() or re.search(r'@import\b', body):
            raise AdmissionError('unsafe CSS token in ' + filename)
        styles.append('/* source: ' + filename + ' */\n' + body)
    scripts = []
    for filename in JS:
        body = parts[filename]
        if '</script' in body.lower() or '<!-- /wp:' in body.lower():
            raise AdmissionError('unsafe JS token in ' + filename)
        scripts.append('<script data-fv-source="' + filename + '">\n' + body + '\n</script>')
    return ('\n<!-- FVS EX2: OFFLINE REVIEW-ONLY SINGLE-BLOCK COMPOSITION; NOT FOR PUBLICATION -->\n'
            + content.strip() + '\n<style data-fv-source="experience-2.0">\n'
            + '\n'.join(styles) + '\n</style>\n'
            + '\n'.join(scripts) + '\n')

def compose(raw: str, payload: str) -> tuple[str, dict]:
    matches = list(HTML_BLOCK.finditer(raw))
    targets = [m for m in matches if 'data-fv-home-flagship' in m.group(1)]
    if len(targets) != 1:
        raise AdmissionError('must find exactly one existing Gutenberg flagship wp:html block')
    m = targets[0]
    outside = raw[:m.start()] + raw[m.end():]
    if len(matches) < 3 or len(JETPACK.findall(outside)) != 1:
        raise AdmissionError('native Jetpack block missing or unexpectedly inside candidate swap')
    if len(MARGINS.findall(outside)) != 72:
        raise AdmissionError('original 72 Margins not fully outside candidate swap')
    if 'fv-focus-cta' not in outside or 'https://finalvestige.com/focus/' not in outside:
        raise AdmissionError('native external Focus block/destination would be removed')
    for chapter in CHAPTERS:
        if len(re.findall(r'id=["\']'+re.escape(chapter)+r'["\']', outside)):
            raise AdmissionError('chapter destination duplicates outside flagship')
    if len(HTML_BLOCK.findall(payload)) or '<!-- /wp:html -->' in payload:
        raise AdmissionError('candidate payload contains Gutenberg block delimiters')
    if len(re.findall(r'<div\b[^>]*\bdata-fv-home-flagship\b', payload)) != 1:
        raise AdmissionError('candidate must have exactly one flagship root')
    for chapter in CHAPTERS:
        if len(re.findall(r'id=["\']'+re.escape(chapter)+r'["\']', payload)) != 1:
            raise AdmissionError('candidate missing or duplicating chapter '+chapter)
    insertion = '<!-- wp:html -->' + payload + '<!-- /wp:html -->'
    composed = raw[:m.start()] + insertion + raw[m.end():]
    if composed[:m.start()] != raw[:m.start()] or not composed.endswith(raw[m.end():]):
        raise AdmissionError('out-of-scope Gutenberg content changed')
    if len(JETPACK.findall(composed)) != 1 or len(MARGINS.findall(composed)) != 72:
        raise AdmissionError('custody check failed after composition')
    return composed, {
        'release': 'HOLD', 'writes_to_wordpress': False, 'preview_only': True,
        'original_sha256': sha(raw.encode()), 'candidate_sha256': sha(composed.encode()),
        'untouched_prefix_sha256': sha(raw[:m.start()].encode()),
        'untouched_suffix_sha256': sha(raw[m.end():].encode()),
        'untouched_external_bytes': len((raw[:m.start()]+raw[m.end():]).encode()),
        'replaced_flagship_block_bytes': len(m.group(0).encode()),
        'new_flagship_block_bytes': len(insertion.encode()),
        'gutenberg_html_blocks': len(matches), 'margins_retained': 72,
        'native_jetpack_retained': True, 'native_focus_retained': True,
        'chapter_count': 7, 'wp_integration': 'NOT TESTED',
        'conditions': ['Use public-only Page 6 raw editor content',
                       'Never upload this file to production or sync database',
                       'Requires isolated WordPress/Assembler + native Jetpack acceptance',
                       'Requires rights/WCAG/Lighthouse/CI/QD/founder release gates'],
    }

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--page6-raw', required=True, type=Path, help='public-only WP Page 6 context=edit content')
    ap.add_argument('--source-dir', required=True, type=Path)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--receipt', required=True, type=Path)
    ap.add_argument('--expected-page-sha256', default=None)
    args = ap.parse_args()
    raw = args.page6_raw.read_text('utf-8')
    if args.expected_page_sha256 and sha(raw.encode()) != args.expected_page_sha256:
        raise AdmissionError('Page 6 source changed; re-review before staging')
    merged, receipt = compose(raw, stage_payload(args.source_dir))
    args.out.write_text(merged, 'utf-8')
    args.receipt.write_text(json.dumps(receipt, indent=2), 'utf-8')
    print(json.dumps(receipt, indent=2))

if __name__ == '__main__':
    main()
