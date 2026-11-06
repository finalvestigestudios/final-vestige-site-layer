#!/usr/bin/env python3
"""R177 safety-critical wording custody for Preparedness draft excerpts.

Structural guard only: no source adjudication, clinician review or QD approval.
Never connects to network, edits repository files, or enables publication.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unicodedata

SCHEMA = 'fv-preparedness-r177-safety-excerpt-custody-v1'
HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
MANIFEST = Path('preparedness/review/r177/safety_contract.json')
CONTRACT_SHA256 = 'bcff23175c09c9e4e54ade74377cadd4bf9604653593a819e6dd31f873c3a700'
ROOT = Path('preparedness/content/articles')
EXPORT = Path('preparedness/build/wp')
SOURCE_RE = re.compile(r'\{\{(?:cite|link):[^}]+\}\}')
DANGEROUS = (
    (r'\b(?:switch|turn|shut)\s+off\s+(?:the\s+|your\s+)?main\s+(?:power|breaker)\s+for\s+', 'positive_main_power_drill'),
    (r'\b(?:switch|turn|shut)\s+off\s+(?:the\s+)?household\s+(?:electricity|power)\s+for\s+', 'positive_house_power_drill'),
    (r'\b(?:discard|throw\s+away)\s+all\s+refrigerated\s+medicines?\s+(?:without|immediately)', 'unqualified_disposal'),
)


def clean(text: str) -> str:
    """Normalize visual text while ignoring original citation-template syntax."""
    text = SOURCE_RE.sub(' ', text)
    text = unicodedata.normalize('NFKC', text).replace('\u00a0', ' ')
    return ' '.join(text.casefold().split())


class TextNodes(HTMLParser):
    """Capture visible HTML text and source-specific block boundaries.

    HTML comments, JS, CSS, template content, and hidden fragments do not
    satisfy a required safety statement. This is NOT a browser CSS audit.
    """
    BLOCKS = frozenset(('li', 'p', 'div'))
    IGNORED = frozenset(('script', 'style', 'template', 'noscript'))
    VOID = frozenset(('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                      'link', 'meta', 'param', 'source', 'track', 'wbr'))

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[dict] = []
        self.nodes: list[dict] = []
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.VOID:
            return
        d = dict(attrs)
        ancestor_hidden = any(node['hidden'] for node in self.stack)
        hidden = (ancestor_hidden or 'hidden' in d or
                  str(d.get('aria-hidden', '')).casefold() == 'true' or
                  bool(re.search(r'display\s*:\s*none|visibility\s*:\s*hidden',
                                 str(d.get('style', '')), re.I)))
        node = {'tag': tag, 'classes': str(d.get('class') or '').split(),
                'hidden': hidden, 'chunks': []}
        self.stack.append(node)
        if tag in self.BLOCKS:
            self.nodes.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        # Void elements contribute no visible text.
        return

    def handle_endtag(self, tag: str) -> None:
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i]['tag'] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data: str) -> None:
        if any(n['tag'] in self.IGNORED or n['hidden'] for n in self.stack):
            return
        self.text.append(data)
        for node in self.stack:
            node['chunks'].append(data)


def inspect_html(html: str, rule: dict) -> list[str]:
    parser = TextNodes()
    parser.feed(html)
    parser.close()
    failures = []
    for section in rule['sections']:
        anchor = clean(section['anchor'])
        candidates = [node for node in parser.nodes
                      if node['tag'] == section['tag'] and
                      (not section.get('class') or section['class'] in node['classes']) and
                      not node['hidden'] and anchor in clean(' '.join(node['chunks']))]
        if len(candidates) != 1:
            failures.append(f"{section['id']}: expected one visible section, found {len(candidates)}")
            continue
        content = clean(' '.join(candidates[0]['chunks']))
        for fragment in section['required']:
            if clean(fragment) not in content:
                failures.append(f"{section['id']}: missing required fragment: {fragment}")
    global_text = clean(' '.join(parser.text))
    for pattern, name in DANGEROUS:
        if re.search(pattern, global_text, re.I):
            failures.append('unsafe wording regression: ' + name)
    return failures


def inspect(repo: Path, check_export: bool = False) -> dict:
    report: dict = {
        'schema': SCHEMA, 'state': INVALID,
        'publication_authorized': False,
        'independent_qd_pass': False,
        'qualified_source_review': False,
        'medical_safety_approved': False,
        'food_safety_approved': False,
        'check_export_requested': check_export,
        'files': [], 'errors': [],
    }
    try:
        manifest_path = repo / MANIFEST
        manifest_bytes = manifest_path.read_bytes()
        if hashlib.sha256(manifest_bytes).hexdigest() != CONTRACT_SHA256:
            raise ValueError('safety contract byte identity changed without reviewed code')
        manifest = json.loads(manifest_bytes.decode('utf-8'))
        if (manifest.get('schema') != SCHEMA or manifest.get('state') != HOLD or
            any(manifest.get(k) is True for k in ('publication_authorized',
                'independent_qd_pass', 'qualified_source_review',
                'medical_safety_approved', 'food_safety_approved'))):
            raise ValueError('invalid review manifest or false approval')
        rules = manifest['articles']
        if not isinstance(rules, list) or len(rules) != 2 or {
                r['slug'] for r in rules} != {'household-emergency-plan', 'three-day-kit'}:
            raise ValueError('required two-article scope missing, duplicated or altered')
        for rule in rules:
            slug = rule['slug']
            if not re.fullmatch('[a-z0-9-]+', slug):
                raise ValueError('malformed article slug')
            for stage, path in [('source', repo / ROOT / (slug + '.body.html')),
                                *([('wordpress_draft', repo / EXPORT / (slug + '.html'))]
                                  if check_export else [])]:
                if not path.is_file() or path.is_symlink() or path.stat().st_size > 8_000_000:
                    report['errors'].append(f'{slug}/{stage}: missing, symlinked or oversize file')
                    continue
                raw = path.read_bytes()
                failures = inspect_html(raw.decode('utf-8'), rule)
                report['errors'].extend(f'{slug}/{stage}: {failure}' for failure in failures)
                report['files'].append({'slug': slug, 'stage': stage,
                                        'sha256': hashlib.sha256(raw).hexdigest(),
                                        'structural_status': 'REVIEW_HOLD' if not failures else 'REJECTED'})
        if not report['errors']:
            report['state'] = HOLD
    except (ValueError, KeyError, TypeError, OSError, UnicodeError) as exc:
        report['errors'].append(type(exc).__name__ + ': ' + str(exc))
    report['review_only'] = True
    report['errors_count'] = len(report['errors'])
    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', default='.')
    p.add_argument('--check-export', action='store_true')
    args = p.parse_args(argv)
    print(json.dumps(inspect(Path(args.repo).resolve(), args.check_export),
                     sort_keys=True, separators=(',', ':')))
    return 2  # ALWAYS hold; never use a green exit to trigger release.


if __name__ == '__main__':
    sys.exit(main())
