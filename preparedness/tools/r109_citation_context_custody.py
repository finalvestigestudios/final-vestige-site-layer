#!/usr/bin/env python3
"""R109 private, read-only changed-claim-neighborhood review gate.

Git identity and preserved citation counts cannot establish claim support. This
report flags changed text surrounding the *same* citation marker and citations
hidden in attributes, comments or scripting. No article body is exported.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

SCHEMA = 'r109-citation-neighborhood-custody-HOLD-v1'
TOKEN = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
TOKEN_INTENT = re.compile(r'\{\{cite:')
SPACE = re.compile(r'\s+')
CONTEXT_TAGS = frozenset('p li td th dt dd blockquote figcaption summary h1 h2 h3 h4 h5 h6'.split())
SUPPRESSED_TAGS = frozenset('script style template noscript svg math'.split())
VOID_TAGS = frozenset('area base br col embed hr img input link meta param source track wbr'.split())
SAFETY_CLASSES = frozenset('pa-act pa-tag--unc pa-warning pa-alert pa-caution pa-safety'.split())
MAX_BYTES = 2_000_000
MAX_CONTEXTS = 50_000
MAX_TOKENS = 20_000


class Hold(ValueError):
    """The source representation is not suitable for publication approval."""


def require(ok: bool, message: str):
    if not ok:
        raise Hold(message)


def digest(raw: str) -> str:
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def normalized(s: str) -> str:
    return SPACE.sub(' ', s).strip()


class _CitationHTML(HTMLParser):
    """Conservative text-level detector, *not* a browser visibility oracle."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.frames: list[tuple[str, int | None, bool, bool]] = []
        self.contexts: dict[int, list[str]] = {0: []}
        self.safety: dict[int, bool] = {0: False}
        self.next_id = 1
        self.suppressed = Counter()
        self.attribute_citations = Counter()
        self.comment_citations = Counter()
        self.invalid = 0
        self.unmatched_end_tags = 0

    def _inside_suppressed(self):
        return any(f[2] for f in self.frames)

    def _nearest_context(self):
        for _, cid, _, _ in reversed(self.frames):
            if cid is not None:
                return cid
        return 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for name, value in attrs:
            if value is not None and TOKEN_INTENT.search(value):
                self.attribute_citations.update(TOKEN.findall(value))
                self.invalid += len(TOKEN_INTENT.findall(value)) - len(TOKEN.findall(value))
        hide = (tag in SUPPRESSED_TAGS or 'hidden' in a or
                (a.get('aria-hidden') or '').strip().lower() == 'true' or
                re.search(r'(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)\b',
                          (a.get('style') or ''), re.I) is not None)
        cid = None
        if tag in CONTEXT_TAGS:
            require(self.next_id <= MAX_CONTEXTS, 'too many text contexts')
            cid = self.next_id
            self.next_id += 1
            self.contexts[cid] = []
            self.safety[cid] = any(f[3] for f in self.frames)
        is_safety = bool(set((a.get('class') or '').split()) & SAFETY_CLASSES or a.get('role') == 'alert')
        if is_safety:
            self.safety[self._nearest_context()] = True
            if cid is not None:
                self.safety[cid] = True
        if tag not in VOID_TAGS:
            self.frames.append((tag, cid, bool(hide), is_safety))

    def handle_startendtag(self, tag, attrs):
        # Void elements are not pushed; non-void self-closing syntax remains
        # a text-only parsing ambiguity requiring reviewer attention.
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        if not self.frames:
            self.unmatched_end_tags += 1
            return
        if self.frames[-1][0] == tag:
            self.frames.pop()
        else:
            # Tolerate common HTML implied closing tags in the review packet,
            # but disclose that the text model was not a browser rendering.
            ix = next((i for i in range(len(self.frames)-1, -1, -1)
                       if self.frames[i][0] == tag), -1)
            self.unmatched_end_tags += 1
            if ix >= 0:
                del self.frames[ix:]

    def handle_data(self, data):
        if self._inside_suppressed():
            self.suppressed.update(TOKEN.findall(data))
            self.invalid += len(TOKEN_INTENT.findall(data)) - len(TOKEN.findall(data))
            return
        cid = self._nearest_context()
        self.contexts[cid].append(data)

    def handle_comment(self, data):
        self.comment_citations.update(TOKEN.findall(data))
        self.invalid += len(TOKEN_INTENT.findall(data)) - len(TOKEN.findall(data))

    def summarize(self):
        contexts = defaultdict(list)
        warnings = []
        tokens = 0
        for cid, pieces in self.contexts.items():
            value = normalized(''.join(pieces))
            if not value:
                continue
            ids = TOKEN.findall(value)
            count_intent = len(TOKEN_INTENT.findall(value))
            self.invalid += count_intent - len(ids)
            tokens += len(ids)
            if ids:
                fingerprint = digest(value)
                for sid in ids:
                    contexts[sid].append(fingerprint)
            if self.safety.get(cid):
                warnings.append(digest(value))
        require(tokens <= MAX_TOKENS, 'too many citation markers')
        return {
            'citation_context_sha256': {sid: sorted(vals) for sid, vals in sorted(contexts.items())},
            'visible_token_count_text_model': tokens,
            'attribute_citations': dict(sorted(self.attribute_citations.items())),
            'comment_citations': dict(sorted(self.comment_citations.items())),
            'suppressed_citations': dict(sorted(self.suppressed.items())),
            'malformed_tokens': self.invalid,
            'html_structure_ambiguities': self.unmatched_end_tags + len(self.frames),
            'warning_text_sha256': sorted(warnings),
        }


def inspect(raw: bytes) -> dict:
    require(type(raw) is bytes and len(raw) <= MAX_BYTES, 'untrusted or oversized HTML')
    try:
        html = raw.decode('utf-8', errors='strict')
    except UnicodeDecodeError as exc:
        raise Hold('invalid UTF-8 article') from exc
    parser = _CitationHTML()
    parser.feed(html)
    parser.close()
    return parser.summarize()


def compare(old: bytes, new: bytes) -> dict:
    """Only metadata/digests, never source paragraphs or positive approvals."""
    before, after = inspect(old), inspect(new)
    bc, ac = before['citation_context_sha256'], after['citation_context_sha256']
    common = sorted(set(bc) & set(ac))
    drift = [sid for sid in common if Counter(bc[sid]) != Counter(ac[sid])]
    new_ids = sorted(set(ac) - set(bc))
    lost_ids = sorted(set(bc) - set(ac))
    count_drift = [sid for sid in common if len(ac[sid]) != len(bc[sid])]
    return {
        'unchanged_citation_id_changed_claim_neighborhood_NOT_APPROVED': drift,
        'unchanged_id_same_count_changed_context_NOT_APPROVED': [
            sid for sid in drift if sid not in count_drift],
        'citation_ids_added': new_ids, 'citation_ids_removed': lost_ids,
        'same_id_citation_occurrence_count_changed': count_drift,
        'visible_citations_before_text_model': before['visible_token_count_text_model'],
        'visible_citations_after_text_model': after['visible_token_count_text_model'],
        'hidden_or_nontext_citations_before': {k: before[k] for k in
            ('attribute_citations','comment_citations','suppressed_citations')},
        'hidden_or_nontext_citations_after': {k: after[k] for k in
            ('attribute_citations','comment_citations','suppressed_citations')},
        'warning_text_changed_requires_review':
            before['warning_text_sha256'] != after['warning_text_sha256'],
        'structural_ambiguity_or_malformed_token': any(
            before[k] or after[k] for k in ('malformed_tokens', 'html_structure_ambiguities')),
        'all_revision_claims_need_human_review': True,
        'evidence_is_not_a_safety_verdict': True,
        'may_publish': False,
    }


def scan(root: Path) -> dict:
    """Re-derive R107/R108 exact Git custody; augment only changed body paths."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import r107_exact_branch_progression_adjudication as r107
    import r108_source_citation_change_impact_crosswalk as r108
    queue = r107.scan(root)
    evidence = r108.crosswalk(queue, lambda commit, path: r108.git_object(root, commit, path))
    tips = {r['origin']: r for r in queue['seven_contributor_commit_ancestry']}
    rows = []
    for row in evidence['rows_NOT_APPROVED']:
        if row['category'] != 'body':
            continue
        tip = tips[row['origin']]
        if row['frozen_oid'] and row['observed_oid']:
            old = r108.git_object(root, tip['frozen_commit_sha'], row['path'])
            new = r108.git_object(root, tip['observed_commit_sha'], row['path'])
            require(r107.r60.blob_sha(old) == row['frozen_oid'] and
                    r107.r60.blob_sha(new) == row['observed_oid'],
                    'body Git OID no longer matches R107/R108 evidence')
            details = compare(old, new)
        else:
            details = {'created_or_removed_body_requires_review': True,
                       'may_publish': False}
        rows.append({'origin': row['origin'], 'path': row['path'],
                     'frozen_oid': row['frozen_oid'], 'observed_oid': row['observed_oid'],
                     'citation_neighborhood_review_NOT_APPROVED': details,
                     'human_claim_review': 'NOT_REVIEWED', 'may_publish': False})
    result = {'schema': SCHEMA, 'issue': 136, 'release_state': 'HOLD',
              'may_publish': False, 'independent_QD_PASS': False,
              'qualified_emergency_safety_approved': False,
              'R108_sha256_NOT_A_SIGNATURE': evidence['sha256_NOT_A_SIGNATURE'],
              'changed_body_review_count': len(rows),
              'rows_NOT_APPROVED': sorted(rows, key=lambda x: (x['origin'],x['path'])),
              'review_required': 'Each revised claim neighborhood needs original-source and safety review; Git hashes are not approvals.'}
    result['sha256_NOT_A_SIGNATURE'] = digest(json.dumps(result, sort_keys=True,
        ensure_ascii=False, separators=(',', ':'), allow_nan=False))
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument('--json', action='store_true')
    a = p.parse_args(argv)
    result = scan(a.repo_root.resolve())
    if a.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print(json.dumps({'schema': SCHEMA, 'release_state': 'HOLD',
                          'changed_body_review_count': result['changed_body_review_count'],
                          'may_publish': False, 'sha256_NOT_A_SIGNATURE': result['sha256_NOT_A_SIGNATURE']}, sort_keys=True))
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (Hold, OSError, ValueError, KeyError) as exc:
        print('R109 CITATION CONTEXT HOLD: '+str(exc), file=sys.stderr)
        raise SystemExit(2)
