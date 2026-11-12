# Live WordPress P0 / P1 image source readback — Nov 11 Pacific

Read-only source validation on **13 published post bodies / 58 inline tags**, out of **66 published posts**, and the current **122-item image Media Library**. This does not test real visitor images. The worklist exists in draft #183, not main; Site QA #154 retains the sole guest browser collector.

- All **6/6** P0 suspected third-party source URLs still appear unchanged in live Gutenberg post positions. Actual browser status/decode/transfer unknown. Prior retriever wrappers are **not** HTTP origin or browser evidence.
- All **11/11** previously identified oversized inline originals remain embedded in 8 published posts; **15/15** WordPress originals still exceed 1.5 decimal MB, totaling **47,096,779 stored bytes**, of which **38,480,915** belong to those eleven. Four additional originals must not be deleted or presumed unused.
- Media original storage now **70,627,679 B**, up **72,773 B** from the earlier 121-item snapshot; the difference matches new small media **#2267** (500×668 NARA Zimmermann Telegram JPEG, 72,773 B). Stored bytes are **not browser transfer bytes**.
- Proposed **76%** reduction is unmeasured; **42** historically reported broken originals remain guest-unconfirmed. Conditional 960px dimensions and item-specific copyright/scene-review gates hold; no third-party binaries cached, downloaded or uploaded.

See [machine-readable record](../qa/media-recovery/live_cms_priority_readback_20261111.json), [fail-closed validator](../qa/media-recovery/validate_live_cms_priority_readback_20261111.cjs), and [16-case Node-compatible regression suite](../qa/media-recovery/test_live_cms_priority_readback_20261111.cjs). No WordPress writes, homepage edits, production repair, merging, deployment or subscription spend.
