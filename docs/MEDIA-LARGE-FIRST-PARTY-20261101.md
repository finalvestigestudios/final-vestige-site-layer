# Media Recovery — authenticated oversized-image delivery triage (2026-11-01)

This isolated follow-up to [PR #183](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/183) complements Site QA [PR #154](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/154). It does not modify homepage design or Site QA's existing source scanner/browser scripts. **No production changes, image downloads, subscriptions or image republishing.**

## What was actually checked

Authenticated, read-only WordPress `media.get(context=edit)` returned metadata for **13/13** large originals; `posts.get(context=edit)` confirmed **six** relevant published post records: 34–38 and 621. Their exact URLs, media IDs, original pixel widths/heights, original file byte counts, and `media_details.sizes` state were matched to the frozen prior JSON list. All five early historical-reconstruction images occur as **inline original URLs** and are the **featured_media** of their respective published posts. Each has `media_details.sizes = {}`. The other eight large records have one or more responsive size entries in WordPress. These are actual CMS metadata observations, **not browser GET results**.

| Published post | WP media ID | Original bytes | Original pixels | WordPress subsizes | Conditional derivative pixels |
|---|---:|---:|---:|---|---:|
| [34](https://finalvestige.com/2026/08/16/the-morning-san-francisco-lost-its-water/) | 39 | 2,892,087 | 1672×941 | **No `media_details.sizes` entries** | 960×540 |
| [38](https://finalvestige.com/2026/08/16/the-cisterns-beneath-san-francisco/) | 43 | 2,836,245 | 1672×941 | **No `media_details.sizes` entries** | 960×540 |
| [35](https://finalvestige.com/2026/08/16/the-boat-that-refused-to-die/) | 40 | 2,552,136 | 1672×941 | **No `media_details.sizes` entries** | 960×540 |
| [36](https://finalvestige.com/2026/08/16/the-city-that-went-underground/) | 41 | 2,498,247 | 1672×941 | **No `media_details.sizes` entries** | 960×540 |
| [37](https://finalvestige.com/2026/08/16/how-petra-made-water-flow-through-stone/) | 42 | 2,488,823 | 1672×941 | **No `media_details.sizes` entries** | 960×540 |

The five account for **13,267,538 original bytes (12.65 MiB)**. This is **storage size only**; it is not their summed visitor transfer, nor any estimated or achieved savings.

Across all thirteen originals, **7/13** appear inline in the frozen 61-post/355-source census (these five plus Malbone media IDs 1257 and 1258). **6/13** are not inline in that specific census; do not label them unused, because cards, featured images, pages and templates are outside that count. The Malbone originals have real WordPress 768/1024px derivative URLs and should not be reprocessed without measuring the CDN-selected `currentSrc` first.

## Priorities: breakage before optimization

**P0 visitor-visible failures:** Site QA's guest browser must first check the previously escalated specific URLs: Three Mile Island **285:5** (independent retriever 404), USCG **418:1/418:2** (independent retriever 403), and USGS **407:1** (published source unsupported as octet-stream by retriever). These are not yet proven broken for site visitors; keep HTTP status, decoded image dimensions and browser screenshots **unknown** pending independent guest Chrome.

**P1 first-party weight:** Inspect the exact five post URLs above in a logged-out mobile browser, including `img.currentSrc`, `naturalWidth`, image GET status, MIME, encoded transferred bytes and LCP. Confirm whether Jetpack rewrites the original PNG URLs to smaller CDN derivatives despite missing WordPress `sizes` metadata. Count network requests, not duplicate featured/inline DOM references. Preserve independent baseline screenshot and page-level waterfall before testing changes.

Only if actual transfer weight is excessive and creator rights have been reviewed: produce a separate master-derived test candidate (≤960px width, no enlargement, preserve ratio) at **960×540**; compare quality (fine historical detail/legible graphics) and format (WebP or JPEG vs PNG). Maintain original master and SHA-256, proper ALT describing the image as an AI-assisted **historical reconstruction**, dimensions and captions, and cache/rollback plan. No Gutenberg HTML rewriting or media upload until specifically authorized after visual QA. **Do not pass a third-party historical photograph off as a reconstruction or vice versa.**

## Evidence and test boundaries

- `qa/media-recovery/large_first_party_20261101.json`: exact **13** originals, real first-party source URLs and known 1024px variant candidates, full original dimensions, five verified empty WordPress subsize states, published post associations and **null** visitor HTTP/currentSrc/transfer fields.
- `qa/media-recovery/validate_large_first_party.cjs` and `test_large_first_party.cjs`: fail-closed original-byte/dimension/inline/960px check, 22 adversarial tests exercised against exact GitHub-committed validator/ledger and frozen baseline in isolated V8 using Node shims. **Not native Node or hosted CI.**
- Guest browser status and measured reduction remain unavailable: current runner DNS failed before HTTP on FinalVestige.com and the public web retriever could not access sampled URLs. No claim of a genuine public outage follows.
- Site-wide earlier figures stay scoped: 61 posts, 355 inline source slots, 288 external source slots; the **42 broken-image report is not verified**, and **76% image-weight reduction has never been measured** in an approved before/after guest trace.

**Decision:** This is an actionable **P1 five-post optimization shortlist**, not an authorization to change media. Assign guest evidence to the existing Site QA browser lane; keep source-identity/rights and compression candidate planning in Media Recovery PR #183. Production images repaired: **0**.
