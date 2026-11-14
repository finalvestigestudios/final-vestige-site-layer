# Media Recovery — LOC stereograph evidence custody hardening (14 Nov 2026)

**Draft only. No publication, rehosting, asset caching, WordPress write, homepage-design change, merge, deploy or paid call.**

## Concrete validator defect reproduced

The prior committed [Mount Pelée four-source validator](../qa/media-recovery/validate_pelee_413_loc_20261114.cjs) checked that provenance was at least 45 characters long, but did **not** authenticate its meaning. In an offline replay, the original validator returned `ok:true` when slot **413:3** was rewritten to state that an exact 8 May 1902 early-morning eruption photograph had been authenticated and fully cleared for WordPress republication. It also accepted changing the archive rights advisory to a blanket reuse license, fabricating a guest-browser verification method, and changing the article URL. Those are **synthetic custody mutations**, not discoveries about the live pictures.

The validator now freezes exact per-slot provenance strings and article URL, research method, rights note and 2026-10-30 source snapshot PR identity. Any deviation raises `provenance_or_chronology_drift`, `evidence_custody_drift`, or `source_snapshot`. This is a fail-closed editorial-integrity gate, not a license grant; intentional scholarly correction requires an explicit reviewed ledger and validator revision.

## Four exact original media sources (source inventory only)

| Slot | Original LOC image | Catalog record | Retriever observation |
| --- | --- | --- | --- |
| 413:1 | [LOC 1s41590](https://tile.loc.gov/storage-services/service/pnp/stereo/1s40000/1s41000/1s41500/1s41590v.jpg) | [Item](https://www.loc.gov/item/98504788/) | RETRIEVER_INACCESSIBLE |
| 413:3 | [LOC 1s41518](https://tile.loc.gov/storage-services/service/pnp/stereo/1s40000/1s41000/1s41500/1s41518v.jpg) | Unmatched; do not invent an item number | RETRIEVER_INACCESSIBLE |
| 413:4 | [LOC 1s41424](https://tile.loc.gov/storage-services/service/pnp/stereo/1s40000/1s41000/1s41400/1s41424v.jpg) | [Item](https://www.loc.gov/item/2006688499/) | RETRIEVER_RENDERED |
| 413:5 | [LOC 1s41568](https://tile.loc.gov/storage-services/service/pnp/stereo/1s40000/1s41000/1s41500/1s41568v.jpg) | [Item](https://www.loc.gov/item/2004680426/) | RETRIEVER_INACCESSIBLE |

All retriever observations reflect tool-specific access, **not actual HTTP origin status or an uncached visitor failure**. Source census: 61 posts / 355 stored images; 42 broken original-source reports remain unconfirmed by guest browser; the proposed 76% network-byte saving remains unmeasured. The current WordPress oversized inventory reports 16 originals exceeding 1.5 decimal MB, totaling 49,107,665 **stored** bytes, not actual browser transfers.

The missing LOC catalog match for **413:3** and its 'early-morning eruption' ALT remain editorial HOLD. Maintain full stereograph left/right pairs; do not crop into one eye or claim a 960px rendition is sharp without rendered CSS box and DPR evidence. Width cap is `min(960, native_width)`, preserve aspect ratio, never upscale, and review legibility.

## Release and rights protocol

1. Site QA #154 alone owns six P0 logged-out Chrome checks. Acquire exact `currentSrc`, cold final response status/MIME, natural dimensions, CSS box and DPR, full redirect/cache provenance and encoded transferred bytes before declaring any source broken.
2. Reconcile exact photo/item identity against LOC original, publication/copyright history and item-level reuse guidance; historical 'no known restrictions' descriptions are not a blanket permission. Keep existing source URL, attribution and historical date on the rollback plan.
3. Only after individual rights and visual approval could a first-party WordPress Media derivative be proposed for isolated staging (no third-party scraping). Never overwrite published Gutenberg blocks automatically. Verify old/new appearance at actual breakpoints, network transfer accounting and accessible ALT, then request a separate production-release decision.

Machine-readable [source and prepatch mutation audit](../qa/media-recovery/pelee_413_provenance_mutation_repro_20261114.json) preserves all four exact URLs and null actual guest status. New [regressions](../qa/media-recovery/test_pelee_413_evidence_custody_20261114.cjs) complement, not replace, the prior 34-case suite; the existing Site QA #154 collector is untouched.
