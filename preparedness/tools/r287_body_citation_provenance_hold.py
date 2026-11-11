#!/usr/bin/env python3
"""R287: body-to-metadata-to-frozen-source citation crosswalk. DRAFT/HARD HOLD ONLY.

Protects 35 integrated article bodies + six tool bodies as immutable Git blobs,
then enumerates every literal {{cite:id}} use against its matching pinned
metadata source_use and all 8 frozen source registers. Does NOT adjudicate the
truth of a claim, duplicate source identities, safety, print usability or sales.
No file writes, publishing operations, network calls or new trackers.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import types

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
BRIDGE_FILE = 'tools/r285_metadata_source_bridge_hold.py'
BRIDGE_SHA = '1b3d4ca5056871ede00101eb5902dfdfa1b20867'
MARKER = re.compile(r'\{\{cite:([^\{\}\r\n]+)\}\}')
SOURCE_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]*\Z')
SUSPECT_CITE = re.compile(r'\{\{\s*cite\b', flags=re.IGNORECASE)
EXPECTED = {'article_body': 35, 'article_meta': 35, 'tool_body': 6, 'tool_meta': 6}


def require(yes, message):
    if not yes:
        raise ValueError(message)


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def load_bridge(root):
    """Load EXACT R286 Git-pinned bridge source; never a path-based import/.pyc."""
    path = Path(root) / BRIDGE_FILE
    require(path.is_file() and not path.is_symlink(), 'R286 bridge missing/unsafe')
    base = Path(root)
    require(base.is_dir() and not base.is_symlink(), 'unsafe root')
    for part in BRIDGE_FILE.split('/'):
        base = base / part
        require(not base.is_symlink(), 'symlinked R286 bridge ancestor')
    data = path.read_bytes()
    require(git_blob(data) == BRIDGE_SHA, 'R286 bridge Git identity changed')
    module = types.ModuleType('fv_r286_authenticated_bridge_r287')
    module.__file__ = str(path)
    module.__package__ = ''
    exec(compile(data, str(path), 'exec', dont_inherit=True), module.__dict__)
    require(callable(getattr(module, 'audit', None)), 'R286 bridge lacks audit')
    return module


def parse_cites(raw, name):
    """Reject malformed cite markup instead of silently losing references."""
    require(type(raw) is bytes, 'body bytes required: ' + name)
    text = raw.decode('utf-8')
    valid = list(MARKER.finditer(text))
    for found in SUSPECT_CITE.finditer(text):
        require(any(m.start() == found.start() for m in valid),
                'malformed citation tag: ' + name)
    found_ids = []
    for match in valid:
        value = match.group(1)
        require(bool(SOURCE_ID.fullmatch(value)), 'invalid citation identifier: ' + name)
        found_ids.append(value)
    require(text.count('{{cite:') == len(valid), 'unpaired citation tag: '+name)
    return Counter(found_ids)


def paired_content_rows(entries):
    """Build a closed 41-pair census; don't trust caller-selected paths."""
    require(type(entries) is list and len(entries) == 96, '96-entry inventory required')
    role_counts = Counter(x.get('role') for x in entries if isinstance(x, dict))
    for role, count in EXPECTED.items():
        require(role_counts[role] == count, 'unexpected '+role+' census')
    paths = [e.get('path') for e in entries if isinstance(e, dict)]
    require(len(paths) == len(set(paths)), 'duplicate inventory paths')
    by_path = {e['path']: e for e in entries}
    result = []
    for row in entries:
        if row['role'] not in ('article_body','tool_body'):
            continue
        body = row['path']
        require(body.startswith('content/articles/') if row['role']=='article_body'
                else body.startswith('content/tools/'), 'body role/path mismatch: '+body)
        require(body.endswith('.body.html') and body.count('/') == 2,
                'unexpected body path: '+body)
        meta_path = body[:-len('.body.html')]+'.meta.json'
        meta = by_path.get(meta_path)
        expected = 'article_meta' if row['role']=='article_body' else 'tool_meta'
        require(meta is not None and meta['role'] == expected,
                'missing paired metadata: '+body)
        result.append((row, meta))
    require(len(result) == 41, '41 body/metadata pairs required')
    return sorted(result, key=lambda x:x[0]['path'])


def evaluate(entries, contents, metadata, source_files):
    """Deterministic pure provenance review. All inputs must be pinned by caller."""
    pairs = paired_content_rows(entries)
    require(isinstance(contents,dict) and isinstance(metadata,dict) and
            isinstance(source_files,dict), 'crosswalk inputs malformed')
    permitted_bodies = {a['path'] for a,_ in pairs}
    permitted_meta = {m['path'] for _,m in pairs}
    require(set(contents) == permitted_bodies, '41 body bytes missing/extra')
    require(set(metadata) == permitted_meta, '41 metadata rows missing/extra')
    source_index = defaultdict(list)
    total_sources = 0
    for origin in sorted(source_files):
        doc = source_files[origin]
        require(isinstance(doc,dict) and isinstance(doc.get('sources'),list),
                'invalid source origin: '+origin)
        for source in doc['sources']:
            require(isinstance(source,dict) and isinstance(source.get('id'),str)
                    and isinstance(source.get('url'),str), 'malformed source record')
            source_index[source['id']].append({
                'origin':origin,'url':source['url'],
                'verified_on':source.get('verified_on'),
                'human_link_check':source.get('human_link_check'),
            })
            total_sources += 1
    require(total_sources == 244, 'source identity census changed')
    require(len(source_files) == 8, 'eight frozen sources required')
    crosswalk=[];unresolved=[];ambiguous=[];uncited=[];total_tags=0
    for bodyrow,metarow in pairs:
        bp,mp=bodyrow['path'],metarow['path']
        meta=metadata[mp]
        require(type(meta) is dict and type(meta.get('source_use')) is dict,
                'source_use mapping missing: '+mp)
        uses = meta['source_use']
        tags=parse_cites(contents[bp],bp)
        require(all(x in uses for x in tags), 'body citation missing metadata source_use: '+bp+':'+
                repr(sorted(set(tags)-set(uses))))
        require(all(x in source_index for x in tags), 'body citation absent from frozen register: '+bp)
        if not tags: uncited.append(bp)
        for id_,times in sorted(tags.items()):
            candidates = sorted(source_index[id_],key=lambda x:(x['origin'],x['url']))
            if len(candidates)>1:ambiguous.append({'body':bp,'id':id_,'candidate_count':len(candidates)})
            crosswalk.append({'body':bp,'metadata':mp,'source_id':id_,
                              'occurrences':times,'candidates':candidates})
            total_tags+=times
        extra=sorted(set(uses)-set(tags))
        if extra:unresolved.append({'body':bp,'metadata_only_sources':extra})
    return {'state': HOLD, 'publication_authorized':False, 'independent_qd_pass':False,
            'medical_safety_verified':False,'privacy_approved':False,
            'requires_human_citation_scope_review':True,'requires_qualified_safety_review':True,
            'body_count':len(pairs),'article_count':35,'tool_count':6,
            'frozen_source_rows':total_sources,'inline_citation_occurrences':total_tags,
            'body_source_edges':len(crosswalk),'ambiguous_body_source_edges':ambiguous,
            'metadata_only_source_review':unresolved,'uncited_body_review':uncited,
            'crosswalk':crosswalk}


def audit(root):
    root=Path(root)
    try:
        bridge=load_bridge(root)
        upstream=bridge.audit(root)
        require(type(upstream) is dict and upstream.get('state') == HOLD and
                upstream.get('publication_authorized') is False and
                upstream.get('independent_qd_pass') is False and
                upstream.get('medical_safety_verified') is False and
                upstream.get('privacy_approved') is False,
                'R286 upstream source custody gate did not return safe HOLD')
        original=bridge.strict_json(bridge.pinned_bytes(root,*bridge.ORIGINAL))
        require(original.get('state')==HOLD and original.get('independent_qd_pass') is False,
                'R200 origin safety hold changed')
        integrated=bridge.strict_json(bridge.pinned_bytes(root,*bridge.INTEGRATED))
        entries=integrated['entries']
        pairs=paired_content_rows(entries)
        bodybytes={b['path']:bridge.pinned_bytes(root,b['path'],b['sha']) for b,_ in pairs}
        meta={m['path']:bridge.strict_json(bridge.pinned_bytes(root,m['path'],m['sha'])) for _,m in pairs}
        srcrows={r['path']:r for r in entries if r['path'] in bridge.SOURCE_ROSTER}
        require(set(srcrows)==bridge.SOURCE_ROSTER,'frozen source roster missing')
        sources={p:bridge.strict_json(bridge.pinned_bytes(root,p,row['sha']))
                 for p,row in sorted(srcrows.items())}
        return evaluate(entries,bodybytes,meta,sources)
    except (OSError,ValueError,TypeError,KeyError,AttributeError,UnicodeError,ImportError,SyntaxError) as e:
        return {'state':INVALID,'publication_authorized':False,'independent_qd_pass':False,
                'medical_safety_verified':False,'privacy_approved':False,
                'errors':[str(e)]}


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,type=Path)
    p=parser.parse_args()
    outcome=audit(p.root)
    print(json.dumps(outcome,sort_keys=True,indent=2))
    raise SystemExit(2 if outcome['state']==HOLD else 3)
