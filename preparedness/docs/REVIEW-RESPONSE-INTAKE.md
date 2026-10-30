# Preparedness Archive: Human Review Response Intake (DRAFT / HOLD)

**Scope:** Issue #136; source/citation gates only. Additive to the hash-bound reviewer request packets in draft PR #200. The program processes **human self-reported observations**, never verified approvals. It does not edit articles, crosswalks, sources, metadata, WordPress, homepage, subscriber list, or public navigation.

## What this closes

PR #200 generates an immutable citation review request for each article/source use and a group packet for each duplicated-source URL. Until now, there was no structured way to record an editor's observations without risking that the responses were mistakenly treated as human approval or independently verified safety evidence.

This new offline, read-only utility accepts reviewer observations only when they correspond to the **exact current source-review manifest** and exact per-request SHA-256. A changed article body, contributor reading-scope note, citation, source URL, or source packet changes the manifest and invalidates earlier submissions. It rejects extra or missing fields, duplicate request records, duplicate JSON keys, malformed dates, oversized or symlinked input, non-HTTPS observations, inconsistent link status versus source locator, and missing individual row reviews within a shared-URL group.

All outputs remain release_state HOLD and may_publish false; no reviewer's stated name is authenticated; no specialist credential verification is performed. Even if a reviewer reports a source as reached and a claim as supported, the output is marked REVIEWER_REPORT_RECORDED_UNVERIFIED. Unvisited sources, redirects, contradictory evidence, uncertain findings, and flagged water/food/medical/infant/fire/CO or historical-method advice enter FOLLOW_UP_REQUIRED, not approval. Shared-source groups retain all separate contributor reading scopes; observed consistency never rewrites or resolves the crosswalk.

## Existing project and related independent QA

The integrated corpus contains 35 complete long-form unpublished article drafts and one separate water-planning draft. Seven original Claude cluster heads were reconciled in PR #176, reinforced by input-freeze PR #179, Start Here copy/citation PR #186, deterministic source queue PR #193, and hash-bound packets PR #200. Independent Start Here safety PR #157 and food fixture-isolation PR #169 were inspected, not merged or overwritten. Their intended protections have already been represented in the integration stack, while stronger modern safety gates were preserved. Upstream is frozen at PR #200 SHA e7926676731b7853eb314f8b214ec10373270164. Homepage PR #49 remains separately frozen.

## Usage on a trusted exact checkout

1. Run existing validators and tests independently:
   
   python -I preparedness/tools/evidence_freeze.py
   python -I preparedness/tools/validate.py
   python -I preparedness/tools/build.py
   python -I -m unittest discover -s preparedness/tests -v

2. Generate reviewer request packets to the ONLY allowed file build subtree:

   python -I preparedness/tools/review_receipts.py --out-dir preparedness/build/review-packets

3. Print a safely blank response scaffold bound to the current manifest (no prefilled approvals):

   python -I preparedness/tools/review_response_audit.py --emit-empty-template > preparedness/build/review-packets/response-intake.json

4. A human reviewer reads **actual sources** and manually adds entries to citation_responses and shared_url_responses in the response JSON. Reviewers record actual check date, any redirect, URL, exact source locator/page, claim-level support or contradiction, reading limitations, and affected safety topics. Groups must include all physically distinct contributor rows; unread rows are explicitly NOT_INSPECTED.

5. Re-run the intake with the local response file:

   python -I preparedness/tools/review_response_audit.py --responses preparedness/build/review-packets/response-intake.json > preparedness/build/review-packets/review-triage.json

6. Optional human-input completion check:

   python -I preparedness/tools/review_response_audit.py --responses preparedness/build/review-packets/response-intake.json --require-complete-input

   A 1 means incomplete response fields; 2 means invalid input. **A 0 does NOT mean safe, approved, source-verified, independently QA-passed, or publishable**. The triage output keeps HOLD in all cases.

The intake tool itself writes to standard output only; any files produced by redirecting the output are the operator's responsibility. Human reviewer notes may contain names, privately obtained records, copyrighted excerpts, or sensitive observations; do not upload these into public WordPress content, mail campaigns, or public GitHub PRs.

## Schema summary

At the top level, exactly: schema_version=1, manifest_sha256, citation_responses array, shared_url_responses array. Each citation response uses exactly these fields:
- review_request_sha256, reviewer, reviewed_on (ISO date, no future date);
- link_check: REACHED_SOURCE / REDIRECTED_SOURCE / NOT_REACHABLE / NOT_ATTEMPTED;
- observed_url (HTTPS when reached, otherwise null); source_locator (precise page/section when reached, otherwise empty);
- claim_check: SUPPORTED_IN_INSPECTED_SCOPE / CONTRADICTED / UNCERTAIN / NOT_CHECKED;
- evidence_notes, reading_limits, risk_flags (zero or more of WATER, FOOD, MEDICINE, INFANT, POWER_CO, FIRE, SHELTER, HISTORICAL_METHOD, OTHER).

A shared URL response uses exactly packet_sha256, reviewer, reviewed_on, url, row_reviews, relationship, comparison_notes. Each row uses exactly source_row_key, reading_status=INSPECTED/NOT_INSPECTED, source_locator and reading_notes. relationship is CONSISTENT_LIMITED_SCOPES, CONFLICTING_SCOPES or UNRESOLVED. Any NOT_INSPECTED row prevents a claim of consistency. No keys such as safe, approved, released or may_publish may appear.

## Verification evidence and absolute boundaries

The additive PR contains only three Preparedness files: utility, 76 self-contained synthetic adversarial unittest methods and this documentation. On October 30, 2026 the exact authored source and test Git blob IDs were compared against local tested files: utility 64328842d10f090d20ff890034b33435053b29a6; tests eb537db965b9e9abb653d8911fe89663af89ad31. **138 local Python tests actually passed** across the intake, prior hash-bound receipts and source-review queue synthetic modules. This is not the integrated 35-article full suite. Do not claim independent QD, human link checks, or medical/safety review because tests passed.

Current verified unresolved work inherited from PR #200: 224 source records (209 machine-dated), 186 literal source URLs, 30 shared-URL groups, 367 article/source citation pairs, 0 documented human source-link checks. Every article and tool is a DRAFT. Required before any public release: trusted exact-branch full validation/build/test execution; human URL/source section review and documented resolution of group scopes; independent review by qualified experts for potentially dangerous health, medication, food, water, CO, generator and infant guidance; editorial and accessibility QA; source rights verification; independent QD and specific founder approval. This utility does not bypass those gates.
