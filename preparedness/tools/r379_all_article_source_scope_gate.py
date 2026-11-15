"""R379: fail-closed, read-only original nine-ref / 35-article source-scope audit.

It never chooses a Shelter fork, asserts human source approval, or publishes content.
Run in an authenticated *full* git checkout with the original branches fetched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from html import unescape
from pathlib import Path
from urllib.parse import urlsplit

REPO = 'finalvestigestudios/final-vestige-site-layer'
MANIFEST_SHA = '5e7d9a8972872c82b4bc46ac13aab18883d8149a'
CROSSWALK_SHA = 'd62e493a67dedd23e04cfdf3cce762ef933c6bf9'
REGISTER_SHA = 'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77'
TAXONOMY_SHA = '15c547bb3018ac182b12a51036389cfa39a59168'
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
LINK = re.compile(r'\{\{link:([a-z0-9-]+)\|([^{}]+)\}\}')
OBJ = re.compile(r'^preparedness/content/articles/([a-z0-9-]+)\.(body\.html|meta\.json)$')
FRAGMENT = re.compile(r'^preparedness/sources/fragments/([a-z0-9-]+)\.json$')
SHA = re.compile(r'^[a-f0-9]{40}$')
NO_RELEASE = ('approval', 'approved', 'publish', 'published', 'qd_pass', 'release_ready', 'live')


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw, usedforsecurity=False).hexdigest()


def load_git_blob(root: Path, sha: str) -> bytes:
    if not SHA.fullmatch(sha):
        raise ValueError('unsafe Git object SHA')
    result = subprocess.run(['git', '-C', str(root), 'cat-file', 'blob', sha],
                            capture_output=True, timeout=20, check=True)
    return result.stdout


def evaluate(manifest: object, crosswalk: object, register: object, reader, taxonomy: object = None) -> dict:
    """reader(blob_sha) -> original bytes. Pure, does not select manuscript forks."""
    errors = []
    warnings = []
    if not all(isinstance(x, dict) for x in (manifest, crosswalk, register)):
        return {'status':'INVALID_HARD_HOLD', 'errors':['invalid input document'],
                'publication_approved':False, 'qualified_safety_approved':False}
    if manifest.get('repository') != REPO or manifest.get('schema_version') != 1:
        errors.append('untrusted nine-ref manifest identity')
    if manifest.get('release_state') != 'DRAFT_HARD_HOLD' or any(manifest.get(k) not in (None, False) for k in NO_RELEASE):
        errors.append('manifest release hold missing or approval asserted')
    pins = manifest.get('branch_pins', [])
    if not isinstance(pins, list) or len(pins) != 9 or len({p.get('branch') for p in pins if isinstance(p, dict)}) != 9:
        errors.append('nine immutable branch identities required')
        pins = []
    pin_map = {p.get('branch'): p.get('sha') for p in pins if isinstance(p, dict)}
    if any(not SHA.fullmatch(str(x)) for x in pin_map.values()):
        errors.append('malformed contributor SHA pin')
    objects = manifest.get('objects', [])
    if not isinstance(objects, list):
        objects = []
        errors.append('missing manifest objects')
    bypath = {}
    for obj in objects:
        if not isinstance(obj, dict) or not isinstance(obj.get('path'), str):
            errors.append('invalid manifest object')
            continue
        p = obj['path']
        if not (OBJ.fullmatch(p) or FRAGMENT.fullmatch(p)) or p in bypath:
            errors.append('unexpected or duplicate object path: ' + p)
            continue
        bypath[p] = obj
        variants = obj.get('variants', [])
        if not isinstance(variants, list) or not variants:
            errors.append('missing original variants: ' + p)
            continue
        shas = [v.get('sha') for v in variants if isinstance(v, dict)]
        if len(shas) != len(variants) or any(not SHA.fullmatch(str(s)) for s in shas):
            errors.append('invalid variant fingerprints: ' + p)
        if len({v.get('branch') for v in variants if isinstance(v, dict)}) != len(variants):
            errors.append('duplicated branch version: ' + p)
        if obj.get('selected_sha') is not None or obj.get('decision') != ('REVIEW_REQUIRED' if len(set(shas)) > 1 else 'IDENTICAL_OR_SINGLE'):
            errors.append('unreviewed version selected or conflict hidden: ' + p)
        for v in variants:
            if isinstance(v, dict) and v.get('branch') not in pin_map:
                errors.append('variant belongs to unpinned branch: ' + p)
    bodies = {OBJ.fullmatch(p).group(1) for p in bypath if OBJ.fullmatch(p) and p.endswith('.body.html')}
    metas = {OBJ.fullmatch(p).group(1) for p in bypath if OBJ.fullmatch(p) and p.endswith('.meta.json')}
    if len(bodies) != 35 or bodies != metas or manifest.get('article_count') != 35:
        errors.append('35-body/metadata coverage incomplete')
    if sum(len({v.get('sha') for v in o.get('variants', []) if isinstance(v, dict)}) > 1 for o in objects) != 9 or manifest.get('conflict_count') != 9:
        errors.append('nine unresolved original object conflicts must remain visible')
    origins = crosswalk.get('article_origins', {})
    if not isinstance(origins, dict):
        origins = {}
        errors.append('missing article origin crosswalk')
    # Taxonomy includes optional private tool targets. A valid link target is not
    # evidence that a destination is public, approved or usable for conversions.
    tool_targets = set()
    if taxonomy is not None:
        if not isinstance(taxonomy, dict):
            errors.append('taxonomy input must be an object')
        else:
            tools = taxonomy.get('tools')
            slate = taxonomy.get('slate')
            if not isinstance(tools, list) or not isinstance(slate, list):
                errors.append('taxonomy tool/slate arrays missing')
            else:
                tool_targets = {x.get('slug') for x in tools if isinstance(x, dict) and isinstance(x.get('slug'), str)}
                tax_articles = {x.get('slug') for x in slate if isinstance(x, dict) and isinstance(x.get('slug'), str)}
                if tax_articles != bodies or len(slate) != 35:
                    errors.append('taxonomy original 35-article slate mismatch')
                if len(tool_targets) != len(tools) or tool_targets & bodies:
                    errors.append('duplicate or colliding tool slug')
    base_rows = register.get('sources', [])
    if not isinstance(base_rows, list):
        base_rows = []
        errors.append('invalid BASE source registry')
    base = {}
    for src in base_rows:
        if not isinstance(src, dict) or not isinstance(src.get('id'), str) or src['id'] in base:
            errors.append('duplicate or malformed BASE source ID')
        else:
            base[src['id']] = src
    cache = {}
    def read(sha: str) -> bytes:
        if sha not in cache:
            data = reader(sha)
            if not isinstance(data, bytes) or git_blob(data) != sha:
                raise ValueError('Git blob content does not match authenticated SHA ' + str(sha))
            cache[sha] = data
        return cache[sha]
    fragment_rows = {}
    for path, obj in bypath.items():
        match = FRAGMENT.fullmatch(path)
        if not match:
            continue
        for v in obj['variants']:
            key = (match.group(1), v['branch'])
            if key in fragment_rows:
                errors.append('duplicate source origin/branch')
                continue
            try:
                rows = json.loads(read(v['sha']).decode('utf-8'))['sources']
                if not isinstance(rows, list):
                    raise ValueError('source list missing')
                ids = [s['id'] for s in rows]
                if len(ids) != len(set(ids)):
                    raise ValueError('duplicate source identity within fragment')
                fragment_rows[key] = {s['id']: s for s in rows}
            except (KeyError, ValueError, TypeError, UnicodeError, OSError) as exc:
                errors.append('source fragment unreadable: ' + path + ': ' + type(exc).__name__)
    census, target_slugs = [], defaultdict(set)
    for slug in sorted(bodies & metas):
        bb = bypath[f'preparedness/content/articles/{slug}.body.html']['variants']
        mm = {v['branch']:v for v in bypath[f'preparedness/content/articles/{slug}.meta.json']['variants']}
        if set(mm) != {v['branch'] for v in bb}:
            errors.append('unpaired article body/metadata variants: ' + slug)
        if slug not in origins:
            errors.append('article missing original source owner: ' + slug)
        for b in bb:
            branch = b['branch']
            if branch not in mm:
                continue
            try:
                html = read(b['sha']).decode('utf-8')
                meta = json.loads(read(mm[branch]['sha']).decode('utf-8'))
            except (ValueError, UnicodeError, OSError) as exc:
                errors.append('article original Git blob unreadable: ' + slug + ': ' + type(exc).__name__)
                continue
            if meta.get('slug') != slug or not isinstance(meta.get('section'), str) or not meta['section']:
                errors.append('article identity or section drift: ' + slug)
            if meta.get('status',{}).get('publish') != 'draft':
                errors.append('article publish state no longer draft: ' + slug)
            review = meta.get('safety_review', {})
            review_state = review.get('state') if isinstance(review, dict) else None
            if review_state not in ('pending', 'approved', 'not-required'):
                errors.append('unrecognized original safety label: ' + slug)
            elif review_state == 'approved':
                if not isinstance(review.get('reviewer'), str) or not review['reviewer'].strip() or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(review.get('date', ''))):
                    errors.append('legacy approved label lacks dated reviewer: ' + slug)
                warnings.append('original approval label retained; independent source/safety/QD review still required: ' + slug)
            elif review_state == 'not-required':
                warnings.append('original not-required label retained; not independent QD clearance: ' + slug)
            if not isinstance(meta.get('source_use'), dict):
                errors.append('article source_use not an object: ' + slug)
                uses = {}
            else:
                uses = meta['source_use']
            citations = CITE.findall(html)
            cited = set(citations)
            if not citations:
                warnings.append('no citation tokens: ' + slug)
            if cited != set(uses):
                errors.append('body/metadata cite mismatch: ' + slug)
            origin = origins.get(slug)
            own = fragment_rows.get((origin, branch), {})
            if origin not in ('base', None) and not own:
                errors.append('original reading-scope fragment absent: ' + slug + '/' + branch)
            fallback, unresolved, missing_scope, unchecked = [], [], [], []
            for sid in sorted(cited | set(uses)):
                src = own.get(sid) or base.get(sid)
                if src is None:
                    unresolved.append(sid)
                    continue
                if sid not in own:
                    fallback.append(sid)
                if not isinstance(uses.get(sid), str) or not uses[sid].strip() or not isinstance(src.get('supports'), str) or not src['supports'].strip():
                    missing_scope.append(sid)
                url = urlsplit(str(src.get('url', '')))
                if url.scheme != 'https' or not url.hostname or url.username or url.password:
                    errors.append('unsafe citation destination: ' + slug + '/' + sid)
                if src.get('human_link_check') is not True:
                    unchecked.append(sid)
            if unresolved:
                errors.append('unresolved IDs: ' + slug + ': ' + ','.join(unresolved))
            if missing_scope:
                errors.append('missing source/claim reading scope: ' + slug + ': ' + ','.join(missing_scope))
            # Native builder link syntax is {{link:slug|Label}}; the older
            # one-group regex silently returned no links for authentic bodies.
            links = LINK.findall(html)
            link_targets = sorted({target for target, _label in links})
            missing_links = sorted(set(link_targets) - bodies - tool_targets)
            if missing_links:
                errors.append('unresolved original article/tool link targets: ' + slug + ': ' + ','.join(missing_links))
            linked_private_tools = sorted(set(link_targets) & tool_targets)
            if linked_private_tools:
                warnings.append('private tool links require independently reviewed destination: ' + slug + ': ' + ','.join(linked_private_tools))
            if html.count('{{link:') != len(links):
                errors.append('malformed or unparsed internal link token: ' + slug)
            url = '/preparedness/' + meta.get('section', '') + '/' + slug + '/'
            target_slugs[url].add(slug)
            words = len(re.findall(r"\b[\w'-]+\b", unescape(re.sub(r'<[^>]+>', ' ', html))))
            if words < 600:
                warnings.append('original reading-depth below 600 words: ' + slug + '/' + branch)
            census.append({'slug':slug, 'branch':branch, 'body_git_blob':b['sha'], 'meta_git_blob':mm[branch]['sha'],
                           'origin':origin, 'word_count':words, 'citations':len(citations), 'unique_source_ids':len(cited),
                           'base_fallback_ids':fallback, 'unchecked_human_source_ids':unchecked,
                           'unresolved_ids':unresolved, 'source_scope_missing_ids':missing_scope,
                           'unresolved_internal_links':missing_links, 'internal_link_targets':link_targets,
                           'private_tool_link_targets':linked_private_tools, 'canonical_path':url,
                           'publish':meta.get('status', {}).get('publish'), 'original_safety_label':review_state,
                           'independent_qd_approved':False})
    duplicates = [{'url':url, 'slugs':sorted(ss)} for url,ss in target_slugs.items() if len(ss) > 1]
    if duplicates:
        errors.append('duplicate article canonical URL across distinct slugs')
    by_slug = defaultdict(list)
    for c in census:
        by_slug[c['slug']].append(c)
    depth = [{'slug': slug, 'min_words': min(x['word_count'] for x in vs),
              'max_words': max(x['word_count'] for x in vs),
              'versions':len(vs), 'human_adjudication':len(vs) > 1}
             for slug,vs in sorted(by_slug.items())]
    return {'status':'INVALID_HARD_HOLD' if errors else 'CUSTODY_COMPLETE_REVIEW_REQUIRED',
            'article_count':len(by_slug), 'article_variants':len(census),
            'object_conflicts':manifest.get('conflict_count'), 'canonical_duplicate_groups':duplicates,
            'errors':sorted(set(errors)), 'warnings':sorted(set(warnings)),
            'per_variant':census, 'reading_depth_comparison':depth,
            'publication_approved':False, 'qualified_safety_approved':False,
            'historical_approval_is_not_independent_qd':True,
            'verified_paid_offer':False, 'verified_net_revenue':None}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.repo
    paths = [('manifest', 'preparedness/audits/r374_nine_ref_object_manifest_HARD_HOLD.json', MANIFEST_SHA),
             ('crosswalk', 'preparedness/sources/crosswalk.json', CROSSWALK_SHA),
             ('register', 'preparedness/sources/register.json', REGISTER_SHA),
             ('taxonomy', 'preparedness/taxonomy.json', TAXONOMY_SHA)]
    try:
        inputs = {}
        for label, path, expected in paths:
            raw = (root / path).read_bytes()
            if git_blob(raw) != expected:
                raise ValueError('authenticated '+label+' input SHA mismatch')
            inputs[label] = json.loads(raw)
        result = evaluate(inputs['manifest'], inputs['crosswalk'], inputs['register'],
                          lambda sha: load_git_blob(root,sha), inputs['taxonomy'])
    except (OSError, ValueError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        result = {'status':'INVALID_HARD_HOLD','errors':[type(exc).__name__ + ': ' + str(exc)],
                  'publication_approved':False, 'qualified_safety_approved':False}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2  # Always HARD HOLD. Machine custody can never be a Qualified Domain PASS.


if __name__ == '__main__':
    raise SystemExit(main())
