# R467 — executed exact-source QA and release HOLD
**Local date 2026-11-18 PT · source-only · draft PR review state**

## What was actually executed
1. Created a new isolated branch from live `main`; all writes were additive files under `mind/r467/`.
2. Retrieved all **eight** substantive committed GitHub files back through the GitHub connector by exact branch name, recording Git blob SHAs:
   - Article `THE_STATEMENT_YOU_SAW_FIVE_TIMES.md`: `81a050be6d746e17a283b3963f4934c8e4265def`
   - A text guide `ZEN12_A_TEXT_ONLY.html`: `9bb76bf3f6f0c90146cc2ae20c0994fedfeb6d62`
   - B optional short-film guide `ZEN12_B_OPTIONAL_FILM.html`: `e513f1208946e7489753c2ca370072a98511fbdf`
   - VTT `ZEN12_B_42S_CAPTIONS.vtt`: `eede7d3297ccaf305d8c4197d6f5cb84d3e92ca8`
   - Source-only hub `MIND_ARCHIVE_SOURCE_ONLY.html`: `5d8da8704d27adb9acc84326214dbf3e38179544`
   - Matrix `CLAIM_SOURCE_MERCHANT_MATRIX.json`: `63e0c91c5ed15f504c1b8c8fef35643bb27f46a2`
   - Revenue plan `OFFER_FUNNEL_EXPERIMENT_AND_REVENUE_ACCEPTANCE.md`: `42b67e7a79128604eccd8ad5fc3321f77d8ae2c1`
   - Native Node suite `qa.test.cjs`: `c0ffadda83be2cd7e2c00148171cc600c820a3a1`
3. Executed **89/89 deterministic read-only V8 source assertions PASS** across those exact returned file contents. Checked: HTML language, viewport/noindex, no-JS/no tracking/no forms/autoplay/remote media, disabled controls, seller URLs not activated, near-control FTC disclosure, A/B substantive parity, source-format distinction, six contiguous VTT cues totaling exactly 42 seconds, accessible SVG text and transcript, primary research trail, JSON matrix referential integrity, all merchant release gates held, three unverified creator media IDs and existing live destination paths.
4. Ran **7/7 synthetic in-memory adversarial mutation detections PASS** for removing the disabled attribute, inserting a seller hyperlink, altering A/B buyer copy, extending VTT to 44 seconds, falsely setting partner approval, changing the hub from noindex, and fabricating a computable revenue claim. These mutations were never committed to any branch.

## What was authored but NOT run
`node --test mind/r467/qa.test.cjs` — native test file committed for reproducibility; the portable Node suite was **not executed in this connector runtime**, and CI is not represented as passing.

**NOT EXECUTED:** actual browser WCAG 2.2 AA 360/390/768/1440/1920 audit; video encoding/playback/caption sync; Lighthouse/CWV; WordPress Gutenberg sanitizer and CMS saved-draft preview; Jetpack opt-in/welcome delivery; legitimate tracked outbound click; merchant authorized landing-page checkout; publisher approval, payment, postback or settled commission; cross-domain attribution tests. No visitor A/B test, live sale, payee reconciliation or verification of a live paid owned product.

## Reviewed source and merchant context
Official: https://inspire3.com/ ; https://affiliates.inspire3.com/ ; https://zen12.com/about ; https://zen12.com/secret/ . Public affiliate page describes generic network terms and special issued links; neither it nor the seller VSL establishes Final Vestige's approved publisher account, approved exact SKU, earning URL or channel-specific terms. Promo package, price/countdown and guarantee language belong to distinct promotional seller context and are not imported into the buyer guide. Public creatively prepared ads do not license copy/reuse; no approval-authenticated Zen12 swipe/creatives available. Focus https://finalvestige.com/focus/ is free; no verified FV-owned PAYABLE Mind SKU. Health claims and FTC sources independently reviewed:
- https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
- https://pubmed.ncbi.nlm.nih.gov/37205669/

Primary truth-effect original sources are explicitly linked in the ~2,068-word unpublished investigation. This sprint does not infer medical benefit from study of general meditation, binaural beats, hypnosis or repetition.

## Version and governance
Branch: `mind-r467-illusory-truth-conversion-gates-20261118`.
Final HEAD and draft PR number must be taken from the **GitHub response after this QA file commit**; do not substitute this interim commit hash. Never edit homepage PR #49, canonical Mind PR #172, owner Issue #150 or Dispatch drafts. No WordPress CMS write, live nav edits, merge, deploy, email, social post, Grok queue assignment, spending, third-party tracking or affiliate link activation.

## Overall acceptance verdict
**STATIC SOURCE READBACK: PASS, 89/89; mutation checks: PASS, 7/7.**
**RELEASE AND COMMERCE: HARD HOLD**. Neither commercial eligibility nor full-stack browser and merchant QA is satisfied. Until actual independently settled orders and a qualified-human session denominator are authenticated, realized net revenue per 1,000 qualified human sessions is **NOT COMPUTABLE**.
