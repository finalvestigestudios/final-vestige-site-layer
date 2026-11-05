#!/usr/bin/env python3
"""Read-only custody review for PR #157 against the richer frozen Preparedness RC.

This is NOT a medical, fire-safety, editorial, QD, or publication approval.
It refuses files inconsistent with pinned Git blob hashes; never writes article files.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

ARTICLE = 'preparedness/content/articles'
CITE = re.compile(r'\{\{cite:([a-z0-9]+(?:-[a-z0-9]+)*)\}\}')
ANY = re.compile(r'\{\{cite:([^}]+)\}\}')
HTML = re.compile(r'<[^>]+>')
RC = 'ddb3528ba6494dada1fa1c3a142ce746e3a67706'
QA157 = '7d1ae6b8ef93d10cfb6810987672360885e9c1aa'
HOLD = 'DRAFT_HOLD_QUALIFIED_SOURCE_SAFETY_AND_QD_REQUIRED'
# Immutable byte/content evidence retrieved independently from both GitHub commits.
EXPECTED = {
 'household-emergency-plan': {
   'rc_sha':'f81cd43516e8295104230412f18776919148f905',
   'qa_sha':'6407a31a882211e62c00f4e07ec7dc4d5abf99c6',
   'rc_meta_sha':'0681d51e6e29166eaae27ac2b7f1fbde3f836787',
   'rc_cites':57, 'qa_cites':57,
 },
 'three-day-kit': {
   'rc_sha':'933f38ff3cd55a241cf9b392014fc52d4961e84f',
   'qa_sha':'f578cdbae602c1ad58a9237c8dea0fd74c99f7da',
   'rc_meta_sha':'1c69d5f1636a3a41631a5d93f11254d85cbe1b59',
   'rc_cites':79, 'qa_cites':68,
 },
}

def blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def _read(root: Path, rel: str, expected_sha: str) -> str:
    path = root / rel
    if path.is_symlink() or not path.is_file():
        raise ValueError('missing/symlinked exact Git source: ' + rel)
    raw = path.read_bytes()
    if blob_sha(raw) != expected_sha:
        raise ValueError('Git blob identity mismatch: ' + rel)
    return raw.decode('utf-8', errors='strict')

def citations(html: str) -> Counter:
    valid = CITE.findall(html)
    if len(valid) != len(ANY.findall(html)):
        raise ValueError('malformed citation token')
    return Counter(valid)

def _words(html: str) -> int:
    return len(HTML.sub(' ', ANY.sub('', html)).split())

def audit(manifest: dict, rc_root: Path, qa_root: Path) -> dict:
    if set(manifest) != {'schema','candidate_ref','qa_ref','articles','status'}:
        raise ValueError('invalid evidence schema')
    if manifest['schema'] != 'R143-QA157-AUTHENTIC-PAIRS-1' or manifest['candidate_ref'] != RC or manifest['qa_ref'] != QA157:
        raise ValueError('wrong immutable RC/QA source commit')
    if manifest['status'] != 'UNREVIEWED_HUMAN_REQUIRED' or manifest['articles'] != EXPECTED:
        raise ValueError('manifest custody or approval forgery')
    report = []
    for slug, expected in sorted(EXPECTED.items()):
        rel = f'{ARTICLE}/{slug}.body.html'
        rc = _read(rc_root, rel, expected['rc_sha'])
        qa = _read(qa_root, rel, expected['qa_sha'])
        meta_rel = f'{ARTICLE}/{slug}.meta.json'
        meta = json.loads(_read(rc_root, meta_rel, expected['rc_meta_sha']))
        if meta.get('slug') != slug or meta.get('status',{}).get('publish') != 'draft':
            raise ValueError('article identity/draft release state changed')
        if meta.get('safety_review',{}).get('state') != 'pending':
            raise ValueError('independent safety review not verified')
        old, new = citations(rc), citations(qa)
        if sum(old.values()) != expected['rc_cites'] or sum(new.values()) != expected['qa_cites']:
            raise ValueError('frozen source citation totals mismatch')
        if set(old) != set(meta.get('source_use',{})):
            raise ValueError('RC source-to-author explanation mismatch')
        if slug == 'household-emergency-plan':
            # Existing RC already avoids the original breaker-switch-off instruction.
            if 'Do not switch off the main breaker as a drill' not in rc or 'Do not switch off the main breaker' not in qa:
                raise ValueError('power-drill safety-language review target drift')
        if slug == 'three-day-kit':
            if ('start-fema-power-sheet' not in old or 'start-cdc-power-outage' not in old or
                'Do not stop essential treatment or discard' not in qa):
                raise ValueError('medicine/source review target drift')
        removed, added = old-new, new-old
        report.append({
          'slug':slug, 'rc_blob':expected['rc_sha'],'qa_blob':expected['qa_sha'],
          'rc_words_approx':_words(rc),'qa_words_approx':_words(qa),
          'rc_citations':sum(old.values()),'qa_citations':sum(new.values()),
          'lost_source_occurrences':dict(sorted(removed.items())),
          'added_source_occurrences':dict(sorted(added.items())),
          'fully_removed_source_ids':sorted(set(old)-set(new)),
          'replacement_allowed':False,'human_review':'UNREVIEWED_REQUIRED',
        })
    return {'schema':'R143-QA157-REVIEW-REPORT-1','status':HOLD,
            'qd':'NOT_APPROVED','qualified_safety':'NOT_APPROVED',
            'word_preservation_required':True,'automatic_cherry_pick':False,
            'articles':report}

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--manifest', type=Path, required=True)
    ap.add_argument('--rc-root',type=Path,required=True)
    ap.add_argument('--qa-root',type=Path,required=True)
    ap.add_argument('--report',type=Path)
    args=ap.parse_args(argv)
    try:
        out = audit(json.loads(args.manifest.read_text(encoding='utf-8')),args.rc_root,args.qa_root)
        code = 0
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, json.JSONDecodeError) as e:
        out = {'schema':'R143-QA157-REVIEW-REPORT-1','status':HOLD,'qd':'NOT_APPROVED',
               'qualified_safety':'NOT_APPROVED','verified_exact_pairs':0,'error':str(e)}
        code = 2
    data = json.dumps(out,indent=2,sort_keys=True,ensure_ascii=False) + '\n'
    if args.report:
        args.report.write_text(data,encoding='utf-8')
    else: print(data)
    return code

if __name__ == '__main__':
    sys.exit(main())
