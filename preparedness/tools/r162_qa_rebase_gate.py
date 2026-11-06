#!/usr/bin/env python3
"""R162: independently rebase QA PR #157 and fixture PRs #169/#973 onto the frozen 35.

Read-only reconciliation. Matching a QA intent is NOT medical advice, source approval,
PR merge, QD PASS or permission to publish. No access to WordPress or merchant accounts.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path

PINS = {
    'household': ('preparedness/content/articles/household-emergency-plan.body.html', 'f81cd43516e8295104230412f18776919148f905'),
    'kit': ('preparedness/content/articles/three-day-kit.body.html', '933f38ff3cd55a241cf9b392014fc52d4961e84f'),
    'sources': ('preparedness/sources/fragments/start.json', '96140d6d1872588e5d20d9052445c9157e88934d'),
    'taxonomy': ('preparedness/taxonomy.json', '15c547bb3018ac182b12a51036389cfa39a59168'),
    'tests': ('preparedness/tests/test_preparedness.py', 'c329f98e051d2aabe31a3343869b0fdac355b315'),
}
BASE = 'e7d1eabf6210460c6f3b35e9f8a32235e795844d'
QA_HEADS = {
    '157': '7d1ae6b8ef93d10cfb6810987672360885e9c1aa',
    '169': 'e9cd7766dac59d47ab467d8945269b9146c2aef5',
    '973': '4d40996a559b0124d74a9bb3bdcd481ad1992aa8',
}
SCHEMA = 'fv-preparedness-r162-qa-rebase-v1'


def need(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def git_blob(raw: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()


def read_snapshot(root: Path) -> dict[str, str]:
    """Never silently treat current heads as canonical if their contents drift."""
    data = {}
    for key, (name, sha) in PINS.items():
        path = root / name
        need(path.is_file() and not path.is_symlink(), 'missing or symlink: ' + name)
        raw = path.read_bytes()
        need(git_blob(raw) == sha, 'unreviewed canonical drift: ' + name)
        data[key] = raw.decode('utf-8')
    return data


def function_text(source: str, name: str) -> str:
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise ValueError('invalid synthetic fixture test syntax') from exc
    hits = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
    need(len(hits) == 1, 'required isolated fixture test missing/duplicated: ' + name)
    return ast.get_source_segment(source, hits[0]) or ''


def verify_payload(data: dict[str, str]) -> dict:
    """Pure evidence-intent checks. Called on pinned real files; synthetic tests call directly."""
    need(set(data) == set(PINS), 'QA packet inputs changed')
    household, kit = data['household'], data['kit']
    need('The simulated-outage evening.' in household, 'household practice heading missing')
    # A breaker-off drill is NOT an acceptable equivalent of a simulated outage.
    need('Do not switch off the main breaker as a drill.' in household, 'no-main-breaker warning absent')
    for term in ('refrigerator and freezer', 'smoke and carbon monoxide alarms',
                 'medical or safety-critical equipment', 'sump pump', 'switch off nonessential lights'):
        need(term in household, 'household critical loads missing: ' + term)
    need('Switch off the main power' not in household, 'unsafe older main-power practice reappeared')
    need('Medicines that need refrigeration: ask your prescriber or pharmacist' in kit,
         'refrigerated-medicine expert referral missing')
    for term in ('Do not stop, throw away or ration a medicine',
                 'Two FEMA documents, two wordings', 'start-fema-power-sheet',
                 'start-ready-power', 'drug\'s label', 'replacement'):
        need(term in kit, 'refrigerated-medicine source/qualifier missing: ' + term)
    # Preserve the explicit editorial uncertainty; the two sources do NOT prove
    # the rule is individually appropriate for an actual patient's prescription.
    need('We do not know which document FEMA intends to govern' in kit,
         'medical-source uncertainty removed')
    sources = json.loads(data['sources'])
    entries = [s for s in sources['sources'] if s.get('id') == 'start-redcross-older-adults']
    need(len(entries) == 1, 'Red Cross original source ID changed/duplicated')
    entry = entries[0]
    need(entry.get('kind') == 'nonprofit' and entry.get('publisher') == 'American Red Cross',
         'Red Cross incorrectly classified as regulator')
    need(entry.get('human_link_check') is False, 'Red Cross human-check status falsely upgraded')
    need(entry.get('url') == 'https://www.redcross.org/get-help/how-to-prepare-for-emergencies/older-adults.html',
         'Red Cross official URL changed')
    taxonomy = json.loads(data['taxonomy'])
    slate = taxonomy['slate']
    need(len(slate) == 35 and len(set(a['slug'] for a in slate)) == 35, '35-title slate drift')
    for slug in ('household-emergency-plan', 'three-day-kit', 'go-bags', 'preparedness-real-households'):
        matches = [a for a in slate if a.get('slug') == slug]
        need(len(matches) == 1 and matches[0].get('gate') is True, 'source/safety gate weakened: ' + slug)
    src = data['tests']
    for name in ('test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source',
                 'test_register_fragments_cannot_duplicate_ids'):
        function = function_text(src, name)
        for required in ('TemporaryDirectory', 'copytree(', 'sandbox', 'with self.assertRaisesRegex'):
            need(required in function, 'test-isolation guard missing: ' + name + ': ' + required)
        need('ROOT / "sources" / "fragments"' not in function,
             'shared fixture directory write pattern reappeared: ' + name)
    fixture_test = function_text(src, 'test_unverified_source_cannot_be_cited')
    for required in ('test-fixture-unverified-source', '"verified_on": None', 'unverified source'):
        need(required in fixture_test, 'synthetic source test regressed: ' + required)
    return {
        'schema': SCHEMA, 'state': 'DRAFT_HARD_HOLD', 'original_article_count_from_r161': 35,
        'canonical_parent_sha': BASE, 'independent_qa_heads': QA_HEADS,
        'qa_157_disposition': 'canonical_equivalent_qualifiers_present_not_merge_approved',
        'qa_169_973_disposition': 'synthetic_isolation_behavior_present_not_merge_approved',
        'source_reclassification': 'redcross_nonprofit_human_link_check_false',
        'canonical_files_checked': len(PINS), 'source_claim_adjudication': False,
        'qualified_medical_review': False, 'independent_qd_pass': False,
        'live_publication_authorized': False, 'purchasable_preparedness_sku_verified': False,
    }


def check(root: Path) -> dict:
    # R161's immutable 35-body gate must succeed structurally BEFORE any
    # QA intent checks run. It cannot approve content or release.
    import sys
    tools = root / 'preparedness' / 'tools'
    sys.path.insert(0, str(tools))
    import r161_body_custody_gate as custody
    baseline = custody.verify(root)
    need(baseline['state'] == 'DRAFT_HARD_HOLD' and baseline['articles'] == 35,
         '35-body custody cannot be established')
    return verify_payload(read_snapshot(root))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, default=Path('.'))
    args = parser.parse_args(argv)
    try:
        report = check(args.repo.resolve(strict=True))
    except (ValueError, KeyError, OSError, UnicodeError, TypeError, SyntaxError, json.JSONDecodeError, ImportError) as exc:
        report = {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD', 'error': str(exc),
                  'independent_qd_pass': False, 'live_publication_authorized': False}
    print(json.dumps(report, sort_keys=True))
    return 2  # successful source rebase is still a HARD HOLD, never QD PASS


if __name__ == '__main__':
    raise SystemExit(main())
