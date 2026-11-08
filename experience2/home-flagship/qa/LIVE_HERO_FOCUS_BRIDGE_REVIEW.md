# EX2 — Live homepage hero → Focus: conversion-first review experiment

**2026-11-07 PT | DRAFT REVIEW ONLY | RELEASE HOLD.** Parent #1522 at `5220131734747879879fe77893056065a5aa8f2e`. Frozen #49 not touched. Only `finalvestige.com` production WordPress site ID 256784396 is connected; no authorized isolated WordPress core/Assembler staging was used.

## Authenticated live source finding

Published WordPress **Page 6** (`home`; modified `2026-11-05T12:07:24`) already contains seven chapters, 72 Margins fragments, the Franklin editorial hero, four body-level Focus links, and four image elements (Apollo, Franklin, NYPL 1903 map, Fieldbook cover). Its secondary **hero** action is **“Read the investigations” → /blog/**, next to the primary **“Enter the evidence room” → #fv-hf-evidence**.

The protected unpublished Playground candidate already uses **“Explore the free 52-page Focus Fieldbook” → /focus/** as that secondary hero action. This PR proposes making only that conversion-focused destination change to the existing published Page 6, **without replacing the full page**. It is an experiment, not an instruction to publish.

Authenticated read-only in-memory preview against the live WordPress page **actually passed**: old anchor 1, new anchor 0 → after old 0/new 1; Focus links 4 → 5; 72 Margins unchanged; seven chapter links unchanged; four image elements unchanged; the exact original page is recoverable by reversing just that one anchor. **No CMS write occurred.**

## Source pin and executable tests

The review CLI refuses raw Page 6 inputs unless their SHA-256 equals the published source pin `685911178ae68ca9dfbd8f47f5903ef57f76ac4b52e886d8287416304c98794b`. It produces a local-only proposed page file and JSON receipt. No raw published content, user list, cookies, subscriber records, or private plugin bundle is committed to Git.

```sh
cd experience2/home-flagship/qa
python -m unittest -v test_live_hero_focus_cta_review.py
python live_hero_focus_cta_review.py /path/to/authenticated-raw-page6-content.html --out /tmp/page6-hero-proposal.html
```

**Local committed-source tests: 9/9 PASS**, including deliberately corrupted SHA, duplicated/missing hero, chapter/Margins/media drift, unexpected Focus link, and new third-party link checks. A separately packaged extended suite passed **16/16**. Browser study using the exact SHA-pinned **PRIVATE** Playground PHP payload (NOT live WordPress) passed **40/40** combinations: before/after × 320/390/768/1440/1920 × 100%/200% CSS zoom × JS on/off. Screenshots show the proposed secondary action at 390/1440; actual live WordPress screenshots and Lighthouse remain missing. At 200% zoom the hero secondary link can be below the first screen, but was keyboard-reachable in the isolated study.

## Conversion hypothesis and decision rule

**Audience/intent:** People arriving from Grok's evidence/mind-oriented videos who engage with the archival hero. **Offer:** Existing 52-page free Focus Fieldbook, with Dispatch opt-in consent explained on /focus/. **Funnel:** qualified-human session with existing `utm_content=asset_id` → contextual action → genuinely confirmed Jetpack subscriber → separately verified paid order or independently reported affiliate commission → refunded/fee-adjusted realized net revenue. **Current measurements: unknown.** Link clicks and lead messages do not constitute sales. Do not add or redeploy attribution scripts; Claude owns that lane under #820.

**Hypothesis:** Keeping an evidence-first primary CTA while making the optional secondary CTA a clear free Fieldbook action improves qualified opt-in *intent* without harming archive discovery. Measure impact on **net revenue per 1,000 qualified sessions**, not raw CTA clicks, after merchant/Jetpack observability is real. A/B only after founder acceptance; no launch decision from this offline study. Preserve blog discovery through existing site navigation.

## Historical/rights gate and limits

No new imagery, scripts, CSS, merchant claims or affiliate links. NASA Apollo #473 and Franklin #474 retained; live NYPL 1903 Brooklyn Transit map #1258 stays publicly present and has **not** been adjudicated as a rights violation. NYPL's own rail guide identifies image **5003296** as the 1903 map: https://libguides.nypl.org/nyc-rail-transit/companies . NYPL describes reuse rights **per exact image/capture**, not all collection items collectively: https://api.repo.nypl.org/api_documentation_v1 . The specific Digital Collections item URL returned a 403 in this environment; do not substitute a different 1903 Brooklyn map to assert rights clearance. **Item-level rights remain HOLD** pending actual record review and binary provenance.

## Releasing requires

No merge/deploy/publish/plugin install, subscription submission, social post, analytics script or spending. Must first verify real isolated WordPress/Assembler and Jetpack behavior, first-party archive bytes, independent axe/WCAG 2.2 AA, mobile/keyboard/touch/no-JS, measured Lighthouse/CWV, founder art-direction review, and exact-head QD/CI. GitHub workflow job on parent #1522 failed before reporting any steps; its archived log endpoint was unavailable (404), so no specific code or billing cause has been proven here.

**Status: BUILT + TESTED IN ISOLATION; NOT LIVE; NOT CONVERSION-VERIFIED.**
