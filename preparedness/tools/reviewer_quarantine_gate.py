#!/usr/bin/env python3
"""R38: fail-closed, read-only quarantine of *untrusted* edited review worksheets.

Spreadsheet annotations are not source visits, authenticated reviewer decisions,
qualified safety findings, QD approval or permission to publish.  This module
compares every imported worksheet cell to an exact SHA-256-bound R37 baseline;
only constrained, clearly unverified progress notes may enter the quarantine.
No network, filesystem, CMS or publication side effects.
"""
from __future__ import annotations

import csv
from datetime import date
import hashlib
import io
import json
import re
import importlib.util
from pathlib import Path

# The mandatory pipeline uses \`python -I\`: do not trust sys.path to resolve
# a like-named external package. Load the exact, non-linked R37 sibling.
_r37_path = Path(__file__).with_name('reviewer_csv_export_gate.py')
if not _r37_path.is_file() or _r37_path.is_symlink():
    raise ValueError('missing or linked frozen R37 private exporter')
_r37_spec = importlib.util.spec_from_file_location('preparedness_r38_exact_r37', _r37_path)
if _r37_spec is None or _r37_spec.loader is None:
    raise ValueError('cannot load exact R37 private exporter')
_r37 = importlib.util.module_from_spec(_r37_spec)
_r37_spec.loader.exec_module(_r37)
TABLES, HOLD_FLAGS, AUTHORITY = _r37.TABLES, _r37.HOLD_FLAGS, _r37.AUTHORITY
canonical, sha = _r37.canonical, _r37.sha

QUARANTINE_AUTHORITY = 'UNAUTHENTICATED_REVIEW_NOTES_QUARANTINE_NOT_APPROVAL'
STATES = frozenset(('NOT_STARTED', 'IN_PROGRESS', 'FLAGGED_FOR_FACT_CHECK',
                    'ESCALATE_TO_QUALIFIED_REVIEW'))
TABLE_COUNTS = {'claim_review.csv':'claim_reviews',
                'source_scope_review.csv':'source_scope_reviews',
                'fallback_scope_review.csv':'fallback_reviews',
                'global_shared_url_review.csv':'global_shared_url_reviews'}
KEYS = {name: columns[0] for name, columns in TABLES.items()}
HEX64 = re.compile(r'[a-f0-9]{64}\Z')
ISO_DATE = re.compile(r'\d{4}-\d{2}-\d{2}\Z')
FORMULA = re.compile(r'^[\s\ufeff\u200b\u200c\u200d\u2060]*[=+\-@]', re.UNICODE)
BIDI = re.compile('[\u202a-\u202e\u2066-\u2069]')
MAX_NOTE = 2048
MAX_TOTAL_EXTRA = 5000000

class IntakeHold(ValueError):
    """Human CSV import cannot be safely reconciled to original evidence."""

def need(condition, why):
    if not condition:
        raise IntakeHold(why)

def hash_text(body):
    return hashlib.sha256(body.encode('utf-8', errors='strict')).hexdigest()

def validated_manifest(bundle):
    need(type(bundle) is dict and set(bundle) == {'manifest', 'csv_tables'},
         'R37 baseline package shape altered')
    manifest = bundle['manifest']
    need(type(manifest) is dict and manifest.get('schema_version') == 1 and
         manifest.get('issue') == 136 and manifest.get('release_state') == 'HOLD' and
         manifest.get('machine_authority') == AUTHORITY,
         'baseline is not an R37 private HOLD export')
    for flag in HOLD_FLAGS:
        need(manifest.get(flag) is False, 'baseline claims approval: '+flag)
    for parent in ('parent_R34_original_reading_sha256',
                   'parent_R35_fingerprint_sha256',
                   'parent_R36_fingerprint_sha256'):
        need(type(manifest.get(parent)) is str and HEX64.fullmatch(manifest[parent]),
             'missing original contributor/source lineage '+parent)
    fp = manifest.get('fingerprint_sha256')
    need(type(fp) is str and HEX64.fullmatch(fp) and
         sha({k:v for k,v in manifest.items() if k != 'fingerprint_sha256'}) == fp,
         'R37 manifest fingerprint differs from the trusted export')
    meta = manifest.get('csv_tables')
    counts = manifest.get('counts')
    need(type(meta) is dict and set(meta) == set(TABLES) and
         type(counts) is dict and set(TABLE_COUNTS.values()).issubset(counts),
         'R37 worksheet census missing or extra')
    need(all(type(counts[k]) is int and counts[k] >= 0 for k in TABLE_COUNTS.values()),
         'invalid source and citation census')
    need(type(bundle['csv_tables']) is dict and set(bundle['csv_tables']) == set(TABLES),
         'baseline table was added or removed')
    return manifest

def parse_table(body, name, *, limit):
    need(type(body) is str, 'worksheet is not a Unicode string: '+name)
    try:
        size = len(body.encode('utf-8', errors='strict'))
    except UnicodeError as exc:
        raise IntakeHold('invalid Unicode worksheet') from exc
    need(size <= limit and '\x00' not in body and not body.startswith('\ufeff'),
         'worksheet exceeds size limit or contains NUL/BOM: '+name)
    try:
        parsed = csv.reader(io.StringIO(body, newline=''), dialect='excel', strict=True)
        header = next(parsed)
        need(header == list(TABLES[name]), 'worksheet headers altered/duplicated: '+name)
        identity = KEYS[name]
        found = {}
        for row in parsed:
            need(len(row) == len(header), 'worksheet cells/columns missing or extra: '+name)
            item = dict(zip(header,row))
            key = item[identity]
            need(bool(HEX64.fullmatch(key)) and key not in found,
                 'worksheet case ID invalid or duplicate: '+name)
            found[key] = item
        return found, size
    except (csv.Error, StopIteration, UnicodeError, OverflowError) as exc:
        raise IntakeHold('malformed CSV worksheet: '+name) from exc

def check_note(value, field):
    need(type(value) is str and len(value) <= MAX_NOTE and
         not any(ord(ch) < 32 or ord(ch) == 127 for ch in value) and
         BIDI.search(value) is None and FORMULA.match(value) is None,
         'untrusted note is too long, a formula, or contains controls: '+field)
    if field in ('human_source_access_date', 'human_access_date') and value:
        need(bool(ISO_DATE.fullmatch(value)), 'invalid reviewer observation date')
        try:
            date.fromisoformat(value)
        except ValueError as exc:
            raise IntakeHold('impossible reviewer observation date') from exc

def quarantine_reviewer_csv(bundle, edited_csv_tables):
    """Return frozen, evidence-bound *quarantine* annotations, never approvals.

    \`bundle\` is the original R37 export. The 4 edited CSVs may be reordered by
    spreadsheet software but must contain exactly the same rows and every
    original evidence cell byte-for-byte. Only review_state and human_* cells
    may differ. States are deliberately nonterminal; purported approvals are
    rejected, and safety-assessment cells are never accepted from CSV.
    """
    manifest = validated_manifest(bundle)
    need(type(edited_csv_tables) is dict and set(edited_csv_tables) == set(TABLES),
         'edited worksheets must contain exactly the four original tables')
    annotations, input_digests, row_count = [], {}, {}
    for name, columns in TABLES.items():
        old = bundle['csv_tables'][name]
        meta = manifest['csv_tables'][name]
        need(type(meta) is dict and type(old) is str and
             meta.get('columns') == list(columns) and
             type(meta.get('rows')) is int and meta['rows'] >= 0 and
             meta.get('sha256_utf8') == hash_text(old) and
             meta.get('bytes_utf8') == len(old.encode('utf-8')) and
             meta['rows'] == manifest['counts'][TABLE_COUNTS[name]],
             'original worksheet disagrees with its SHA-256 census: '+name)
        baseline, _ = parse_table(old, name, limit=meta['bytes_utf8'])
        need(len(baseline) == meta['rows'], 'original review cases lost: '+name)
        edited = edited_csv_tables[name]
        incoming, size = parse_table(edited, name,
                                      limit=meta['bytes_utf8'] + MAX_TOTAL_EXTRA)
        need(set(incoming) == set(baseline),
             'review import omitted, inserted or changed a source/claim case: '+name)
        input_digests[name] = {'sha256_utf8':hash_text(edited), 'bytes_utf8':size,
                               'rows':len(incoming)}
        row_count[name] = len(incoming)
        immutable = set(columns) - {'review_state'} - {
            field for field in columns if field.startswith('human_')}
        for case_id in sorted(baseline):
            original = baseline[case_id]
            submitted = incoming[case_id]
            need(all(original[k] == submitted[k] for k in immutable),
                 'historical evidence, source URL or citation context was edited: '+name)
            state = submitted['review_state']
            need(state in STATES, 'untrusted spreadsheet tried terminal review state: '+name)
            notes = {}
            for key in columns:
                if not key.startswith('human_'):
                    continue
                value = submitted[key]
                check_note(value, key)
                if 'safety_check' in key or 'safety_assessment' in key:
                    need(value == '', 'CSV cannot certify emergency or medical safety')
                if value:
                    notes[key] = value
            need((state == 'NOT_STARTED') == (not notes),
                 'review progress without an observation, or notes without progress')
            if state != 'NOT_STARTED':
                annotations.append({'table':name, 'case_id':case_id,
                    'submitted_progress_unverified':state,
                    'untrusted_human_notes':notes,
                    'original_evidence_row_sha256':sha(original),
                    'submitted_row_sha256':sha(submitted)})
    output = {'schema_version':1, 'issue':136, 'release_state':'HOLD',
        'machine_authority':QUARANTINE_AUTHORITY,
        'parent_R37_fingerprint_sha256':manifest['fingerprint_sha256'],
        'parent_R34_original_reading_sha256':manifest['parent_R34_original_reading_sha256'],
        'parent_R35_fingerprint_sha256':manifest['parent_R35_fingerprint_sha256'],
        'parent_R36_fingerprint_sha256':manifest['parent_R36_fingerprint_sha256'],
        'input_csv_tables':input_digests,
        'unchanged_original_case_counts':row_count,
        'unverified_progress_records':len(annotations),
        'no_authenticated_human_reviews_or_qualified_safety_findings':True,
        **{flag:False for flag in HOLD_FLAGS},
        'limitations':'Quarantined notes are untrusted, anonymous and not source checks. '
            'No completed, verified, safe, QD-PASS or publication state can be imported.'}
    output['fingerprint_sha256'] = sha(output)
    return {'manifest':output, 'quarantine_annotations':annotations}
