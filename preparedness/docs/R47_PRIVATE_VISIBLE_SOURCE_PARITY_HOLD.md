# Preparedness R47 — visible evidence parity / PRIVATE HOLD

**Issue:** #136. **Scope:** only Preparedness Archive private review tooling; stacked on frozen R46 PR #471. No homepage, navigation, original article, water tool, original source record, taxonomy, publication or WordPress change.

## R47 threat model

R44 proves a reviewer ZIP matches a trusted package digest. R45/R46 check inert DOM, source-content control characters, warning placement and internal links. Neither separately verifies each browser-visible review cell against the independently pinned original article-level R42 source packet. A changed/re-rendered private HTML document may retain plausible structure, counts, a source warning and even a newly recomputed package hash while replacing an original source-reading quotation or altering a contributor-specific scope.

The independent R47 HTMLParser audit compares the actual visible field names and literal values for every R42 dossier source-record row against all 36 private article/tool HTML pages. It separately checks all 30 cited/uncited global shared-source groups, per-article taxonomy status as recorded NOT approval, fingerprint/identity and safety review requirements, exact title/HOLD warning and disclaimer, complete index titles and claim-count labels.

R47 does not deduplicate URL variants or collapse original scope records, and does not normalize, rewrite, truncate, silently repair or approve evidence.

## Release boundaries

- audit_visible_evidence_rows requires an externally pinned R42 fingerprint and R43 HTML manifest fingerprint. The mandatory machine preflight uses fingerprints derived from the same frozen checkout only as internal consistency tests. External provenance is not established merely by self-hashing.
- Source verification, factual accuracy, professional emergency-safety assessment, reviewer identity, accessible current links, rendered browser testing and independent QD remain NOT_STARTED / HOLD.
- Offline review pages and private ZIP remain in RAM. CI never persists or distributes human evidence and never publishes to WordPress or changes navigation.
- Any failures abort the mandatory private citation/source gate; no synthetic approvals.
- New independent synthetic tests exercise changed claim fields, source reading scopes, fallbacks, shared URL variants, metadata, misleading index counts, URLs embedded as inert text, reordering/omission and safety-warning parity.
- Original seven contributor refs, independent QA PR #157, fixture PR #169 and homepage work remain separate. Human QD must review any integration; no auto-merge.

## Running

For a checkout with Python 3.12, run:

- python -I preparedness/tools/validate.py
- python -I preparedness/tools/build.py
- python -I -m unittest discover -s preparedness/tests -p 'test*.py'
- python -I preparedness/tools/citation_fallback_review_gate.py

The private GitHub workflow is the existing mandatory 13-stage pipeline. A passing machine run does not grant release permission.
