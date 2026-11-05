#!/usr/bin/env python3
"""R144: read-only, exact-source surgical editorial review for Preparedness #136.

Compares a proposed change to one paragraph of an authentic draft. This guards
custody, not semantic medical safety. The output is always DRAFT/HOLD.
"""
from __future__ import annotations
import argparse
from collections import Counter
from difflib import unified_diff
import hashlib
from html import unescape
import json
from pathlib import Path
import re

FROZEN_RC = 'ddb3528ba6494dada1fa1c3a142ce746e3a67706'
QA157 = '7d1ae6b8ef93d10cfb6810987672360885e9c1aa'
TARGETS = {
    'household-emergency-plan': {'section': 'practice', 'sha': 'f81cd43516e8295104230412f18776919148f905', 'meta_sha': '0681d51e6e29166eaae27ac2b7f1fbde3f836787'},
    'three-day-kit': {'section': 'medicine', 'sha': '933f38ff3cd55a241cf9b392014fc52d4961e84f', 'meta_sha': '1c69d5f1636a3a41631a5d93f11254d85cbe1b59'},
}
P = re.compile(r'<(?:p|li)(?:\s[^>]*)?>[\s\S]*?</(?:p|li)>', re.I)
CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
ANY_CITE = re.compile(r'\{\{cite:([^}]+)\}\}')
H2 = re.compile(r'<h2\s+id="([a-z0-9-]+)"[^>]*>', re.I)
TAGS = re.compile(r'<[^>]*>')

class Hold(ValueError):
    pass

def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\x00' + data).hexdigest()

def read_pinned(path: Path, sha: str) -> str:
    if path.is_symlink() or not path.is_file():
        raise Hold('missing or symlinked immutable baseline file')
    data = path.read_bytes()
    if blob_sha(data) != sha:
        raise Hold('immutable baseline Git blob mismatch')
    return data.decode('utf-8', errors='strict')

def _cites(content: str) -> list[str]:
    valid = CITE.findall(content)
    if len(valid) != len(ANY_CITE.findall(content)) or '{{cite:' in CITE.sub('',content):
        raise Hold('malformed or missing citation identity')
    return valid

def _segment_html(html: str) -> tuple[list[str],list[str]]:
    paras, gaps, pos = [], [], 0
    for m in P.finditer(html):
        gaps.append(html[pos:m.start()]); paras.append(m.group()); pos=m.end()
    gaps.append(html[pos:])
    if not paras or len(gaps) != len(paras)+1:
        raise Hold('no valid paragraph segmentation')
    return paras, gaps

def _visible(s: str) -> str:
    return unescape(TAGS.sub(' ',s)).strip()

def review(baseline: str, candidate: str, metadata: dict, slug: str,
           *, baseline_sha: str | None = None) -> dict:
    if slug not in TARGETS:
        raise Hold('non-target article: only QA #157 reconciliation may enter this lane')
    if not isinstance(baseline,str) or not isinstance(candidate,str):
        raise Hold('HTML must be UTF-8 text')
    expected = baseline_sha or TARGETS[slug]['sha']
    if blob_sha(baseline.encode('utf-8')) != expected:
        raise Hold('frozen baseline mismatch (possible stale or unreviewed candidate)')
    if not isinstance(metadata,dict) or metadata.get('slug')!=slug:
        raise Hold('article identity mismatch')
    if metadata.get('status',{}).get('publish')!='draft':
        raise Hold('not a draft article')
    if metadata.get('safety_review',{}).get('state')!='pending':
        raise Hold('unexpected historical safety state; no automatic status promotion')
    before, gaps = _segment_html(baseline)
    after, gaps2 = _segment_html(candidate)
    if gaps != gaps2 or len(before)!=len(after):
        raise Hold('non-paragraph markup or paragraph count modified')
    edits = [i for i,(a,b) in enumerate(zip(before,after)) if a!=b]
    if len(edits)!=1:
        raise Hold('exactly one paragraph may be changed')
    idx = edits[0]
    # The closest preceding h2 must be the declared correction's original section.
    prefix = ''.join(gaps[j]+before[j] for j in range(idx+1))
    headings = H2.findall(prefix)
    if not headings or headings[-1]!=TARGETS[slug]['section']:
        raise Hold('edit outside pinned QA correction section')
    old,new=before[idx],after[idx]
    if not _visible(new) or len(_visible(new).split())<10:
        raise Hold('trivial or blank replacement')
    tag = re.match(r'<(p|li)\b', old, re.I)
    if not tag or old[:old.index('>')+1] != new[:new.index('>')+1] or not new.lower().endswith(f'</{tag.group(1).lower()}>'):
        raise Hold('paragraph wrapper changed')
    if _cites(baseline)!=_cites(candidate) or _cites(old)!=_cites(new):
        raise Hold('citation occurrence order, identity or count changed')
    # Forbid scripting, interactive elements, anchors, and hidden review text in edits.
    forbidden=re.compile(r'<\s*(?:script|style|iframe|form|a|button|input|template|object|svg)\b|\bon\w+\s*=|\b(?:hidden|inert|aria-hidden)\s*=|(?:display\s*:\s*none|visibility\s*:\s*hidden)',re.I)
    if forbidden.search(new):
        raise Hold('active, hidden or navigational markup in proposed paragraph')
    # Existing document-wide protective guidance must remain literally present.
    if slug=='three-day-kit':
        required=('Do not stop, throw away or ration', 'call your doctor or pharmacist', 'Two FEMA documents, two wordings')
    else:
        required=('Do not switch off the main breaker as a drill', 'refrigerator', 'medical equipment')
    if any(x.lower() not in candidate.lower() for x in required):
        raise Hold('previously documented hazard-caution language removed')
    if len(_visible(new).split())*2 < len(_visible(old).split()):
        raise Hold('paragraph lost more than half its reading depth')
    return {
        'schema':'R144-BOUNDED-REVIEW-1', 'release':'DRAFT_HOLD',
        'qualified_source_review':'REQUIRED', 'qualified_medical_review':'REQUIRED',
        'independent_qd':'NOT_APPROVED', 'word_preservation':'LOCAL_ONLY',
        'automatic_merge':False, 'publication_allowed':False,
        'rc_commit':FROZEN_RC, 'qa_157_commit':QA157,
        'slug':slug,'section':TARGETS[slug]['section'],'paragraph_index':idx,
        'original_git_blob':expected,
        'candidate_git_blob':blob_sha(candidate.encode('utf-8')),
        'unchanged_citation_occurrences':len(_cites(baseline)),
        'changed_paragraph_citations':_cites(old),
        'before_words':len(_visible(old).split()),'proposed_words':len(_visible(new).split()),
        'proposed_diff':'\n'.join(unified_diff(old.splitlines(),new.splitlines(),fromfile='baseline',tofile='human-proposal',lineterm='')),
        'review_note':'Structure and citation preservation only. Never a claim of clinical, editorial, or publication safety.'
    }

def main(argv=None) -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--slug',required=True)
    ap.add_argument('--baseline',type=Path,required=True)
    ap.add_argument('--candidate',type=Path,required=True)
    ap.add_argument('--metadata',type=Path,required=True)
    args=ap.parse_args(argv)
    try:
        baseline=read_pinned(args.baseline,TARGETS[args.slug]['sha'])
        metadata=json.loads(read_pinned(args.metadata,TARGETS[args.slug]['meta_sha']))
        output=review(baseline,args.candidate.read_text(encoding='utf-8'),metadata,args.slug)
        status=0
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, AttributeError) as ex:
        output={'schema':'R144-BOUNDED-REVIEW-1','release':'DRAFT_HOLD',
                'publication_allowed':False,'independent_qd':'NOT_APPROVED','error':str(ex)}
        status=2
    print(json.dumps(output,indent=2,sort_keys=True,ensure_ascii=False))
    return status
if __name__=='__main__':
    raise SystemExit(main())
