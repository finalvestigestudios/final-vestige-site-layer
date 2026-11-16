# R412 — Original manuscript depth + reader-discernible citation escrow

**DRAFT / HARD HOLD** · [Preparedness Issue #136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136) · Conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) · Business [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818).

## Exact starting point, custody and findings

Stacked on R411 draft PR #2732 HEAD `9671eefe98c9d991372ccc17ee5e580fc718e425`; **additive Preparedness-only files**. R397 original graph Git blob `86d22a1d504c93db7689b914e2202a7845b648e2`: 35 original article identities, 77 object paths, 203 source IDs, 280 occurrences, 17 exact shared-URL groups requiring distinct-source review, five source-scope conflicts, nine unselected manuscript forks. No source is deduplicated or manuscript chosen.

Two concrete *synthetic* R411 structural gaps were reproduced:

1. If both WordPress and private-preview HTML lost the same original paragraphs, R411 compared them to each other and could report structural `integrity_ok=true`. R412 demands each original candidate source Git blob as **private original bytes** and compares approximate lexical reading depth and five-word phrase overlap. It flags <90% raw original candidate word count or <80% five-word overlap as **requiring human adjudication**—never as automatic selection or semantic proof. Every original candidate, including forks, must be present and hash verified.
2. R411 accepted source-ID-and-URL-correct links with **empty visible anchor text**. R412 rejects blank, short or generic source labels, keyboard-excluded/ARIA-disabled citations, misleading role/button citations, download attributes and new-window links without both `noopener` and `noreferrer`. Paired WordPress/private exports must preserve the same visible source label, source ID and exact URL.

R412 composes R409/R410/R411 in order and **always returns `release_state=DRAFT_HARD_HOLD`, `eligible=false`, `publication_approved=false`, CLI exit 2**. It never issues QD PASS. A positive synthetic structural test does not establish content safety, accuracy, rights, original reading-depth acceptance or verified sales.

## Execution evidence

**Local exact-code suite:** 80 new R412 tests PASS; 232 inherited R409–R411 tests PASS; **312/312 assembled Python PASS**; Python `compileall` PASS. Remote R412 source and test blobs must match these locally executed Git hashes before exact-commit parity is claimed:
- `preparedness/tools/r412_baseline_citation_gate.py`: `652ed017d4573327b12d62119e59c5c0681d43fb`
- `preparedness/tests/test_r412_baseline_citation_gate.py`: `cf4230c3cf3f1d0f88a6cddec01d7982ea7c23cc`

Synthetic fixtures exercise all 35 article identities, 203 IDs, 17 same-URL review groups, a second unselected source candidate, private symlink/hardlink rejection and the two before/after bypasses. **Not tested:** authentic native full validate/build, genuine 35 WordPress/preview export pairs, private original manuscript source bytes, browser computed CSS/accessibility, claim-support adjudication or independent QD. The original-content token/shingle comparison is only a **review cue**: historical HTML/Markdown/JSON containers and legitimate editorial changes require human interpretation. Never upload private source manuscripts; the CLI expects them at `<PRIVATE_ROOT>/<slug>/<git-blob-sha>.txt`, verifies actual Git blob bytes and refuses absent originals.

## Current independent SHA checks, 2026-11-16 PT

All original **nine** Claude/Shelter refs match R397 pins: 0 ahead/behind. QA draft [#157](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/157) `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic fixture draft [#169](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/169) `e9cd7766dac59d47ab467d8945269b9146c2aef5`; dependent correction [#2205](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2205) `bbcf1859768624c611df4abadc564c18247cf32a`. Home lead #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0` left untouched. Editorial E405's Article #11 jerky-source NCHFP/CDC/FSIS applicability conflict remains **human food-safety HOLD**.

## ONE conversion-first funnel: offer → step → blocker → change → evidence → owner

| Offer | Step | Blocker | Draft change / acceptance test | Evidence / owner |
| --- | --- | --- | --- | --- |
| ONE FV-owned, rights-cleared Preparedness digital pack (SKU not independently authenticated) | Free guide → optional paid resource → verified order | No confirmed FV seller ownership, live payable SKU, delivery, rights/refunds/fees or safety approval | **No paid CTA until founder/commerce supply actual offer and test real checkout + fulfillment, disclosures and refund policy** | HOLD; Founder/Commerce |
| Free family emergency-contact/reunification references at `https://finalvestige.com/preparedness/` | On-topic **already-published** Grok asset → existing free agency-reference landing | Matching immutable asset_id, exact social hook/rights, permitted mobile URL and UTM not authenticated | Unpublished candidate CTA “Start With Trusted Preparedness Resources”; signed-out 360/390px route checks. Never alter Grok's queue | UNVERIFIED; Grok/Praxxis |
| Optional Tool #104 private printable | Free guide → optional practical tool | Child privacy/emergency specificity/accessible printing no QD | Hold/private until independent review; core official advice remains ungated/free | HARD HOLD; Preparedness/QD |
| Paid commercial conversion and net revenue | Qualified-human sessions by asset_id/UTM → CTA → confirmed lead if any → merchant-confirmed paid order → refunds/fees | No purchase receipts, net values or reliable denominator | Use existing consented Claude-owned first-party measurement only; 7/30-day cohorts, tiny-sample flags | NOT COMPUTABLE; Claude/Commerce |

Primary KPI is **realized net revenue per 1,000 qualified human sessions**, not views, clicks, checkout starts, emails or affiliate outbound visits represented as paid orders.

**No merge, WordPress/CMS/navigation writes, publishing, sales/affiliate activation, creator work, social posts, emails, duplicated analytics, paid services or spending.** Founder controls release/commerce; Grok owns production/distribution, Praxxis independent social QA, Claude core site/analytics. TASK-008 handoff is research-only.
