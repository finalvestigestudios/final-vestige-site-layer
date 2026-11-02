# Experience 2.0 — exact-source private WordPress staging admission

**Decision: RELEASE HOLD.** This is a release-engineering review artifact, not the WordPress homepage, a plugin installation, a deployment, or an approval. The seven existing chapters remain unchanged. Frozen v1 PR #49 stays frozen. Apollo PR #158, Mind issue #171, public page ID 6, 72 Margins items, 52-page Focus Fieldbook and Jetpack signup are untouched.

## What changed in this companion draft

The PR #225 provisional private renderer verifies every decoded asset hash before serving an authorized editor, but its response lacked an observable binding between the served HTML and the **canonical index.html at a specific Git HEAD**. This change adds a header **only on successfully authenticated, hash-verified preview responses**:

    X-FV-EX2-Index-SHA256: <sha256 of exact decoded index.html bytes>

The header is emitted after authorization/nonce/custody checks. Unauthorized access has no source body or attestation header. A corrupted payload still fails HTTP 503 without a source body or attestation header. The browser admission harness compares this served hash with the SHA-256 of the repository's clean, exact-HEAD index.html. It also compares all six inlined stylesheet text payloads and four script payloads byte-for-byte with the pinned checkout, rather than trusting filenames or caller labels alone.

There is **no public HTML, JS or CSS**, and no new CDN, font, analytics, plugin install, WordPress write or subscription.

## Reproducible tests performed before PR submission

From an offline development copy of PR #225's actual plugin and packaging function, including the exact hash-header change:

    python -m unittest -v test_exact_staging test_php_header
    # 14/14 passed: 11 Python admission tests; 3 local PHP HTTP tests
    php -l fv-ex2-private-preview.php
    # No syntax errors
    python verify_exact_staging.py --url https://finalvestige.com/ \
       --allow-host finalvestige.com --expected-head <SHA> \
       --storage-state /dev/null --out <REPORT_DIR>
    # Explicit RELEASE HOLD, refuses production; no requests sent to production.

Local PHP test uses only a **synthetic generated eleven-asset payload** and the same shipped PHP composer and local mock router. It confirms exact original index SHA in authorized HTTP 200 header; denied production-context request returns 403, no body or header; deliberate payload corruption returns 503, no body or header. These are NOT real WordPress or exact seven-chapter browser measurements. GitHub-hosted CI must independently rerun tests at the current PR head.

## Separate private WordPress staging requirement — exact access checklist

1. A **separate, founder-authorized private WordPress installation**, NOT finalvestige.com production, ideally with the same Assembler theme, PHP 8+, and content/media environment. The current WordPress connection lists **only** production site ID 256784396 (read on 2026-10-30 PT); this does not prove no staging site exists elsewhere.
2. An exact checkout of the latest review commit. Run the prior attested private ZIP builder from this clean HEAD. Installation only on separately authorized staging, never on production. Staging must set WP_ENVIRONMENT_TYPE=staging/development/local AND explicitly opt in to FV_EX2_ALLOW_PREVIEW; use an authenticated editor-only shortcode preview page. Do not edit live page ID 6 or production theme/navigation/settings.
3. Keep the Playwright editor **storage state only on the local QA runner**. Never commit it, attach it to the PR, print its cookies, or put access tokens in the URL.
4. A preview-page URL on the exact staging host (without a nonce/query string). Install optional locally approved axe-core JavaScript file separately; do not fetch remote scripts into the staging preview. Ensure correct account scope and authorization.

Run the tests from the checked-out repository root:

    python -m unittest discover -s experience2/home-flagship/qa/release-candidate \
      -p 'test_exact_staging.py' -v
    python -m unittest discover -s experience2/home-flagship/qa/release-candidate \
      -p 'test_private_hash_header.py' -v
    python experience2/home-flagship/qa/integration/private-preview/attest_private_preview.py \
      --repo . --expected-head "$(git rev-parse HEAD)" \
      --out /tmp/fv-staging-private.zip --report /tmp/fv-staging-source-receipt.json
    python experience2/home-flagship/qa/release-candidate/verify_exact_staging.py \
      --url "https://AUTHORIZED-STAGING-HOST/private-home-preview/" \
      --allow-host "AUTHORIZED-STAGING-HOST" \
      --repo . --expected-head "$(git rev-parse HEAD)" \
      --storage-state /secure/qa-editor-browser-state.json \
      --axe-script /secure/axe.min.js \
      --out /secure/fv-ex2-review

**This script refuses direct production domains** even when passed via --allow-host. It does not have a CMS write path. Its outputs are explicit: full-page 390px and 1440px founder previews if the authorized iframe loads, 360–1920px browser results, no-JS results, page errors, inline exact SHA checks, three real image load observations (naturalWidth/currentSrc and available resource timings), CSP/noindex/no-store headers, and injected axe-core WCAG tag violations when an approved local axe file is supplied. Any missing required observation is reported as FAIL/HOLD. If no axe file is supplied, AXE_NOT_RUN is a blocking result, not a hidden pass.

Images are **not** rights-approved merely because they load. The existing manifest still requires independent NASA commercial-context and NYPL item-level review, while Franklin provenance must be retained. No new image is introduced here. On a private staging host, img URLs may target the official production origin or the existing Jetpack CDN: the harness records the actual selected URL, response-derived resource timing when observable, and natural dimensions; it does not invent image transfer bytes.

## Deliberate limitations / remaining gates

- The actual staging site cannot currently be reached via the connected WordPress tools. Consequently **no complete-site staging browser screenshots or loaded-image results are claimed** in this PR.
- Synthetic PHP/HTTP tests are not a WordPress Assembler integration test. Browser rendering has not been rerun on the complete pinned canonical checkout at the new PR HEAD.
- Browser PerformanceObserver's LCP/CLS observations, when available, are **lab observations, not field Core Web Vitals p75**; resource transfer sizes may be zero for cross-origin resources without Timing-Allow-Origin. A separately run Lighthouse report, authenticated real-user context and field measurements are required; this script deliberately reports Lighthouse NOT_RUN and field CWV NOT_MEASURED.
- Even a clean axe automated run does not certify WCAG 2.2 AA. Manual keyboard, touch, VoiceOver/NVDA, reduced-motion, screen zoom/reflow and Safari remain necessary, as do independent QD/CI and founder approval.
- Page 6 read-only inventory checked on 2026-10-30 PT: 72 distinct margin spans indexed 0–71, two /focus/ links and one Jetpack subscriptions block. The new source-code-only margins_contract() can reject a missing/duplicate margin from an exported snapshot, but **no production write or replacement** is part of this PR. Any future page update requires a separately governed preservation proof.

**Release decision remains HOLD** until authorized staging, exact-SHA CI/QD, rights signoff, genuine Lighthouse/CWV and founder visual acceptance. No automatic merge, deploy, install or publication.
