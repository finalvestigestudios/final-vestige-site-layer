#!/usr/bin/env python3
"""Fail closed on changes to the 96 frozen R275 Preparedness source files.

This is file-integrity custody, NOT editorial or safety approval. Never publish
from a passing custody check. No CMS, browser, network, or merchant side effects.
"""
from __future__ import annotations

import hashlib
import json
import re
import stat
from collections import Counter
from pathlib import Path, PurePosixPath

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
MANIFEST = 'audits/r276_all_slate_identity_UNAPPROVED.json'
MANIFEST_SHA = 'b8c7c6df0dca62b04b01abc5671b7083ad9cb61e'
SNAPSHOT = 'df96120007ceb33290764392a5900e356e04deac'
COUNTS = {'article_body': 35, 'article_meta': 35, 'tool_body': 6,
          'tool_meta': 6, 'hub_body': 1, 'source_origin': 8,
          'crosswalk': 1, 'docket': 1, 'export_gate': 1,
          'source_gate': 1, 'docket_gate': 1}
SHA = re.compile(r'^[a-f0-9]{40}$')
ARTICLE = re.compile(r'^content/articles/([a-z0-9-]+)\.(body\.html|meta\.json)$')
TOOL = re.compile(r'^content/tools/([a-z0-9-]+)\.(body\.html|meta\.json)$')
# Source-like extensions can alter registered evidence even when an existing
# fragment's SHA stays unchanged. README/notes are not source inputs.
SOURCE_DATA_EXTENSIONS = frozenset({'.json', '.jsonl', '.yaml', '.yml', '.csv', '.tsv'})


def require(ok, error):
    if not ok:
        raise ValueError(error)


def blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def load_json(raw: bytes):
    def unique(pairs):
        d = {}
        for k, v in pairs:
            if k in d:
                raise ValueError('duplicate JSON key: ' + k)
            d[k] = v
        return d
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def check_manifest(m: dict):
    require(isinstance(m, dict) and m.get('schema') == 'fv-r276-all-slate-identity-v1', 'manifest schema')
    require(m.get('snapshot_ref') == SNAPSHOT and m.get('state') == HOLD, 'manifest snapshot/hold')
    require(m.get('source_review') == {'shared_url_groups': 32, 'duplicate_id_groups': 15, 'held_occurrences': 3}, 'source review gates')
    for field in ('may_merge', 'publication_authorized', 'independent_qd_pass',
                  'medical_safety_verified', 'privacy_approved', 'merchant_offer_approved'):
        require(m.get(field) is False, 'unauthorized approval: ' + field)
    rows = m.get('entries')
    require(isinstance(rows, list) and len(rows) == 96, '96-file inventory incomplete')
    paths, kinds, groups = set(), Counter(), {'article': {}, 'tool': {}}
    for row in rows:
        require(isinstance(row, dict) and set(row) == {'path', 'role', 'sha', 'size'}, 'entry shape changed')
        p, kind = row['path'], row['role']
        require(isinstance(p, str) and p and '\\' not in p and '\x00' not in p, 'invalid inventory path')
        posix = PurePosixPath(p)
        require(not posix.is_absolute() and str(posix) == p and '..' not in posix.parts, 'path traversal')
        require(p not in paths, 'duplicate inventory path')
        paths.add(p)
        require(isinstance(row['sha'], str) and SHA.fullmatch(row['sha']), 'invalid object identity')
        require(type(row['size']) is int and row['size'] > 0, 'invalid byte length')
        require(kind in COUNTS, 'unexpected role')
        kinds[kind] += 1
        if kind.startswith('article_') or kind.startswith('tool_'):
            family = kind.split('_', 1)[0]
            match = (ARTICLE if family == 'article' else TOOL).fullmatch(p)
            require(match is not None, 'content role/path mismatch')
            require(kind.endswith('body') == (match.group(2) == 'body.html'), 'body/meta role mismatch')
            groups[family].setdefault(match.group(1), set()).add(kind)
        elif kind == 'source_origin':
            require(p.startswith('sources/fragments/') and p.endswith('.json'), 'source origin path')
        elif kind == 'hub_body':
            require(p == 'content/hubs/start-here.body.html', 'hub path')
        elif kind == 'crosswalk':
            require(p == 'sources/crosswalk.json', 'crosswalk path')
        elif kind == 'docket':
            require(p == 'audits/r273_shared_source_review_docket_UNAPPROVED.json', 'docket path')
        else:
            allowed = {'export_gate': 'tools/r220_full_slate_draft_custody.py',
                       'source_gate': 'tools/r272_crosswalk_snapshot_hold.py',
                       'docket_gate': 'tools/r273_source_review_docket_hold.py'}
            require(p == allowed[kind], 'gate path changed')
    require(dict(kinds) == COUNTS, 'inventory role census')
    require(len(groups['article']) == 35 and all(x == {'article_body', 'article_meta'} for x in groups['article'].values()), 'article pair lost')
    require(len(groups['tool']) == 6 and all(x == {'tool_body', 'tool_meta'} for x in groups['tool'].values()), 'tool pair lost')
    return rows


def check_tree(root: Path, manifest: dict):
    """Used by audit after pin validation. Synthetic inputs permitted ONLY by tests."""
    rows = check_manifest(manifest)
    root = Path(root)
    for row in rows:
        p = root / row['path']
        info = p.lstat()  # Reject symlinks (including a symlink final component).
        require(stat.S_ISREG(info.st_mode) and not p.is_symlink(), 'nonregular/symlink file: ' + row['path'])
        # Parent symlinks must also fail; do not follow outside the checkout.
        parent = p.parent
        while parent != root:
            require(not parent.is_symlink(), 'parent symlink: ' + row['path'])
            parent = parent.parent
        raw = p.read_bytes()
        require(len(raw) == row['size'] and blob(raw) == row['sha'], 'source bytes changed: ' + row['path'])
        if row['role'] in ('article_meta', 'tool_meta'):
            meta = load_json(raw)
            require(isinstance(meta, dict), 'metadata not object')
            require(meta.get('slug') == Path(row['path']).name.removesuffix('.meta.json'), 'metadata slug drift')
            require(isinstance(meta.get('status'), dict) and meta['status'].get('publish') == 'draft', 'non-draft manuscript')
    expected = {r['path'] for r in rows}
    # R280: an added fragment can shadow registered evidence in a source loader
    # without touching any of the eight frozen source files. Traverse all levels
    # and reject both untracked source-like files and symlink indirection.
    fragments = root / 'sources/fragments'
    require(fragments.is_dir() and not fragments.is_symlink(), 'source-fragment directory unavailable')
    for candidate in fragments.rglob('*'):
        rel = candidate.relative_to(root).as_posix()
        require(not candidate.is_symlink(), 'source-fragment symlink: ' + rel)
        if candidate.is_file() and candidate.suffix.lower() in SOURCE_DATA_EXTENSIONS:
            require(rel in expected, 'untracked source fragment: ' + rel)
    for directory in ('content/articles', 'content/tools'):
        folder = root / directory
        require(folder.is_dir() and not folder.is_symlink(), 'content directory unavailable')
        for file in folder.rglob('*'):
            if file.is_symlink():
                require(False, 'untracked content symlink: ' + file.relative_to(root).as_posix())
            if file.is_file() and file.name.lower().endswith(('.body.html', '.meta.json')):
                require(file.relative_to(root).as_posix() in expected, 'unexpected article/tool: ' + file.relative_to(root).as_posix())
    return {'state': HOLD, 'mechanical_source_parity_only': True, 'protected_files': 96,
            'article_count': 35, 'tool_count': 6, 'publication_authorized': False,
            'independent_qd_pass': False, 'medical_safety_verified': False,
            'privacy_approved': False, 'requires_independent_review': True}


def audit(root: Path):
    root = Path(root)
    try:
        raw = (root / MANIFEST).read_bytes()
        require(blob(raw) == MANIFEST_SHA, 'manifest Git identity mismatch')
        return check_tree(root, load_json(raw))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError) as exc:
        return {'state': INVALID, 'mechanical_source_parity_only': False,
                'publication_authorized': False, 'independent_qd_pass': False,
                'errors': [str(exc)]}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True, help='Local preparedness directory')
    print(json.dumps(audit(parser.parse_args().root), indent=2, sort_keys=True))
    # HARD HOLD even when bytes match; never signals a publish-ready PASS.
    raise SystemExit(2)
