# Apollo Experience 2.0 — R193: distinct native disclosure controls (staging only)

**Issue #150; commercial measurement coordination #820; charter #818.** Isolated additive child of R192 PR #1426 (SHA `34592aa346a0798acf579213bd2a0b2b8da527b1`). Do not edit homepage PR #49, Research Desk PR #158, WordPress, social publishing, merchant or affiliate configuration. **NO production merge or activation approval.**

## Reproduced problem and fix

In R191/R192, the four EvidencePlate `<summary>` controls were identically named **"Examine source custody"**, and the four gallery SourceDrawer controls were identically named **"Open source details"**. This is visually workable but makes a screen-reader list of eight disclosures ambiguous. R193 creates eight uniquely contextual, readable names tied to oxygen conditions, ignition uncertainty, inward-opening hatch, cabin pressure and the four NASA archival sources. The native HTML `<details>` elements remain interactive with no JavaScript, no new JS/CSS, no fabricated coordinates, and no change to the underlying technical claims, URLs, photo roles, provenance warnings or single free-investigation CTA.

The R193 generator reconstructs the candidate WordPress PHP adapter and assets from R191's SHA-pinned source, re-pins the resulting HTML integrity digest, and versions its PHP function/script/style names. The original source generation chain must be present. It **does not** modify any ancestor files. Generated files are intentionally build artifacts, as with R191/R192; do not activate the R191 and R193 plugins together.

## Build and independent local QA

From checkout containing the R192 ancestry:

```bash
python experience2/apollo-r193/build_r193.py
php -l experience2/apollo-r193/dist/fv-ex2-apollo-r193.php
python experience2/apollo-r193/qa/gate_r193.py /tmp/apollo-r193-proof
```

Requires local Python Playwright, Chromium `/usr/bin/chromium`, and PHP. The QA tool checks PHP-rendered content through a WordPress-function shim and then exercises real Chromium. It verifies **nine contexts spanning 320–1920px**, no-JS, forced-colors, reduced-motion, eight unique source controls using the Chromium accessibility tree, keyboard-open/pointer-close native disclosure behavior, target IDs, horizontal overflow and screenshot hashes. It is an **offline DOM fixture**, not an installed WordPress, real HTTP/CDN, screen reader or genuine axe-core test. Browser network navigation is blocked in the current isolated environment.

### Local evidence, November 7, 2026

- Generator output HTML SHA-256: `d1e11f5e4e2d36f9f8b47c8fe4e9ebedb0707ddc6e59d948016a39c00468b1a0`.
- PHP output SHA-256: `28f0600e29fef3320a320e4153cee2c946215a23863b86be2dbc16ed3e1ac301`.
- Original R191 HTML: `100e6059cc891ba404125ecadd71a877566f79012b16a8e36889bacffb474453`.
- CSS and optional JS are copied unmodified: `0cb74e30baf0bb2f9f8086c6a714388dc04f277ede52c1b2939fa8c017caae80` and `eeab075280948b771eecd4cb13cc04ed946ffc34fc059bd6ac0d16ba555e446b`.
- **Two local runs:** nine contexts each; 9/9 reproducible screenshot SHA-256 digests; 8/8 distinct disclosure names; all native disclosure keyboard/pointer assertions passed; no horizontal overflow or page errors in the fixture; PHP syntax PASS.
- **Not executed:** genuine axe-core, installed Gutenberg/Assembler/CSP/CDN test, exact-head GitHub CI, real-user LCP/CLS/INP, actual social-to-site attribution, merchant-confirmed purchases.
- Parent R191 complete regression could not be rerun from the archived R192 ZIP alone because its R190 generator ancestry is not included in that archive. The repository branch contains the earlier generators; do not claim an exact-head full ancestry test until independently executed from checkout.

## Source custody and rights

NASA Review Board: https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/ — board found no conclusively identified ignition source.
NASA S67-21294: https://www.nasa.gov/image-detail/amf-s67-21294/ — aftermath photograph, not an image of ignition.
NASA advertising restrictions: https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ — citation ≠ commercial likeness or implied-endorsement approval.
No NASA image file is reproduced; original technical source and print-source index are preserved.

## Commercial mandate and release gates

**Audience:** historically curious viewers/educators from a Grok-owned Apollo long-form/Shorts concept; actual asset ID, publication, and UTMs remain unverified in TASK-008. **One Atlas next action:** *Read original investigation*; no unrelated merchant link. **Potential product:** original classroom-ready Apollo evidence dossier, still **not verified as sellable**, so do not display a purchase CTA. The conversion hypothesis is that credible source custody increases qualified reader trust before an independently validated rights-cleared educator purchase pathway. Revenue per 1,000 qualified human sessions is **not computable** without verified campaign visits and net paid orders.

**Hold before release:** Claude/QA must run installed WordPress with Gutenberg + theme, native axe-core and assistive tech, real asset/CSP/CDN/caching and responsive Core Web Vitals on exact head; independent QA and founder review must approve; commerce owner must independently verify relevant SKU, seller rights, checkout, refunds/fees and net paid orders. Do not infer sales from clicks, visits, leads or mock tests.
