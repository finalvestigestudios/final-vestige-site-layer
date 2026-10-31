# Apollo Experience 2.0 — R25 no-JavaScript NASA printable source custody

**DRAFT / HOLD — October 31, 2026 (PDT).** Parent R24 exact commit `2589caf1beadf7da2f6986f0b04e33ca10eb4ec0`. Source/casefile witness commit `74375657f2cdaac0710f94c6de6c24534ee06858`. Branch `feature/ex2-apollo-r25-print-source-custody-20261031` stacked *only* on R24, not PR #49, main, Research Desk #158 or the lead homepage lane.

## Substantial change

A fully offline, CSS `@media print`, six-entry source-custody transcript is generated from the pinned Apollo 1 source and Research Desk witness. A browser-native Print command produces black-on-white, readable, documentary-vs-photo attribution and limitations with original NASA source URLs printed inline. The transcript explicitly discloses that source-photo dates differ from the historical claim dates. Six individual photo reuse restrictions remain HOLD, catalog disagreement `S67-19766` remains HOLD; distinct NASA `S66-30236` portrait is not substituted. No NASA image bytes embedded, no WordPress nonce/authenticated download URLs, no speculative Atlas pins/edges. No JS, external CSS or third-party service required. Ordinary screen review remains unchanged. The private editorial PHP WordPress adapter bundles two new sealed assets with exact hashes, adds authenticated digest headers; read-only admission rejects changed HTML/CSS and matching-header downgrades.

## Reproducible real QA executed locally

- **159/159 Python/PHP regression/adversarial tests** passed (baseline R24 150). PHP lint passed.
- `qa/browser_print_r25.py`: **7/7 real Chromium Playwright** 320,360,390,768,1024,1440,1920 CSS px with actual generated PHP preview in `page.set_content`. Six print sources, 6/6 source URLs, 0 inline photos, 0 authentication nonces, 0 geographic pins/edges, no horizontal overflow and no page JS exceptions. Browser print CSS foreground `rgb(17,17,17)` and background `rgb(255,255,255)`. JavaScript-disabled print verified at 390. Two screenshots SHA-256:
  * `r25-print-ledger-390.png`: `ff7ca017a4007218b453a2498afae6cf4ee0a9613549fddc6b07fbb194435ddd`
  * `r25-print-ledger-1440.png`: `6a0fc0d45514e8c2f1b35997fd2393536b39c43b223b2252adf86b29869ccae9`
- Existing `qa/browser_exact.py` **7/7 pass**, `qa/ax_tree_r16.py` **7/7 pass**, `qa/browser_catalog_identity_r23.py` **7/7 pass**; historic catalog/source contract intact. R24 touch-target browser re-run was interrupted by a local Playwright transport EPIPE after process timeout; its 150/150 unit coverage and prior successful R24 browser report remain, but **do not claim fresh R25 R24-touch browser pass**.
- Synthetic Chromium lab LCP (ms): 320=460,360=176,390=160,768=176,1024=180,1440=220,1920=180. Observed synthetic CLS=0 at all seven widths. These are *not* production Core Web Vitals, no hosted p75 or INP.
- Deterministic private ZIP built twice: both SHA-256 `471e171d65061d0c2e7fae5ea1af16a18b0aa9e8c21c63efd0e9320acb8d5344`, internal verified preview SHA-256 `ff564e07d4e132bd2860492773e2636901128ca3021f0009f7ca5b2572f7e464`; **23** sealed generated assets, +2 from R24.

## Reproduction

```bash
cd experience2/apollo-wp-bridge/sealed
python -m unittest discover -s qa -p 'test_*.py' -q
php -l fv-ex2-apollo-sealed-template.php
python qa/browser_print_r25.py
python qa/browser_exact.py
python qa/ax_tree_r16.py
python qa/browser_catalog_identity_r23.py
python build_sealed.py --out /tmp/a.zip
python build_sealed.py --out /tmp/b.zip
sha256sum /tmp/{a,b}.zip
python qa/browser_exact.py --require-axe  # strict fail-closed: axe bundle unavailable
```

## Unclosed release gates — DO NOT MERGE OR DEPLOY

No installed authentic isolated WordPress+Assembler/Jetpack staging, no browser-origin HTTP/CSP/cookie checks (Chromium loopback navigation blocked by administrator), no independently pinned axe-core vendor bundle, no Safari/VoiceOver/NVDA/manual accessibility, no actual printer/PDF QA, no hosted LCP/CLS/INP, no confirmed NASA S67-19766 accession for linked photo, no NASA image-reuse clearance, no independent QD / founder visual review, no green hosted GitHub CI on exact head. The source transcript is a documentary ledger, not a full casefile or media license. No external maps/geo inference. No WordPress writes.
