# Apollo Experience 2.0 — R236 source-action accessibility (staging only)

**NOT LIVE / DRAFT / HOLD.** Based on R235 SHA `9316db161fb6b88c2a0a804d0a931ffdb13526a5`. The homepage PR #49 and Research Desk PR #158 are not modified.

## Correction

Four EvidencePlate records shared the generic visible link texts “Verify at NASA” and “Find this source in the investigation,” making eight destinations ambiguous in assistive-technology link lists. The builder supplies distinct accessible names for the Review Board report versus NASA photographs S66-58038, S67-15717 and S67-21294. All original URLs, visible captions, ARIA evidence-limit descriptions, SourceDrawer behavior, one free investigation CTA and chronology remain unchanged. No image, map pin, speculative narrative, commercial CTA or analytics is added.

## Exact pinned reproducibility

The verified R235 parent manifest must be SHA-256 `eccfee83d2856185f216345c58ad83fb85224da41047de7b6b2d6fbefd526082`; its index SHA-256 `e95101467cd278a13cf8a4959a29ae17260577dab2ed4d3f4f9910423795f4d9`. Do not bypass pin checks. Generate the R235 parent with the previous committed script and its approved fixture, or use the independently SHA-verified previous bundle.

```bash
python experience2/apollo-r236/qa/r236_patch.py /path/to/generated-r235 /tmp/generated-r236
python experience2/apollo-r236/qa/r236_mutations.py /tmp/generated-r236/templates/atlas-fragment.html
python experience2/apollo-r236/qa/r236_acceptance.py --out /tmp/generated-r236 --qa /tmp/r236-qa
php -l /tmp/generated-r236/fv-ex2-apollo-r224.php
```

Requires Python, BeautifulSoup, Playwright, Chromium at /usr/bin/chromium, PHP CLI. Both output paths must be new.

## Locally verified

Two independent full-fixture builds yielded template SHA-256 `50dbe79bbb223762a01614e52fd7a5098784a7d2bd04ceadd2ac69cdf43d3bb6`; PHP `81735082bb6dc8490d663c4f110d48e8d884cbe2c87a6f76581aa364cd935317`; manifest `f9169870eb3c02415feaf70eed9bbefdca5b194c6ddb27a92a0b80102ef1ce95`. Browser QA: 10 Chromium contexts per execution (320–1920px, JS/no-JS), native keyboard/touch disclosures, native accessibility tree and role/name checks, 10/10 matching screenshots, no overflow or unexpected requests. Both deterministic receipts SHA-256 `7c1d7d547ab3d95ae0bec0286ccb8a11e16f63cc1bfdad95df5ce8314f70a19c`. Six adversarial source-URI/label/limit/anchor corruptions rejected twice. PHP syntax and normal/printed/late-fallback shim tests PASS.

## No release

Genuine axe-core and human screen-reader testing **NOT EXECUTED**; installed WordPress/Assembler, browser HTTP fixture navigation, actual browser UI zoom, hosted exact-head CI, field LCP/CLS, independent source/rights review, inherited R198 ancestry resolution, and founder approval **HOLD**. This is neither WCAG certification nor production CWV evidence.

**Commercial path:** verified Grok documentary asset (not yet supplied) → NASA-backed Evidence Atlas → free original Apollo investigation. Paid educational dossier is a proposed, not purchasable, rights-cleared offer. No paid conversions, authenticated qualified human sessions or net revenue are verified; net revenue / 1000 qualified humans NOT COMPUTABLE. Existing ownership remains Grok distribution, Praxxis creator QA, Claude production and founder commercial/release approval. See #150, #820, #818.