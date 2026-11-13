# Apollo Evidence Studio R335 — computed text-contrast QA (staging only)

**Parent:** Apollo R333 draft PR #2331 (`1144b5c624c46e021ac4c4f543f834d050fd9fc2`), under Issue #150; conversion charter #820/#818. This QA-only child does **not** modify Apollo runtime, Research Desk PR #158, either of the existing independently authored R334 Research Desk custody-bridge drafts (#2340/#2342), frozen homepage PR #49, WordPress content or settings, Grok's queue, merchant, analytics, emails or production. Independent repository QA to assist final editorial acceptance.

## Why this matters

Accessibility source links are a *trust and conversion-path requirement*. Existing tests covered hitbox dimensions, 320px/400% reflow and named controls, but did not quantitatively evaluate text contrast over the actual colored cards after all native disclosures are expanded. R335 exercises the real R281 PHP code via the already-reviewed WordPress lifecycle stub and Chromium's **computed styles**, rather than screenshots, guesses or HTML-only assertions.

`qa/contrast_gate.py` tests 16 actual offline Chromium browser contexts across 320, 360, 390, 768, 1024, 1440 and 1920px, JavaScript enabled/disabled, 320px at 400% root text, 390px forced-colors and reduced-motion. All 3,264 visible text-node samples were >= WCAG text contrast ratio thresholds under the script's simple opaque-background nearest-ancestor model: 4.5:1 for normal and 3:1 for large text. It verified the 17 institutional sources, four rights-uncleared photo identifiers and single existing editorial CTA. Two unsafe palette mutations (near-black gold/muted text on dark ground) were correctly rejected by real browser reruns. Three actual full-page Chromium screenshots and a structured JSON test receipt are in the separate evidence ZIP; source-controlled runner generates them deterministically aside from browser rendering variability. This is useful regression protection but **not an axe-core report, an official WCAG certification, color-blindness simulation, or screen-reader acceptance**.

### Execute

From repo root with PHP 8+, Python 3, Playwright Python and Chromium installed at `/usr/bin/chromium`:

```bash
python experience2/apollo-r335/qa/contrast_gate.py
```

The test intentionally pins the reviewed R281 PHP, CSS and R320 WordPress-stub Git blobs. A changed parent source fails closed until explicitly re-audited; it must not silently borrow results from an old revision. Staged fixture, not installed WordPress/CDN or native HTTP/CSP. No external NASA image requests or commercial links, no invented geodata, no extra analytics or attribution events. Repeat on installed WordPress with genuine axe-core, NVDA/VoiceOver and Firefox/Safari; check focus indicators, non-text contrast, dynamic overlays and physical touch separately. Production LCP/CLS, orders, refunds, fees and revenue remain **unverified**.

### Conversion-first release plan

| Offer | Funnel step | Blocker | Change/experiment | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Apollo educator evidence kit | Paid checkout | No rights-cleared payable SKU confirmed | Authenticate existing product, merchant acceptance and usable checkout before any CTA | HOLD: no purchase/rights proof | Founder + Claude |
| Grok Apollo documentary | Social → Atlas | No published immutable asset_id/allowed landing URL confirmed | Obtain asset inventory via existing TASK-008 handoff (not by editing Grok's queue) | UNKNOWN | Grok + Praxxis |
| Free Apollo investigation | NASA source → editorial continuation | Unmeasured source-link contrast risk | Protect readable 320–1920px contrast in cached/no-JS source experience | LOCAL PASS 16 contexts; 3,264 text nodes | Apollo Evidence Studio |
| Settled order | Confirmed net revenue | Qualified visits, merchant orders, refunds/fees not reconciled | Use consent-respecting first-party plus merchant records, 7/30-day cohorts | NOT COMPUTABLE | Claude + Commerce |

Proposed (unlaunched) reader journey: **Grok Apollo documentary → verified NASA Atlas/Research Desk → the one published free Apollo investigation → separately approved, authenticated educational offer**. Neither an editorial click nor a prospective lead is a sale. Net realized revenue per 1,000 qualified-human sessions is the governing KPI, not views or raw clicks. No paid offer was inserted into the accident narrative. Founder/QD approval, hosted exact-HEAD CI, source-label resolution and rights/legal acceptance remain hard release blockers.
