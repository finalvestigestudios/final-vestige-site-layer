# Media recovery — total CDP Image-request coverage (2026-11-18, 16:43 PST)

**Scope:** Read-only QA for published FinalVestige.com article navigations; distinct from interim homepage design. [Media draft #2747](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2747) complements [Site QA draft #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154). Do not create a second browser collector or modify WordPress production.

## Blocking methodology gap identified

The existing `image_wire_parity_gate_20261118.cjs` measures **known Gutenberg inline-image slots**: 355 in the historical 61-post cohort or 361 in the current 66-post cohort. That is a legitimate *inline-images-only* statistic, but it is **not a complete count of the Image resource network transfers** needed to render articles. CSS background images and other separately requested image resources are outside that denominator; zero inline images on post 1922 does not establish that its rendered page downloads zero images.

A synthetic, deliberately **not measured live-site** counterexample shows why the distinction matters:

| Measure | Before CDP image bytes | After CDP image bytes | Reduction |
|---|---:|---:|---:|
| 61 tracked inline-image requests | 6,100 | 1,220 | 80% |
| One untracked CSS background image | 10,000 | 10,000 | 0% |
| **All image requests together** | **16,100** | **11,220** | **30.31%** |

An inline-only gate could pass a 76% goal while the real article-navigation image bandwidth would miss it badly.

## Scoped engineering change

- [All-CDP-image companion gate](../qa/media-recovery/full_image_request_census_20261118.cjs) **consumes the Site QA collector's existing per-page CDP image-request export** plus the existing inline parity report. It does not launch a new browser, fetch images or change published posts.
- [16 native Node tests](../qa/media-recovery/test_full_image_request_census_20261118.cjs) cover both 61/66 cohorts, CSS-background transfer accounting, missing event/slot IDs, duplicate requests, trace mismatch, status/bytes drift, cached images, after-state failures, baseline error-page accounting, exact 76% boundary and independent-review hold.
- [Machine-readable evidence ledger](../qa/media-recovery/all_cdp_image_wire_gap_20261118_1643.json) pins the published P0 origin URLs, earlier same-day public-retriever 404 observations and still-unknown guest status/bytes. Fresh attempts to open four published Jetpack URLs were **inaccessible to the public document retriever**; **no numeric guest HTTP result exists**. Do not classify these as 404s or confirmed visitor failures.

### Companion JSON contract

Provide a sibling object with `schema: "fv-cdp-all-image-requests-v1"`, `cohort_id`, `manifest_sha256`, and `before/after.desktop/mobile`, aligning with the original parity capture. Each capture must repeat the original `trace_evidence_url` and `trace_sha256`. Each post records `post_id`, exact `url`, `complete_image_requests: true`, `cdp_image_events_complete: true`, `cdp_image_request_count`, and an `image_requests` array. Every final CDP Image request must have `request_id`, `resource_type: "Image"`, `final_url`, numeric final `http_status`, `mime`, `decoded`, `transfer_bytes`, `transfer_metric: "CDP_ENCODED_DATALENGTH"`, `from_cache: false`, and `from_service_worker: false`. Supply **all** image requests including CSS backgrounds, not only Gutenberg inline slots; for every inline `request_id` the two exports must agree on final URL/status/MIME/decoded/wire bytes/cache flags.

The guard conservatively HOLDS on missing resources, duplicate request IDs, mismatched traces, unexplained cache/SW loads, missing actual bytes, undecoded **after** requests, or incomplete page coverage. For real baseline 404 images, HTML error bytes do not count as image bandwidth. Use exact `BigInt` byte threshold `after * 100 <= before * 24` on **both** desktop and mobile separately. The companion is **supplementary**, not a replacement for the existing manifest, source-identity, crop, rights, and visual parity checks; **both** offline gates must pass on the same unmodified CDP traces. Even after both, independent screenshot, request-event authenticity, and rights review are required.

The fixture tests contain synthetic post URLs: they prove contract behavior, **not** completeness of the actual WordPress cohort. Native Node tests pass locally, but repository CI and guest Chromium have not run as of this commit.

## Prioritized recovery and publishing safety

First obtain exact guest HTTP/decode/currentSrc/screenshot/transfer evidence for **285:5** (Three Mile Island), **274:6** (USS Tang) and **287:5** (Sunshine Skyway), plus the Teton Dam **291:2** wrong-scene/caption mismatch. Published image proxies were not accessible through a public document retriever this run, and earlier original-source 404s are not proof of a broken visitor image.

Tang's official Navy 80-G-227989 catalog/Commons lead has an original 1910×1288 and proportional 960×647 preview; exact framing, attribution and individual reuse rights remain on hold. Florida Memory RC09237 is **not the same** Skyway documentary still; dimensions unknown, and editorial approval is mandatory before any different-scene replacement. The Three Mile Island movie still has no confirmed unencumbered exact replacement. Re-check all item-level licensing; do not bulk scrape, mirror, or download third-party content.

For any eventually approved exact-raster substitution: archive catalog URL/rights/credit/master SHA-256, retain original URL and caption history, generate proportional derivative **no wider than 960px** with **no upscaling**, stage WordPress Media and reversible rollback **only after separate approval**, and compare real desktop/mobile cold-CDP transfer and visible screenshots. Do not rewrite Gutenberg blocks automatically.

**Status:** historical 61-post and current 66-post cohorts are deliberately separate. Reported 42 visitor-broken images are unproven; 76% total image-wire savings is unmeasured; 20 originals above 1.5 MB total 64,385,752 **stored bytes**, not visitor transfers. No CMS production edits, external media downloads, homepage changes, PR merges, deployments, or paid calls.
