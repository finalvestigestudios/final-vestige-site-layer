# P0 CDP response/request lineage hardening — November 13, 2026
**DRAFT / QA ONLY — no production changes, media downloads, cache, post rewrites, homepage work, or spending.**

## New finding and concrete fix
The previous P0 adjudicator validated a generic `cdp_request_id`, nominal response/finish provenance strings and image pixels, but did **not** bind the actual `Network.responseReceived` and `Network.loadingFinished` event IDs, response URL, response status or Chrome resource type to that single P0 request. In synthetic tests, a foreign HTTP 404 could therefore be misattributed to a pinned image. A second synthetic case could claim HTTP 200 with a decoded image and native pixels even when the reported response MIME was `text/html`. Neither is evidence of a production fault.

The revised intake requires `resource_type: "Image"`, **matching** response/request/finish request IDs, final response URL and status, valid MIME, and nonnegative `Network.loadingFinished.encodedDataLength`. A successful decoded 200 additionally needs an image MIME and positive completed-transfer bytes. A real failed image request may legitimately receive `text/html` on 404, and is still admitted for **failure review only** when all other evidence is bound. Unknown/mismatched fields become HOLD; do not fake omitted fields to make the validator pass.

Protocol contract: https://chromedevtools.github.io/devtools-protocol/tot/Network/ — `Network.responseReceived` supplies request ID, resource type and response data; `Network.loadingFinished` supplies request ID and `encodedDataLength`. CDP evidence blobs and screenshot hashes must still be independently inspected, not accepted merely from self-reported strings.

## Verification and exact source custody
- Intake code blob: `70c1366fbdf423fab312d977d728d52865907a12`.
- Native-Node-form regression suite blob: `914f5b4212e79ad050f9f7aff78bf652f1c9bd24`.
- **53 / 53** existing-plus-new regression tests passed in isolated V8 with minimal Node-compatible `test/assert` shims on the exact code/test contents before writing. **Native Node on this revised commit and repository CI are not yet executed**.
- [Six-slot machine audit](../qa/media-recovery/p0_request_event_custody_20261113.json) preserves exact URLs, reported wrapper codes distinctly from **null browser/origin statuses**, provenance pointers, item-rights holds and conditional derivative sizing.
- Site QA #154 retains its collector, priority order `285:5 → 285:2 → 287:5 → 418:1 → 418:2 → 407:1`, and must provide cold logged-out request/response/finish event linkage. **No replacement, rights or browser failure is approved**.

## Archival and visual integrity
The U.S. Coast Guard catalog for `418:1` and the USGS official Original link for `407:1` remain preservation leads; moved Skyway publisher media and Scotch Cap same-basename images remain exact-photo/crop/rights unverified. Florida Memory alternatives are potentially different historical moments, not silent replacements. Maintain item-level attribution, 960px maximum width, no upscale, actual source-master dimensions and hash, painted CSS × DPR, map/figure legibility, screenshot scene and ALT review. No binaries acquired or local WordPress cache permitted.

## Site-wide baseline limits
Frozen **61 posts / 355 image positions**; **42 alleged broken original links remain unconfirmed by guest browser**. Expanded census shows **15 original media files over 1.5 decimal MB = 47,096,779 stored bytes**, not wire transfer. The alleged **76% visitor transfer saving** is still unmeasured and requires paired cold captures with request-ID deduplication, matching slots and verified scene/ALT/crop. This sprint repaired an evidence-validation hazard, **not an image or page-weight issue on the live site**.
