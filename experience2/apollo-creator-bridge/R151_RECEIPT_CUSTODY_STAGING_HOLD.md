# Apollo R151 — independent browser acceptance receipt custody (STAGING HOLD)

Issues: #150, #820, #818. Base: R150 PR #1155. **No changes to homepage PR #49, Research Desk PR #158, Grok/Praxxis queues, merchant accounts, WordPress, analytics or production.**

## Why this sprint
R150 checked whether axe-core returned zero *violations* but did not require its `incomplete` count to be zero. This could incorrectly certify an inconclusive accessibility result. R151 fixes that existing staging code and adds a **separate post-execution attestation** against R149/R150 browser receipts.

## New guarantees
- Source file must be the exact independently archived, real WordPress-source-derived R149 excerpt (Git blob `899b7c4a1c46b2e6c46bf079d6784124636a011e`); synthetic HTML and even one-byte source drift must fail.
- Recompute original / repaired source SHA-256 and Git blob identities; enforce expected chronology/gallery source and proposed exact repair.
- Require a passing Chromium *before and after* matrix at 320, 360, 390, 768, 1440, 1920 px, including four marked chronology positions, keyboard slider, historical disclaimer, live status, link continuity and no horizontal overflow.
- Require no-JavaScript preservation at all six widths and verified screenshot SHA-256 for exactly seven expected files.
- Require six actual axe scans with zero WCAG violations **and zero incomplete results**, rather than trusting a single `axe=EXECUTED` flag.
- Reject contradictory release, photo-rights or sales claims. Even fully passing **offline excerpt** evidence only yields `SOURCE_EXCERPT_QA_PASS_STAGING_HOLD`, **never** production approval.

## Reproduce on a clean R151 checkout
From `experience2/apollo-creator-bridge`:

```bash
python -m unittest -v test_r149_gallery_release_candidate.py test_r150_real_excerpt_gate.py test_r151_receipt_custody.py
python r150_real_excerpt_gate.py --input fixtures/r149_published_chronology_source_excerpt.html --out /tmp/apollo-r151-source --axe /path/to/independently-verified/axe.min.js
python r151_receipt_custody.py --source fixtures/r149_published_chronology_source_excerpt.html --r149 /tmp/apollo-r151-source/r149_browser_receipt.json --r150 /tmp/apollo-r151-source/r150_qa_receipt.json --artifacts /tmp/apollo-r151-source --out /tmp/apollo-r151-verdict.json
```

Do not pass `--controlled-model` to the actual-source gate. Model runs remain negative controls only. If local axe-core is unavailable, the R150 receipt must remain incomplete and R151 must fail closed. Do not reuse or overwrite an old receipt directory.

## Verified in this sprint (2026-11-05)
- The exact repository-committed R151 parser and test Git blobs were checked against the local native-Python-tested bytes.
- Python 3 native suite: **40/40 PASS** (R149 + R150 + new 19 R151 adversarial checks).
- Chromium 144 *controlled model*: 153 checks PASS, 0 failed, six widths, screenshots. This is **not the real WP source**.
- R151 independently rejected that controlled-model receipt with `FAIL_STAGING_HOLD` (two hard errors: wrong source identity/scope, and thirteen missing axe results).
- Actual WordPress page #2017 (read-only connector, last modified 2026-11-04 17:09:24): three source-linked photos, selector defect remains **present**. No R149 fix has been published.
- Real WP-source-derived excerpt Chromium execution and actual-page axe remain **NOT EXECUTED**. Actual site LCP/CLS, image transport, Assembler theme, Safari, physical devices, purchase records and media-specific commercial permissions remain **UNVERIFIED**.

## Conversion-first bridge (not activation)
**Grok Apollo historical long-form/Shorts (UNVERIFIED asset) → existing Apollo Evidence Atlas (published) → existing “Read the full investigation” CTA (published) → proposed classroom evidence dossier (NOT SELLABLE/VERIFIED).** One CTA, no unrelated products and no invented links. Buyer: secondary history/STEM educator; verify licensed product, checkout, delivery and rights **before** any purchase CTA. KPI remains verified realized net revenue per 1,000 qualified human sessions over 7/30 days, with merchant-confirmed paid orders, fees and refunds. All Apollo-specific sales and attributed Grok sessions remain unknown.

NASA sources: official Apollo 204 Review Board, images S66-58038 and S67-15717 verified at NASA pages; 2017 hatch image URL independent retrieval remains incomplete. NASA media and brand guidance: https://www.nasa.gov/nasa-brand-center/ . No NASA endorsement or rights clearance is claimed.

**Release gate: STAGING HOLD.** Need exact-source Chromium/axe, full WP staging and media QA, independent QD review, hosted CI on exact head, proven rights-cleared sellable offer, and founder explicit approval. No writes to WordPress or merchant systems.
