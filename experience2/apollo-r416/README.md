# Apollo Experience 2.0 — R416 integrated custody, accessibility and conversion acceptance

**BUILT + LOCAL TESTED. No WordPress installation, merge, publish, product activation or live claims. Production HARD HOLD.**

R416 is a read-only **acceptance/offer-readiness gate**, not another decorative website page, analytics script or new purchase button. It audits the **actual R415 PHP-rendered integrated chronology + six-record gallery** against six exact archive destinations, the three documented NASA chronology publications, meaning-preserving ignition/test limitations, IDs/fragments, no fabricated coordinates, native no-JS disclosures and exactly one existing free Apollo investigation CTA per instance. It rejects unauthorized scripts/media/forms, injected buy buttons, lookalike NASA links and off-domain routes. It does not change R415, R414, R411, PR #158, homepage PR #49 or Grok/Praxxis TASK-008.

## Authenticated source custody and rights
- Research Desk source of record: original [PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158), template Git blob `403d128c57b9bc82dac7c619651689070edef86c`.
- R411 source catalog Git blob `efd0cc3841ed6fd2998806be7ebe9055fc7f2fc1`.
- R414 gallery code blob `41540268014b4a792b2e52685ebe8c471a35c3da`; CSS blob `a5eeb96aeebe5569db4cef0d3d0a0e05fdf99c5f`.
- R415 CSS blob `8861287fa3e565963454f7a524a60cafe23bd797`, R415 source [draft PR #2790](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2790) exact HEAD `ca7f9323934ef957a19ab412a474953bbc72205c`.
- NASA [Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/): did not conclusively determine initiating ignition source. NASA's [102 *later* deliberate flammability tests](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/) took place Dec 1967–Feb 1968; [mixed-gas launch decision](https://www.nasa.gov/history/50th-anniversary-of-nasa-deciding-on-a-mixed-gas-atmosphere-for-apollo-a-direct-result-of-the-apollo-fire/) was announced Mar 14 1968. None identifies the original initiating fault.
- NASA [media-use guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/) and [advertising / no-endorsement rules](https://www.nasa.gov/nasa-brand-center/advertising-guidelines/) require separate asset/personality/brand clearance for any future commercial offering. The R415/R416 components reproduce **no NASA imagery, crew portraits or insignia**. Source archive hyperlinks are not image-redistribution licenses.

## How to reproduce (repo checkout containing inherited R411, R414 and R415)

```sh
php experience2/apollo-r415/qa/test_php.php
python experience2/apollo-r415/qa/test_browser.py
python experience2/apollo-r416/qa/test_gate.py
python experience2/apollo-r416/qa/journey_acceptance.py
python experience2/apollo-r416/qa/test_browser.py
python experience2/apollo-r416/qa/package_evidence.py
```

Requires PHP CLI, Python 3.10+, BeautifulSoup4, Playwright, system Chromium at `/usr/bin/chromium`. Browser harness uses **actual PHP-generated markup injected with `page.set_content`**; Chrome DevTools Accessibility Tree is observed but **is not axe-core**, and the fixture is not installed WordPress or an actual HTTP navigation. It emits explicit `NOT_EXECUTED`/`NOT_MEASURED` for genuine axe-core, navigated LCP and CLS, real-user 75th-percentile CWV and WP/Assembler acceptance. There is no invented LCP or CLS result. Screenshots are reproducible viewport contexts, not production render screenshots. The byte-reproducible ZIP includes source, tests, JSON gates and captures.

## Founder conversion hierarchy — OFFER → STEP → BLOCKER → CHANGE → PASS/FAIL → OWNER

1. **Proposed *original* classroom evidence dossier** → merchant-confirmed paid order → no authenticated rights-cleared payable FV-owned SKU, price, actual purchase/fulfillment or refund policy → `review_commerce` rejects missing proofs and *never* treats self-declared receipts as sales → **HOLD** → Founder/Claude commerce.
2. **A genuinely already-posted Grok Apollo long-form** → campaign-tagged qualified-human sessions → no independently verified post URL, immutable asset ID, asset-rights review, permitted mobile link or human-session data → `review_campaign` checks UTM consistency but requires independent post/analytics proof; syntactically valid URLs are **not** attributed sessions → **HOLD** → Grok creator/post, Praxxis external QA, Claude analytics.
3. **Source-led R415 journey** → existing [free Apollo investigation](https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/) → source/CTA and responsive/browser-contract proof locally **PASS**, real installation and genuine axe/LCP/CLS **HOLD** → independent QD + Apollo QA.
4. **Independently confirmed actual purchases** → 7/30-day net revenue/1,000 *qualified human* sessions → no merchant settlements, fees/refunds, qualified denominator or validated attribution → KPI **NOT COMPUTABLE** (no fallback zero sales claim) → Founder/Claude.

Potential educator product must be **original pedagogy**, not repackaged NASA publications. Audience is educators/history research users drawn to the Apollo 1 evidence question, not general site traffic. Free historical source access is retained. Do not add paid links inside historical records. No new forms, visitor scripts, analytics vendors, cookie collection, social posts, emails or spending.

## Release governance

`release_gate` **always remains HARD_HOLD for this synthetic build** even when local static/browser checks pass or a fixture supplies fabricated approval fields. External qualified editorial/QD and source/rights review, installed staging with real Chromium navigation and WCAG/axe, genuine HTTPS LCP/CLS, and founder authorization cannot be self-certified in test data. Coordinated under [Apollo Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), [conversion Issue #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) and [business charter #818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). No homepage branch or protected PRs touched. No release is approved.
