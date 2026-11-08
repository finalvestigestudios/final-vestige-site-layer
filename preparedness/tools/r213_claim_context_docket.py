#!/usr/bin/env python3
"""R213: deterministic, read-only human review docket for held source citations.

This is NOT a source adjudicator. It imports R212's authenticated six-file
custody check, never changes source text, and has no publication/PASS state.
Only use native CLI with the frozen Start Here contributor checkout.
"""
from __future__ import annotations
import argparse
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re

SCHEMA = 'fv-preparedness-r213-held-claim-context-v1'
INVALID = 'INVALID_HARD_HOLD'
HOLD = 'DRAFT_HARD_HOLD'


def _r212():
    path = Path(__file__).with_name('r212_citation_exception_receipts.py')
    spec = importlib.util.spec_from_file_location('fv_r212_custody_from_r213', path)
    if spec is None or spec.loader is None:
        raise ValueError('missing R212 custody gate')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _clean_context(raw: str) -> str:
    """Conservative non-executable preview of original source claim context."""
    # Frozen trusted originals contain HTML; always serialize this as JSON text.
    raw = re.sub(r'<[^>]*>', ' ', raw)
    raw = html.unescape(raw)
    return ' '.join(raw.split())


def _invalid(message: str) -> dict:
    return {'schema': SCHEMA, 'state': INVALID, 'errors': [message],
            'publication_authorized': False, 'independent_qd_pass': False,
            'medically_safe': False, 'review_complete': False, 'claims': []}


def evaluate(raw: dict[str, bytes], *, synthetic_pins=None) -> dict:
    """Enforce R212 custody before exposing source-bound review snippets.

    The synthetic_pins test seam is never exposed by main() or CLI.
    Even successful synthetic checks remain HARD HOLD.
    """
    try:
        r212 = _r212()
        custody = r212.evaluate(raw, expected=synthetic_pins)
        if custody.get('state') != r212.HOLD:
            return _invalid('R212 source custody failed: ' + '; '.join(custody.get('errors', [])))
        records = custody['held_occurrences']
        if len(records) != 3 or [rec['article'] for rec in records] != [7, 7, 20]:
            return _invalid('R212 receipt count/order mismatch')
        bodies = {7: raw[r212.A7+'.body.html'], 20: raw[r212.A20+'.body.html']}
        claims = []
        receipts = set()
        for rec in records:
            article = rec['article']
            body = bodies[article]
            start, end = rec['byte_span']
            if (type(start) is not int or type(end) is not int or
                    not 0 <= start < end <= len(body)):
                return _invalid('invalid receipt byte span')
            expected_marker = ('{{cite:'+rec['source_id']+'}}').encode('ascii')
            if body[start:end] != expected_marker:
                return _invalid('citation marker at receipt byte span does not match')
            receipt_id = rec['receipt_sha256']
            if receipt_id in receipts or not re.fullmatch(r'[0-9a-f]{64}', receipt_id):
                return _invalid('duplicate or malformed review receipt')
            receipts.add(receipt_id)
            # Keep a compact but substantive original context, with exact byte
            # boundaries and a separate SHA-256 for the displayed excerpt.
            left = max(0, start - 320)
            right = min(len(body), end + 320)
            snippet_raw = body[left:right].decode('utf-8', errors='replace')
            snippet = _clean_context(snippet_raw)
            if not snippet or len(snippet) < 24:
                return _invalid('empty claim context')
            claims.append({
                'article': article,
                'citation_occurrence': rec['occurrence'],
                'source_id': rec['source_id'],
                'source_url': rec['source_url'],
                'body_git_blob_sha1': rec['body_sha'],
                'source_start_byte': start,
                'source_end_byte': end,
                'receipt_sha256': receipt_id,
                'context_excerpt': snippet,
                'context_excerpt_sha256': hashlib.sha256(snippet.encode('utf-8')).hexdigest(),
                'review_action': 'HUMAN_SOURCE_CLAIM_ADJUDICATION_REQUIRED',
                'editorial_decision': 'PENDING',
                'source_link_verified_by_human': False,
            })
        return {'schema': SCHEMA, 'source_head': r212.FROZEN_HEAD,
                'state': HOLD, 'errors': [], 'claims': claims,
                'review_complete': False, 'publication_authorized': False,
                'independent_qd_pass': False, 'medically_safe': False,
                'conversion_issue': 820, 'issue': 136,
                'notes': ('This docket preserves original claims for human source review; '
                          'even zero structural errors never grant safety, QD or publication approval.')}
    except (KeyError, TypeError, ValueError, UnicodeError, AttributeError, IndexError, OSError) as exc:
        return _invalid('R213 unable to prepare review context: ' + str(exc))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Preparedness R213 read-only source-claim docket (always HOLD)')
    parser.add_argument('--checkout', required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        r212 = _r212()
        result = evaluate(r212.read_checkout(args.checkout))
    except (OSError, ValueError, ImportError) as exc:
        result = _invalid('read-only source checkout failed: ' + str(exc))
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))
    return 2 if result['state'] == HOLD else 3


if __name__ == '__main__':
    raise SystemExit(main())
