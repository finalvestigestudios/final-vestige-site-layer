# Preparedness R238 — quote-aware source-citation visibility HOLD (2026-11-09 PT)

**Source of truth:** #136, #820, #818. **DRAFT_HARD_HOLD. No merge, WordPress/CMS, navigation, public, email, analytics, social, merchant, affiliate or spending changes.**

## Finding and regression

The R237 citation context gate used `rfind('<') > rfind('>')` to decide whether a token sat inside a markup tag. With a `>` character inside a **quoted HTML attribute**, the final greater-than symbol occurs after the tag opener but before the marker; that test incorrectly labels an attribute-only citation reader-visible. The exact syntactic counterexample is `<p data-note="plain > {{cite:ready-plan}}">Not a real citation</p>`. An isolated negative-control execution reproduced acceptance under that prior lexical rule; R238 rejects it. Similarly, a misleading `>` inside an unterminated comment, hidden elements, or nested `<template>` must not turn evidence into visible citations.

R238 adds a **separate Git-blob-pinned, fail-closed source lexer** that parses quoted tags without treating `>` inside a quote as a tag boundary. It rejects citations in tag attributes, comments, opaque/nonreader sections, hidden/aria-hidden/inert/display-none subtrees, malformed syntax and nested templates requiring browser review. It preserves original R237 claim-context receipts and all earlier R220–R237 gates. This is a conservative syntax screen, **NOT** a complete HTML5 browser proof, claim-support validation, medical safety assessment, or independent QD approval.

**Committed exact blob identities:** R238 module `694bbb23bcadb16169d783a0352b790f3629e4f6`; R238 tests `e0180061f216360905f043877e220d72d15a0494`. R220 integrated loader binds the new module blob, checks 35 articles / 2,000 markers and false approval flags, and rechecks the loader blob after source audit. Existing manuscript/source/taxonomy/canonical IDs and all seven contributor branches remain read-only.

## Evidence and limitations

- Python `-I -m unittest discover -s ...` on **exact Git-blob-matching R238 local source and tests:** **162/162 PASS** (140 per-article-equivalent matrix cases and 22 controls); `py_compile` passed. Includes tag attributes containing `>`, comments with `>`, hidden containers, positive visible-citation checks, nested templates, no-publish flags.
- **Read-only authenticated GitHub connector** inspected all 35 original integrated body HTML files at parent R237 SHA `3ba9a4e306244c34747918ce1725f8d502af2dd0`. A separate JavaScript port of the R238 lexical scan reported **35/35 parse successes, 2,000 citations (18 articles / 1,137; 17 articles / 863)**. This is NOT execution of the exact Python gate on the authentic checkout; count alone does not prove claim correctness.
- Original frozen contributor SHAs were checked against current seven Claude branch names with same-ref GitHub comparisons; **all 7 status identical, 0 ahead/behind**: start `2122d856fce9f64887c16df3d52e64be9f59a55b`; shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; hist-field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; hist-food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; hist-home `7504a5f099594d635e3dd7332a33a2e1346c43a2`.
- Independent QA #157 **draft/head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`**, synthetic fixture #169 **draft/head `e9cd7766dac59d47ab467d8945269b9146c2aef5`**, homepage #1689 **draft/head `f55c36b6598eec558dd8bb24e4c8988becc51be0`** inspected, not modified.
- Full native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, `python -I -m unittest discover -s preparedness/tests -v` and all true WordPress/preview outputs **NOT EXECUTED**: local shell cannot resolve `github.com` to obtain a trusted complete checkout. Do not infer pass from isolated synthetic testing.
- **Source and safety HOLD persists:** 32 shared-source scope groups need human adjudication, plus two original disputed source groups / three original occurrences (Article 7 CDC twice, Article 20 Ready.gov once). Special caution for water safety, drugs/devices, food and electricity-dependent households. Risk vocabulary, author notes, and structural checks do not certify claims.

## Scoped conversion-first handoff (no paid CTA)

**Existing free guide:** `https://finalvestige.com/preparedness/` official resource index, accessible without purchase or email. **High-intent candidate:** household out-of-area contact and essential-document planning. Actual published Grok asset ID, post URL/date/hook, rights, `utm_content`, in-app mobile destination and relevant qualified-human denominator remain **UNVERIFIED**; Praxxis/Grok TASK-008 should reconcile an existing post, **not** add assignments to Grok's queue.

**Single provisional optional existing offer:** Legacy Triage, listed $19 PDF, primarily estate/incapacity paperwork — **not a verified disaster-readiness toolkit**. Founder/Commerce must independently verify current ownership/rights, product and audience fit, contents, storage/privacy statements, merchant acceptance, checkout, PDF delivery, refunds, and consent/disclosure before any promotion. No new product or retired water freebie.

**Draft text only:** “Make a plan everyone in your household can find. Start with our free emergency planning references.” Optional paid explanation only *after* authorization: “Legacy Triage: organizing estate and incapacity records — optional paid PDF, not an emergency response guide.” Never add merchant link while gated.

**OFFER → STEP → BLOCKER → CHECK → EVIDENCE → OWNER:**
1. Free official-resource index → social visit → published Grok asset/UTM/mobile continuity unknown → reconcile actual existing post in TASK-008 → UNVERIFIED → Grok/Praxxis.
2. Free guide → detailed original manuscripts → native build/claim/safety review not complete → run full native suite and editorial signoff → HARD HOLD → Preparedness/Independent QA.
3. Guide → optional paid Legacy Triage → fit, rights and privacy unproven → examine actual PDF and merchant authorizations → NOT APPROVED → Founder/Commerce.
4. Paid detail → actual paid order → checkout, delivery, refunds unverified → permitted end-to-end transaction check → NOT TESTED → Commerce.
5. Paid orders → net revenue/1k qualified humans → reconciled orders, costs, fees/refunds and attribution absent → separately verify 7/30-day cohorts → NOT COMPUTABLE → Analytics/Commerce.

**Strict custody:** this draft PR changes only paths under `preparedness/`. No publishing, merging, CMS, nav, merchant, email, social content, tracking scripts or paid services. R238 cannot authorize release.