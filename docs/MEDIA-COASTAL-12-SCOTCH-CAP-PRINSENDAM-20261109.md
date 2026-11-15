# Coastal image integrity: Scotch Cap / Prinsendam — 2026-11-09

**Read-only, isolated media research. NO PROD WRITES OR IMAGE DOWNLOADS.** Branch media/triage-43-source-15-oversize-20261109, Draft PR #1703. Existing Site QA PR #154 remains browser-test owner. This batch does not replace the 288-slot census or alter #154 source collector.

## Snapshot and evidence
Pinned frozen WordPress inventory: `qa/media-recovery/offsite_upstream_288_20261109.json`, Git blob `92a904c8da1ace1f972b2f00adf1a4847dde2b99`, 61 posts / 355 inline slots / 288 external-origin image references. WordPress read-only search on 2026-11-09 confirmed both posts **292** (*They Marked the Empty Boats*) and **418** (*The Lighthouse Was Gone at Dawn*) are published; this connector returns sanitized prose without inline IMG tags, so it **cannot** independently reconfirm live image URLs. All twelve literal URLs come from the frozen source inventory, not newly extracted WordPress IMG markup.

New ledger: `qa/media-recovery/coastal_scotch_cap_prinsendam_12_20261109.json`. Twelve slots across two posts; **10 previously unresearched in the 288-row inventory**, **2 preexisting P0 (418:1, 418:2)** kept distinct. Web-tool opens of the exact historical source URLs: **7 images displayed**, **3 retrieval tool 403 responses**, **2 inaccessible**. These are observations from a remote retrieval tool, **not actual browser or origin HTTP statuses**; none establishes a broken visitor image. All visitor fields are null.

## Priority observations

* **Prinsendam 292:3:** Original aviation-history website image *displayed* through the retrieval tool. U.S. Coast Guard official archive `https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002603427/` has a likely same-frame aerial sinking image, **VIRIN 210210-G-G0000-1014**, catalog **2820×1891** pixels, 1.03 MB cataloged (NOT guest transferred), with public-domain release statement requiring credit and DoD visual-information limitations. Conditional downsize **960×644**, pending exact-image/crop visual review and rights confirmation. Do **not** interpret the official 1.03 MB file size as the embedded image's wire bytes.
* **Prinsendam 292:0:** A second, zoomed museum crop of the ship and helicopter *displayed*. Its source filename specifies a delivered **900×675 rendition**, not the museum's native original. Never upscale it to 960; an alternative official Coast Guard image would require careful crop/scene matching.
* **Prinsendam 292:1:** City Archives Rotterdam supplies the 1973 archival image; its official story attributes the photo to **Ary Groeneveld** and dates the vessel passing the Koningsbruggen to **8 April 1973**. It is not a rescue photograph. The City of Rotterdam warns that some image rights are still protected. License/attribution needs item-level clearance before caching.
* **Prinsendam 292:2:** An industrial shipyard image was displayed, but exact ship/launch identity was not independently confirmed from a primary archive. Do not treat the existing narrative caption as independent photographic proof.
* **Scotch Cap 418:0 and 418:3:** Official Coast Guard long-form history illustrates the old/new lighthouse and post-tsunami remains, but the legacy direct image URLs were inaccessible to the tool. The 418:0 URL suffix suggests a 1200×984 rendition (NOT verified catalog dimensions); only after verifying native geometry would a 960×787 version be considered. The official article provides an authoritative **candidate catalogue**, not a verified binary replacement.
* **Scotch Cap 418:1 and 418:2:** Previously researched P0 entries remain on browser testing priority. Independent web retriever got 403 for both. A 403 from that service is **not proof of guest breakage**; 418:2's older third-party lighthousefriends catalog remains a rights hold despite Coast Guard's related original historical account.
* **Scotch Cap 418:4:** Historical tsunami photo on Hawaii Magazine *displayed*, but the original magazine source and any NOAA publication rights require separate checking. The NOAA Hilo archive identified is **topical-only**, not an exact-image match.
* **Scotch Cap 418:5:** USGS S3 photograph *displayed*, showing the devastated **Hilo, Hawaiʻi commercial district**, not Scotch Cap. The article also covers Hawaiʻi and lists USGS Hilo damage imagery, so this is **a placement/alt-text verification instruction**, not a claim that the existing page has mislabeled it.
* **Prinsendam 292:4 and :5:** No authoritative identical photograph has been established. No silent substitution of a different sinking scene is permitted.

## Replacement/local media gate (not permission to publish)
1. Site QA #154 must check **logged-out browser** for each source slot after browser runtime rewrite, response/redirect chain, actual `naturalWidth`/decode, failures, image request transfer bytes and site visual placement across desktop/mobile. Record capture date, final URL, HTTP response, network cache state, browser viewport and device.
2. Confirm photograph identity and historical scene with official item-level archival catalog; obtain independent photographic/crop comparison. A related photograph of the same disaster is **not necessarily** a suitable replacement.
3. Verify item-specific rights/copyright, attribution, archive license terms and USCG/DoD endorsement limitations. No unlicensed wholesale mirroring or third-party scraping.
4. After clearance, propose only the verified image for a local WordPress Media Library copy. Create source/credit/licensing metadata, original binary hash, cropped/uncropped aspect ratio and provenance. If original width ≥960 use a **max 960 px** derivative, except scientific diagrams requiring legibility review; if <960, do **not** upscale. Generate modern-format variants only with explicit source rights.
5. Inspect alt text, caption, editorial placement, responsive behavior, visual similarity, CLS and mobile decode. Use isolated staging and compare pre/post cold-network image transfer. No risky Gutenberg rewrites; use reviewable per-post targeted replacement only after explicit approval.

## Performance methodology / boundaries
The old proposed **76% image-transfer reduction is UNMEASURED**. A test must compare the *same* baseline and candidate post/image cohorts across identical user agent, browser, connection/CPU throttling, viewport, blocked cache, navigation count and network request definitions; total actual bytes from resource responses, cold successful loads, LCP and CLS plus visual parity. The 15 known WP originals >1.5 decimal MB (total **47,096,779 stored B**) are *storage* inventory, not proven visitor transfer or recoverable savings. This sprint does not change those assets, use subscriptions, run native Chrome, install media, or affect homepage visual design.

## Source links
- U.S. Coast Guard Prinsendam catalog: https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002603427/
- USCG detailed Scotch Cap history: https://www.history.uscg.mil/Research/THE-LONG-BLUE-LINE/Article/2866442/the-long-blue-line-standing-a-deadly-watch-75-years-agofinal-hours-of-scotch-ca/
- Rotterdam City Archives: https://stadsarchief.rotterdam.nl/holland-amerika-lijn
- City archive rights notice: https://www.rotterdam.nl/beeld-en-geluid-van-stadsarchief-opzoeken
- NOAA Hilo record (context, NOT identity match): https://prod-01-alb-www-noaa.woc.noaa.gov/noaa-collections/photo-library/pl23theb2705jpg

## QA
`node qa/media-recovery/validate_coastal_12_20261109.cjs`
`node --test qa/media-recovery/test_coastal_12_20261109.cjs`

No production permissions are implied by passing either test. Native Node CI and guest-browser wire proof remain outstanding.
