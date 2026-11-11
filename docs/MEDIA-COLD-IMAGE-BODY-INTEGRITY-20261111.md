# Final Vestige Media — cold image-body integrity and staging handoff (11 November 2026 UTC)

**Scope:** media recovery only. No homepage design, WordPress production writes, downloads, caching, licensing approval, new browser collector, merge, deploy or spend.

## Confirmed engineering defect, not a website incident

Independent replay of the prior draft P0 gate (blob `c8f206a5a8f544dab3a17f632d2105433fcedb58`) with **synthetic** page/source/CDP-bound evidence showed two false-success classifications: (1) HTTP 200 and positive DOM image dimensions with **zero encoded bytes**; (2) HTTP 200 and positive DOM dimensions with **text/html** response. Both were classified `CONFIRMED_GUEST_DISPLAYED`. The corrected draft gate (blob `0828b55819be300f486db3598cfbbb3c24b05353`) returns `HOLD:IMAGE_MIME_LIFECYCLE_OR_BODY_BYTES_NOT_PROVEN` for each, while accepting a full, noncached, positive-dimension, `image/jpeg`, `loading_finished=true`, nonzero-byte synthetic control.

**Verification:** exact postcommit code and test blobs (`0828b55819be300f486db3598cfbbb3c24b05353`, `ee4a6e0049abf4c27d008fe4a54fe8af491bb314`); **95/95 isolated V8 regression callbacks passed**. Native Node CI and genuine logged-out Chromium have **not** run; no new browser HTTP results are claimed.

## Site QA #154: evidence fields to collect in existing collector

For each original published image (not a replacement image), retain actual page permalink, WordPress post, stored source slot, DOM image src/currentSrc, CDP request/response IDs, final URL and status, screenshot SHA-256, cache flags, natural width/height and `Network.loadingFinished.encodedDataLength`. **Newly required to classify a displayed image:** CDP image `resource_type=Image`, MIME from the **final response** (`image/jpeg`, `image/png`, etc.), and an explicit successful `loading_finished=true`, plus `encoded_data_length>0`. Don't infer a clean finish from `responseReceived`; capture `loadingFailed` distinctly. Media Recovery must not duplicate or modify the Site QA collector.

Keep exact priority: **285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1**. Their source-only retriever wrappers (404, 500, 404, 403, 403, 400) are **not origin HTTP statuses**. Guest HTTP status, browser-selected URL, MIME and transferred bytes all remain **unknown**; the historical 42 broken images are not guest-confirmed.

## Rights / scene / resizing release gate

The machine audit records each exact original URL, archival/publisher candidate, item-specific rights observation, and `null` for actual guest HTTP, bytes and unverified native dimensions. Candidate status remains **HOLD** pending same-image identification, historical scene/date/crop verification, commercial reuse permission and necessary attribution, appropriate captions/ALT, editor approval and staging screenshot comparison. For **285:5**, the Commons original is 819×614; no automatic upscale to 960px or cropping to the SayMedia 16:9 transform. For maps, preserve label legibility and full-resolution access. Cache/rehost only after item-specific clearance and staging QA, with original URLs and rollback mapping retained.

## Performance / 76% measurement

The historic 61/355/288 image research scope differs from expanded 66/361 WordPress live census. Fifteen originals **>1,500,000 stored bytes** total **47,096,779 stored bytes**; 11 inline-matched originals across 8 posts account for **38,480,915 stored bytes**. These are **not visitor-network bytes**. First measure post 621 Malbone direct originals and posts 34–38 no-subsize PNGs, then Jetpack-served Vasa 299 and Halifax map 269, ensuring no unsupported photo replacements or unreadable map labels.

For one article and otherwise identical cold Chrome sessions with full scroll, comparable viewport/DPR and network tracing, calculate `100*(sum_baseline_image_wire_bytes - sum_candidate_image_wire_bytes)/sum_baseline_image_wire_bytes`. Exclude cached/failed/incomplete captures and do not mix different post cohorts. Image identities must remain the same or be explicitly reviewed as substitutions. **76% is an unmeasured target**, not a measured saving. No preemptive resize/download/deletion is authorized.

[Exact six-source and fifteen-media machine-readable audit](../qa/media-recovery/p0_response_mime_and_15_oversize_handoff_20261111.json) · [Existing Site QA draft](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154) · [Media recovery draft](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1703).
