# R468 — Executed exact-source checks, commercial decision and release hold
**Date:** 2026-11-18 PT  
**Branch:** `mind-r468-choice-blindness-offer-eligibility-20261118`  
**Status:** SOURCE-ONLY / DRAFT / NO PRODUCTION WRITE / COMMERCIAL HARD HOLD

## Readback and executed checks

The following **nine GitHub file blobs** were fetched back independently from the isolated branch after their writes and fixes; checks inspected retrieved remote source, not a proposed patch:

| File | Retrieved blob SHA |
| --- | --- |
| `THE_CHOICE_YOU_NEVER_MADE.md` | `7ac5ccde41a0c8b06113ca8dc731c2c84d4cd4ad` |
| `ZEN12_A_TEXT_GUIDE.html` | `7ebcf1b374fd1a2b6c9000ed6b63bdbade537506` |
| `ZEN12_B_OPTIONAL_FILM_GUIDE.html` | `afc5766dfb86e1438fbb6eaffce59bbdec7f5730` |
| `ZEN12_POSTER.svg` | `efeffac051bffc924e11eee79ca02bae36272008` |
| `ZEN12_FILM_CAPTIONS.vtt` | `e4ca10cf245a9999c6df8e9393b5110bdea104a8` |
| `MIND_HUB_WP_SOURCE_ONLY.html` | `e21b274a52229efe38a96a84df5f0316a8edebb7` |
| `CLAIM_PERMISSION_AND_REVENUE_MATRIX.json` | `ae3092114039aefc95759d983adfa88a0e62e174` |
| `OFFER_TO_REALIZED_NET_REVENUE_ACCEPTANCE.md` | `4cc6273b6c7fd420b48a323dd2614f332f2b4c4c` |
| `qa.test.cjs` | `71048b8f9ef7602904350cb9adaa47929229ecc4` |

**Actually executed:** 42/42 deterministic read-only JavaScript/V8 source assertions passed on these exact retrieved source bodies; eight negative synthetic safety mutations were correctly detected (merchant link insertion, native enabled button, missing commission notice, script injection, capture form, text A/B drift, opening a merchant gate, and caption alteration). A first pass reported 33/35; the two failures were test-predicate errors—`aria-disabled` was improperly mistaken for the native `disabled` attribute and a mutation attempted to replace absent wording. The predicates were corrected. A later 41/42 check flagged the word “autoplay” inside a *no autoplay* note; the condition was narrowed to an actual media autoplay attribute. The final 42/42 run executed after those harness corrections. Do not present earlier failed checks as successful production testing.

The **22-case Node test suite** is source-controlled in `qa.test.cjs`, with instructions `node --test qa.test.cjs`; this Node suite was **authored but NOT executed** in the native repository runtime. The V8 readback asserts are distinct from the portable Node test results. Do not conflate them.

## Substance and safety of the delivered work

- Original ~2,006-word choice-blindness investigation includes DOI-linked 2005, 2013 and 2014 studies, a Puységur evidence/provenance bridge, scientific limits and a practical free 12-minute source audit. No earning link or unsupported clinical/wealth conclusion.
- Text A and optional-film B contain **byte-for-byte identical substantive purchasing text** after removal of B's optional media `<section>`; the one inserted separator newline was normalized for parity checking. Seller descriptions explicitly distinguished from scientific claims; catalog/package and promotional SKU contexts not conflated.
- B has original SVG poster, `alt` text, `<details>` transcript and six nonoverlapping consecutive caption cues covering 00:00–00:42. It is a **concept, not encoded or playable video**; no autoplay, audio, third-party embed or JavaScript.
- Both guides retain native-disabled purchase buttons, clear **prospective** affiliate wording in the same CTA section, **zero active earning links, prices or promotional countdowns**, no email capture form, no analytics/pixel, responsive focus/reduced-motion CSS and noindex meta. These are source observations only, not browser-certified accessibility.
- Four-stream Mind hub source links only real published destinations or labels unpublished resources without creating false live hyperlinks. The sole Fieldbook CTA points to the pre-existing 52-page /focus/ route, not a second signup.
- Claim matrix has 19 explicit source URLs, 30 product/science/commercial decisions and 30 gates all **HOLD**, with `affiliate_url: null` and no commission/net-revenue assertion.

## Source and commercial eligibility evidence

Official sources checked 2026-11-18:
- https://inspire3.com/ (brand/catalog)
- https://zen12.com/about (standard format/seller benefit claims)
- https://zen12.com/?no-popup=1 (several purchasing packages)
- https://zen12.com/secret/ (separate promotional pitch/discount/clock)
- https://hypnosislive.com/faq and https://brainwaveshots.com/ (distinct products; not Zen12 packages)
- https://pubmed.ncbi.nlm.nih.gov/37205669/ and https://doi.org/10.1371/journal.pone.0286023 (14-study heterogeneous EEG review; not Zen12 efficacy)
- https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking (adjacent material-connection disclosure)
- https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance (claim substantiation)
- https://finalvestige.com/focus/ and https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ (existing live free source and existing single opt-in).

Read-only connected Gmail search found the Aug 24, 2026 Refersion **pending application** notice; no subsequent named Inspire3 publisher approval or earning URL was authenticated through the searches run. This is a limited search, not confirmation that no approval exists in some external merchant portal. Promotional consumer emails cannot replace publisher acceptance. No verified FV-owned genuinely paid/rights-cleared Mind product was found. **No actual qualified-human denominators, settled commissions, orders, refunds or net revenue were obtained.** KPI is NOT COMPUTABLE, not `$0`.

## Required checks before founder release

**UNEXECUTED:** Native Node suite; real browser 360/390/768/1440/1920 visual QA, keyboard/screen-reader/WCAG 2.2 AA, reduced-motion/no-JS at actual deployment; WordPress content sanitizer/staging page; Lighthouse/field CWV; encoded playable film/caption playback, actual media licensing; Jetpack confirmed delivery; consent-aware analytics integration with Claude; genuine Grok media IDs and lawful exact mobile routes; independent seller purchase/refund checkout testing; publisher channel approval and settled purchase attribution. The source-only hub is *not* a saved WordPress draft.

**Hard prohibitions:** No publication, CMS or navigation writes, homepage PR #49 changes, canonical Mind PR #172 changes, Issue #150 owner edits, Dispatch campaign rewriting, Grok queue edits, new paid tools, affiliate link activation, social posts, email sends, deployed scripts, live merchant transactions, merging or release. Founder retains commercial/production authority; Claude owns core site and measurement engineering; Site QA independent acceptance.

**Decision:** PR is safe to circulate as a DRAFT for source/editorial/UX review, **not approved to merge or deploy**. Next useful work should close partner/paid-product evidence and the existing funnel's confirmation/settlement tests rather than multiplying inactive sales pages.