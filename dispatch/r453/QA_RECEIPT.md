# Dispatch R453 — exact committed-source QA receipt

**Date:** 2026-11-18, sampled WordPress at 18:34:50–18:35 UTC. **Change set:** isolated `dispatch/r453/` on fresh review branch stacked on R452 #3026 exact starting head `52c3f79bf4f775e977c3e32ebe6e00bd2075bd4a`. Master six-issue PR #175, per-edition safety PR #201, frozen homepage PR #49 and all WordPress content untouched. Final branch commit is recorded in GitHub PR metadata.

## Test truthfulness — what actually ran

- **V8 directly executed pure-function logic:** 28 receipt/opt-in/revenue assertions on the initial `conversion_proof.mjs` functions; 17 mature-cohort assertions on the initial `cohort_math.mjs` functions; 11 subject/preheader assertions against **the actual R446 manifest content fetched by exact Git blob** (`bfd17cb9df915772ba317616b6d8ebf7b51b218e`). Total **56/56 V8 inline proof/logic assertions passed** in development. These are **not native Node test results**.
- **Final hardening after that execution:** Added five new signup dedup test cases, and upgraded the cohort proof predicate to require a source reference and checked-at field instead of a bare boolean. After those changes, all **nine final committed R453 source/data files were fetched independently**, their exact blob IDs recorded below, and **18/18 additional final-source structural/policy assertions passed**. The earlier 56 V8 checks cannot be passed off as execution of the final hardened code.
- **Committed regression test definitions:** `conversion_proof.test.mjs` has **38** Node test declarations, `cohort_math.test.mjs` has **18**, `subject_preheader_gate.test.mjs` has **11** (**67 defined total**). **Native Node test execution did not occur** in this sprint. The reliable way to close this remaining test gap is checkout this exact branch and run `node --test dispatch/r453/*.test.mjs` in CI or a trusted local checkout, recording exit status against the exact final commit.
- No genuine Jetpack sender preview, inbox receipt, email client screenshot, new confirmation event, paid checkout or settlement was witnessed. Static modules are source-only and do not constitute customer-facing production instrumentation.

## Independently fetched final Git blob identities

| File within `dispatch/r453/` | Exact Git blob SHA |
|---|---|
| `conversion_proof.mjs` | `a931aa1b195aed28b4e75310df0c82863ca1e3b3` |
| `conversion_proof.test.mjs` | `0e3e0de14da3c57d5473573a796e385d1964cf64` |
| `cohort_math.mjs` | `2686cb0d1bd60fc42ddb9dfcaa30153fee16582e` |
| `cohort_math.test.mjs` | `edc7d69e248f9d95c52b7eb0f1ad5995d4f32a47` |
| `subject_preheader_gate.mjs` | `3772427637ccb2e54950b724245a329f7a7eeed0` |
| `subject_preheader_gate.test.mjs` | `53e5003b4c0f6336f4d01987f32046b6deabb86a` |
| `PROOF_FIRST_CONVERSION_HANDOFF.md` | `a29f2d89169e944b459d2803db809c33f09f6da2` |
| `MERCHANT_AND_EMAIL_ENVELOPE_REVIEW.md` | `733fc2b41907eb08e77ca4dae77c28f56021d9ea` |
| `LIVE_AGGREGATE_ONLY_20261118.json` | `7a76eafca08745ee4d21877706d6812c265a2599` |

## Source-authenticated findings, not manufactured outcomes

1. **Actual R446 alternate metadata bug:** Source manifest has **4 of 6 alternative subject/preheader pairs** with literal leading `** ` Markdown markers: issues **01, 02, 05, 06**. All six original metadata pairs passed static envelope formatting checks. Corrected human-review text is in `MERCHANT_AND_EMAIL_ENVELOPE_REVIEW.md`. **No original subject/manuscript was edited.** Real subject and preheader render remains unverified.
2. **Newsletter audience buckets contradict:** 3 confirmed/3 source-classified email subscribers; 2 additional unconfirmed excluded; independent Followers surface says email 0 and Reader 3, while Stats Subscriber filter says Reader 0. Both category axes conflict. No actual new lead, delivered welcome or unique reader population may be inferred. `reply_to=no-reply`, `email_content_format=full`, new-post default OFF, newest five posts `never_sent_opted_out`. No current post-email Stats rows.
3. **Official merchant/FTC:** Zen12 standard page claims and special `/secret/` countdown/coupon funnel differ. Hypnosis Live seller FAQ states MP3/refund terms; neither establishes affiliate EMAIL-channel permission, exact FV earning link, product-specific independent efficacy or honored merchant checkout. FTC commercial-mail address/unsubscribe obligations remain unverified at **actual native email rendering**.
4. **Demand/outcome evidence:** Zero audited sales ledgers, human-session denominator, valid attribution proof or mature paid cohorts provided in this sprint. This is **absence of verifiable information, not proof of zero sales**. The code's positive numbers are expressly synthetic unit-test data, never FV observed revenue.
5. **No action on recipients:** No emails, including test sends; no recipients contacted, WordPress writes, list imports, new signup account, affiliate link activated, live merchant checkout, spending or merge.

## Owner handoff and required follow-up

**Dispatch/Founder:** choose exact editorial variant; resolve contaminated proposed subject metadata; witness genuine native non-sending Jetpack Preview including legal mailer footer; provide FV-owned validated postal address; do not paste reviewer-only notes into any full-content post. **Focus/Claude:** reconcile two contradictory Jetpack Stats category surfaces privately and observe a new, provider-confirmed subscription and actual 52-page welcome receipt only under a separately authorized safe witness. **Mind/Commerce:** obtain account-specific named Zen12/Hypnosis Live partner approval, **EMAIL** marketing rights, real approved published guide, issued earning URL and verified current checkout/refund proof. **Grok/Praxxis/Claude:** supply valid source asset IDs + authorized qualified-human analytics and independently linked paid settlement ledger. **All:** maintain original 4:2 and `HOLD_UNSENT`.

**Release gate:** still closed. **Commercial KPI:** realized net revenue/1,000 qualified humans **NOT COMPUTABLE**; no fabricated A/B inference.
