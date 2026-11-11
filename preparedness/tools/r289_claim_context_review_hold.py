#!/usr/bin/env python3
"""R289: review-only reader-claim citation context and obvious CSS concealment gate.

Authenticates the exact R288 parent source before execution. Preserves the frozen
35-article/six-tool archive, routes, metadata, source IDs and safety holds.
A text excerpt or inline-style check is NOT a rendered/browser visibility test,
a source-scope adjudication, medical clearance, or permission to publish.
"""
from __future__ import annotations
from collections import Counter
import hashlib
from html.parser import HTMLParser
from html import unescape
import json
from pathlib import Path
import re
import types

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
PARENT = 'tools/r288_reader_exposure_citation_hold.py'
PARENT_SHA = '0924ead810a4df8c169a5e77f05bcf979eac3dc9'
CITE = re.compile(r'\{\{cite:([A-Za-z0-9][A-Za-z0-9._-]*)\}\}')
NO_NARRATIVE = frozenset(('textarea', 'select', 'option', 'datalist'))
HIDDEN_ELEMENTS = frozenset(('script','style','template','head','noscript','iframe','svg','math','canvas','object'))
HIDE_STYLE = re.compile(r'(?i)(?:^|;)\s*(?:display\s*:\s*none\b|visibility\s*:\s*(?:hidden|collapse)\b|content-visibility\s*:\s*hidden\b)')
SEMANTIC = frozenset(('p', 'li', 'td', 'th', 'blockquote', 'figcaption', 'caption',
                      'dt', 'dd', 'summary', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'))
VOID = frozenset(('area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                  'link', 'meta', 'param', 'source', 'track', 'wbr'))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def git_blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def load_parent(root):
    root = Path(root)
    require(root.is_dir() and not root.is_symlink(), 'unsafe root')
    path = root
    for part in PARENT.split('/'):
        require(part not in ('', '.', '..'), 'unsafe gate path')
        path = path / part
        require(not path.is_symlink(), 'symlinked parent gate')
    require(path.is_file(), 'R288 parent missing')
    raw = path.read_bytes()
    require(git_blob(raw) == PARENT_SHA, 'R288 exact source drift')
    mod = types.ModuleType('fv_r288_exact_r289')
    mod.__file__ = str(path)
    mod.__package__ = ''
    exec(compile(raw, str(path), 'exec', dont_inherit=True), mod.__dict__)
    require(callable(getattr(mod, 'audit', None)), 'R288 audit missing')
    return mod


def style_flags(css):
    """Recognize limited obvious CSS; never claim exhaustive CSS/browser visibility."""
    require(isinstance(css, str), 'style must be text')
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    hard, review = set(), set()
    for item in css.split(';'):
        if ':' not in item:
            continue
        prop, value = (x.strip().lower() for x in item.split(':', 1))
        value = re.sub(r'\s*!important\s*$', '', value).strip()
        compact = re.sub(r'\s+', '', value)
        if prop == 'opacity' and re.fullmatch(r'(?:0+(?:\.0*)?|\.0+)%?', compact):
            hard.add('opacity-zero')
        if prop in ('filter', '-webkit-filter') and re.search(r'opacity\((?:0+(?:\.0*)?|\.0+)%?\)', compact):
            hard.add('filter-opacity-zero')
        if prop == 'transform' and re.search(r'(?:^|\))scale\((?:0+(?:\.0*)?|\.0+)\)', compact):
            hard.add('scale-zero')
        if prop in ('font-size', 'line-height') and re.fullmatch(r'0+(?:\.0*)?(?:px|em|rem|%)?', compact):
            review.add(prop+'-zero')
        if prop == 'color' and compact in ('transparent', 'rgba(0,0,0,0)'):
            review.add('transparent-text')
        if prop in ('clip', 'clip-path') and ('rect(' in compact or 'inset(' in compact):
            review.add('css-clipping')
        if prop == 'overflow' and compact == 'hidden':
            review.add('overflow-hidden')
    return sorted(hard), sorted(review)


class ClaimContext(HTMLParser):
    """Conservative source-marker placement ledger, not a DOM/CSS renderer."""
    def __init__(self, raw_text):
        super().__init__(convert_charrefs=False)
        self.raw = raw_text
        self.line_starts = [0] + [m.end() for m in re.finditer(r'\n', raw_text)]
        self.reader_parts = []
        self.stack = []
        self.blocks = {'implicit': []}
        self.excluded_blocks = set()
        self.seq = 0
        self.edges = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        hard, review = style_flags(attributes.get('style') or '')
        block = None
        if tag in SEMANTIC:
            self.seq += 1
            block = f'{tag}-{self.seq}'
            self.blocks[block] = []
        hidden = (tag in HIDDEN_ELEMENTS or 'hidden' in attributes or
                  'inert' in attributes or
                  str(attributes.get('aria-hidden','')).lower() == 'true' or
                  bool(HIDE_STYLE.search(attributes.get('style') or '')))
        if tag not in VOID:
            self.stack.append({'tag': tag, 'block': block, 'hard': hard,
                               'hidden': hidden, 'review': review,
                               'collapsed':tag == 'details' and 'open' not in attributes})

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        indices = [i for i, item in enumerate(self.stack) if item['tag'] == tag]
        if indices:
            del self.stack[indices[-1]:]
        elif tag not in VOID:
            self.errors.append('unmatched HTML end tag '+tag)

    def permitted_reader_context(self):
        """Reuse the citation-exposure exclusions for surrounding claim text.

        This is only a conservative HTML source-level rule, not a CSS renderer.
        Hidden/hard-concealed/non-narrative siblings cannot substantiate a
        separate visible citation by contaminating its context fingerprint.
        """
        return not any(item['hidden'] or item['hard'] or
                       item['tag'] in NO_NARRATIVE for item in self.stack)

    def record_excluded(self, data):
        if data.strip():
            block = next((item['block'] for item in reversed(self.stack) if item['block']), 'implicit')
            self.excluded_blocks.add(block)

    def add_decoded_entity(self, data):
        if self.permitted_reader_context():
            block = next((item['block'] for item in reversed(self.stack) if item['block']), 'implicit')
            self.blocks[block].append(data)
            self.reader_parts.append(data)
        else:
            self.record_excluded(data)

    def handle_entityref(self, name):
        self.add_decoded_entity(unescape('&'+name+';'))

    def handle_charref(self, name):
        self.add_decoded_entity(unescape('&#'+name+';'))

    def handle_data(self, data):
        in_reader = not any(item['hidden'] for item in self.stack)
        matches = list(CITE.finditer(data))
        require(in_reader or not matches, 'nonreader hidden literal citation occurrence')
        block = next((item['block'] for item in reversed(self.stack) if item['block']), 'implicit')
        offset = len(''.join(self.blocks[block]))
        if self.permitted_reader_context():
            self.blocks[block].append(data)
            self.reader_parts.append(data)
        else:
            self.record_excluded(data)
        for match in matches:
            tags = [item['tag'] for item in self.stack]
            require(not any(t in NO_NARRATIVE for t in tags),
                    'citation in non-narrative form control')
            hard = sorted({f for item in self.stack for f in item['hard']})
            require(not hard, 'CSS-concealed citation: '+','.join(hard))
            risk = sorted({f for item in self.stack for f in item['review']})
            if any(item['collapsed'] for item in self.stack):
                # A <summary> descendant is exposed in a closed <details>.
                if not any(item['tag'] == 'summary' for item in self.stack):
                    risk.append('closed-details-disclosure')
            pre = data[:match.start()]
            line, col = self.getpos()
            line += pre.count('\n')
            col = len(pre.rsplit('\n', 1)[-1]) if '\n' in pre else col + len(pre)
            position = self.line_starts[self.getpos()[0]-1] + self.getpos()[1] + match.start()
            require(self.raw[position:position+len(match.group(0))] == match.group(0),
                    'literal DATA source span mapping failed')
            self.edges.append({'source_id':match.group(1),'raw_start':position,
                               'raw_end':position+len(match.group(0)),
                               'line':line,'column':col,
                               'block':block,'block_tag':block.split('-',1)[0],
                               'block_offset':offset+match.start(),
                               'review_flags':sorted(set(risk))})

    def finish(self):
        self.close()
        require(not self.errors, 'HTML structure: '+repr(self.errors[:3]))
        raw_spans = [(m.start(),m.end(),m.group(1)) for m in CITE.finditer(self.raw)]
        reader_spans = [(x['raw_start'],x['raw_end'],x['source_id']) for x in self.edges]
        require(raw_spans == reader_spans,
                'raw citation occurrence not identical to visible DATA occurrence')
        require(Counter(CITE.findall(''.join(self.reader_parts))) ==
                Counter(e['source_id'] for e in self.edges),
                'markup/entity-assembled citation token requires review')
        for edge in self.edges:
            raw = ''.join(self.blocks[edge['block']])
            pos = edge.pop('block_offset')
            left = CITE.sub('', raw[max(0, pos-130):pos])
            right = CITE.sub('', raw[pos:pos+170])
            nearby = re.sub(r'\s+', ' ', left+' [SOURCE] '+right).strip()[:240]
            context = re.sub(r'\s+', ' ', CITE.sub('', raw)).strip()
            edge['context_sha256'] = hashlib.sha256(context.encode('utf-8')).hexdigest()
            edge['review_excerpt'] = nearby
            if not context:
                edge['review_flags'].append('no-claim-text-in-block')
            if edge['block'] in self.excluded_blocks:
                edge['review_flags'].append('excluded-nonreader-sibling-context')
            if edge['block'] == 'implicit':
                edge['review_flags'].append('no-semantic-block')
            edge['review_flags'] = sorted(set(edge['review_flags']))
        return self.edges


def scan_document(raw, name, parent_scanner, canonical_parser):
    require(type(raw) is bytes and callable(parent_scanner) and callable(canonical_parser),
            'invalid authenticated scan inputs')
    baseline = parent_scanner(raw, name, canonical_parser)
    parser = ClaimContext(raw.decode('utf-8'))
    parser.feed(raw.decode('utf-8'))
    edges = parser.finish()
    require(Counter(x['source_id'] for x in edges) == canonical_parser(raw, name),
            'literal/reader citation identity mismatch: '+name)
    require(len(edges) == baseline['inline_occurrences'], 'R288 count mismatch: '+name)
    return {'body':name,'source_edges':edges,'count':len(edges),
            'source_occurrence_identity_verified':True,
            'context_entity_decoding_applied':True,
            'context_review_flags':sum(bool(e['review_flags']) for e in edges),
            'source_scope_verified':False,'browser_visibility_verified':False}


def audit(root):
    try:
        gate = load_parent(root)
        upstream = gate.audit(root)
        require(type(upstream) is dict and upstream.get('state') == HOLD and
                all(upstream.get(k) is False for k in
                    ('publication_authorized','independent_qd_pass',
                     'medical_safety_verified','privacy_approved')),
                'R288 upstream safe hold failed')
        ancestor = gate.load_parent(root)
        bridge = ancestor.load_bridge(root)
        manifest = bridge.strict_json(bridge.pinned_bytes(root, *bridge.INTEGRATED))
        pairs = ancestor.paired_content_rows(manifest['entries'])
        rows = []
        for body, _ in pairs:
            raw = bridge.pinned_bytes(root, body['path'], body['sha'])
            rows.append(scan_document(raw,body['path'],gate.scan_body,ancestor.parse_cites))
        require(len(rows)==41, '41 pinned bodies required')
        require(sum(x['count'] for x in rows)==upstream['inline_occurrences'],
                'R288 authentic total occurrence mismatch')
        return {'state':HOLD,'publication_authorized':False,'independent_qd_pass':False,
                'medical_safety_verified':False,'privacy_approved':False,
                'source_scope_verified':False,'browser_visibility_verified':False,
                'wp_export_verified':False,'body_count':41,
                'inline_occurrences':sum(x['count'] for x in rows),
                'risk_flagged_edges':sum(x['context_review_flags'] for x in rows),
                'review_only_body_rows':rows}
    except (OSError,ValueError,TypeError,KeyError,AttributeError,UnicodeError,
            ImportError,SyntaxError) as exc:
        return {'state':INVALID,'publication_authorized':False,
                'independent_qd_pass':False,'medical_safety_verified':False,
                'privacy_approved':False,'errors':[str(exc)]}


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,type=Path)
    outcome = audit(parser.parse_args().root)
    print(json.dumps(outcome,sort_keys=True,indent=2))
    raise SystemExit(2 if outcome['state']==HOLD else 3)
