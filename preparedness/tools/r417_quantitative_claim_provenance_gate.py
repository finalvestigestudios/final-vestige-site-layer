#!/usr/bin/env python3
"""R417 fail-closed original-quantitative-claim custody, not safety/medical QA.

R416 protects cited paragraphs and checks a small subset of *added* uncited
instructions. A date, measurement, count or threshold in an uncited ORIGINAL
paragraph can nonetheless be changed in both exports while passing R416.
This overlay preserves original numerical evidence in both private renderings,
records candidate-specific review failures, and screens newly inserted numerical
instructions even when they omit R416's mandatory/medical keywords. Source
truth, real-world applicability, currentness and permission remain human gates.
"""
from __future__ import annotations
import argparse
from collections import Counter
from difflib import SequenceMatcher
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys

_spec=spec_from_file_location('r416_cited_claim_block_gate',Path(__file__).with_name('r416_cited_claim_block_gate.py'))
_r416=module_from_spec(_spec)
sys.modules[_spec.name]=_r416
_spec.loader.exec_module(_r416)
_r412=_r416._r412
_r409=_r412._r409
_r414=_r416._r414
HEX40=_r412.HEX40
# Lexical screening only. Not a dosage parser, trusted source list, or advice review.
NUM=re.compile(r'^\d+(?:[.,]\d+)*$', re.ASCII)
QUANTITY_WORDS=frozenset({'zero','one','two','three','four','five','six','seven',
'eight','nine','ten','dozen','half','quarter','percent','percentage'})
UNITS=frozenset({'hour','hours','minute','minutes','day','days','week','weeks',
'fahrenheit','celsius','degrees','degree','milligram','milligrams','mg',
'gram','grams','ounce','ounces','pound','pounds','cup','cups','liter','liters',
'litre','litres','gallon','gallons','ppm','tablets','tablet','pills','pill',
'drops','drop','times','percent','percentage','minutes','seconds','second'})
ACTION_WORDS=frozenset({'give','take','feed','mix','dilute','use','administer','add',
'keep','wait','store','drink','eat','boil','freeze','heat','cool','treat',
'disinfect','replace','dose','measure','prepare','leave','cook','refrigerate',
'stop','start','repeat','remove','apply','avoid','increase','decrease',
'recommended','recommend','sufficient','safe','unsafe','must','should'})
HIGH_RISK=frozenset({'child','children','baby','babies','pet','pets','tablet',
'pills','pill','tablets','medicine','medication','dose','dosage','bleach',
'water','food','meat','jerky','canning','generator','fuel','carbon','monoxide',
'emergency','freezer','refrigerator','heat','illness','injury','medical',
'infant','infants','sterilization','disinfection','temperature','danger',
'drink','drinking','boil','boiling','treatment','treat','refrigerate'})
MAX_BLOCKS=2000


def has_number(words):
    return any(NUM.fullmatch(x) or x in QUANTITY_WORDS for x in words)


def block_words(parsed):
    seq=[tuple(block.words) for block in parsed.blocks if block.words]
    if len(seq)>MAX_BLOCKS: raise ValueError('excessive original/rendered block count')
    return seq


def cited_blocks(parsed):
    return {idx for _,idx in parsed.markers if idx is not None}


def quantitative_original(parsed):
    """Original numeric blocks lacking inline anchors; source order retained."""
    cites=cited_blocks(parsed)
    return [(i, tuple(b.words)) for i,b in enumerate(parsed.blocks)
            if i not in cites and b.words and has_number(b.words)]


def numeric_action_blocks(parsed):
    """Conservatively quarantine novel quantitative household instruction blocks."""
    out=Counter()
    for block in parsed.blocks:
        words=tuple(block.words)
        w=set(words)
        if (has_number(words) and bool(w & ACTION_WORDS)
                and (bool(w & HIGH_RISK) or bool(w & UNITS))):
            out[words]+=1
    return out


def align_original_blocks(original,rendered):
    src=[tuple(b.words) for b in original.blocks]
    target=[tuple(b.words) for b in rendered.blocks]
    if max(len(src),len(target))>MAX_BLOCKS:
        raise ValueError('block count exceeds alignment bound')
    blocks=SequenceMatcher(None,src,target,autojunk=False).get_matching_blocks()
    return {i+k:j+k for i,j,n in blocks for k in range(n)}


def numeric_fidelity(original,rendered):
    """Count original quantitative uncited blocks lost/relocated from paired HTML.

    Exact source block identity is required. Relative order/neighbor positions
    must survive; cannot relocate a copy of a passage into a new bibliography.
    Treat edits as review blockers rather than automatic proposals to rewrite.
    """
    mapping=align_original_blocks(original,rendered)
    target=[tuple(b.words) for b in rendered.blocks]
    drift=0; count=0
    for src_idx, words in quantitative_original(original):
        count+=1
        dst_idx=mapping.get(src_idx)
        if dst_idx is None or target[dst_idx]!=words:
            drift+=1;continue
        # Anchor to immediately adjacent unmodified source blocks where present.
        # Large relocation of duplicated text is never accepted solely by text.
        prev=mapping.get(src_idx-1)
        nxt=mapping.get(src_idx+1)
        if prev is not None and not (prev<dst_idx<=prev+3):
            drift+=1;continue
        if nxt is not None and not (dst_idx<nxt<=dst_idx+3):
            drift+=1;continue
        if sum(1 for x in target if x==words)!=1:
            drift+=1
    return count,drift


def check(original,manifest,exports,candidates,*,raw_original=None,test_only=False):
    parent=_r416.check(original,manifest,exports,candidates,raw_original=raw_original,test_only=test_only)
    errors=list(parent.get('errors',[])); details=[]
    try:
        for entry in original['original_articles']:
            slug=entry['slug']
            pair=exports[slug]
            if not isinstance(pair,(tuple,list)) or len(pair)!=2:
                raise ValueError('missing paired original export')
            rendered=[_r416.extract(x) for x in pair]
            for pin in sorted(set(entry['body_candidate_git_blobs'])):
                data=candidates[(slug,pin)]
                if not isinstance(data,bytes) or _r409.blob(data)!=pin:
                    errors.append('R417 candidate blob does not match pin: '+slug)
                    continue
                src=_r416.extract(data,candidate=True)
                for idx,draft in enumerate(rendered):
                    target='wordpress' if idx==0 else 'private_preview'
                    protected,drift=numeric_fidelity(src,draft)
                    added=sum((numeric_action_blocks(draft)-numeric_action_blocks(src)).values())
                    if drift:
                        errors.append('R417 original quantitative evidence changed or displaced: '+slug+' @ '+pin+' '+target)
                    if added:
                        errors.append('R417 novel uncited or unreviewed quantitative instruction: '+slug+' @ '+pin+' '+target)
                    details.append({'slug':slug,'original_blob':pin,'target':target,
                        'original_uncited_quantitative_blocks':protected,
                        'original_quantitative_drift':drift,
                        'novel_quantitative_action_blocks':added,
                        'qualified_human_source_scope_review_required':True})
    except (ValueError,TypeError,KeyError,IndexError,UnicodeError,OverflowError,AttributeError) as e:
        errors.append('R417 missing or malformed original numeric evidence: '+str(e))
    return {'release_state':'DRAFT_HARD_HOLD','eligible':False,'publication_approved':False,
        'qualified_safety_approved':False,
        'integrity_ok':bool(parent.get('integrity_ok')) and not errors,
        'errors':sorted(set(errors)),'draft_checks':len(details),'details':details,
        'warnings':list(parent.get('warnings',[]))+[
            'Exact numeric-text custody cannot establish that a threshold is safe or source-supported',
            'All newly added or modified quantitative instructions require qualified human review',
            'Private originals and each contributor fork remain unselected; publication is always HARD HOLD']}


def main():
    ap=argparse.ArgumentParser(description='R417 original quantitative evidence escrow: ALWAYS HOLD')
    for x in ('original','manifest','export_root','private_candidate_root'):
        ap.add_argument(x,type=Path)
    a=ap.parse_args()
    try:
        raw=_r409.read_original(a.original)
        original=json.loads(raw.decode('utf-8'),object_pairs_hook=_r409.unique_pairs)
        manifest=json.loads(_r409.read_original(a.manifest).decode('utf-8'),object_pairs_hook=_r409.unique_pairs)
        exports,candidates={},{}
        for item in original['original_articles']:
            slug=item['slug']
            if not isinstance(slug,str) or not _r414.SLUG.fullmatch(slug):
                raise ValueError('unsafe original article slug')
            exports[slug]=(_r409.read_original(a.export_root/'wordpress'/(slug+'.html')),
                           _r409.read_original(a.export_root/'preview'/(slug+'.html')))
            for pin in set(item['body_candidate_git_blobs']):
                if not isinstance(pin,str) or not HEX40.fullmatch(pin):
                    raise ValueError('unsafe Git blob SHA')
                candidates[(slug,pin)]=_r412.checked_candidate_read(
                    a.private_candidate_root/slug/(pin+'.txt'),root=a.private_candidate_root)
        r=check(original,manifest,exports,candidates,raw_original=raw)
    except (OSError,TypeError,ValueError,KeyError,IndexError,UnicodeError,OverflowError) as e:
        r={'release_state':'DRAFT_HARD_HOLD','eligible':False,'publication_approved':False,
           'qualified_safety_approved':False,'integrity_ok':False,'errors':[str(e)]}
    print(json.dumps(r,sort_keys=True,indent=2));return 2

if __name__=='__main__':
    raise SystemExit(main())
