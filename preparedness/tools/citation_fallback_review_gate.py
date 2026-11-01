#!/usr/bin/env python3
"""R25: independent, read-only claim-to-source *review packet*, never a safety PASS.

Run on the complete, 81-file-frozen checkout after source_group_review_gate.
Every article-source relationship retains the contributor-specific source record,
full original supports/notes and article-specific source_use. No URL de-duping.
"""
from __future__ import annotations
from collections import Counter
from datetime import date
import argparse
import hashlib
import html
import importlib.util
import json
from pathlib import Path
import re
import sys

CITE = re.compile(r'\{\{cite:([A-Za-z0-9_.-]+)\}\}')
EXPECTED = (35, 1, 1959, 367, 43, 30)

class ReviewHold(ValueError):
    """Missing or ambiguous evidence: this is not publication authorization."""

def need(ok, reason):
    if not ok:
        raise ReviewHold(reason)

def _load_placement_validator():
    # `python -I` intentionally removes the script directory from sys.path.
    # Load this fixed, scoped sibling by exact path (never from a package search).
    location = Path(__file__).with_name('citation_token_visibility_gate.py')
    need(location.is_file() and not location.is_symlink(),
         'missing or linked citation placement gate')
    spec = importlib.util.spec_from_file_location('preparedness_citation_placement', location)
    need(spec is not None and spec.loader is not None, 'citation placement gate cannot load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.verified_citations


def _load_review_index_validator():
    # R31 hardens the existing mandatory 13th preflight stage without
    # changing the hosted runner's step contract or claiming review completion.
    location = Path(__file__).with_name('citation_review_index_gate.py')
    need(location.is_file() and not location.is_symlink(),
         'missing or linked independent citation review index gate')
    spec = importlib.util.spec_from_file_location('preparedness_citation_review_index', location)
    need(spec is not None and spec.loader is not None,
         'citation review index gate cannot load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_index


def _load_occurrence_priority_validator():
    # R33: reviewer work order is required inside the existing mandatory
    # final preflight stage, with NO new public/CMS/publishing actions.
    location = Path(__file__).with_name('citation_occurrence_priority_gate.py')
    need(location.is_file() and not location.is_symlink(),
         'missing or linked human claim-priority custody gate')
    spec = importlib.util.spec_from_file_location('preparedness_r33_claim_priority', location)
    need(spec is not None and spec.loader is not None,
         'claim-priority custody gate cannot load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_priority_queue


def _load_source_reading_batches_validator():
    # R34: mandatory lossless review-batch custody in existing private stage 13.
    # An absent/linked validator fails closed; no CMS, navigation or public writes.
    location = Path(__file__).with_name('citation_review_batch_gate.py')
    need(location.is_file() and not location.is_symlink(),
         'missing or linked full source-reading batch gate')
    spec = importlib.util.spec_from_file_location('preparedness_r34_reading_batches', location)
    need(spec is not None and spec.loader is not None,
         'source-reading batch validator cannot load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.make_batch_index



def _load_human_review_intake_validator():
    # R35: mandatory independent, evidence-bound review work-item census.
    # It creates blank intake forms ONLY. No human/QD/safety authorization.
    location = Path(__file__).with_name('citation_review_handoff_gate.py')
    need(location.is_file() and not location.is_symlink(),
         'missing or linked human review handoff validator')
    spec = importlib.util.spec_from_file_location('preparedness_r35_review_intake', location)
    need(spec is not None and spec.loader is not None,
         'human review handoff validator cannot load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.make_handoff


def _load_global_shared_source_validator():
    # R36 closes the cited-only blind spot: all 30 original duplicate-URL
    # groups, including uncited contributors, get lossless NOT_STARTED tasks.
    # Keep the frozen source and 81-file custody preflights authoritative.
    location = Path(__file__).with_name('global_shared_source_review_gate.py')
    need(location.is_file() and not location.is_symlink(),
         'missing or linked global shared-source review gate')
    spec = importlib.util.spec_from_file_location('preparedness_r36_global_sources', location)
    need(spec is not None and spec.loader is not None,
         'global shared-source gate cannot load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_global_source_review


def _load_private_reviewer_csv_export_validator():
    # R37: mandatory private CSV reviewer-desk census. It is data-only:
    # spreadsheet-safe read-only worksheets; no public/CMS writes or human signoff.
    location = Path(__file__).with_name('reviewer_csv_export_gate.py')
    need(location.is_file() and not location.is_symlink(),
         'missing or linked R37 private CSV human-review export gate')
    spec = importlib.util.spec_from_file_location('preparedness_r37_private_csv_export', location)
    need(spec is not None and spec.loader is not None,
         'R37 private reviewer export module cannot load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_review_csv_export


def _load_quarantined_csv_intake_validator():
    # R38: even an edited reviewer CSV can only enter a quarantined, untrusted
    # private annotation queue. Original citation/source cells are immutable;
    # false completed reviews, QD-PASS, safety or publication claims fail closed.
    location = Path(__file__).with_name('reviewer_quarantine_gate.py')
    need(location.is_file() and not location.is_symlink(),
         'missing or linked R38 quarantine validator')
    spec = importlib.util.spec_from_file_location('preparedness_r38_quarantined_intake', location)
    need(spec is not None and spec.loader is not None,
         'R38 quarantine validator cannot load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.quarantine_reviewer_csv


def _load_private_key_receipt_validator():
    # R39: the exact R38 evidence-quarantine chain now has a private
    # key-possession receipt challenge. No credentials, reviewers, approvals,
    # or progress are synthesized by CI. Independent trusted key registries
    # and durable replay ledgers are mandatory for real receipt verification.
    location = Path(__file__).with_name('reviewer_receipt_chain_gate.py')
    need(location.is_file() and not location.is_symlink(),
         'missing or linked R39 reviewer receipt validator')
    spec = importlib.util.spec_from_file_location(
        'preparedness_r39_private_receipt', location)
    need(spec is not None and spec.loader is not None,
         'R39 reviewer receipt validator cannot load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.unsigned_challenge


def _load_recent_transcript_validator():
    # R40: freeze the zero-review R39 baseline and require the new offline
    # transcript auditor to exist as an exact, nonsymlinked sibling. Actual
    # reviewer receipts require EXTERNAL trusted anchors and are never
    # manufactured or signed by private CI.
    location = Path(__file__).with_name('reviewer_receipt_transcript_gate.py')
    need(location.is_file() and not location.is_symlink(),
         'missing or linked R40 offline receipt-transcript audit gate')
    spec = importlib.util.spec_from_file_location(
        'preparedness_r40_offline_transcript', location)
    need(spec is not None and spec.loader is not None,
         'R40 transcript validator cannot load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.preflight_unsigned_baseline


def _load_historical_history_unsigned_preflight():
    # R41: evidence-retaining retrospective audit contract. Still zero actual
    # receipts, human review or ledger in CI; keep the public release on HOLD.
    location = Path(__file__).with_name('reviewer_receipt_history_gate.py')
    need(location.is_file() and not location.is_symlink(),
         'missing or linked R41 historical receipt-custody gate')
    spec = importlib.util.spec_from_file_location(
        'preparedness_r41_private_retrospective_custody', location)
    need(spec is not None and spec.loader is not None,
         'R41 history gate cannot load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.preflight_unsigned_history


def _load_article_review_dossiers():
    # R42: bind each individual article/tool to its exact original R37
    # human-review worksheets, preserving all duplicate URL reading scopes.
    # Machine preflight cannot approve sources, medical guidance, or release.
    location = Path(__file__).with_name('article_review_dossier_gate.py')
    need(location.is_file() and not location.is_symlink(),
         'missing or linked R42 article review evidence gate')
    spec = importlib.util.spec_from_file_location(
        'preparedness_r42_article_source_review_handoff', location)
    need(spec is not None and spec.loader is not None,
         'R42 article review gate cannot load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_article_review_dossiers


def _load_private_offline_html_gate():
    # R43: render all 35+1 private dossiers and global URL groups to inert,
    # fully escaped local-only reviewer pages. Never publish or fetch sources.
    location = Path(__file__).with_name('reviewer_offline_html_gate.py')
    need(location.is_file() and not location.is_symlink(),
         'missing or linked R43 private offline review desk gate')
    spec = importlib.util.spec_from_file_location(
        'preparedness_r43_private_offline_evidence_view', location)
    need(spec is not None and spec.loader is not None,
         'R43 offline review view gate cannot load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_offline_html



def _load_private_zip_custody_gate():
    # R44: offline, deterministic 38-page + manifest ZIP evidence custody.
    # All ZIP bytes remain in memory inside the mandatory private stage.
    # External reviewers need separately pinned R42/R43 trust anchors.
    # No publication, CMS upload, reviewer identity or safety approval.
    location = Path(__file__).with_name('reviewer_private_zip_gate.py')
    need(location.is_file() and not location.is_symlink(),
         'missing or linked R44 private ZIP custody gate')
    spec = importlib.util.spec_from_file_location(
        'preparedness_r44_private_zip_custody', location)
    need(spec is not None and spec.loader is not None,
         'R44 private ZIP custody gate cannot load')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_private_zip, module.verify_private_zip

verified_citations = _load_placement_validator()
build_review_index = _load_review_index_validator()
build_priority_queue = _load_occurrence_priority_validator()
build_source_reading_batches = _load_source_reading_batches_validator()
build_human_review_intake = _load_human_review_intake_validator()
build_global_shared_source_review = _load_global_shared_source_validator()
build_private_reviewer_csv_export = _load_private_reviewer_csv_export_validator()
build_quarantine_reviewer_csv = _load_quarantined_csv_intake_validator()
build_private_key_receipt_challenge = _load_private_key_receipt_validator()
build_recent_transcript_unsigned_preflight = _load_recent_transcript_validator()
build_history_unsigned_preflight = _load_historical_history_unsigned_preflight()
build_article_review_dossiers = _load_article_review_dossiers()
build_private_offline_review_desk = _load_private_offline_html_gate()
build_private_zip_custody, verify_private_zip_custody = _load_private_zip_custody_gate()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')

def excerpt(body, begin, end):
    # Context only; original HTML remains authoritative and frozen separately.
    before, after = body[max(0, begin - 210):begin], body[end:end + 210]
    before = re.sub(r'<[^>]*>', ' ', before)
    after = re.sub(r'<[^>]*>', ' ', after)
    return re.sub(r'\s+', ' ', html.unescape(before[-140:] + ' [CITATION] ' + after[:140])).strip()

def audit(lib, expected=EXPECTED):
    """Re-derive every citation occurrence and source binding from draft objects.

    expected = articles, tools, occurrences, relationships, base fallbacks,
    shared URLs. Only tests may override production frozen totals.
    """
    need(type(expected) is tuple and len(expected) == 6 and
         all(type(x) is int and x >= 0 for x in expected), 'invalid audit contract')
    origins = lib.article_origins
    articles = lib.articles
    need(type(origins) is dict and set(origins) == set(articles),
         'crosswalk origin map does not cover every article and tool')
    need(len(articles) == expected[0] + expected[1], 'article/tool count drift')
    need(len({a.get('slug') for a in articles.values()}) == len(articles) and
         all(a.get('slug') == s for s, a in articles.items()), 'article slug duplication')
    need(sum(a.get('kind') == 'tool' for a in articles.values()) == expected[1],
         'tool inventory drift')
    need(all(isinstance(k, str) and k and '/' not in k for k in articles),
         'unsafe article URL slug')
    urls = {}
    for versions in lib.source_variants.values():
        for v in versions:
            need(type(v.get('id')) is str and type(v.get('url')) is str and
                 v['url'].startswith('https://') and type(v.get('_origin')) is str,
                 'source ID, URL or original origin invalid')
            urls.setdefault(v['url'], []).append(v)
    collisions = {url for url, rows in urls.items() if len(rows) > 1}
    need(len(collisions) == expected[5] and set(lib.crosswalk_groups) == collisions,
         'shared URL review groups missing or silently collapsed')
    for url in collisions:
        g = lib.crosswalk_groups[url]
        need(g.get('review_status') == 'pending-human-source-and-reading-scope-review' and
             g.get('reviewer') is None and g.get('reviewed_on') is None,
             'shared URL group falsely marked reviewed')
    queue, total, fallback_count = [], 0, 0
    for slug, meta in sorted(articles.items()):
        origin = origins[slug]
        need(type(origin) is str and origin in {'base','start','shelter','food','health',
             'hist-food','hist-home','hist-field'}, 'unknown contributor origin')
        need(type(meta.get('status')) is dict and meta['status'].get('publish') == 'draft',
             'non-draft article or tool forbidden')
        body, uses = meta.get('_body'), meta.get('source_use')
        need(type(body) is str and type(uses) is dict,
             'article body or article-specific source-use missing')
        # R27: exact tokens alone did not exclude malformed, invisible or
        # attribute-only tokens; keep all original article HTML unchanged.
        found = verified_citations(body)
        ids = {m.group(1) for m in found}
        need(ids == set(uses), 'citation/source_use map missing, extra or mismatched')
        need(all(type(s) is str and bool(s.strip()) for s in uses.values()),
             'blank or nontext reading-scope explanation')
        total += len(found)
        by_id = {}
        for m in found:
            by_id.setdefault(m.group(1), []).append(excerpt(body, m.start(), m.end()))
        for sid, contexts in sorted(by_id.items()):
            variants = lib.source_variants.get(sid)
            need(type(variants) is list and len(variants) >= 1, 'unknown source ID')
            own = [v for v in variants if v['_origin'] == origin]
            base = [v for v in variants if v['_origin'] == 'base']
            need(len(own) <= 1 and len(base) <= 1, 'ambiguous same-origin source variant')
            need(bool(own or base), 'source never read in own cluster or base')
            selected = own[0] if own else base[0]
            need(selected.get('id') == sid, 'source variant ID differs from cited identity')
            # R26: comparing only _origin was insufficient. A renderer could
            # substitute a different URL, source-use scope, publisher, title or
            # verification date from the SAME contributor and the prior test
            # would still pass. Compare the ENTIRE JSON identity, with types.
            rendered = lib.source_for(meta, sid)
            need(type(rendered) is dict and canonical(rendered) == canonical(selected),
                 'rendered source identity or reading scope differs from custody source')
            verified = selected.get('verified_on')
            need(type(verified) is str and
                 bool(re.fullmatch(r'\d{4}-\d{2}-\d{2}', verified)),
                 'source has no machine verification date')
            try:
                date.fromisoformat(verified)
            except ValueError as exc:
                raise ReviewHold('source has impossible machine verification date') from exc
            need(type(selected.get('supports')) is str and bool(selected['supports'].strip()),
                 'original reading-depth evidence missing')
            is_fallback = selected['_origin'] != origin
            fallback_count += int(is_fallback)
            # Retain full unabridged original source metadata, not only a
            # URL and a clipped supports/notes excerpt. Fingerprints and
            # zero-based Unicode offsets let reviewers re-find each of the
            # 1,959 tokens in the unchanged article bodies. These are NOT
            # human fact checks or endorsement of clinical/emergency advice.
            source_bytes = canonical(selected)
            row_offsets = [m.start() for m in found if m.group(1) == sid]
            need(len(row_offsets) == len(contexts), 'citation position parity failure')
            queue.append({'slug': slug, 'article_origin': origin,
                          'frozen_article_html_sha256': hashlib.sha256(body.encode('utf-8')).hexdigest(),
                          'frozen_source_use_sha256': hashlib.sha256(uses[sid].encode('utf-8')).hexdigest(),
                          'original_source_record_as_selected': json.loads(source_bytes),
                          'original_source_record_sha256': hashlib.sha256(source_bytes).hexdigest(),
                          'citation_token_codepoint_offsets': row_offsets,
                          'source_id': sid, 'source_origin': selected['_origin'],
                          'source_url': selected['url'], 'machine_verified_on': selected['verified_on'],
                          'base_fallback_requires_human_scope_review': is_fallback,
                          'shared_url_group_requires_human_review': selected['url'] in collisions,
                          'source_supports_as_recorded': selected['supports'],
                          'source_notes_as_recorded': selected.get('notes'),
                          'article_source_use_as_recorded': uses[sid],
                          'citation_occurrences': len(contexts),
                          'all_citation_contexts_for_human_claim_review': contexts,
                          'human_link_checked_by_this_gate': False,
                          'human_claim_reviewed_by_this_gate': False})
    need((len(articles) - expected[1], expected[1], total, len(queue),
          fallback_count, len(collisions)) == expected,
         'frozen 35+1 claim/source counts or base-fallback coverage changed')
    payload = {'schema_version': 1, 'issue': 136, 'release_state': 'HOLD',
               'may_publish': False, 'qualified_safety_clearance': False,
               'independent_QD_approval': False, 'human_source_reviews_completed': False,
               'source_claim_accuracy_verified': False,
               'machine_authority': 'STRUCTURAL_CITATION_TO_SOURCE_REVIEW_QUEUE_ONLY',
               'counts': {'articles': expected[0], 'tools': expected[1],
                          'citations': total, 'relationships': len(queue),
                          'base_fallback_relationships': fallback_count,
                          'shared_url_groups_unreviewed': len(collisions)},
               'review_queue': queue}
    payload['fingerprint_sha256'] = hashlib.sha256(canonical(payload)).hexdigest()
    # The packet digest now binds a second, independently maintained review
    # index validator. Every citation and source relationship must survive its
    # own reconciliation before this mandatory preflight stage can succeed.
    review_index = build_review_index(payload, expected=expected)
    # Bind all individual claim occurrences to both parent custody digests,
    # preserve duplicate URLs, and always leave every task UNREVIEWED.
    priority_queue = build_priority_queue(payload, review_index, expected=expected)
    # Assert full original contributor evidence survives reviewer batching.
    # One card per original source-use relationship, one item per claim occurrence.
    # No automated approval is granted even when this structural gate succeeds.
    reviewer_batches = build_source_reading_batches(payload, priority_queue, expected=expected)
    # R35: every source scope, citation and fallback must have a blank,
    # traceable human-review intake form; successful grouping stays HOLD.
    handoff = build_human_review_intake(reviewer_batches, expected=expected)
    # Mandatory R36 reviewer census of every original repeated URL, including
    # source variants never selected by an article. This grants NO approval.
    # Only the frozen 35+1 production census authorizes a global inventory
    # check. R25's explicitly reduced, synthetic unit fixtures have no actual
    # 224-row crosswalk; R36 exercises those independently in its own 88 tests.
    # The real checkout and mandatory private preflight use EXPECTED, always.
    if expected == EXPECTED:
        # The full frozen corpus gets the R36 global crosswalk, then R37's
        # optional-for-human-use but mandatory-for-machine-custody CSV desk.
        # Older reduced R25 synthetic unit fixtures have no global crosswalk
        # and are tested independently through the R37 synthetic suite.
        original_global_packet = build_global_shared_source_review(
            lib, handoff, expected=expected)
        reviewer_csv = build_private_reviewer_csv_export(
            handoff, original_global_packet, reviewer_batches, expected=expected)
        need(reviewer_csv['manifest']['release_state'] == 'HOLD'
             and reviewer_csv['manifest']['may_publish'] is False,
             'private reviewer export cannot grant publishing approval')
        # R42: structurally reconcile the complete original 35+1 corpus at
        # article level, preserving every citation, reading scope, fallback,
        # cross-cluster source and uncited shared-URL group. Every result is
        # an UNREVIEWED, nonpublishing machine HOLD, not an editorial verdict.
        article_dossiers = build_article_review_dossiers(
            reviewer_csv, lib.taxonomy,
            trusted_r37_manifest_sha256=reviewer_csv['manifest']['fingerprint_sha256'])
        dossier_rows = article_dossiers['article_dossiers']
        need(article_dossiers['release_state'] == 'HOLD'
             and len(dossier_rows) == 36
             and article_dossiers['counts'] ==
                 reviewer_csv['manifest']['counts']
             and sum(x['counts']['claims'] for x in dossier_rows) == 1959
             and sum(x['counts']['scopes'] for x in dossier_rows) == 367
             and sum(x['counts']['fallbacks'] for x in dossier_rows) == 43
             and article_dossiers['all_case_rows_preserved_without_url_deduplication'] is True
             and article_dossiers['may_publish'] is False
             and article_dossiers['qualified_safety_clearance'] is False
             and article_dossiers['independent_QD_approval'] is False
             and article_dossiers['human_source_reviews_completed'] is False
             and all(x['release_state'] == 'HOLD'
                     and x['may_publish'] is False
                     and x['qualified_safety_clearance'] is False
                     and x['independent_QD_approval'] is False
                     for x in dossier_rows),
             'R42 individual article evidence or mandatory safety HOLD drift')
        # R43: mandatory, unapproved, local-only evidence presentation check.
        # The source packet is R42-frozen through the upstream R37 crosswalk.
        # The generated HTML is NOT a WordPress source, safety finding or
        # independent trust pin. No page is persisted by the CI preflight.
        offline_review = build_private_offline_review_desk(
            article_dossiers,
            trusted_r42_sha256=article_dossiers['fingerprint_sha256'])
        private_pages = offline_review['html_files']
        private_manifest = offline_review['manifest']
        need(private_manifest['release_state'] == 'HOLD'
             and len(private_pages) == 38
             and private_manifest['counts'] == article_dossiers['counts']
             and private_manifest['may_publish'] is False
             and private_manifest['qualified_safety_clearance'] is False
             and private_manifest['independent_QD_approval'] is False
             and private_manifest['human_source_reviews_completed'] is False
             and 'global-source-variants.html' in private_pages,
             'R43 offline review view corpus/presentation/safety HOLD drift')
        # R44: privately package, read back and byte-verify every R43 page.
        # CI uses the upstream frozen machine fingerprints for consistency,
        # NOT an independent human-controlled trust anchor or safety finding.
        # No ZIP is written to disk, attached publicly, emailed or published.
        private_package = build_private_zip_custody(
            article_dossiers,
            trusted_r42_sha256=article_dossiers['fingerprint_sha256'])
        private_package_manifest = verify_private_zip_custody(
            private_package['zip_bytes'],
            trusted_r42_sha256=article_dossiers['fingerprint_sha256'],
            trusted_r43_sha256=private_manifest['fingerprint_sha256'])
        need(private_package_manifest == private_package['manifest']
             and private_package['member_count'] == 39
             and private_package_manifest['counts'] == article_dossiers['counts']
             and private_package_manifest['release_state'] == 'HOLD'
             and private_package_manifest['may_publish'] is False
             and private_package_manifest['qualified_safety_clearance'] is False
             and private_package_manifest['independent_QD_approval'] is False
             and private_package_manifest['human_source_reviews_completed'] is False,
             'R44 package lost source-reading evidence or violated private HOLD')
        # The unedited baseline must round-trip R38 intact. This mandatory
        # check is intentionally zero progress: machine CI cannot verify that
        # a human actually visited, read or understood a referenced source.
        quarantined = build_quarantine_reviewer_csv(
            reviewer_csv, reviewer_csv['csv_tables'])
        need(quarantined['manifest']['release_state'] == 'HOLD'
             and quarantined['manifest']['may_publish'] is False
             and quarantined['manifest']['qualified_safety_clearance'] is False
             and quarantined['manifest']['independent_QD_approval'] is False
             and quarantined['manifest']['unverified_progress_records'] == 0,
             'R38 reviewer intake cannot authorize publication or safety clearance')
        # R39 preflight verifies the entire zero-annotation R37 -> R38 -> R39
        # challenge contract on the real checkout. No signing key is present,
        # no identity is asserted, and no human reviews are marked done.
        challenge = build_private_key_receipt_challenge(
            reviewer_csv, reviewer_csv['csv_tables'])
        need(challenge['release_state'] == 'HOLD'
             and challenge['unverified_progress_records'] == 0
             and challenge['parent_R37_fingerprint_sha256'] ==
                 reviewer_csv['manifest']['fingerprint_sha256']
             and challenge['parent_R38_fingerprint_sha256'] ==
                 quarantined['manifest']['fingerprint_sha256']
             and challenge['may_publish'] is False
             and challenge['qualified_safety_clearance'] is False
             and challenge['independent_QD_approval'] is False
             and challenge['human_source_reviews_completed'] is False,
             'R39 unsigned receipt challenge must remain zero-progress HOLD')
        # R40 binds the same frozen real-corpus R37/R38/R39 challenge and
        # guarantees the machine has NOT fabricated a signed human receipt.
        # Recent signed segments are separately audited only with external
        # trusted start/end anchors, keyring, clock and nonce replay registry.
        unsigned_baseline = build_recent_transcript_unsigned_preflight(
            reviewer_csv, challenge)
        need(unsigned_baseline['release_state'] == 'HOLD'
             and unsigned_baseline['verified_human_receipts'] == 0
             and unsigned_baseline['key_possession_verified'] is False
             and unsigned_baseline['reviewer_real_identity_verified'] is False
             and unsigned_baseline['parent_R37_fingerprint_sha256'] ==
                 reviewer_csv['manifest']['fingerprint_sha256']
             and unsigned_baseline['may_publish'] is False
             and unsigned_baseline['qualified_safety_clearance'] is False
             and unsigned_baseline['independent_QD_approval'] is False,
             'R40 machine baseline cannot certify real reviewer or release')
        # R41 protects the long-term original R40 full-evidence retention
        # contract WITHOUT inventing receipts or an authenticated human.
        # No durable ledger, external trust anchor or export is created here.
        history_baseline = build_history_unsigned_preflight(unsigned_baseline)
        need(history_baseline['release_state'] == 'HOLD'
             and history_baseline['archived_signed_receipt_records'] == 0
             and history_baseline['trusted_external_ledger_present'] is False
             and history_baseline['parent_R37_fingerprint_sha256'] ==
                 reviewer_csv['manifest']['fingerprint_sha256']
             and history_baseline['may_publish'] is False
             and history_baseline['qualified_safety_clearance'] is False
             and history_baseline['independent_QD_approval'] is False
             and history_baseline['human_source_reviews_completed'] is False,
             'R41 machine history cannot fabricate human review or release')
    return payload

def audit_checkout(root):
    root = Path(root)
    need(root.is_dir() and not root.is_symlink(), 'checkout unavailable or linked')
    root = root.resolve(strict=True)
    prep = root / 'preparedness'
    for part in ('taxonomy.json','sources/crosswalk.json','sources/register.json'):
        path = prep / part
        need(path.is_file() and not path.is_symlink() and
             path.resolve(strict=True).is_relative_to(prep), 'unsafe source input: ' + part)
    tool = prep / 'tools/build.py'
    need(tool.is_file() and not tool.is_symlink(), 'original renderer missing')
    spec = importlib.util.spec_from_file_location('preparedness_draft_build', tool)
    need(spec and spec.loader, 'renderer cannot be loaded')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return audit(module.Library(root=prep))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        print(json.dumps(audit_checkout(args.repo_root), sort_keys=True, ensure_ascii=False))
    except (ReviewHold, OSError, KeyError, TypeError, ValueError) as exc:
        print(f'citation source review HOLD: {exc}', file=sys.stderr)
        return 2
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
