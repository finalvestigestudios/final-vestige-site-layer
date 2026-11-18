# Mind R465 — committed-source QA receipt and commercial release hold
**Date:** 2026-11-18 PT | **Branch:** `mind-r465-repetition-blindness-seller-gates-20261118`
**Exact pre-receipt reviewed HEAD:** `5105efeaea1f723ab5fb0350c967f38c3f40e8a1`.
**Scope:** only `mind/r465/` newly added files; no existing homepage, Mind hub, Dispatch, creator, analytics or CMS files changed.

## Actually executed in this run
Read exact committed GitHub file contents at the reviewed HEAD using authenticated repository reads and tested in the connected JavaScript V8 execution environment. **42/42 source-level assertions PASS**, with **6/6 intentionally unsafe in-memory mutations caught**. Initial test-harness matcher incorrectly referred to `pubmed.nih.gov`; its native Node test was corrected to `pubmed.ncbi.nlm.nih.gov` and source checks rerun, 42/42. The error was in a test matcher, not the manuscript's URLs.

Coverage: both Zen12 A/B HTML variants contain inert disabled purchase controls, clear adjacent commission disclosure, no earning URL, no form/script/iframe/autoplay; A/B substantive section text matches byte-for-byte across five sections; B optional source-only SVG and readable transcript; six WebVTT cues ending at 42.000 seconds; 27 claim decisions including a conflicting primary psychological study; 15 closed commercial gates, no authenticated paid order or qualified-session denominator; verified existing Focus and Puységur navigation; 1,835-word original cited article with seven PubMed primary-science URLs and counterevidence; privacy-separated `affiliate_click` versus merchant-confirmed purchase and refunds. No fake partner acceptance or sale.

**Committed readback blob SHAs (GitHub):**
- `THE_WORD_YOU_SAW_TWICE.md` — `419aaf573b43d75ac98eb356ef645d832c39742f`
- `ZEN12_A_BUYER_GUIDE.html` — `208ea5eaf20e59cd018ef6080864cf525a44c208`
- `ZEN12_B_OPTIONAL_FILM_GUIDE.html` — `cbe0a817cb743156cb95363c42638eff4cf5ec7f`
- `ZEN12_OPTIONAL_FILM_42S.vtt` — `79a2257b3c97169edaf030c733869a61322b137b`
- `MIND_HUB_WORDPRESS_SOURCE_ONLY.html` — `c7cb2760d279f159758ff993be2e72a16df17dcb`
- `CLAIM_SOURCE_PARTNER_MATRIX.json` — `5a7dc977a26f95a674e60d019048a018a9299dcb`
- `CREATOR_CONVERSION_ACCEPTANCE.md` — `1a5cd4106969dcdc3fd1b964b7e248f478e74469`
- `qa.test.cjs` — `b2f2f407e271ccfca46e6e9eafade5565fd72a9a`

## Authored but not executed
An independent, reproducible **10-case native Node suite** is source controlled in `qa.test.cjs` with `node --test mind/r465/qa.test.cjs`. **NOT EXECUTED** in this run, due to lack of a checkout-mounted repository/native CI runner. Do not label authored tests as passed. Real Chrome/Safari mobile 360/390/768/1440/1920, WCAG 2.2 AA, keyboard/no-JS on devices, Lighthouse/CWV, WordPress sanitize/render, Jetpack confirm-and-deliver, final MP4 playback/closed captions, exact merchant checkout, refunds and settlement are likewise **NOT TESTED**.

## Commercial and publication blocker
Targeted connected Gmail search for Refersion/Zen12 approval revealed August 24 2026 pending notice, not a later named acceptance in the searched scope. Public Inspire3, Zen12 standard catalog and `/secret/` offer are distinct public descriptions, not approval to earn. No actual FV-owned payable, rights-cleared Mind SKU was proven. The free 52-page Focus Fieldbook is not a paid fallback. Therefore **no active offsite CTA, no A/B visitor test and no computed realized net revenue per thousand qualified human sessions.**

## Evidence source links
- Original repetition blindness: https://pubmed.ncbi.nlm.nih.gov/3691023/
- Disconfirming retrieval interpretation: https://pubmed.ncbi.nlm.nih.gov/7595242/
- Immediate online responses: https://pubmed.ncbi.nlm.nih.gov/11999868/
- Seller standard page: https://zen12.com/about ; ordinary catalog: https://zen12.com/ ; separate promo: https://zen12.com/secret/
- Scientific EEG systematic review: https://doi.org/10.1371/journal.pone.0286023
- FTC endorsement rules: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- FTC health claims: https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
- Live FV Puységur: https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/
- Live existing free Focus: https://finalvestige.com/focus/

## Explicit disposition
**BUILT:** eight source files + QA receipt; A text, B source-only storyboard, hub markup, claim matrix, creator map, testing contract.
**TESTED:** 42/42 V8 committed-source assertions and 6/6 synthetic mutation detections.
**NOT TESTED/LIVE:** Native Node tests, real video, actual WP CMS draft, browser, forms, commerce, affiliate sale, merchant or revenue attribution.
**RELEASE:** HARD HOLD. Founder commercial/release approval, named partner terms, actual paid transaction and independent accessibility/performance tests still required. Preserve PR #49, Mind PR #172, Issue #150, Jetpack welcome and all other agent work.
