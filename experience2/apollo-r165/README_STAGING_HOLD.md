# Apollo R165 — selected-media delivery custody; review-only

**New evidence gap:** A first-party `img.src` does not prove visitors receive first-party bytes. WordPress Image CDN may select `i0.wp.com`/`i1.wp.com`/`i2.wp.com` via `srcset`, and a valid `img.src`/`naturalWidth` check alone can miss a failed selected candidate, anomalous MIME, or missing resource evidence. The related Experience 2.0 audit documented that distinction in [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150#issuecomment-6682383786). Do not assume these CDN candidates are currently selected for Apollo without the installed-page witness.

## Scope and provenance

Complement, **do not alter**, R164's installed-page Playwright acceptance. The standalone read-only runner measures six viewport widths (320, 360, 390, 768, 1440, 1920), browser `currentSrc`, the selected response's 2xx status, MIME, SHA-256, response byte count, decoded dimensions, source alt and original NASA catalog hyperlinks, and screenshot checksums. It records the actual selected host, flags proxy selection, and strips URL query strings from report output. `naturalWidth` alone is insufficient. Source-custody anchors: NASA image S66-58038 (Oct 18, 1966); S67-15717 (Jan 3, 1967); and KSC-20170124-PH_KLS01_0129 (Jan 24, 2017). These are contextual imagery **not fire-second evidence**. Do not infer paid-use rights or NASA endorsement from a public NASA record URL.

## Local reproducible execution

`python -m unittest -v test_media_custody.py` (from this directory) requires free installed `playwright` + Chromium. Test uses deterministic **generated pixels**, Playwright HTTP image routing, and actual Chromium `srcset/currentSrc` selection. It has a success case and a negative CDN-failure case. It intentionally NEVER returns WordPress acceptance; tests are synthetic. Python standard-library PNG generator avoids redistributing NASA copyrighted photographs.

## Authorized installed staging procedure (read only)

`python media_custody_witness.py --url https://STAGING-HOST/ACTUAL-APOLLO-PAGE/ --out ./evidence`

For actual-page acceptance, inspect `media_custody.json` for 2xx selected image response, real response bytes, decoded dimensions, NASA links, and each viewport's `currentSrc` host. No mocks or request interception allowed. If navigation fails, returned report has a failure, **never pass**. Execute R164 suite separately with genuine axe-core, screen-reader + 200–400% zoom, 44px targets, no-JS, actual CSP and performance; verify backend/cache/CDN separately. Verify required image-specific editorial/marketing rights before use in paid promotions. CI must run on exact PR head.

**Release:** HARD HOLD. Only founder + Claude may authorize production. No WordPress, merchant, social, analytics or email writes; no added tracker; no homepage PR #49 or PR #158 change. Apollo editorial CTA remains **Read full investigation**. A hypothetical premium educator dossier is not an available merchant product until verified SKU, rights, working payment/delivery, refunds/fees and settled orders. Grok TASK-008 actual asset IDs/attribution and realized net revenue per 1,000 qualified humans remain unknown.
