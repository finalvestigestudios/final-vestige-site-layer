#!/usr/bin/env python3
"""R469 source-only citation visibility custody: fail closed, never grant QD PASS.

Scope is the literal authored HTML and explicit attributes, not computed browser CSS,
JavaScript, PDF accessibility, source accuracy, or medically safe advice.
"""
from __future__ import annotations
import argparse
from dataclasses import dataclass
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import sys

CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
TOKEN_HINT = re.compile(r'\{\{\s*cite\s*:', re.I)
INVISIBLE = frozenset({'script', 'style', 'template', 'noscript', 'svg', 'math',
                       'iframe', 'object', 'canvas', 'head', 'title', 'textarea'})
VOID = frozenset({'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                  'link', 'meta', 'param', 'source', 'track', 'wbr'})
HOLD = 'DRAFT_HARD_HOLD'

class VisibilityHold(ValueError):
    pass

def require(condition, reason):
    if not condition:
        raise VisibilityHold(reason)

def explicitly_hidden(tag, attrs):
    """Conservative literal-attribute classification; no class/CSS inference."""
    vals = {}
    for key, value in attrs:
        key = key.lower()
        require(key not in vals, 'duplicate HTML attribute: ' + key)
        vals[key] = value
    if tag in INVISIBLE:
        return True
    if 'hidden' in vals or 'inert' in vals:
        return True
    aria = (vals.get('aria-hidden') or '').strip().lower()
    if aria == 'true':
        return True
    require(aria in ('', 'false', 'true'), 'ambiguous aria-hidden')
    style = (vals.get('style') or '').lower()
    style = re.sub(r'/\*.*?\*/', '', style, flags=re.S)
    rules = {}
    for declaration in style.split(';'):
        if not declaration.strip():
            continue
        require(':' in declaration, 'malformed inline style declaration')
        name, value = declaration.split(':', 1)
        name, value = name.strip(), value.strip()
        require(name not in rules, 'duplicate CSS inline property')
        rules[name] = value.replace('!important', '').strip()
    if rules.get('display') == 'none' or rules.get('visibility') in ('hidden', 'collapse'):
        return True
    if rules.get('content-visibility') == 'hidden':
        return True
    if rules.get('opacity') in ('0', '0.0', '0%'):
        return True
    # A citation underneath a closed details disclosure is accessible by expansion;
    # it remains a review warning rather than a silent denial or publication PASS.
    return False

@dataclass
class Frame:
    tag: str
    hidden: bool

class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.visible_citations = []
        self.raw_citations = []
        self.held_tokens = []
        self.disclosure_count = 0
        self.all_text = []

    def handle_starttag(self, tag, attrs):
        require(not TOKEN_HINT.search(self.get_starttag_text() or ''),
                'citation token embedded in HTML attributes')
        require(tag not in {'base', 'meta', 'link'},
                'head or route-changing HTML not permitted in article body')
        hidden = explicitly_hidden(tag, attrs) or any(frame.hidden for frame in self.stack)
        if tag == 'details' and not any(k == 'open' for k, _ in attrs):
            self.disclosure_count += 1
        if tag not in VOID:
            self.stack.append(Frame(tag, hidden))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        require(bool(self.stack), 'unmatched closing tag: ' + tag)
        require(self.stack[-1].tag == tag,
                'unbalanced HTML: expected </' + self.stack[-1].tag + '>, got </' + tag + '>')
        self.stack.pop()

    def handle_data(self, data):
        self.all_text.append(data)
        ids = CITE.findall(data)
        self.raw_citations.extend(ids)
        if TOKEN_HINT.search(data) and not ids:
            self.held_tokens.append('malformed citation token')
        if self.stack and self.stack[-1].hidden and (ids or TOKEN_HINT.search(data)):
            self.held_tokens.append('citation in explicitly nonvisible HTML')
        else:
            self.visible_citations.extend(ids)

    def handle_comment(self, data):
        if TOKEN_HINT.search(data):
            self.held_tokens.append('citation in HTML comment')

    def handle_decl(self, decl):
        require(False, 'DOCTYPE and declarations not permitted in article body')

    def handle_entityref(self, name):
        pass

    def finish(self, raw):
        self.close()
        require(not self.stack, 'unclosed HTML tags')
        require(not self.held_tokens, '; '.join(self.held_tokens[:4]))
        literal = CITE.findall(raw)
        require(literal and literal == self.visible_citations,
                'citation count/order/visibility mismatch')
        require(not TOKEN_HINT.search(raw.replace('{{cite:', '')),
                'noncanonical or ambiguous citation token')
        return {'citation_count': len(literal), 'citation_ids': literal,
                'closed_disclosures_review': self.disclosure_count,
                'visibility_model': 'literal_inline_only',
                'computed_css_verified': False, 'browser_verified': False,
                'qualified_qd_pass': False, 'may_publish': False, 'release_state': HOLD}

def audit(body, expected_ids=None):
    require(isinstance(body, str) and bool(body.strip()), 'missing authored article')
    scan = Scan()
    scan.feed(body)
    out = scan.finish(body)
    if expected_ids is not None:
        require(expected_ids == out['citation_ids'], 'R468 citation order witness mismatch')
    return out

def load(path):
    require(path.is_file() and not path.is_symlink(), 'required pinned module unavailable')
    spec = importlib.util.spec_from_file_location('r469_parent', path)
    require(spec is not None and spec.loader is not None, 'module cannot be loaded')
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

def native(root):
    root = root.resolve()
    prior = load(root / 'tools/r468_citation_context_docket.py')
    previous = prior.native(root)
    require(previous['article_count'] == 35 and previous['citation_count'] == 2000,
            'R468 article citation census drift')
    custody = load(root / 'tools/r463_article_citation_use_custody.py')
    snapshot = custody.pinned_json(root, 'audits/R460_ORIGIN_BRANCH_BLOB_SNAPSHOT.json',
                                    custody.SNAPSHOT_BLOB)
    items = []
    for entry in previous['articles']:
        slug = entry['slug']
        pins = snapshot['candidate']['articles'][slug]
        path = f'content/articles/{slug}.body.html'
        body = custody.pinned_bytes(root, path, pins['body'], max_size=180000).decode('utf-8')
        ids = [cite['source_id'] for cite in entry['citation_events']]
        result = audit(body, expected_ids=ids)
        items.append({'slug': slug, 'citation_count': result['citation_count'],
                      'closed_disclosures_review': result['closed_disclosures_review'],
                      'release_state': HOLD, 'qualified_qd_pass': False})
    require(len(items) == 35 and sum(x['citation_count'] for x in items) == 2000,
            'R469 cumulative citation census mismatch')
    return {'state': 'VISIBLE_CITATION_REVIEW_REQUIRED', 'release_state': HOLD,
            'articles': items, 'article_count': 35, 'citation_count': 2000,
            'computed_css_verified': False, 'browser_verified': False,
            'medical_safety_verified': False, 'claim_support_verified': False,
            'qualified_qd_pass': False, 'may_publish': False,
            'verified_paid_orders': None, 'realized_net_revenue': None}

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = ap.parse_args(argv)
    try:
        print(json.dumps(native(args.root), sort_keys=True))
    except (VisibilityHold, ValueError, KeyError, TypeError, OSError, UnicodeError) as exc:
        print(json.dumps({'state': 'VISIBLE_CITATION_FAILURE_HARD_HOLD',
                          'release_state': HOLD, 'qualified_qd_pass': False,
                          'may_publish': False, 'error': str(exc)}, sort_keys=True))
    return 2

if __name__ == '__main__':
    sys.exit(main())
