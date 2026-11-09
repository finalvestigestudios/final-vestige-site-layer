# R246 — Article #15 / Tool #104 source-to-privacy-claim custody

**2026-11-09 PT.** Preparedness-only Issue #136. Commercial cross-reference #820, charter #818, Grok/Praxxis TASK-008. **DRAFT / HARD HOLD; unpublished.** This is a reproducible source-assertion *review docket*, NOT a privacy audit of the live site, WordPress safety certification, QD PASS or commercial authorization.

## Authenticated originals held without alteration

- Article #15 `content/articles/family-communication-plan.body.html` Git blob `8ac8bd7dba3be15d477c15737e54d83364d72527`.
- Companion Tool #104 `content/tools/family-reunification-card.body.html` `be8698ac5d020476ff649d85813810e2000c6f98`; metadata `47da1e7e20e39f0ea85e26d54a8d58301f6e0a15`.
- Existing pure-JS logic `tools/reunion_card.js` `b1a09b1eda1ae26f081de65b400a37bc19538035`; shared helper `tools/shelter_common.js` `efe1c7910d99437e3687621dabab8ce55dc24fd4`.

All five authenticated GitHub versions were read independently, and the **exact original JavaScript** from the latter two source files was evaluated in an isolated V8 function scope with **fictitious sample values only**. The `rcModel(sample, true)` front rows were Household TEST HOUSEHOLD, Phone 555-0101, Out-of-area contact TEST CONTACT, Out-of-area phone 555-0102, and Meet first at LIBRARY. The back included Reviewed 2026-11-09 and Details “Kept in our written plan at home.” The input's school/caregiver/access fields were excluded. This directly demonstrates the model's minimal mode still includes optional household identifiers, *not* a live printer or full site test.

## Seven precise held source/claim witnesses

1. Article #15 says the tool “keeps what you type on your own device” — absolute environment/privacy claim pending browser/CMS/session/storage/print verification.
2. Tool #104 says “It is not sent or saved. Closing the tab clears it” — absolute promise not substantiated by a whole-site/browser audit. No evidence of actual exfiltration has been observed.
3. Tool introduction says minimal “prints only the out-of-area contact, a phone and the first meeting place,” omitting household name and household phone present in the executed model when entered.
4. Tool checkbox says “only” out-of-area contact, phone, first meeting place and review date; same omission.
5. Tool metadata says “Nothing is stored”; broader WordPress/analytics/autofill/browser/print behavior not audited.
6. Original JS `rcModel` front rows unconditionally include user-entered household name and phone in minimal mode; needs either deliberate copy correction with proper privacy warning or code correction after separate editorial decision and testing.
7. Original JS minimal back unconditionally asserts a written home plan exists; no such user input is required.

The gate preserves these as **unresolved**. It will reject unexpected changes to any of the five source blobs, the article-to-tool link, Tool #104 citation, metadata state, or the seven review witnesses until a reviewer explicitly refreshes the custody docket. Merely retaining the witness or matching its hash **does not mean the statement is true**. No user/personal values are retained in receipts.

## Engineering / testing

- New `tools/r246_family_card_claim_custody_hold.py` returns a seven-witness, five-source SHA-256 custody receipt with every source, privacy, medical, publication, merchant, and independent-QD approval **false**; original inputs read only. Imported from an authenticated Git blob by R220 and invoked before any WordPress producer.
- New `tests/test_r246_family_card_claim_custody_hold.py`: **67/67 locally executed Python unit tests PASS**, covering 55 source-mutation tests, citation/link deletion, duplicate metadata keys, type/state violations, no zero bytes, determinism, and preservation of all review/approval holds. `python -I -m py_compile` PASS. Exact local test/module Git-object IDs compared with committed GitHub blob IDs. **These are synthetic fixture tests, not the full native suite.**
- R220 loader pins the new gate and re-verifies its source identity after audit. Existing R200/R219 citation provenance, 35 article bodies, 2,000-citation inherited baseline, six tools, 41 frozen routes, WordPress draft export guards and all review holds remain unchanged.
- **NOT RUN:** native `python -I preparedness/tools/validate.py`, native `build.py`, inherited repository suite, original full-corpus Python audit, authenticated WordPress export/browser/network/storage testing. Local network cannot resolve github.com for an authorized native checkout. Connected GitHub read does not substitute for the native run.
- Outstanding shared-source review: **32 groups / three original disputed citation occurrences** (two CDC references in #7; one Ready.gov in #20). Preserve separate independent QA #157 and isolated test-fixture #169; neither is a release authorization.

## Source-safety review ownership

**Preparedness Editorial / independent QA:** Decide truthful, narrow privacy copy for Article #15, Tool #104 body and metadata, plus exact minimal-mode disclosure and genuine JS-off/printed-card behavior. Verify whether inputs are recorded, transmitted, cached, persisted in forms/browser memory, or exposed by printing; do not infer total-site behavior from pure helper code. Confirm the conditional warnings do not warn about fields suppressed from minimal printout. Do not quietly rewrite existing frozen source files or adopt safety-approved labels from metadata as independent authorization.

**Integration:** Once editors submit reviewed, exact Git blobs and corresponding documented claim/risk decisions, deliberately update source pins, integration chain and all associated tests in a separate draft PR; retain pending human-QD/source review.

## Conversion-first OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

| Offer | Step | Blocker | Change/experiment | Evidence/status | Owner |
|---|---|---|---|---|---|
| Free Article #15 / Tool #104 | Existing social visitor → useful free guide | Misleading minimal and unverified privacy assertions may undermine trust | Resolve seven editorial witnesses and verify genuine mobile/no-JS behavior *before* creator promotion | Authentic JS result + original source witness **TESTED IN ISOLATION / HARD HOLD**; no live browser proof | Preparedness Editorial + QA |
| Existing free Archive | Existing Grok/Praxxis asset → landing | No validated household-contact asset_id, rights, native mobile tap path or campaign tag | TASK-008 research-only matching of **already published** creator asset to free official-source page | **UNVERIFIED** | Grok/Praxxis |
| Provisional existing Legacy Triage ($19 advertised previously) | Free guide → optional practical digital pack | The pack is estate/incapacity oriented; rights, privacy suitability, checkout, delivery/refunds unverified | Founder/Commerce audit actual PDF and authorize only after fit, safety, delivery verified | **NOT APPROVED** — no CTA activation | Founder/Commerce |
| Existing paid offer, if later approved | Checkout → completed paid order | No authorized confirmed transaction or merchant settlement | Inspect permitted merchant confirmation/refund/fee evidence, without dummy buyer or test charges | **NOT TESTED** | Commerce |
| Confirmed qualified sessions | Orders → realized net revenue | No attributed paid orders / qualified-human denominator | 7-/30-day consent-compliant cohort reconciliation only after trusted signal | **NOT COMPUTABLE** (not zero) | Claude analytics/Commerce |

**No new product, paywall, water freebie, paid CTA, affiliate activation, signup, tracking script, CMS/navigation/homepage write, social post, email, merge, release, or spend.** Revenue per 1,000 qualified-human sessions remains NOT COMPUTABLE. Founder retains any commercial and production authorization.
