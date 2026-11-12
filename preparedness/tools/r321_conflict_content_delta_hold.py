#!/usr/bin/env python3
"""Read-only, Git-blob-authenticated change witnesses for R320's 15 held source conflicts.

A diff is NOT safety approval; no content selection, release, or CMS access occurs.
"""
from __future__ import annotations
import argparse
from collections import Counter
import difflib
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import subprocess

PARENT = Path(__file__).with_name('r320_conflict_adjudication_docket_hold.py')
if PARENT.is_symlink():
    raise RuntimeError('linked reviewer gate')
spec = importlib.util.spec_from_file_location('fv_r320_review', PARENT)
if spec is None or spec.loader is None:
    raise RuntimeError('missing reviewer gate')
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)
SCHEMA = 'fv-preparedness-r321-authenticated-content-delta-v1'
REVIEW_VERSIONS = ('integrated', 'continuation', 'followup')
HOLD = {'publication_authorized': False, 'independent_qd_pass': False,
        'qualified_safety_approved': False, 'automatic_merge_permitted': False,
        'paid_conversion_verified': False}
SENSITIVE = ('source','citat','reference','approval','safety','status','review',
             'slug','number','canonical','url','permalink','disclos','publish')


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def read_verified_blob(ref: dict, loader) -> bytes:
    if not isinstance(ref, dict) or set(ref) != {'sha','size'}:
        raise ValueError('invalid pinned Git blob reference')
    sha, size = ref['sha'], ref['size']
    if not isinstance(sha, str) or re.fullmatch('[a-f0-9]{40}', sha) is None:
        raise ValueError('invalid object SHA')
    if type(size) is not int or size < 0:
        raise ValueError('invalid object byte size')
    data = loader(sha)
    if not isinstance(data, bytes) or len(data) != size or git_blob_sha(data) != sha:
        raise ValueError('Git object content does not match pinned ref')
    data.decode('utf-8', 'strict')
    return data


class FeatureParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.headings, self.links, self.controls, self.text = [], [], [], []
        self._heading = None
        self._hidden = 0
        self._suppress = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ('script','style','template'): self._suppress += 1
        if tag in ('h1','h2','h3','h4','h5','h6'): self._heading = tag
        if tag == 'a' and a.get('href'): self.links.append(a['href'])
        if tag in ('input','textarea','select','button'):
            self.controls.append((tag,a.get('name',''),a.get('id',''),a.get('type','')))
    def handle_endtag(self, tag):
        if tag in ('script','style','template'): self._suppress = max(0,self._suppress-1)
        if tag in ('h1','h2','h3','h4','h5','h6'): self._heading = None
    def handle_data(self, data):
        if self._suppress: return
        normalized = ' '.join(data.split())
        if not normalized: return
        self.text.append(normalized)
        if self._heading: self.headings.append((self._heading,normalized))


def html_features(data: bytes) -> dict:
    html = data.decode('utf-8')
    parser = FeatureParser()
    parser.feed(html)
    return {'headings': parser.headings, 'links': parser.links,
            'controls': parser.controls, 'text': parser.text,
            'citation_tokens': sorted(re.findall(r'\[([A-Za-z][A-Za-z0-9_-]{2,70})\]', html))}


def strict_json(data: bytes) -> object:
    def no_duplicate(items):
        out = {}
        for key, value in items:
            if key in out: raise ValueError('duplicate JSON key: ' + key)
            out[key] = value
        return out
    return json.loads(data.decode('utf-8'), object_pairs_hook=no_duplicate)


def changed_paths(a, b, prefix='$') -> list[str]:
    if isinstance(a, dict) and isinstance(b, dict):
        keys = set(a) | set(b)
        return [p for k in sorted(keys) for p in changed_paths(a.get(k,object()),b.get(k,object()),prefix+'.'+k)]
    if a != b: return [prefix]
    return []


def delta(a: bytes, b: bytes, path: str) -> dict:
    if path.endswith('.meta.json'):
        pa,pb = strict_json(a),strict_json(b)
        if not isinstance(pa, dict) or not isinstance(pb, dict): raise ValueError('metadata must be object')
        keys=changed_paths(pa,pb)
        flagged=[k for k in keys if any(s in k.lower() for s in SENSITIVE)]
        return {'kind':'metadata','changed_paths':keys,'safety_sensitive_paths':flagged,
                'human_review_required': True}
    if not path.endswith('.body.html'): raise ValueError('unrecognized source suffix')
    aa,bb=html_features(a),html_features(b)
    sm=difflib.SequenceMatcher(None, aa['text'],bb['text'], autojunk=False)
    edits=[(tag, i2-i1, j2-j1) for tag,i1,i2,j1,j2 in sm.get_opcodes() if tag!='equal']
    return {'kind':'body','text_segments_before':len(aa['text']),
            'text_segments_after':len(bb['text']),
            'text_change_ops':edits,
            'headings_removed':list((Counter(map(tuple,aa['headings']))-Counter(map(tuple,bb['headings']))).elements()),
            'headings_added':list((Counter(map(tuple,bb['headings']))-Counter(map(tuple,aa['headings']))).elements()),
            'citations_removed':list((Counter(aa['citation_tokens'])-Counter(bb['citation_tokens'])).elements()),
            'citations_added':list((Counter(bb['citation_tokens'])-Counter(aa['citation_tokens'])).elements()),
            'links_removed':list((Counter(aa['links'])-Counter(bb['links'])).elements()),
            'links_added':list((Counter(bb['links'])-Counter(aa['links'])).elements()),
            'form_fields_removed':len((Counter(map(tuple,aa['controls']))-Counter(map(tuple,bb['controls'])))),
            'form_fields_added':len((Counter(map(tuple,bb['controls']))-Counter(map(tuple,aa['controls'])))),
            'human_review_required': True}


def build_report(manifest: dict, docket: dict, loader) -> dict:
    check = review.validate_docket(manifest,docket)
    errors=list(check['errors'])
    output=[]
    if not errors:
        for rec in docket['records']:
            path=rec['path']; refs=rec['source_refs']; objects={}
            for variant in REVIEW_VERSIONS:
                ref=refs.get(variant)
                if ref is None: continue
                try: objects[variant]=read_verified_blob(ref,loader)
                except (ValueError, OSError, KeyError, UnicodeError, subprocess.SubprocessError) as exc:
                    errors.append('MISSING_OR_INVALID_GIT_OBJECT:'+path+':'+variant+':'+type(exc).__name__)
            if 'integrated' not in objects:
                errors.append('MISSING_BASELINE:'+path)
                continue
            comparisons={}
            for variant in ('continuation','followup'):
                if variant not in objects: continue
                try: comparisons[variant]=delta(objects['integrated'],objects[variant],path)
                except (ValueError,UnicodeError,TypeError) as exc:
                    errors.append('UNREADABLE_AUTHORED_SOURCE:'+path+':'+variant+':'+type(exc).__name__)
            output.append({'path':path,'severity':rec['severity'],
                           'source_refs':refs, 'comparisons':comparisons,
                           'status':'UNRESOLVED_HOLD', 'qualified_approval':False})
    return {'schema':SCHEMA,'state':'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors':sorted(set(errors)),'review_count':len(output),
            'release':HOLD.copy(),'records':output}


def _git_loader(root: Path):
    def load(sha: str) -> bytes:
        proc=subprocess.run(['git','cat-file','blob',sha],cwd=root,stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL,timeout=10,check=True)
        return proc.stdout
    return load


def main() -> int:
    parser=argparse.ArgumentParser(description='Read-only, source-pinned Preparedness review delta')
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    args=parser.parse_args()
    try:
        root=args.root.resolve(strict=True)
        manifest_path=root/review.SOURCE_MANIFEST_PATH
        docket_path=root/'preparedness/audits/r320_conflict_adjudication_docket.json'
        if (not (root/'.git').exists() or any(p.is_symlink() for p in (manifest_path,docket_path))):
            raise ValueError('missing git repository or linked inputs')
        manifest=strict_json(manifest_path.read_bytes())
        docket=strict_json(docket_path.read_bytes())
        report=build_report(manifest,docket,_git_loader(root))
        native=review.custody.validate_manifest(manifest,root)
        if native['errors']:
            report['state']='INVALID_HARD_HOLD';report['errors'].append('NATIVE_SOURCE_CUSTODY_FAILURE')
    except (OSError,ValueError,TypeError,UnicodeError) as exc:
        report={'schema':SCHEMA,'state':'INVALID_HARD_HOLD',
                'errors':['AUTHENTIC_CHECKOUT_REQUIRED:'+type(exc).__name__],
                'review_count':0,'release':HOLD.copy(),'records':[]}
    print(json.dumps(report,sort_keys=True,indent=2))
    return 2 if report['state']=='DRAFT_HARD_HOLD' else 1

if __name__=='__main__': raise SystemExit(main())
