# EX2 — isolated WordPress browser egress boundary (2026-11-07)

**Draft review only. RELEASE HOLD.** Child of PR #1429 exact `700e9322306ef09aaf3ee05c9321ed02b3d75ddf`. No changes to frozen PR #49, live WordPress Page 6, Focus Page 1579, theme, menus, Jetpack, analytics, public posts or affiliate campaigns.

## Verified implementation gap

`verify_integrated_playground.py` previously intercepted only top-frame navigations. All image, script, iframe, stylesheet and beacon requests could otherwise leave isolated WordPress staging. This is particularly inappropriate for an unpublished seven-chapter review build: third-party scripts/merchant endpoints must not receive staging requests by default. The bug is in the **QA harness**, not evidence of any live-site incident or data exfiltration.

The new `request_boundary.py` policy admits only:
- The exact isolated preview scheme/hostname/port (local WordPress or explicitly authorized private HTTPS developer preview).
- Inline non-network data/blob resources.
- The two source-reviewed archival URLs for Apollo 1 WP media #473 and Franklin WP media #474 and their strictly enumerated `i0.wp.com` responsive derivatives, classified as CDN not first-party.

It rejects live production `/focus/`, WordPress production REST calls, unexpected external tracking/ads/affiliate endpoints, wrong localhost ports, HTTP external media, spoofed domains, changed image queries, unauthorized embeds and cross-origin top-frame navigation. The actual browser gate is now wired to **every request**, and a blocked unexpected request becomes a fail-closed admission error. Source links in the document remain ordinary hyperlinks, but QA automation must not follow them to production.

The request boundary is deliberately restrictive. Legitimate new external assets must undergo rights/performance/privacy review and explicit policy revision **on a separate approved review branch**, not automatically inherit permission.

## Reproducible evidence

- `FV_EX2_BUNDLE_PATH=/path/to/fv-ex2-local-cli-preflight-guarded.zip python -m unittest -v test_native_identity test_run_local_wordpress_acceptance test_runtime_source_pins test_request_boundary` — **37/37 local tests PASS**, including 7 new request-policy/Chromium checks and 30 inherited tests.
- Actual Chromium request interception was exercised using `page.set_content()` (one 390px JavaScript-on in-memory fixture): injected unapproved image and third-party analytics script were both intercepted/aborted; history/museum texts were not altered. The test did **not** navigate to a local HTTP server because this container refuses localhost navigation (`ERR_BLOCKED_BY_ADMINISTRATOR`).
- Exact Git blobs: `request_boundary.py` `4b28513f4ee140eccf5c6d6e9ff8b4ab93235f69`; `test_request_boundary.py` `7a243c134895649e62543a4eb179b72da6bf08ec`; wired `verify_integrated_playground.py` `47a405b11d930a8e837a99b82abf93123bfea3a6`. The two new files' Git hashes match locally executed bytes. The wired full harness was source-reviewed but **not executed as a WordPress page**.
- The pinned ZIP remains SHA-256 `9833800a112027b17dfec154358d7b630e258feb581820b749ca26ab88ffe69d`; CLI 3.1.55, WP 7.1.4, PHP 8.3 and pinned Assembler commit unchanged.
- **Not established:** actual isolated WordPress/Assembler execution; first-party or CDN archive HTTP transfer bytes; independent axe WCAG 2.2 AA; keyboard/zoom/mobile touch in real WP; Lighthouse/CWV; Jetpack subscriber confirmation; Payhip/affiliate sale; CI/QD.

## Conversion-first acceptance

**Offer:** free 52-page Seven Day Focus Fieldbook. **Step:** source-rich hero to visible Focus CTA to real `/focus/` lead capture to verified paid customer. **Blocker:** uncontrolled browser egress could leak preview requests, distort source media/analytics evidence, and accidentally test live commercial destinations. **Change:** fail-closed request boundary in native acceptance. **Pass/fail:** 37 offline tests pass; actual WordPress and commercial conversion are not validated. **Owner:** interim homepage engineer + independent Site QA for nonproduction preview; Claude for production tracking/Jetpack, checkout and paid orders; Grok/Praxxis for permitted social acquisition.

Historical mission and seven chapters remain untouched. 72 Margins items, five proposed Focus links and the original Fieldbook/Jetpack experience remain intact; the rights-pending NYPL image #1258 is not allowed. No third-party commercial offer is activated, no earnings claims are made, and affiliate disclosures remain a separate pre-release acceptance gate.

## Next decisive action

Run the pinned guarded bundle in a **free, isolated**, network-enabled WordPress Playground with Assembler and actual local browser navigation, allowing only explicitly approved media fetches. Collect a genuine WordPress HTML/asset/network report, archived response byte hashes, independent axe + keyboard/no-JS/reduced motion, measured lab Lighthouse, actual /focus/ user path on a separately authorized safe test environment, and a reviewed founder screenshot set. A local WordPress clone does not certify WordPress.com host-specific Jetpack/signup, redirects, cookies, or field CWV. WordPress.com Personal lacks a native staging clone; no paid upgrade is proposed.

No merge, deployment, WordPress changes, social posts, email sends, affiliate activation or spending authorized. CI/QD and explicit founder release approval remain hard holds.
