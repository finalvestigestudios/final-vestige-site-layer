# Media recovery — CDP redirect lineage without false image failures (2026-11-12)

Scope: independent draft PR #1703; Site QA draft #154 owns the existing guest-browser collector; the interim lead owns homepage visual design. Worklist is in draft #183, not main (blob `2acd06a4ca4317646006eb6591face3fe76fedec`).

## Verified source cohort
The frozen 61-post/355-inline-image ledger (`4965a862f7de7de46c1f4a1e26f3ca70a8c38805`) contains **118 exact stored Commons `Special:Redirect/file/` image URLs across 20 posts** within 288 external positions. This is **not** 118 observed browser redirects, failures, or downloads. Each original URL, post slot, candidate archival/catalog source, item-level rights observation and conditional at-most-960px dimensions is copied to `qa/media-recovery/redirect_lineage_118_source_audit_20261112.json`. All live guest HTTP status, redirect target, image-body bytes and rights approvals remain null/false. Do not count this as an increase in the 42 historically reported but guest-unconfirmed failures.

## Reproduced software measurement blocker and fix
`measure_image_transfer_pair_20261111.cjs` formerly rejected any Image request where `final_response_url !== request_url`, even if Site QA could prove a legitimate HTTP 302 redirect. This rejects an important class of source URLs during performance measurement and risks mislabeling a correctly loaded image as absent evidence.

The new validator **accepts a final URL change only** with one to five complete HTTPS-only `Network.requestWillBeSent` / `redirectResponse` hops, preserving exact requestId, previous response URL, next request URL and 301/302/303/307/308 status. Unknown, inconsistent, missing, overly long, credential-bearing, downgraded or cyclic chains remain HOLD. Shared request deduplication now binds the redirect chain as well as the response. Validated chains count **one final completed Image request's** `Network.loadingFinished.encodedDataLength`, not one byte total per hop, and record unique redirected request/hop counts. Only final HTTP 200 image MIME, positive body data, cold uncached full-scroll proof may be compared.

This does not change WordPress originals or grant reuse rights. The comparator still states **single-post** measured transfer only and refuses sitewide 76% or any production approval. The second-stage visual-parity gate remains required: original photo, crop, ALT, physical pixels, rights, credits and editor signoff are not inferred from HTTP 302. An example in tests is **synthetic CDP-shaped evidence**, not a live site pass.

## Site QA handoff (no new collector)
Existing Site QA #154 should retain the original first six suspected missing-image queue: **285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1**. For its existing full-scroll cold Chrome capture, enrich a redirecting Image request with `redirect_chain` entries containing `request_id`, `from_url`, `response_url` (CDP `redirectResponse.url`), `to_url` (next `requestWillBeSent.request.url`), `http_status` (`redirectResponse.status`), and `provenance: CDP_NETWORK_REQUEST_WILL_BE_SENT_REDIRECT_RESPONSE`. The final `final_response_url` is from the terminal `Network.responseReceived`. If the collector does not supply the evidence, **HOLD** instead of fabricating a chain.

## Performance and restoration restrictions
15 WP originals >1.5 decimal MB total 47,096,779 *stored* B; 11 inline-matched across eight posts total 38,480,915 *stored* B. No actual transferred-byte reductions have been measured. The proposed 76% reduction requires controlled baseline/candidate cold samples plus complete sitewide aggregation, not storage-size arithmetic.

No external image downloads/scraping, automatic caching or WP media upload, Gutenberg rewrite, production deploy, subscription spend or homepage change. Candidate reuse rights must be checked at the individual catalog item. Staging, if separately authorized, should retain originals, generate at-most-960px *without upscaling*, account for DPR/critical text legibility and explicit `srcset`/rollback, and compare screenshots. Official hosting does not itself license a photo.

References: https://chromedevtools.github.io/devtools-protocol/tot/Network/ ; https://commons.wikimedia.org/wiki/Help:File_redirect
