#!/usr/bin/env python3
"""Non-mutating semantic reconciliation for FV Preparedness QA #157/#169/#973.

The original branches and PRs remain separate. This script cannot authorize release;
passing structural evidence returns DRAFT_HARD_HOLD and process exit status 2.
"""
from __future__ import annotations
import argparse
import ast
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re
import sys

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
SCHEMA = 'fv-preparedness-r182-semantic-reconciliation-v1'
FILES = {
    'plan': 'preparedness/content/articles/household-emergency-plan.body.html',
    'kit': 'preparedness/content/articles/three-day-kit.body.html',
    'sources': 'preparedness/sources/fragments/start.json',
    'taxonomy': 'preparedness/taxonomy.json',
    'tests': 'preparedness/tests/test_preparedness.py',
}
# Connected GitHub content SHA at exact R181 head 1062eb2c775bed8c061fa853d25bc954c28c9529.
# Git blob SHA, NOT sha256(content). Recheck all five before changing any custody baseline.
PINNED_BLOBS = {
    'plan': 'f81cd43516e8295104230412f18776919148f905',
    'kit': '933f38ff3cd55a241cf9b392014fc52d4961e84f',
    'sources': '96140d6d1872588e5d20d9052445c9157e88934d',
    'taxonomy': '15c547bb3018ac182b12a51036389cfa39a59168',
    'tests': 'c329f98e051d2aabe31a3343869b0fdac355b315',
}
DRAFT_PR_HEADS = {157: '7d1ae6b8ef93d10cfb6810987672360885e9c1aa',
                  169: 'e9cd7766dac59d47ab467d8945269b9146c2aef5',
                  973: '4d40996a559b0124d74a9bb3bdcd481ad1992aa8'}
REQUIRED_TEST_FUNCTIONS = (
    'test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source',
    'test_register_fragments_cannot_duplicate_ids',
    'test_unverified_source_cannot_be_cited',
    'test_every_modern_slate_item_is_gated',
    'test_red_cross_cannot_be_called_a_regulator',
)
REQUIRED_FAMILY = (
    'household-emergency-plan', 'three-day-kit', 'go-bags', 'preparedness-real-households',
)

def demand(check, message):
    if not check:
        raise ValueError(message)


def blob_sha(value):
    data = value.encode('utf-8')
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def content_segment(body, marker, tag='li'):
    # Prevent a safety phrase in a bibliography, footer or comment from satisfying a
    # requirement for the *actual* local instruction. We accept only containing HTML block.
    pattern = rf'<{tag}(?:\s[^>]*)?>[\s\S]*?</{tag}>'
    blocks = re.findall(pattern, body, re.I)
    matches = [x for x in blocks if marker.lower() in html.unescape(re.sub('<[^>]+>', ' ', x)).lower()]
    demand(len(matches) == 1, f'{marker}: exactly one content-block match required')
    return html.unescape(re.sub(r'<[^>]+>', ' ', matches[0])).lower()


def check_sources(values, pins):
    demand(isinstance(values, dict) and set(values) == set(FILES), 'five source items required')
    for key in FILES:
        demand(isinstance(values[key], str) and bool(values[key]), f'{key} source unreadable')
        demand(blob_sha(values[key]) == pins[key], f'{key}: source blob SHA drift')
    # The content tests below are deliberately independently executable with test-controlled
    # pins. The production CLI always supplies the immutable connected-GitHub PINNED_BLOBS.
    plan = values['plan']
    kit = values['kit']
    p = content_segment(plan, 'simulated-outage evening')
    for phrase in ('switch off nonessential lights', 'leave on everything that keeps people safe',
                   'smoke and carbon monoxide alarms', 'medical or safety-critical equipment',
                   'do not switch off the main breaker'):
        demand(phrase in p, f'household rehearsal safety phrase missing: {phrase}')
    demand('switch off the main power' not in p and 'switch off the main breaker for' not in p,
           'unsafe main-power drill instruction')
    paragraph = content_segment(kit, 'Do not stop, throw away or ration', tag='p')
    for phrase in ('do not stop, throw away or ration', 'prescriber or pharmacist',
                   'each of your medicines', 'refrigeration', 'replacement', 'if you are already in an outage'):
        demand(phrase in paragraph, f'medicine safety caution missing: {phrase}')
    second = content_segment(kit, 'interim-use and replacement plan', tag='p')
    demand('{{cite:start-cdc-pyh-prescriptions}}' in kit,
           'medication advice provenance token missing')
    demand('pharmacist' in second and 'refrigerated medicine' in second,
           'refrigeration contingency/source explanation missing')
    demand(not re.search(r'href\s*=\s*["\']https?://[^"\']*(?:awin1\.com|payhip\.com)',
                         plan + kit, re.I), 'unexpected merchant redirect in free safety guides')
    source = json.loads(values['sources'])
    entries = source.get('sources')
    demand(isinstance(entries, list), 'original start source list absent')
    red = [x for x in entries if x.get('id') == 'start-redcross-older-adults']
    demand(len(red) == 1 and red[0].get('publisher') == 'American Red Cross' and
           red[0].get('kind') == 'nonprofit', 'Red Cross must not be classed as regulator')
    tax = json.loads(values['taxonomy'])
    slate = tax.get('slate')
    demand(isinstance(slate, list) and len(slate) == 35, '35-article taxonomy missing')
    slugs = [x.get('slug') for x in slate]
    demand(len(set(slugs)) == 35, 'duplicate slate slugs')
    demand(all(isinstance(x.get('gate'), bool) and x['gate'] for x in slate
               if x.get('track') == 'modern'), 'ungated modern safety instructions')
    demand(all(next((x for x in slate if x.get('slug') == slug), {}).get('gate') is True
               for slug in REQUIRED_FAMILY), 'Start Here safety gates missing')
    tree = ast.parse(values['tests'])
    funcs = {node.name: node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for name in REQUIRED_TEST_FUNCTIONS:
        demand(name in funcs, f'original regression removed: {name}')
    for name in REQUIRED_TEST_FUNCTIONS[:2]:
        fn = ast.get_source_segment(values['tests'], funcs[name]) or ''
        for phrase in ('TemporaryDirectory', 'copytree', 'root=sandbox', 'duplicate source id'):
            if phrase == 'duplicate source id' and name == REQUIRED_TEST_FUNCTIONS[0]:
                # Both fixture tests explicitly reject duplicate IDs.
                pass
            demand(phrase in fn, f'{name}: required isolated fixture property missing: {phrase}')
        demand('ROOT / "sources" / "fragments"' not in fn,
               f'{name}: unsafe write to shared source path')
    unverified = ast.get_source_segment(values['tests'], funcs[REQUIRED_TEST_FUNCTIONS[2]]) or ''
    demand('test-fixture-unverified-source' in unverified and 'verified_on' in unverified,
           'synthetic unverified-citation regression missing')
    demand('not a regulator' in values['tests'] and 'test_every_modern_slate_item_is_gated' in values['tests'],
           'safety/source-type regression missing')
    # Also reject any newly introduced shared ROOT file writes anywhere in test module.
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ('write_text', 'unlink', 'write_bytes'):
            expr = ast.get_source_segment(values['tests'], node.func.value) or ''
            demand('ROOT' not in expr, 'test module writes directly to shared ROOT')
    return {'safety_rehearsal': 'structurally_present',
            'medical_caution': 'structurally_present',
            'red_cross_source_kind': 'nonprofit',
            'modern_gated': True, 'article_roster': 35,
            'fixture_isolation': 'both_source_fragment_tests_use_temporary_copy',
            'citation_claims_verified': False, 'safety_adjudicated': False}


def inspect(repo):
    values = {key: (repo / path).read_text(encoding='utf-8') for key, path in FILES.items()}
    signals = check_sources(values, PINNED_BLOBS)
    receipt_path = repo / 'preparedness/review/r181/contributor-evidence.json'
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    gate_path = repo / 'preparedness/tools/r181_contributor_intake_gate.py'
    spec = importlib.util.spec_from_file_location('_r181_gate', gate_path)
    demand(spec is not None and spec.loader is not None, 'R181 gate could not be loaded')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    earlier = mod.inspect(receipt)
    demand(earlier['state'] == HOLD and earlier['independent_prs_held'] == 3 and
           earlier['claude_branches_intact'] == 7, 'R181 inventory / seven branches not admitted')
    for pr in receipt['review_prs']:
        demand(pr['head_sha'] == DRAFT_PR_HEADS[pr['number']], 'PR head custody changed')
    digest = hashlib.sha256(json.dumps({k: blob_sha(v) for k,v in values.items()},
                                  sort_keys=True).encode()).hexdigest()
    return {'schema': SCHEMA, 'state': HOLD, 'publication_authorized': False,
            'independent_qd_pass': False, 'native_build_executed': False,
            'semantic_reconciliation': signals, 'source_blobs': PINNED_BLOBS,
            'content_custody_sha256': digest, 'qa_prs': DRAFT_PR_HEADS,
            'independent_qa_prs_merge_authorized': False,
            'review_needed': ['human source and safety adjudication',
                              'complete trusted native validation/build',
                              'independent QD and staging browser/print review',
                              'actual checkout & seller/paid SKU verification']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        report = inspect(args.repo)
    except (OSError, ValueError, KeyError, TypeError, SyntaxError, json.JSONDecodeError) as exc:
        report = {'schema': SCHEMA, 'state': INVALID, 'error': str(exc),
                  'publication_authorized': False, 'independent_qd_pass': False}
    rendered = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.output:
        try:
            args.output.write_text(rendered, encoding='utf-8')
        except OSError as exc:
            print(f'report save failed: {exc}', file=sys.stderr)
    print(rendered, end='')
    return 2

if __name__ == '__main__':
    sys.exit(main())
