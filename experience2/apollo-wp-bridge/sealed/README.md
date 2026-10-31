# Apollo Experience 2.0 — private, source-pinned WordPress staging (DRAFT / HOLD)

This **isolated alternative** to the previous direct-file shortcode bridge in PR #221 is for a *separate, approved staging WordPress instance only*. Nothing in this branch activates a plugin, changes a page, alters site settings, merges into `main` or touches frozen homepage PR #49 / standalone Research Desk PR #158.

## The concrete defects addressed

1. The PR #221 `upstream-pr215-blobs.json` shipped `response_lab.py` with a **39-character Git blob SHA**, truncated from the 40-character `82f4f42e05227207a38a707aa209edf14c75bd5d`. Its intended exact-head build was impossible even with the correct source. This PR repairs the pin and makes `build.py` reject malformed/missing pins **before** attempting to generate output.
2. The original PR #221 adapter placed unpublished `generated/fragment.html`, CSS, JS and CSV/JSON inside a publicly URL-addressable plugin folder. Its shortcode was not hard-gated to a non-production environment. An editor-only frontend would **not** protect these static files from direct URL access. This alternative packs them in PHP constants and serves the content only after a per-request auth, staging-environment and nonce check. It never includes public raw source/data files in the plugin ZIP.
3. The earlier real-browser evidence used an **older local response fixture**, so it explicitly did not prove the assembled exact PR #215 head. The new QA suite executes against **all 12/12 verified Git blob inputs** at source head `74375657f2cdaac0710f94c6de6c24534ee06858`, then verifies PHP shortcode access, source and export delivery and real Chromium interactions.

## Usage (not installation authorization)

From a checkout containing the PR #221 parent and this stacked draft:

```bash
python experience2/apollo-wp-bridge/sealed/build_sealed.py --out /tmp/fv-ex2-apollo-private-review.zip
python -m unittest discover -s experience2/apollo-wp-bridge/sealed/qa -p test_sealed.py -v
python experience2/apollo-wp-bridge/sealed/qa/browser_exact.py
```

Dependencies: Python 3, `tinycss2` 1.5 (build), PHP >=7.4 (runtime and CLI QA), Playwright Python package and Chromium (QA only). **No paid service or network at runtime.** The ZIP is byte-for-byte reproducible; its three files are plugin PHP, SHA256 source manifest and installation HOLD note.

Private staging *after separate approval* requires `WP_ENVIRONMENT_TYPE=staging` (or development/local), `FV_EX2_APOLLO_STAGING_ALLOW=true` defined in staging configuration, a logged-in `edit_pages` reviewer and valid WordPress nonce. Shortcode: `[fv_ex2_apollo_sealed_preview]`. The handler registers **no anonymous Ajax endpoint**. Pages, scripts, styles and exports are embedded in authenticated responses; no public static media, JSON, HTML or CSV artifacts. No JS is required to read the source cards; progressive enhancement adds filters and anchored navigation. A sandboxed iframe isolates themes and restricts top-level navigation. **Do not activate on production, even for testing.**

## Verification executed (2026-10-30 Pacific)

- All 12 historical source Git blob SHA-1s reproduced in a local checkout from the exact GitHub PR #215 data; previous 39-character pin corrected. Earlier four-source-file fixture divergence eliminated.
- Local `unittest` **9/9 PASS**: two deterministic ZIP builds, PHP lint, production/off/guest/reader denial, nonce denial, private shortcode and Ajax registration, complete page rendering, four downloaded export byte identities, path traversal rejection, tamper denial, CSP/no-WordPress-mutation structural contracts.
- Real Chromium Playwright **7/7 widths PASS**: 320, 360, 390, 768, 1024, 1440, 1920 CSS px, 6 chronology stages, 6 response comparisons, 6 documentary trails, 6 Atlas records, no root overflow or JS exceptions. Verified source filters, reset, source drawer and hash-focused navigation, no-JS access, 390px touch and 640px simulated 200% zoom. PNG previews at 390 and 1440 for hero, Research Desk, Atlas and trails; reproducible commands and screenshot SHA-256 hashes recorded.
- Laboratory Playwright `page.set_content` and meta-CSP approximation produced **LCP observations 140–300 ms and CLS 0** across the seven tested widths. These measure an offline in-memory document with no network, not a production page or field p75 Core Web Vitals; the page has no externally fetched imagery. The meta approximation cannot validate actual HTTP CSP, headers, cookies or WordPress iframe sandbox behavior.
- **axe-core NOT RUN** because no locally verified pinned bundle was available. A parameterized optional axe hook is included in `qa/browser_exact.py`: `FV_VERIFIED_AXE_BUNDLE=/path/to/axe.min.js FV_VERIFIED_AXE_SHA256=<verified sha256>`. No WCAG 2.2 AA certification is claimed.

## Editorial, rights and geography

Primary official sources rechecked 2026-10-30: NASA Apollo 204 Review Board report, https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ and NASA historical response, https://www.nasa.gov/missions/apollo/apollo-1/nasa-response-to-findings/. The Board considered an electrical arc the **most probable** initiator but could not conclusively identify a single ignition source. The 1968 response documents reported recommendations and measures, **not** certification that every remedy was fully implemented. The atlas uses six source-defined narrative records with **no invented geometry, pins, or inferred relations**.

NASA media guidance, https://www.nasa.gov/nasa-brand-center/images-and-media/, permits certain reuse subject to limitations, including no endorsement implications and separate rights for third-party assets; it is **not** per-item image clearance. This code reproduces no archival photographs, NASA marks, or NASA promotional claims. Treat actual media reuse as a separate editorial/rights review.

## Outstanding non-waivable gates

- Execute the package on an **authorized private WordPress staging** server with real authentication/nonce/iframe CSP, export MIME/download routing, no visitor access to the unpublished assets, and the actual theme.
- Run an **independently verified axe-core** scan and manual NVDA/VoiceOver/Safari and keyboard zoom tests; resolve violations and human review.
- Collect Lighthouse and real-user p75 LCP, CLS, INP after genuine staging hosting; local synthetic 140–300 ms does **not** predict field performance.
- Independent QD review, hosted CI on the exact SHA (Actions startup incident #75), founder art direction and explicit separate release approval. No homepage, Research Desk PR #158 or public WordPress writes.
