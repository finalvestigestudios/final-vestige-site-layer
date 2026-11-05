# FV Experience 2.0 — Page 6 native Gutenberg Margins integration
2026-11-05 | Issues #150, #820 | Companion stacked on draft PR #1062 | **DRAFT / HOLD, NO PRODUCTION CHANGES**

## Why this closes an integration-artifact blocker
A fresh read-only WordPress fetch of published Page 6 (site 256784396, modified 2026-11-04T14:39:24) returned 150,710 characters of Gutenberg content. Its first HTML block contains 72 original historical note spans. The embedded reduced-motion declaration sets display:none on all spans except nth-child(1), removing 71 notes from sight.

PR #1062 previously supplied an isolated CSS overlay and a passing 15-check Chromium fixture, but not a Gutenberg-native patch. This new branch supplies a **source-pinned, fail-closed, review-only transformer for the actual first Gutenberg HTML block**, replacing the original problematic media rule. It adds a visible reduced-motion instruction and a neutral accessible scroll-region name; no plugin, new scripts, external assets, new subscriptions, or CMS API calls.

## Before → proposed after (not live or browser-certified)
| Existing published **source** | Review-only patched **source** |
|---|---|
| 71 of 72 notes display:none in reduced motion | All 72 static cards with bounded horizontal scrolling, no animation |
| No visible scroll guidance | Reduced-motion-only text: "Scroll or swipe to browse all 72 notes" |
| Accessible label: "Rotating source and accountability notes" | "72 Hidden in the Margins historical notes" |
| No explicit high-contrast treatment in the reduced rule | Canvas / CanvasText forced-color support |
| Seven chapter destinations, four /focus/ hrefs, native Jetpack block | All preserved verbatim |
| All 72 authentic source-fragment texts | Exactly unchanged, in original order |
| Other Gutenberg blocks | 135,224 characters identical byte-for-byte |

Normal-motion behavior remains unaffected by the proposed CSS; actual computed CSS still requires integrated browser verification. This is not a new homepage chapter or an art-direction alternative.

## Verification actually executed in this sprint
- Fetched the **exact committed** transformer and tests from this isolated GitHub branch.
- Executed the **20 committed test bodies** with a compatible V8 assertion adapter (not native Node). After identifying and fixing two genuine guard defects, result: **20/20 PASS**.
- Executed the committed transform on **fresh public WordPress Page 6 content** obtained through a read-only connected call. Result: **PASS**. Public source chars: **150,710**; proposed review chars: **151,511** (801-character delta); all 72 note texts, 4 Focus links, 7 chapter destinations, single Jetpack block and all 135,224 characters outside the first Gutenberg HTML block preserved exactly.
- Negative tests reject a changed legacy CSS rule, altered Gutenberg wrapper, missing/duplicated/blank records, missing chapter destinations, insufficient Focus links, missing/duplicated Jetpack marker, changed source labels and repeat patching.
- Added a standalone offline Node CLI to generate a source/output SHA-256 review receipt from a **public-only** Page 6 JSON snapshot. It refuses stale modified timestamps and writes only to a new local .review.blocks.html file plus receipt, never to WordPress. The CLI and committed Node tests **have not been executed by native Node in this environment**.

## Reproducible offline use (no production access)
Export only public page content with fields id, modified, status, content and optionally title, excluding private editor fields, subscriber records, secrets, users and the live database.

    node --test experience2/home-flagship/qa/release-candidate/test_margins_page6_native_patch.mjs
    node experience2/home-flagship/qa/release-candidate/build_margins_page6_review.mjs --in public-page-6.json --out page-6-margins.review.blocks.html --review-only

The resulting Gutenberg blocks file is **review-only** for an authorized isolated WordPress Playground/Assembler developer installation. Its receipt is not a certificate of browser accessibility or hosted WordPress correctness. The WordPress.com Personal plan does not provide native staging clones. If Page 6's modified time changes, the builder intentionally returns HOLD until the source is reread.

## Required acceptance / independent release HOLD
1. Import public content and the Assembler theme into an isolated WordPress Playground or local clone, without production database, accounts, secrets or subscriber information. No live WordPress writes; do not install preview plugins without explicit release approval.
2. Execute real Chromium before/after on 320, 360, 390, 768, 1279, 1280, 1440 and 1920px with reduced motion, normal motion, JavaScript disabled, 200% zoom, keyboard and physical/touch emulation; verify all 72 notes visually readable, no global horizontal scroll and the Focus CTA reachable without overlay.
3. Run full-document axe-core and manual WCAG 2.2 AA. Fail closed if unavailable. Measure real image currentSrc/HTTP 200 transferred bytes, source rights, current Lighthouse lab and field CWV if available. Published NYPL commercial reproduction rights are under separate review #948.
4. Confirm approved merchant SKU and offer, actual /focus/ behavior, Jetpack confirmation without unauthorized test subscribers, and any paid purchase only from independent merchant records. Require current exact-head independent QD and green CI before any merge.
5. Obtain the founder's explicit visual and production release approval. Historical PR #637 WordPress Lighthouse/axe PASS belongs to its earlier commit, not this branch.

## Conversion and ownership contract
**OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER:** Free existing 52-page Focus Fieldbook → evidence trust and accessible reading → contextual Fieldbook action → independently confirmed subscriber → paid order and realized net revenue only if merchant records verify them. BLOCKER: reduced-motion visitors lose 71 evidence fragments in published source, weakening source credibility; separate storefront audit found no direct owned-product checkout URL on published Collection Page 78. CHANGE: WordPress-native source-safe Margins review patch, not an unverified paid offer or more popups. EVIDENCE: fresh Page 6 source accepted; historical texts and remaining Gutenberg blocks preserved; 20/20 V8 source test bodies passed; real WordPress browser and revenue unverified. OWNER: homepage engineering and independent QA; Claude owns commerce/attribution; Grok and Praxxis own creator acquisition and asset IDs. Primary KPI is realized net revenue per 1,000 qualified human sessions, with 7-/30-day cohorts, not traffic alone.

## Source and rights containment
Branch starts from PR #1062 SHA 299283a7f06a999654abd71eed08f1a4159278dc. Frozen PR #49, Apollo #158, candidate #254, live Page 6, theme, navigation, Jetpack, Focus and the #171 Mind/affiliate lane are untouched. No new artwork, archival photograph, historical claim, source URL, font, tracking or affiliate link. The 72 existing fragments are unchanged. All existing image-rights and evidentiary gates remain open.

**Release decision: HOLD. Source-integrated review artifact exists; real WordPress/Assembler visual and accessibility acceptance still required.**
