#!/usr/bin/env python3
"""Fail-closed STATIC review gate for quarantined Family Card; never a safety/QD pass.

This is a pre-browser contract, NOT runtime network/privacy, printing or medical verification.
The built template includes unresolved inline-js placeholders; browser tests remain mandatory.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

SCHEMA = 'fv-preparedness-r164-family-browser-contract-v1'
STAGED = 'preparedness/review/r163/family-reunification-card.body.html'
STAGED_BLOB = '1b8a340c69b28280ae485a667da4564d9e849d70'
FIELDS = {
    'rc-hhName': ('text', 24), 'rc-hhPhone': ('tel', 24),
    'rc-outName': ('text', 24), 'rc-outPhone': ('tel', 24),
    'rc-meet1': ('text', 32), 'rc-meet2': ('text', 32),
    'rc-school': ('text', 32), 'rc-schoolPlan': ('text', 44),
    'rc-pickup': ('text', 44), 'rc-careName': ('text', 24),
    'rc-carePhone': ('tel', 24), 'rc-access': ('text', 44),
    'rc-reviewed': ('date', None),
}
OTHER_CONTROLS = {'rc-minimal': 'checkbox', 'rc-copies': 'select'}
IDS_REQUIRED = {'rc', 'rc-help', 'rc-warn', 'rc-live', 'rc-preview', 'rc-sheet',
                'rc-print', 'rc-reset', 'rc-meet1-h', 'rc-schoolPlan-h',
                'rc-pickup-h', 'rc-access-h'}
PLACEHOLDERS = {'{{inline-js:shelter_common.js}}', '{{inline-js:reunion_card.js}}'}
# Static red flags; matching is conservative and creates a reviewer block, not proof of exfiltration.
RISK = re.compile(
    r'(?:fetch\s*\(|sendBeacon\s*\(|XMLHttpRequest\b|WebSocket\b|EventSource\b|'
    r'localStorage\b|sessionStorage\b|indexedDB\b|document\.cookie\b|'
    r'window\.location\s*=|document\.location\s*=|postMessage\s*\(|'
    r'FormData\s*\(|navigator\.serviceWorker\b|eval\s*\(|'
    r'innerHTML\s*=|outerHTML\s*=|insertAdjacentHTML\s*\(|document\.write\s*\(|'
    r'new\s+Image\s*\(|\.ajax\s*\(|\$\.post\s*\(|\$\.get\s*\()', re.I)
URL_CSS = re.compile(r'@import\b|url\s*\(\s*[\'\"]?\s*(?:https?:|//|data:)', re.I)
UNSAFE_CLAIM = re.compile(r'\b(?:never\s+(?:stored|transmitted|saved)|guaranteed\s+private|'
                          r'no\s+data\s+(?:ever\s+)?(?:stored|transmitted)|'
                          r'cannot\s+be\s+accessed\s+by\s+anyone)\b', re.I)


def need(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


class ContractParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids: dict[str, tuple[str, dict]] = {}
        self.labels: set[str] = set()
        self.forms: list[dict] = []
        self.tags: list[tuple[str, dict]] = []
        self.errors: list[str] = []
        self.in_form = False
        self.form_controls: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        keys = [k for k, _ in attrs]
        if len(keys) != len(set(keys)):
            self.errors.append('duplicate HTML attributes: '+tag)
        a = dict(attrs)
        self.tags.append((tag, a))
        ident = a.get('id')
        if ident:
            if ident in self.ids:
                self.errors.append('duplicate HTML ID: '+ident)
            self.ids[ident] = (tag, a)
        if tag == 'label' and a.get('for'):
            self.labels.add(a['for'])
        if tag == 'form':
            if self.in_form:
                self.errors.append('nested form')
            self.in_form = True
            self.forms.append(a)
        elif self.in_form and tag in {'input', 'select', 'textarea', 'button'}:
            if ident:
                self.form_controls.add(ident)
        if tag in {'input', 'select', 'textarea', 'button'} and not self.in_form:
            self.errors.append('unexpected control outside card form: '+tag)
        if tag in {'input', 'select', 'textarea'} and ('name' in a or 'required' in a):
            self.errors.append('named/required personal field: '+tag)
        if tag == 'button' and a.get('type') != 'button':
            self.errors.append('nonbutton type may submit')
        for k, val in attrs:
            if k.startswith('on') and not (tag == 'form' and k == 'onsubmit' and val == 'return false'):
                self.errors.append('new inline event handler: '+tag+'.'+k)
            if k in {'src', 'srcset', 'formaction', 'action', 'ping'} and val:
                self.errors.append('navigation/data endpoint attribute: '+tag+'.'+k)
            if k == 'contenteditable' and (val or '').lower() != 'false':
                self.errors.append('unexpected editable element')
        if tag in {'iframe', 'object', 'embed', 'video', 'audio', 'base', 'meta'}:
            self.errors.append('active/embedded element: '+tag)

    def handle_endtag(self, tag: str) -> None:
        if tag == 'form':
            self.in_form = False


def check_html(html: str) -> dict:
    need(isinstance(html, str) and len(html) > 500, 'missing substantive card content')
    parser = ContractParser()
    parser.feed(html)
    parser.close()
    need(not parser.errors, '; '.join(parser.errors))
    need(len(parser.forms) == 1 and parser.forms[0].get('id') == 'rc', 'one expected card form required')
    form = parser.forms[0]
    need(form.get('onsubmit') == 'return false', 'form submission not disabled')
    need(not any(k in form for k in ('method', 'action', 'target', 'enctype', 'novalidate')), 'unexpected form submission options')
    need(IDS_REQUIRED.issubset(parser.ids), 'critical form/print/clear/live id missing')
    controls = set(FIELDS) | set(OTHER_CONTROLS) | {'rc-print', 'rc-reset'}
    need(parser.form_controls == controls, 'unexpected or missing card controls')
    for ident, (kind, maximum) in FIELDS.items():
        tag, attrs = parser.ids[ident]
        need(tag == 'input' and attrs.get('type') == kind, 'field type changed: '+ident)
        need(ident in parser.labels, 'missing form label: '+ident)
        need('name' not in attrs and 'form' not in attrs and 'value' not in attrs, 'serializable/prefilled field: '+ident)
        if maximum is not None:
            need(attrs.get('maxlength') == str(maximum) and attrs.get('autocomplete') == 'off', 'length/autocomplete changed: '+ident)
        need(attrs.get('required') is None, 'mandatory personal input: '+ident)
    for ident, kind in OTHER_CONTROLS.items():
        tag, attrs = parser.ids[ident]
        need(tag == ('select' if kind == 'select' else 'input'), 'control tag changed: '+ident)
        if kind == 'checkbox':
            need(attrs.get('type') == 'checkbox', 'minimal mode changed')
        need(ident in parser.labels, 'control label missing: '+ident)
    for ident in ('rc-print', 'rc-reset'):
        tag, attrs = parser.ids[ident]
        need(tag == 'button' and attrs.get('type') == 'button', 'print/clear button may submit: '+ident)
        need('hidden' in attrs, 'interactive control shown before initialization: '+ident)
    need(parser.ids['rc-warn'][1].get('aria-live') == 'polite', 'warning live region disabled')
    need('hidden' in parser.ids['rc-live'][1], 'preview enabled without initialization')
    need(len(re.findall(r'<noscript\b', html, re.I)) >= 2, 'no-JavaScript paper fallback missing')
    need('A printed card can be lost' in html and 'Do not put a child\'s full name' in html,
         'critical printed-card privacy warning missing')
    need('Every field is optional' in html and 'minimal version' in html.lower(), 'optional/minimal access missing')
    need('form.reset(); render();' in html and "window.print();" in html, 'print/clear behavior changed')
    need('document.createTextNode(r.v)' in html and 'e.textContent = text' in html,
         'text-only display sink removed')
    need(not RISK.search(html), 'potential browser state/network/executable sink requires manual review')
    need(not URL_CSS.search(html), 'potential external CSS resource requires manual review')
    need(not UNSAFE_CLAIM.search(html), 'absolute privacy assertion requires substantiation')
    found = set(re.findall(r'\{\{inline-js:[^{}]+\}\}', html))
    need(found == PLACEHOLDERS, 'inline script dependencies changed')
    need(not re.search(r'<script\b[^>]*\bsrc\s*=', html, re.I), 'script remote dependency')
    need('{{cite:shelter-cdc-reunification}}' in html and '{{cite:shelter-ncmec-hotline}}' in html,
         'source identity lost')
    return {
        'schema': SCHEMA,
        'state': 'DRAFT_HARD_HOLD',
        'controls_checked': len(controls),
        'source_safety_scope': 'STATIC_PREVIEW_ONLY',
        'external_template_dependencies_unexpanded': sorted(PLACEHOLDERS),
        'script_runtime_inspected': False,
        'network_privacy_verified': False,
        'browser_print_verified': False,
        'mobile_a11y_verified': False,
        'independent_safety_review': False,
        'publication_authorized': False,
        'paid_offer_verified': False,
    }


def audit(root: Path) -> dict:
    import sys
    sys.path.insert(0, str(root / 'preparedness' / 'tools'))
    import r163_family_scope_reconciliation as prior
    prev = prior.audit(root)
    need(prev.get('state') == 'DRAFT_HARD_HOLD', 'upstream 35-article/source custody not authenticated')
    staged = root / STAGED
    need(staged.is_file() and not staged.is_symlink(), 'staged html missing/linked')
    raw = staged.read_bytes()
    need(git_blob(raw) == STAGED_BLOB, 'staged original changed')
    report = check_html(raw.decode('utf-8'))
    report['staged_git_blob'] = STAGED_BLOB
    report['original_35_articles'] = 'UPSTREAM_R163_CUSTODY_CHECKED_DRAFT_HOLD'
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, default=Path('.'))
    opts = p.parse_args(argv)
    try:
        result = audit(opts.repo.resolve(strict=True))
    except (ValueError, OSError, UnicodeError, ImportError, KeyError, TypeError) as e:
        result = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
                  'reason': str(e), 'publication_authorized': False}
    print(json.dumps(result, sort_keys=True))
    return 2  # structural pass is never source, safety, privacy, or release approval


if __name__ == '__main__':
    raise SystemExit(main())
