# Apollo Experience 2.0 — R233 exact-fixture browser acceptance (STAGING HOLD)

**Scope:** one isolated QA addition stacked on Apollo R229 (`a7ff175f4035cd0d9ccc3d6d8a9bc70f8b60c028`). No component, home page, Research Desk PR #158, revenue offer, WordPress page, or production file changed. This is a release-quality testing improvement, not a deployment request.

## What is different from R229

R229 tests text contrast and semantics against the pinned R228 Atlas. R233 additionally runs **real Chromium PerformanceObserver LCP/CLS** on the **actual generated Apollo HTML/CSS**, 320/390/768/1440/1920px (JS enabled and disabled), and a 256px **reflow proxy**, with native keyboard disclosure, exact source-record count (4), a single existing free-investigation CTA, no unauthorized outbound requests, no invented geo coordinates, and no horizontal overflow. The generated R228 source manifest SHA-256 is **`28f1427da6d096c801927ac8e1e8dd8a53f14ff3f6fcb014089ada2bdd662413`**, with every referenced file rehashed before browser execution. Never accept a changed fixture silently.

Run (after producing the exact R228 generated bundle with its pinned builder):
```bash
python experience2/apollo-r233/qa/r233_perf_gate.py --dist /path/to/generated-r228 --out /tmp/apollo-r233-A
python experience2/apollo-r233/qa/r233_perf_gate.py --dist /path/to/generated-r228 --out /tmp/apollo-r233-B
sha256sum /tmp/apollo-r233-{A,B}/receipt.json
```

### Local evidence on November 8–9, 2026

Two independent system Chromium 144/Playwright executions of the *exact committed script* against the SHA-pinned full generated bundle produced **11 contexts/run PASS**, all 11 full-page screenshot pairs identical, and identical deterministic `receipt.json` SHA-256 **`c04c4b5e687e7f7c84396236f947a5472e4b904a0314c269f593bc54801b2e6f`**. Data: four source records, minimum four native disclosures, precisely one original investigation CTA, no JS and no-JS preserved, 0 horizontal overflow at 256/320/390/768/1440/1920, 0 unexpected network requests, no geo attributes. Native Enter-key disclosure passed.

The **non-deterministic** `fixture-performance-observations.json` is deliberately separate from the deterministic receipt. R233 observed local LCP **96–240 ms** across two executions and five standard widths; post-observer CLS **0** throughout. These results are *not* field CWV or valid installed-site performance claims: `set_content` loads an inline local document with no network, no WordPress, no image loading, no real user traffic, and no full session of layout-shift monitoring. 256px is a **reflow proxy**, not a tested 400% browser UI zoom. Genuine axe-core, manual screen reader, installed WordPress/Assembler, hosted CI, R198 ancestry reconciliation and founder approval remain missing. Fail the release gate until these are satisfied.

## Commercial boundary

**Flagship:** Apollo 1. **Proven immediate action:** the original free Apollo investigation, with NASA evidence and source limitations visible first. **Hypothesized later product:** educator evidence dossier (not a product, no SKU or checkout verified). Proposed funnel remains real Grok published asset (unknown ID; verify via existing TASK-008 with Praxxis) → Apollo Atlas/Research Desk → free investigation → rights-cleared approved educator pilot if demand validated. Do not insert an unrelated affiliate offer or count outbound clicks as sales.

**OFFER → FUNNEL → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL → OWNER**

- Hypothetical educator dossier → paid purchase → rights/merchant/SKU/fulfillment unverified → demand and checkout review → **HOLD** → founder / Claude.
- Grok documentary → Atlas → actual `asset_id`, published URL, media rights and UTM destination unverified → reconcile existing TASK-008 only → **UNVERIFIED** → Grok / Praxxis.
- Atlas → free investigation → real-fixture performance and 256px reflow previously not measured → R233 independent Chromium gate → **LOCAL COMPONENT PASS, INSTALL HOLD** → Apollo.
- Verified orders → net revenue → no authenticated payment/refund/qualified-human session joins → 7/30-day reconciliation by `asset_id/utm_campaign` → **NOT COMPUTABLE** → analytics / commerce.

## Governance

No homepage PR #49 or lead homepage branch edits; PR #158 untouched; no CMS, paid service, creator queue, publishing or merchant writes. Source rights must be evaluated separately from NASA archival page availability. The inherited R198 source-ancestry discrepancy is unresolved. Exact screenshots and receipts are stored in the locally reproducible R233 evidence package; production release remains **STAGING HOLD**. Cross-reference Issues #150, #818 and #820.
