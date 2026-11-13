# Dispatch R329 — first genuine-inbox evidence gate and one-offer revenue contract

**Isolated, draft, NON-SENDING, unmerged.** Base: R328 preview PR #2337 at `6bf50815fcdd6f170bd30e963d6d9140c4cc120b`. Source manuscript master: #175 at `d57ccdba3aee8f065e143e101c2945f4f3d01647`. This folder is additive; no canonical email or WordPress code changed. Links in the original commercial letters remain disabled, and original alternative manuscripts remain NOT_ADOPTED.

## Why R329 exists
R328 already solved source-preserving static previews. The major launch blocker is **not** email HTML volume: actual Jetpack received-message rendering, publisher-owned legal mailing address, functional unsubscribe, provider-origin subscriber eligibility and commercial affiliate rights cannot be inferred from local previews. R329 develops acceptance evidence and one high-intent offer experiment without inventing any success.

## Files
- `receipt_guard.cjs`: privacy-safe **read-only** RFC822 MIME header/body presence inspector, fail-closed; never sends, logs, imports, activates or derives subscribers/revenue. Returns `HOLD_UNSENT` in ALL circumstances. Does not claim that headers alone prove functional opt-out.
- `receipt_guard.test.cjs`: synthetic/adversarial native Node test suite, also run in isolated V8.
- `RECEIPT_AND_CONSENT_RUNBOOK.md`: actual Jetpack email-client, welcome and privacy witness protocol, awaiting separate founder authorization.
- `MERCHANT_OFFER_AND_PRICE_DRIFT.md`: official seller-specific Zen12 and Total Focus evidence, second-list consent, differing Total Focus displayed prices and written approval obligations.
- `SINGLE_OFFER_CONVERSION_CONTRACT.md`: source-tagged one-offer conversion hypothesis with 7-/30-day cohorts; no more messages, no invented subscriber identities or orders.
- `evidence_attestations_all_unverified.json`: factual snapshot and zero-commercial-attestation ledger; intentionally no personal data.
- `QA_AND_CANONICAL_SUBJECT_REVIEW.md`: honest six-issue editorial strengths/gaps, original Python rerun and exact-source V8 findings.

## Verification
- Native original master suite: `python -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_*.py' -v` → 6/6 PASS using prior archived files whose four sampled Git blob SHA values re-matched today's live PR #175.
- R329 committed guard test: exact committed JS bytes loaded through GitHub fetch in V8/CommonJS harness → 23/23 PASS after one test expectation correction. Native Node execution of R329 source is *not* attested in this PR.
- All-FALSE external attestation ledger: no valid commercial release conclusions; missing evidence includes postal address and actual authorized commercial inbox.
- The input fixture is **fabricated synthetic** and its domains/addresses are invalid. It is not actual received email. Never store a real receipt on a public branch.
- No public/production writes, messages, test sends, list changes, new platforms or spending.

## Standard release logic
1. Provide product-rights/claims/guide/checkout evidence **via Mind/Commerce owner #171** (individually per commercial issue).
2. Independently substantiate Final Vestige postal address, actual received Jetpack HTML/plaintext/subject, unsubscribe functionality and welcome receipt when *separately* authorized.
3. Reconcile subscriber eligibility read-only from authenticated provider; no counting Reader followers, PDF opens or merchant newsletter signups as confirmed leads.
4. Obtain explicit founder approval for copy, audience and schedule; none was given.
5. Only then may another agent plan release outside this PR. This code itself can NEVER authorize sending.

Owner/issues: Dispatch #174, Focus #129, Mind #171, conversion #820. Homepage flagship #150 and frozen PR #49 untouched.

References: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174 | https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2337 | https://finalvestige.com/editorial-standards/ | https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
