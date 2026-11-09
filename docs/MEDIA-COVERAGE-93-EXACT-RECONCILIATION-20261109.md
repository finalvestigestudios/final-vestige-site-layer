# Media recovery: exact-source coverage reconciliation (2026-11-09)

**Actual newly verified finding:** Prior progress notes counted **94** independently researched external image positions, but this was a one-row overcount. [USGS batch](../qa/media-recovery/usgs_407_418_eight_20261109.json) includes `418:5`, already present in the [coastal batch](../qa/media-recovery/coastal_scotch_cap_prinsendam_12_20261109.json). Earlier recognized overlaps `418:1` and `418:2` between the 43-source baseline and coastal batch are unchanged. All **three** overlapping sources have literal-URL matches to each other and the frozen 288-position upstream inventory.

The reliable coverage is **93 distinct researched external image positions out of 288**, **195 without individual source research**, from **96 research observations** across seven batch files (43 + 7 + 18 + 12 + 4 + 4 + 8 = 96; 3 duplicate-position observations). There were **zero original-URL discrepancies** in the joined records.

## What was delivered
- [Machine reconciliation](../qa/media-recovery/coverage_93_exact_reconciliation_20261109.json): each of 93 exact original URLs linked to the original source batch, branch, immutable Git blob, observed *retrieval-tool* outcome, catalog candidate/claimed dimensions when available, mandatory item-specific rights HOLD, NULL guest HTTP/decode/bytes/broken result, and disabled asset/WordPress actions.
- [Fail-closed validator](../qa/media-recovery/validate_coverage_93_20261109.cjs): compares all rows to the immutable 288-row Oct 30 host census, enforces exact source/post/host and per-batch evidence counts, three overlaps, known Git blob SHA custody, no upscaling or invented rights or visitor measurements.
- [Regression suite](../qa/media-recovery/test_coverage_93_20261109.cjs): one positive whole-corpus case and 23 adversarial cases (source swap, duplication, forged failure, fabricated 76% savings, unauthorized cache/WordPress writes, invented 960px geometry and rights clearance).

These are **source research slots, not proven broken images**. Independent retriever 403/404/502 errors are not real final origin status or guest Chromium evidence. No image transfer measurements exist to substantiate the 76% projection; 15 WordPress originals >1.5 decimal MB total 47,096,779 **stored** bytes, not wire bytes. Historic 61 posts/355 refs/288 external origins and separate later 66 posts/361 refs must never be interchanged for baseline comparisons.

## Next highest-value action, delegated to Site QA
Preserve [Site QA #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) ownership of its existing full-scroll guest Chrome collector and check P0 sources `285:5,285:2,287:5,418:1,418:2,407:1`, followed by `407:3` and the correlated Florida Memory post 432 redirects. Require actual uncached response chain, Content-Type, real encoded transfer bytes, intrinsic decoded dimensions and visual screenshots before asserting failure or replacement. Rights must be individually cleared and original historical scene preserved before preparing any ≤960px no-upscale derivative. Any potential approved WordPress restoration must use a verified, rollbackable attachment/ALT/caption record; this PR authorizes **none**.

No binary download or rehosting, WordPress live write, Gutenberg rewrite, homepage visual design change, merge or subscription spend.
