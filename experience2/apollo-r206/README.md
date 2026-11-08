# Apollo Experience 2.0 — R206 evidence-confidence ladder

**STAGING ONLY / NOT APPROVED FOR PRODUCTION.** Parent R205 PR #1526, governing Experience issue #150, revenue issue #820, charter #818. Homepage PR #49 and Research Desk PR #158 must not be edited or merged as part of this lane. Claude owns production engineering, Grok owns social assets, Praxxis independent creator review, and founder owns release/paid activation.

## User-facing implementation

Native `<details>` / `<summary>` source-confidence panel immediately after the four-record ChronologyRail, separating **Documented** (100% oxygen, 16.7 psia and combustibles), **Most probable** (electrical arc), and **Not determined** (specific ignition event). Each includes its precise evidence limitation, an internal evidence navigation link, and a primary NASA source. No third-party images or geo pins, no additional client JavaScript. Screen-reader and keyboard accessible native disclosure structure. Responsive at 320–1920px, reduced-motion/forced-colors CSS, and *verified printed disclosure expansion*. Inherited eight disclosures, gallery, source link index and one editorial CTA remain. No paid product/affiliate CTA or tracking instrumentation introduced.

NASA source references: [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/), [NASA S67-21294 aftermath catalog](https://www.nasa.gov/image-detail/amf-s67-21294/), [NASA advertising guidance](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/). Linking to a NASA source is not commercial media/likeness clearance.

## Exact build instructions and release block

R206 generator: `python experience2/apollo-r206/build_r206.py`; local fixture: `python experience2/apollo-r206/qa/gate_r206.py /tmp/r206-qa`. Python 3, PHP CLI, `playwright`, `bs4`, `/usr/bin/chromium` required for local browser QA. The generator requires the **generated R205 dist** at `experience2/apollo-r205/dist/` with manifest-hashed assets, rather than silently reconstructing uncertified history. R205 dist is intentionally not committed in its source-only PR. Unless that dist is supplied and independently verified, a clean GitHub checkout cannot pass this build. This failure is expected, and **DOES NOT count as CI-green**.

The inherited R198 local generator Git blob `2e09257cbd0b32a93f2e7e034a84685d93ed93f5` is different from canonical R198 GitHub blob `57ef73d5719662a1b3647536a0eace5fb65bac4a`. `source_chain_verified=false` stays in the manifest. Do not remove the block without a canonical rebuild and independent review. Parent SHA `0f64a13fb258f8c4007c2d04d7553085d7500019`.

## QA scope and limitations

The packaged **local** test used PHP shortcode rendering and Chromium 144 with 2 independent runs × 10 browser contexts (320, 390, 768, 1440, 1920, no-JS, mobile touch, reduced motion, forced colors, CSS zoom). It tested keyboard Enter toggling, labels and links in Chromium AX tree, duplicate IDs and unique CTA, source provenance, 8 malformed/misleading mutations, printed closed disclosure contents, error logs, overflow, LCP/CLS via PerformanceObserver (fixture only), and screenshots whose 10 cases matched across both runs.

**Not performed:** genuine axe-core, NVDA or VoiceOver, actual browser UI zoom, installed WordPress/Assembler acceptance, public HTTPS/CDN/CSP/performance acceptance, exact-head GitHub-hosted CI, independent QD release review. Local LCP/CLS are not production CWV. No paid checkout, merchant order, refund, confirmed signup, Grok Apollo asset ID or attributable human-session denominator was verified.

## Revenue-first hold

High-intent audience: history educators and evidence-focused Apollo viewers. Proposed route: Grok long-form documentary → Apollo Evidence Atlas → confidence and primary sources → free original investigation → **optional original educator evidence dossier if and only if a rights-cleared, approved, truly purchasable SKU is later validated**. The paid dossier is hypothetical; no sales CTA is displayed. Metric once valid: independently confirmed net revenue per 1,000 qualified human sessions, using asset IDs, 7/30-day cohort reconciliation, actual merchant-confirmed orders, fees and refunds. Do not equate clicks or attributed site traffic with revenue.

Release decision: **STAGING HOLD, no production actions.**
