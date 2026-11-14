# Apollo Experience 2.0 R362 — Research Desk documentary crosswalk (DRAFT)

**Scope:** nonproduction, isolated `experience2/apollo-r362/` companion to the existing Research Desk [PR #158](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/158). Historical source and release issue [#150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), conversion source [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). No edits to #158 or frozen homepage #49. It is NOT a WP installation or approved production feature.

## Why it exists

Research Desk PR #158 presents the 102 deliberate flammability-test ignitions within its engineering-response card but its linked "institutional research" destination is the original Apollo 204 Board report. The test count instead comes from [NASA's February 14, 2018 retrospective](https://www.nasa.gov/history/50-years-ago-apollo-flammability-tests/), describing tests in December 1967–February 1968. This is a source classification correction, not a change to the count.

This separate shortcode `[fv_apollo_research_crosswalk_r362]` derives three documented 1967 findings from R345 and one later test summary from R355; every NASA URL passes existing R360 source-identity checks. It labels the record era, evidence limit and commercial-media rights individually. Four native `<details>` source disclosures work without JavaScript; print-only custody preserves both distinct NASA source destinations even when disclosures are closed. It includes **one relevant free editorial continuation CTA**, no paid offer, forms, tracking, NASA media, or geo pins. Source-access rights do **not** equal NASA commercial endorsement or reuse rights. The shortcode's asset enqueue currently covers literal singular post content only; template-part/Assembler lifecycle acceptance remains open.

## Reproduction from repository root

```bash
php -l experience2/apollo-r362/research-crosswalk.php
php experience2/apollo-r362/qa/php_contract.php
python experience2/apollo-r362/qa/browser_gate.py
python experience2/apollo-r362/qa/build_evidence.py
```

The PHP suite uses API stubs, **not installed WordPress**. The Playwright suite uses real local Chromium on PHP-generated markup via `page.set_content`; 320–1920px, keyboard/touch/no-JS, root-text 400%, reduced motion/forced colors and print links. This is not native HTTP/CSP testing, genuine axe-core, NVDA, VoiceOver, or hosted CI. LCP/CLS are *local fixture observations*, not real-user Core Web Vitals.

## Conversion-first gate

**Audience:** educator/history researcher who clicked from an actual Grok Apollo long-form asset. **Route:** approved, attributable Grok video → free NASA provenance crosswalk / Evidence Atlas → free Apollo 1 investigation → only *after independently authenticated seller rights and payable SKU* optional Apollo-classroom evidence kit. Never interrupt the narrative with unrelated commerce. **Hypothesis:** accessible dated source custody improves trust and qualified educator intent; no commercial lift measured.

**Offer → step → blocker → experiment → evidence → owner:** candidate educator kit → verified paid order → no authenticated rights-cleared product/SKU/checkout → keep purchase CTA withheld → BLOCKED → Founder/Claude. Grok film → qualified landing → exact published asset_id/UTM destination unverified → await owner proof → UNKNOWN → Grok/Praxxis. Evidence atlas → free investigation → earlier source classification ambiguous → show dated original vs later source with one CTA → LOCAL PHP/Chromium PASS, not installed WP → Apollo. Confirmed sale → net revenue per 1,000 qualified sessions → sessions, merchant-settled orders, fees/refunds absent → NOT COMPUTABLE → Claude/Commerce.

Grok owns social content/distribution, Praxxis owns external creator QA, Claude owns production website/measurement engineering, founder owns commerce/release. Use native consent-respecting, deduplicated tracking *only after separate approval*: `utm_source=platform`, `utm_medium=organic_social`, `utm_campaign=history_pilot_2026_11`, `utm_content=actual_asset_id`; report 7/30-day cohorts, paid orders, refunds/fees, and realized net revenue per 1,000 **qualified human** visits. Clicking a source or signup ≠ sale.

**Release HARD HOLD:** installed Assembler/WordPress, true axe-core and independent screen readers, WebKit/Firefox, exact-HEAD CI, HTTP/CSP and real-world CWV, human review of source/media and copyright, verified SKU/payment, independent QD/founder approval. No merge, deploy, paid service, WP write, social post, external email or analytics install.
