# Site image weight: reproducible, guarded browser measurement
**2026-10-30 — draft, non-deployed**. This is the independent media-recovery lane; Site QA PR #154 and homepage design are not changed.

The reported **42 broken original images** and **76% image-weight reduction** are *not verified*. Media Library originals (110, totaling 64,900,772 bytes; 13 >1.5 MiB) are not visitor transfer bytes. Images can be optimized by existing WordPress/Jetpack variants. Do not infer actual weight reduction from media-file sizes.

## P0 visitor-visible image queue
`qa/media-recovery/p0_recovery_queue_20261030.json` enumerates **43 stored image slots across six priority articles**, 36 externally sourced and seven first-party comparison images. Each contains an exact stored URL, post/slot ID, alt text, catalog clue, explicit unknown browser HTTP status and byte counts, item-by-item rights gate, and a ≤960px, no-upscale, aspect-ratio-preserving localization plan. **43 slots is not evidence for 42 failures.** The initial queue captured 16 linked source records; subsequent separate archival ledgers document **source-identity candidates for all 36 P0 offsite slots**, with varying confidence and unresolved item-level rights, binary equivalence and browser availability. A source candidate is **not** a repaired image or permission to republish.

## Strict before/after measurement
`browser_probe_chrome.cjs` (audit schema **v3**) records the final image response HTTP status, MIME, `Network.loadingFinished.encodedDataLength`, cache/service-worker indicators and per-image `naturalWidth`. It explicitly disables cache and bypasses service workers. Re-run on the same six or 61 articles, with the same logged-out Chromium version, **390×844 mobile** or **1440×900 desktop** viewport, and the identical scroll/wait protocol.

**Decoded image safety gate:** When HTML `src` or `data-src` matches an original but browser `currentSrc` selects unrelated content, the stored image is `current_src_identity_unverified`—neither loaded nor broken. A probe `current_src_identity_verified` flag is required before trusting a stored image's decoded result. Response statuses and bytes follow `currentSrc`, not a stale HTML attribute. Unknown responsive derivative identities must be manually reconciled, never assumed.

`compare_wire_runs.cjs` accepts two existing local browser JSON reports (**v3 required**). Every claimed measured slot must match a real Image-network row by active URL/redirect alias, status and encoded bytes; shared DOM uses of one request do not multiply page bytes. It rejects incomplete page sets, broken baseline images, untriggered lazy images, unknown/failed HTTP status, cached image loads, zero bytes, changed source-slot identity, different viewports/browsers and mismatched totals. **Restoration of broken media is an availability fix**, not a compression reduction claim.

```sh
node --test qa/media-recovery/test_p0_recovery_queue.cjs qa/media-recovery/test_compare_wire.cjs qa/media-recovery/test_browser_probe_active_src.cjs
node qa/media-recovery/browser_probe_chrome.cjs --plan
# Only with a network-enabled logged-out QA browser, and before actual authorized improvements:
node qa/media-recovery/browser_probe_chrome.cjs
# Repeat same scope after a reviewed production change. Then compare:
node qa/media-recovery/compare_wire_runs.cjs before.json after.json
```

Formula: `100 * (sum_before_image_encoded_bytes - sum_after_image_encoded_bytes) / sum_before_image_encoded_bytes`; show each post's delta. A synthetic fixture of 10,000 → 2,400 bytes equals 76%, **but is not a FinalVestige.com measurement**. Compare screenshot/HAR and image quality before publishing a number. All licensing/reuse, source credit, historical identity, WordPress upload and post-edit gates remain closed. NASA's official [media guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/) highlight attribution, third-party rights, nonendorsement and recognizable individuals. No WordPress writes were made.


## October 31 — same-image continuity is mandatory (non-deployed comparator fix)

A new adversarial fixture proved a **false performance-win path** in the previous offline comparator: two perfectly valid Chrome network reports could have the same post ID, slot keys, page URL, status=200, decoded currentSrc identity *within each report*, and a synthetic **76%** byte delta, while one report silently substituted a **different historical photograph** in the same image slot. The old comparator checked slot keys, but did not compare the stored image URLs or visible ALT descriptions **between** reports.

`qa/media-recovery/compare_wire_core.cjs` now fails closed with `stored_asset_changed:POST:KEY` or `historical_alt_changed:POST:KEY`, returning `NOT_COMPARABLE` and **no reduction percentage**. The raw stored URL is intentionally exact-match across runs; CDN-decoded `currentSrc` may vary as previously allowed. This conservative same-content comparison can assess optimization with unchanged source references, but **cannot** claim a compression improvement from an intentional image replacement, changed caption, or WordPress media migration without a separate, rights- and identity-reviewed baseline methodology. That restriction is deliberate.

Three new adversarial and positive regression cases were added to `test_compare_wire.cjs`; **30/30 exact-source isolated V8 test replays passed**, with URL/URLSearchParams compatibility shims and source readback. These are not native Node, hosted CI, actual Chromium, or historical-photo fingerprint tests. SHA-256 binary checks and human side-by-side historical identity review remain required for any image replacement. **42 broken**, **76% saved**, image HTTP statuses and visitor transfer bytes remain **unknown**, with **zero live fixes and zero CMS writes**.
