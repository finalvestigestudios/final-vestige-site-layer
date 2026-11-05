#!/usr/bin/env python3
"""Read-only R153 interlock: 67 tool source uses + eight Historical Food citations.

Constructs a reviewer queue, not source/safety approval. Requires prior authentic
manifests and the R152 frozen Git-source comparator on a trusted checkout.
Intentionally returns exit 2 on valid evidence and invalid evidence alike.
"""
import argparse
import hashlib
import importlib.util
import json
import re
from pathlib import Path

R149_BLOB = 'e63aaaa35bcb5c4378f05ae45a07cc8cfc5c070c'
R151_BLOB = '9cf386519eda970209ff6be4ff0243661cd9d996'
R149_PATH = 'preparedness/docs/r149/tool-source-use-review-docket.json'
R151_PATH = 'preparedness/docs/r151/contributor-three-way.json'
SLUGS = {'pemmican-and-dried-meats': (7, 46), 'pioneer-travel-rations': (1, 39)}
CHANGED_IDENTITIES = {
    ('home-fire-escape-worksheet', 'usfa-fire-escape'),
    ('kit-builder', 'ready-are-you-ready'),
    ('power-outage-planner', 'fsis-power-failure'),
    ('reunification-plan', 'ready-are-you-ready'),
}
TOOLS = {'family-reunification-card': (11, 16), 'home-fire-escape-worksheet': (7, 11),
         'kit-builder': (22, 106), 'power-outage-planner': (17, 26),
         'reunification-plan': (7, 7), 'water-planner': (3, 7)}
SHA = re.compile(r'^[0-9a-f]{40}$')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git_blob(raw):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def load_pinned(root, path, digest):
    target = root / path
    require(target.is_file() and not target.is_symlink(), 'missing or linked evidence: ' + path)
    raw = target.read_bytes()
    require(git_blob(raw) == digest, 'original Git evidence changed: ' + path)
    return json.loads(raw.decode('utf-8'))


def fingerprint(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode('utf-8')).hexdigest()


def make_packet(docket, contributor, alias):
    require(docket.get('schema') == 'FV-PREP-R149-TOOL-CLAIM-CUSTODY-1', 'incorrect tool docket schema')
    require(docket.get('publication_allowed') is False and docket.get('independent_qd') is False,
            'tool docket has unauthorized approval')
    require(docket.get('source_scope_human_review') is False, 'tool docket asserts source approval')
    require(docket.get('human_link_checked_rows') == 0, 'link checks are no longer the frozen baseline')
    require(contributor.get('schema') == 'fv-preparedness-r151-v1', 'incorrect contributor manifest schema')
    require(contributor.get('decision') == 'DRAFT_HARD_HOLD' and contributor.get('qd_pass') is False
            and contributor.get('qualified_safety_review') is False, 'contributor manifest asserts approval')
    require(len(contributor.get('metadata_blobs', {})) == 35, 'not all 35 metadata files are pinned')
    require(len(contributor.get('branches', {})) == 7 and len(contributor.get('source_head_commits', {})) == 7,
            'seven contributor origins are missing')
    require(all(SHA.fullmatch(str(s)) for s in contributor['source_head_commits'].values()),
            'invalid contributor Git SHA')
    require(alias.get('schema') == 'fv-preparedness-r152-v1'
            and alias.get('decision') == 'DRAFT_HARD_HOLD'
            and alias.get('qd_pass') is False
            and alias.get('qualified_food_safety_approval') is False
            and alias.get('release_authorized') is False, 'invalid Historical Food custody result')
    variants = alias.get('source_variants') or {}
    require(variants.get('same_url_is_not_same_evidence') is True
            and variants.get('review') == 'PENDING_INDEPENDENT_HUMAN_SOURCE_AND_FOOD_SAFETY_REVIEW'
            and set(variants.get('origins', {})) == {'base', 'food', 'hist-food'},
            'three distinct source interpretations not retained')
    require(all(v.get('human_link_check') is False for v in variants['origins'].values()),
            'historical source link check unexpectedly approved')
    articles = {a.get('slug'): a for a in contributor.get('articles', [])}
    require(len(articles) == 7, 'seven three-way article comparisons missing')
    historic_tasks = []
    for slug, (expected, total) in SLUGS.items():
        require(articles.get(slug, {}).get('resolution') == 'PINNED_SUBSTITUTION_PENDING',
                'historical citation substitution appears applied')
        article = (alias.get('articles') or {}).get(slug, {})
        require(article.get('substitutions') == expected and article.get('citations') == total,
                'Historical Food occurrence/count drift')
        require(article.get('decision') == 'PENDING_HUMAN_SOURCE_REVIEW',
                'Historical Food review state changed')
        contexts = article.get('contexts', [])
        require(len(contexts) == expected, 'Historical Food citation contexts missing')
        for idx, context in enumerate(contexts, 1):
            require(type(context.get('line')) is int and context['line'] > 0, 'bad citation line')
            require(isinstance(context.get('excerpt'), str) and context['excerpt'].strip()
                    and len(context['excerpt']) <= 320, 'missing or overlong citation excerpt')
            historic_tasks.append({'type': 'historic_food_citation', 'article': slug,
                                  'occurrence': idx, 'line': context['line'], 'excerpt': context['excerpt'],
                                  'old_source_id': 'hist-food-nchfp-jerky', 'suggested_alias': 'nchfp-jerky',
                                  'review': 'PENDING', 'qualified_reviewer': None,
                                  'review_fingerprint': fingerprint([slug, idx, context])})
    rows = docket.get('source_use_rows')
    require(isinstance(rows, list) and len(rows) == docket.get('source_use_row_count') == 67,
            '67 tool/source relationships missing')
    require(docket.get('currently_unresolved_source_ids') == 58, 'missing source origin count changed')
    require(set(docket.get('candidate_tool_origins', {})) == set(TOOLS), 'unexpected tool origin list')
    require(all(s.get('publication_allowed') is False for s in docket.get('tool_summaries', [])),
            'tool summary claims publication approval')
    counts, unique, unresolved, changed, tasks = {}, set(), 0, set(), []
    for row in rows:
        tool, sid = row.get('tool'), row.get('source_id')
        require(tool in TOOLS and isinstance(sid, str) and bool(sid), 'unknown tool/source identifier')
        require((tool, sid) not in unique, 'duplicate tool/source relationship')
        unique.add((tool, sid))
        count = row.get('citation_occurrences')
        require(type(count) is int and count > 0, 'invalid citation multiplicity')
        require(row.get('review_decision') == 'PENDING'
                and row.get('human_link_check_recorded') is False
                and row.get('human_source_scope_adjudicated') is False
                and row.get('medical_safety_approved') is False
                and row.get('reviewer') is None, 'fabricated human/source/medical approval')
        require(isinstance(row.get('literal_url'), str) and row['literal_url'].startswith('https://'),
                'source URL is not HTTPS')
        require(all(isinstance(row.get(k), str) and row[k].strip() for k in
                    ('title', 'publisher', 'source_supports', 'author_specific_use')),
                'source scope missing')
        require(row.get('candidate_origin') == docket['candidate_tool_origins'][tool],
                'candidate source origin changed')
        require(type(row.get('currently_resolvable')) is bool, 'resolution flag invalid')
        if not row['currently_resolvable']:
            unresolved += 1
        if (tool, sid) in CHANGED_IDENTITIES:
            require(row['currently_resolvable'], 'shadow-changed identity is no longer resolvable')
            changed.add((tool, sid))
        c = counts.setdefault(tool, [0, 0]); c[0] += 1; c[1] += count
        tasks.append({'type': 'tool_source_scope', 'tool': tool, 'source_id': sid,
                      'citations': count, 'url': row['literal_url'], 'publisher': row['publisher'],
                      'supports': row['source_supports'], 'author_specific_use': row['author_specific_use'],
                      'current_origin': row['current_origin'], 'candidate_origin': row['candidate_origin'],
                      'currently_resolvable': row['currently_resolvable'],
                      'interpretation_changed_by_shadow_origin': (tool, sid) in CHANGED_IDENTITIES,
                      'review': 'PENDING', 'qualified_reviewer': None,
                      'review_fingerprint': fingerprint(row)})
    require(counts == {k: list(v) for k, v in TOOLS.items()}, 'tool citation occurrence or source identity changed')
    require(unresolved == 58 and changed == CHANGED_IDENTITIES, '58 unresolved / four shadow changes not retained')
    require(sum(x['citations'] for x in tasks) == 173, '173 tool citation occurrences lost')
    require(len(historic_tasks) == 8, 'eight Historical Food contexts lost')
    result = {'schema': 'fv-preparedness-r153-review-interlock-v1',
              'decision': 'DRAFT_HARD_HOLD', 'release_authorized': False,
              'qualified_source_review': False, 'medical_safety_approved': False,
              'independent_qd_pass': False, 'original_articles_changed': False,
              'source_crosswalk_changed': False, 'genuine_paid_preparedness_sku_verified': False,
              'tool_source_relationships': 67, 'tool_citation_occurrences': 173,
              'tool_unresolved': 58, 'source_interpretation_changes': 4,
              'historical_food_substitutions': 8, 'review_tasks_total': 75,
              'tool_review_tasks': tasks, 'historic_food_review_tasks': historic_tasks}
    result['packet_fingerprint'] = fingerprint({'tool': tasks, 'historic': historic_tasks})
    return result


def real_packet(repo):
    docket = load_pinned(repo, R149_PATH, R149_BLOB)
    contributor = load_pinned(repo, R151_PATH, R151_BLOB)
    tool_path = repo / 'preparedness/tools/r152_jerky_alias_gate.py'
    require(tool_path.is_file() and not tool_path.is_symlink(), 'missing frozen R152 source custody gate')
    spec = importlib.util.spec_from_file_location('r152_read_only_custody', tool_path)
    require(spec is not None and spec.loader is not None, 'cannot import R152 source custody')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    alias = mod.run(repo)  # exact Git original/source objects; raises when no trusted checkout
    return make_packet(docket, contributor, alias)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--report', type=Path)
    args = parser.parse_args(argv)
    try:
        packet = real_packet(args.repo.resolve())
        if args.report is not None:
            report = args.report.resolve()
            require(not args.report.exists() and not report.is_relative_to(args.repo.resolve()),
                    'report must be a new local path outside the original repository')
            report.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        print(json.dumps({'decision': packet['decision'], 'review_tasks_total': 75,
                          'qualified_source_review': False, 'independent_qd_pass': False}))
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, json.JSONDecodeError) as error:
        print(json.dumps({'decision': 'INVALID_HARD_HOLD', 'error': str(error)}))
    return 2  # Neither structural success nor failure approves publication.


if __name__ == '__main__':
    raise SystemExit(main())
