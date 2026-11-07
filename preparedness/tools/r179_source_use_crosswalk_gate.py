#!/usr/bin/env python3
"""R179: deterministic, fail-closed source-use/citation crosswalk; DRAFT only.

A citation identifier or a machine-fetched URL is NOT verification of the
nearby claim, modern safety, editorial permission, an order, or publication.
No CMS, payment, email, analytics or other network call is performed.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
SCHEMA = 'fv-preparedness-r179-source-use-crosswalk-v1'
FILES = {
    'register.json': 'b25cd02b9beaadaf5a2db0c52e0ae66d20b1ac77',
    'fragments/food.json': 'a1f73c8170932d6b3192e9cd506686d516d23d30',
    'fragments/health.json': 'cc29c439372b9d49debf78e63020ffe4d62baeb8',
    'fragments/hist-field.json': '3dafa9425f3829c0be2e6fea00889aff95124031',
    'fragments/hist-food.json': 'd10628342fea5f177a8d1be00dd906d0c9c7850e',
    'fragments/hist-home.json': '8d85fd868508c5caba14a839d119d55f31f14f72',
    'fragments/shelter.json': '2a3f1a7ddeab2782add875be1e0e378513504aa1',
    'fragments/start.json': '96140d6d1872588e5d20d9052445c9157e88934d',
}
CITE = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def unique_dict(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError('duplicate JSON key: ' + k)
        out[k] = v
    return out


def load_json(path: Path, limit=1_000_000):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
        raise ValueError('missing, oversized or symlink input: ' + str(path))
    raw = path.read_bytes()
    obj = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_dict)
    if not isinstance(obj, dict):
        raise ValueError('expected JSON object at ' + str(path))
    return obj, raw


def must(ok, error):
    if not ok:
        raise ValueError(error)


def valid_source(s):
    must(isinstance(s, dict) and isinstance(s.get('id'), str)
         and ID.fullmatch(s['id']), 'malformed source identifier')
    url = s.get('url')
    must(isinstance(url, str) and len(url) < 2048
         and not any(ord(c) < 33 for c in url), s['id'] + ': unsafe or absent source URL')
    p = urlsplit(url)
    must(p.scheme == 'https' and p.hostname and p.username is None and p.password is None
         and not p.fragment and p.port in (None, 443),
         s['id'] + ': source must be an HTTPS citation URL without credentials or fragment')
    return url


def build_crosswalk(pins: dict, custody: dict, metadata: dict,
                    bodies: dict, inventories: dict) -> dict:
    """Pure function: deterministic report for synthetic tests / authenticated CLI.

    Pins and custody are independently checked against R178 by inspect_repo.
    Returns an *inventory only*, never an approval. Unknown source is a hard error.
    """
    rows = pins.get('articles')
    must(isinstance(rows, list) and len(rows) == 35, '35-article roster absent')
    must(len({r['slug'] for r in rows}) == 35 and
         set(metadata) == set(bodies) == {r['slug'] for r in rows},
         '35-article source corpus identities differ')
    must(custody.get('article_count') == 35 and
         custody.get('article_source_relationships') == 385,
         'R161 original custody counts differ')
    must(set(custody['articles']) == set(metadata), 'R161 body roster mismatch')

    sources = defaultdict(list)
    raw_count = 0
    for path in sorted(inventories):
        source_list = inventories[path].get('sources')
        must(isinstance(source_list, list), path + ': no source entries')
        for source in source_list:
            url = valid_source(source)
            raw_count += 1
            sources[source['id']].append({'inventory': path, 'url': url,
                                         'verified_on': source.get('verified_on'),
                                         'human_link_check': source.get('human_link_check') is True})
    must(bool(sources), 'empty source inventories')
    # Different URLs for the SAME identifier are not interchangeable.
    for identifier, variants in sources.items():
        must(len({v['url'] for v in variants}) == 1,
             identifier + ': conflicting original source URLs')

    canon = defaultdict(set)
    raw_url = defaultdict(set)
    for identifier, variants in sources.items():
        url = variants[0]['url']
        raw_url[url].add(identifier)
        # Grouping is ONLY for human investigation, never source substitution.
        canon[url.rstrip('/')].add((identifier, url))

    crosswalk = []
    totals = Counter()
    unfetched = []
    uncited = []
    for pin in sorted(rows, key=lambda x: x['slug']):
        slug = pin['slug']
        meta = metadata[slug]
        body = bodies[slug]
        must(meta.get('slug') == slug and meta.get('n') == pin['article_number']
             and meta.get('status', {}).get('publish') == 'draft',
             slug + ': invalid article identity or publication state')
        must(meta.get('safety_review', {}).get('state') == pin['recorded_state'],
             slug + ': modified historical safety state')
        uses = meta.get('source_use')
        must(isinstance(uses, dict) and len(uses) == pin['source_use_count'],
             slug + ': source interpretation inventory changed')
        must(isinstance(body, str), slug + ': missing original HTML')
        citations = CITE.findall(body)
        must(len(citations) == custody['articles'][slug]['citations'],
             slug + ': citation occurrences changed')
        cited = Counter(citations)
        must(set(cited).issubset(uses), slug + ': citation not declared by author')
        for source_id, scope in sorted(uses.items()):
            must(isinstance(source_id, str) and ID.fullmatch(source_id)
                 and isinstance(scope, str) and scope.strip(),
                 slug + ': malformed or empty authored source relationship')
            must(source_id in sources,
                 slug + ': source identifier not present in pinned register or fragments: ' + source_id)
            matches = sources[source_id]
            first = matches[0]
            crosswalk.append({
                'article': slug, 'source_id': source_id, 'citation_occurrences': cited[source_id],
                'scope_sha256': hashlib.sha256(scope.encode('utf-8')).hexdigest(),
                'source_url': first['url'],
                'source_inventory_files': sorted(m['inventory'] for m in matches),
                'inventory_record_count': len(matches),
                'has_human_link_check': any(m['human_link_check'] for m in matches),
                'machine_verified_any': any(bool(m['verified_on']) for m in matches),
                'independently_reviewed_claim': False,
                'modern_safety_approved': False,
            })
            if not cited[source_id]:
                uncited.append({'article': slug, 'source_id': source_id})
            if not any(m['verified_on'] for m in matches):
                unfetched.append({'article': slug, 'source_id': source_id})
        totals['articles'] += 1
        totals['citations'] += len(citations)
        totals['source_uses'] += len(uses)
    must((totals['articles'], totals['citations'], totals['source_uses']) ==
         (35, 2000, 385), 'original 35/2000/385 evidence corpus count mismatch')
    # The digest proves ordering and fields of this generated *inventory*, not factual validity.
    raw = json.dumps(crosswalk, sort_keys=True, ensure_ascii=False,
                     separators=(',', ':')).encode('utf-8')
    return {'schema': SCHEMA, 'state': HOLD, 'publication_authorized': False,
            'qualified_safety_review_complete': False, 'independent_qd_pass': False,
            'human_source_claim_review_complete': False,
            'commercial_product_verified': False, 'word_press_ready': False,
            'article_count': totals['articles'], 'citation_occurrences': totals['citations'],
            'article_source_relationships': totals['source_uses'],
            'source_inventory_records': raw_count, 'unique_source_ids': len(sources),
            'duplicate_source_id_groups': sorted(i for i, v in sources.items() if len(v) > 1),
            'shared_literal_url_groups': sorted(
                [sorted(s) for s in raw_url.values() if len(s) > 1]),
            'trailing_slash_review_groups': sorted(
                [sorted(v) for v in canon.values() if len({url for _, url in v}) > 1]),
            'uncited_author_source_uses': uncited,
            'unfetched_source_uses': unfetched,
            'crosswalk_sha256': hashlib.sha256(raw).hexdigest(),
            'crosswalk': crosswalk}


def inspect_repo(root: Path, expected_files: dict | None = None) -> dict:
    """CLI always fails publication admission, even for intact inputs."""
    r = {'schema': SCHEMA, 'state': INVALID,
         'publication_authorized': False, 'independent_qd_pass': False,
         'qualified_safety_review_complete': False,
         'human_source_claim_review_complete': False,
         'commercial_product_verified': False, 'errors': []}
    try:
        must(root.is_dir() and not root.is_symlink(), 'checkout missing or symlinked')
        module = Path(__file__).with_name('r178_safety_state_admission_gate.py')
        must(module.is_file() and not module.is_symlink(), 'R178 whole-slate gate missing')
        spec = importlib.util.spec_from_file_location('prep_r178', module)
        prior = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(prior)
        previous = prior.inspect(root)
        must(previous['state'] == HOLD and not previous.get('errors'),
             'R178 whole-slate custody gate has not established structural HOLD')
        pin, _ = load_json(root / prior.PIN_PATH)
        custody, _ = load_json(root / prior.CUSTODY_PATH)
        invent = {}
        for relative, blob in (expected_files or FILES).items():
            # CLI supplies no overrides; alternate pins are only for synthetic tests.
            must(relative in FILES and isinstance(blob, str), 'unlisted source inventory')
            path = root / 'preparedness/sources' / relative
            obj, raw = load_json(path)
            must(git_blob(raw) == blob, 'source inventory changed: ' + relative)
            invent[relative] = obj
        article_dir = root / 'preparedness/content/articles'
        metadata, bodies = {}, {}
        for row in pin['articles']:
            slug = row['slug']
            metadata[slug], _ = load_json(article_dir / (slug+'.meta.json'))
            body = article_dir / (slug+'.body.html')
            must(body.is_file() and not body.is_symlink() and
                 body.stat().st_size <= 8_000_000,
                 'unsafe or missing article body: ' + slug)
            bodies[slug] = body.read_text(encoding='utf-8')
        r = build_crosswalk(pin, custody, metadata, bodies, invent)
        # The full crosswalk can be piped to a local file if needed; no writes by us.
        r['errors'] = []
    except (ValueError, OSError, KeyError, TypeError, UnicodeError, AttributeError) as error:
        r['errors'].append(str(error))
    return r


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo', type=Path, default=Path('.'))
    p.add_argument('--summary', action='store_true', help='suppress 385 review rows')
    args = p.parse_args(argv)
    data = inspect_repo(args.repo)
    if args.summary:
        data = {k: v for k, v in data.items() if k != 'crosswalk'}
    print(json.dumps(data, indent=2, sort_keys=True))
    return 2  # No form of local structural proof authorizes publication.


if __name__ == '__main__':
    sys.exit(main())
