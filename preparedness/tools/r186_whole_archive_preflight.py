#!/usr/bin/env python3
"""Read-only R186 35-guide + six-tool integrated, *non-approval* native preflight.

Runs the real native validator, builder, >=36 unit tests and nine independent
custody gates on ONE disposable full-tree copy. Every structurally good result
still exits 2 and remains DRAFT_HARD_HOLD. Never publish or interpret a
citation/structural check as independent source, safety or commerce approval.
This is a test runner for a trusted checkout, NOT a hostile-code sandbox.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from importlib import util as import_util
from pathlib import Path
import re
import shutil
import tempfile

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
SCHEMA = 'fv-preparedness-r186-whole-archive-native-preflight-v1'
TOOLS = frozenset(('family-reunification-card', 'home-fire-escape-worksheet',
                   'kit-builder', 'power-outage-planner', 'reunification-plan',
                   'water-planner'))
FALSE_FLAGS = frozenset(('publication_authorized', 'publication_allowed',
    'wordpress_publication_performed', 'independent_qa_verified',
    'independent_qd_pass', 'independent_qd_verified',
    'qualified_safety_review_complete', 'qualified_source_review',
    'independent_source_review', 'food_safety_approved', 'medical_safety_approved',
    'commercial_offer_verified', 'merchant_offer_verified',
    'payment_offer_verified', 'paid_checkout_enabled',
    'customer_conversion_verified', 'independent_qa_prs_merge_authorized'))
# A missing command, fake success exit 0, non-JSON output, or a silently skipped
# gate invalidates the *entire* packet. R181 is evaluated inside R182.
GATES = (
    ('r174', 'r174_rendered_citation_gate.py', '--check-export'),
    ('r175', 'r175_link_custody_gate.py', '--check-export'),
    ('r177', 'r177_safety_wording_gate.py', '--check-export'),
    ('r178', 'r178_safety_state_admission_gate.py'),
    ('r179', 'r179_source_use_crosswalk_gate.py', '--summary'),
    ('r180', 'r180_docket_reconciliation_gate.py', '--summary'),
    ('r182', 'r182_semantic_patch_reconciliation_gate.py'),
    ('r184', 'r184_report_admission_gate.py'),
    ('r185', 'r185_tool_custody_gate.py'),
)


def safe_false(value, path='receipt'):
    """Recursive: no hidden nested approval claim may be smuggled into a receipt."""
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FALSE_FLAGS and item is not False:
                raise ValueError(f'{path}.{key}: explicit false required')
            safe_false(item, path+'.'+key)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            safe_false(item, f'{path}[{i}]')


def verify_gate(label: str, step: dict) -> dict:
    """Pure adjudicator; a valid EXIT 2 is a structural HOLD, never PASS."""
    result = {'step': label, 'returncode': step.get('returncode'),
              'status': 'FAIL', 'reason': 'invalid structural HOLD'}
    stdout = step.get('stdout', '')
    result['stdout_sha256'] = hashlib.sha256(stdout.encode('utf-8')).hexdigest()
    try:
        if label not in {r[0] for r in GATES} or step.get('returncode') != 2:
            raise ValueError('missing gate or unexpected exit code')
        receipt = json.loads(stdout)
        if not isinstance(receipt, dict) or receipt.get('state') != HOLD:
            raise ValueError('missing DRAFT_HARD_HOLD receipt')
        if receipt.get('errors') or receipt.get('error') or receipt.get('errors_count', 0):
            raise ValueError('gate reports errors')
        safe_false(receipt)
        checks = {
            'r174': {'article_count': 35, 'rendered_citations': 2000,
                     'rendered_source_uses': 385, 'draft_export_bytes_checked': True},
            'r175': {'articles': 35, 'export_compared': True},
            'r177': {'review_only': True, 'errors_count': 0},
            'r178': {'article_count': 35, 'citations': 2000, 'source_use': 385},
            'r179': {'article_count': 35, 'citation_occurrences': 2000},
            'r184': {'articles_checked': 35, 'citation_occurrences_checked': 2000},
            'r185': {'tool_count': 6, 'source_rows': 67,
                     'citation_occurrences': 173},
        }
        for key, expected in checks.get(label, {}).items():
            if receipt.get(key) != expected or type(receipt.get(key)) != type(expected):
                raise ValueError(f'{key} missing or changed')
        if label == 'r180' and (receipt.get('review_tickets_pending') != 21 or
                                receipt.get('family_source_decisions_pending') != 11 or
                                receipt.get('jerky_claim_decisions_pending') != 10):
            raise ValueError('21 unresolved source decisions missing')
        if label == 'r182' and set(map(str, receipt.get('qa_prs', {}))) != {'157','169','973'}:
            raise ValueError('independent QA patch custody missing')
        result['status'] = 'STRUCTURAL_HOLD'
        result.pop('reason')
    except (ValueError, TypeError, AttributeError) as exc:
        result['reason'] = str(exc)[:200]
    return result


def check_census(preparedness: Path, inventory: dict) -> dict:
    """Fail closed before *any* executable is run on a snapshot."""
    articles, tools = set(), set()
    for folder, expected, target in [('articles', 35, articles), ('tools', 6, tools)]:
        metas = {p.removesuffix('.meta.json').split('/')[-1] for p in inventory
                 if re.fullmatch(rf'content/{folder}/[a-z0-9-]+\.meta\.json', p)}
        bodies = {p.removesuffix('.body.html').split('/')[-1] for p in inventory
                  if re.fullmatch(rf'content/{folder}/[a-z0-9-]+\.body\.html', p)}
        if len(metas) != expected or bodies != metas:
            raise ValueError(f'{folder}: missing/duplicate source-body pair')
        target.update(metas)
    if tools != TOOLS or not articles.isdisjoint(tools):
        raise ValueError('41 distinct original content IDs not present')
    routes = set()
    for folder, names in [('articles', articles), ('tools', tools)]:
        for slug in sorted(names):
            path = preparedness / 'content' / folder / (slug+'.meta.json')
            if not path.is_file() or path.is_symlink():
                raise ValueError('untrusted meta file: '+slug)
            data = json.loads(path.read_text(encoding='utf-8'))
            if data.get('slug') != slug or data.get('status', {}).get('publish') != 'draft':
                raise ValueError('non-draft or wrong content identity: '+slug)
            section = data.get('section', '')
            if not re.fullmatch(r'[a-z0-9-]+', section):
                raise ValueError('invalid section: '+slug)
            route = '/preparedness/'+section+'/'+slug+'/'
            if route in routes:
                raise ValueError('duplicate canonical: '+route)
            routes.add(route)
    return {'articles': len(articles), 'tools': len(tools),
            'distinct_draft_canonicals': len(routes), 'published': 0}


def load_sibling(name: str):
    """Load pinned local tool modules without relying on sys.path under python -I."""
    path = Path(__file__).resolve().with_name(name + '.py')
    if not path.is_file() or path.is_symlink():
        raise ImportError('missing trusted sibling module: ' + name)
    spec = import_util.spec_from_file_location('_fv_preparedness_' + name, path)
    if spec is None or spec.loader is None:
        raise ImportError('invalid sibling module: ' + name)
    module = import_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def preflight(repo: Path, timeout: int = 300) -> dict:
    """Native execution in one temporary copy; no original files are changed."""
    packet = {'schema': SCHEMA, 'state': INVALID, 'checks': [],
              'publication_authorized': False, 'independent_qd_pass': False,
              'merchant_offer_verified': False, 'verified_paid_orders': None,
              'qualified_human_sessions': None, 'realized_net_revenue': None}
    try:
        native = load_sibling('r176_native_review_preflight')
        strict = load_sibling('r187_receipt_contract_gate')
        inventory, run_command, assess = native.inventory, native.run_command, native.assess
        if not (10 <= timeout <= 1200) or not repo.is_dir() or repo.is_symlink():
            raise ValueError('trusted repository or timeout unavailable')
        source = repo / 'preparedness'
        before = inventory(source)
        packet['census'] = check_census(source, before)
        packet['original_sha256'] = hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest()
        for _, file, *_ in GATES:
            if 'tools/'+file not in before:
                raise ValueError('missing mandated gate '+file)
        with tempfile.TemporaryDirectory(prefix='fv-prep-r186-') as temp:
            staged = Path(temp)
            shutil.copytree(source, staged/'preparedness',
                            ignore=shutil.ignore_patterns('build','__pycache__','*.pyc'),
                            symlinks=False)
            if inventory(staged/'preparedness') != before:
                raise ValueError('staged copy changed source identity')
            steps = (
                ('validate', ('preparedness/tools/validate.py',)),
                ('build', ('preparedness/tools/build.py',)),
                ('unit_tests', ('-m','unittest','discover','-s','preparedness/tests','-v')),
            )
            for label, argv in steps:
                run = run_command(label, argv, staged, timeout)
                packet['checks'].append(assess(run, staged))
            for label, file, *extra in GATES:
                argv = ('preparedness/tools/'+file, '--repo', '.', *extra)
                run = run_command(label, argv, staged, timeout)
                decision = verify_gate(label, run)
                if decision['status'] == 'STRUCTURAL_HOLD':
                    try:
                        strict.verify_contract(label, json.loads(run['stdout']))
                    except (ValueError, TypeError, KeyError) as exc:
                        decision['status'] = 'FAIL'
                        decision['reason'] = 'R187 receipt contract: ' + str(exc)[:170]
                packet['checks'].append(decision)
            if inventory(staged/'preparedness') != before:
                raise ValueError('a native command modified staged source inputs')
        if inventory(source) != before:
            raise ValueError('original checkout modified during execution')
        if len(packet['checks']) != 12:
            raise ValueError('missing mandatory pipeline stage')
        if all(row['status'] in ('CHECKED', 'STRUCTURAL_HOLD') for row in packet['checks']):
            packet['state'] = HOLD
        else:
            packet['blocker'] = 'one or more native or independent gates failed'
    except (OSError, ValueError, TypeError, KeyError, ImportError, json.JSONDecodeError) as exc:
        packet['blocker'] = str(exc)[:300]
    return packet


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path('.'))
    parser.add_argument('--timeout', type=int, default=300)
    args = parser.parse_args(argv)
    print(json.dumps(preflight(args.repo, args.timeout), sort_keys=True, indent=2))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
