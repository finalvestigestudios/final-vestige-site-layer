# Logged-out image loaded-response integrity (October 31, 2026)

The read-only media browser classifier previously could label a photograph `loaded_in_probe_browser` even when **no matching image request** was captured (`!req`) or the matched request returned **HTTP 403**, provided that the DOM still reported positive naturalWidth. A 200 HTML error body paired with decoded fallback pixels could also receive a false loaded classification. These are reproduced audit-code defects, **not demonstrated public-site outages**.

## Safe isolated correction
- `browser_probe_core.cjs` requires authenticated *network evidence* of a successfully decoded source: exact stored-to-currentSrc and final-response image identity, page verification, completed positive-width decode, HTTP **200**, `image/*` MIME, positive real CDP encoded bytes, no network error, and no reported cache/service-worker delivery.
- Otherwise visible pixels become `decoded_without_verified_response` (not a proven success and **not** an asserted failure); an unrelated redirect target stays identity-unverified.
- `image_census_coverage_core.cjs` independently rejects old or mutated loaded rows lacking the explicit network-proof flag, image MIME, actual bytes or final network identity.
- New adversarial synthetic cases `test_loaded_network_proof_20261031.cjs` plus existing fixture updates. The browser probe remains **read-only**; nothing is installed on WordPress. A logged-out Chrome/CDP run must still confirm image URLs/statuses and transferred bytes.

**Scope and unresolved evidence:** 61 published article posts, 355 stored image slots, 288 source-offsite references in media's frozen snapshot, 13 >1.5MiB original media assets. The reported 42 broken original sources and claimed 76% weight reduction are **not verified**. No primary-source image binaries, rights clearances, new 960px derivatives or repairs are asserted. No homepage, Site QA #154, production WordPress or subscriptions were changed.

**Native verification to run on network-independent checkout:** `node --test qa/media-recovery/test_browser_probe*.cjs qa/media-recovery/test_network_redirect_identity.cjs qa/media-recovery/test_image_census_coverage.cjs qa/media-recovery/test_loaded_network_proof_20261031.cjs`. Native CI/live browser remains independent from any isolated V8 smoke verification.
