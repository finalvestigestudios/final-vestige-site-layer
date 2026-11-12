# Apollo Experience 2.0 / R315 — Native context-menu continuity (staging only)

**Status:** draft; unmerged; not installed on WordPress. Isolated from frozen homepage PR #49 and independently owned Research Desk PR #158. Stacked directly on R314 draft PR #2222. Coordination: #150, #820, business charter #818.

## User-visible defect and boundary

Prior staging enhancement carried source-matched Grok campaign identifiers only on primary `click` and middle-button `auxclick`. A reader opening the existing free Apollo investigation through a native right-click context menu did **not** receive validated labels. R315 adds a **trusted right-button `contextmenu`** path using the existing allowlisted four-field validator. It does not intercept navigation, add a CTA, record an analytics event, read storage, load an external script, or declare any lead/purchase/revenue.

Only the exact Apollo editorial destination receives labels, and only on a properly scoped Atlas instance. Malformed, missing, duplicate or PII-like input is rejected. The canonical server response is identical for different visitor query strings, protecting shared cache bodies from cross-visitor UTM injection. JavaScript/CSS failures preserve the original link and fully readable historical evidence. The exact R314 script is pinned in `qa/r314_prior.js` as a falsifiable negative control. R315 does **not** establish a genuine native-menu "Open in new tab" destination in this restricted environment; it validates the link value at the menu event.

Context-menu activation represents **navigation intent, not a purchase, checkout, verified signup or qualified human session**. Native keyboard menu shortcuts and every browser's menu implementation are still pending independent acceptance. A long-lived SPA can temporarily retain a campaign-bearing link until a subsequent validated activation; actual installed WordPress/CDN lifecycle, consent and link-copy behavior remain release gates.

## Reproduce

Requires PHP, Node, Python with BeautifulSoup and Playwright, and Chromium at `/usr/bin/chromium`.

```bash
python experience2/apollo-r315/qa/contextmenu_gate.py
```

Source-controlled gate: 11/11 actual offline Chromium viewport/JS contexts PASS, spanning 320, 390, 768, 1440 and 1920px; invalid label rejection; two-instance isolation; no-JS fallback; PHP response parity; source/media role counts. Extended 24/24 local Chromium tests and genuine R314 negative control are included only in the downloadable R315 QA archive; **do not misstate them as the committed gate.** Inherited R314 gate 11/11, R311 cache-isolation and R312 source/link-purpose regression gates PASS locally. Offline fixture LCP and CLS readings are not field Core Web Vitals.

## Flagship and one conversion hypothesis

**Audience:** history/documentary viewers who follow a Grok Apollo 1 investigation to examine primary documentary evidence. Controlled journey: approved Grok Apollo film → source-backed Atlas → free original Apollo investigation → **only after separately verified approval**, relevant rights-cleared and currently payable FV teaching/evidence product. This sprint changes no historical claim, NASA original URL, contextual photograph, geo pin or commercial offer. NASA photographic catalogue IDs are not causal proof or commercial use licenses; NASA cannot be portrayed as endorsing FV merchandise.

**Hypothesis:** readers taking legitimate context-menu navigation actions should not lose valid campaign context; **not a proven increase in purchases or revenue**. The TASK-008 generic Grok `history_pilot_yyyy_mm` campaign scheme and the current narrowly constrained Apollo validator are not yet reconciled. No published Grok Apollo asset_id or destination is verified. This has to be explicitly resolved before any measurement release; do not silently relax validation.

## OFFER → FUNNEL → BLOCKER → CHANGE → EVIDENCE → OWNER

| Offer / step | Blocker and experiment | Evidence | Owner |
|---|---|---|---|
| Apollo-relevant FV teaching/evidence product → paid checkout | Payable rights-cleared Apollo SKU and merchant reporting unverified; validate before any CTA | HARD HOLD, no claimed revenue | Founder + Claude |
| Grok documentary → Atlas | No authenticated published asset ID/destination; reconcile TASK-008 UTM schema first | UNVERIFIED | Grok + Praxxis |
| NASA Atlas → free investigation | Native right-click was not supported; test narrowly scoped campaign continuation | R314 negative control; R315 offline Chromium PASS | Apollo |
| Qualified session → verified order → refunds/fees → realized net | No reconciled human cohort, merchant order or refund records | KPI not computable | Claude + Commerce |

Primary KPI: confirmed realized net revenue per 1,000 qualified human sessions, reported in 7/30-day cohorts with tiny-sample warnings. Link annotation is neither an attributed sale nor purchase evidence.

## HARD HOLD — release governance

Genuine axe-core, NVDA/VoiceOver, actual WordPress/Assembler, CDN cache behavior, native HTTP/CSP/popup menu, production LCP/CLS/INP, device-specific touch/keyboard and consent review, NASA image/editorial and independent QD clearance, verified Grok IDs, fully payable relevant offer, hosted exact-HEAD CI and founder approval remain outstanding. No WordPress, homepage, merchant, analytics, social, email, affiliate or spending writes are authorized.
