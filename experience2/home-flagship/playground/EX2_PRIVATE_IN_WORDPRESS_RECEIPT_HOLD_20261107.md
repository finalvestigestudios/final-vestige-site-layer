# EX2 — In-WordPress private browser evidence receipt (RELEASE HOLD)

**Stack parent:** PR #1365 at `ce000385462e3acad97ba292cf6dd7a2bfb9f397`. **Frozen PR #49 untouched.** No WordPress.com production changes, deploy, merge, subscriber operations, tracking, purchase, affiliate activation or spending.

## Actual blocker and improvement

Prior PR #1339 builds a source-pinned private WordPress Playground launcher, but its browser bridge could not load the external Playground site in this execution environment. We still lack a genuine integrated WordPress/Assembler proof. This isolated PR adds a **review-only MU-plugin and an opt-in in-page browser receipt**, usable inside the *actual* imported WordPress Playground page once opened on a network-connected machine. This does not claim staging has run.

The builder pins canonical Blueprint Git blob `137c74a476005684a28f5ff9a36e75c6b03268f7`, pins the helper PHP SHA-256 `57bdfac3aebdf508e3484d8a2197ef31f4e97be27f583e8fc93909d47d40e4dd`, and pins Assembler commit `75faa8a1e0367a37c2638250a3c9ed0a0f8c0b7f`. It inserts exactly one new **writeFile** action for the extra MU-plugin, leaving the original five operations unchanged. The reviewed derivative Blueprint has Git blob `8b4d4d5af5d4102797eeeb8c2914f7c6c11b9e19`. It is **NOT canonical** and must **never** be used in production. The WordPress plugin is doubly fenced behind the original isolated-review option marker and `is_page('fv-ex2-review')`. The browser inspector requires an explicit click, downloads a JSON **locally**, and never transmits or persists analytics.

The JSON honestly separates *browser-selected currentSrc* from declared `src`; it checks the seven chapter anchors, all 72 Margins items, five /focus/ links and CTA dimensions, two archival image identities/decode status, WordPress shell marker, document overflow and viewport/reduced-motion metadata. It explicitly labels the unknowns: real response bytes, axe/WCAG 2.2 AA, keyboard/touch/no-JS acceptance, Lighthouse/CWV, Jetpack confirmation, merchant-paid sales, net revenue and WordPress.com hosted parity. **Even if all structural checks pass, the report does not grant release approval.**

## Verification performed: genuine Chromium, but offline fixture NOT WordPress

- **12 Python unit-test methods passed** with source hash negative controls and PHP syntax validation.
- Chromium panel/download exercised at **320, 390, 768, 1440 CSS pixels**; the historical source and five Focus paths remained intact in the fixture.
- Missing WordPress shell, one missing Margins item and altered Focus URL correctly generated BLOCKED receipts. Reduced-motion metadata and no-JS source visibility checked.
- Image network requests deliberately aborted. Local receipts show **ARCHIVAL_IMAGE_NOT_DECODED_MAY_BE_LAZY** rather than fabricated image-transfer or first-party success.
- A four-width screenshot gallery and JSON receipts are in the independently generated local evidence package. **None are genuine staging screenshots.**

## Rights, conversion and safety

The unchanged source candidate references Apollo 1 NASA S67-19766 media #473 and the Franklin Victory Point note reproduction media #474; original metadata reports 78,346 and 466,043 bytes, **not independently measured transfer bytes**. The rights-pending NYPL #1258 image remains excluded from this candidate but appears on published Page 6; that separate rights reconciliation is still open. No new artwork, historical claims, merchant product links, affiliate claims or scripts are added.

**Offer → Funnel → Blocker → Change → Evidence → Owner:** 52-page free Focus Fieldbook → evidence/trust → /focus/ link → confirmed Jetpack lead → verified paid purchase/refunds/fees/net revenue. Blocker: no integrated WordPress admission and possible invalid image-origin assumptions. Change: safe inside-WordPress receipt to help capture actual browser-state evidence. Evidence: 12 offline tests PASS; real WordPress, actual paid conversions and net revenue NOT VERIFIED. Owner: interim homepage engineering / Site QA; Claude owns analytics, Jetpack, checkout; Grok/Praxxis own creator posts and asset IDs.

## Reproduce from exact checkout (no CMS writes)

```sh
python3 experience2/home-flagship/playground/test_private_browser_receipt.py
python3 experience2/home-flagship/playground/make_private_browser_receipt_variant.py \
  experience2/home-flagship/playground/FV_EX2_ASSEMBLER_BLUEPRINT_20261105.json \
  experience2/home-flagship/playground/fv-ex2-private-browser-receipt.php \
  /tmp/FV_EX2_LOCAL_WP_REVIEW_RECEIPT_ONLY.zip
```

Open extracted `launch_review.html` only on a trusted computer with access to the public WordPress Playground. Scroll to the foot of the imported private preview; select **Capture this viewport** then **Download JSON receipt**. Retain HOLD if page import, audit panel, archive images or any subsequent axe/Lighthouse/network gates fail. Do not expose unreleased Blueprint source publicly.

**Release gates still open:** genuine WordPress/Assembler import, actual 320–1920px hosted screenshots, image response bytes + provenance, independent axe/WCAG 2.2 AA, keyboard/touch/no-JS, Lighthouse, Jetpack/checkout verification, exact-head CI and independent QD, rights and founder approval. WordPress.com Personal plan cannot create the native staging clone. Playground is an isolated approximation, not proof of WordPress.com Atomic parity.

**Decision: HOLD.**
