# Apollo R345 — NASA finding-to-uncertainty EvidencePlate (DRAFT / NOT LIVE)

**Parent:** [Experience 2.0 #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150); commercial coordination [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) and charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Branch based on R344 draft PR #2394 at `806ffcf2b2ae161f545517c7e7ebca554de28550`. Do not modify frozen homepage PR #49 or the Research Desk owner's PR #158.

## Editorial problem and implementation

The R344 printed chronology mislabeled the later NASA institutional history about spacecraft redesign as a **Primary source**. R345 changes the printed source label to **Later institutional source** for the sixth chronology record, and makes source class explicit in the on-screen drawer. No underlying historical date, finding or source URL changed.

A new `evidence-plate.php` adds three documentary-first claims derived from NASA's **1967 Apollo 204 Review Board Finding and Determination 1, 2 and 4**: probable electrical-arc initiator with no conclusively identified source; 16.7 psia pure-oxygen conditions and nearby combustible materials; and inner hatch blocked by cabin pressure before rupture. Each plate prominently states what it **cannot** establish. No image, reconstruction, precise ignition-point claim or NASA branding is embedded. Source links remain on NASA's domain.

The R340 composite shortcode `[fv_apollo_experience_r340]` now renders chronology → three evidence plates → existing accession gallery. Existing **one** free-investigation continuation stays in the chronology; there is no second commercial/editorial CTA. The WordPress prehead style resolver conditionally includes the new scoped CSS only for the composite shortcode. Missing plate PHP fails open to chronology plus gallery; **installed WordPress, reusable dynamic blocks, Assembler, CDN and deployed asset loading remain unverified**.

Original source: https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html (Apollo 204 Review Board Findings, Determinations and Recommendations). For chronology custody: https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/invest.html and https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/chro.html . NASA hosting is not blanket commercial-reuse permission; image accessions remain linked and unembedded pending individual rights checks.

## Reproduce offline

Prerequisites: PHP 7.4+, Python 3, Python Playwright, `fitz`/PyMuPDF, local Chromium (`/usr/bin/chromium` by default). Do not fetch or run a paid service.

```bash
php -l experience2/apollo-r339/chronology-rail.php
php -l experience2/apollo-r340/apollo-accession-gallery.php
php -l experience2/apollo-r345/evidence-plate.php
php experience2/apollo-r345/qa/preflight.php
python experience2/apollo-r345/qa/acceptance.py
```

Local results on 2026-11-13: PHP lint PASS, WordPress *stub* cases 3/3 PASS, actual Playwright Chromium configurations 10/10 PASS at widths 320, 390, 768, 1440 and 1920, including no-JS, keyboard disclosure, touch, reduced motion, forced colors and simulated 400% root text. Native Chromium PDF at 390px, no-JS: **5 original Board source labels, 1 later institutional label, 18 NASA link annotations, 1 free-investigation link, 7 pages**. Two adversarial mutation controls rejected. These are fixture and software regression results, **not** installed WordPress, real screen-reader/axe-core/Firefox/WebKit acceptance or production LCP/CLS. An axe-core package was not locally available. Artifacts and exact source hash receipts are in the reproducible R345 evidence archive.

## Conversion-first mapping and ownership

| Offer | Funnel step | Blocker | Change or hypothesis | Pass/fail evidence | Owner |
|---|---|---|---|---|---|
| Unverified Apollo educator evidence kit | Confirmed paid order | No authenticated payable rights-cleared SKU, checkout or fulfillment | Keep purchase CTA **on hold** | **BLOCKED** | Founder / Claude Commerce |
| Grok long-form Apollo documentary | Qualified landing | Published asset ID and platform-permitted landing URL unknown | Verify creator asset/campaign through existing TASK-008; no posting | **UNKNOWN** | Grok / Praxxis |
| NASA Evidence Atlas | Source proof → free investigation | Print source-class mislabel and absent claim comparison | Three claim/evidence-limit plates, corrected primary/later labels, single editorial CTA | **LOCAL PASS** (not live) | Apollo lane |
| Paid product receipts | Realized net revenue | 7-/30-day qualified sessions, actual paid orders, fees and refunds unavailable | Reconcile native merchant and first-party records, do not infer sales from clicks | **NOT COMPUTABLE** | Claude / Commerce |

Controlled journey: **Grok Apollo long-form → NASA source-led Atlas → existing free Apollo investigation → separately authenticated educational offer**. No unrelated product is injected into the accident narrative, no duplicate measurement script, merchant alteration, WordPress write, social post, email, affiliate activation or spending.

## Release gate

**HARD HOLD.** Owner acceptance of stacked PRs and Research Desk source taxonomy; real installed WordPress/Assembler/CDN; genuine axe-core and independent screen readers; Firefox/WebKit; native HTTP/CSP; hosted exact-HEAD CI; editorial verification and individual image/likeness/branding rights; authentic published creator asset; verified payable product/checkout; founder/QD authorization. Do not merge or deploy on these local results.
