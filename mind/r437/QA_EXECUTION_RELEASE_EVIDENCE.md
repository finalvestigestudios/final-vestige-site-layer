# R437 — Actual source verification & release evidence

**Prepared 2026-11-16 PT**  
**Branch:** `mind-r437-thatcher-illusion-offer-proof-20261116`  
**QA source checkpoint before receipt:** `12263f839046104f8ef5937d0c045b8365e71d40`  
**Release state:** UNPUBLISHED / COMMERCIAL HARD HOLD. No CMS edits, affiliate links, merchant changes, social posts or deployment.

## What was actually run

One independent, read-only JavaScript V8 audit retrieved the eight exact GitHub blobs below at the isolated branch source checkpoint, then evaluated **48/48 source-level assertions PASS**. Tests covered claim counts, held gates, source-key integrity, 2,000+ word substantive editorial draft, original science citations, HTML language/noindex, no scripts/forms/iframes, no active seller anchors, visible focus styles, responsive rules, near-CTA prospective affiliate disclosures, disabled seller control, existing free /focus/ route, buyer-text byte equality across A/B, original SVG poster, no-JS transcript, six VTT cues completing at 42 seconds, all three social IDs UNMATCHED, no invented revenue and A/B allocation hypothesis.

**Evidence scope:** These are static property checks of the fetched source strings, **not** execution of Node CLI, hosted CI, a browser, WordPress, an encoded video player, analytics, Jetpack or a merchant checkout. The committed `verify.mjs` provides a reproducible native-Node check for a maintainer with a checkout. It was not run with native Node in this environment; a passing V8 audit is not equivalent to its execution. A subsequent verifier-only regex correction is present at the pinned QA source checkpoint. The original pre-correction 48/48 V8 check did not exercise the exact committed Node script. Independent reviewer should run `node mind/r437/verify.mjs` on the pinned SHA.

| Inspected exact file | Git blob SHA |
|---|---|
| `ZEN12_A_TEXT_ONLY.html` | `4ff60b1316ea8142990661bc69be5c168c2755d8` |
| `ZEN12_B_OPTIONAL_FILM_CONCEPT.html` | `0da27b524a969aba16701c48fc0c707199f2e56f` |
| `MIND_ARCHIVE_WORDPRESS_SOURCE_ONLY.html` | `be9434eb052764b9c1c3fa65e57165bf29cd5e9f` |
| `ZEN12_42S_CONCEPT.vtt` | `9acf1d6963a99444aeffb3d1625e01071bd3a88e` |
| `THE_FACE_THAT_CHANGED_WHEN_TURNED.md` | `90217f77fed6eb7fc828b4f7cd734166d4ad84c9` |
| `CLAIM_SOURCE_AND_PERMISSION_MATRIX.json` | `eeb89ab5510edd4a668b61fff65330cf7995b417` |
| `CONVERSION_ACCEPTANCE_AND_CREATOR_FIT.md` | `a08298e39ce0fca2bcdc820e83750104034c34fa` |
| `verify.mjs` after hardening | Read from source checkpoint again when executing native Node; earlier blob `2cd06701210e4ab35d808c42e3ed21e9b6cab3f3` was corrected in two additive verifier-only commits. |

## Credible source verification

- Thompson 1980 original journal record: https://doi.org/10.1068/p090483 (paper's copyrighted figure NOT reused)
- Wong et al. 2010 non-face comparison: https://pubmed.ncbi.nlm.nih.gov/20942363/
- Psalta et al. 2014 fMRI: https://doi.org/10.1177/0956797613501521
- Lobmaier & Mast 2007 viewer rotation: https://doi.org/10.1068/p5508
- FV Puységur original archive and evidence/consent: https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/
- Existing live change-blindness canonical to avoid duplicate: https://finalvestige.com/2026/11/02/change-blindness/
- FV existing free 52-page Fieldbook: https://finalvestige.com/focus/
- Official parent merchant: https://inspire3.com/
- Zen12 exact product description and promoted full-course presentation: https://zen12.com/about ; https://zen12.com/secret/ ; alternate tiers https://zen12.com/
- Hypnosis Live Total Focus SKU: https://hypnosislive.com/mental-skills/total-focus
- Brainwave Shots Focus Shot SKU: https://brainwaveshots.com/focus-shot
- FTC near-link disclosure: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- FTC mental/health efficacy substantiation: https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance

## What remains UNTESTED / BLOCKED

- Native Node CLI and hosted GitHub Actions status on this PR; don't infer CI green.
- Browser at 360/390/768/1440/1920, keyboard, touch, screen reader, zoom, forced colors, real WCAG 2.2 AA, responsive performance, Lighthouse LCP/CLS/INP.
- WordPress sanitizer and editorial publish route; the hub is **source-only**, not a WP saved draft or a live /mind/ route.
- Encoding/licensing, playback, captions, volume behavior and accessibility of a real original 42-second video. Current B is poster+storyboard+VTT only.
- Actual consented first-party events, tracking scripts, UTM filtering and real Grok asset IDs. Nothing was installed.
- Verified Inspire3 named partner approval, exact SKU/channel rights, approved creative license, earning URL, referred checkout price/refund and settlement reporting. Gmail account-level targeted searches found only consumer/promotional contexts, not authorizing partner documents.
- FV-owned paid Mind SKU, ownership, real checkout/fulfillment/returns and purchase confirmation.
- Jetpack provider-confirmed email opt-in/delivery; existing welcome email intentionally untouched.
- Merchant paid order, commission settlement, refund/fee reconciliation and qualified human cohort denominator; realized net revenue/1000 is **NOT COMPUTABLE**.

## Release rules

**28/28 permission and acceptance gates remain HOLD.** No change in public site, menus, dispatch, Grok queue, home art, analytics or affiliate links. Founder controls release and spending, Claude site/measurement, Site QA independent acceptance, Praxxis/Grok media proof. PR #49/Issue #150 and canonical Mind PR #172 are untouched.

This draft is reviewable as content/prototype, not commercially operable. Any claim of "built," "tested," "live" or "verified" must identify its exact evidence tier and may not conflate them.
