#!/usr/bin/env python3
"""R418: original ordinary uncited-claim custody and new safety-verdict quarantine.

R417 protects dates, quantities and numerical instructions, R416 cites entire
cited blocks, and R413 guards warnings/headings. Ordinary original prose outside
those classes could still be silently rewritten in *both* draft renderings. This
conservative additive review gate requires every unselected, Git-blob-pinned
original uncited block to survive verbatim after text normalization and in order.
New unreviewed high-consequence declarations get an explicit HOLD even without
numbers or imperative language. Nothing here decides source truth or safety.
"""
from __future__ import annotations
import argparse
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

_spec=spec_from_file_location('r417_quantitative_claim_provenance_gate',Path(__file__).with_name('r417_quantitative_claim_provenance_gate.py'))
_r417=module_from_spec(_spec)
sys.modules[_spec.name]=_r417
_spec.loader.exec_module(_r417)
_r416=_r417._r416
_r409=_r417._r409
_r412=_r417._r412
_r414=_r417._r414
HEX40=_r417.HEX40
HEADINGS=frozenset({'h1','h2','h3','h4','h5','h6'})
SAFETY_SUBJECT=frozenset({'water','food','meat','jerky','canning','generator',
    'medicine','medication','medications','infant','infants','baby','babies',
    'children','child','shelter','emergency','bleach','fuel','fire','power',
    'device','devices','refrigerator','freezer','pet','pets','cistern'})
SAFETY_VERDICT=frozenset({'drinkable','potable','harmless','sufficient','adequate',
    'stable','suitable','approved','guaranteed','certified','riskless','nontoxic',
    'reliable','safe','safely','effective','sterile','sterilized','fine','okay',
    'permitted','nonperishable','nonperishables'})


def baseline_blocks(parsed):
    """Ordered uncited original prose; headings and cited blocks have earlier gates."""
    used=_r417.cited_blocks(parsed)
    return [(i,tuple(block.words)) for i,block in enumerate(parsed.blocks)
            if i not in used and block.tag not in HEADINGS and block.words]


def ordinary_fidelity(original,rendered):
    """Exact whole-block custody. Adjacent new paragraphs may be added for review.

    SequenceMatcher with autojunk disabled preserves ordering; the multiplicity
    test forbids silently replaying one original paragraph as a substitute for
    another. All source candidates are checked independently, never auto-picked.
    """
    mapping=_r417.align_original_blocks(original,rendered)
    src=[tuple(b.words) for b in original.blocks]
    dst=[tuple(b.words) for b in rendered.blocks]
    protected=baseline_blocks(original)
    originals=Counter(src)
    actual=Counter(dst)
    drift=0
    for i,words in protected:
        j=mapping.get(i)
        if j is None or dst[j]!=words or actual[words]!=originals[words]:
            drift+=1
            continue
        # Where neighbors survive, this paragraph must still appear between them.
        before=mapping.get(i-1)
        after=mapping.get(i+1)
        if before is not None and j<=before or after is not None and j>=after:
            drift+=1
    return len(protected),drift


def verdict_blocks(parsed):
    """Screen unapproved safety verdicts, including nonnumerical declaratives.

    An editorial warning or accurately sourced statement may be a false positive:
    qualified human review resolves it, not this mechanical lexical detector.
    """
    found=Counter()
    for block in parsed.blocks:
        words=tuple(block.words)
        tokens=set(words)
        if tokens & SAFETY_SUBJECT and tokens & SAFETY_VERDICT:
            found[words]+=1
    return found


def check(original,manifest,exports,candidates,*,raw_original=None,test_only=False):
    parent=_r417.check(original,manifest,exports,candidates,
                       raw_original=raw_original,test_only=test_only)
    errors=list(parent.get('errors',[]));details=[]
    try:
        for entry in original['original_articles']:
            slug=entry['slug']
            pair=exports[slug]
            if not isinstance(pair,(tuple,list)) or len(pair)!=2:
                raise ValueError('missing paired draft export')
            drafts=[_r416.extract(item) for item in pair]
            for pin in sorted(set(entry['body_candidate_git_blobs'])):
                body=candidates[(slug,pin)]
                if not isinstance(body,bytes) or _r409.blob(body)!=pin:
                    errors.append('R418 original candidate Git blob mismatch: '+slug)
                    continue
                source=_r416.extract(body,candidate=True)
                src_verdict=verdict_blocks(source)
                for index,draft in enumerate(drafts):
                    channel=('wordpress','private_preview')[index]
                    total,drift=ordinary_fidelity(source,draft)
                    added=sum((verdict_blocks(draft)-src_verdict).values())
                    if drift:
                        errors.append('R418 original uncited prose changed, missing, duplicated or reordered: '+slug+' @ '+pin+' '+channel)
                    if added:
                        errors.append('R418 newly introduced unreviewed safety verdict: '+slug+' @ '+pin+' '+channel)
                    details.append({'slug':slug,'original_blob':pin,'target':channel,
                        'original_uncited_prose_blocks':total,
                        'original_uncited_prose_drift':drift,
                        'novel_safety_verdict_blocks':added,
                        'requires_qualified_source_and_safety_review':True})
    except (ValueError,TypeError,KeyError,IndexError,UnicodeError,OverflowError,AttributeError) as exc:
        errors.append('R418 missing or malformed authentic prose evidence: '+str(exc))
    return {'release_state':'DRAFT_HARD_HOLD','eligible':False,
        'publication_approved':False,'qualified_safety_approved':False,
        'integrity_ok':bool(parent.get('integrity_ok')) and not errors,
        'errors':sorted(set(errors)),'draft_checks':len(details),'details':details,
        'warnings':list(parent.get('warnings',[]))+[
            'Exact original prose custody detects edits; it does not establish original accuracy or safety',
            'Any new safety verdict requires qualified human review regardless of lexical test result',
            'All original variants remain unselected; WP and private export checks never authorize publishing']}


def main():
    ap=argparse.ArgumentParser(description='R418 original uncited claim custody; ALWAYS HARD HOLD')
    for x in ('original','manifest','export_root','private_candidate_root'):
        ap.add_argument(x,type=Path)
    args=ap.parse_args()
    try:
        raw=_r409.read_original(args.original)
        original=json.loads(raw.decode('utf-8'),object_pairs_hook=_r409.unique_pairs)
        manifest=json.loads(_r409.read_original(args.manifest).decode('utf-8'),object_pairs_hook=_r409.unique_pairs)
        exports,candidates={},{}
        for entry in original['original_articles']:
            slug=entry['slug']
            if not isinstance(slug,str) or not _r414.SLUG.fullmatch(slug):
                raise ValueError('unsafe original article slug')
            exports[slug]=(_r409.read_original(args.export_root/'wordpress'/(slug+'.html')),
                           _r409.read_original(args.export_root/'preview'/(slug+'.html')))
            for pin in set(entry['body_candidate_git_blobs']):
                if not isinstance(pin,str) or not HEX40.fullmatch(pin):
                    raise ValueError('invalid original Git blob identity')
                candidates[(slug,pin)]=_r412.checked_candidate_read(
                    args.private_candidate_root/slug/(pin+'.txt'),root=args.private_candidate_root)
        outcome=check(original,manifest,exports,candidates,raw_original=raw)
    except (OSError,ValueError,TypeError,KeyError,IndexError,UnicodeError,OverflowError) as exc:
        outcome={'release_state':'DRAFT_HARD_HOLD','eligible':False,
            'publication_approved':False,'qualified_safety_approved':False,
            'integrity_ok':False,'errors':[str(exc)]}
    print(json.dumps(outcome,sort_keys=True,indent=2))
    return 2

if __name__=='__main__':
    raise SystemExit(main())
