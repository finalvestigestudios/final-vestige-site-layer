#!/usr/bin/env python3
"""R288: fail-closed citation context review of the 41 frozen HTML bodies.

Only distinguishes literal citation markers in reader-text nodes from markers
in comments, attributes, raw-text elements and locally concealed markup.
Neither this lexer nor a source ID is evidence of rendered visibility, medical
safety, editorial truth, accessibility, QD approval or release authorization.
"""
from __future__ import annotations
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import types

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
PARENT = 'tools/r287_body_citation_provenance_hold.py'
PARENT_SHA = 'b7bd7b2b65010df2aaef8875f717ee94cc70d553'
CITE = re.compile(r'\{\{cite:([A-Za-z0-9][A-Za-z0-9._-]*)\}\}')
HIDE_STYLE = re.compile(r'(?i)(?:^|;)\s*(?:display\s*:\s*none\b|visibility\s*:\s*(?:hidden|collapse)\b|content-visibility\s*:\s*hidden\b)')
HIDDEN_ELEMENTS = frozenset(('script', 'style', 'template', 'head', 'noscript', 'iframe', 'svg', 'math', 'canvas', 'object'))
VOID_ELEMENTS = frozenset(('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'))


def require(ok, why):
    if not ok:
        raise ValueError(why)


def git_blob(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode('ascii')+b'\0'+raw).hexdigest()


def load_parent(root):
    base = Path(root)
    require(base.is_dir() and not base.is_symlink(), 'unsafe archive root')
    candidate = base
    for piece in PARENT.split('/'):
        require(piece not in ('','.','..'), 'unsafe parent component')
        candidate = candidate / piece
        require(not candidate.is_symlink(), 'symlinked parent gate')
    require(candidate.is_file(), 'R287 parent gate missing')
    raw = candidate.read_bytes()
    require(git_blob(raw) == PARENT_SHA, 'R287 authenticated gate drift')
    module = types.ModuleType('fv_r287_authenticated_r288')
    module.__file__ = str(candidate)
    module.__package__ = ''
    exec(compile(raw, str(candidate), 'exec', dont_inherit=True), module.__dict__)
    require(callable(getattr(module,'audit',None)), 'R287 audit absent')
    return module


class ReaderTextScanner(HTMLParser):
    """Intentionally conservative HTML-token context, NOT browser visibility."""
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.stack = []
        self.readable_parts = []
        self.nonreader_parts = []
        self.errors = []
        self.markup_text_parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        local_hidden = (tag in HIDDEN_ELEMENTS or 'hidden' in attrs or
                        'inert' in attrs or
                        str(attrs.get('aria-hidden','')).lower() == 'true' or
                        bool(HIDE_STYLE.search(attrs.get('style') or '')))
        if tag not in VOID_ELEMENTS:
            self.stack.append((tag,local_hidden))
        self.markup_text_parts.extend(value or '' for value in attrs.values())

    def handle_startendtag(self, tag, attrs):
        self.markup_text_parts.extend(value or '' for _,value in attrs)

    def handle_endtag(self, tag):
        indexes = [i for i,item in enumerate(self.stack) if item[0] == tag]
        if indexes:
            del self.stack[indexes[-1]:]
        elif tag not in VOID_ELEMENTS:
            self.errors.append('unmatched end tag: '+tag)

    def handle_data(self, data):
        if any(hidden for _,hidden in self.stack):
            self.nonreader_parts.append(data)
        else:
            self.readable_parts.append(data)

    def handle_comment(self, data):
        self.nonreader_parts.append(data)

    def handle_decl(self, decl):
        self.nonreader_parts.append(decl)

    def handle_pi(self, data):
        self.nonreader_parts.append(data)

    def unknown_decl(self, data):
        self.nonreader_parts.append(data)


def scan_body(raw, name, canonical_parser):
    require(type(raw) is bytes and callable(canonical_parser), 'body/parser invalid: '+name)
    raw_cites = canonical_parser(raw,name)  # R287 strict exact-marker syntax
    body = raw.decode('utf-8')
    scanner = ReaderTextScanner()
    scanner.feed(body)
    scanner.close()
    require(not scanner.errors, 'HTML tag structure incomplete: '+name+': '+repr(scanner.errors[:3]))
    visible_text = ''.join(scanner.readable_parts)
    reader_cites = Counter(CITE.findall(visible_text))
    # Text-node concatenation can reveal a marker split across HTML tags.
    # This is an unresolved markup defect, never a safe matched citation.
    require(sum(reader_cites.values()) <= sum(raw_cites.values()),
            'markup-split citation requires review: '+name)
    require(reader_cites == raw_cites,
            'nonreader/attribute/comment/hidden citation context: '+name)
    # HTMLParser may recover malformed tags; do not present this as HTML validity.
    return {'body':name,'inline_occurrences':sum(reader_cites.values()),
            'distinct_source_ids':len(reader_cites),'context_token_consistent':True,
            'render_visibility_verified':False,'human_source_scope_verified':False}


def audit(root):
    try:
        gate = load_parent(root)
        upstream = gate.audit(root)
        require(type(upstream) is dict and upstream.get('state') == HOLD and
                all(upstream.get(k) is False for k in
                    ('publication_authorized','independent_qd_pass',
                     'medical_safety_verified','privacy_approved')),
                'R287 source/citation gate failed or promoted approvals')
        bridge = gate.load_bridge(root)
        manifest = bridge.strict_json(bridge.pinned_bytes(root,*bridge.INTEGRATED))
        pairs = gate.paired_content_rows(manifest['entries'])
        results=[]
        for bodyrow, _ in pairs:
            raw = bridge.pinned_bytes(root, bodyrow['path'], bodyrow['sha'])
            results.append(scan_body(raw,bodyrow['path'],gate.parse_cites))
        require(len(results)==41, '41-authenticated-body census drift')
        return {'state':HOLD,'publication_authorized':False,'independent_qd_pass':False,
                'medical_safety_verified':False,'privacy_approved':False,
                'renderer_visibility_verified':False,'wordpress_drafts_verified':False,
                'human_source_scope_review_required':True,
                'body_count':41,'inline_occurrences':sum(r['inline_occurrences'] for r in results),
                'review_only_context_rows':results}
    except (OSError,ValueError,TypeError,KeyError,AttributeError,UnicodeError,ImportError,SyntaxError) as e:
        return {'state':INVALID,'publication_authorized':False,'independent_qd_pass':False,
                'medical_safety_verified':False,'privacy_approved':False,
                'renderer_visibility_verified':False,'wordpress_drafts_verified':False,
                'errors':[str(e)]}


if __name__ == '__main__':
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--root',required=True,type=Path)
    outcome=audit(ap.parse_args().root)
    print(json.dumps(outcome,indent=2,sort_keys=True))
    raise SystemExit(2 if outcome['state']==HOLD else 3)
