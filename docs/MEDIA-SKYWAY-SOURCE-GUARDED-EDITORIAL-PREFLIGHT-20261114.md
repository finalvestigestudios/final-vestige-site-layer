# 14 Nov 2026 — Skyway #287 review-only image correction guard

**Scope:** Final Vestige media integrity only; no homepage design, image binary, post edit, WordPress API mutation, merge, deploy, subscription, or sitewide collector change.

## New verified result

Authenticated `posts_get(context=edit)` of **published** WordPress post **287**, last modified **2026-11-02T21:40:01**, returned **six Gutenberg `wp:image` blocks**. All six exact published `src` URLs and the existing ALT/caption pairs of **slots 287:4 and 287:5** were independently matched to the prior two-item visual audit. The new [six-source machine-readable snapshot](../qa/media-recovery/skyway_287_six_live_slot_review_20261114.json) records each URL, current ALT/caption and explicit null guest-browser status, intrinsic dimensions and transferred bytes; blob `d7fe6facf3575ce1592ae48af6b3ea79455fbab8`.

The court-hosted slot **287:4** currently labels otherwise unidentified recovery vessels as `Summit Venture` in its ALT and caption. Recommend neutral recovery-work descriptions. The original publisher-hosted **287:5** uses ALT claiming the later replacement bridge appears; the same publisher's independently viewable moved image shows the *1980 damaged original bridge* and ship. Its existing contextual figcaption is retained.

See [source/ALT/caption review record](../qa/media-recovery/skyway_visual_fidelity_287_20261114.json). The published slot 287:5 URL remains `https://stpetecatalyst.com/wp-content/uploads/2020/04/Skyway-Bridge-documentary.jpg`, while the same-publisher image currently displays at `https://media.stpetecatalyst.com/uploads/2020/04/Skyway-Bridge-documentary.jpg`. The original returned **web-retriever wrapper 404** on 14 Nov; this is **not** a logged-out Chrome/origin HTTP 404. **Do not replace the source URL yet.** The publisher credits University Press of Florida; no local caching, mirroring, rehosting, or assumed hotlink permission.

## New concrete engineering deliverable

`qa/media-recovery/skyway_editorial_review_guard_20261114.cjs` is an **offline read-only preflight**. Given an editor-exported raw WordPress post snapshot and the existing source audit, it:

- Refuses stale post modification timestamps, incorrect post ID/status, unexpected image-block counts or positions, duplicate image/caption elements, or an altered exact URL/ALT/caption at either target slot.
- Refuses invented guest HTTP or byte evidence, purported rights clearance, source URL replacement, auto-apply, or non-review status.
- Produces only **two structured proposed before/after ALT/caption deltas** with post and image-block SHA-256 custody fingerprints; it **never returns edited post HTML and has no network/CMS/write method**.
- Explicitly reports four untouched image slots, zero writes/downloads/derivatives, and approval required. This is an editorial review aid, not an approved repair or a promise of a safe automatic WordPress block rewrite.

Run locally after an authorized read-only export (do not commit full editorial HTML to the repository):

```bash
node qa/media-recovery/skyway_editorial_review_guard_20261114.cjs /tmp/post-287-readonly.json qa/media-recovery/skyway_visual_fidelity_287_20261114.json
node --check qa/media-recovery/skyway_editorial_review_guard_20261114.cjs
node qa/media-recovery/test_skyway_editorial_review_guard_20261114.cjs
```

**Native Node 22 check:** 40/40 assertions passed, including 39 case checks + image-block control, on local source whose Git blob SHA matches the GitHub-committed code. Code blob `548358cb8297c8de5cb3d353a6cfeb59fc9d4206`; tests blob `452394b3146b13dfc10dd311a92e8647a1140463`. The 40 cases use a six-image synthetic article fixture constructed with the real current source URLs, and prior committed audit values. This is **not** a real browser result or a production change. The full live WordPress post was read and independently source-matched, but was not passed to the native local Node process.

## Release and QA gate

Site QA [draft #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) owns logged-out guest Chrome verification of the existing P0 six-source queue **285:5, 285:2, 287:5, 418:1, 418:2, 407:1**; do not duplicate its collector. Before a P0 source change: confirmed actual failure, exact scene/crop, item-specific copyright/reuse/hotlink rights, width / rendered CSS / DPR / retina legibility, conditional derivative width at most 960px **without upscaling**, comparative cold-wire byte measurements, rollback, and separate staging approval. A 960px derivative is not automatically sharp at 1024 CSS px or 2x DPR. No external binaries were obtained.

The historic **61 posts / 355 inline images** remain frozen separately from the later **66 / 361** cohort. The **42 reportedly broken images** remain *guest-browser-unconfirmed*. The proposed **76% image-network reduction** is **unmeasured**. Last verified WordPress image library has **123 originals, 16 >1,500,000 bytes, totaling 49,107,665 stored bytes** (not visitor downloads), including one unpublished draft image. No WordPress media or production post was changed.

**Decision:** two Skyway description corrections are ready for human editorial review once the preflight is rerun against the current post; the source replacement remains **HOLD** until visitor browser and rights checks complete. This draft is deliberately separate from Site QA's existing work.
