#!/usr/bin/env python3
"""Read-only R215 transport guard: authored claim text + citations to draft WP/preview.
No source verification, editorial adjudication, safety approval, publication or writes.
Inputs are original HTML bytes, the HOLD-only R214 dossier, and two rendered outputs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from html.parser import HTMLParser
import re

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
SCHEMA = 'fv-preparedness-r215-wp-draft-transport-v1'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
LINK = re.compile(r'\{\{link:[a-z0-9-]+\|([^}]+)\}\}')
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
BLOCKED = {'iframe', 'object', 'embed', 'form', 'textarea', 'input', 'script', 'style', 'template'}


def sha(b):
    return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()


def invalid(reason):
    return {'schema':SCHEMA,'state':INVALID,'errors':[str(reason)],'articles':[],
            'human_source_claim_review':'REQUIRED','independent_qd_pass':False,
            'publication_authorized':False,'medical_safety_verified':False}


class TextReader(HTMLParser):
    """Collect text from the original body, retaining ordered citation identity."""
    def __init__(self, order):
        super().__init__(convert_charrefs=True)
        self.order=order; self.parts=[]
    def handle_data(self, data):
        data=LINK.sub(lambda m:m.group(1),data)
        data=CITE.sub(lambda m:' CITENOTE'+str(self.order.index(m.group(1))+1)+' ',data)
        self.parts.append(data)
    def text(self):
        return ' '.join(' '.join(self.parts).split())


class DraftReader(HTMLParser):
    """Collect only .pa-body text and the numbered source hrefs."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags=[]; self.parts=[]; self.body_count=0; self.source_count=0
        self.body_at=None; self.sources_at=None; self.cite_at=None
        self.citations=[];self.hrefs={};self.current_source=None
        self.errors=[];self.whole=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs);classes=set(a.get('class','').split())
        in_body=self.body_at is not None
        if in_body and (tag in BLOCKED or 'hidden' in a or a.get('aria-hidden')=='true' or re.search(r'display\s*:\s*none|visibility\s*:\s*hidden',a.get('style',''),re.I)):
            self.errors.append('hidden or active content in rendered guide body')
        if tag not in VOID:
            self.tags.append(tag)
        depth=len(self.tags)
        if 'pa-body' in classes:
            if 'hidden' in a or a.get('aria-hidden')=='true' or re.search(r'display\s*:\s*none|visibility\s*:\s*hidden',a.get('style',''),re.I):
                self.errors.append('rendered guide body is hidden')
            self.body_count+=1
            if self.body_at is not None:self.errors.append('nested guide body')
            self.body_at=depth
        if 'pa-sources' in classes:
            self.source_count+=1;self.sources_at=depth
        if self.body_at is not None and tag=='sup' and 'pa-cite' in classes:
            if self.cite_at is not None:self.errors.append('nested cite')
            self.cite_at=depth
        if self.cite_at is not None and tag=='a':
            h=a.get('href','')
            if not re.fullmatch(r'#src-[1-9][0-9]*',h):self.errors.append('invalid numbered citation href')
            else:
                n=int(h[5:]);self.parts.append(' CITENOTE'+str(n)+' ');self.citations.append(n)
        if self.sources_at is not None and tag=='li' and re.fullmatch(r'src-[1-9][0-9]*',a.get('id','')):
            self.current_source=int(a['id'][4:])
            if self.current_source in self.hrefs:self.errors.append('duplicate source target')
        if self.current_source is not None and tag=='a':
            if self.current_source in self.hrefs:self.errors.append('duplicate source link')
            else:self.hrefs[self.current_source]=a.get('href','')
    def handle_endtag(self,tag):
        if tag in VOID:return
        if not self.tags or self.tags[-1]!=tag:
            self.errors.append('malformed HTML nesting')
            return
        depth=len(self.tags)
        if self.cite_at==depth:self.cite_at=None
        if self.body_at==depth:self.body_at=None
        if self.sources_at==depth:self.sources_at=None
        if tag=='li' and self.current_source is not None:self.current_source=None
        self.tags.pop()
    def handle_data(self,data):
        self.whole.append(data)
        if self.body_at is not None and self.cite_at is None:self.parts.append(data)
    def guide_text(self):
        return ' '.join(' '.join(self.parts).split())


def evaluate(dossier, originals, rendered):
    """A structurally sound transport stays HOLD. Any discrepancy stays INVALID HOLD.

    \`rendered\`: {7: {'wp': bytes, 'preview': bytes}, 20: ...}.
    No source URLs or content are fetched or modified here.
    """
    try:
        if type(dossier) is not dict or dossier.get('schema')!='fv-preparedness-r214-complete-claim-block-v1' or dossier.get('state')!=HOLD:
            raise ValueError('R214 HOLD dossier required')
        for key in ('human_claim_verified','medical_safety_verified','independent_qd_pass','publication_authorized'):
            if dossier.get(key) is not False:raise ValueError('unauthorized dossier release state: '+key)
        claims=dossier.get('claims')
        if not isinstance(claims,list) or len(claims)!=3 or [c.get('article') for c in claims]!=[7,7,20]:
            raise ValueError('three ordered original citation receipts required')
        if type(originals) is not dict or set(originals)!={7,20} or type(rendered) is not dict or set(rendered)!={7,20}:
            raise ValueError('exact two held article identifiers required')
        article_rows=[];receipts=set()
        for n in (7,20):
            original=originals[n]
            if type(original) is not bytes:raise ValueError('original body must be bytes')
            if any(c['body_git_blob_sha1']!=sha(original) for c in claims if c['article']==n):
                raise ValueError('original Git blob changed')
            src=original.decode('utf-8','strict')
            order=list(dict.fromkeys(CITE.findall(src)))
            if not order:raise ValueError('no original source citations')
            for c in (x for x in claims if x['article']==n):
                if c['receipt_sha256'] in receipts:raise ValueError('duplicate receipt')
                receipts.add(c['receipt_sha256'])
                if not re.fullmatch(r'[0-9a-f]{64}',c['receipt_sha256']):raise ValueError('bad receipt')
                if c['source_id'] not in order or not c.get('source_url','').startswith('https://'):
                    raise ValueError('untrusted source identity')
                if c.get('human_source_claim_review')!='REQUIRED' or c.get('editorial_decision')!='PENDING':
                    raise ValueError('unreviewed citation changed state')
            text=TextReader(order);text.feed(src);text.close()
            expected=text.text()
            if not expected or 'CITENOTE' not in expected:raise ValueError('source claim text not retained')
            outputs=rendered[n]
            if type(outputs) is not dict or set(outputs)!={'wp','preview'}:raise ValueError('both draft artifacts required')
            digests={}
            for channel in ('wp','preview'):
                raw=outputs[channel]
                if type(raw) is not bytes or len(raw)>5_000_000:raise ValueError('invalid draft transport bytes')
                doc=raw.decode('utf-8','strict')
                rd=DraftReader();rd.feed(doc);rd.close()
                if rd.errors or rd.body_count!=1 or rd.source_count!=1 or rd.body_at is not None or rd.sources_at is not None:
                    raise ValueError(channel+': malformed/missing body/sources: '+';'.join(rd.errors))
                if rd.guide_text()!=expected:raise ValueError(channel+': authored reading depth or citation order lost')
                citation_numbers=[order.index(s)+1 for s in CITE.findall(src)]
                if rd.citations!=citation_numbers:raise ValueError(channel+': citation occurrence order changed')
                for c in (x for x in claims if x['article']==n):
                    num=order.index(c['source_id'])+1
                    if rd.hrefs.get(num)!=c['source_url']:
                        raise ValueError(channel+': held citation source destination changed')
                whole=' '.join(rd.whole)
                if 'Draft: not public' not in whole or 'Safety review pending' not in whole or 'human safety review is required' not in whole:
                    raise ValueError(channel+': missing explicit draft/safety warning')
                digests[channel]=hashlib.sha256(raw).hexdigest()
            article_rows.append({'article':n,'original_blob_sha1':sha(original),
                                 'citation_occurrences':len(CITE.findall(src)),
                                 'render_sha256':digests,'source_review':'REQUIRED'})
        return {'schema':SCHEMA,'state':HOLD,'errors':[], 'articles':article_rows,
                'human_source_claim_review':'REQUIRED','independent_qd_pass':False,
                'publication_authorized':False,'medical_safety_verified':False,
                'issue':136,'conversion_issue':820}
    except (TypeError,ValueError,UnicodeError,KeyError,IndexError,AttributeError) as exc:
        return invalid(str(exc))


def main(argv=None):
    parser=argparse.ArgumentParser(description='R215 read-only draft parity gate; output is ALWAYS HOLD or INVALID')
    for name in ('dossier','original7','original20','wp7','wp20','preview7','preview20'):
        parser.add_argument('--'+name,required=True,type=Path)
    args=parser.parse_args(argv)
    try:
        dossier=json.loads(args.dossier.read_text(encoding='utf-8'))
        originals={7:args.original7.read_bytes(),20:args.original20.read_bytes()}
        rendered={7:{'wp':args.wp7.read_bytes(),'preview':args.preview7.read_bytes()},
                  20:{'wp':args.wp20.read_bytes(),'preview':args.preview20.read_bytes()}}
        report=evaluate(dossier,originals,rendered)
    except (OSError,ValueError,TypeError,UnicodeError) as exc:
        report=invalid('read-only input error: '+str(exc))
    print(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False))
    return 2 if report['state']==HOLD else 3

if __name__=='__main__':
    raise SystemExit(main())
