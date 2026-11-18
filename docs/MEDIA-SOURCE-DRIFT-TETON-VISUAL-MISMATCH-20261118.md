# Media Recovery: 61→66 offsite reconciliation + Teton wrong-scene P0

Date: 2026-11-18. Status: **DRAFT / REVIEW ONLY; no WordPress production writes or media rehosting**.

## Method / provenance

Read only [Site QA #154’s 2026-10-30 CSV](../qa/media/cms_image_census_20261030.csv) from branch `qa/media-source-dependency-20261029-2347`, Git blob `76aa63ffaa299a6e6878edc1b66e637fa6f058ab`, and the nine pinned [66-post 2026-11-17 VIEW JSON slices](../qa/media-recovery/) listed by their exact blob SHA in the [machine ledger](../qa/media-recovery/source_61_66_route_drift_duplicate_1222_20261118.json).

Historical cohort: **61 posts, 355 image slots, 286 offsite source routes**. In 2026-11-17, those same 61 post IDs have **355 image slots but 288 offsite source routes**. Only two posts differ in the per-post offsite count: **285 Three Mile Island (5→6)** and **291 Teton Dam (5→6)**. New posts 1917/1920/1922/1924/1926 add **6 offsite image slots** (post 1922 is image-free), giving **66 posts, 361 images, 294 offsite routes** in the newer source inventory.

**This resolves the apparent discrepancy between the 286 in #154 and 288 in the earlier worklist without re-labeling the historical evidence.** The newer 288 is the _shared 61-post cohort at a later VIEW snapshot_, not proof that the 2026-10-30 CSV miscounted. The October per-slot URLs were not preserved in the aggregate CSV; exact changed images and causes of drift cannot be proven.

Route types in the newer VIEW ledger: **154 third-party direct + 140 third-party via first-party Jetpack + 67 first-party Jetpack = 361**. Offsite here means _upstream origin dependency_, not necessarily an offsite visitor network GET or live broken image.

## High-priority real visual-integrity finding (post 291)

The 66-post source ledger includes **two image slots pointing to exactly the same original and published Jetpack URL**:

- `291:2` alt: “Growing breach in Teton Dam during the final hour before collapse.”
- `291:5` alt: “Aftermath of the Teton Dam failure and downstream cleanup in Idaho.”
- Exact original: `https://cloudfront-us-east-1.images.arcpublishing.com/deseretnews/PLWPL72QKJB7BBFJWTXJWVK6QQ.JPG`

On November 18, an independent public image retriever **displayed that original as black-and-white, street-level sidewalk/debris cleanup—not a growing dam breach**. This is a **source-photo-to-caption mismatch for 291:2** independent of any guest-browser failure claim. It may fit the _aftermath_ caption of 291:5, but exact event/location/copyright provenance is not established. The retriever returned an image rendering but no numeric final HTTP status or visitor Jetpack decode. Do not claim a numeric 200, 404, or browser broken status.

The only other identical-origin duplicate in 361 slots is `213:2` + `213:6`, a Mann Gulch staff-ride map used for two feature callouts; **review, not an automatic error**.

**Archival candidate mapping for 291:2 (not approved replacement):** [National Archives RG115 Teton Dam chronology](https://text-message.blogs.archives.gov/2016/05/31/the-unforgettable-calamity-40th-anniversary-of-the-teton-dam-failure/) identifies two source photograph accessions: **NAID 28894684** (enlarging breach) and **NAID 28894685** (breach reaching crest). Both are thematic sources, not claimed exact-pixel matches. Individual item rights, caption, photographer, asset dimensions and reproduction terms are still **HOLD**. A USGS [official disaster study](https://www.usgs.gov/publications/flood-southeastern-idaho-teton-dam-failure-june-5-1976) establishes context but is not an asset license.

## No risky remediation

Site QA #154 owns guest desktop/mobile Chromium collector: verify post 291 slots **2 and 5** rendered `currentSrc`, final GET/redirect, decode, screenshot and actual CDP transfer bytes. Editorial lead then determines whether to correct caption or separately approve a primary-source replacement. Never silently switch photos: independently verify exact image, legal reuse, photo credit, alt text context and caption accuracy. If editorially approved, prepare only **≤960px proportional no-upscale** image via a permitted download, stage a reversible WordPress Media plan with original slot/URL backup and no full Gutenberg block rewrite; production remains **HOLD**.

All **42 reported missing guest images** and **76% sitewide bandwidth-savings claim** remain unverified. The >1.5 MB original-media worklist is stored original sizes, not measured visitor wire bytes. No licensed media downloaded/rehosted, WordPress writes, homepage visual work, merge/deploy or spend.

### QA/code acceptance

- [Machine-readable 66-post census drift and 12 exact changed-post URLs](../qa/media-recovery/source_61_66_route_drift_duplicate_1222_20261118.json)
- [Fail-closed offline validator](../qa/media-recovery/validate_source_route_drift_20261118.cjs)
- [Native-Node-compatible regression test fixture](../qa/media-recovery/test_source_route_drift_20261118.cjs)

Use `node --test qa/media-recovery/test_source_route_drift_20261118.cjs` and existing Site QA collector. Tests only validate audit integrity and safety; they do not assert live browser behavior or rights clearance. The PR remains draft, unmerged and undeployed.
