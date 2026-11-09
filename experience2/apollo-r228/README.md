# Apollo R228 — source-navigation access and release gate

STAGING ONLY — NOT LIVE. Isolated child of R227 draft PR #1671 (base SHA f4eb0c76d972c7815b2611e6e2f36d2e969dbfa2). Do not edit frozen homepage PR #49, Research Desk PR #158 or WordPress. Source of truth: issues #150 and #820.

## Finding and implementation

390px Playwright inspection found standalone source-trace and custody links with 20px clickable height. The builder verifies exact R225 input assets (manifest SHA256 4efaf0a57d38af349d44302905fbfdc8b8936ac8bbc04a2d7a61fb805ba93628), adds scoped 44px-minimum touch targets and visible keyboard focus, repins the CSS SHA in a disposable PHP adapter and emits a deterministic manifest (SHA256 28f1427da6d096c801927ac8e1e8dd8a53f14ff3f6fcb014089ada2bdd662413). It leaves NASA evidence, URLs, and the single free investigation CTA unchanged.

## Reproduce locally

Use the unmodified generated-r225 directory from the R225 evidence archive; Python Playwright, Chromium at /usr/bin/chromium and PHP are required. The parent R227 PHP shim and Python acceptance suite must be present at their normal repo paths.

1. python experience2/apollo-r228/qa/build_accessible_source_paths.py --parent generated-r225 --out generated-r228
2. php -l generated-r228/fv-ex2-apollo-r224.php
3. python experience2/apollo-r228/qa/source_path_browser_gate.py --dist generated-r228 --out qa-r228-A
4. python experience2/apollo-r228/qa/source_path_browser_gate.py --dist generated-r228 --out qa-r228-B
5. Compare SHA256 of qa-r228-A/receipt.json and qa-r228-B/receipt.json.

Two real local Chromium runs each passed 10 contexts (320/390/768/1440/1920 CSS px; JS enabled/disabled), source target dimensions, keyboard/native touch disclosure, fallback PHP lifecycle (nine cases), five content-tamper cases, zero remote browser requests, and no horizontal overflow. Both screenshot sets and receipts matched; receipt SHA256 4ee8446418f60d43e1a060d20d48b94880badf40aab1d46ba184fa281bc3fcbb.

## Hard hold

These tests use the real generated PHP and browser component output, but a simulated WordPress function shim and Playwright page.set_content. They DO NOT establish installed WordPress/Assembler, navigation to a real HTTP host (administrator blocked), genuine axe-core (offline package unavailable), NVDA/VoiceOver, actual browser zoom, hosted exact-head CI, field LCP/CLS or commercial conversions. The inherited R198 ancestry discrepancy remains open. Independent QA and founder approval are required before any merge/release.

NASA technical source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ . NASA commercial and endorsement restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . No new images, geo pins or unverified media rights.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE → EVIDENCE → OWNER

Apollo educator dossier → paid order: no approved SKU/rights/checkout → no commercial activation → HOLD → Founder/Claude. Verified Grok Apollo asset → Atlas: no published asset_id/UTM from TASK-008 → source-linked handoff → UNVERIFIED → Grok/Praxxis. Atlas → free investigation: small source taps → 44px target patch → LOCAL PASS → Apollo. Attributed paid orders → net revenue: missing merchant orders/refunds/fees and qualified-human sessions → 7/30-day reconciliation → NOT COMPUTABLE → Analytics/Commerce. Never equate clicks with paid sales.

No live publishing, email, script activation, social posting, affiliate modification, or spending.
