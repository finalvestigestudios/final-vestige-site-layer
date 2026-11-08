# Apollo Evidence Atlas — R208 retrospective-date source custody (staging only)

**Source-controlled builder:** `build_r208.py`. **Native PHP/Chromium regression:** `qa/gate_r208.py`.

## Correction

R207 grouped the January 27, 1967 Apollo 1 fire and the later Apollo 204 Review Board findings under a single date, while suggesting the dates identify the actual evidence records. That could mislead a visitor into treating the retrospective technical report as an accident-day source.

R208 distinguishes: (a) the **27 January 1967 accident date**, (b) the **Board report completed in April 1967** (NASA states month precision), and (c) NASA's separate dated photograph records. Source verification is native HTML with a link to NASA's report-timing page; it works without JavaScript. The four-record archival custody view, eight source disclosures, four chronology entries, source limitations, gallery and **single free investigation CTA** remain. No new map pin, purchase, tracking, media asset or implied NASA endorsement.

NASA primary report: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/
NASA report timing: https://www.nasa.gov/apollo-1-resources/
NASA photograph catalog: https://www.nasa.gov/gallery/apollo-1/
NASA advertising/likeness rules: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/

## Reproduce in a source-available checkout

The builder deliberately requires the sibling `experience2/apollo-r206/dist` fixture, with all its files matching the SHA-256 hashes in its manifest. This fixture is **not** automatically obtained from a clean Git checkout and the inherited R198 builder source discrepancy is still unresolved. Do not claim complete canonical ancestry.

```sh
python3 experience2/apollo-r208/build_r208.py
php -l experience2/apollo-r208/dist/fv-ex2-apollo-r208.php
python3 experience2/apollo-r208/qa/gate_r208.py /tmp/apollo-r208-qa
```

The QA script tests actual PHP-rendered content and real Chromium at 320–1920px (keyboard, touch, no-JS, reduced-motion, forced-colors, simulated CSS zoom, print, links and source-limit associations), checks SHA-256 file custody, and rejects deliberate date/source/sales/anchor mutations. Chromium **uses set_content HTML fixtures** because network/browser navigation is administrator-blocked here. HTTP is separately checked with urllib. Neither a fixture LCP/CLS number nor the absence of browser errors establishes production performance.

### Hard release gates

Genuine axe-core, NVDA/VoiceOver, installed WordPress/Assembler, actual browser zoom, CSP/CDN, hosted CI exact head, full R198-R208 canonical source reconstruction, independent QD and founder approval remain **open**. No new WordPress write, merge, deployment, tracking script, social post, affiliate activation or spending is authorized.

**Conversion contract:** Grok-owned long-form Apollo audience → evidence atlas → existing free investigation CTA → potential future educator dossier *only after* its rights, SKU, merchant checkout, fulfillment and attribution are independently verified. Do not call a CTA click or affiliate outbound link a paid sale. Seven/30-day confirmed orders, refunds/fees and realized net revenue per 1,000 qualified human sessions are not currently computable. Grok owns media; Praxxis owns creator QA; Claude owns core production engineering; the founder retains release approval. See Issues #150, #820, #818. Frozen homepage PR #49 and Research Desk PR #158 were not edited.
