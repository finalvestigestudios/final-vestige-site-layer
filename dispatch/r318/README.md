# FV Dispatch R318 — Source-of-truth subscriber → customer audit

**Status:** source-controlled, review-only, no sends, no scheduled issues, no WordPress/editor/merchant/social/analytics deployment. Stacked on **R317 draft #2271**, not on homepage frozen PR #49. Original **six-issue campaign #175** and prior QA #201 are unchanged; this branch contains additional `dispatch/r318/*` files only. Owner #174; partner #171; Focus #129; conversion #820.

## What is genuinely new

1. **Live-anchored cross-channel snapshot:** authenticated Jetpack newsletter and separate follower count, read-only /dispatch/, /focus/, Editorial Standards, source-of-truth official merchant pages. The public /focus/ UI visibly exposes a post-signup PDF download and asks for confirmation; **file access cannot be counted as confirmed email subscription**. Do not confuse the existence of a confirmation request with verified delivery/consent. See `EVIDENCE_SNAPSHOT_2026-11-13.json`.
2. **High-impact copy and destination audit** of **all six immutable original draft issues**, with precise issue-by-issue defect and founder decision; no seventh or substitute newsletter auto-adopted. See `SIX_ISSUE_DECISION_REVIEW.md`.
3. **Concrete one-offer authorization/technical inbox witness worksheet** distinguishing real private merchant terms and legal postal/unsubscribe from public sales/recruitment pages. See `MERCHANT_AND_INBOX_PROOF_REQUEST.md`.
4. **Pure, non-sending event classifier** enforcing actual provider-acknowledged email eligibility, exactly one opaque confirmed signup, no tracking pixels or subscriber PII, independent received/settled commerce records, fee/refund-adjusted net cash, zero-denominator=NULL and cohort boundaries. `proof_model.mjs` + `proof_model.test.mjs`.
5. `review_board.html` is an accessible offline decision surface. It is not a substitute for a Jetpack inbox preview.

## Repeatable tests and caveats

- Immutable #175 head confirmed GitHub `d57ccdba3aee8f065e143e101c2945f4f3d01647`; archived exact-source eight blobs have Git SHA fingerprints. Independently executed native Python `python -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_*.py' -v`: **6/6 pass** Nov 12 PT.
- R318 source model exercised by **21 V8 direct logic checks pass (21/21)** including negative tests for faked consent/UTM/sales/PII/refunds/cohorts. This is **NOT native Node/CI execution of the committed test module**; `proof_model.test.mjs` is committed for that future test.
- All real counts and source quotations are dated. This model verifies logical consistency of **supplied** provider attestations; it cannot verify those attestations are real. Live provider confirmations, merchant commissions, privacy-safe joins, actual campaign asset IDs and real qualified-human session counts remain UNKNOWN.
- A numerical example in test fixtures is **SYNTHETIC**, never business revenue. Site-level realized net/1000 qualified-human sessions remains **NOT COMPUTABLE**, not zero.

## Non-negotiable release state

01/02/03/04/05/06 `HOLD_UNSENT`. 03/05 `HOLD_MERCHANT`. All optional prior editions `NOT_ADOPTED`. No send/test send, publisher draft, post, plugin, newsletter settings, subscriber manipulation, tracking pixel, affiliate activation, social posting or spend. Founder approval is required to change that.

[GitHub issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) · [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171) · [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129) · [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).
