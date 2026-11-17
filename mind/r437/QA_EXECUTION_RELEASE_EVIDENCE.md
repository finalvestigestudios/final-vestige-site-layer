# R437 — Actual source verification & release evidence

**Prepared 2026-11-16 PT**  
**Branch:** `mind-r437-thatcher-illusion-offer-proof-20261116`  
**QA source checkpoint before receipt:** `f8d04db655b1841b3afb5ea3ea4322879a78c3b4`  
**Release state:** UNPUBLISHED / COMMERCIAL HARD HOLD. No CMS edits, affiliate links, merchant changes, social posts or deployment.

## What was actually run

**Read-only source check:** eight exact GitHub source blobs were fetched from this branch and inspected directly; **48/48 independent static V8 checks PASS**.

**Committed verifier executed in isolated V8:** the exact `verify.mjs` GitHub blob at this checkpoint was executed with only its shebang/Node `import` and filesystem read wrapper replaced by read-only in-memory adapters to the exact fetched source blobs. Its real validation body executed **82/82 PASS**. The final three-line result was `R437 SOURCE SAFETY & AB PARITY: 82/82 assertions PASS (source-level ONLY; no hosted CI/browser/merchant proof)`.

**Adversarial mutation proof:** the same verifier body was run against twelve synthetic, in-memory mutations of the read source only. It rejected **12/12 unsafe changes**: flipping all gates to PASS; adding a merchant anchor; enabling the disabled button; removing commission disclosure; injecting script; injecting iframe; changing only B's buyer copy; damaging the last VTT timing cue; erasing SVG accessible description; fabricating matching social IDs; removing original DOI provenance; and deleting the existing /focus/ route. Zero repository files were changed by these synthetic checks.

**Important boundary:** These checks verify text/source properties using read-only V8 adapters. **Native Node CLI on an actual checkout, hosted GitHub CI, a browser, WordPress, a playable encoded movie, Jetpack and real merchant checkout were NOT executed.** The `verify.mjs` file is committed for native reproduction by a maintainer. Do not label the full release QA passing.

| Inspected exact file | Git blob SHA |
|---|---|
| `ZEN12_A_TEXT_ONLY.html` | `4ff60b1316ea8142990661bc69be5c168c2755d8` |
| `ZEN12_B_OPTIONAL_FILM_CONCEPT.html` | `0da27b524a969aba16701c48fc0c707199f2e56f` |
| `MIND_ARCHIVE_WORDPRESS_SOURCE_ONLY.html` | `be9434eb052764b9c1c3fa65e57165bf29cd5e9f` |
| `ZEN12_42S_CONCEPT.vtt` | `9acf1d6963a99444aeffb3d1625e01071bd3a88e` |
| `THE_FACE_THAT_CHANGED_WHEN_TURNED.md` | `90217f77fed6eb7fc828b4f7cd734166d4ad84c9` |
| `CLAIM_SOURCE_AND_PERMISSION_MATRIX.json` | `eeb89ab5510edd4a668b61fff65330cf7995b417` |
| `CONVERSION_ACCEPTANCE_AND_CREATOR_FIT.md` | `a08298e39ce0fca2bcdc820e83750104034c34fa` |
| `verify.mjs` tested verifier body | `93d74012789c47414d257544aeb4243b602c0651` |

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
