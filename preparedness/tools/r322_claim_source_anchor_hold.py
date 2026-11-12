#!/usr/bin/env python3
"""Read-only claim-to-source anchor drift witnesses for unresolved Preparedness conflicts.

Never infer truth, medical safety, qualified review, approval, publishability or
sales from a matching citation. Only compare pinned, exact Git objects and emit
conservative privacy-preserving reviewer flags; never select contributor text.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import unicodedata

PARENT = Path(__file__).with_name('r321_conflict_content_delta_hold.py')
if PARENT.is_symlink():
    raise RuntimeError('linked previous gate')
spec = importlib.util.spec_from_file_location('fv_r321_parent', PARENT)
if spec is None or spec.loader is None:
    raise RuntimeError('missing previous gate')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)

SCHEMA = 'fv-preparedness-r322-claim-source-anchor-drift-v1'
HOLD = dict(prior.HOLD)
CITATION_RE = re.compile(r'\{\{cite:([a-z0-9][a-z0-9-]{1,99})\}\}')
CITE_POSSIBLE = re.compile(r'\{\{cite:', re.I)
BLOCKS = frozenset('p li h1 h2 h3 h4 h5 h6 blockquote dt dd td th summary figcaption'.split())
VOID = frozenset('area base br col embed hr img input link meta param source track wbr'.split())
HIDDEN_STYLE = re.compile(r'(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*(?:hidden|collapse)|opacity\s*:\s*0(?:\.0+)?(?:\s*!important)?)(?:\s*;|\s*$)',re.I)
WARNINGS = {'do not':r'\bdo\s+not\b', 'never':r'\bnever\b',
    'medical':r'\bmedical\b','carbon monoxide':r'\bcarbon\s+monoxide\b',
    '911':r'\b911\b', 'not safe':r'\bnot\s+safe\b',
    'child':r'\bchild(?:ren)?\b', 'official instructions':r'\bofficial\s+instructions\b',
    'boil':r'\bboil\b', 'generator':r'\bgenerator\b'}


def normalize(s: str) -> str:
    return ' '.join(unicodedata.normalize('NFKC', s).split())


def witness(s: str) -> str:
    return hashlib.sha256(normalize(s).encode('utf-8')).hexdigest()


class Claims(HTMLParser):
    """Conservative HTML claim inventory; browser-equivalence is separately gated."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags: list[tuple[str,bool]] = []
        self.blocks: list[dict] = []
        self.active: list[tuple[str,dict|None]] = []
        self.hidden_citations: list[str] = []
        self.orphan_citations: list[str] = []
        self.malformed_citations = 0
        self.outside_text: list[str] = []
        self.raw_citation_mentions = 0

    def _hidden(self) -> bool:
        return any(hidden for _,hidden in self.tags)

    def _new_block(self, tag: str):
        obj = {'tag':tag,'parts':[], 'cites':[]}
        self.blocks.append(obj)
        self.active.append((tag,obj))

    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        hidden=tag in {'script','style','template','noscript'} or 'hidden' in a
        hidden |= str(a.get('aria-hidden','')).lower() == 'true'
        hidden |= bool(HIDDEN_STYLE.search(str(a.get('style',''))))
        for k,v in attrs:
            if isinstance(v,str) and CITE_POSSIBLE.search(v):
                self.hidden_citations.extend(CITATION_RE.findall(v))
                self.raw_citation_mentions+=len(CITATION_RE.findall(v))
                if len(CITATION_RE.findall(v))!=v.lower().count('{{cite:'):
                    self.malformed_citations+=1
        if tag not in VOID: self.tags.append((tag,bool(hidden)))
        if tag in BLOCKS:
            self._new_block(tag)

    def handle_startendtag(self,tag,attrs):
        self.handle_starttag(tag,attrs)
        if tag not in VOID:self.handle_endtag(tag)

    def handle_endtag(self,tag):
        # HTMLParser does not emulate the browser. Fail closed for malformed stacks
        # rather than removing an unrelated ancestor's hidden flag.
        i=next((j for j in range(len(self.tags)-1,-1,-1) if self.tags[j][0]==tag),-1)
        if i>=0:self.tags=self.tags[:i]
        for i in range(len(self.active)-1,-1,-1):
            if self.active[i][0]==tag:
                self.active=self.active[:i]
                break

    def handle_comment(self,data):
        matches=CITATION_RE.findall(data)
        self.hidden_citations.extend(matches)
        self.raw_citation_mentions+=len(matches)
        if data.lower().count('{{cite:')!=len(matches):self.malformed_citations+=1

    def handle_data(self,data):
        if not data.strip():return
        cites=CITATION_RE.findall(data)
        self.raw_citation_mentions+=len(cites)
        if data.lower().count('{{cite:')!=len(cites):self.malformed_citations+=1
        if self._hidden():
            self.hidden_citations.extend(cites)
            return
        cleaned=CITATION_RE.sub(' ',data)
        if self.active:
            block=self.active[-1][1]
            if block is not None:
                block['parts'].append(cleaned)
                block['cites'].extend(cites)
        else:
            # Authored citation token outside a recognized claim must not be
            # silently treated as proof of support.
            self.orphan_citations.extend(cites)
            self.outside_text.append(cleaned)


def claim_inventory(data: bytes) -> dict:
    html=data.decode('utf-8','strict')
    if '\x00' in html:raise ValueError('NUL byte in HTML')
    p=Claims();p.feed(html);p.close()
    anchors=[];uncited=[]
    for block in p.blocks:
        text=normalize(''.join(block['parts']))
        cites=block['cites']
        if not text and cites:p.orphan_citations.extend(cites)
        if not text:continue
        sig=witness(text)
        if cites:
            for c in cites:anchors.append((sig,c,block['tag']))
        else:uncited.append((sig,block['tag']))
    return {'anchors':anchors,'uncited':uncited,
            'visible_citation_ids':sorted({c for _,c,_ in anchors}),
            'hidden_citation_ids':sorted(p.hidden_citations),
            'orphan_citation_ids':sorted(p.orphan_citations),
            'malformed_citation_count':p.malformed_citations,
            'raw_citation_mentions':p.raw_citation_mentions,
            'block_count':sum(bool(normalize(''.join(x['parts']))) for x in p.blocks),
            'warning_counts':{k:len(re.findall(pattern,html,re.I)) for k,pattern in WARNINGS.items()}}


def compare_claims(before:bytes, after:bytes) -> dict:
    a,b=claim_inventory(before),claim_inventory(after)
    ac,bc=Counter(a['anchors']),Counter(b['anchors'])
    lost=list((ac-bc).elements());new=list((bc-ac).elements())
    # Only claim hash + source ID + tag, not private household strings.
    before_refs=Counter(x[1] for x in a['anchors'])
    after_refs=Counter(x[1] for x in b['anchors'])
    warnings={k:v for k,v in a['warning_counts'].items()
              if v > b['warning_counts'].get(k,0)}
    return {'before_claim_blocks':a['block_count'], 'after_claim_blocks':b['block_count'],
            'before_visible_citations':sum(before_refs.values()),
            'after_visible_citations':sum(after_refs.values()),
            'removed_claim_source_anchors':sorted([{'claim_sha256':h,'source_id':s,'tag':t} for h,s,t in lost],key=lambda x:(x['source_id'],x['claim_sha256'],x['tag'])),
            'new_claim_source_anchors':sorted([{'claim_sha256':h,'source_id':s,'tag':t} for h,s,t in new],key=lambda x:(x['source_id'],x['claim_sha256'],x['tag'])),
            'removed_source_ids':sorted((before_refs-after_refs).elements()),
            'new_source_ids':sorted((after_refs-before_refs).elements()),
            'warning_cue_decreases':warnings,
            'hidden_citation_count':len(b['hidden_citation_ids']),
            'orphan_citation_count':len(b['orphan_citation_ids']),
            'malformed_citation_count':b['malformed_citation_count'],
            'requires_claim_level_review':True}


def source_use_audit(body:bytes, metadata:bytes) -> dict:
    inv=claim_inventory(body);meta=prior.strict_json(metadata)
    if not isinstance(meta,dict):raise ValueError('nonobject metadata')
    source_use=meta.get('source_use')
    if not isinstance(source_use,dict) or any(not isinstance(k,str) or not isinstance(v,str) for k,v in source_use.items()):
        # Treat missing declarations as hold, not as a successful crosswalk.
        return {'state':'SOURCE_USE_UNAVAILABLE_HOLD','cited_without_source_use':inv['visible_citation_ids'],
                'declared_without_visible_citation':[], 'qualified_approval':False}
    visible=set(inv['visible_citation_ids']);declared=set(source_use)
    st=meta.get('status')
    pub=(st.get('publish') if isinstance(st,dict) else None)
    return {'state':'SOURCE_USE_MISMATCH_HOLD' if visible-declared else 'SOURCE_USE_PRESENT_REVIEW_HOLD',
            'cited_without_source_use':sorted(visible-declared),
            'declared_without_visible_citation':sorted(declared-visible),
            'publish_status':pub,
            'unsafe_release_state':pub!='draft',
            'qualified_approval':False}


def build_report(manifest:dict,docket:dict,loader) -> dict:
    prior_report=prior.build_report(manifest,docket,loader)
    errors=list(prior_report['errors']); rows=[]
    if not errors:
        bypath={x['path']:x for x in manifest['records']}
        for docket_row in docket['records']:
            path=docket_row['path']
            if not path.endswith('.body.html'):continue
            record=bypath[path]
            objects={}
            for variant in prior.REVIEW_VERSIONS:
                ref=record.get(variant)
                if ref is None:continue
                try:objects[variant]=prior.read_verified_blob(ref,loader)
                except (ValueError,KeyError,OSError,UnicodeError) as e:
                    errors.append('BAD_PINNED_BODY:'+path+':'+variant+':'+type(e).__name__)
            if 'integrated' not in objects:
                errors.append('NO_BASELINE_BODY:'+path);continue
            comparisons={};source_uses={}
            meta_record=bypath.get(path.replace('.body.html','.meta.json'))
            for variant,body in objects.items():
                try:
                    if variant!='integrated':comparisons[variant]=compare_claims(objects['integrated'],body)
                    if meta_record and meta_record.get(variant):
                        m=prior.read_verified_blob(meta_record[variant],loader)
                        source_uses[variant]=source_use_audit(body,m)
                    else:source_uses[variant]={'state':'NO_PINNED_VARIANT_METADATA_HOLD','qualified_approval':False}
                except (ValueError,UnicodeError,TypeError,OSError) as e:
                    errors.append('INVALID_AUTHORED_CLAIM_EVIDENCE:'+path+':'+variant+':'+type(e).__name__)
            rows.append({'path':path,'severity':docket_row['severity'],
                         'source_refs':docket_row['source_refs'],
                         'comparisons':comparisons,'source_use_crosswalk':source_uses,
                         'status':'UNRESOLVED_HOLD','qualified_review':False})
    return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors':sorted(set(errors)),'body_conflicts_audited':len(rows),
            'source_docket_conflicts_held':prior_report['review_count'],
            'release':HOLD.copy(),'rows':rows}


def main() -> int:
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);args=ap.parse_args()
    try:
        root=args.root.resolve(strict=True)
        mpath=root/prior.review.SOURCE_MANIFEST_PATH
        dpath=root/'preparedness/audits/r320_conflict_adjudication_docket.json'
        if not (root/'.git').exists() or mpath.is_symlink() or dpath.is_symlink():
            raise ValueError('AUTHENTIC_CHECKOUT_REQUIRED')
        m=prior.strict_json(mpath.read_bytes());d=prior.strict_json(dpath.read_bytes())
        r=build_report(m,d,prior._git_loader(root))
        if prior.review.custody.validate_manifest(m,root)['errors']:
            r['errors'].append('NATIVE_SOURCE_CUSTODY_FAILURE');r['state']='INVALID_HARD_HOLD'
    except (OSError,ValueError,TypeError,UnicodeError) as e:
        r={'schema':SCHEMA,'state':'INVALID_HARD_HOLD',
           'errors':['AUTHENTIC_CHECKOUT_REQUIRED:'+type(e).__name__],
           'body_conflicts_audited':0,'source_docket_conflicts_held':0,
           'release':HOLD.copy(),'rows':[]}
    print(json.dumps(r,sort_keys=True,indent=2))
    return 2 if r['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__':raise SystemExit(main())
