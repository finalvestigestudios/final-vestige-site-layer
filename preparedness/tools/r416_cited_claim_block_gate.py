#!/usr/bin/env python3
"""R416 original-cited-claim block escrow. Review-only; NEVER a safety release.

An unchanged anchor and its immediate 9-token neighbors do not preserve a
nonwarning assertion elsewhere in the paragraph that the source was meant to
support. This gate pins the entire normalized citation-bearing block (or, for
standalone anchors, its preceding evidence block) to each authenticated original
Git blob, and applies the comparison to WordPress and private preview separately.
It also quarantines newly inserted high-consequence instructions outside cited
blocks. It does NOT decide factual truth, citation scope, or article selection.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from html.parser import HTMLParser
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re

_spec = spec_from_file_location('r415_global_citation_alignment_gate', Path(__file__).with_name('r415_global_citation_alignment_gate.py'))
_r415 = module_from_spec(_spec)
_spec.loader.exec_module(_r415)
_r414 = _r415._r414
_r412 = _r415._r412
WORDS = _r414.WORD
CITE = _r414.MARKER
BLOCKS = {'p', 'li', 'blockquote', 'td', 'th', 'figcaption', 'dt', 'dd', 'h1','h2','h3','h4','h5','h6'}
MAX_BLOCK_WORDS = 5000
MAX_DOCUMENT_WORDS = 12000
# Screening only; not an automated finding that any particular advice is unsafe.
RISK_WORDS = frozenset({'boil', 'boiling', 'sanitize', 'sanitizing', 'disinfect',
  'disinfection', 'bleach', 'dose', 'dosage', 'medicine', 'medication', 'medical',
  'injury', 'emergency', 'potable', 'drink', 'drinking', 'canning', 'curing',
  'dehydration', 'freeze', 'freezing', 'generator', 'carbon', 'monoxide',
  'sterilize', 'sterilization', 'pressure', 'temperature', 'treatment'})
ASSERT_WORDS = frozenset({'must','should','always','never','safe','unsafe','guaranteed',
  'recommended','recommend','required','requires','necessary','use','avoid',
  'remove','removes','prevents','protects','prevention','approved','proven'})


@dataclass
class Block:
    tag: str
    words: list[str] = field(default_factory=list)


class Extract(HTMLParser):
    """Text-only blocks with each citation bound to one explicit reader block."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks: list[Block] = []
        self.open_blocks: list[int] = []
        self.markers: list[tuple[str,int | None]] = []
        self.last_block: int | None = None
        self.all_words: list[str] = []
        self.invalid = False
        self.ignored: list[str] = []

    def handle_starttag(self, tag, attrs):
        tag = tag.casefold()
        if tag in {'script','style','template','noscript'}:
            self.ignored.append(tag)
        if self.ignored:
            return
        if tag in BLOCKS:
            if self.open_blocks:
                # Nested list-item/blockquote can legitimately contain paragraphs;
                # attach text only to innermost block, never merge two claims.
                pass
            self.blocks.append(Block(tag))
            self.open_blocks.append(len(self.blocks)-1)
        if tag == 'a':
            ids = [v for k,v in attrs if k.casefold() == 'data-source-id']
            if len(ids)>1:
                raise ValueError('repeated citation identifier attribute')
            if ids:
                if not isinstance(ids[0],str) or not _r414.SLUG.fullmatch(ids[0]):
                    raise ValueError('invalid citation identifier')
                self.markers.append((ids[0],self.open_blocks[-1] if self.open_blocks else self.last_block))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag,attrs)
        if tag.casefold() in BLOCKS:
            self.handle_endtag(tag)

    def handle_data(self, text):
        if self.ignored:
            return
        words = [w.casefold() for w in WORDS.findall(text)]
        self.all_words.extend(words)
        if self.open_blocks:
            self.blocks[self.open_blocks[-1]].words.extend(words)
        if len(self.all_words)>MAX_DOCUMENT_WORDS:
            raise ValueError('claim block document word limit exceeded')

    def handle_endtag(self, tag):
        tag = tag.casefold()
        if self.ignored:
            if tag == self.ignored[-1]:
                self.ignored.pop()
            return
        if tag in BLOCKS:
            if not self.open_blocks or self.blocks[self.open_blocks[-1]].tag != tag:
                # Previous structural parser also enforces HTML balance; fail closed.
                raise ValueError('unbalanced claim block markup')
            self.last_block=self.open_blocks.pop()

    def finish(self):
        self.close()
        if self.open_blocks or self.ignored:
            raise ValueError('unclosed claim block markup')
        if any(len(b.words)>MAX_BLOCK_WORDS for b in self.blocks):
            raise ValueError('citation claim block oversized')
        return self


def markdown_blocks(text):
    """For source candidates with Markdown citation tokens, preserve paragraphs."""
    text=re.sub(r'\A---\s*\n.*?\n---\s*\n','',text,flags=re.S)
    text=re.sub(r'!\[[^]]*]\([^)]*\)',' ',text)
    text=re.sub(r'\[([^]]+)]\([^)]*\)',r'\1',text)
    out=Extract()
    for group in re.split(r'\n\s*\n',text):
        if not group.strip():
            continue
        body=group.strip()
        tag = 'h1' if re.match(r'^#\s',body) else 'p'
        idx=len(out.blocks); out.blocks.append(Block(tag))
        last=0
        for citation in CITE.finditer(body):
            out.blocks[idx].words.extend(w.casefold() for w in WORDS.findall(body[last:citation.start()]))
            out.markers.append((citation.group(1),idx))
            last=citation.end()
        out.blocks[idx].words.extend(w.casefold() for w in WORDS.findall(body[last:]))
        out.all_words.extend(out.blocks[idx].words)
        if len(out.all_words)>MAX_DOCUMENT_WORDS:
            raise ValueError('claim block document word limit exceeded')
    return out


def extract(data, *, candidate=False):
    if isinstance(data,bytes):
        data=data.decode('utf-8','strict')
    if not isinstance(data,str) or not 0<len(data.encode('utf-8'))<=1_000_000:
        raise ValueError('invalid claim block input')
    if candidate and not re.search(r'<(?:article|section|p|h[1-6]|div)\b',data[:2000],re.I):
        return markdown_blocks(data)
    p=Extract();p.feed(data);return p.finish()


def signatures(document):
    """Ordered occurrence-specific block signatures; do not deduplicate sources."""
    result=[]
    for sid,idx in document.markers:
        if idx is None or idx<0 or idx>=len(document.blocks):
            raise ValueError('source anchor missing source-associated evidence block')
        words=document.blocks[idx].words
        if not words:
            raise ValueError('citation associated with empty evidence block')
        result.append((sid,tuple(words)))
    return result


def risk_slices(document):
    """Screen added standalone safety instructions; this is not medical validation."""
    out=Counter()
    for block in document.blocks:
        w=tuple(block.words)
        if len(w)>=3 and any(t in RISK_WORDS for t in w) and any(t in ASSERT_WORDS for t in w):
            out[w]+=1
    return out


def check(original,manifest,exports,candidates,*,raw_original=None,test_only=False):
    parent=_r415.check(original,manifest,exports,candidates,raw_original=raw_original,test_only=test_only)
    errors=list(parent.get('errors',[])); details=[]
    try:
        for entry in original['original_articles']:
            slug=entry['slug']
            pair=exports[slug]
            rendered=[extract(h) for h in pair]
            rsign=[signatures(d) for d in rendered]
            if rsign[0]!=rsign[1]:
                errors.append('R416 WordPress/private cited-block parity diverged: '+slug)
            for pin in sorted(set(entry['body_candidate_git_blobs'])):
                candidate=candidates[(slug,pin)]
                if not isinstance(candidate,bytes) or _r412._r409.blob(candidate)!=pin:
                    errors.append('R416 original candidate Git blob mismatch: '+slug)
                    continue
                src=extract(candidate,candidate=True)
                original_sig=signatures(src)
                for idx, draft in enumerate(rendered):
                    target='wordpress' if idx==0 else 'private_preview'
                    structural_mismatch=(original_sig!=rsign[idx])
                    if structural_mismatch:
                        errors.append('R416 original cited evidence block modified or detached: '+slug+' @ '+pin+' '+target)
                    new_risk=sum((risk_slices(draft)-risk_slices(src)).values())
                    if new_risk:
                        errors.append('R416 new unreviewed high-consequence instruction: '+slug+' @ '+pin+' '+target)
                    details.append({'slug':slug,'original_blob':pin,'target':target,
                        'inline_sources':len(original_sig),'cited_block_drift':int(structural_mismatch),
                        'new_high_consequence_blocks':new_risk,'source_scope_human_review_required':True})
    except (TypeError,ValueError,KeyError,IndexError,UnicodeError,AttributeError,OverflowError) as exc:
        errors.append('R416 malformed cited-block provenance: '+str(exc))
    return {'release_state':'DRAFT_HARD_HOLD','eligible':False,'publication_approved':False,
        'qualified_safety_approved':False,'integrity_ok':bool(parent.get('integrity_ok')) and not errors,
        'errors':sorted(set(errors)),'draft_checks':len(details),'details':details,
        'warnings':list(parent.get('warnings',[]))+[
          'Cited-block text fidelity does not establish the source actually supports a claim',
          'Screened new risk instructions require qualified human review; false positives are held',
          'Preserve every unselected original candidate, source dispute, and review gate; no publication']}


def main():
    ap=argparse.ArgumentParser(description='R416 cited claim block escrow — ALWAYS HARD HOLD')
    for f in ('original','manifest','export_root','private_candidate_root'):
        ap.add_argument(f,type=Path)
    a=ap.parse_args()
    try:
        raw=_r412._r409.read_original(a.original)
        original=json.loads(raw.decode('utf-8'),object_pairs_hook=_r412._r409.unique_pairs)
        manifest=json.loads(_r412._r409.read_original(a.manifest).decode('utf-8'),object_pairs_hook=_r412._r409.unique_pairs)
        exports,candidates={},{}
        for entry in original['original_articles']:
            slug=entry['slug']
            if not isinstance(slug,str) or not _r414.SLUG.fullmatch(slug):
                raise ValueError('unsafe original article slug')
            exports[slug]=(_r412._r409.read_original(a.export_root/'wordpress'/(slug+'.html')),
                           _r412._r409.read_original(a.export_root/'preview'/(slug+'.html')))
            for pin in set(entry['body_candidate_git_blobs']):
                if not isinstance(pin,str) or not _r412.HEX40.fullmatch(pin):
                    raise ValueError('unsafe Git blob SHA')
                candidates[(slug,pin)]=_r412.checked_candidate_read(
                    a.private_candidate_root/slug/(pin+'.txt'),root=a.private_candidate_root)
        result=check(original,manifest,exports,candidates,raw_original=raw)
    except (OSError,TypeError,ValueError,KeyError,IndexError,UnicodeError,OverflowError) as exc:
        result={'release_state':'DRAFT_HARD_HOLD','eligible':False,'publication_approved':False,
                'qualified_safety_approved':False,'integrity_ok':False,'errors':[str(exc)]}
    print(json.dumps(result,sort_keys=True,indent=2));return 2


if __name__=='__main__':
    raise SystemExit(main())
