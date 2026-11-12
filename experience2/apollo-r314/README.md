# Apollo Evidence Atlas R314 — trusted input parity (staging only)

**Status: draft, no live deployment, no commercial activation.** Isolated from homepage PR #49 and Research Desk PR #158; this is stacked on Apollo R313. Issue #150; conversion coordination #820 and business charter #818.

## Defect and implementation

R313's first-party, click-only UTM continuation ran on a trusted `click` event. Chromium uses `auxclick` for a middle mouse-button activation, so this legitimate open-in-new-tab path did not carry approved Apollo campaign labels. R314 uses the same safe URL validator for trusted primary `click` and middle-button `auxclick`, rejects right-button/synthetic/canceled events, and never prevents navigation. Only the existing **free** Apollo 1 investigation link is eligible. No cookies, analytics, external requests, added CTA, merchant integration, source rewrites or paid conversion claims.

The PHP renderer remains byte-identical across UTM request variants; versioned script enqueue changes solely to load the amended staging file. No-JS or missing dynamically enqueued script: plain first-party editorial link remains usable. Context-menu copy/open-new-tab, pre-navigation URL handling by every browser, actual HTTP/CSP and production campaign persistence have **not** been certified.

## Reproduce (Python Playwright, Chromium, PHP, BeautifulSoup)

```bash
python experience2/apollo-r314/qa/committed_gate.py
python experience2/apollo-r314/qa/input_activation_gate.py
```

- Committed gate: **11 actual offline Chromium contexts passed**: 320–1920 widths, native middle clicks, invalid label rejection, byte-identical PHP and no-JS fallback.
- Extended local QA: **21 actual offline Chromium contexts passed**: touch/keyboard, JS on/off, repeated instances, forced colors, reduced motion, native middle clicks, invalid PII-like label, synthetic event rejection, SPA history-change reset and native accessibility-tree name checks. The extended gate is included with this review evidence bundle; its independent outcome is not a substitute for axe-core or manual screen-reader testing.
- Negative control: R313 middle-button test **fails to carry** validated labels; R314 passes with the same fixture.
- Existing R311 cache-isolation, R311 source-controlled, R312 source-controlled and R312 link-purpose Python gates passed. R313 source-controlled inheritance timed out on this environment, so is **not** counted as passed.
- Offline `PerformanceObserver`: Chromium LCP 68–140 ms, CLS 0 across 320/390/768/1440/1920 widths, **not production field performance**.

## Release and commercial HOLD

Needs genuine axe-core, independent NVDA/VoiceOver and touch-device QA, installed WP/Assembler/CDN, real browser HTTP/CSP and popup/new-tab URL acceptance, consent/privacy and Grok asset-ID review, hosted CI, NASA editorial/rights review and founder release approval. Nothing in this branch establishes a paid offer, a verified signup, an order, a refund, net revenue or valid 7/30-day acquisition cohort.

One controlled future path: approved Grok Apollo documentary asset → Atlas → verified NASA evidence → free Apollo investigation → separately approved, truly payable and rights-cleared educational product. Do not insert Apollo 11 memorabilia as Apollo 1 documentary evidence or suggest NASA endorses FV goods. Commerce/Claude must authenticate payable offers and net revenue separately; only then run a controlled offer-path experiment. The key KPI remains **realized net revenue per 1,000 qualified human sessions**; currently not computable.
