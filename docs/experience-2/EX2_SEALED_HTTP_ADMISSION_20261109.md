# EX2 sealed private preview — PHP HTTP admission (2026-11-09)

**Status: DRAFT / RELEASE HOLD.** This isolated companion stacks on draft #1822 (`18ad7e9e044d1f6b2ede255d28d2b9e877ed5efd`) and does not change any homepage runtime code, production page, plugin, or frozen #49.

## Why this gate exists
Earlier sealed-preview verification proved CLI PHP rendering and offline Chromium behavior, but it did **not** prove HTTP statuses, HTTP Content-Security-Policy header emission, or that invalid reviewer requests fail before the page is served. This adds an actual 127.0.0.1 PHP built-in HTTP server test of the **unchanged** packaged PHP, with deliberately fake WordPress functions. The difference is transport/header coverage, not real WordPress integration.

## Reproduction
Use the exact current source-controlled 11-file home candidate and sealed builder (see #224 and #1822) to regenerate the gated preview ZIP. Extract its PHP and `STAGING_MANIFEST.json`, then run:

```sh
python tests/experience-2/verify_sealed_php_http.py \
  --plugin /tmp/fv-ex2-sealed-staging-preview/fv-ex2-sealed-preview.php \
  --manifest /tmp/fv-ex2-sealed-staging-preview/STAGING_MANIFEST.json \
  --out /tmp/fv-ex2-sealed-http-receipt.json
```

This suite requires the PHP CLI and a working localhost loopback from Python. It spawns **no WordPress server**; all role, environment, nonce and shortcode APIs are explicit test doubles. It creates only ephemeral files, binds only to `127.0.0.1`, and never calls production endpoints or mutates CMS state. It compares the input plugin SHA-256 to the actual manifest before executing it. A caller-supplied `expected_commit` is metadata; do not treat that field as cryptographic Git provenance.

## Actual isolated-run evidence
- Full source baseline: PR #1822 head `18ad7e9e044d1f6b2ede255d28d2b9e877ed5efd`; source and builder/renderer SHA ledger provided with previous exact-source review.
- **23/23 local HTTP assertions PASS** against generated sealed PHP with SHA-256 `1c1a52eb20a44b9ac2bd769c637f14c7d4efca57820f534875d57e492c240322`.
- Tested explicitly: production preview denial even when opt-in is enabled; disabled staging preview denial; unexpected environment denial; anonymous, reader and incorrect/missing nonce 403; editor-only shortcode; approved staging/development/local 200; unavailable raw HTML/CSS/JS paths 404 in the **stub router**; `noindex`, `nosniff`, `no-referrer`, `no-cache`, actual HTTP CSP header and fresh per-response nonce; preservation of six CSS/four JS payloads and contextual Focus destination.
- Browser loading of a localhost HTTP page was attempted separately but Chromium returned `net::ERR_BLOCKED_BY_ADMINISTRATOR` even for an intercepted route. **No claim of browser-enforced HTTP CSP, actual editor cookies or genuine WP staging.** Earlier offline Chromium tests remain distinct, not substituted as HTTP CSP proof.
- The local HTTP response uses no real user, subscriber, credential, Jetpack, order, or affiliate data.

## Rights, editorial and conversion custody
No image, text, commerce, tracking, script or runtime homepage change. The Franklin historical folio remains explicitly editorial typesetting, **not a facsimile**. Existing Apollo/Franklin/NYPL imagery is unchanged. Rights/provenance must continue through #1730; media metadata is not proof of transferred bytes or final licensing clearance. All seven archive chapters, original Focus destination, and current public WordPress Page 6 with its 72 Margins and Jetpack are untouched.

**Offer → funnel → blocker → change → evidence → owner:** Existing 52-page Focus Fieldbook → historical evidence and a clear invitation to opt in → missing transport-level review evidence for sealed staging → source-controlled real-PHP HTTP admission harness → 23 passing stub-HTTP assertions; no verified leads or sales → interim homepage engineer, independent QA; Claude retains production/attribution, Grok the creator campaign, founder release control. The live false-success subscription issue remains separately gated by #1681.

## Still required before any release
Authorized isolated WordPress/Assembler installation and genuine authenticated/anonymous requests; actual browser navigation with HTTP CSP and no-JS; first-party archival images transferred and rights cleared; manual and axe WCAG 2.2 AA (fail closed if unavailable); keyboard, touch, 200% zoom, Safari, 320–1920 widths; measured Lighthouse/CWV; genuine Jetpack subscriber confirmation; independent CI/QD, founder visual approval and explicit production release approval.

WordPress.com Personal has no native staging clone; `vestigefinal-tezws.wpcomstaging.com` is **not** a second site. An isolated free developer WordPress/Playground instance is the valid testing route, but not an exact reproduction of WordPress.com Atomic.

**No merging, deployment, WordPress production edit, plugin install, new subscriptions, analytics, affiliate activation, or spending authorized.**
