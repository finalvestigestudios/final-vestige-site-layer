# Final Vestige read-only Media Library audit — 2026-11-18 17:23 PST

**Scope and owner:** Media Recovery draft [#2747](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2747). Separate from interim homepage visuals. Aligns with [Site QA's browser collector in #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154). No new browser collector or WordPress writes.

## New concrete evidence

Queried the *connected live WordPress Media API read-only*, all pages (100+32) with image filter and media details. This snapshot contains **132 image media records**. Of these, **20 originals strictly greater than 1,500,000 bytes** total **64,385,752 original stored bytes**; **19** are strictly greater than 1.5 MiB (1,572,864 bytes). There are **10 JPEG and 10 PNG originals** among the decimal-threshold 20. The historical archived `docs/IMAGE-WEIGHT-WORKLIST.md` (archived Git blob `9cdf7af84175883775aaebf55ffa5ca77b33e423`, absent from current branch) described 110 images and 13 larger than 1.5 MiB on October 30. **Different date and different threshold units:** do not misstate as a same-cohort regression.

The [read-only machine ledger](../qa/media-recovery/wp_media_20_oversize_20261118_1723.json) captures **every one of the 20 real WordPress Media URLs, media IDs, original bytes, original pixel sizes, media-attachment parent, known Gutenberg slot where independently documented, WP virtual large variant if provided, metadata credit/copyright text, exact proportional ≤960-pixel-wide candidate dimensions and unknown guest browser status/decoded/transfer**. A parent attachment ID is *not* proof that an asset appears inline.

**Prioritize actual article usage and transfer measurement**, rather than compressing all originals:

| Priority | Live Media ID(s) | Original stored bytes | Visitor measurement |
| --- | --- | ---: | --- |
| Vasa museum / model | 388 | 8,176,362 | Unknown; rights metadata names Karolina Kristensson/Statens Maritima Museer |
| Piri Reis map | 2640 | 7,422,309 | Unknown; no licensing inferred from empty metadata |
| Malbone photos, slots 621:0–1 | 1257, 1258 | 10,352,064 combined | Published source routes are known; actual currentSrc/transfers unknown |
| Five narrative reconstruction PNGs, slots 34:0–38:0 | 39–43 | 13,267,538 combined | WordPress/Jetpack can serve existing derivatives; actual transfer unknown |
| Mesmer engraving | 2636 | 4,462,854 | Media metadata explicitly cites Wellcome CC BY 4.0 with attribution; item-level verification still required |

**Metadata rights watch:** IDs **388, 2636 and 382** carry nonempty copyright statements. Item 382 carries a CC BY 4.0 assertion; ID 2636 contains a fuller Wellcome attribution/CC BY 4.0 caption. Do not strip existing rights/captions, interpret an empty EXIF copyright as public domain, or infer permission to rehost external sources. The ledger holds **all 20** pending record-level reuse checks.

## Sizing and caching plan, no publishing

The audit derives **target width = min(original width, 960)** and **target height = round(original height × target width/original width)**, preserving aspect and never upscaling. Example: Vasa 4256×2832→960×639; Piri Reis 1964×2619→960×1280; Malbone 4000×3000→960×720 and 5667×3831→960×649. Derivatives are *proposals*, not files created. Existing WordPress virtual `fit` URLs are noted; these are not proof of bytes actually delivered. No production Media uploads, Gutenberg rewrites, cache purges, CDP captures, external downloads, or rehosting.

If an individual image is *confirmed* to be downloading unnecessarily large or broken in a guest browser, stage its exact, licensed source and a ≤960px proportional derivative in a **nonproduction** review environment after explicit approval. Preserve historical raster identity, source credit, caption and original permalink; verify responsive source selection, MIME, guest decoded pixels, mobile/desktop screenshots, cold encoded transfer bytes and rollback to previous source. Published Site QA #154 collector owns the browser traces; no competing collector.

## Recovery-source leads, explicitly not automatic replacements

The ledger preserves four archival leads from **earlier research**, not reverified live here: USS Tang slot 274:6 → [Navy 80-G-227989](https://www.history.navy.mil/our-collections/photography/numerical-list-of-images/nara-series/80-g/80-G-220000/80-G-227989.html) (960×647 proposed, exact raster/rights hold); Sunshine Skyway 287:5 → [Florida Memory RC09237](https://floridamemory.com/items/show/32083) (**different photograph**, no automatic swap); Scotch Cap 418:1 → [Coast Guard catalog](https://www.history.uscg.mil/Our-Collections/Photos/igphoto/2002905913/) (identity and rights hold); Teton Dam 291:2 → [National Archives NAID 28894685](https://catalog.archives.gov/id/28894685) (960×675 proposed; distinct from the incorrect cleanup photo). Older origin-retriever 404/403s **are not confirmed guest failures**.

## Engineering QA and acceptance

[Validator](../qa/media-recovery/validate_wp_media_20_20261118.cjs) rejects invented public bandwidth claims, unauthorized writes/rights, off-domain media URLs, incorrect original-byte totals, duplicates, inaccurate proportional derivatives and invented browser HTTP/transfer numbers. [24 native Node tests](../qa/media-recovery/test_validate_wp_media_20_20261118.cjs) exercise the contract. The validator's only success state is **PASS_STORAGE_ONLY**; it cannot authorize a media replacement or publish a 76% performance claim.

Run `node --test qa/media-recovery/test_validate_wp_media_20_20261118.cjs`. **24/24 passed locally**, and the exact test and validator Git blob hashes were independently checked after committing. The live 20-row ledger was separately recalculated and all proposed dimensions/metadata holds checked. Full repository CI and actual guest desktop/mobile CDP image transfers are unrun.

**No premature conclusions:** historic 61/355 inline slots vs current 66/361 stay separate; 42 reported guest-broken images still lack browser proof; 76% image-wire reduction is not measured. This is **20 original stored files**, not 20 oversized visitor downloads, and no change to the public site.
