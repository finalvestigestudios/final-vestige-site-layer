#!/usr/bin/env python3
"""Offline-only Gutenberg Page 6 single-block replacement preview. Never writes to WordPress."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

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


# Published WordPress Page 6 uses a root-relative /focus/ native CTA. Never
# require an absolute URL that appears only inside the replaceable flagship:
# that falsely blocks the real page while allowing unrelated links as proof.
class NativeFocusParser(HTMLParser):
    """Interpret actual attribute names, not regex suffix matches like data-href."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth = 0
        self.active_depth = None
        self.focus_sections = 0
        self.actions = []
        self.invalid = False

    def handle_starttag(self, tag, attrs):
        names = [name for name, _ in attrs]
        amap = dict(attrs)
        if tag == 'section':
            self.depth += 1
            if 'fv-focus-cta' in (amap.get('class') or '').split():
                self.focus_sections += 1
                if self.active_depth is not None:
                    self.invalid = True
                self.active_depth = self.depth
                if names.count('class') != 1:
                    self.invalid = True
        if tag == 'a' and self.active_depth is not None:
            if 'fv-focus-cta__button' in (amap.get('class') or '').split():
                if (names.count('class') != 1 or names.count('href') != 1
                        or any(name.startswith('on') for name in names)):
                    self.invalid = True
                self.actions.append(amap.get('href'))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag == 'section':
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == 'section':
            if self.active_depth == self.depth:
                self.active_depth = None
            self.depth -= 1
            if self.depth < 0:
                self.invalid = True


def native_focus_action(outside: str) -> str:
    """Fail closed on actual native button href, including attribute spoofing."""
    parser = NativeFocusParser()
    parser.feed(outside)
    parser.close()
    if parser.invalid or parser.focus_sections != 1 or len(parser.actions) != 1:
        raise AdmissionError('native Focus section/button missing, duplicated, or unsafe')
    href = parser.actions[0]
    if not isinstance(href, str):
        raise AdmissionError('native Focus button href is missing')
    parsed = urlsplit(href)
    if (parsed.path != '/focus/' or parsed.query or parsed.fragment or parsed.username
            or parsed.password or (parsed.scheme, parsed.netloc) not in
            (('', ''), ('https', 'finalvestige.com')) or href.startswith('//')):
        raise AdmissionError('native Focus button has an unapproved destination')
    return href

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
    # Assembler supplies site-level branding and navigation. The source masthead
    # duplicates that navigation in WordPress, pushing evidence below the fold.
    # Preserve its original Focus action in a small, independent resource rail.
    mastheads = list(re.finditer(r'<header class="fv-hf__masthead">.*?</header>', content, re.S))
    if len(mastheads) != 1:
        raise AdmissionError('expected exactly one isolated source masthead')
    masthead = mastheads[0]
    source_ctas = re.findall(r'<a class="fv-hf__mast-cta" href="https://finalvestige.com/focus/">.*?</a>', masthead.group(), re.S)
    if len(source_ctas) != 1:
        raise AdmissionError('source masthead Focus link missing or duplicated')
    focus_rail = ('<div class="fv-hf__focus-rail" aria-label="Free reader resource">'
                  + source_ctas[0] + '</div>')
    content = content[:masthead.start()] + focus_rail + content[masthead.end():]
    if content.count('<div class="fv-hf" data-fv-home-flagship') != 1:
        raise AdmissionError('expected exactly one original flagship wrapper')
    content = content.replace('<div class="fv-hf" data-fv-home-flagship',
                              '<div class="fv-hf fv-hf--wp-integrated" data-fv-home-flagship', 1)
    # Keep all three original art-direction choices for founder review.
    # The Focus link remains accessible if optional JavaScript is disabled.
    replacements = [
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
    styles = ["""/* WordPress/Assembler integration-only rail; original sources untouched. */
.fv-hf--wp-integrated .fv-hf__studio-note{display:none}
.fv-hf--wp-integrated .fv-hf__studio{min-height:0;padding-block:6px}
.fv-hf--wp-integrated .fv-hf__focus-rail{display:flex;justify-content:flex-end;
  padding:8px clamp(18px,4vw,72px);background:#101a19;border-bottom:1px solid #50432d}
.fv-hf--wp-integrated .fv-hf__focus-rail .fv-hf__mast-cta{min-height:44px;
  max-width:100%;padding:10px 18px;white-space:normal;text-align:center}
@media(max-width:560px){
  .fv-hf--wp-integrated .fv-hf__focus-rail{padding:7px 18px}
  .fv-hf--wp-integrated .fv-hf__focus-rail .fv-hf__mast-cta{width:100%}
}
/* WCAG 2.2 2.5.8 target-custody improvement for integrated preview only.
   Leave inline citations, original standalone sources and theme controls alone. */
.fv-hf--wp-integrated :is(
  .fv-hf__opening-actions > .fv-hf__text-link,
  .fv-hf__folio-bottomline > a,
  .fv-hf__opening-foot > a,
  .fv-hf__index-note > a,
  .fv-hf__case-actions > .fv-hf__text-link,
  .fv-hf__case-source > a,
  .fv-hf__method > a,
  .fv-hf__inquiry-sources > a,
  .fv-hf__observer-context a,
  .fv-hf__observer-exit > a,
  .fv-hf__mind-actions > a,
  .fv-hf__exit > a,
  .fv-hf__footer > a,
  .fv-hf__chronicle-sources > a
){display:inline-flex;align-items:center;min-height:28px;max-width:100%;white-space:normal;overflow-wrap:anywhere}
.fv-hf--wp-integrated .fv-hf__case-source > a{display:flex}
.fv-hf--wp-integrated .fv-hf__case-actions summary{min-height:44px;padding-block:11px;box-sizing:border-box}
"""]
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
    focus_href = native_focus_action(outside)
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
        'native_focus_destination': focus_href,
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
