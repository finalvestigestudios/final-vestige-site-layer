# Mind R16 · exact-source QA execution evidence

**Date:** 31 October 2026 PT. **Owner:** GitHub Issue #171. **Status:** Source-controlled editorial draft, no production effects.

## Source-level verification actually executed

The committed checker was **fetched back from GitHub**, along with its exact four auditable source inputs, and run as a JavaScript exported function inside an isolated V8 environment. This exercises real audit logic and adversarial mutation logic against committed content, not merely checks that a test file exists. The V8 execution is not a claim that a full Node checkout or hosted GitHub Actions run passed.

| Exact GitHub file | Last audited blob SHA |
|---|---|
| mind/mcgurk-focus-shot-r16/wordpress-draft.html | 1231d992d2ac6688d393a7b2d043e31d7ee05e09 |
| mind/mcgurk-focus-shot-r16/focus-shot-evidence-guide.md | 46159eff3c0ea4137e4492bf887e36451024e628 |
| mind/mcgurk-focus-shot-r16/claims-and-product-evidence.json | cddbfd19111fb26393e7b9c7c319d3adcc835c46 |
| mind/mcgurk-focus-shot-r16/conversion-video-measurement-protocol.md | 61feaced915e71d9be8e667e0ebf6cc9b055847e |
| mind/mcgurk-focus-shot-r16/qa.cjs | c9bfa68fb458441fa83c0346bdb65e02a4aeec39 |

### Final source audit: 96 of 96 PASS

Covers 49 exact claim decisions / 20 source URL records, claim-source references, account-specific authorization flags, null merchant earning URL, disclosures adjacent to disabled CTA, no merchant/external unreviewed anchor, no tracking, form, script, iframe, hidden signup, pixel, autoplay or hosted media, first-party real published routes, HTML/heading/fragment ID integrity, no-JS semantic explanation, mobile/reduced motion/forced-colors/focus provisions, buyer guide length, two actual auditory methods kept separate, and **eight numeric source-palette text-contrast checks** at >= 4.5:1. These checks are source contracts, NOT actual rendered visual accessibility certification.

### Adversarial mutations: 18 of 18 detected

Individually introduced unauthorized merchant purchase anchor, stripped real commission disclosure, erroneously enabled CTA, injected JS, new signup form, tracking image pixel, fake auto-video, invalid published Focus link, invalid Puységur link, lost reduced-motion CSS, corrupted source anchor, duplicated ID, false merchant acceptance, invented earning URL, activated analytics, invented firsthand product trial, false company-guaranteed attention result, and missing UNHOSTED video qualification.

**Transparent iteration:** Initial checker 93/95 because two precise article/guide phrases lacked the exact phrasing its tests expected. Both pieces were edited to make limitations unambiguous, then 95/95 passed. Initial mutation checks caught 14/18; the undetected cases exposed overly permissive disclosure/disabled-attribute matching and an overly narrow source URL whitelist. The checker was corrected with an actual adjacent commission disclosure assertion, a standalone disabled attribute, and a verified URL whitelist for every external article link. Final re-readback: **96/96 static checks, 18/18 deliberate regressions detected**. No earlier test count is represented as final.

### Reproduction in a local Node checkout (not executed by this runtime)

From repo root after checkout, run the committed script using Node 18+ with the command (plain text):

    node mind/mcgurk-focus-shot-r16/qa.cjs --mutation

No production URL, partner token, API access or paid service is required. The script must print source QA 96/96 and Mutations 18/18; it returns nonzero on any failed audit or any undetected mutation. An independent reviewer should execute this exact command against the PR head SHA and run hosted CI separately.

## Independent REAL Chromium offline Zen12 optional-film fixture: 43/43 PASS

A distinct review fixture uses the already produced original portrait film from prior draft PR #229, exact H.264 MP4 **40.000 s / 155,763 bytes / 540x960**, poster and five-cue English WebVTT. **Not source-controlled within this branch, NOT a WordPress preview, NOT published, NO simulated conversion test.** The companion original script, standalone HTML A and B examples, screenshot captures at 390/1440 and no-JS 390, assets and JSON results are attached in this automation's conversation as FV_Mind_R16_Zen12_Optional_Film_Chromium_QA.zip.

Chromium's environment administrator blocked navigation to both local file and 127.0.0.1 addresses. The test did **not** bypass site rules or upload media: it used Playwright page.set_content with data-URL encoded copies of the exact same local reviewed video, poster and VTT; the output was a real Chromium DOM and real video stream decode, not a mock. Failing first-round comparisons were a fixture-test mistake (incorrect string-prefix matching around the inserted component); the comparator was corrected to compare the unchanged guide DOM after removing the optional figure. **Final result 43/43 PASS** including:

- A and B exactly the same guide markup/content except optional film.
- Tested 360, 390, 768, 1440, 1920 pixels with no horizontal document overflow, disabled merchant CTA and identical guide copy; optional native video has manual controls, paused on load, no autoplay, preload=none, poster, caption track and transcript.
- JavaScript-disabled Chromium allowed the native details/summary transcript to open, and retained disabled merchant CTA.
- 40.000 s MP4 metadata decoded in Chromium and frame timeline advanced after explicitly programmatic playback invocation; this is NOT a human keyboard/touch playback usability certification.
- Offline asset integrity matched prior review: MP4 SHA-256 c4cb33fef60dfa773e65a46b9167c0581e58cf07f09c42b744f90c60af48ebbc, caption SHA-256 5924d265a8081acbef9d1599a012bae75e71096e4f60e2f17511e96a5422785d, poster SHA-256 cce9065e7f4f53a34baefa628ad82af509a31f696b6e55f120d8645a6565b6e3.
- **Not tested:** real WordPress sanitization, real hosted network preload/caching, WebVTT visual cue timing in assistive technology, Safari/Firefox, external screen readers, keyboard playback controls, 200-400% zoom, real Lighthouse CWV, conversion outcomes, user experience of the seller product, actual paid offer.

## Source accuracy and FTC compliance boundaries

Direct official product records https://inspire3.com/ ; https://brainwaveshots.com/focus-shot ; https://brainwaveshots.com/faq ; https://zen12.com/about. Primary effect https://doi.org/10.1038/264746a0 . Binaural reviews https://pubmed.ncbi.nlm.nih.gov/30073406/ and https://pubmed.ncbi.nlm.nih.gov/37205669/ . FTC https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking and https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance .

We established only **seller-described features** for the Focus Shot isochronic SKU and independent research on distinct auditory interventions. We explicitly **did not establish** Focus Shot focus/brainwave/medical effects, an approved merchant link, seller affiliate account permission or actual merchant conversion, and therefore do not activate an affiliate recommendation.

### Before release / Site QA handoff

QAs needed: founder source/factual approval; partner acceptance and specific SKU eligibility, tracking format/permissions for merchant creatives, social video and separate opted-in email; authorized recording use and seller landing/checkout review; full independent WordPress Gutenberg/browser/a11y/contrast/zoom/mobile/poster/WebVTT/media/performance; public Focus and Jetpack no-submit verification; founder separate publication and monetization signoff.

The homepage Issue #150 and flagship PR #49 are untouched; the original Mind hub PR #172 remains distinct. Dispatch Issue #174 is informational only, no emails sent. All live CMS/navigation/subscriptions/settings unchanged. Do not merge or deploy this PR as part of QA.
