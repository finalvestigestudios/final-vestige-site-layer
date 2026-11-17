# Media Recovery: redirect-chain historical identity guard — 2026-10-31

**Scope:** Draft PR #183 only. Complements the separate Site QA source-dependency census in PR #154. No production WordPress/media changes, homepage redesign, external image copies, uploads, paid services or publication approvals.

## Reproduced engineering defect (synthetic CDP scenario; NOT a reported live-site substitution)

A browser image element's `currentSrc` identifies the URL it requested, **not necessarily the final image bytes obtained after HTTP redirects**. Previously `classifyImages()` could find an HTTP 200 image response via a CDP redirect-chain alias and mark the original historical image as `loaded_in_probe_browser` when the final response URL identified a completely different photograph. A visible decoded photograph is not proof of the intended archival image's identity.

**Conservative remediation:**
- For a successful decode, compare `currentSrc` against the **final CDP response URL** using the established exact-source identity rules. A different filename, institution or Navy `image=` selector means `redirected_image_identity_unverified`, never automatically working or broken.
- Known Commons file redirect → matching hashed upload filename, a different rendition of the same NHHC `image=` ID, and ordinary static-file resize proxies still qualify under `sameSource`. This is a metadata-level identity check, **not a binary hash or archival license confirmation**.
- An actual final HTTP 404/network error, or an HTTP 200 HTML/JSON/XML error that fails image decoding, can remain a confirmed **visible broken request**, even if it follows a redirect. This reports a broken source link, not the historical identity of an alternate image.
- Record `network_final_identity_verified` and `redirected_image_identity_unverified` for each matched image. The independent `image_census_coverage_core.cjs` recomputes stored-vs-decoded and decoded-vs-final URL identities; it refuses a fabricated loaded claim even if a report asserts `current_src_identity_verified: true`.
- Unverified redirected images make the complete-page broken-image count **NULL**, not zero. The stricter wire-byte comparator already separately rejects such mismatched source evidence.

## Verification

Replayed **130 of 130** committed-source synchronous regression cases across nine suites in an isolated V8 harness with a deterministic test-only URL parser: 15 redirect-chain adversarial cases plus 115 existing browser, Commons, Navy-compatible URL, decoded-currentSrc, 2xx-MIME, screenshot, census, transfer and scroll-coverage cases. Core blob SHAs: `browser_probe_core.cjs` `d72a05e49063abb9faf60eccbb3829881a9cc6d1`; `image_census_coverage_core.cjs` `5885f1aa5143fb66d83f75c51f27701a29ae11c2`; redirect regression tests `0343d2729b31dbf83e52a0a47b278776bd5004c8`.

**Not yet verified:** Native Node CI, live logged-out Chromium image responses, post-level screenshots, final-image hashes, actual visitor failures, actual transfer bytes, a 76% reduction or copyright clearance. The local probe returned DNS resolution failure for `finalvestige.com`, which is **not evidence of a public outage**. The source snapshot remains 61 published articles, 355 stored image references, 288 offsite by current classifier (286 in older Site QA inventory), and 13 original WordPress media files >1.5 MiB.

## Recovery decision gate

If logged-out browser evidence shows `redirected_image_identity_unverified`, compare the exact final CDN/request chain to the published archival source record, confirm the **identical historical photograph**, and review item-specific copyright, credit and editorial context. Do **not** label it a confirmed 404 merely for redirecting; do **not** mirror the URL or swap images without a cleared licensed original. Proposed first-party WordPress-cached responsive derivative is at most **960px wide, never upscaled or cropped**, retaining credit, aspect ratio, original URL and SHA-256 custody. Stage only after approval and verify visual parity + actual image-wire bytes before/after.
