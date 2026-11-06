# Apollo R171 — NASA caption readability and custody | STAGING HOLD

**2026-11-06 | BUILT + offline real Chromium TESTED; NOT WordPress-tested or approved for release.**

Read-only WordPress Page 2017 `/apollo-1-evidence-atlas/` (modified 2026-11-05 18:19:45) contains three NASA archive figcaptions with no HTML whitespace between the bold title, narrative and small NASA credit. On source-derived 390px Chromium, a failed-image view makes the title and body run together (`The crew before the testNASA...`), and original source attribution becomes cramped. This is a **fixture visual finding**, not proof of live theme rendering.

## Implemented
- `apollo_caption_readability.py`: exact-SHA guarded semantic markup transform for only the three NASA figcaptions, with explicit title/body/source separation and whitespace preserved without CSS or JavaScript. Unrecognized source drift, forged URLs, modified caption content and duplicate entries fail **HOLD**.
- `apollo_caption_readability.css`: local component-only typography and block flow, accessible NASA source links in forced-colors; no tracking, links, or additional products.
- `test_apollo_caption_readability.py`: real Chromium fixture tests with six widths (320/360/390/768/1440/1920), JS/no-JS, keyboard Home/End, touch-capable viewport, reduced motion, forced-colors, failed-image nonoverlap, source link/CTA preservation, text-size checks, screenshot hashes, and laboratory LCP/CLS observations. Negative controls deliberately corrupt original captions and NASA destinations; rejection expected.

The existing source files are `../apollo-r166/verified_gallery_excerpt.html`, `gallery-independent.*`, `gallery-fallback.*`, `gallery-fallback-flow.r167.css` and optional `../apollo-r168/archive-accessibility.r168.css`. No local versioned duplication. To test from a checked-out stacked branch:

```bash
cd experience2/apollo-r171
python -m unittest -v test_apollo_caption_readability.py
python apollo_caption_readability.py ../apollo-r166/verified_gallery_excerpt.html /tmp/r171-preview.html
```

## Evidence and release integrity
Three official records unchanged:
1. S66-58038: 1966-10-18 training https://www.nasa.gov/image-detail/amf-s66-58038/
2. S67-15717: 1967-01-03 spacecraft processing https://www.nasa.gov/image-detail/amf-s67-15717/
3. KSC-20170124-PH_KLS01_0129: 2017-01-24 museum display https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129

None is contemporaneous imagery of the 1967-01-27 Apollo 1 fire; fire chronology derives from NASA Apollo 204 Review Board primary records. NASA photo rights **not individually cleared for commercial FV product advertising**; preserve nonendorsement.

**Release blocker:** R169/R170 executable/source custody validators correctly reject caption changes until the approved-delta contract is explicitly reviewed and updated. Do not bypass those guards or apply the patch directly. No genuine axe-core or screen-reader test, installed WP staging (WordPress.com plan staging availability unresolved), CDN image delivery, CSP, hosted exact-head CI, or real-site Core Web Vitals. Lab LCP/CLS is **not production**. No WordPress/merchant/Grok/analytics writes or new paid services. Homepage PR #49 and Research Desk PR #158 untouched.

## Conversion-first contract (source of truth #820/#818)
One proposed journey, not an active commerce claim: verified Grok Apollo long-form `asset_id` (none yet attested) → published Apollo Evidence Atlas → **Read original investigation** (only contextual existing CTA) → optional future rights-cleared teacher-ready Apollo casefile **only after SKU/checkout/fulfillment/fees/refunds and founder approval**. No speculative checkout link. Hypothesis: visibly distinct source credits and readable captions increase qualified continuation; this is not measured sales.

| Offer | Funnel step | Blocker | Change/experiment | Pass/fail evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Apollo teacher evidence casefile | Paid conversion | No authenticated sellable rights-cleared Apollo SKU | Verify inventory, checkout and delivery before activating CTA | **BLOCKED** | Claude/Commerce |
| Grok Apollo video | Social → Atlas | Published platform URL/UTM/asset_id unknown | TASK-008 reconciliation, no Grok queue change | **UNVERIFIED** | Grok/Praxxis |
| Free Apollo evidence | Atlas → investigation | Mobile caption and source-credit readability | R171 source-locked semantic typography | **BUILT; OFFLINE CHROMIUM TESTED** | Apollo/Site QA |
| Apollo paid casefile | Investigation → merchant | Offer not approved | Retain existing reading CTA only | **HOLD** | Founder/Claude |
| Verified net revenue | Paid reconciliation | Qualified human session and merchant order source data missing | 7/30 day session→lead→confirmed paid order→refunds/fees ledger | **NOT COMPUTABLE** | Analytics |

Revenue per 1,000 qualified human sessions remains **NOT COMPUTABLE**; click != lead != checkout != paid sale. No unrelated affiliate inserted. Cross-reference Apollo #150, attribution #820 and business charter #818. Do not merge/deploy without explicit governed approval.
