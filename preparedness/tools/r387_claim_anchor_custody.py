"""R387: fail-closed, review-only original CLAIM -> rendered citation-position custody.

R386 checks prose parity and aggregate footnote order; R387 checks the *attachment*
of each citation to its original prose block and exact word boundary. Moving
unchanged citations between identical words/paragraphs is not acceptable.
Matching is NOT semantic, safety, QD or publishing approval. Never writes files.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
BLOCK = {'p','li','h1','h2','h3','h4','h5','h6','blockquote','td','th','figcaption','dt','dd'}
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
WORD = re.compile(r"\b[\w]+(?:['’-][\w]+)*\b")
ANCHOR = re.compile(r'#src-([1-9][0-9]*)\Z')
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}


def dependency(name):
    spec=importlib.util.spec_from_file_location(name, HERE / (name+'.py'))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ClaimParser(HTMLParser):
    """Read visible claim prose and its citation tokens; reject ambiguous markup.

    A citation inside a BLOCK has a single word-boundary position. The parser
    ignores footnote superscript label text, but never ignores its anchor.
    """
    def __init__(self, rendered:bool):
        super().__init__(convert_charrefs=True)
        self.rendered=rendered
        self.stack=[]
        self.claim=None
        self.claim_depth=0
        self.rows=[]
        self.errors=[]
        self.sup=None

    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if len(a)!=len(attrs): self.errors.append('DUPLICATE_HTML_ATTRIBUTE')
        if self.sup is not None:
            if tag not in VOID:self.sup['tags'].append(tag)
            if tag=='a':
                self.sup['links'].append(a.get('href'))
            return
        if tag=='sup' and 'pa-cite' in (a.get('class') or '').split():
            self.sup={'tags':['sup'],'links':[]}
            return
        if tag in BLOCK:
            if self.claim is None:
                self.claim={'tag':tag,'tokens':[]}
                self.claim_depth=1
            else: self.claim_depth+=1
        if tag not in VOID: self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        if self.sup is not None:
            if tag=='a':self.sup['links'].append(dict(attrs).get('href'))
            return
        if tag in BLOCK: self.errors.append('SELF_CLOSED_CLAIM_BLOCK')

    def handle_endtag(self, tag):
        if self.sup is not None:
            if not self.sup['tags'] or tag!=self.sup['tags'][-1]:
                self.errors.append('MALFORMED_CITATION_NESTING')
            if tag in self.sup['tags']:
                while self.sup['tags']:
                    last=self.sup['tags'].pop()
                    if last==tag:break
            if not self.sup['tags']:
                links=self.sup['links']
                if len(links)!=1 or not isinstance(links[0],str) or not ANCHOR.fullmatch(links[0]):
                    self.errors.append('MALFORMED_CLAIM_CITATION')
                else:
                    self.marker(int(ANCHOR.fullmatch(links[0]).group(1)))
                self.sup=None
            return
        if self.stack:
            if self.stack[-1]!=tag: self.errors.append('MALFORMED_CLAIM_HTML')
            if tag in self.stack:
                while self.stack:
                    tail=self.stack.pop()
                    if tail==tag:break
        else: self.errors.append('UNEXPECTED_CLOSING_TAG')
        if tag in BLOCK and self.claim is not None:
            self.claim_depth-=1
            if self.claim_depth==0:
                self.rows.append(self.claim)
                self.claim=None

    def marker(self, value):
        if self.claim is None: self.errors.append('ORPHAN_CITATION_OUTSIDE_CLAIM')
        else:self.claim['tokens'].append(('cite',value))

    def handle_data(self, value):
        if self.sup is not None:return
        if self.claim is None:
            if CITE.search(value):self.errors.append('ORPHAN_CITATION_OUTSIDE_CLAIM')
            return
        if self.rendered:
            self.claim['tokens'].append(('text',value))
        else:
            pos=0
            for m in CITE.finditer(value):
                self.claim['tokens'].append(('text',value[pos:m.start()]))
                self.marker(m.group(1))
                pos=m.end()
            self.claim['tokens'].append(('text',value[pos:]))

    def finish(self, html):
        self.feed(html)
        self.close()
        if self.sup is not None:self.errors.append('UNCLOSED_CITATION')
        if self.claim is not None:self.errors.append('UNCLOSED_CLAIM_BLOCK')
        if self.stack:self.errors.append('UNCLOSED_HTML_TAG')
        return self


def _positions(row):
    txt=''; marks=[]
    for kind,value in row['tokens']:
        if kind=='text':txt+=value
        else:marks.append((value,len(WORD.findall(txt))))
    normalized=' '.join(txt.split())
    return {'tag':row['tag'],'prose_sha256':hashlib.sha256(normalized.casefold().encode()).hexdigest(),
            'marks':marks}


def compare_claim_positions(original:bytes|str, rendered:str):
    """Immutable original body and paired private rendering; no release PASS."""
    if isinstance(original,bytes):original=original.decode('utf-8')
    if not isinstance(original,str) or not isinstance(rendered,str):
        return ['INVALID_CLAIM_INPUT']
    o=ClaimParser(False).finish(original)
    r=ClaimParser(True).finish(rendered)
    errors=['ORIGINAL:'+x for x in o.errors]+['RENDERED:'+x for x in r.errors]
    source_order=list(dict.fromkeys(v for row in o.rows for kind,v in row['tokens'] if kind=='cite'))
    number_by_id={v:i+1 for i,v in enumerate(source_order)}
    left=[_positions(row) for row in o.rows]
    right=[_positions(row) for row in r.rows]
    if len(left)!=len(right):errors.append('CLAIM_BLOCK_COUNT_DRIFT')
    for i,(a,b) in enumerate(zip(left,right),start=1):
        if a['tag']!=b['tag'] or a['prose_sha256']!=b['prose_sha256']:
            errors.append(f'CLAIM_PROSE_OR_TAG_DRIFT:{i}')
        original_marks=[(number_by_id[id],ordinal) for id,ordinal in a['marks']]
        if original_marks!=b['marks']:
            errors.append(f'CITATION_CLAIM_BOUNDARY_DRIFT:{i}')
    if len(source_order)!=len(set(source_order)):
        errors.append('DUPLICATE_ORIGINAL_SOURCE_ID')
    return sorted(set(errors))


def audit_original_candidates(packet, wp_dir:Path, read_blob):
    """Every authentic variant considered; none automatically elected."""
    results=[];errors=[]
    if packet.get('status')!='REVIEW_PACKET_HARD_HOLD' or packet.get('publication_approved') is not False or packet.get('qualified_safety_approved') is not False:
        return {'status':'INVALID_HARD_HOLD','errors':['UNAUTHENTIC_PACKET'], 'publication_approved':False}
    r386=dependency('r386_rendered_citation_parity')
    if len(packet.get('articles',[]))!=35 or len(packet.get('unselected_conflicts',[]))!=9:
        errors.append('ORIGINAL_INVENTORY_MISMATCH')
    for article in packet.get('articles',[]):
        slug=article['slug']
        if not isinstance(slug,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',slug):
            errors.append('INVALID_ORIGINAL_SLUG');continue
        file=wp_dir/(slug+'.html')
        if not file.is_file() or file.is_symlink():
            errors.append(slug+':MISSING_OR_SYMLINK_EXPORT');continue
        try:
            if file.stat().st_size>3_000_000:raise ValueError('OVERSIZED_EXPORT')
            html=file.read_text(encoding='utf-8')
            t=r386.Subtree('div','pa-article'); outer=t.take(html)
            body=r386.Subtree('div','pa-body'); rendered=body.take(outer)
            if t.errors or body.errors:raise ValueError('SUBTREE_INVALID')
            matches=[]; mismatches={}
            for v in article['variants']:
                raw=read_blob(v['body_sha'])
                if not isinstance(raw,bytes) or r386._load_r384().blob_sha(raw)!=v['body_sha']:
                    raise ValueError('ORIGINAL_GIT_BLOB_MISMATCH')
                issues=compare_claim_positions(raw,rendered)
                if issues:mismatches[v['branch']]=issues
                else:matches.append({'branch':v['branch'],'body_sha':v['body_sha']})
            if not matches:errors.append(slug+':NO_VARIANT_PRESERVES_CLAIM_CITATION_POSITIONS')
            results.append({'slug':slug,'matching_original_candidates':matches,'candidate_errors':mismatches})
        except (OSError,UnicodeError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as exc:
            errors.append(slug+':CANNOT_VALIDATE_ORIGINAL:'+type(exc).__name__)
    return {'schema':1,'status':'INVALID_HARD_HOLD' if errors else 'CLAIM_POSITION_REVIEW_HARD_HOLD',
            'release_state':'DRAFT_HARD_HOLD','publication_approved':False,'qualified_safety_approved':False,
            'offer_approved':False,'errors':sorted(set(errors)),'articles':results,
            'counts':{'original_articles':len(packet.get('articles',[])),'checked_exports':len(results),'unselected_forks':len(packet.get('unselected_conflicts',[]))}}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo',default='.')
    ap.add_argument('--wp',default='preparedness/build/wp')
    ap.add_argument('--preview',default='preparedness/build/preview')
    args=ap.parse_args(argv)
    try:
        r384=dependency('r384_variant_review_packet')
        r386=dependency('r386_rendered_citation_parity')
        def reader(sha):
            data=subprocess.run(['git','-C',args.repo,'cat-file','blob',sha],check=True,capture_output=True,timeout=20).stdout
            if r384.blob_sha(data)!=sha:raise ValueError('BLOB_SHA_MISMATCH')
            return data
        manifest=json.loads(reader(r386.ORIGINAL_MANIFEST_BLOB))
        packet=r384.build_packet(manifest,reader)
        if packet['status']!='REVIEW_PACKET_HARD_HOLD':raise ValueError('ORIGINAL_PACKET_INVALID')
        result=audit_original_candidates(packet,Path(args.wp),reader)
        # R386 remains independent/mandatory; R387 is strictly additive and cannot be substituted for it.
        result['r386_native_parity_required']=True
        result['private_preview_validation_required']=True
    except (OSError,ValueError,TypeError,UnicodeError,subprocess.SubprocessError,json.JSONDecodeError) as exc:
        result={'status':'INVALID_HARD_HOLD','release_state':'DRAFT_HARD_HOLD',
                'publication_approved':False,'qualified_safety_approved':False,
                'errors':['AUTHENTIC_ORIGINALS_UNAVAILABLE:'+type(exc).__name__]}
    print(json.dumps(result,sort_keys=True,indent=2))
    return 2

if __name__=='__main__':raise SystemExit(main())
