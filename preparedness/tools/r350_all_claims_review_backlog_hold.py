#!/usr/bin/env python3
"""R350: deterministic review backlog for every authored Preparedness citation.

Read-only; converts R349's private, digest-only citation registry into a complete
reviewer work queue. A populated proposal is *not* a verified source, safety pass,
commerce approval, publication permission or a substitute for qualified review.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha1, sha256
from pathlib import Path
from urllib.parse import urlsplit
from ipaddress import ip_address
import argparse
import importlib.util
import json
import re

SCHEMA = 'fv-preparedness-r350-full-citation-review-backlog-v1'
PREDECESSOR_GIT_BLOB = '75be8aeed9863d2a2ec0fec88f8774bda3e7f7e5'
HEX64 = re.compile(r'^[0-9a-f]{64}$')
DOC = re.compile(r'^(articles|tools)/[a-z0-9]+(?:-[a-z0-9]+)*$')
SID = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
ALLOWED_PROPOSALS = frozenset(('needs_source_check', 'needs_claim_revision',
                               'pending_specialist_review'))
HARD_HOLD = {'may_merge': False, 'may_publish': False, 'may_send_social': False,
             'may_update_cms': False, 'qualified_qd_pass': False,
             'independent_claim_support_verified': False,
             'human_link_check_verified': False, 'safety_review_approved': False,
             'paid_offer_verified': False, 'settled_order_verified': False,
             'net_revenue_verified': False}


def sha(text: str) -> str:
    return sha256(text.encode('utf-8')).hexdigest()


def git_blob(contents: bytes) -> str:
    return sha1(b'blob ' + str(len(contents)).encode() + b'\x00' + contents).hexdigest()


def ticket_id(row: dict) -> str:
    """Bind one original citation occurrence and its registered source identity."""
    return sha('|'.join((str(row[k]) for k in ('document', 'source_id', 'ordinal',
                 'occurrence_sha256', 'region_sha256', 'source_identity_sha256',
                 'url_sha256', 'metadata_source_use_sha256'))))


def safe_review_url(url: object) -> bool:
    """Only public HTTPS review references; never fetch or imply corroboration."""
    if not isinstance(url, str) or not 10 <= len(url) <= 2048:
        return False
    if any(ord(c) < 33 or ord(c) == 127 for c in url):
        return False
    try:
        parsed = urlsplit(url)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
            return False
        if parsed.port not in (None, 443) or parsed.query or parsed.fragment:
            return False
        host = parsed.hostname.lower().rstrip('.')
        if host in ('localhost', 'localhost.localdomain') or host.endswith('.local') or host.endswith('.internal'):
            return False
        if '.' not in host or not re.fullmatch(r'[a-z0-9.-]+', host):
            return False
        try:
            ip_address(host)
            return False
        except ValueError:
            pass
        if any(not label or label.startswith('-') or label.endswith('-') for label in host.split('.')):
            return False
        return True
    except ValueError:
        return False


def compile_backlog(crosswalk: object, proposals: object = None) -> dict:
    """Pure function. No source text, URLs, reviewer notes or sensitive forms exported."""
    errors = []
    crosswalk = crosswalk if isinstance(crosswalk, dict) else {}
    upstream = crosswalk.get('errors')
    if not isinstance(upstream, list) or not all(isinstance(e, str) for e in upstream):
        errors.append('INVALID_UPSTREAM_ERRORS_FIELD')
        upstream = []
    if upstream:
        errors.append('UPSTREAM_CROSSWALK_BLOCKED')
    if crosswalk.get('schema') != 'fv-preparedness-r349-41-document-citation-registry-join-v1':
        errors.append('WRONG_R349_SCHEMA')
    if crosswalk.get('status') != 'DRAFT_CROSSWALK_ONLY_HARD_HOLD':
        errors.append('R349_NOT_IN_DRAFT_HARD_HOLD_STATE')
    if crosswalk.get('documents_inspected') != 41 or not isinstance(crosswalk.get('documents_inspected'), int):
        errors.append('FULL_41_DOCUMENT_CUSTODY_NOT_ESTABLISHED')
    if crosswalk.get('may_publish') is not False or crosswalk.get('qualified_qd_pass') is not False:
        errors.append('UPSTREAM_RELEASE_FLAG_INCONSISTENCY')
    citations = crosswalk.get('all_citations')
    if not isinstance(citations, list):
        citations = []
        errors.append('INVALID_UPSTREAM_CITATIONS')
    if crosswalk.get('occurrences_count') != len(citations):
        errors.append('UPSTREAM_OCCURRENCE_COUNT_MISMATCH')
    submissions = [] if proposals is None else proposals
    if not isinstance(submissions, list):
        submissions = []
        errors.append('INVALID_PROPOSALS_TYPE')
    review_by_ticket: dict[str, dict] = {}
    for submission in submissions:
        if not isinstance(submission, dict) or not isinstance(submission.get('ticket_id'), str):
            errors.append('INVALID_REVIEW_PROPOSAL')
            continue
        key = submission['ticket_id']
        if key in review_by_ticket:
            errors.append('DUPLICATE_REVIEW_TICKET')
        review_by_ticket[key] = submission
        if set(submission) - {'ticket_id', 'disposition', 'evidence_url', 'reviewer_note'}:
            errors.append('UNRECOGNIZED_REVIEW_OR_APPROVAL_FIELD')
        if submission.get('disposition') not in ALLOWED_PROPOSALS:
            errors.append('UNSUPPORTED_REVIEW_DECISION_OR_FALSE_APPROVAL')
        if 'evidence_url' in submission and not safe_review_url(submission['evidence_url']):
            errors.append('UNSAFE_OR_UNTRUSTED_REVIEW_URL')
        if 'reviewer_note' in submission and (not isinstance(submission['reviewer_note'], str) or
                                              len(submission['reviewer_note']) > 2000):
            errors.append('INVALID_PRIVATE_REVIEW_NOTE')
    rows, found, documents, by_source = [], set(), Counter(), Counter()
    for row in citations:
        if not isinstance(row, dict) or not DOC.fullmatch(str(row.get('document', ''))) or not SID.fullmatch(str(row.get('source_id', ''))):
            errors.append('MALFORMED_CITATION_IDENTITY')
            continue
        if type(row.get('ordinal')) is not int or row['ordinal'] <= 0:
            errors.append('INVALID_CITATION_ORDINAL')
            continue
        digests = ('occurrence_sha256', 'region_sha256', 'source_identity_sha256',
                   'url_sha256', 'metadata_source_use_sha256')
        if any(not isinstance(row.get(field), str) or not HEX64.fullmatch(row[field]) for field in digests):
            errors.append('MISSING_OR_INVALID_SOURCE_CLAIM_CUSTODY')
            continue
        key = ticket_id(row)
        if key in found:
            errors.append('DUPLICATE_SOURCE_CLAIM_TICKET')
            continue
        found.add(key)
        documents[row['document']] += 1
        by_source[row['source_id']] += 1
        submission = review_by_ticket.get(key)
        rows.append({'ticket_id': key, 'document': row['document'],
                     'source_id': row['source_id'], 'ordinal': row['ordinal'],
                     'claim_region_sha256': row['region_sha256'],
                     'source_identity_sha256': row['source_identity_sha256'],
                     'evidence_url_sha256': row['url_sha256'],
                     'status': 'UNREVIEWED' if submission is None else 'PROPOSAL_RECEIVED_NOT_APPROVED',
                     'proposed_disposition': submission.get('disposition') if submission else None,
                     'review_note_sha256': sha(submission['reviewer_note']) if submission and isinstance(submission.get('reviewer_note'), str) else None,
                     'requires_independent_qualified_review': True})
    if set(review_by_ticket) - found:
        errors.append('STALE_OR_UNKNOWN_REVIEW_TICKET')
    rows.sort(key=lambda r: (r['document'], r['ordinal'], r['ticket_id']))
    summary = {'schema': SCHEMA,
               'status': 'INVALID_HARD_HOLD' if errors else 'PRIVATE_REVIEW_BACKLOG_HARD_HOLD',
               'errors': sorted(set(errors)), 'upstream_error_codes': sorted(set(upstream)),
               'documents_inspected': crosswalk.get('documents_inspected'),
               'tickets': rows, 'ticket_count': len(rows),
               'unreviewed_count': sum(r['status'] == 'UNREVIEWED' for r in rows),
               'proposals_received_count': sum(r['status'] == 'PROPOSAL_RECEIVED_NOT_APPROVED' for r in rows),
               'citation_counts_by_document': dict(sorted(documents.items())),
               'citation_counts_by_source': dict(sorted(by_source.items())),
               'original_private_claims_exported': False,
               'private_urls_exported': False,
               'review_proposals_are_not_adjudication': True,
               'qualified_review_remains_required': True}
    return {**summary, **HARD_HOLD}


def native_audit(root: Path, proposals: object = None) -> dict:
    """Refuse incomplete or altered predecessor. No CMS/build/social writes."""
    prep = root / 'preparedness' if (root / 'preparedness').is_dir() else root
    target = prep / 'tools' / 'r349_full_corpus_citation_registry_hold.py'
    if target.is_symlink() or not target.is_file():
        return compile_backlog({}, proposals)
    try:
        if git_blob(target.read_bytes()) != PREDECESSOR_GIT_BLOB:
            result = compile_backlog({}, proposals)
            result['errors'].append('R349_PINNED_GIT_BLOB_MISMATCH')
            result['errors'].sort()
            return result
        spec = importlib.util.spec_from_file_location('r349_full_corpus_citation_registry_hold', target)
        if spec is None or spec.loader is None:
            raise ImportError('R349 import spec unavailable')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return compile_backlog(module.audit_native(root), proposals)
    except (ImportError, ValueError, OSError, TypeError, KeyError, AttributeError):
        result = compile_backlog({}, proposals)
        result['errors'].append('R349_NATIVE_AUDIT_UNAVAILABLE')
        result['errors'].sort()
        return result


def main() -> int:
    cli = argparse.ArgumentParser(description='All 41 Preparedness source claims: private reviewer backlog, always HOLD')
    cli.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    cli.add_argument('--proposals', type=Path, help='optional private, local reviewer notes JSON; never published')
    opts = cli.parse_args()
    try:
        proposals = json.loads(opts.proposals.read_text('utf-8')) if opts.proposals else None
        result = native_audit(opts.repo_root, proposals)
    except (OSError, ValueError, UnicodeError):
        result = compile_backlog({})
        result['errors'].append('UNREADABLE_REVIEW_PROPOSALS')
    print(json.dumps(result, sort_keys=True, indent=2))
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
