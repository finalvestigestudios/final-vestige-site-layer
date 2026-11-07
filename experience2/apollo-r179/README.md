# Apollo R179 — runtime fail-open Research Desk search (STAGING ONLY)

Stacked on R178 draft #1335. Additive source and QA; frozen homepage PR #49 and original Research Desk #158 unchanged.

**Defect:** An R177 input-event exception outside initialization can leave 5/6 source records hidden. Synthetic status-update exception reproduced this fault in real Chromium. R179 restores six records, hides unusable tools, removes the failed input listener and prevents broken reinitialization. No changed history, NASA attribution, commercial links, analytics, persistence or network calls.

**Integration:** R179 JS is a replacement-only candidate for the existing source-ledger.js asset alongside the R178 PHP replacement and reviewed R174–R176 source template. Do not co-load PR #158/R177/R179 scripts or activate R178 as a separate plugin.

**QA:** node --check source-ledger-semantic-fail-open.js; python -m unittest -v test_fail_open.py. Local browser harness in evidence package uses the exact witnessed R177 baseline JS and source-derived R177 fixture. Actual offline Chromium: 210 assertions, 15 contexts, six widths 320–1920, 12 injected post-input failures recovered, JavaScript-disabled / forced-colors checks, no unexpected network/page exceptions, 6/6 repeat screenshot hashes. Fixture LCP/CLS are NOT production metrics. Genuine axe/installed WordPress/actual NASA media are NOT TESTED.

**Conversion:** Apollo 1 possible Grok flagship (post IDs unverified); source-grounded Research Desk → one existing Read original investigation CTA → hypothetical original rights-cleared educator dossier. No verified Apollo SKU, checkout, attributable sessions, confirmed paid orders or settled commissions. Net revenue per 1,000 qualified human sessions NOT COMPUTABLE. Issue #150, charter #818, conversion #820; TASK-008 Grok/Praxxis.

**HOLD:** real WordPress/Assembler staging, original full template and shortcode lifecycle, genuine axe and manual assistive testing, NASA media/rights, CSP and real CWV, exact-head CI, independent review and founder release decision. No merge, live WP writes, social publishing, paid services or commerce activation.
