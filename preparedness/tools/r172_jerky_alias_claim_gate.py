#!/usr/bin/env python3
"""R172: fail-closed jerky URL alias + source-use impact review (NOT safety approval)."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

SCHEMA = 'fv-preparedness-r172-jerky-alias-impact-v1'
HOLD = 'DRAFT_HARD_HOLD'
ALIAS = 'hist-food-nchfp-jerky'
ROOT_URL = 'https://nchfp.uga.edu/how/dry/recipes/jerky'
SLASH_URL = ROOT_URL + '/'
ORIGINAL = {
    'preparedness/sources/crosswalk.json': 'd62e493a67dedd23e04cfdf3cce762ef933c6bf9',
    'preparedness/sources/fragments/hist-food.json': 'd10628342fea5f177a8d1be00dd906d0c9c7850e',
    'preparedness/review/r171/source-variance-quarantine.json': 'cd757a36e3015b732916ffd6655856a575140350',
    'preparedness/docs/r151/contributor-three-way.json': '9cf386519eda970209ff6be4ff0243661cd9d996',
    'preparedness/docs/r161/body_custody.json': 'fede4222c796d92798eff7cf0dcb225c291f7d61',
}

def require(condition: object, message: str) -> None:
    if not condition:
        raise ValueError(message)

def blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()

def pinned(root: Path, path: str, sha: str) -> dict:
    target = root / path
    require(target.is_file() and not target.is_symlink(), 'missing or symlink: ' + path)
    raw = target.read_bytes()
    require(blob(raw) == sha, 'pinned Git blob drift: ' + path)
    value = json.loads(raw)
    require(type(value) is dict, 'expected JSON object: ' + path)
    return value

def audit(quarantine: dict, crosswalk: dict, fragment: dict,
          metadata: dict, *, strict: bool = True) -> dict:
    """Pure evidence audit. Synthetic strict=False never grants a source approval."""
    require(type(quarantine) is dict and quarantine.get('schema') ==
            'fv-preparedness-r171-source-variance-quarantine-v1', 'R171 docket drift')
    require(quarantine.get('state') == HOLD and
            quarantine.get('human_source_equivalence_review_complete') is False and
            quarantine.get('human_qualified_safety_approval') is False and
            quarantine.get('independent_qd_pass') is False and
            quarantine.get('publication_authorized') is False and
            quarantine.get('commercial_offer_verified') is False,
            'unverified decision promoted to approval')
    disc = quarantine.get('material_discrepancy')
    require(type(disc) is dict and disc.get('source_id') == ALIAS and
            disc.get('crosswalk_group_url') == ROOT_URL and
            disc.get('current_literal_fragment_url') == SLASH_URL and
            disc.get('crosswalk_group_includes_id') is True and
            disc.get('current_literal_group_includes_id') is False,
            'alias discrepancy record changed')
    require(type(crosswalk) is dict and crosswalk.get('schema_version') == 1 and
            crosswalk.get('status') == 'DRAFT_CROSSWALK_ALL_SHARED_SOURCE_GROUPS_UNRESOLVED',
            'original crosswalk review state drift')
    groups = crosswalk.get('groups')
    require(type(groups) is list and len(groups) >= 1, 'crosswalk groups unavailable')
    require(all(type(g) is dict and
                g.get('review_status') == 'pending-human-source-and-reading-scope-review' and
                g.get('reviewer') is None and g.get('reviewed_on') is None and
                g.get('canonical_url') == g.get('url') for g in groups),
            'crosswalk human review fabricated')
    urls = [g['url'] for g in groups]
    require(len(set(urls)) == len(urls), 'duplicate crosswalk URL groups')
    matches = [g for g in groups if g['url'] == ROOT_URL]
    require(len(matches) == 1, 'crosswalk alias group absent/duplicated')
    group = matches[0]
    variants = group.get('variants')
    require(type(variants) is list and len(variants) == 3,
            'original alias source roster changed')
    seen = {(v.get('origin'), v.get('row_index'), v.get('source', {}).get('id'))
            for v in variants if type(v) is dict and type(v.get('source')) is dict}
    require(seen == {('base', 20, 'nchfp-jerky'), ('food', 3, 'nchfp-jerky'),
                     ('hist-food', 14, ALIAS)}, 'alias identity/row membership drift')
    require(len(seen) == 3 and all(v['source'].get('human_link_check') is False
                                   for v in variants), 'source link state falsely checked')
    vmap = {v['origin']: v for v in variants}
    require(vmap['base']['source'].get('url') == ROOT_URL and
            vmap['food']['source'].get('url') == ROOT_URL and
            vmap['hist-food']['source'].get('url') == SLASH_URL,
            'literal alias source URL replaced/normalized')
    identities = group.get('identities')
    require(type(identities) is list and len(identities) == 3 and
            {(x.get('origin'), x.get('row_index'), x.get('id')) for x in identities} == seen,
            'source identity list no longer matches variants')
    sources = fragment.get('sources') if type(fragment) is dict else None
    require(type(sources) is list and len(sources) > 14, 'hist-food source register absent')
    source = sources[14]
    require(type(source) is dict and source.get('id') == ALIAS and
            source.get('url') == SLASH_URL and source.get('human_link_check') is False,
            'hist-food fragment source record changed')
    require(source == vmap['hist-food']['source'], 'crosswalk variant differs from source fragment')
    require(type(metadata) is dict and len(metadata) >= 1, 'metadata census absent')
    routes, impact, edges = set(), [], 0
    for slug, meta in sorted(metadata.items()):
        require(type(meta) is dict and meta.get('slug') == slug and
                meta.get('status', {}).get('publish') == 'draft',
                'article identity/draft status changed')
        route = '/preparedness/' + meta['section'] + '/' + slug + '/'
        require(route not in routes, 'duplicate Preparedness URL')
        routes.add(route)
        uses = meta.get('source_use')
        require(type(uses) is dict and len(uses) > 0, 'source-use evidence absent')
        require(all(type(v) is str and len(v.strip()) >= 8 for v in uses.values()),
                'unsupported source-use explanation')
        edges += len(uses)
        impacted = sorted(set(uses) & {ALIAS, 'nchfp-jerky'})
        if impacted:
            impact.append({'slug': slug, 'route': route, 'literal_source_ids': impacted})
    require(len(impact) > 0, 'jerky alias lost all article-level source uses')
    if strict:
        require(len(groups) == 32 and len(metadata) == 35 and edges == 385,
                'immutable 35-article/385-source baseline changed')
        require(quarantine.get('original_source_rows') == 244 and
                quarantine.get('original_unique_source_ids') == 225 and
                quarantine.get('original_distinct_literal_urls') == 202 and
                quarantine.get('crosswalk_shared_url_groups') == 32 and
                quarantine.get('source_url_group_material_roster_discrepancies') == 1,
                'source-census / discrepancy status drift')
    receipt = hashlib.sha256(json.dumps(impact, sort_keys=True,
                   separators=(',', ':')).encode()).hexdigest()
    return {'schema': SCHEMA, 'state': HOLD,
            'alias_equivalence_verified': False, 'food_safety_approved': False,
            'independent_qd_pass': False, 'publication_authorized': False,
            'shared_url_groups_pending': len(groups), 'article_routes': len(routes),
            'source_uses': edges, 'impacted_articles': impact,
            'impact_receipt_sha256': receipt,
            'required_human_review': ['literal URL/redirect equivalence',
                'source scope and conflicting NCHFP versus USDA FSIS jerky advice',
                'each affected article claim; independent food safety and QD']}

def verify(root: Path) -> dict:
    docs = {k: pinned(root, k, sha) for k, sha in ORIGINAL.items()}
    legacy = docs['preparedness/docs/r151/contributor-three-way.json']
    custody = docs['preparedness/docs/r161/body_custody.json']
    require(legacy.get('decision') == HOLD and legacy.get('qd_pass') is False and
            legacy.get('qualified_safety_review') is False, 'original review gate promoted')
    require(custody.get('status') == HOLD and custody.get('article_count') == 35 and
            custody.get('article_source_relationships') == 385,
            'original body custody inconsistent')
    module_path = root / 'preparedness/tools/r161_body_custody_gate.py'
    require(module_path.is_file() and not module_path.is_symlink(), 'R161 gate missing')
    spec = importlib.util.spec_from_file_location('r172_r161_original', module_path)
    require(spec is not None and spec.loader is not None, 'R161 gate invalid')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    proof = module.verify(root)
    require(proof.get('state') == HOLD and proof.get('articles') == 35 and
            proof.get('citations') == 2000 and proof.get('source_uses') == 385 and
            proof.get('independent_qd_pass') is False,
            'original 35-body / 2000-citation chain failed')
    metadata = {}
    for slug, sha in legacy['metadata_blobs'].items():
        metadata[slug] = pinned(root, f'preparedness/content/articles/{slug}.meta.json', sha)
    return audit(docs['preparedness/review/r171/source-variance-quarantine.json'],
                 docs['preparedness/sources/crosswalk.json'],
                 docs['preparedness/sources/fragments/hist-food.json'], metadata)

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', type=Path, default=Path('.'))
    args = ap.parse_args(argv)
    try:
        result = verify(args.repo.resolve(strict=True))
    except (ValueError, OSError, TypeError, KeyError, AttributeError,
            ImportError, json.JSONDecodeError, UnicodeError) as exc:
        result = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
                  'error': str(exc), 'publication_authorized': False}
    print(json.dumps(result, sort_keys=True))
    return 2

if __name__ == '__main__':
    raise SystemExit(main())
