# Saved Gutenberg performance: independently verified budget failure (2026-11-02)

**Decision: DRAFT / RELEASE HOLD.** This is a diagnostic/qualification change, not a design expansion, production release, or independently approved optimization.

## Reproducible source

- Parent draft PR #693 exact SHA: `8ad099cd8dc7e9c4e88ada2b5c41f8b244a6d780`.
- GitHub Actions run: https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41542357489
- Uploaded artifact #13187695354, GitHub zip SHA-256: `88bf66ba407b27aaf52c1fd995a8435e06368b1f57b93e51e7dc5cddd85f6a38`. Independently downloaded and matched byte-for-byte to the announced digest.
- Inside artifact: `GUTENBERG_SAVED_NATIVE_CDP_LAB.json`, `source_sha` exactly matching #693.
- Environment: authenticated ephemeral local WordPress/Assembler **saved Gutenberg page**, using **synthetic placeholder copies of protected blocks**. It is neither the private iframe nor hosted WordPress.com.
- Chromium CDP: **cold browser cache**, 390px mobile, 4× CPU slowdown, 150ms simulated RTT and 1.6Mbps downlink. Desktop: 1440px unthrottled. The automated `PerformanceObserver` collects LCP and layout shifts, excluding recent input.

| Actual measured trial | LCP (ms) | CLS | responseStart (ms) | Meets 2.5s laboratory LCP target? |
| --- | ---: | ---: | ---: | --- |
| mobile_390_trial_1 | **4,132** | 0 | 1,043.3 | **NO** |
| mobile_390_trial_2 | **4,112** | 0 | 1,048.2 | **NO** |
| desktop_1440 | 1,184 | 0 | 888.6 | Yes |

**Important correction to prior reporting:** Both GitHub CI jobs passed because the test measured and recorded results successfully; the previous harness reported `any_lab_budget_missed=true` but did **not** fail admission or diagnose the LCP element. Thus previous private-iframe Lighthouse 97–99 mobile scores cannot be used to claim the **saved Gutenberg page** meets its mobile LCP target. This source-controlled diagnostic makes the missed laboratory budget explicit, machine-readable and separately tested.

## Changes in this stacked draft

- Capture redacted LCP candidate identity (HTML tag, tightly allowlisted Final Vestige element ID, element size and resource-backed flag). **Do not upload document text, cookies, HTML, image URLs, query strings, browser storage or traces.**
- Record cold-cache first-contentful paint and navigation response-end/DOM-ready/load timings so slow HTML response can be separated from LCP rendering and media delay.
- Add `native_lab_budget_gate: FAIL | PASS_LAB_ONLY`, `lab_budget_misses`, permanent `release_gate: HOLD`, and `SAVED_NATIVE_CDP_BUDGET_MISS_RELEASE_HOLD` status.
- Adversarial budget regression tests assert that the two **actual observed** mobile failures remain release blockers. CI can certify instrumentation works while the **release budget remains red**; this distinction prevents an erroneous go decision.

## Next evidence-driven optimization, not yet assumed

1. Re-run at this PR's exact new Git SHA. Inspect redacted `lcp_element`, `page_timing_ms` and actual network timings before changing styles or resource loading.
2. If LCP is hero text, isolate font/style/layout delays (avoid animations that conceal content), compare cold-cache FCP and LCP; if resource-backed, inspect first-party image priority and discovered dependencies. Treat the present 1.04s mobile responseStart as a measured fact, **not proof of root cause**.
3. Optimize only after attribution. Require both throttled mobile trials <=2.5s (lab target) and no content, accessibility, rights or no-JS regression. Also collect full Lighthouse scores from the actual saved page when feasible, not the iframe.
4. Even after a lab-budget pass, independently verify manually: 200% browser UI zoom, AT and real touch devices, legal source/asset custody, hosted WordPress.com Personal behavior and founder/QD signoff. Lab results are **not p75 field Core Web Vitals**.

**No new image or media rights are asserted.** The disputed NYPL capture remains excluded from candidate reproduction; Apollo NASA crew photo and Franklin Commons scan remain separately reviewable. All seven chapters, native Jetpack/Focus/Margins preservation gates, PR #49 freeze and no production writes remain mandatory.
