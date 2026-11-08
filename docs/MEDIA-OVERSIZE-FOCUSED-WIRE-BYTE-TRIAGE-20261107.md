# Final Vestige media triage — oversized originals crossed with actual editor-source inline references
**Audit: 2026-11-07. Source cohort: 2026-10-30 (61 published posts, 355 raw img sources).**

This is a **read-only replay** of the original WordPress library/source audit at commit `f69a12cd9241ea0f39cfcb74c669bb6f7fb10357`, not a new visitor-browser result. The [machine-readable crosswalk](../qa/media-recovery/oversize_inline_61x355_20261107.json) contains **ten input blob SHAs**, every original URL, owning post permalink/slot/ALT when matched, real original-byte counts, measured Media Library pixel dimensions, candidate max-960px no-upscale dimensions, and explicitly null network statuses and bytes.

## A concrete optimization queue, not an assumed 76% saving

**13 original Media Library assets larger than 1.5 MiB occupy 43,522,829 bytes of original storage.** Exactly **7** raw inline `img src` references match those originals in the 61-post cohort, representing **23,619,602 original storage bytes**; the other 6 originals total **19,903,227 bytes** but **have no matching raw inline `src` in this cohort**. That does **not** imply unused elsewhere: featured images, CSS backgrounds, new posts, product pages, `srcset`, blocks and responsive variants could still use them. Original storage and page wire bytes are categorically different measures.

**P1 capture priority: five PNGs without a recorded 1024-pixel proxy variant.** These are published article source slots `34:0`, `35:0`, `36:0`, `37:0`, `38:0`. Their original 1672×941 files account for **13,267,538 storage bytes**. They may already be transformed at runtime; check on logged-out guest desktop/mobile before proposing any file changes. If and only if justified, a dimension-preserving cap would be **960×540** pixels, subject to quality and source-rights review.

**P1 capture priority: two first-party Malbone JPEGs.** Article [Six Miles an Hour](https://finalvestige.com/2026/08/23/six-miles-an-hour-malbone-street-wreck/), slots `621:0` and `621:1`, references originals totaling **10,352,064 storage bytes**. Both have known 1024-pixel **Jetpack URL candidates**; **neither is verified as the actual guest-browser `currentSrc`**. Candidate no-upscale geometry: **960×720**, **960×649**. Direct original URLs and existing proxy URL strings are in the ledger.

**P2: six originals with no matching inline source** should not become speculative recompression work based on the 61-post audit. Re-check live runtime and other contexts before ranking them.

## Coordination: Site QA #154 remains the browser owner

The current external-image P0 queue `285:5`, `285:2`, `287:5`, `418:1`, `418:2`, `407:1` must take precedence over these P1 size checks. Pass the next seven inline original slots to **the existing Site QA guest Chrome/CDP collector**, not a parallel collector. For both desktop and mobile: report actual `currentSrc`, actual HTTP response/redirects, content type, image load/decode and natural dimensions, CDN/Jetpack rewriting, encoded transferred bytes, LCP/CLS, full-scroll lazy completion and screenshot. A tool's 400/403/500 wrapper failure is not browser evidence.

The reported **42 broken images are not verified**. The claimed **76% image-weight saving is not measured**, and **the two-image discrepancy between Site QA's original 286 offsite sources and Media Recovery's 288 remains unresolved**. The working 66-post/361-image inventory is a later cohort; don't compare it as a matched before/after study.

## Reproducibility and release gate

From the PR checkout, run:

```sh
node qa/media-recovery/validate_oversize_inline_20261107.cjs
node --test qa/media-recovery/test_oversize_inline_20261107.cjs
```

The validator enforces exact storage/cohort totals, source blob IDs, specific seven slots, geometry ≤960px without upscaling, rights/WordPress holds and null browser claims. Twenty negative mutations are included to prove fail-closed behavior. This draft does not depend on #183's 877-commit diff, touch any homepage design or alter Site QA's collector.

**Release policy:** if a genuine visitor failure or material wire-byte bottleneck is established, confirm image identity/crop, ownership/licensing, attribution and intended context before producing a test derivative. Upload to **staging only** after applicable rights and separate editorial approval. Preserve caption, context and accessibility. No automated Gutenberg block rewrites; no WordPress production writes, media downloads or paid services during this audit.
