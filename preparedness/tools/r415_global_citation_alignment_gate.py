#!/usr/bin/env python3
"""R415: bounded global original-to-export citation alignment escrow.

R414's nine-word locality windows can be replayed beside a relocated source.
This read-only add-on binds the citation position to a monotone ORIGINAL-to-DRAFT
word alignment and rejects ambiguous duplicate source-adjacent contexts. It
never evaluates whether a source actually supports the claim or releases content.
"""
from __future__ import annotations

import argparse
from difflib import SequenceMatcher
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path

_spec = spec_from_file_location('r414_citation_locality_escrow_gate', Path(__file__).with_name('r414_citation_locality_escrow_gate.py'))
_r414 = module_from_spec(_spec)
_spec.loader.exec_module(_r414)
_r412 = _r414._r412
MAX_TOKENS = 12000
MAX_GAP = 24
CONTEXT = 9


def global_alignment(source, draft):
    """Return deterministic one-to-one word correspondences, fail on oversized input."""
    if len(source) > MAX_TOKENS or len(draft) > MAX_TOKENS:
        raise ValueError('candidate exceeds global citation alignment word bound')
    # autojunk prevents repeated filler from causing uncontrolled quadratic work;
    # failure to align means human adjudication, never silent acceptance.
    blocks = SequenceMatcher(None, source, draft, autojunk=True).get_matching_blocks()
    return {i + k: j + k for i, j, size in blocks for k in range(size)}


def context_count(words, left, right, gap):
    """Count ordered, exact context witnesses with a limited intervening span.

    Detects copy-pasting the unchanged context elsewhere, even if its citation
    remains linked to the same source ID and visually matches R414's window.
    """
    if not left or not right:
        return 1  # The monotone alignment still handles boundary citations.
    hits = 0
    left_len, right_len = len(left), len(right)
    if gap < 0 or gap > MAX_GAP:
        return 2  # Suspiciously long source labels need human review.
    for i in range(len(words) - left_len + 1):
        if tuple(words[i:i + left_len]) != left:
            continue
        start = i + left_len
        j = start + gap
        if j <= len(words) - right_len and tuple(words[j:j + right_len]) == right:
            hits += 1
            if hits > 1:
                return hits
    return hits


def marker_alignments(original_parse, rendered_parse):
    """Protect each citation's original span, not merely similar nearby words."""
    source, draft = original_parse.words, rendered_parse.words
    mapped = global_alignment(source, draft)
    if [sid for sid, _ in original_parse.markers] != [sid for sid, _ in rendered_parse.markers]:
        return len(original_parse.markers), len(original_parse.markers)
    drift = duplicates = 0
    for index, ((sid, at), (_, target)) in enumerate(zip(original_parse.markers, rendered_parse.markers)):
        label = original_parse.labels[index] or ()
        first_after = min(len(source), at + len(label))
        left_i = [i for i in range(max(0, at-CONTEXT), at) if i in mapped]
        right_i = [i for i in range(first_after, min(len(source), first_after+CONTEXT)) if i in mapped]
        if not left_i and not right_i:
            drift += 1
            continue
        # Require each available side to retain its complete adjacent source
        # context. A partial overlap could be an ambiguous repeated passage.
        expected_left = min(CONTEXT, at)
        expected_right = min(CONTEXT, len(source)-first_after)
        if len(left_i) != expected_left or len(right_i) != expected_right:
            drift += 1
            continue
        lo = mapped[left_i[-1]]+1 if left_i else 0
        hi = mapped[right_i[0]] if right_i else len(draft)
        if lo > hi or hi-lo > MAX_GAP or not lo <= target <= hi:
            drift += 1
        left = tuple(source[max(0,at-CONTEXT):at])
        right = tuple(source[first_after:first_after+CONTEXT])
        label_gap = len(rendered_parse.labels[index] or ())
        if context_count(draft,left,right,label_gap) > 1:
            duplicates += 1
    return drift, duplicates


def check(original, manifest, exports, candidates, *, raw_original=None, test_only=False):
    base = _r414.check(original,manifest,exports,candidates,
                       raw_original=raw_original,test_only=test_only)
    errors = list(base.get('errors', [])); details = []
    try:
        for entry in original['original_articles']:
            slug = entry['slug']
            draft_pair = exports[slug]
            if not isinstance(draft_pair,(tuple,list)) or len(draft_pair) != 2:
                raise ValueError('missing paired draft: '+slug)
            parsed = [_r414.positions(html) for html in draft_pair]
            for pin in set(entry['body_candidate_git_blobs']):
                data = candidates[(slug,pin)]
                if not isinstance(data,bytes) or _r412._r409.blob(data) != pin:
                    errors.append('R415 authentic source blob mismatch: '+slug); continue
                src = _r414.positions(data,candidate=True)
                if not src.markers:
                    errors.append('R415 missing source marker: '+slug); continue
                for idx, render in enumerate(parsed):
                    drift,duplicate = marker_alignments(src,render)
                    if drift:
                        errors.append('R415 citation globally detached from original location: '+slug+' @ '+pin)
                    if duplicate:
                        errors.append('R415 ambiguous replayed source-adjacent context: '+slug+' @ '+pin)
                    details.append({'slug':slug,'original_blob':pin,
                                    'target':'wordpress' if idx==0 else 'private_preview',
                                    'source_markers':len(src.markers), 'global_mismatches':drift,
                                    'replayed_contexts':duplicate,'human_review_required':True})
    except (ValueError,TypeError,KeyError,IndexError,AttributeError,UnicodeError,OverflowError) as exc:
        errors.append('R415 missing/malformed global alignment evidence: '+str(exc))
    return {'release_state':'DRAFT_HARD_HOLD','eligible':False,
            'publication_approved':False,'qualified_safety_approved':False,
            'integrity_ok':bool(base.get('integrity_ok')) and not errors,
            'errors':sorted(set(errors)), 'draft_pairs_inspected':len(details),
            'details':details,'warnings':list(base.get('warnings',[]))+[
                'Global citation alignment is NOT verification of factual source support or advice safety',
                'No fork selection, source scope adjudication, private-export approval, QD PASS or public release']}


def main():
    p=argparse.ArgumentParser(description='R415 citation global alignment: ALWAYS DRAFT HARD HOLD')
    for field in ('original','manifest','export_root','private_candidate_root'):
        p.add_argument(field,type=Path)
    args=p.parse_args()
    try:
        raw=_r412._r409.read_original(args.original)
        original=json.loads(raw.decode('utf-8'),object_pairs_hook=_r412._r409.unique_pairs)
        manifest=json.loads(_r412._r409.read_original(args.manifest).decode('utf-8'),
                            object_pairs_hook=_r412._r409.unique_pairs)
        exports,candidates={},{}
        for a in original['original_articles']:
            slug=a['slug']
            if not isinstance(slug,str) or not _r414.SLUG.fullmatch(slug):
                raise ValueError('unsafe original slug')
            exports[slug]=(_r412._r409.read_original(args.export_root/'wordpress'/(slug+'.html')),
                           _r412._r409.read_original(args.export_root/'preview'/(slug+'.html')))
            for sha in set(a['body_candidate_git_blobs']):
                if not isinstance(sha,str) or not _r412.HEX40.fullmatch(sha):
                    raise ValueError('unsafe original blob SHA')
                candidates[(slug,sha)] = _r412.checked_candidate_read(
                    args.private_candidate_root/slug/(sha+'.txt'),root=args.private_candidate_root)
        out=check(original,manifest,exports,candidates,raw_original=raw)
    except (OSError,ValueError,TypeError,KeyError,IndexError,UnicodeError,OverflowError) as exc:
        out={'release_state':'DRAFT_HARD_HOLD','eligible':False,'publication_approved':False,
             'qualified_safety_approved':False,'integrity_ok':False,'errors':[str(exc)]}
    print(json.dumps(out,indent=2,sort_keys=True)); return 2


if __name__ == '__main__':
    raise SystemExit(main())
