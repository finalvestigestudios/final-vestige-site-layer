# Offline Chrome HAR triage — Final Vestige historical media

**2026-10-31.** Independent Media Recovery draft PR #183. No WordPress writes, homepage layout changes, third-party image copies, asset downloads, subscription spend, or publishing. Complements — does not replace — Site QA PR #154 or the existing read-only CDP Chromium probe.

## What this adds

**A real network-evidence ingestion route even when the engineering runner cannot resolve FinalVestige.com.** A user or Site QA engineer with ordinary logged-out Chrome network access can collect a browser-generated HAR locally, and this tool turns *only* the article's known stored-image requests into structured JSON with actual HAR HTTP statuses and image MIME evidence. It does not infer statuses from the CMS, archive, or a web image viewer. Each image is anchored to one of **355 stored slots across 61 frozen published posts**. The six-article P0 queue (43 slots, 36 offsite) provides extra archival leads where available; all 61 posts work.

Source: qa/media-recovery/har_image_triage.cjs. Native regression source: test_har_image_triage.cjs. The importer reuses browser_probe_core.cjs's conservative same-photograph source identity, including origin-preserving Jetpack proxies; it does **not** modify Site QA's own classifier.

## Capture (on a network-connected workstation only)

1. Open a fresh *logged-out* Chrome Incognito window and navigate directly to the investigation, e.g. **post 268**: https://finalvestige.com/2026/08/18/they-painted-over-archimedes/. No sign-in, no WordPress admin pages.
2. Open DevTools → **Network**, check **Preserve log** and **Disable cache**, reload the article, then scroll slowly to the end and return to the top so deferred images request. Don't copy images.
3. Network → **Save all as HAR with content**, e.g. archimedes-guest.har. Chrome HAR files may contain tokens, URLs and cookies despite Incognito: **never commit, email, publish, or upload the raw HAR**. Work locally and delete when no longer needed. No third-party endpoint or dependency is required.
4. From the repository root, run (Node >=22):

    node qa/media-recovery/har_image_triage.cjs --har=archimedes-guest.har --post-id=268 --out=archimedes-triage.json

5. Inspect the generated JSON and compare any HAR_IMAGE_HTTP_ERROR_OBSERVED or HAR_IMAGE_NONIMAGE_RESPONSE_OBSERVED with logged-out DevTools **Image** requests, each DOM image's currentSrc, naturalWidth, historical ALT and screenshot. The normal browser_probe_chrome.cjs v3 CDP JSON, when available, is stronger evidence because it binds pixels and redirects to the same exact photograph.

The --post-id can be any ID in the frozen 61-post census, including 432 (Florida Memory), 418 (1946 Hilo), 407 (USGS), 434 (Apollo 1), 621 (Malbone), 299 (Vasa), or 34–38 (oversized first-party featured PNGs). One HAR per article, one explicit post ID; do not mix unrelated pages. The tool rejects an unknown post, a drifted P0 identity, an oversized (>25 MiB) HAR, or output file overwrite. Output mode 0600. **An article's identity is not independently verified by the HAR; validate the captured browser URL manually.**

## Exact evidence semantics

- har_observations[].http_status is an **actual status recorded in the supplied HAR**, **not** a current production check performed by this agent. It remains null when no valid HTTP status is present. The script never fabricates a 404 from a stale hotlink, viewer refusal, or missing request.
- Only Chrome _resourceType:"image" **GET** records are eligible. Same-URL XHR/Fetch/HEAD calls cannot claim an image loaded or mask its Image 403. If Chrome omits resource-type metadata, leave the case unverified instead of guessing from .jpg.
- MIME image/* with HTTP 2xx is **response evidence, not visual or historical-image identity proof**. HTTP 200 HTML, 4xx/5xx, and 3xx responses are separately flagged. Redirect destination identity remains unverified unless independently checked.
- The tool **never sets verified_broken_in_browser=true**: visual failure requires DOM naturalWidth===0 and source/currentSrc/final-response proof in the CDP probe or a manually reviewed equivalent. Duplicate same-URL slots remain ambiguous, not arbitrarily assigned.
- har_reported_transfer_size_bytes and har_reported_body_size_bytes are separate, vendor-specific HAR fields. **Do not use either to claim the purported 76% reduction** or compare against CDP encodedDataLength; use strict same-content, same-browser v3 CDP comparison after actual rights-cleared optimization.
- Output whitelists only matched image-resource fields, never HTTP headers, cookies or response bodies; common secret-bearing URL query keys are redacted. Nevertheless review any output before sharing. Unknown unrelated HAR URLs are not exported.
- Source catalog candidates and 960px no-upscale limits are carried forward as **review leads only**. source_reuse_rights_verified, rights_cleared, wordpress_write_authorized, verified_broken_in_browser, image_identity_after_redirect_verified and measured_article_wire_savings_percent cannot become positive merely by importing a HAR.

## Rights and controlled recovery

For a confirmed broken visitor image, match the exact historical photograph to its primary record (Navy, Coast Guard, USGS, NASA, Florida Memory, municipal/other archives), preserve dates and photographer credit, verify source-specific publication rights, master SHA-256 and original dimensions, prepare a reviewed derivative **at most 960 pixels wide** without upscaling, stage as first-party WordPress media **only through a separately authorized workflow**, and review rendered visual/caption identity before publishing. Unknown-rights or merely similar alternative photographs stay **HOLD**.

## Verification and deployment status

- The new 61/355 census adapter ran on all eight actual committed snapshot parts and matched the P0 queue without source drift.
- Native Node regression run with a narrow local substitute for the already-committed URL matcher: **18/18 PASS**. The **exact GitHub-committed code plus the actual committed URL identity helper** passed **18/18 isolated V8 replay cases** using URL and Node-test assertion shims. This is **not native CI or live Chrome**.
- This environment's DNS resolution for finalvestige.com, www.google.com and www.archimedespalimpsest.org failed before HTTP, and direct public-site web access was unavailable. There are **no actual HAR files, visitor-facing HTTP statuses, broken-image screenshots, verified 42 failures, verified 76% reduction, image conversions, rights clearances, or production repairs** from this sprint. The block does not establish that FinalVestige.com is offline.

**Priority:** Site QA can collect a guest-browser HAR for post 268 or 432 and return the *sanitized triage JSON + screenshot/DOM evidence* via PR #154. Media Recovery PR #183 then owns exact-source recovery, item rights and the first-party 960px staging plan; no cross-branch code duplication.
