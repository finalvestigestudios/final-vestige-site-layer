# Browser census decode-failure coverage — 2026-11-01

**Isolated Media Recovery PR #183; Site QA PR #154 remains independent. No production WordPress, homepage, historical-photo, image binary, or billing changes.**

## Confirmed code defect and correction

The Media Recovery classifier (`qa/media-recovery/browser_probe_core.cjs`) already marks a true completed, zero-intrinsic-width HTTP **200 image/* response** as `confirmed_broken_in_probe_browser` / `image_decode_failure`, provided the archived image is mapped to the exact `currentSrc` and uncached final Chrome CDP Image response and positive encoded transfer bytes. However, its separate sitewide completeness gate (`qa/media-recovery/image_census_coverage_core.cjs`) recognized only network errors, HTTP 4xx+, and HTML/XML/JSON error bodies. Thus an otherwise fully observed 200-image decode failure caused `proofKind()` to return `unresolved`, `assessPage()` to return `INCOMPLETE` and `assessRun().confirmed_broken_count` to remain **null**. An actually broken picture could prevent the sitewide broken-image census from reaching a defensible number.

**Patch:** treat `image_decode_failure` as an independently acceptable *broken* proof, only if the network is exactly matched to the stored image's decoded source, `http_status===200`, MIME starts with `image/`, the response has positive safe-integer encoded bytes, `loaded_network_proof_verified===true`, `network_final_identity_verified===true`, the redirect is not unverified, and no network failure is reported. The preexisting global gates also require a verified stored source, completed image element and `natural_width===0`. A mismatched substitute or unverified redirect never passes.

This is **not** a claim that FinalVestige.com currently has such a failure. It corrects the counting logic *if real visitor CDP evidence demonstrates one*.

## Verification and scope

- Exact committed GitHub source and new synthetic Node test file replayed in an isolated JavaScript runtime with direct same-URL identity and strict-assert shims: **24/24 test cases passed**.
- Cases include positive image-decode proof; full post/site census aggregation; 18 adversarial proof mutations (missing/falsified identity, nonimage MIME, missing/zero/negative bytes, cached-proof omission, HTTP 206, unresolved redirects, network failure, substituted asset, incomplete DOM); unfinished scroll and blocked page; existing 404 and 200 HTML error handling.
- Native Node command still required: `node --test qa/media-recovery/test_decode_census_gate_20261101.cjs qa/media-recovery/test_decode_failure_guard_20261101.cjs qa/media-recovery/test_network_redirect_identity.cjs`. No native/hosted CI, DNS-enabled logged-out Chrome or production HAR executed in this environment.
- Important distinction: a *known* broken classification can be recorded even when the **complete** article/site census is not proven. Only a complete guest-browser census may produce a definitive `confirmed_broken_count`. Never turn unknowns into zero or infer missing images from independent web-retriever 403/404.

## Site QA acceptance and priority queue

Keep Site QA PR #154 untouched. On desktop and mobile logged-out Chrome, preserve exact source key, `currentSrc`, request ID/final URL, uncached status, MIME, encoded transfer, `complete`, `naturalWidth`, scroll coverage and screenshot. A real 200-image MIME/bytes but zero-width decode must survive from per-image classifier through independent full-page/site census (rather than being discarded as unresolved). Priority live slots remain Three Mile Island **285:5**, Skyway **287:5**, Hebgen **407:1** and Scotch Cap **418:1–2**. An external retriever's response is not guest HTTP proof.

## Inventory, reuse, and performance boundaries

Current frozen baseline is **61 published posts, 355 stored image slots, 288 offsite references and 13 Media Library originals >1.5 MiB**. The **42 supposedly broken images remain unverified** and **76% weight reduction remains unmeasured**. Original storage sizes are not visitor-transfer sizes; a partial failed-media load does not constitute legitimate saved bytes. No offsite image copied, license inferred, 960px derivative generated or WordPress upload/rewrite authorized.

## Code pointers

- `qa/media-recovery/image_census_coverage_core.cjs` — fail-closed census proof correction.
- `qa/media-recovery/test_decode_census_gate_20261101.cjs` — 24 adversarial Node test cases.
- `qa/media-recovery/browser_probe_core.cjs` — unchanged per-image image-decoding classifier.
