# Apollo Experience 2.0 R353 — atomic source-index filter (staging only)

**Scope:** isolated Apollo Evidence Index enhancement. Based on R352; homepage PR #49, Research Desk PR #158, Grok and production remain untouched. No automatic merge, WordPress installation, analytics, paid services, photography use or checkout changes.

## Reproduced defect and change

R352 set `data-fv-apollo-index-ready=1` before creating its five filter buttons. In real Chromium, injected failure on the third button's event registration produced `ready=1`, only **two** controls, and a hidden toolbar. An error while hiding groups could also leave a partial evidence index. R353 builds the controls off-DOM, installs them as one fragment, and marks ready only after success. A creation or filter exception restores **all 13 evidence entries**, removes partial controls and clears the marker. No JS preserves the full index.

## Executable acceptance

`python experience2/apollo-r353/qa/atomic_gate.py` checks real Chromium with PHP-rendered staging markup (320/390/768/1440/1920, no-JS, 400% root text, keyboard/touch filter behavior, visibility and three simulated faults). Extended replay/receipts, native PDF and screenshots are separately archived in the R353 evidence package. Inherited R352, R351 and R350 regression runners also pass locally. None of these is installed WordPress acceptance, a genuine axe-core run, browser CSP verification, screen reader certification, or real production CWV.

## Evidence, rights and conversion scope

Primary historical source: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — no conclusively identified single ignition source. NASA commercial/endorsement policy: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ . Preserve contextual source citations, not speculative map pins; link access does not license photos, logos, identifiable people or commercial use.

One contextual path: Grok Apollo long-form (published asset and UTM unverified) → Atlas/chronology → existing **free** Apollo investigation → optional **separately approved** rights-cleared educator evidence kit. No paid Apollo SKU, checkout, UTM-attributed buyer, confirmed purchase, refunds or net revenue verified. The purchase action stays ON HOLD; no unrelated commerce in historical content. Conversion hypothesis: trustworthy source access improves willingness to investigate a relevant educational product, **not yet tested**.

**Release hold:** real WordPress/Assembler and HTTP/CSP, axe-core/assistive tech, Firefox/WebKit, exact-HEAD hosted CI, media-rights/editorial review, authenticated commerce, founder/QD release authorization. Track #150 with cross-reference to #820 and charter #818.
