# Apollo R144 — published-gallery media provenance and no-JS custody (STAGING HOLD)

**Governance:** Experience 2.0 #150, commercial #820/#818. Isolated source-controlled QA stacked on R143 PR #1112 (base `460101c1f0acd82918c9b7a1099638666f61e93c`). No homepage PR #49, Research Desk PR #158, Claude production branches, WordPress, merchant, Grok, Praxxis or analytics writes.

## Read-only source of record (November 5, 2026)

WordPress **published page 2017**, `https://finalvestige.com/apollo-1-evidence-atlas/`, modified **2026-11-04T17:09:24**, returned 96,274 characters of raw page content. R144 was evaluated against that actual retrieved content, **not** against a made-up production snapshot.

The page contains exactly three `figure[data-fvx-chrono-photo]` in slots 0,1,2:

| Slot | NASA record | Original archival source | On-page use |
| --- | --- | --- | --- |
| 0 | S66-58038 | https://www.nasa.gov/image-detail/amf-s66-58038/ | Pre-fire crew training, Oct 18, 1966; **not** fire footage |
| 1 | S67-15717 | https://www.nasa.gov/image-detail/amf-s67-15717/ | CSM-012 processing, January 1967; **not** emergency footage |
| 2 | KSC-20170124-PH_KLS01_0129 | https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0129 | 2017 display of original hatch, not the 1967 fire |

The page's NASA Apollo 204 Review Board link, per-image original source links, exact expected image asset paths, nonempty descriptive alternatives, explicit image dimensions, contextual captions, gallery caveat, no-JS figure availability, hidden optional slider and CSS hidden guard all passed the R144 **source-level** checks.

**Unresolved live defect:** `const photos = $(box, '[data-fvx-chrono-photo]');` still exists in published source. The selector `$` returns a single Element, so the list-based gallery switching does not activate. R143 isolated the one-character `$$` repair in a draft branch; R144 correctly reports `PUBLISHED_GALLERY_ENHANCEMENT_DEFECT` and remains release HOLD. **No WP repair was deployed.**

## Actual current-source audit receipt

```json
{
  "source": "WP page 2017, modified 2026-11-04T17:09:24",
  "photoCount": 3,
  "records": ["S66-58038", "S67-15717", "KSC-20170124-PH_KLS01_0129"],
  "sourceAndStaticGalleryIntegrity": "SOURCE_PASS",
  "selector": "BROKEN_PUBLISHED_SELECTOR",
  "blockers": ["PUBLISHED_GALLERY_ENHANCEMENT_DEFECT"],
  "commercialMediaRights": "NOT_APPROVED",
  "release": "STAGING_HOLD"
}
```

## Media-rights boundary

NASA's official `https://www.nasa.gov/nasa-brand-center/` and `https://www.nasa.gov/nasa-brand-center/advertising-guidelines/` prohibit implied agency endorsement and restrict advertising uses involving identifiers or astronauts' likenesses. NASA gallery index independently lists S66-58038 and S67-15717 (`https://www.nasa.gov/gallery/apollo-1/`). This is **not** individual commercial rights clearance, and no image shall be bundled into, used to advertise, or licensed with an FV paid educator product pending documented rights review.

The on-page note says **editorial use only**; this QA enforces it and refuses a Payhip/checkout call-to-action inside these uncleared gallery records. It does not conclude that all 3 images require the same permissions or that editorial display violates NASA policy.

## Implemented, reproducible commands

```bash
node --test experience2/apollo-creator-bridge/test_r144_gallery_media_custody.cjs
node experience2/apollo-creator-bridge/r144_gallery_media_audit_cli.cjs /path/to/read-only-wp-export.html
```

The second command **only reads** a supplied export, writes no files or network requests, prints deterministic JSON, exits 2 on blockers, exits 64 without input. R144 has 12 adversarial tests for original sources, missing/duplicated photographs, alt text, image dimensions, no-JS, context warnings, promotional links and the broken selector.

**Exact committed file blobs:**
- `r144_gallery_media_custody.cjs`: `5bac16dcefc96a089a829e50b4f6939da7ccbf3c`
- `test_r144_gallery_media_custody.cjs`: `9b171d78efd6bfa8aa55c4a86dadd9b05daf689e`
- `r144_gallery_media_audit_cli.cjs`: `929abf89a139f5ba682292d49ceeb80dc48b0413`

Local Node v22.16.0: **12/12 PASS**; hashes of the tested local module and test file matched the committed Git blobs. The committed exact module evaluated in memory on the actual WP export yielded the receipt above. Hosted CI exact-head **not verified**.

**Browser limitation:** Chromium v144 returns `net::ERR_BLOCKED_BY_ADMINISTRATOR` for direct HTTP/HTTPS/file/data navigation in this environment. No actual WP Playwright, real-page axe, Core Web Vitals/LCP/CLS, screenshots, image-transfer acceptance or manual screen-reader results are claimed. Prior synthetic Chromium fixtures are not real-page acceptance.

## Conversion-first path / owners

**One relevant existing action:** proposed Grok YouTube long-form Apollo 1 audience → published Atlas → **Read the full investigation** → approved educator evidence kit **only if verified sellable and rights-cleared** → reconciled Payhip order. Do not use gallery as an unrelated commerce surface, add an unavailable worksheet CTA, count CTA clicks as paid sales, or distribute a Grok asset without proof and founder authorization.

| Offer → step | Blocker | Change / experiment | Pass / fail evidence | Owner |
| --- | --- | --- | --- | --- |
| Educator dossier → purchase | No verified Apollo SKU/rights/fulfillment | Independently audit inventory and terms before CTA | **HOLD; no merchant proof** | Claude/Growth/Founder |
| Grok → Atlas | Actual per-asset campaign/published links unverified | Reconcile TASK-008 and canonical URL | **NOT VERIFIED** | Grok/Praxxis |
| Atlas gallery → source trust → article | Published selector broken; rights uncleared | R143 selector repair + R144 provenance/no-JS guard | **R144 source PASS except live selector; STAGING HOLD** | Apollo/Claude |
| Paid order → net revenue | No attributable paid order/refund/fees or qualified sessions | Existing #820 7/30-day scorecard, no duplicate script | **NOT COMPUTABLE** | Claude/Analytics |

Pending gates: review/document photo-specific promotional rights, approve sellable educator SKU, independent history review, approved WP staging integration, actual-page 320–1920 browser/axe/keyboard/touch/no-JS/LCP/CLS acceptance, exact-head green CI, founder release. Nothing is live through this PR.
