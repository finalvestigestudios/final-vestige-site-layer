# Final Vestige source image recovery — live eight-post Part 02 readback (November 12, 2026)

**Scope:** Authenticated WordPress `posts_get(context=edit)` read-only scan of frozen Oct-30 Part 02 (post IDs 413, 407, 370, 367, 330, 299, 292, 291), from PR #183 blob `48e1ebf07207e948ba5802e714eb39659d2e1c1d`. Exactly 59 literal image tags, compared slot-for-slot with frozen URL, ALT, HTML width/height and `srcset`. Candidate catalogs and conditional 960px sizes are pinned to the 288-source ledger blob `4965a862f7de7de46c1f4a1e26f3ca70a8c38805` (draft #1703). This is not a guest-browser HTTP or CDN response measurement.

## Findings
```json
{
  "posts": 8,
  "images": 59,
  "frozen_images": 59,
  "src_equal": 59,
  "src_drift": 0,
  "missing_width_height": 38,
  "has_both_width_height": 21,
  "partial_width_height": 0,
  "alt_changed": 0,
  "candidate_slots": 32,
  "srcset": 0
}
```

Source drifts (if any): []. ALT changes since frozen audit: []. Missing width/height attributes only indicate absent markup hints, **not** measured CLS or blur. Do not rewrite post blocks or add invented dimensions.

The original six P0 guest-browser suspected missing-image queue remains owned exclusively by Site QA #154: `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`. This batch overlaps existing 407 source readback solely to preserve the intact frozen Part 02 cohort. Actual origin/guest HTTP statuses, image decode, network bytes, rights approval, and hash-identical replacement are **unknown**. Any source drifts need current editor review before a replacement plan.

For 15 WP originals exceeding 1.5 decimal MB (47,096,779 **stored** bytes), including Vasa post 299, avoid claiming a 76% network reduction absent controlled cold guest baseline/candidate transfers and pixel-parity checks. 960px is an upper width only where source resolution, displayed CSS × DPR, crop and map/diagram legibility allow. Candidate URLs are research leads, never implicit licenses. Cache or WordPress upload only after item-by-item rights clearance, exact scene matching, staged mobile/desktop QA and rollback plan.

**Policy:** no asset downloads/caching/rehosting, public WordPress writes, risky Gutenberg rewrites, homepage design changes, Site QA collector duplication, merge, deployment, or spend. Draft only.
