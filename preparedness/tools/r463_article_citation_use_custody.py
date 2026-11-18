#!/usr/bin/env python3
"""R463 35-article citation-to-authored-source-use/cluster provenance. Review only.

Reads Git-blob-pinned R460 manuscripts/metadata and R462 sources. Does not
approve cited claims, safety, payment, exports, or publication. CLI always HOLD.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

REPO = 'finalvestigestudios/final-vestige-site-layer'
SNAPSHOT_BLOB = '056d14cd97d29b843d52912383c237b9122e73ef'
CROSSWALK_BLOB = 'd62e493a67dedd23e04cfdf3cce762ef933c6bf9'
REQUIRED = (35, 2000, 385)
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
SLUG = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
HOLD = 'DRAFT_HARD_HOLD'

class ArticleHold(ValueError):
    pass

def require(ok, msg):
    if not ok:
        raise ArticleHold(msg)

def git_blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()

def pairs_unique(pairs):
    obj = {}
    for k, v in pairs:
        require(k not in obj, 'duplicate JSON key: ' + k)
        obj[k] = v
    return obj

def pinned_bytes(root, relative, pin, *, max_size=150000):
    require(isinstance(relative, str) and not relative.startswith('/') and
            '..' not in Path(relative).parts, 'unsafe evidence path')
    path = root / relative
    require(path.is_file() and not path.is_symlink(), 'missing/symlink input: ' + relative)
    raw = path.read_bytes()
    require(len(raw) <= max_size and git_blob(raw) == pin, 'Git-blob mismatch: ' + relative)
    return raw

def pinned_json(root, relative, pin, *, max_size=150000):
    return json.loads(pinned_bytes(root, relative, pin, max_size=max_size).decode('utf-8'),
                      object_pairs_hook=pairs_unique)

def inspect(slate, origins, source_files, *, expected=REQUIRED):
    """Immutable author's source-use to every literal citation occurrence.

    slate: slug => (meta dict, raw body str); origins: slug => source cluster;
    source_files: origin => list of original source rows. Unit fixtures override
    expected counts; native CLI uses 35/2000/385 observations and Git blob pins.
    """
    require(isinstance(slate, dict) and isinstance(origins, dict) and
            isinstance(source_files, dict), 'invalid custody input')
    require(len(slate) == expected[0] and len(slate) == len(set(slate)), 'article census drift')
    by_origin = {}
    total_source_rows = 0
    for origin, rows in source_files.items():
        require(isinstance(origin, str) and isinstance(rows, list), 'source origin malformed')
        reg = {}
        for s in rows:
            require(isinstance(s, dict) and isinstance(s.get('id'), str) and
                    isinstance(s.get('url'), str) and s['id'] not in reg and
                    s['url'].startswith('https://'), 'invalid/duplicate source in ' + origin)
            reg[s['id']] = s
            total_source_rows += 1
        by_origin[origin] = reg
    require('base' in by_origin and len(by_origin) == 8, 'original eight source files missing')
    require(set(slate) <= set(origins), 'missing article source-origin provenance')
    citation_occurrences = 0
    source_use_memberships = 0
    origin_fallbacks = []
    conflicting_url_id_refs = []
    reviews = []
    for slug in sorted(slate):
        require(SLUG.fullmatch(slug) is not None, 'unsafe slug')
        meta, body = slate[slug]
        require(isinstance(meta, dict) and isinstance(body, str) and meta.get('slug') == slug,
                'body/metadata identity mismatch: ' + slug)
        require(meta.get('status', {}).get('publish') == 'draft', 'non-draft article: ' + slug)
        require(meta.get('safety_review', {}).get('state') in
                {'pending', 'approved', 'not-required'}, 'unrecognized safety state: ' + slug)
        scope = meta.get('source_use')
        require(isinstance(scope, dict) and scope, 'missing authored reading-scope ledger: ' + slug)
        require(all(isinstance(sid, str) and SLUG.fullmatch(sid) and
                    isinstance(note, str) and note.strip() for sid, note in scope.items()),
                'empty or malformed authored source_use: ' + slug)
        ids = CITE.findall(body)
        require(ids and body.count('{{cite:') == len(ids), 'malformed citation token: ' + slug)
        cited = set(ids)
        require(cited == set(scope), 'citation/source_use bijection lost: ' + slug +
                ' missing=' + ','.join(sorted(cited-set(scope))) +
                ' orphan=' + ','.join(sorted(set(scope)-cited)))
        origin = origins[slug]
        require(origin in by_origin, 'unknown cluster source origin: ' + slug)
        for sid in sorted(cited):
            own = by_origin[origin].get(sid)
            base = by_origin['base'].get(sid)
            require(own is not None or base is not None,
                    'citation resolves only to unrelated cluster: ' + slug + '/' + sid)
            selected = own if own is not None else base
            chosen_origin = origin if own is not None else 'base'
            require(selected.get('url', '').startswith('https://'), 'non-HTTPS selected source')
            if own is None and origin != 'base':
                origin_fallbacks.append({'article': slug, 'id': sid, 'chosen_origin': 'base'})
            urls = {r[sid]['url'] for r in by_origin.values() if sid in r}
            if len(urls) > 1:
                conflicting_url_id_refs.append({'article': slug, 'id': sid,
                                                'chosen_origin': chosen_origin,
                                                'selected_literal_url': selected['url'],
                                                'conflicting_origin_count': len(urls)})
        citation_occurrences += len(ids)
        source_use_memberships += len(scope)
        reviews.append({'slug': slug, 'origin': origin, 'citation_occurrences': len(ids),
                        'distinct_citation_ids': len(cited), 'source_use_ids': len(scope),
                        'safety_review_state_in_authored_meta': meta['safety_review']['state'],
                        'publication_state_in_authored_meta': meta['status']['publish']})
    require((len(slate), citation_occurrences, source_use_memberships) == expected,
            'frozen article/source-use census drift: human review required')
    return {'state': 'SOURCE_USE_CITATION_STRUCTURAL_HOLD', 'release_state': HOLD,
            'qualified_qd_pass': False, 'claim_support_verified': False,
            'may_publish': False, 'merchant_offer_verified': False,
            'verified_paid_orders': None, 'net_revenue_per_1000_qualified_humans': None,
            'article_count': len(slate), 'citation_occurrences': citation_occurrences,
            'distinct_article_source_use_memberships': source_use_memberships,
            'original_source_records': total_source_rows,
            'source_origin_fallbacks': origin_fallbacks,
            'conflicting_literal_url_source_id_references': conflicting_url_id_refs,
            'articles': reviews}

def native(root):
    root = root.resolve()
    snapshot = pinned_json(root, 'audits/R460_ORIGIN_BRANCH_BLOB_SNAPSHOT.json', SNAPSHOT_BLOB)
    cw = pinned_json(root, 'sources/crosswalk.json', CROSSWALK_BLOB, max_size=180000)
    require(snapshot.get('repository') == REPO and snapshot.get('release_state') == HOLD and
            snapshot.get('qualified_qd_pass') is False, 'nine-origin source custody malformed')
    require(cw.get('status') == 'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
            'shared URL docket elevated or lost')
    rows = {}
    for entry in cw['source_files']:
        path = entry['path']
        require(path.startswith('preparedness/sources/'), 'source escaped Preparedness')
        data = pinned_json(root, path.removeprefix('preparedness/'), entry['git_blob_sha'])
        require(len(data['sources']) == entry['count'], 'source origin row loss')
        require(entry['origin'] not in rows, 'source origin repeated')
        rows[entry['origin']] = data['sources']
    slate = {}
    articles = snapshot['candidate']['articles']
    require(len(articles) == 35, 'original 35-article inventory missing')
    for slug, pair in articles.items():
        prefix = 'content/articles/' + slug + '.'
        meta = pinned_json(root, prefix + 'meta.json', pair['meta'])
        body = pinned_bytes(root, prefix + 'body.html', pair['body'], max_size=180000).decode('utf-8')
        slate[slug] = (meta, body)
    import importlib.util
    tool = Path(__file__).with_name('r462_shared_url_scope_custody.py')
    require(tool.exists() and not tool.is_symlink(), 'R462 dependency missing')
    spec = importlib.util.spec_from_file_location('r462_source', tool)
    require(spec is not None and spec.loader is not None, 'R462 dependency unavailable')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    source_by_path = {'preparedness/sources/register.json': rows['base']}
    for origin, values in rows.items():
        if origin != 'base':
            source_by_path['preparedness/sources/fragments/' + origin + '.json'] = values
    mod.audit(cw, source_by_path, snapshot)
    return inspect(slate, cw['article_origins'], rows)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    try:
        print(json.dumps(native(args.root), sort_keys=True, indent=2))
    except (OSError, UnicodeError, TypeError, ValueError, KeyError) as exc:
        print(json.dumps({'state': 'ORIGINAL_CITATION_USE_FAILURE_HARD_HOLD',
                          'release_state': HOLD, 'qualified_qd_pass': False,
                          'may_publish': False, 'error': str(exc)}))
    return 2

if __name__ == '__main__':
    sys.exit(main())
