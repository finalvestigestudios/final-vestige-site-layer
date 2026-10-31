# Apollo sealed staging: authenticated HTTP release gate (DRAFT / HOLD)

**Scope:** Apollo Experience 2.0 only. Source-pinned to Apollo documentary PR #215 commit `74375657f2cdaac0710f94c6de6c24534ee06858`. Stacked on sealed-preview PR #228. Do not touch homepage PR #49, lead homepage branches, standalone Research Desk PR #158, or WordPress production.

## Change and why it matters

The existing sealed preview's CLI PHP tests inspected body output but did not verify actual HTTP status codes, CSP response headers, downloadable evidence bytes, and direct-source URL exposure on a network socket. This draft adds a **local-only synthetic WordPress PHP HTTP router** and an independent Python `unittest` that performs those checks over actual localhost HTTP. It also adds an editor-only **full-page authenticated alternate review link** for keyboard, narrow-screen, and assistive-technology reviewers, avoiding dependence on nested iframe scrolling. The iframe remains opaque-origin (no `allow-same-origin` or top navigation). Popups explicitly escape inherited sandbox restrictions so NASA references open in an ordinary tab. All access remains restricted to a logged-in editor on opt-in, non-production environments and a valid WordPress nonce; no public static source files.

## Reproduction in a checkout containing the exact PR #215 sources

Run:

```sh
python -m unittest discover -s experience2/apollo-wp-bridge/sealed/qa -p 'test_sealed.py' -v
python -m unittest discover -s experience2/apollo-wp-bridge/sealed/qa -p 'test_http.py' -v
python experience2/apollo-wp-bridge/sealed/qa/browser_exact.py
python experience2/apollo-wp-bridge/sealed/build_sealed.py --out /tmp/fv-apollo-private.zip
```

`test_http.py` starts PHP's local development server, binds **only** to 127.0.0.1 with an ephemeral port, and shuts it down after tests. The synthetic router does not serve arbitrary files. Denied users do not see the iframe or private payload. Access checks cover guest, reader, production, disabled opt-in, malformed nonce, export-path traversal, direct static paths, absent public AJAX route, exact CSV/JSON bytes, CSP/anti-indexing/anti-sniffing/Referrer-Policy headers, and deterministic ZIP generation.

## Local evidence, 2026-10-30

* **9/9 existing Python/PHP security tests PASS**, **8/8 new HTTP unittest cases PASS**, **seven Chromium in-memory exact-source viewports PASS** (320, 360, 390, 768, 1024, 1440, 1920). These were run on locally reconstructed exact PR #215 inputs plus this proposed PHP change. The GitHub checkout test of this exact new PR head still requires execution.
* Synthetic in-memory LCP observations were 124–288 ms across the seven widths; observed CLS 0. This does **not** establish actual WordPress field Core Web Vitals.
* **Browser-enforced HTTP CSP/cookies/iframe status: NOT VERIFIED.** Chromium navigation to all localhost/external origins is blocked by `net::ERR_BLOCKED_BY_ADMINISTRATOR` in this execution environment. HTTP requests made by Python and PHP do work and validate the actual headers. The prior `page.set_content` browser tests use an approximate meta CSP; they cannot certify header-enforced CSP or cookie behavior.
* **axe-core: NOT RUN.** No locally verified/pinned axe-core bundle is available; do not report WCAG 2.2 AA certification.
* **WordPress integration: NOT INSTALLED OR TESTED.** Synthetic WordPress methods emulate permissions/nonce; actual WordPress session cookies, editor roles, iframe headers, WP cache/CDN configuration, plugin interactions, Safari, NVDA/VoiceOver, Lighthouse, and real-user CWV remain open.
* Historical records use NASA sources as outbound hyperlinks. No NASA photographs or logos were added. NASA states that its imagery is generally reusable under conditions, including no implied endorsement; individual item/release review is still required. See https://www.nasa.gov/nasa-brand-center/images-and-media/ and https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/.

## Release gate

**HOLD** until founder-approved isolated WordPress staging exists, direct HTTP browser CSP/cookie checks and manual keyboard/screen reader testing succeed, verified axe-core runs on the exact checkout, NASA per-item rights are cleared for any reproduced media, hosted CI is green, and independent QD signs off. Never merge this stacked draft automatically or deploy/activate the plugin.
