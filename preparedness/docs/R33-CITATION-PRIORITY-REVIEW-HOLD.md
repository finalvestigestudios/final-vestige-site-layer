# R33 — Lossless citation-by-citation human review order (DRAFT / HOLD)

Issue #136. Isolated draft on R32 `e08905d3f47cf5497bec981a82ce0d0d605e3fa0`. **Do not merge/publish or edit the WordPress CMS/navigation.** Nothing here is source verification, clinical/emergency safety approval, or independent QD PASS.

## Why this exists

The R25 evidence packet and R31 review index account for 35 articles, one water-planning tool, 1,959 citation occurrences, 367 unique article-source relationships, 43 cross-cluster base-fallback relationships, and 30 unresolved shared-source URL groups. Their necessary structural validation does not tell a human reviewer **which individual contexts to inspect first**. Repeated citations must not disappear behind URL or source-ID deduplication.

R33 builds one cryptographically bound reviewer task for **each original citation occurrence**: original slug/source ID, zero-based Unicode codepoint offset, full bounded citation context, context SHA-256, frozen article-body SHA-256, original contributor source-record SHA-256, original per-article source-use SHA-256, the preserved source URL/origin, and the individual task digest. Deterministic sort places potentially consequential review contexts before standard contexts, without changing any editorial content.

The first-review keyword categories are water/chemicals, food preservation, fire/combustion, medication/medical dependency, and children/accessibility, plus **all** original shared-source and contributor-fallback relationships. These are **high-recall triage suggestions**, not medical advice, link verification, an authoritative hazard classifier, or a statement that unflagged content is safe. A human must inspect **every** citation occurrence, including `STANDARD_REVIEW` items. Each result remains `PENDING_INDEPENDENT_CLAIM_AND_SAFETY_REVIEW`; all clearance flags remain literally false.

The new validator enforces the R25 and R31 canonical SHA-256 receipts, their parent/child binding, exact frozen population totals, citation-offset uniqueness, per-article relationship and occurrence parity, source/reading-depth/body digests and no fabricated approvals. It is invoked from the existing mandatory **13th** preflight stage; it does not add a publishing stage or change the 13-stage contract.

## Private reviewer export only (stdout, no files or network writes)

From a trusted, locally available checkout at the exact R33 commit:

```sh
python -I -B preparedness/tools/citation_occurrence_priority_gate.py --format summary
python -I -B preparedness/tools/citation_occurrence_priority_gate.py --format ndjson > PRIVATE_R33_claim_review.ndjson
python -I -B preparedness/tools/citation_occurrence_priority_gate.py --format json > PRIVATE_R33_claim_review.json
```

The shell redirects stdout only if a private reviewer chooses to save an offline queue. Do not commit exports containing complete claim excerpts to a public repository, publish them, or treat their presence as evidence of human completion. Reopen original R25 contributor-specific full reading notes and original article at the frozen hashes to confirm any proposed change.

## Verification and outstanding work

New synthetic suite: **99 passed locally** against the reconstructed R29/R30 parser/evidence modules and an explicitly labeled *local-only R31-shaped stand-in*. This is **not a full trusted checkout** and does not establish current remote native CI PASS. Production and test files were independently compared byte-for-byte with GitHub blobs; follow the actual hosted CI result before recording a native green claim.

Independent QA PR #157 and synthetic-fixture PR #169 remain separate. All seven Claude source branches and homepage PR #49/#254 must be rechecked each run; R33 modifies none of them. Preserve the unresolved original source README/repeated-ID tension and the known food-source provenance discrepancy.

**Release: HOLD.** Human assessment of all individual claims, 30 shared URL groups, 43 fallbacks, qualified review of consequential emergency guidance, rendered-browser review, and independent QD approval remain required even after every machine gate succeeds.
