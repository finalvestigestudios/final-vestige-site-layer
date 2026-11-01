#!/usr/bin/env python3
"""R13 Preparedness: deterministic, *non-authoritative* action-claim review triage.

Citation-preserving R8/R12 reports enumerate statements that already have a {{cite:id}}
marker. They cannot find a consequential instruction with NO citation. This reader-only
triage records visible high-consequence action blocks, including uncited ones, for
human editorial/source/safety review. A cited block is never automatically verified.

This code does not fetch source URLs, check clinical accuracy, publish, or approve.
"""
from __future__ import annotations

import argparse
import csv
from hashlib import sha256
from html import unescape
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import re
import sys

CITES = re.compile(r'\{\{cite:([a-z0-9-]+)\}\}')
WRONG_CITE = re.compile(r'\{\{\s*cite\s*:', re.I)
BLOCKS = frozenset({'p', 'li', 'td', 'th', 'blockquote', 'dd', 'figcaption', 'caption'})
IGNORED = frozenset({'script', 'style', 'template', 'noscript', 'svg', 'math', 'head'})
VOID = frozenset('area base br col embed hr img input link meta param source track wbr'.split())
MAX_BODY_BYTES = 2_000_000
MAX_BLOCKS = 50_000
MAX_NOTE_LENGTH = 1200
MAX_RESULTS = 15000
# The pattern list is deliberately a *flagging heuristic*, not a safety classifier.
HAZARDS = {
    'water-treatment': r'\b(?:water|bleach|chlorin(?:e|ate|ation)|boil(?:ing)?|disinfect(?:ion|ant)?|filter(?:ing)?|cistern|purif\w*)\b',
    'food-preservation': r'\b(?:canner|canning|can(?:ned)?\s+(?:meat|food)|botulis\w*|jerky|dehydrat\w*|ferment\w*|cur(?:e|ed|ing)|brin(?:e|ing)|refrigerat\w*|freez(?:e|er|ing)|food(?:\s+safety)?|leftovers?)\b',
    'combustion-fire': r'\b(?:generator|carbon\s+monoxide|co\s+alarm|grill|propane|charcoal|flame|fire\s+escape|smoke(?:\s+(?:alarm|detector))?|burner|ventilat\w*|fuel\s+(?:burn|stor)|evacuat\w*)\b',
    'medical-dependency': r'\b(?:insulin|medicat\w*|prescri\w*|pharmacist|medical\s+device|oxygen|dialys\w*|symptom|injur\w*|poison\w*|wound|first\s+aid|epipen|defibrillat\w*|emergency\s+number)\b',
    'vulnerable-households': r'\b(?:infants?|bab(?:y|ies)|formula|pregnan\w*|disabilit\w*|wheelchair|mobility\s+(?:aid|device)|elderly|caregiver|service\s+animals?)\b',
}
ACTION = re.compile(
    r'\b(?:must|should|need\s+to|have\s+to|do\s+not|don\x27t|never|always|only\s+use|'
    r'call|seek|stop|avoid|remove|place|position|plan|store|discard|replace|throw\s+out|'
    r'boil|heat|cool|refrigerate|freeze|freeze\s+again|disinfect|filter|treat|'
    r'add|dilute|mix|wait|leave|keep|check|follow|take|use|plug|move|'
    r'turn\s+off|turn\s+on|stay\s+out|ventilate|evacuate|call\s+911)\b', re.I)
NUMERIC = re.compile(
    r'\b\d+(?:[.,]\d+)?\s*(?:°?\s*[CF]\b|degrees?\s*(?:[CF]|fahrenheit|celsius)|'
    r'feet|foot|ft\b|meters?|minutes?|hours?|days?|weeks?|months?|seconds?|'
    r'gallons?|lit(?:er|re)s?|ounces?|oz\b|drops?|teaspoons?|tablespoons?|'
    r'ppm\b|mg\b|ml\b|%|percent)\b', re.I)
STATUS = 'PENDING_HUMAN_EVIDENCE_AND_SAFETY_REVIEW'


def digest(value: object) -> str:
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                             separators=(',', ':')).encode('utf-8')).hexdigest()


def normalize(s: str) -> str:
    return ' '.join(unescape(s).split())


class TriageFailure(ValueError):
    pass


class VisibleActionBlocks(HTMLParser):
    """Parse actual leaf-level reader blocks. Do not treat hidden markup as evidence."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.frames: list[dict] = []
        self.hidden_depth = 0
        self.element_stack: list[tuple[str, bool]] = []
        self.records: list[dict] = []
        self.citation_count = 0
        self.visible_citation_count = 0
        self.error = None
        self.open_counter = 0

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = dict(attrs)
        # Explicit hidden/aria-hidden is excluded from the visible instruction queue.
        # R8 separately rejects hidden citations, so exclusion cannot launder a cite.
        hidden = (tag in IGNORED or 'hidden' in attrs
                  or attrs.get('aria-hidden', '').lower() == 'true'
                  or bool(re.search(r'(?:^|;)\s*display\s*:\s*none(?:\s|;|$)', attrs.get('style') or '', re.I)))
        if tag in VOID:
            return
        self.element_stack.append((tag, hidden))
        if hidden:
            self.hidden_depth += 1
        if tag in BLOCKS and not self.hidden_depth:
            self.open_counter += 1
            self.frames.append({'tag': tag, 'depth': len(self.element_stack), 'parts': [], 'open_ordinal': self.open_counter})

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_data(self, text):
        if self.hidden_depth:
            return
        self.visible_citation_count += len(CITES.findall(text))
        if self.frames:
            self.frames[-1]['parts'].append(text)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in VOID:
            return
        if not self.element_stack:
            self.error = 'unbalanced closing HTML tag'
            return
        actual, hidden = self.element_stack.pop()
        if actual != tag:
            # The source bodies are expected to be valid HTML. Never silently
            # attribute advice/citations across broken nesting.
            self.error = 'ill-nested HTML'
        if self.frames and self.frames[-1]['depth'] == len(self.element_stack) + 1:
            frame = self.frames.pop()
            if frame['tag'] != tag:
                self.error = 'mismatched semantic block'
            else:
                raw = ''.join(frame['parts'])
                citations = CITES.findall(raw)
                self.citation_count += len(citations)
                text = normalize(CITES.sub('', raw))
                if len(text) > 15000:
                    self.error = 'oversized single visible block'
                if text:
                    self.records.append({'tag': tag, 'text': text, 'citations': citations, 'open_ordinal': frame['open_ordinal']})
        if hidden:
            self.hidden_depth -= 1


def scan_html(body: str, *, include_count: bool = False):
    if not isinstance(body, str) or not body or len(body.encode('utf-8')) > MAX_BODY_BYTES or '\x00' in body:
        raise TriageFailure('invalid, missing or oversized article HTML')
    parser = VisibleActionBlocks()
    try:
        parser.feed(body)
        parser.close()
    except (ValueError, OverflowError, UnicodeError) as exc:
        raise TriageFailure('malformed source HTML') from exc
    if parser.error or parser.element_stack or parser.frames or parser.hidden_depth:
        raise TriageFailure('incomplete or ill-nested article HTML')
    if len(parser.records) > MAX_BLOCKS:
        raise TriageFailure('excessive semantic blocks')
    # Visible citations in headings or other non-leaf containers are counted too.
    # R8 remains authoritative for occurrence-to-source claim matching.
    records = sorted(parser.records, key=lambda r: r['open_ordinal'])
    return (records, parser.visible_citation_count) if include_count else records


def triage_article(slug: str, meta: dict, body: str, *, expected_citations: int | None = None) -> dict:
    if not re.fullmatch(r'[a-z][a-z0-9-]{1,99}', slug):
        raise TriageFailure('invalid article slug')
    if not isinstance(meta, dict) or meta.get('slug') != slug or not isinstance(meta.get('source_use'), dict):
        raise TriageFailure('article metadata or source-use missing')
    status = meta.get('status') or {}
    if status.get('publish') != 'draft':
        raise TriageFailure('article is not a private draft')
    source_notes = meta['source_use']
    if not all(isinstance(k, str) and re.fullmatch(r'[a-z0-9-]+', k)
               and isinstance(v, str) and v.strip() for k, v in source_notes.items()):
        raise TriageFailure('blank or invalid source-use annotation')
    records, visible_citation_count = scan_html(body, include_count=True)
    # A source citation in hidden content or a non-block does not prove support.
    actual_citations = visible_citation_count
    if expected_citations is not None and actual_citations != expected_citations:
        raise TriageFailure(f'{slug}: citation count changed or cite appeared outside reader blocks')
    body_hash = sha256(body.encode('utf-8')).hexdigest()
    flags = []
    for ordinal, block in enumerate(records, 1):
        text = block['text']
        families = sorted(k for k, p in HAZARDS.items() if re.search(p, text, re.I))
        if not families:
            continue
        has_action = bool(ACTION.search(text))
        has_units = bool(NUMERIC.search(text))
        if not (has_action or has_units):
            continue
        ids = block['citations']
        unknown = sorted(set(ids) - source_notes.keys())
        if unknown:
            raise TriageFailure(f'{slug}: claim cites unannotated source ID(s): {unknown[:3]}')
        if WRONG_CITE.search(text):
            raise TriageFailure(f'{slug}: malformed cite marker visible in reader text')
        flag = {
            'article': slug, 'source_body_sha256': body_hash,
            'block_ordinal': ordinal, 'block_tag': block['tag'],
            'risk_families': families, 'has_action_language': has_action,
            'has_numeric_instruction': has_units,
            'source_ids_in_same_block': list(dict.fromkeys(ids)),
            'citation_occurrences_in_same_block': len(ids),
            'citation_proximity': 'SAME_VISIBLE_BLOCK' if ids else 'NO_SAME_BLOCK_CITATION',
            'review_state': STATUS,
            'review_reason': ('NO_SAME_BLOCK_CITATION_NEEDS_HUMAN_EVIDENCE_CHECK' if not ids
                              else 'CITED_CLAIM_STILL_NEEDS_HUMAN_SOURCE_AND_SAFETY_REVIEW'),
            'excerpt': text[:MAX_NOTE_LENGTH],
            'excerpt_truncated': len(text) > MAX_NOTE_LENGTH,
        }
        flag['flag_sha256'] = digest(flag)
        flags.append(flag)
        if len(flags) > MAX_RESULTS:
            raise TriageFailure('excessive actionable claims')
    return {'slug': slug, 'draft': True, 'body_sha256': body_hash,
            'visible_blocks': len(records), 'visible_block_citation_occurrences': actual_citations,
            'triaged': len(flags), 'without_same_block_citation': sum(not f['source_ids_in_same_block'] for f in flags),
            'flags': flags}


def build_triage(lib, *, expected_items=36, canonical=None, expected_occurrences=1959) -> dict:
    if len(lib.articles) != expected_items:
        raise TriageFailure('frozen 35 articles plus 1 planner inventory changed')
    expected_by_slug = {}
    if canonical is not None:
        claims = canonical.get('claims') if isinstance(canonical, dict) else None
        if not isinstance(claims, list) or len(claims) != expected_occurrences:
            raise TriageFailure('canonical R8 occurrence evidence missing or changed')
        for item in claims:
            slug = item.get('article')
            if slug not in lib.articles:
                raise TriageFailure('canonical claim references unknown article')
            expected_by_slug[slug] = expected_by_slug.get(slug, 0) + 1
        if canonical.get('release_state') != 'HOLD' or canonical.get('may_publish') is not False:
            raise TriageFailure('canonical evidence makes unauthorized release claim')
    rows = [triage_article(slug, lib.articles[slug], lib.articles[slug]['_body'],
                           expected_citations=expected_by_slug.get(slug) if canonical else None)
            for slug in sorted(lib.articles)]
    if canonical is not None and sum(x['visible_block_citation_occurrences'] for x in rows) != expected_occurrences:
        raise TriageFailure('visible citation occurrence inventory drift')
    flags = [f for row in rows for f in row['flags']]
    result = {'schema_version': 1, 'authority': 'MACHINE_HEURISTIC_TRIAGE_ONLY',
              'release_state': 'HOLD', 'may_publish': False,
              'independent_human_source_checks_verified': False,
              'qualified_safety_approvals': 0, 'no_citation_is_proof_of_accuracy': True,
              'uncited_is_review_priority_not_proof_of_inaccuracy': True,
              'regex_heuristics_have_false_negatives': True,
              'draft_items': len(rows), 'triaged_blocks': len(flags),
              'without_same_block_citation': sum(not f['source_ids_in_same_block'] for f in flags),
              'source_body_sha256_by_article': {row['slug']: row['body_sha256'] for row in rows},
              'articles': rows}
    result['triage_digest_sha256'] = digest(result)
    return result


def csv_export(report: dict) -> str:
    output = io.StringIO(newline='')
    writer = csv.writer(output, lineterminator='\n')
    writer.writerow(('article', 'block_ordinal', 'risk_families', 'citation_proximity',
                     'source_ids', 'body_sha256', 'flag_sha256', 'review_state', 'excerpt'))
    for row in report['articles']:
        for f in row['flags']:
            values = (f['article'], f['block_ordinal'], ';'.join(f['risk_families']),
                      f['citation_proximity'], ';'.join(f['source_ids_in_same_block']),
                      f['source_body_sha256'], f['flag_sha256'], f['review_state'], f['excerpt'])
            # Spreadsheet imports must never run formula-like excerpts.
            writer.writerow([("'" + v) if isinstance(v, str) and v.lstrip().startswith(('=', '+', '-', '@', '\t', '\r'))
                             else v for v in values])
    return output.getvalue()


def bind_full_R8_claim_evidence(lib, physical_rows, fingerprint, receipt,
                               *, make_report, baseline, expected_occurrences=1959):
    """Bounded re-derivation: R10 receipt is a DIGEST, not the 1,959 claims.

    Independently regenerate the original full R8 claim ledger, compare its
    canonical SHA-256 to R10's already validated HOLD receipt, and only then
    let the heuristic action triage inspect individual claim positions. Never
    mistake a compact custody receipt for the actual evidence ledger.
    """
    if (not isinstance(receipt, dict) or receipt.get('release_state') != 'HOLD'
            or receipt.get('may_publish') is not False):
        raise TriageFailure('R10 receipt lost explicit publication HOLD')
    report = make_report(lib, rows=physical_rows, fingerprint=fingerprint,
                         expect=baseline)
    if (not isinstance(report, dict) or report.get('release_state') != 'HOLD'
            or report.get('may_publish') is not False
            or not isinstance(report.get('claims'), list)
            or len(report['claims']) != expected_occurrences):
        raise TriageFailure('R8 claim report missing or not HOLD')
    content_digest = sha256(json.dumps(
        report, ensure_ascii=False, sort_keys=True,
        separators=(',', ':')).encode('utf-8')).hexdigest()
    if receipt.get('source_content_digest_sha256') != content_digest:
        raise TriageFailure('full R8 claims do not match frozen R10 custody digest')
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--json-out', type=Path, help='private HOLD queue inside preparedness/build only')
    ap.add_argument('--csv-out', type=Path, help='private HOLD CSV inside preparedness/build only')
    args = ap.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'tools'))
    import build, evidence_freeze, validate, source_review_queue
    import claim_corpus_release_gate as r10, claim_occurrence_audit as r8
    import draft_export_custody as r11, rendered_citation_gate as r12
    # A zero exit from these deterministic checks does not mean QD approval.
    lib = build.Library(root)
    errors = evidence_freeze.verify(lib)
    if errors:
        raise TriageFailure('evidence freeze: ' + '; '.join(errors[:4]))
    errors, _warnings = validate.validate(lib)
    if errors:
        raise TriageFailure('native validator: ' + '; '.join(errors[:4]))
    physical_rows = source_review_queue.source_rows(root)
    canonical = r10.audit_corpus(lib, physical_rows, evidence_freeze.fingerprint)
    r11.audit_export(lib, root / 'build', build, canonical_receipt=canonical)
    rendered = r12.audit_corpus(lib, build, claim_parser=r8.parse_visible_claims)
    if (rendered.get('release_state') != 'HOLD' or rendered.get('may_publish') is not False
            or rendered.get('rendered_citation_occurrences') != 1959
            or rendered.get('article_source_pairs') != 367):
        raise TriageFailure('R12 rendered source/citation parity was not proven')
    frozen_claims = bind_full_R8_claim_evidence(
        lib, physical_rows, evidence_freeze.fingerprint, canonical,
        make_report=r8.make_report, baseline=r8.BASELINE)
    result = build_triage(lib, canonical=frozen_claims)
    private_root = root / 'build'
    if args.json_out:
        r8.safe_export(args.json_out, json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + '\n', private_root)
    if args.csv_out:
        r8.safe_export(args.csv_out, csv_export(result), private_root)
    print(json.dumps({k: v for k, v in result.items() if k not in {'articles', 'source_body_sha256_by_article'}}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
