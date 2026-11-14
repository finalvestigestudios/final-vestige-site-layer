# Nine-image source-custody gate — 14 November 2026

This is an isolated **review-only** correction on media draft #1655; Site QA #154 retains browser testing. The existing nine-item audit [includes exact source and catalog URLs, tentative 960px/no-upscale dimensions and null guest HTTP/transfer bytes](../qa/media-recovery/image_density_preflight_nine_20261114.json).

**Reproduced defect:** the offline density validator pinned source URLs, sizes, IDs and source/catalog hashes, but previously tolerated altering a record's `source_kind`, `provenance_note`, or switching between two allowed `historical_scene_identity` values while returning `source_inventory_valid:true`. This could misrepresent rights or confuse historical-source review; it never authorized production release.

**Correction:** all nine records' editorial custody now has immutable exact labels/notes. Unauthorized edits raise `source_provenance_drift` and invalidate the inventory. Five first-party historical reconstructions, two Malbone images, Three Mile Island 285:5 and Scotch Cap 418:2 are covered. The new 33-case test file adds 1 baseline + 27 record/field mutations + five adversarial cases. Existing 42-case density tests remain separately applicable.

```bash
node --check qa/media-recovery/image_density_release_gate_20261114.cjs
node --test qa/media-recovery/test_image_density_release_gate_20261114.cjs qa/media-recovery/test_image_density_source_custody_20261114.cjs
node qa/media-recovery/image_density_release_gate_20261114.cjs qa/media-recovery/image_density_preflight_nine_20261114.json
```

**HOLD:** all nine guest-browser HTTP statuses, natural-image loads, actual CSS/DPR transfer bytes, copyright reuse determinations, downloaded binary identities and staged replacement approval remain unknown. The historical 61-post/355-image baseline, reported 42 failures (unconfirmed), proposed 76% network reduction (unmeasured) and latest 16 oversized originals totaling 49,107,665 *stored* bytes remain separate. No rights granted, binary fetched or cached, WordPress production content rewritten, homepage altered, deployment, merge or subscription spend.
