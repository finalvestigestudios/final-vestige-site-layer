# FV Media Recovery — 361-slot image source / layout resilience audit
**Evidence date:** 2026-11-18, 20:28 PST work session; **source snapshots:** November 17 WordPress published VIEW, nine immutable Git blobs. **Scope:** QA-only, not homepage design, not Site QA browser collector. **Status:** HOLD; no release approval.

## Source custody and scope
- Historical **61 posts / 355 inline images** from October 30 remains a distinct cohort (Site QA draft [#154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154)). The November 17 pinned WordPress VIEW census is **66 posts / 361 inline images**.
- Historical worklist read from archived branch `qa/media-recovery-reviewed-20261030-1158:docs/IMAGE-WEIGHT-WORKLIST.md`; absent on current draft PR HEAD. Archived tallies must not be silently merged into November 17 census.
- The machine-readable **361/361 full URL/slot mapping** is [all_361_source_slot_risk_20261118_2028.json](../qa/media-recovery/all_361_source_slot_risk_20261118_2028.json); each row preserves exact authored `src`, derived original URL, origin host, post URL/ID, image slot, alt, markup geometry, responsive properties, origin-only response if independently known, and explicit NULL guest response/decode/transfer.
- Every one of the nine Git blob pins was independently checked against the original cohort manifest during this audit. The [offline crosswalk validator](../qa/media-recovery/verify_all_361_source_risk_20261118.cjs) checks all 361 records against the nine frozen VIEW slices. [20 regression checks](../qa/media-recovery/test_verify_all_361_source_risk_20261118.cjs) passed **in V8 with Node-compatible shims against the committed GitHub file readbacks**; native `node --test`, complete CI and logged-out Chromium **not executed**. The V8 crypto stub reused the GitHub-returned blob SHA for source custody, not native SHA-1 hashing.

## Newly reconciled source-markup risk, not measured failures
| Property | 66-post current source count | Meaning |
| --- | ---: | --- |
| Inline image references | **361** | Source image slots, not all CDP Image resources |
| Direct offsite requests | **154** | Additional source-host dependency; NOT proven failure |
| Offsite via Jetpack | **140** | Proxying needs real CDN/guest verification |
| First-party via Jetpack | **67** | Actual selected size still unmeasured |
| No positive explicit width AND height pair | **273** | Possible layout reservation / CLS exposure; verify CSS before claiming CLS |
| No `srcset` / no `sizes` | **301** | Potential responsive payload inefficiency; actual browser selection unknown |
| Direct-offsite missing dimension pair | **152 / 154** | High-value visual-stability review cohort |
| Wikimedia `Special:Redirect/file` image routes | **124** | Redirect-driven dependencies; NOT HTML catalog pages or proven dead URLs |
| URL requested-width hint greater than 960px | **135** | Authored request hints, NOT confirmed decoded/transfer dimensions |

**Highest concentration:** Courrières article #425 carries 8 direct external images lacking explicit dimensions out of 9 inline images. Palomares #367 has 7 directly external images out of 9. The latter count and their priority are derived from frozen source only, not contemporary browser failure rates.

## Material provenance correction during this run
The original JSON's first crosswalk accidentally compared `post_id + ':' + slot` even though probe slot IDs **already include the post ID** (`274:6`). This silently dropped three genuine *original-publisher-only* 404 observations. The validator, 361-row audit and tests now use **exact fully qualified post:slot identity**, checking the separately retained post ID and original URL. Correctly mapped:
- **274:6** — War History Online USS Tang original, HTTP **404 to earlier Nov 18 public retriever**. The same original is published as the article `og:image`, a P0 share-preview dependency. Actual guest and social crawler responses UNKNOWN.
- **285:5** — SayMedia / *China Syndrome* original, HTTP **404 to earlier Nov 18 public retriever**. Actual guest Jetpack response UNKNOWN. No rights-approved exact still replacement.
- **287:5** — St. Pete Catalyst Skyway original, HTTP **404 to earlier Nov 18 public retriever**. Actual guest Jetpack response UNKNOWN. The article's separate Washington Post `og:image` is not this image.
These are **historical observations from November 18 already pinned in the earlier 12-page social-card audit**, **not fresh guest HTTP 404s**. The fix is integrity of the mapping, not proof of a present visitor outage. Teton Dam **291:2** still has the prior same-photo/different-event caption issue, while **291:5** is the correct cleanup context.

## Candidate / copyright / geometric holds
Six official-source leads are preserved in the machine mapping, **none authorized for automatic replacement**:
- Tang **274:6**: Navy image accession **80-G-227989**; provisional catalog-derived proportional **960×647**; exact frame, rights and credit hold.
- Scotch Cap **418:1**: official Coast Guard **210330-G-DE713-0002**; item public-domain/cleared statement subject to individual review; native size and frame hold. **418:2** Coast Guard Museum debris preview **600×463**, **never upscale**.
- Skyway **287:5**: Florida Memory **RC09237** is a **different photo**, NOT an exact replacement; collection PDM is no authorization for silently rewriting history.
- Teton **291:2**: National Archives **NAID 28894685** catalog image 2798×1966; proposed proportional **960×675**, editorial and rights hold.
- Hebgen **407:1**: official USGS J. R. Stacy source; catalog public domain; same-pixel and final native dimensions hold.

Do not download/archive/host a media file without individual item-level source identity, reuse rights, credit/attribution, native dimensions, exact caption/crop review and proposed no-crop/no-upscale image <=960px wide (no arbitrary enlargement). Prefer explicit staged WP Media entry and reversible URL mapping only **after** approval, with checksum and CDN variant verification. **No WordPress production writes today.**

## Required Site QA #154 acceptance (use existing collector, no duplicate)
1. On logged-out desktop/mobile, prioritize **274:6, 285:5, 287:5, 291:2**, then 418:1/2 and 407:1. Record authored src / `currentSrc` / final response URL and redirection, numeric HTTP status, MIME, naturalWidth/naturalHeight, failed decode, screenshot/frame match and trace SHA.
2. For missing markup dimensions, distinguish layout stability from CSS aspect-ratio reservations: capture actual CLS and screenshots before any styling fix; do not touch homepage design.
3. For 154 directly external images and 124 Wikimedia redirect routes, measure actual guest result and hot/cold cache behavior before marking a missing image. Exact image identity and historical frame outrank merely sourcing a similar illustration.
4. For the claimed **76% total image-transfer reduction**, measure **all** CDP Image requests per article (including CSS/background) under the **same** 61- or 66-post frozen cohort, after cold cache reset, on desktop **and** mobile. Count successful payload bytes rather than 404 HTML bodies, compare exact integers `100 * after <= 24 * before`, and independently verify visual parity.
5. The **20 current Media originals >1.5 decimal MB = 64,385,752 stored bytes**, not measured visitor downloads. 19 exceed 1.5 MiB; inspect actual selected `currentSrc` and CDN payload before optimizing or claiming savings.

## Safe rollback / coordination
Existing Site QA #154 remains sole owner of Chromium measurement. Keep interim homepage design work isolated. This draft adds a source-risk ledger + offline verifier only, no new crawler, new images, PR merge, deployment, media rehosting, Gutenberg rewrite, WP production write, paid calls or subscriptions. Any later staged change needs exact original URL/credit/rights/sha256/native-size record, before-and-after screenshot and cold wire trace, explicit editor approval, and an immediate revert plan. **Release HOLD** until real visitor evidence exists.
