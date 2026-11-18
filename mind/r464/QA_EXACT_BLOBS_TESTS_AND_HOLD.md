# R464 exact committed-source QA and commercial HOLD receipt

**PT review date:** 2026-11-17 · **Workstream:** Final Vestige Mind & Perception only · **Release:** UNPUBLISHED / HARD HOLD. This receipt describes checks actually executed separately from those merely specified.

## Reviewed sources
- Original 1976 McGurk/MacDonald DOI: https://doi.org/10.1038/264746a0
- First-author historical retrospective: https://pubmed.ncbi.nlm.nih.gov/31264593/
- Strand et al. 2014 abstract: https://doi.org/10.1044/2014_JSLHR-H-14-0059
- Brown et al. 2018 open-access study: https://doi.org/10.1371/journal.pone.0207160
- Magnotti, Basu Mallick & Beauchamp (2018, indexed 2019): https://pubmed.ncbi.nlm.nih.gov/31264598/
- Official seller catalog: https://inspire3.com/
- Official Zen12 format: https://zen12.com/about
- Distinct Zen12 promotional offer, not an authorized FV checkout: https://zen12.com/secret/
- Other seller products: https://hypnosislive.com/ and https://brainwaveshots.com/
- Public merchant affiliate site: https://affiliates.inspire3.com/ — seller generalities NOT a named approved account
- FTC endorsements: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- FTC health-claim substantiation: https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance
- Existing live FV Puységur, Focus, Change Blindness and Mesmerism routes checked in read-only web.

## Exact committed GitHub blob readback (NOT local drafts)

| Source | Git blob SHA |
|---|---|
| THE_VOICE_YOUR_EYES_HEARD.md | 58a47f3306155921ded00573ade47f00a6e8af81 |
| ZEN12_A_TEXT_ONLY.html | 3e9f4b0aec9dd98503da6b483cab60da4ac6811b |
| ZEN12_B_OPTIONAL_42S.html | 18968d24287216aa160edf7e5dbde4689b4085e1 |
| MIND_HUB_WORDPRESS_SOURCE_ONLY.html | 8d5e3702fcc63a020d768376b577145600687626 |
| CLAIM_SOURCE_PARTNER_RELEASE_MATRIX.json | 5ad6feb45480f1ae1d48430d241bce86065b068c |
| CONVERSION_CREATOR_AB_ACCEPTANCE.md | b6b76358696787fdb4659c0fb5e580381078d8d1 |
| SOURCE_SAFETY_TESTS.mjs | 5e8e114d0dfbfe6d1aad55552014144562bc33f8 |

**Executed in Code Mode read-only V8 on exact seven GitHub blobs:** 79 deterministic assertions, **79 passed after correcting a test-harness-only third-topic literal-string mismatch**; no source change was needed for that mismatch. **12/12 deliberate synthetic negative modifications were detected**, including removing disclosure, enabling native button, adding seller anchor, injecting script/form, breaking A/B copy parity, opening merchant gate, tampering film timing, adding unsupported price or medical guarantee and fabricating paid conversions.

A first static checker pass had false positives (e.g. counting the literal test-fixture identifier inside the test source itself; treating aria-disabled as a native disabled attribute). **Those were checker issues, not safe-to-release claims.** The committed native test source now uses a strict whitespace-delimited disabled attribute, and it contains seven adversarial mutation tests.

**Authored but NOT EXECUTED:** 37-case portable native Node suite at SOURCE_SAFETY_TESTS.mjs (reproduce from repo root: `node --test mind/r464/SOURCE_SAFETY_TESTS.mjs`). A source check is not equivalent to executing that suite. No hosted CI green state is claimed.

**NOT TESTED:** real-browser WCAG 2.2 AA keyboard/VoiceOver/TalkBack, 360/390/768/1440/1920 viewport layout, CSP/security runtime, Lighthouse/Core Web Vitals, genuine playable MP4 and timed VTT, WordPress Gutenberg sanitizer, native Jetpack subscription confirmation/welcome, social media route/asset IDs, live merchant checkout, affiliate payout/sale reconciliation.

## Editorial and media truthfulness

- Original ~2,086-word source-linked new McGurk essay, not published. A 2018/2019 indexing date confusion for the slowed playback study was corrected to its **2018 journal issue** and authors (Magnotti, Basu Mallick & Beauchamp), with no inflated scientific conclusion.
- A/B pilots contain **byte-identical substantive buyer guidance**. B adds only an original SVG visual and clearly marked 42-second six-cue storyboard/transcript. It is **not** a playable video and no experiment was run.
- Both buyer pages are noindex source files, no merchant domains as clickable anchors, no earning link, no price/coupon/countdown, no script/form/tracker, natively disabled purchase button, adjacent full commission explanation.
- Four-stream hub is source-only Gutenberg-compatible markup, not saved to WordPress, not a published /mind/ route and not a replacement for PR #172.
- Official seller page text offers convenience/formats. Seller's instant mental/health/financial guarantees are not independently adopted or substantiated.
- Public Inspire3 affiliate network and pending Refersion notice (Aug 24) do not establish account-specific permission. Targeted inbox search returned no later approval in that mailbox; other portals/mailboxes could differ. No private identifiers or email content copied into repository.

## Release and revenue ledger

**Status:** BUILT = seven source assets; TESTED = in-memory source assertions and deliberate mutations only; LIVE = referenced preexisting FV routes only; VERIFIED paid sales = none authenticated.

**Blocking P0:** named authorization, allowed exact SKU/channels, official earning URL, checkout terms, reliable refund/settlement records, an actual paid order and a qualified-human denominator. Existing free Fieldbook is not a verified paid fallback. **Net realized revenue per 1,000 qualified human sessions = NOT COMPUTABLE**, not presumed zero.

**Ownership/release:** Mind editorial/commerce writes are isolated to `mind/r464/`. Grok owns content/social posting; Praxxis authenticates real media IDs via TASK-008; Claude owns production analytics/engineering; independent Site QA and founder must approve a release. No live CMS/navigation/settings, existing Jetpack/Dispatch welcome, paid SaaS, Grok queue, homepage PR #49, Mind PR #172, agent Issue #150, merge, deploy or affiliate activation were touched.
