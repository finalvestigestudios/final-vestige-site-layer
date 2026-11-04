#!/usr/bin/env python3
"""Fail-closed, read-only 35-article author-scope reviewer roster (never release approval).

Usage: python -I preparedness/tools/r126_author_scope_gate.py --root .
       python -I preparedness/tools/r126_author_scope_gate.py --root . --candidate-root /path/to/rc584
The optional candidate root must be the exact frozen release candidate checkout.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

RC = 'ddb3528ba6494dada1fa1c3a142ce746e3a67706'
PARENT = '6ca388edbed803e64663e8f0ecfa55bda0fe08c3'
PENDING = 'pending-human-source-and-reading-scope-review'
PARTS = 'ABC'


class Hold(ValueError):
    pass


def demand(ok, code):
    if not ok:
        raise Hold(code)


def unique_keys(pairs):
    obj = {}
    for key, value in pairs:
        demand(key not in obj, 'DUPLICATE_JSON_KEY:' + key)
        obj[key] = value
    return obj


def parse(path):
    return json.loads(Path(path).read_text(encoding='utf8'), object_pairs_hook=unique_keys)


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def audit(crosswalk, taxonomy, parts, *, candidate_root=None):
    demand(len(parts) == 3, 'PART_COUNT')
    demand(len(crosswalk.get('groups', [])) == 32, 'CROSSWALK_COUNT')
    demand(crosswalk.get('status') == 'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
           'CROSSWALK_HOLD')
    groups = crosswalk['groups']
    demand(all(g.get('review_status') == PENDING and g.get('reviewer') is None and
               g.get('reviewed_on') is None for g in groups), 'PREMATURE_SOURCE_REVIEW')
    slugs = [a.get('slug') for a in taxonomy.get('slate', [])]
    demand(len(slugs) == len(set(slugs)) == 35, 'ARTICLE_ROSTER')
    variants = {}
    for g in groups:
        url = g['url']
        demand(url not in variants, 'DUPLICATE_SOURCE_GROUP')
        versions = {}
        for v in g['variants']:
            pair = (v['source']['id'], v['origin'])
            demand(pair not in versions, 'DUPLICATE_SOURCE_VARIANT')
            versions[pair] = v
        variants[url] = versions
    out = []
    for i, part in enumerate(parts):
        demand(part.get('schema') == 'fv-r126-author-source-binding-part-v1', 'SCHEMA')
        demand(part.get('partition') == PARTS[i], 'PART_ORDER')
        demand(part.get('state') == 'DRAFT_UNREVIEWED_HOLD', 'PART_HOLD')
        demand(part.get('candidate_git_commit') == RC and
               part.get('crosswalk_git_commit') == PARENT, 'PIN_DRIFT')
        demand(part.get('crosswalk_group_count') == 32, 'GROUP_COUNT_DRIFT')
        demand(part.get('crosswalk_git_blob') == crosswalk.get('_observed_blob_sha'),
               'CROSSWALK_BLOB_DRIFT')
        demand(part.get('taxonomy_git_blob') == taxonomy.get('_observed_blob_sha'),
               'TAXONOMY_BLOB_DRIFT')
        demand(len(part.get('articles', [])) == (12 if i < 2 else 11), 'PART_SIZE')
        out.extend(part['articles'])
    demand([r.get('slug') for r in out] == slugs, 'ARTICLE_ROSTER_ORDER')
    counts = 0
    group_counts = {g['url']: 0 for g in groups}
    for row in out:
        slug = row['slug']
        origin = crosswalk.get('article_origins', {}).get(slug)
        demand(origin is not None and row.get('origin') == origin, 'AUTHOR_ORIGIN:' + slug)
        demand(row.get('publish') == 'draft', 'UNAUTHORIZED_PUBLICATION:' + slug)
        demand(row.get('safety_state') in ('approved', 'pending', 'not-required'),
               'INVALID_SAFETY_STATE:' + slug)
        demand(isinstance(row.get('metadata_blob_sha'), str) and
               len(row['metadata_blob_sha']) == 40, 'METADATA_BLOB_MISSING:' + slug)
        bound = row.get('shared_source_bindings')
        demand(isinstance(bound, list), 'MISSING_BINDINGS:' + slug)
        seen = set()
        for record in bound:
            sid, url = record.get('source_id'), record.get('shared_url')
            demand(isinstance(sid, str) and isinstance(url, str), 'BAD_BINDING')
            demand((sid, url) not in seen, 'DUPLICATE_BINDING:' + slug)
            seen.add((sid, url))
            demand(url in variants, 'UNKNOWN_SHARED_GROUP:' + slug)
            origin_key = (sid, origin) if (sid, origin) in variants[url] else (sid, 'base')
            demand(origin_key in variants[url], 'FOREIGN_AUTHOR_SCOPE:' + slug)
            demand(record.get('source_record_origin') == origin_key[1],
                   'SOURCE_SCOPE_SUBSTITUTION:' + slug)
            demand(isinstance(record.get('source_use_scope'), str) and
                   bool(record['source_use_scope'].strip()), 'BLANK_SOURCE_SCOPE:' + slug)
            group_counts[url] += 1
            counts += 1
        if candidate_root is not None:
            p = Path(candidate_root) / 'preparedness' / 'content' / 'articles' / (slug + '.meta.json')
            raw = p.read_bytes()
            demand(git_blob(raw) == row['metadata_blob_sha'], 'CANDIDATE_METADATA_CHANGED:' + slug)
            meta = json.loads(raw.decode('utf8'), object_pairs_hook=unique_keys)
            demand(meta['status']['publish'] == 'draft' and
                   meta.get('safety_review', {}).get('state') == row['safety_state'],
                   'CANDIDATE_SAFETY_OR_PUBLICATION_CHANGED:' + slug)
            declared = meta.get('source_use', {})
            demand(len(declared) == row['total_declared_source_uses'],
                   'SOURCE_USE_COUNT_DRIFT:' + slug)
            for record in bound:
                demand(declared.get(record['source_id']) == record['source_use_scope'],
                       'CANDIDATE_READING_SCOPE_DRIFT:' + slug)
    return {'release_state': 'HOLD', 'independent_QD_PASS': False,
            'medical_safety_verified': False, 'may_publish': False,
            'article_count': len(out), 'unreviewed_shared_url_groups': len(groups),
            'author_scope_bindings': counts,
            'groups_with_declared_article_use': sum(bool(c) for c in group_counts.values()),
            'note': 'Metadata scope mapping only. No human link check, claim review or sale.'}


def run(root, candidate_root=None):
    root = Path(root)
    source = root / 'preparedness' / 'sources' / 'crosswalk.json'
    # This stacked reviewer branch and the frozen RC have different taxonomy bytes.
    # Never substitute the branch's historical taxonomy for the candidate's
    # exact evidence. Require an explicit, independently checked RC checkout.
    demand(candidate_root is not None, 'CANDIDATE_ROOT_REQUIRED_EXACT_RC584')
    taxonomy = Path(candidate_root) / 'preparedness' / 'taxonomy.json'
    c, t = parse(source), parse(taxonomy)
    c['_observed_blob_sha'] = git_blob(source.read_bytes())
    t['_observed_blob_sha'] = git_blob(taxonomy.read_bytes())
    parts = [parse(root / 'preparedness' / 'docs' / 'r126' /
                   ('SOURCE_USE_SCOPE_PART_' + ch + '_HOLD.json')) for ch in PARTS]
    return audit(c, t, parts, candidate_root=candidate_root)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path('.'))
    p.add_argument('--candidate-root', type=Path)
    args = p.parse_args(argv)
    try:
        print(json.dumps(run(args.root, args.candidate_root), indent=2, sort_keys=True))
        return 0
    except (Hold, ValueError, OSError, UnicodeError, KeyError) as exc:
        print('HOLD: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
