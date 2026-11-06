# EX2: six-width accessibility admission and Margins visibility — November 6, 2026

**DRAFT / RELEASE HOLD / NO WORDPRESS WRITES.** Stacked on PR #1213 exact parent 1067f80b82bd0cf28bfbafd5294ef75707a53cc9. Frozen PR #49 remains untouched.

## What was verified in the existing runner

PR #1213 captured six responsive screenshots but ran axe-core only after its viewport loop, at 1920 CSS px. A violation present only at 390 px could therefore escape. It also counted all 72 Hidden in the Margins DOM nodes but did not detect CSS hiding 71 of them for reduced-motion users. Connected WordPress Page 6 editor source (last modified November 5, 2026, 12:07:24) confirms the reduced-motion display:none rule. Existing PR #1062 already proposes its CSS remedy; this PR does not duplicate visual work.

## Change

The revised guest runner audits axe-core at **320 / 360 / 390 / 768 / 1440 / 1920 CSS px**, saves per-width findings, and rejects violations, missing axe, invalid results, or runtime failures at any viewport. It also requires all 72 Margins to remain in layout under reduced motion across six widths; it will correctly block until #1062 or an equivalent approved implementation is integrated. Existing network-byte archival checks, no-JS captures, chapter structure, Focus CTA, four interactions, read-only production guard, and no-release-ready default remain intact.

## Reproduction and honesty boundary

From the exact PR checkout run:

    python -m unittest -v qa.test_fv_ex2_archival_transfer_gate_20261106 qa.test_fv_ex2_guest_gate_20261105 qa.test_fv_ex2_axe_multiview_admission_20261106

Native Chromium + Playwright locally: **20/20 synthetic-fixture tests PASS**, including five new adversarial tests. The synthetic axe object is expressly a test double that returns an error at 390px but none at 1920px. It demonstrates correct runner sequencing and fail-closed behavior, **not actual WCAG 2.2 AA qualification**. The existing test double must NEVER be used as the --axe argument on any release candidate. Confirmed local runner Git blob a3844cbcc233d15f5d5c54167eb5ac0e69d55bc2; new test blob 037307a5bc1ab7006386b55d6c8ad0f97c554e2d.

Actual Assembler/WordPress Playground, real verified axe-core bundle, network image bytes, 200% native zoom, guest Jetpack delivery, Lighthouse/field CWV, rights, screen-reader/touch and exact-head CI/QD/founder review remain open. WordPress.com Personal does not provide a native staging clone. Do not use production as a test install.

## Conversion-first contract

**Offer:** Existing free Seven Day Focus Fieldbook (52 pages). **Step:** sourced historical landing → contextual Focus CTA → confirmed opt-in → verified purchase. **Blocker:** an undetected mobile accessibility defect and hidden source notes can obstruct visitor confidence and navigation. **Change:** fail-closed per-viewport accessibility receipt and reduced-motion admission, linked to existing #1062 implementation. **Pass/fail:** synthetic tests pass; actual WordPress and paid conversions NOT VERIFIED. **Owner:** homepage engineering + Site QA; Claude owns attribution/checkout/production, Grok/Praxxis own social acquisition.

No website deployment, merge, production settings, affiliate activation, analytics injection, emails, social posts or spend. Do not call a clean automated axe result full WCAG conformance.
