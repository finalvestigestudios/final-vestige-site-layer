# Media Recovery — CDP resource-type isolation, October 31, 2026

**Scope:** Draft media-recovery PR #183 only. No homepage visual-design files, Site QA PR #154 files, WordPress production content, downloads, images, subscriptions or spending were changed.

## Concrete audit defect reproduced

The Chrome runner previously passed **all** Chrome DevTools Protocol network records to the historical-image classifier while separately counting only `type: "Image"` responses as image-wire bytes. An XHR, Fetch, or Document on the **same URL** could be selected as the latest response for an `<img>` by `findLast()`, potentially certifying an image as loaded from non-image network activity or concealing a real failed Image request. This is a code-level synthetic reproduction; it is **not** evidence that FinalVestige.com currently contains that failure.

Tests against the unchanged classifier demonstrate these cases:

| Synthetic network evidence for same URL | DOM `naturalWidth` | Previous runner's classification | Corrected runner's classification |
| --- | ---: | --- | --- |
| Only `Fetch` HTTP 200 `image/jpeg` | 960 | `loaded_in_probe_browser` (false assurance) | `decoded_without_verified_response` |
| `Image` HTTP 403 then `Fetch` HTTP 200 | 960 | `loaded_in_probe_browser` (false assurance) | `decoded_without_verified_response` |
| `Image` HTTP 403 then `Fetch` HTTP 200 | 0 | `zero_intrinsic_width_needs_review` | `confirmed_broken_in_probe_browser` |
| `Image` HTTP 200 then `Fetch` HTTP 200 | 960 | `loaded_in_probe_browser` | `loaded_in_probe_browser` |

**Not live measurements:** these synthetic URLs and statuses are regression fixtures, not actual response codes from the public website. The reported 42 broken images remain unverified.

## Safe isolated fix

- `qa/media-recovery/cdp_image_request_scope.cjs` defines `selectCdpImageRequests()` to retain only HTTP(S) records with CDP `type === "Image"`. This is fail-closed for missing type; it neither initiates network I/O nor mutates records.
- `browser_probe_chrome.cjs` now passes **that same exact Image-only set** to the source/DOM classifier, the exported network-image audit and the image-transfer counter. A later Fetch response cannot override an actual image HTTP failure, and an unrelated Fetch alone cannot certify a displayed historical photograph.
- `Network.loadingFailed` now retains the event's resource type in the request record, preserving genuine failed image requests when earlier CDP events omitted `type`.
- Redirect aliases remain attached to the selected Image resource record; existing Commons, Navy and Jetpack source-identity checks are still mandatory.
- No effect on cached/served-worker proof gates, HTTP MIME/byte validation, maximum-960px rights-controlled derivative planning, or document/scroll completeness rules.

## Verification and release conditions

**11/11 native Node tests passed locally** for the exact new selector and test source; six additional end-to-end **committed-source V8** integration cases passed against the unchanged `browser_probe_core.cjs`. The latter were not native Node/Chromium. Existing test suites were not rerun end-to-end; CI and guest Chrome remain outstanding.

Reproduce on a network-enabled development machine, no login and no CMS writes:

```sh
node --test qa/media-recovery/test_cdp_image_request_scope.cjs qa/media-recovery/test_cdp_image_request_integration.cjs
node --test qa/media-recovery/test_browser_probe_core.cjs qa/media-recovery/test_loaded_network_proof_20261031.cjs
node qa/media-recovery/browser_probe_chrome.cjs --plan
node qa/media-recovery/browser_probe_chrome.cjs
node qa/media-recovery/browser_probe_chrome.cjs --desktop
```

Prioritize actual visibly broken visitor images in the six P0 investigations, recording exact `image_key`, stored source URL, decoded `currentSrc`, final **Image-type** request URL, status, content type, decoded dimensions, encoded bytes, screenshot and rights source. Do not claim the 76% weight reduction until matched mobile/desktop article-image transfer measurements are independently reproducible and historical assets are unchanged.

**Status on 2026-10-31:** 61 posts / 355 stored image references / 288 offsite references / 13 WordPress originals above 1.5 MiB remain source-census figures; **0 production repairs**, **0 independently confirmed visitor broken-image count**, **0 verified site-wide weight reduction**. The current isolated runner cannot resolve FinalVestige.com or control public domains, so live browser HTTP statuses and screenshots remain unavailable. This is not evidence of a public outage.
