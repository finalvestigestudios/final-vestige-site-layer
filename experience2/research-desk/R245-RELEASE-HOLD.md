# R245 — Research Desk NASA-evidence touch targets (staging hold)

Date: 2026-11-09. Parent: R244 draft PR #1790 at `2497c9b346268670fc5d76cad805a27e75127a78`; protected original Research Desk PR #158 at `250d7f05a4de037e73826dcf0cfaef0ec4c29383`. Independent of frozen homepage PR #49 and Claude's production website work.

## Implemented

The 13px Research Desk source links and disclosure summaries were not provided a minimum 44px touch target. R245 adds scoped min-height/padding/touch-action to evidence-source links and native finding summaries. The @media print overrides restore inline citations/compact summary sizes, preserving the R244 evidence-custody treatment and fully printable NASA URLs. No historical copy, original NASA URL, gallery image, JavaScript, conversion CTA, analytics, checkout, or WordPress settings changed.

## Executable QA

- `qa/r245_accessible_targets.py` supports default **EXACT_NASA_TEMPLATE**, checks the original `ledger.html` Git blob `403d128c57b9bc82dac7c619651689070edef86c`, and exercises the unchanged PHP adapter. It refuses altered original historical HTML.
- `--fixture` is explicitly **SYNTHETIC**, for repeatable browser-target/print CSS regression only. Command: `PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium python experience2/research-desk/qa/r245_accessible_targets.py --source experience2/research-desk --out /tmp/r245 --fixture`.
- Local independently written regression of the same CSS behavior: two Chromium 144 runs, 10 contexts each (320, 390, 768, 1440, 1920px, JS on/off, reduced motion, mobile touch). Both passed; the synthetic fixture measured minimum evidence-link targets 62px, native summaries 64px (these values are from a synthetic baseline stylesheet, **not exact-template pixel measurements**). Keyboard Enter disclosure, print restoration of hidden source, printable NASA URLs, zero unexpected network requests, zero horizontal overflow passed.
- Two fixture receipts were byte-identical; four screenshot pairs byte-identical.
- This run did **not** execute the committed script against the protected original HTML or a real installed WordPress/Assembler site. Genuine axe-core, NVDA/VoiceOver, browser zoom, field LCP/CLS, hosted CI, independent QA, NASA media commercial-rights clearance and founder release approval remain outstanding. Historical R198 source ancestry discrepancy remains under hold.

## Business priority and rights

Flagship: Apollo 1. Grok owns documentary/Shorts creation and distribution. Praxxis owns independent creator QA and TASK-008; this lane owns the evidence-source in-site bridge.

Hypothesis: interested documentary viewers reach the fact-checked Research Desk, can reliably use NASA citations on touch devices, and follow one existing free Apollo investigation action. That increases qualified audience trust *before* a separate, founder-approved and merchant-verified space-history offer (potential Mini Museum). **No paid CTA was activated.** Do not associate NASA with a commercial product or imply endorsement. References: [NASA Apollo 204 Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/) and [NASA advertising guidance](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/).

| Offer | Funnel step | Blocker | Change/experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|---|
| Mini Museum, conditional | purchase | Merchant acceptance/rights, settlement not verified | Hold placement; verify partner, consent, product relevance and checkout | **HOLD** | Founder/affiliate/Claude |
| Apollo investigation (free) | Research Desk → investigation | Small source and summary tap targets | R245 CSS target treatment and print preservation | **SYNTHETIC LOCAL PASS; REAL WP UNTESTED** | Apollo |
| Grok Apollo asset | social → landing | No published asset_id/UTM proof in this lane | Reconcile TASK-008 and dated handoff | **UNVERIFIED** | Grok/Praxxis |
| Any verified SKU | order → net revenue | No reconciled transaction, fees/refunds or qualified sessions | 7/30-day cohort + net revenue per 1k qualified humans | **NOT COMPUTABLE** | Claude/commerce |

**Release decision: STAGING HOLD.** No merge, production deploy, live WordPress write, new script, newsletter, social posting, affiliate activation, or paid service.
