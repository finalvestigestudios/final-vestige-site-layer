# Preparedness R9 — per-occurrence reviewer evidence intake (DRAFT / HOLD)

**Ownership:** Preparedness Archive integration and citation/safety gates only. Issue #136. This PR stacks on unpublished R8 PR #226 at `741cd7fe3a5dc1ddda980c90c5fc38bc49ba96f7`. It does not modify the 35 long-form articles, water-planning tool, 224 physical source rows, content taxonomy or seven contributor branches. PR #157 and fixture PR #169 remain independent review inputs, not certifications.

## Why an additional gate is necessary

R8 found **1,959 visible citation occurrences** across **367 article/source pairs**. A review of a source URL or one broad `source_use` note cannot justify all independent claims in separate paragraphs. R9 routes strictly *self-reported* human observations to the **exact R8 `claim_request_sha256`**, contributor row, article body SHA, contextual text fingerprint, claim ordinal and supporting scope. It does not turn reviewer assertions into verified facts, safety clearance, editorial approval or a publishable article. R9 leaves all **30 shared-URL groups** unresolved regardless of apparent review agreement; two contributors referencing one URL retain separate physical-source identities.

### Guards implemented

- The R8 report must still say `HOLD`, `may_publish=false`, `verified_citation_claims=0`, `reviewed_claim_occurrences=0`, and have the frozen baseline of 36 drafts, 367 pairs, 224 physical rows, 30 shared-URL groups and 1,959 occurrences. Recompute the ordered inventory digest and **each individual review-request fingerprint**, including body, original evidence, source-use, source-support and reading-limits hashes. Enforce article occurrence continuity, unique identity, per-article source-pair totals, and correct contributor row prefixes.
- When supplied canonical physical source rows (mandatory in the CLI), **cross-check exact contributor row key, source origin/ID, literal URL, claimed support and reading limits**; a changed URL cannot pass merely because the old row key was retained. Short full-text claim excerpts must match their source-context SHA; long excerpts are explicitly marked **requiring full original article review**, never treated as complete evidence.
- Accept strictly defined self-report fields only: request SHA, reviewer label, review date, source access/redirect, observed HTTPS URL, inspected locator, claim assessment, anchored proposition quote from R8 paragraph excerpt, evidence basis, reading limitations, and risk flags. Reject stale IDs, false assertions of a successful source check, fabricated redirects, unsupported conclusions, missing locators, unanchored quotes, contradictory status states, extra `approved`/`publish` keys, fake dates and duplicate reviewer submissions (case-insensitive).
- Record disagreements separately and require reconciliation. A shared reviewer label is **not identity authentication**; two agreeing reviewers are **not independent verification**. Any contradiction, partial support, uncertainty, redirected/unreachable source, risk flag, or truncated paragraph context remains `FOLLOW_UP_REQUIRED` (or stronger disagreement status). Even a fully self-reported positive assessment remains `SELF_REPORTS_ONLY_NOT_VERIFIED` with no approval.
- Emit a deterministic private JSON queue with per-article coverage and unresolved-review counts, source row and URL, exact claim request ID, and report status. **All 35 articles and the planner remain unmodified drafts.** Outputs are restricted to a direct file in `preparedness/build/`; the source ledger tool rejects symlink/output traversal. No HTTP requests, WordPress API operations, original source edits, public output paths, navigation changes, billing or third-party analytics.

### Reproduce on a full trusted checkout at the exact PR SHA

```bash
python -I -m unittest discover -s preparedness/tests -p 'test_claim_occurrence_audit.py' -v
python -I -m unittest discover -s preparedness/tests -p 'test_claim_review_intake.py' -v
python -I preparedness/tools/evidence_freeze.py
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
mkdir -p preparedness/build
python -I preparedness/tools/claim_review_intake.py --json-out preparedness/build/private-R9-review-queue.json
python -I -m unittest discover -s preparedness/tests -v
```

For actual review responses, provide a **private locally stored** JSON object shaped like:

```json
{"schema_version":1,"parent_evidence_digest_sha256":"<exact R8 evidence_digest_sha256>","claim_responses":[]}
```

The empty array is intentional until actual human inspection. Do not invent reviewer responses or imply a machine generated reviewer identity. Use `--responses /private/path/review-response.json` for reviewer-provided data. Keep review files out of public WordPress and unprotected artifact hosting. The content of a reviewer form is **not** a qualified safety evaluation or permission to publish. Do not paste sensitive user information into self-reported notes.

### Local tests and honest limits (2026-10-30)

**180/180 Python tests passed locally** in a mirror with the precise inherited R8 source and tests: **99 new R9 tests plus 81 existing R8 tests**. Added a minimal import-path correction for inherited R8 tests so `python -I -m unittest discover -s preparedness/tests` can execute in isolated mode; no source article changes. The R9 CLI `--help` also executed under `python -I` after adding its own explicit import path. These tests are **synthetic/adversarial**, not a source check. The local environment cannot clone the private GitHub repository (DNS unavailable), so complete-corpus `validate.py`, `build.py`, all-repository tests and live 1,959-claim scanner **have not executed here**. Report input and canonical 224-row crosswalk must be run on the exact committed checkout; no test result represents independent human verification of external source URLs or consequential advice. Hosted CI and QD remain unverified. **Publication remains HOLD.**
