#!/usr/bin/env python3
"""R320: deterministic, read-only adjudication docket for R319's 15 open conflicts.

No selection or rewrite of contributor content. A correct docket is STILL a hard hold;
qualified claim/safety/source review and authentic native exports remain separate gates.
"""
from __future__ import annotations
import argparse
import copy
import importlib.util
import json
from pathlib import Path

# Load the sibling, pinned custody validator by path: python -I script.py works
# without trusting a mutable PYTHONPATH or importing unrelated site packages.
_CUSTODY_FILE = Path(__file__).with_name('r319_three_way_custody_hold.py')
if _CUSTODY_FILE.is_symlink():
    raise RuntimeError('linked custody validator')
_spec = importlib.util.spec_from_file_location('fv_r319_custody', _CUSTODY_FILE)
if _spec is None or _spec.loader is None:
    raise RuntimeError('missing custody validator')
custody = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(custody)

SCHEMA = 'fv-preparedness-r320-conflict-adjudication-docket-v1'
SOURCE_MANIFEST_PATH = custody.MANIFEST_PATH
# Classification is conservative. A question is a review task, not a claim of safety.
REVIEW_MATRIX = {
 'articles/family-communication-plan.body.html': ('P0_PRIVACY', 'Compare emergency call/text instructions; preserve full narrative depth, visible sources and school-reunification privacy.'),
 'articles/family-communication-plan.meta.json': ('P0_CITATION', 'Verify related tool routes distinguish the plan builder from wallet card, with source-use IDs and editorial hold unchanged.'),
 'articles/home-fire-escape-plan.body.html': ('P0_LIFE_SAFETY', 'Qualified fire-safety reviewer must adjudicate home-power/drill wording and escape instructions before use.'),
 'articles/home-fire-escape-plan.meta.json': ('P0_CITATION', 'Retain author/source-use provenance and review status; verify no false approval or duplicate destination.'),
 'articles/homemade-water-filters.meta.json': ('P0_HEALTH_SAFETY', 'Qualified water-safety review needed; historical filter context must not imply potable output.'),
 'articles/making-water-safer.meta.json': ('P0_HEALTH_SAFETY', 'Preserve unresolved qualified review; do not infer independent QD PASS from founder chat approval.'),
 'articles/outage-heat-cold-generators.body.html': ('P0_LIFE_SAFETY', 'Qualified carbon-monoxide, generator, indoor heating and medical-device redline review required.'),
 'articles/outage-heat-cold-generators.meta.json': ('P0_CITATION', 'Check source-use changes and danger-warning linkage; maintain safety hold and canonical URL.'),
 'articles/salt-beef-salt-pork-age-of-sail.meta.json': ('P0_HEALTH_SAFETY', 'Keep historical food-preservation treatment distinct from modern food-safety approval.'),
 'articles/shelter-or-evacuate.body.html': ('P0_LIFE_SAFETY', 'Adjudicate evacuation direction, local official instructions, airborne hazards and shelter tradeoffs.'),
 'articles/shelter-or-evacuate.meta.json': ('P0_CITATION', 'Cross-check citation-to-claim mappings and correct related tool identity without silently replacing sources.'),
 'tools/power-outage-planner.body.html': ('P0_LIFE_SAFETY', 'Review generator/CO, medical devices, print and JavaScript-disabled behavior; preserve form fields.'),
 'tools/power-outage-planner.meta.json': ('P0_CITATION', 'Preserve tool taxonomy, canonical destination, safety status and exact source-use declarations.'),
 'tools/reunification-plan.body.html': ('P0_TOOL_IDENTITY', 'Do not replace the household plan-builder with the distinct family wallet card; verify form, print, privacy, JS fallback.'),
 'tools/reunification-plan.meta.json': ('P0_TOOL_IDENTITY', 'Contributor number 104 and card identity conflict with integrated plan builder number 102; retain separate tool 104 source.'),
}
RELEASE_HOLD = {'publication_authorized': False, 'qualified_safety_approved': False,
                'independent_qd_pass': False, 'paid_conversion_verified': False,
                'canonical_sources_modified': False, 'automatic_merge_permitted': False}


def _relative(path: str) -> str:
    prefix = 'preparedness/content/'
    return path[len(prefix):] if isinstance(path, str) and path.startswith(prefix) else ''


def source_refs(record: dict) -> dict:
    return {k: (None if record[k] is None else {'sha': record[k]['sha'], 'size': record[k]['size']})
            for k in ('integrated', 'continuation', 'followup')}


def build_docket(manifest: dict) -> dict:
    """Deterministic proposed human-review docket; never resolves disagreements."""
    if custody.validate_manifest(manifest)['errors']:
        raise ValueError('R319 SOURCE MANIFEST INVALID')
    conflicts = [r for r in manifest['records'] if r['disposition'] == 'HUMAN_REVIEW_REQUIRED']
    docket = []
    for rec in sorted(conflicts, key=lambda r: r['path']):
        short = _relative(rec['path'])
        if short not in REVIEW_MATRIX:
            raise ValueError('UNKNOWN CONFLICT - HUMAN TRIAGE REQUIRED: ' + short)
        severity, task = REVIEW_MATRIX[short]
        docket.append({'path': rec['path'], 'source_refs': source_refs(rec),
                       'severity': severity, 'review_task': task,
                       'status': 'UNRESOLVED_HOLD', 'claim_by_claim_verified': False,
                       'independent_reviewer_approved': False, 'automatic_selection': False})
    if len(docket) != 15 or len(REVIEW_MATRIX) != 15:
        raise ValueError('CONFLICT INVENTORY DRIFT')
    return {'schema': SCHEMA, 'r319_manifest_path': SOURCE_MANIFEST_PATH,
            'baseline': copy.deepcopy(custody.BASELINE), 'branches': copy.deepcopy(custody.BRANCHES),
            'review_required_count': 15, 'records': docket,
            'release': RELEASE_HOLD.copy()}


def validate_docket(manifest: object, docket: object) -> dict:
    errors: list[str] = []
    source_report = custody.validate_manifest(manifest)
    if source_report['errors']:
        errors.append('R319_SOURCE_MANIFEST_INVALID')
    if not isinstance(docket, dict):
        return {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD',
                'errors': ['INVALID_DOCKET'], 'review_required': 15,
                'independent_qd_pass': False, 'publishing_authorized': False}
    if set(docket) != {'schema', 'r319_manifest_path', 'baseline', 'branches', 'review_required_count', 'records', 'release'}:
        errors.append('DOCKET_SHAPE_DRIFT')
    if docket.get('schema') != SCHEMA: errors.append('DOCKET_SCHEMA_DRIFT')
    if docket.get('r319_manifest_path') != SOURCE_MANIFEST_PATH: errors.append('SOURCE_PATH_DRIFT')
    if docket.get('baseline') != custody.BASELINE: errors.append('BASELINE_REF_DRIFT')
    if docket.get('branches') != custody.BRANCHES: errors.append('CONTRIBUTOR_REFS_DRIFT')
    if type(docket.get('review_required_count')) is not int or docket.get('review_required_count') != 15:
        errors.append('REVIEW_COUNT_DRIFT')
    if docket.get('release') != RELEASE_HOLD: errors.append('FALSE_RELEASE_OR_SOURCE_CHANGE')
    rows = docket.get('records')
    if not isinstance(rows, list): rows = []; errors.append('MISSING_DOCKET_RECORDS')
    if len(rows) != 15: errors.append('REVIEW_ROW_COUNT_DRIFT')
    seen = set()
    source_map = {r.get('path'):r for r in manifest.get('records', []) if isinstance(r,dict) and isinstance(r.get('path'),str)} if isinstance(manifest,dict) and isinstance(manifest.get('records'),list) else {}
    expected = {r['path'] for r in source_map.values() if r.get('disposition')=='HUMAN_REVIEW_REQUIRED'}
    for i, row in enumerate(rows):
        if not isinstance(row, dict): errors.append(f'INVALID_REVIEW_ROW:{i}'); continue
        p = row.get('path')
        if not isinstance(p,str) or not custody.SOURCE_PATH.fullmatch(p):
            errors.append(f'INVALID_REVIEW_PATH:{i}'); continue
        if p in seen: errors.append('DUPLICATE_REVIEW_PATH:' + p)
        seen.add(p)
        if p not in expected: errors.append('UNAUTHORIZED_REVIEW_PATH:' + p)
        rel = _relative(p)
        spec = REVIEW_MATRIX.get(rel)
        if spec is None: errors.append('UNRECOGNIZED_HUMAN_CONFLICT:' + p)
        else:
            if row.get('severity') != spec[0]: errors.append('RISK_DOWNGRADED:' + p)
            if row.get('review_task') != spec[1]: errors.append('REVIEW_TASK_TAMPERED:' + p)
        required = {'path','source_refs','severity','review_task','status',
                    'claim_by_claim_verified','independent_reviewer_approved','automatic_selection'}
        if set(row) != required: errors.append('REVIEW_ROW_SHAPE_DRIFT:' + p)
        if row.get('status') != 'UNRESOLVED_HOLD': errors.append('FALSE_REVIEW_RESOLUTION:' + p)
        for flag in ('claim_by_claim_verified','independent_reviewer_approved','automatic_selection'):
            if row.get(flag) is not False: errors.append('FALSE_REVIEW_ATTESTATION:' + p + ':' + flag)
        if p in source_map:
            try:
                expected_refs = source_refs(source_map[p])
            except (KeyError, TypeError):
                errors.append('INVALID_AUTHENTIC_SOURCE_REF:' + p)
            else:
                if row.get('source_refs') != expected_refs: errors.append('SOURCE_REF_DRIFT:' + p)
    if seen != expected: errors.append('MISSING_OR_EXTRA_REVIEW_PATH')
    return {'schema': SCHEMA, 'state': 'INVALID_HARD_HOLD' if errors else 'DRAFT_HARD_HOLD',
            'errors': sorted(set(errors)), 'review_required': 15,
            'independent_qd_pass': False, 'publishing_authorized': False,
            'paid_conversion_verified': False}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--docket', type=Path, default=None)
    args = parser.parse_args()
    try:
        source = args.root / SOURCE_MANIFEST_PATH
        docket_path = args.docket or args.root / 'preparedness/audits/r320_conflict_adjudication_docket.json'
        if source.is_symlink() or docket_path.is_symlink(): raise ValueError('symlink input')
        manifest = json.loads(source.read_text(encoding='utf-8'))
        docket = json.loads(docket_path.read_text(encoding='utf-8'))
        report = validate_docket(manifest,docket)
        native = custody.validate_manifest(manifest,args.root)
        if native['errors']:
            report['errors'] = sorted(set(report['errors'] + ['AUTHENTIC_CHECKOUT_SOURCE_DRIFT']))
            report['state'] = 'INVALID_HARD_HOLD'
    except (OSError, ValueError, TypeError, UnicodeError):
        report = {'schema': SCHEMA,'state': 'INVALID_HARD_HOLD',
                  'errors': ['UNAVAILABLE_AUTHENTIC_SOURCE_OR_DOCKET'],
                  'publishing_authorized': False, 'independent_qd_pass': False}
    print(json.dumps(report,indent=2,sort_keys=True))
    return 2 if report['state']=='DRAFT_HARD_HOLD' else 1

if __name__ == '__main__': raise SystemExit(main())
