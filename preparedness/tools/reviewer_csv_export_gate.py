#!/usr/bin/env python3
"""R37: private, deterministic, spreadsheet-safe HUMAN REVIEW export custody.

Transforms the *unreviewed* R35/R36 source/citation packets into usable CSV
review work queues. Raw originals remain in the upstream fingerprint-bound JSON;
CSV is an escaped presentation, not a change to the historical source record.
Never reads networks, accepts human approvals, writes CMS data, or publishes.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
import hashlib
import io
import json
import re

EXPECTED = (35, 1, 1959, 367, 43, 30)
HOLD_FLAGS = ('may_publish', 'independent_QD_approval', 'qualified_safety_clearance',
              'human_source_reviews_completed', 'source_claim_accuracy_verified')
HEX = re.compile(r'[a-f0-9]{64}\Z')
AUTHORITY = 'PRIVATE_CSV_HUMAN_REVIEW_WORKSHEETS_NOT_APPROVAL'
# Spreadsheet programs often interpret a leading =,+,-,@ as a formula, even
# if the source string originated in a quotation. Escape before CSV quoting.
_FORMULA = re.compile(r'^[\s\ufeff\u200b]*[=+\-@]', re.UNICODE)

class ExportHold(ValueError):
    """Missing, altered, approved or ambiguous human-review evidence."""

def need(ok, message):
    if not ok:
        raise ExportHold(message)

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')

def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()

def _hex(v):
    return type(v) is str and HEX.fullmatch(v) is not None

def _frozen(doc, authority):
    need(type(doc) is dict and doc.get('schema_version') == 1 and
         doc.get('issue') == 136 and doc.get('release_state') == 'HOLD' and
         doc.get('machine_authority') == authority, 'review packet is not frozen HOLD')
    for f in HOLD_FLAGS:
        need(doc.get(f) is False, 'review packet contains forged approval: '+f)
    fp = doc.get('fingerprint_sha256')
    need(_hex(fp) and sha({k:v for k,v in doc.items() if k != 'fingerprint_sha256'}) == fp,
         'review packet fingerprint mismatch')
    return fp

def _safe_cell(v):
    """Lossless, reversible CSV cell presentation; neutralize spreadsheet formulas.

    Newline/tab and backslash escapes prevent multi-line formula smuggling while
    preserving original text in the upstream source packet. None stays blank.
    Unescape after import only by a program treating cells as *data*, never eval.
    """
    if v is None:
        return ''
    if type(v) is bool:
        v = 'true' if v else 'false'
    elif type(v) in (dict, list, tuple):
        v = canonical(v).decode('utf-8')
    elif type(v) is not str:
        v = str(v)
    v = v.replace('\\', '\\\\').replace('\r', '\\r').replace('\n', '\\n').replace('\t', '\\t')
    if _FORMULA.match(v):
        v = "'" + v
    return v

def _render(header, rows):
    need(type(header) is tuple and header and len(set(header)) == len(header),
         'ambiguous CSV columns')
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, dialect='excel', lineterminator='\r\n')
    writer.writerow(header)
    for row in rows:
        need(type(row) is dict and set(row) == set(header),
             'CSV export row has missing or unaccounted evidence fields')
        writer.writerow([_safe_cell(row[key]) for key in header])
    content = stream.getvalue()
    # Round-trip CSV parse, cardinality and shape. No external I/O.
    parsed = list(csv.reader(io.StringIO(content, newline='')))
    need(parsed[0] == list(header) and len(parsed) == len(rows) + 1 and
         all(len(r) == len(header) for r in parsed), 'CSV round-trip lost review data')
    return content

CLAIM = ('claim_case_sha256', 'relationship_sha256', 'slug', 'source_id',
         'source_url', 'original_codepoint_offset', 'triage_priority_not_verdict',
         'triage_tags_not_safety_findings', 'exact_original_context',
         'review_state', 'human_source_access_date', 'human_exact_page_locator',
         'human_claim_support_assessment', 'human_scope_risk_notes',
         'human_qualified_safety_check')
SCOPE = ('source_case_sha256', 'relationship_sha256', 'slug', 'source_id',
         'article_origin', 'original_source_origin', 'source_url',
         'full_original_source_record_json', 'full_original_article_source_use',
         'source_record_sha256', 'source_use_sha256', 'impacted_claims',
         'review_state', 'human_access_date', 'human_reading_scope_check',
         'human_publisher_authority_check', 'human_discrepancy_notes')
FALLBACK = ('fallback_case_sha256', 'relationship_sha256', 'article_origin',
            'original_source_origin', 'source_url', 'review_state',
            'human_reading_scope_match', 'human_provenance_exception_notes')
GROUP = ('global_group_case_sha256', 'source_url', 'original_crosswalk_sha256',
         'full_original_crosswalk_group_json', 'distinct_original_variants_json',
         'used_in_any_citation', 'cited_relationship_ids_json', 'cited_claim_case_ids_json',
         'review_state', 'human_url_and_scope_reconciliation', 'human_source_conflict_notes',
         'human_independent_safety_assessment')

TABLES = {'claim_review.csv': CLAIM, 'source_scope_review.csv': SCOPE,
          'fallback_scope_review.csv': FALLBACK, 'global_shared_url_review.csv': GROUP}

