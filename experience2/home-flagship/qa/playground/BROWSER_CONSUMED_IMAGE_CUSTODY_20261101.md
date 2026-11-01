# Exact-browser image-byte custody — isolated WordPress staging only

**Status:** DRAFT / HOLD. No WordPress production edits, PR merges, plugin installs, releases, or new subscriptions. This work is an isolated child of PR #426 at `7f6ec3fa69d0f9469cf490cc8ed907ee0782ad11`; frozen v1 PR #49 (`10495883299d53596992c26a8987f629b2904670`) remains unchanged.

## Reproduced defect in the existing stage verifier

The seven-chapter source has three `loading="lazy"` image exhibits; the chooser hides inactive cases. PR #426 correctly reveals them, but then used `page.request.get(img.currentSrc)`. That is a SECOND HTTP request, not the bytes consumed by the browser's `<img>`. A test server can return authentic bytes to that new request while serving altered bytes to the browser. In a controlled fake, **old audit accepted three forged browser-image responses** (`b'Z'`) because the independent GET returned the expected `b'a'`/etc.

This is an integrity weakness of the **proposed staging test**, not evidence of altered production media.

## Exact repair

- `verify_playground_browser.py` attaches `page.on('response', ...)` **before** `page.goto`; the ledger is per fresh browser context/width.
- `browser_consumed_media.py` wraps only the `Page.request` interface passed to the existing source-pinned gallery audit; `.get(src)` now looks up the already captured **actual browser image response**. It makes **no second HTTP request**.
- Require unique browser response matching `img.currentSrc`, same origin and exact `/media/{name}` path; resource type `image`, HTTP 200, expected WebP/JPEG MIME, no redirect chain and no service-worker substitution. `Response.body()` supplies the browser-loaded bytes to the existing exact-length, decoded-dimensions and **independently approved SHA-256** checks.
- Missing, duplicate, stale, wrong-origin or wrong MIME response: **fail closed**. Do not weaken the pre-existing three-original manifest gate. Original lazy loading and post-audit Apollo reset remain intact.
- No source photograph, art direction, JS/CSS, archive story, Focus, Jetpack, Mind #171, Apollo #158 or WordPress page 6 changes.

## Executed evidence

1. Old source mock accepts browser `b'Z'` with independently fetched expected `b'a'` (reproduced before change); corrected stage adapter rejects corrupted browser bytes.
2. `python -m unittest -v test_archive_gallery_transfer.py test_browser_consumed_media.py`: **12/12 passing locally**, comprising the six inherited gallery negative controls and six new direct-response/adversarial cases.
3. `python verify_browser_consumed_media_chromium.py`: **real Chromium** using `Page.on('response')`, locally routed one-pixel *synthetic* WebP/JPEG bodies and a JavaScript-controlled lazy gallery: **three correctly loaded images verified; corrupted Apollo browser response rejected**. No external network, WordPress theme, archival photo or production content required.
4. Exact new Git blob identities independently matched the locally executed files: `browser_consumed_media.py` = `2e01841aec7778fc8ee520fe2bff00e66f690f3f`; `test_browser_consumed_media.py` = `c7d9504cc0f4941e4a435aae0fbeec273ba344cf`; `verify_browser_consumed_media_chromium.py` = `21c5068c7d971d5469f2875b836bc1d5ac804a3b`. Runner wiring was verified against GitHub source; a full exact-checkout integration test has **not** been performed.

## Staging and publication boundaries

Real WordPress/Assembler execution is **NOT achieved**. No native staging clone exists on the production WordPress.com Personal plan, and this runtime cannot download WordPress or the Assembler theme. The free WordPress Playground/local WordPress staging method remains required. Three original images must be independently transferred, hashed, compared to the reviewed source, and rights-cleared; the real images **have not been downloaded or certified** by this change. The Franklin RMG catalogue link and source image provenance/reproduction rights are separate questions. The 5,553,669-byte NYPL original must be tested without mistaking CDN derivatives for exact original bytes. Axe WCAG 2.2 AA, full seven-width interaction screenshots, WordPress/Jetpack delivery, measured Lighthouse/CWV, CI/QD, founder visual choice and explicit release approval remain mandatory.

**Result: one real false-PASS vulnerability closed in the browser media admission test, no relaxation of the HOLD.**
