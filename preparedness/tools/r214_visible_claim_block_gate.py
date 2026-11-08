#!/usr/bin/env python3
"""R214: byte-anchored complete HTML claim-block review; no release/PASS pathway.

Only accepts an R213 HOLD docket tied to Git blob bytes. CLI reuses authenticated
R212/R213 readers. Never rewrites authored HTML, source registers or WordPress.
"""
from __future__ import annotations
import argparse
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re

SCHEMA = 'fv-preparedness-r214-complete-claim-block-v1'
HOLD, INVALID = 'DRAFT_HARD_HOLD', 'INVALID_HARD_HOLD'
BLOCK_TAGS = {'li', 'p', 'blockquote', 'td', 'th', 'figcaption', 'h1','h2','h3','h4','h5','h6'}
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
FORBIDDEN = {'script','style','template','noscript','iframe','svg','object','canvas'}
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')


def blob_sha(b):
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def _invalid(message):
    return {'schema': SCHEMA, 'state': INVALID, 'errors': [str(message)], 'claims': [],
            'human_claim_verified': False, 'medical_safety_verified': False,
            'independent_qd_pass': False, 'publication_authorized': False}


class ReviewMarkupError(ValueError):
    pass


class ClaimParser(HTMLParser):
    """HTML source-position parser: citations must occur in a visible text node.

    Captures an *entire* text-containing block rather than cutting a 320-byte
    window through an HTML element, while preserving exact raw byte evidence.
    """
    def __init__(self, text):
        super().__init__(convert_charrefs=False)
        self.text = text
        self.lines = [0]
        for m in re.finditer('\n', text):
            self.lines.append(m.end())
        self.open = []
        self.hits = []
        self.errors = []

    def char_position(self, pos):
        line, col = pos
        if line < 1 or line > len(self.lines):
            raise ReviewMarkupError('bad HTML position')
        return self.lines[line-1] + col

    def handle_starttag(self, tag, attrs):
        start = self.char_position(self.getpos())
        if tag in VOID:
            return
        at = dict(attrs)
        hidden = ('hidden' in at or at.get('aria-hidden','').lower() == 'true' or
                  bool(re.search(r'(?:display\s*:\s*none|visibility\s*:\s*hidden)',at.get('style',''),re.I)))
        self.open.append({'tag':tag, 'start':start, 'hidden':hidden or tag in FORBIDDEN,
                          'text': [], 'hits': []})

    def handle_startendtag(self, tag, attrs):
        return

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.open:
            # Some existing editor-authored HTML fragments are inserted into
            # a larger template; reject only structurally ambiguous claim blocks.
            return
        if self.open[-1]['tag'] != tag:
            # Reject mismatches that could displace the actual claim container.
            if any(frame['tag'] == tag for frame in self.open):
                raise ReviewMarkupError('mismatched HTML nesting')
            return
        frame = self.open.pop()
        end = self.char_position(self.getpos())
        close = self.text.find('>', end)
        if close < 0:
            raise ReviewMarkupError('unterminated closing tag')
        frame['end'] = close+1
        if frame['tag'] in BLOCK_TAGS:
            for hit in frame['hits']:
                if hit.get('block') is None:
                    hit['block'] = (frame['start'], frame['end'])
        if self.open:
            self.open[-1]['text'].extend(frame['text'])
            self.open[-1]['hits'].extend(frame['hits'])

    def handle_data(self, data):
        start = self.char_position(self.getpos())
        for match in CITE.finditer(data):
            hidden = any(fr['hidden'] for fr in self.open)
            hit = {'source_id':match.group(1), 'char_start': start+match.start(),
                   'char_end':start+match.end(), 'hidden':hidden, 'block':None}
            self.hits.append(hit)
            if self.open:
                self.open[-1]['hits'].append(hit)
        if self.open:
            self.open[-1]['text'].append(data)


def _visible_text(block_html):
    class Collector(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts=[]
            self.bad=False
            self.hidden=[]
        def handle_starttag(self,tag,attrs):
            a=dict(attrs)
            is_hidden=tag in FORBIDDEN or 'hidden' in a or a.get('aria-hidden','').lower()=='true' or bool(re.search(r'display\s*:\s*none|visibility\s*:\s*hidden', a.get('style',''),re.I))
            if tag not in VOID:self.hidden.append(is_hidden or any(self.hidden))
        def handle_endtag(self,tag):
            if tag not in VOID and self.hidden:self.hidden.pop()
        def handle_data(self,data):
            if not any(self.hidden):self.parts.append(data)
    p=Collector();p.feed(block_html);p.close()
    text=' '.join(' '.join(p.parts).split())
    text=CITE.sub('',text)
    text=re.sub(r'\{\{link:[^|}]+\|([^}]+)\}\}',r'\1',text)
    return ' '.join(text.split())


def evaluate_from_docket(docket, raw_bodies):
    """Pure structural check. A valid review packet ALWAYS remains HARD HOLD."""
    try:
        if type(docket) is not dict or docket.get('schema') != 'fv-preparedness-r213-held-claim-context-v1' or docket.get('state') != HOLD:
            raise ReviewMarkupError('R213 source custody is not in HOLD state')
        for key in ('publication_authorized','independent_qd_pass','medically_safe','review_complete'):
            if docket.get(key) is not False:
                raise ReviewMarkupError('R213 unauthorized state: '+key)
        claims=docket.get('claims')
        if type(claims) is not list or len(claims)!=3 or [x.get('article') for x in claims]!=[7,7,20]:
            raise ReviewMarkupError('three ordered original claims required')
        if type(raw_bodies) is not dict or set(raw_bodies)!={7,20}:
            raise ReviewMarkupError('exactly two original article bodies required')
        output=[]; seen=set()
        for c in claims:
            n=c['article']; body=raw_bodies[n]
            if type(body) is not bytes:
                raise ReviewMarkupError('non-byte original HTML')
            if blob_sha(body)!=c.get('body_git_blob_sha1'):
                raise ReviewMarkupError('source blob identity changed')
            source=c.get('source_id'); start=c.get('source_start_byte');end=c.get('source_end_byte')
            if type(source) is not str or type(start) is not int or type(end) is not int or not 0 <= start < end <= len(body):
                raise ReviewMarkupError('invalid anchored citation span')
            marker=('{{cite:'+source+'}}').encode('ascii')
            if body[start:end]!=marker or not re.fullmatch(r'[0-9a-f]{64}',c.get('receipt_sha256','')):
                raise ReviewMarkupError('receipt or marker invalid')
            receipt=c['receipt_sha256']
            if receipt in seen:raise ReviewMarkupError('duplicate review identity')
            seen.add(receipt)
            text=body.decode('utf-8','strict')
            parser=ClaimParser(text);parser.feed(text);parser.close()
            # All citations in raw HTML must have visible data-node positions.
            if len(parser.hits) != len(CITE.findall(text)):
                raise ReviewMarkupError('citation in HTML attribute, comment, or concealed markup')
            hit=[h for h in parser.hits if len(text[:h['char_start']].encode('utf-8'))==start and h['source_id']==source]
            if len(hit)!=1 or hit[0]['hidden'] or not hit[0]['block']:
                raise ReviewMarkupError('citation not anchored to visible closed claim block')
            a,b=hit[0]['block']
            block=text[a:b].encode('utf-8')
            byte_a=len(text[:a].encode('utf-8'));byte_b=len(text[:b].encode('utf-8'))
            if not byte_a <= start < end <= byte_b or len(block)>16000:
                raise ReviewMarkupError('unbounded or misaligned full claim block')
            rendered=_visible_text(text[a:b])
            if len(rendered)<24 or '{{cite:' in rendered:
                raise ReviewMarkupError('incomplete text claim block')
            output.append({'article':n,'source_id':source,'source_url':c['source_url'],
                           'citation_occurrence':c['citation_occurrence'],
                           'receipt_sha256':receipt,'body_git_blob_sha1':c['body_git_blob_sha1'],
                           'citation_span_bytes':[start,end], 'claim_block_span_bytes':[byte_a,byte_b],
                           'raw_claim_block_sha256':hashlib.sha256(block).hexdigest(),
                           'visible_claim_text':rendered,
                           'visible_claim_sha256':hashlib.sha256(rendered.encode()).hexdigest(),
                           'human_source_claim_review':'REQUIRED', 'editorial_decision':'PENDING'})
        return {'schema':SCHEMA,'state':HOLD,'claims':output,'errors':[],
                'human_claim_verified':False,'medical_safety_verified':False,
                'independent_qd_pass':False,'publication_authorized':False,
                'issue':136,'conversion_issue':820}
    except (ValueError,TypeError,KeyError,IndexError,AttributeError,UnicodeError,OverflowError) as e:
        return _invalid(str(e))


def main(argv=None):
    p=argparse.ArgumentParser(description='R214 read-only complete citation claim blocks (HOLD only)')
    p.add_argument('--checkout',required=True,type=Path)
    args=p.parse_args(argv)
    try:
        parent=Path(__file__)
        spec=importlib.util.spec_from_file_location('r214_import_r213',parent.with_name('r213_claim_context_docket.py'))
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        r212=mod._r212(); original=r212.read_checkout(args.checkout)
        docket=mod.evaluate(original)
        result=evaluate_from_docket(docket,{7:original[r212.A7+'.body.html'],20:original[r212.A20+'.body.html']})
    except (OSError,ValueError,ImportError,AttributeError,TypeError) as e:
        result=_invalid('source reader failed: '+str(e))
    print(json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False))
    return 2 if result['state']==HOLD else 3

if __name__=='__main__':
    raise SystemExit(main())
