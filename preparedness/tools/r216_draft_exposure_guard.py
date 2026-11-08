#!/usr/bin/env python3
"""R216: conservative, read-only exposure/target audit layered on R215.

The previous R215 gate checks textual parity of .pa-body with the author, but a
hidden ancestor can conceal unchanged words, a hidden bibliography can conceal
sources, and a non-HTTPS link may have been added beside intact citations.
This gate inspects both draft transports, never returns PASS, and performs no
filesystem writes. Inline styles/DOM are checked; computed CSS and browsers
remain outside scope. Not a scientific, medical, or publishing approval.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
SCHEMA = 'fv-preparedness-r216-draft-exposure-v1'
SCOPES = ('pa-body', 'pa-sources', 'pa-chips', 'pa-review')
VOID = frozenset('area base br col embed hr img input link meta param source track wbr'.split())
DANGEROUS = frozenset('base iframe object embed form input textarea button video audio'.split())
BAD_STYLES = (
    re.compile(r'(?:^|;)\s*display\s*:\s*none\b',re.I),
    re.compile(r'(?:^|;)\s*visibility\s*:\s*(?:hidden|collapse)\b',re.I),
    re.compile(r'(?:^|;)\s*content-visibility\s*:\s*hidden\b',re.I),
    re.compile(r'(?:^|;)\s*opacity\s*:\s*(?:0+(?:\.0+)?)(?:\s*!important)?\s*(?:;|$)',re.I),
)
SOURCE_ID = re.compile(r'src-[1-9][0-9]*\Z')


def invalid(reason):
    return {'schema':SCHEMA,'state':INVALID,'errors':[str(reason)],'transports':[],
            'independent_qd_pass':False,'publication_authorized':False,
            'medical_safety_verified':False,'source_claim_review':'REQUIRED'}


class ExposureReader(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.scopes = {x:0 for x in SCOPES}
        self.src_ids = []
        self.src_links = {}
        self.scope_text = {x:[] for x in SCOPES}
        self.anchors = 0

    def _inside(self, scope):
        return any(scope in node['scopes'] for node in self.stack)

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        classes = set((d.get('class') or '').split())
        own = set(SCOPES) & classes
        parent_hidden = bool(self.stack and self.stack[-1]['concealed'])
        style = (d.get('style') or '').strip()
        hidden = ('hidden' in d or 'inert' in d or
                  (d.get('aria-hidden') or '').strip().lower()=='true' or
                  any(p.search(style) for p in BAD_STYLES) or
                  tag in {'script','style','template','noscript'} or
                  (tag in {'details','dialog'} and 'open' not in d))
        concealed = hidden or parent_hidden
        active = any(self._inside(s) for s in SCOPES) or bool(own)
        if own:
            for s in own:
                self.scopes[s] += 1
                if concealed:
                    self.errors.append(f'{s} concealed by self or ancestor')
                if self._inside(s):
                    self.errors.append(f'nested {s} scope')
        if active and any(k.startswith('on') for k in d):
            self.errors.append('inline event handler in protected section')
        if active and tag in DANGEROUS:
            self.errors.append(f'active or forbidden {tag} in protected section')
        if active and concealed and not own and hidden:
            self.errors.append(f'concealed descendant {tag} in protected section')
        if active and tag=='a':
            h = d.get('href')
            if not isinstance(h,str) or not h.strip():
                self.errors.append('empty protected anchor destination')
            elif self._inside('pa-sources') or 'pa-sources' in own:
                if not re.fullmatch(r'https://[^\s<>"\']+',h,re.I):
                    self.errors.append('source bibliography link not absolute HTTPS')
            elif not (re.fullmatch(r'https://[^\s<>"\']+',h,re.I) or
                      re.fullmatch(r'#[A-Za-z][\w:.-]*',h) or
                      re.fullmatch(r'/(?!/)[A-Za-z0-9_./%?#=&+-]*',h)):
                self.errors.append('unsafe or unapproved body/notice anchor scheme')
            if ((d.get('target') or '').lower()=='_blank' and
                not {'noopener','noreferrer'}.issubset(set((d.get('rel') or '').lower().split()))):
                self.errors.append('external new-tab link missing rel protections')
            self.anchors += 1
        if self._inside('pa-sources') and tag=='li':
            ident = d.get('id') or ''
            if SOURCE_ID.fullmatch(ident):
                self.src_ids.append(int(ident[4:]))
            else:
                self.errors.append('bibliography li missing numbered source id')
        if tag=='base':
            self.errors.append('base URL override forbidden')
        if tag=='meta' and (d.get('http-equiv') or '').lower()=='refresh':
            self.errors.append('active document refresh')
        if tag not in VOID:
            self.stack.append({'tag':tag,'concealed':concealed,'scopes':own})

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self,tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1]['tag']!=tag:
            self.errors.append(f'mismatched end tag: {tag}')
            return
        self.stack.pop()

    def handle_data(self,data):
        if self.stack and self.stack[-1]['concealed']:
            return
        for s in SCOPES:
            if self._inside(s):
                self.scope_text[s].append(data)

    def audit(self,raw):
        if type(raw) is not bytes or len(raw)>5_000_000:
            raise ValueError('expected <=5MB HTML bytes')
        self.feed(raw.decode('utf-8','strict'))
        self.close()
        if self.stack:
            self.errors.append('unclosed HTML structures')
        for s, count in self.scopes.items():
            if count != 1:
                self.errors.append(f'{s} must occur once; found {count}')
        if self.src_ids != list(range(1,len(self.src_ids)+1)) or not self.src_ids:
            self.errors.append('source bibliography ids missing, duplicate or out of order')
        for s in ('pa-body','pa-sources','pa-chips','pa-review'):
            if not ' '.join(self.scope_text[s]).strip():
                self.errors.append(f'{s} has no visible source/notice text')
        for s in ('pa-chips','pa-review'):
            text=' '.join(self.scope_text[s]).lower()
            if any(token in text for token in ('qd pass','medical safety verified','approved for publication','ready to publish','publication authorized')):
                self.errors.append(f'false release assurance in {s}')
        return self.errors


def evaluate(prior_report, rendered):
    """A valid R215 HOLD is a prerequisite, never a release authorization."""
    try:
        if (type(prior_report) is not dict or prior_report.get('schema')!='fv-preparedness-r215-wp-draft-transport-v1'
            or prior_report.get('state') != HOLD or prior_report.get('errors')!=[]
            or prior_report.get('independent_qd_pass') is not False
            or prior_report.get('publication_authorized') is not False
            or prior_report.get('medical_safety_verified') is not False):
            raise ValueError('exact R215 HOLD without release flags required')
        articles=prior_report.get('articles')
        if (type(articles) is not list or len(articles)!=2 or
            [x.get('article') for x in articles]!=[7,20]):
            raise ValueError('prior report requires held Article 7/20 rows')
        if type(rendered) is not dict or set(rendered)!={7,20}:
            raise ValueError('exact held article transport set required')
        rows=[]
        for a in articles:
            number=a['article']; outs=rendered[number]
            if type(outs) is not dict or set(outs)!={'wp','preview'}:
                raise ValueError('both transports required')
            for channel in ('wp','preview'):
                raw=outs[channel]
                digest=hashlib.sha256(raw).hexdigest() if type(raw) is bytes else ''
                if a.get('render_sha256',{}).get(channel)!=digest:
                    raise ValueError(f'R215 prior receipt drift: {number}/{channel}')
                doc=ExposureReader()
                errors=doc.audit(raw)
                if errors:
                    raise ValueError(f'{number}/{channel}: '+ '; '.join(errors))
                rows.append({'article':number,'channel':channel,
                             'sha256':digest,'source_count':len(doc.src_ids),
                             'protected_anchors_checked':doc.anchors,
                             'exposure_gate':'DRAFT_HARD_HOLD'})
        return {'schema':SCHEMA,'state':HOLD,'errors':[],'transports':rows,
                'independent_qd_pass':False,'publication_authorized':False,
                'medical_safety_verified':False,'source_claim_review':'REQUIRED',
                'issue':136,'conversion_issue':820}
    except (ValueError,TypeError,KeyError,AttributeError,UnicodeError) as exc:
        return invalid(str(exc))


def main(argv=None):
    p=argparse.ArgumentParser(description='Conservative read-only R216 draft exposure guard; HOLD-only output')
    for name in ('r215-report','wp7','wp20','preview7','preview20'):
        p.add_argument('--'+name,required=True,type=Path)
    args=p.parse_args(argv)
    try:
        prior=json.loads(getattr(args,'r215_report').read_text(encoding='utf-8'))
        rendered={7:{'wp':args.wp7.read_bytes(),'preview':args.preview7.read_bytes()},
                  20:{'wp':args.wp20.read_bytes(),'preview':args.preview20.read_bytes()}}
        result=evaluate(prior,rendered)
    except (OSError,ValueError,TypeError,UnicodeError) as e:
        result=invalid('read-only input error: '+str(e))
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2 if result['state']==HOLD else 3

if __name__=='__main__':
    raise SystemExit(main())
