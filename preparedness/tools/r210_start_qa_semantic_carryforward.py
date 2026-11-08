#!/usr/bin/env python3
"""Read-only R210 reconciliation of PR #157 safety intent against later Start Here author text.

This tool does not merge QA PRs, attest source advice, or authorize release. It
requires exact Git blob identities; semantic anchors are regression tripwires,
NOT medical review. Issue #136; revenue coordination #820.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import importlib.util

# Load the sibling guard by absolute tool path: importlib-based tests do not
# necessarily place preparedness/tools on sys.path. Missing guard => fail closed.
_guard_path = Path(__file__).with_name('r211_path_guard.py')
_guard_spec = importlib.util.spec_from_file_location('fv_preparedness_r211_io_guard', _guard_path)
if _guard_spec is None or _guard_spec.loader is None:
    raise ImportError('required R211 I/O guard cannot be loaded')
io_guard = importlib.util.module_from_spec(_guard_spec)
_guard_spec.loader.exec_module(io_guard)

HOLD = 'DRAFT_HARD_HOLD'
INVALID = 'INVALID_HARD_HOLD'
SCHEMA = 'fv-preparedness-r210-start-qa-carryforward-v1'
FROZEN_START_HEAD = '2122d856fce9f64887c16df3d52e64be9f59a55b'
QA157_BASE = '10f58fed1ba808056813064ca5f9680589db8da1'
QA157_HEAD = '7d1ae6b8ef93d10cfb6810987672360885e9c1aa'
PINNED = {
 'preparedness/content/articles/household-emergency-plan.body.html': '8ca5c261dba56eeaf79c445332381a74867233de',
 'preparedness/content/articles/three-day-kit.body.html': 'ef5463ca668166766ca3d868908bc0bcb6040a23',
 'preparedness/sources/fragments/start.json': '29574c328cbab0548e6e5d4a026694857d56b6b4',
 'preparedness/taxonomy.json': 'eea601e53e16e36cd4fc890876bc249b39632370',
 'preparedness/tests/test_preparedness.py': 'dd1e7bc35cc83da6174c56464583cbbadfd6751f',
}
FOUR = ('household-emergency-plan', 'three-day-kit', 'go-bags', 'preparedness-real-households')
PLAN, KIT, SOURCES, TAXONOMY, TEST = tuple(PINNED)

class Violation(ValueError):
    pass

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()

def strict_json(data: bytes):
    def unique(pairs):
        obj = {}
        for k, v in pairs:
            if k in obj:
                raise Violation('duplicate JSON key: ' + k)
            obj[k] = v
        return obj
    def invalid_constant(s):
        raise Violation('invalid JSON constant: ' + s)
    try:
        return json.loads(data.decode('utf-8'), object_pairs_hook=unique, parse_constant=invalid_constant)
    except (ValueError, UnicodeError) as e:
        raise Violation('invalid UTF-8 or JSON: ' + str(e)) from e

def analyze(files: dict[str, bytes], *, expected_oids: dict[str, str] | None = None):
    """Quarantined structural preflight; expected_oids override is for tests only.

    None of the returned states means editorial approval. The production CLI
    cannot override the frozen SHA map.
    """
    expected = PINNED if expected_oids is None else expected_oids
    out = dict(schema=SCHEMA, issue=136, conversion_issue=820, state=INVALID,
        publication_authorized=False, independent_qd_pass=False,
        medically_safe=False, source_safety_verified=False,
        verified_paid_orders=None, realized_net_revenue=None,
        source_head=FROZEN_START_HEAD, qa157_head=QA157_HEAD,
        authenticated_files=[], review_dispositions=[], pending_qa=[], errors=[])
    try:
        def need(test, why):
            if not test:
                raise Violation(why)
        need(type(files) is dict and set(files) == set(PINNED), 'missing/extra authenticated Start Here files')
        need(type(expected) is dict and set(expected) == set(PINNED), 'incomplete SHA evidence')
        for path in PINNED:
            raw = files[path]
            need(type(raw) is bytes, 'file is not raw bytes: ' + path)
            sha = git_blob_sha(raw)
            need(type(expected[path]) is str and re.fullmatch(r'[0-9a-f]{40}', expected[path]) is not None, 'invalid expected SHA: ' + path)
            need(sha == expected[path], 'Git blob mismatch: ' + path)
            out['authenticated_files'].append(dict(path=path, blob_sha=sha, bytes=len(raw)))
        plan = files[PLAN].decode('utf-8')
        kit = files[KIT].decode('utf-8')
        test = files[TEST].decode('utf-8')
        lower_plan = plan.casefold()
        lower_kit = kit.casefold()
        # Safety-intent preservation is *necessary, never sufficient* for review.
        need('simulated-outage evening' in lower_plan, 'no simulated outage drill')
        need('do not switch off the main breaker' in lower_plan, 'main-breaker prohibition lost')
        for phrase in ('refrigerator', 'smoke and carbon monoxide alarms', 'medical or safety-critical equipment'):
            need(phrase in lower_plan, 'drill critical equipment caveat lost: ' + phrase)
        need('switch off the main power for an evening' not in lower_plan, 'unsafe previous outage drill returned')
        out['review_dispositions'].append(dict(pr=157, path=PLAN,
            disposition='NEWER_AUTHOR_INTENT_PRESENT_REQUIRES_HUMAN_REVIEW',
            qa_head_auto_apply=False, medical_safety_approval=False))
        for phrase in ('fema', 'december 2023', 'refrigerated medications',
                       'call your doctor or pharmacist', 'interim-use and replacement plan',
                       'start-fema-power-sheet', 'start-ready-power'):
            need(phrase in lower_kit, 'medicine qualified guidance / citation lost: ' + phrase)
        need('should discard refrigerated medication unless the label says otherwise' not in lower_kit,
             'older blanket medicine discard text returned')
        out['review_dispositions'].append(dict(pr=157, path=KIT,
            disposition='NEWER_AUTHOR_INTENT_PRESENT_REQUIRES_QUALIFIED_MEDICATION_REVIEW',
            qa_head_auto_apply=False, medical_safety_approval=False))
        sources = strict_json(files[SOURCES]); need(type(sources) is dict and type(sources.get('sources')) is list,
            'source fragment schema missing')
        hits = [s for s in sources['sources'] if type(s) is dict and s.get('id') == 'start-redcross-older-adults']
        need(len(hits) == 1, 'Red Cross citation missing/duplicated')
        need(hits[0].get('kind') == 'nonprofit', 'Red Cross misclassified as regulator')
        need('not a regulator' in hits[0].get('notes','').casefold(), 'Red Cross clarification absent')
        out['review_dispositions'].append(dict(pr=157, path=SOURCES,
            disposition='NONPROFIT_PROVENANCE_ALREADY_PRESENT_REQUIRES_SOURCE_REVIEW',
            qa_head_auto_apply=False))
        tax = strict_json(files[TAXONOMY]); need(type(tax) is dict and type(tax.get('slate')) is list,
            'taxonomy slate absent')
        need(len(tax['slate']) == 35, '35-article slate missing')
        slugs = [a.get('slug') for a in tax['slate'] if type(a) is dict]
        need(len(slugs) == 35 and len(set(slugs)) == 35, 'slate contains duplicate/invalid slugs')
        need(all(type(a) is dict and a.get('n') == n for n,a in enumerate(tax['slate'],1)),
             'slate article order/identity drift')
        for slug in FOUR:
            entries = [a for a in tax['slate'] if a['slug'] == slug]
            need(len(entries) == 1 and entries[0].get('gate') is True, 'Start Here safety gate lost: '+slug)
            need(entries[0].get('status') not in ('published','safety-approved','safety-approved-draft'),
                 'false public/safety approval in Start Here taxonomy: '+slug)
        out['review_dispositions'].append(dict(pr=157, path=TAXONOMY,
            disposition='FOUR_START_HERE_GATES_PRESENT_NO_PUBLICATION_AUTHORITY',
            qa_head_auto_apply=False))
        # The exact named PR #157 test is absent, but existing GovernanceRegressionTests
        # already contain negative publish-gate coverage. Semantic equivalence still
        # requires independent review. #169/#973 remain separate and unmerged.
        need('def test_fragment_may_upgrade_a_placeholder_but_not_a_verified_source' in test,
             'core source test missing')
        need('def test_register_fragments_cannot_duplicate_ids' in test,
             'core duplicate-source test missing')
        out['pending_qa'] = [
            dict(pr=157, path=TEST, issue='named QA test absent; existing negative governance coverage needs independent equivalence review',
                disposition='SEMANTIC_TEST_EQUIVALENCE_REVIEW_PENDING', auto_apply=False),
            dict(pr=169, path=TEST, issue='test source fixture writes into shared tree',
                disposition='ISOLATED_FIXTURE_REBASE_OUTSTANDING', auto_apply=False),
            dict(pr=973, path=TEST, issue='stacked final shared-tree fixture fix',
                disposition='KEEP_DEPENDENCY_ON_PR169', auto_apply=False),
        ]
        need('def test_start_articles_require_human_safety_review' not in test,
             'Start Here test changed without corresponding SHA review')
        out['review_dispositions'].append(dict(pr=157, path=TEST,
            disposition='REBASE_QUALIFIED_NEGATIVE_TEST_PENDING', qa_head_auto_apply=False))
        out['state'] = HOLD
    except (Violation, UnicodeError, TypeError, KeyError, AttributeError, IndexError, ValueError) as e:
        out['errors'].append(str(e))
    return out

def read_checkout(root: Path) -> dict[str,bytes]:
    """Read through R211 descriptor-based, no-symlink source custody."""
    try:
        return io_guard.read_files(root, PINNED)
    except io_guard.GuardViolation as exc:
        raise Violation(str(exc)) from exc

def main(argv=None):
    p=argparse.ArgumentParser(description='R210 fail-closed Start Here QA carry-forward preflight')
    p.add_argument('--checkout', required=True, type=Path,
                   help='Trusted checkout at frozen Claude Start Here SHA (not the older PR base)')
    p.add_argument('--report', type=Path, help='Local output only; never a production approval')
    args=p.parse_args(argv)
    try:
        result=analyze(read_checkout(args.checkout))
    except (ValueError, OSError) as e:
        result=dict(schema=SCHEMA, issue=136, state=INVALID,
            publication_authorized=False, independent_qd_pass=False,
            medically_safe=False, verified_paid_orders=None,
            realized_net_revenue=None, errors=[str(e)])
    if args.report:
        try:
            io_guard.write_new_report(args.report, args.checkout,
                                      json.dumps(result, indent=2, sort_keys=True) + '\n')
        except (io_guard.GuardViolation, OSError) as exc:
            result['state'] = INVALID
            result.setdefault('errors', []).append('report not written: ' + str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if result['state']==HOLD else 3

if __name__=='__main__':
    raise SystemExit(main())
