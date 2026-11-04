# Apollo R116 — six-photo NASA custody and commercial rights release hold

**Date:** 2026-11-04 Pacific. **Scope:** Apollo staging-only, additive; no publication, merchant, script, CMS, social, homepage or hosted settings change. **Parent:** #150, coordinated #820 / charter #818. **Base:** R115 draft #933 at `4b87db2f49980b4ae4ac6c0f140f30d58b1831ee`. Do not touch frozen homepage #49, Research Desk #158, or Grok TASK-008.

## Concrete defect / improvement

The actual landing's six-row photographic register linked to NASA but used ambiguous "NASA page 01–06" links and omitted visible credited photographers/producers. Two **2017 retrospective** exhibit pages explicitly credit **NASA/Kim Shiflett**; treating these as unattributed 1967 photographs undermines classroom source custody. A separate provisional crew portrait catalog association was still represented only as an internal assertion, not verified by the cited NASA page.

**BUILT on this staging-only branch:** Replace six generic links with descriptive subjects and credit/producer lines; distinguish retrospective, preparation, training and aftermath photographs from the January 27 event chronology; keep the provisional crew catalog ID explicitly uncertain. Add a six-record machine-readable provenance ledger and a fail-closed stdlib validator with 15 unittest cases covering date/source swaps, credit loss, rights status escalation, invented geo pins/edges, photo embedding and unapproved capture/checkout. Extend real-page Chromium runner to require displayed photographer/producer credits in every 320–1920px JS/no-JS configuration and print for both 2017 records.

## Direct NASA page evidence, rechecked 2026-11-04

| Row | NASA record URL | Cited-page date / metadata | Editorial and rights boundary |
|---|---|---|---|
| 01 | https://www.nasa.gov/image-detail/apollo-1-crew-honored/ | January 1967, day unspecified; NASA image credit; **S67-19766 not printed on cited page** | NASA verifies named crew; proposed catalog assignment UNCONFIRMED, not a commercial-use license |
| 02 | https://www.nasa.gov/image-detail/amf-s67-15717/ | S67-15717; Jan 3, 1967; Producer JSC | Spacecraft preparation, not a fire measurement |
| 03 | https://www.nasa.gov/image-detail/amf-s66-58038/ | S66-58038; Oct 18, 1966; Producer JSC | Pre-fire training, not fire footage |
| 04 | https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0164/ | KSC-20170124-PH_KLS01_0164; Jan 24, 2017; Image Credit NASA/Kim Shiflett | Retrospective memorial/hatch exhibit, not 1967 |
| 05 | https://www.nasa.gov/image-detail/amf-s67-21294/ | S67-21294; Jan 28, 1967; Producer JSC | Aftermath image, cannot establish ignition |
| 06 | https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/ | KSC-20170124-PH_KLS01_0090; Jan 24, 2017; Image Credit NASA/Kim Shiflett | Retrospective redesigned-hatch exhibit, not event footage |

**Direct page identity and dates:** 6/6 link destinations reviewed; cited NASA pages print the listed catalog identifiers for **5/6**, NOT row 01. **Commercial/individual image reuse:** **0/6 independently cleared**. NASA's https://www.nasa.gov/nasa-brand-center/ and https://www.nasa.gov/nasa-brand-center/advertising-guidelines/ do not convert citation links into reusable commercial assets. Assess third-party rights, depicted people/estates, factual credit, identifier/endorsement restrictions per image; independent rights/editorial signoff remains outstanding. This ledger contains no image assets or geographic inference.

## Reproduction and evidence boundary

```sh
python -I experience2/apollo-creator-bridge/qa_r116_nasa_custody.py
python -I -m unittest discover -s experience2/apollo-creator-bridge -p 'test_r116_nasa_custody.py' -v
python -I experience2/apollo-creator-bridge/qa_r113_print.py --html experience2/apollo-creator-bridge/landing-preview.html --out /tmp/apollo-r116-real-page --chromium /usr/bin/chromium --axe /path/to/previously-approved/axe.min.js
```

**TESTED:** Read-only connector/V8 structural checks against GitHub exact blobs: **26/26 PASS** for six NASA links, credits, catalog statuses, dates, legal/citation restrictions, no speculative geo, single free CTA and staged validator tests. This is **not** executable Python, browser or rights clearance.

**NOT TESTED:** 15 Python tests and compilation, actual R116 Chromium/Playwright 14-mode matrix, axe 4 scans, print PDFs/screenshots, six lab LCP/CLS observations, physical keyboard/screen-reader, WordPress.com/Assembler and hosted exact-head CI. Local Python/container returned `redis.exceptions.ResponseError` on 2026-11-04; no approved axe bundle provided in this environment. Do not label any full QA receipt complete.

**LIVE:** No R116 component or QA runner live. A separately published Atlas page 2017 has unresolved approval-state reconciliation and is not proof of R116 deployment.

## Conversion-first decision path

| Priority | OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| P0 | Proposed paid Apollo educator evidence casefile → actual paid order | No independently verified existing deliverable Apollo SKU, merchant checkout, terms, pricing, or commercial media rights | Ask Growth/Claude to inspect seller-origin current inventory and rights/fulfillment/refunds; do not insert unverified button | **BLOCKED; no sale claim** | Claude/Growth/founder |
| P1 | Future approved Grok long-form or Short → source-led Apollo landing → free classroom exercise | Weak NASA link semantics and missing visible credits, new browser acceptance pending | R116 unique official links, real-page credit QA, retain one free CTA | **BUILT, 26/26 source checks; actual browser NOT TESTED** | Apollo owner; Grok distribution; Praxxis external review |
| P2 | Classroom exercise → relevant rights-cleared purchase | No founder-approved fit product, license or checkout | Stage optional contextual offer only after merchant-origin and rights proof; otherwise free source analysis stays primary | **NOT VERIFIED** | Claude/Site QA/founder |
| P3 | Confirmed order minus refunds/fees → net revenue / 1,000 qualified sessions (7/30-day cohorts) | No independently reconciled Apollo asset_id sessions or paid orders | Reuse #820 privacy-safe existing measurement, no duplicate tracker | **NOT COMPUTABLE** | Claude/Growth |

**Conversion hypothesis:** Secondary educators who arrive from an approved source-grounded Apollo investigation may value a teacher-ready casefile, but willingness-to-pay, actual product availability, paid conversion and acquisition attribution are not established. Preserve source proof before any pitch. Only useful next action remains the ungated classroom exercise. Never infer sales from taps, clicks or free content.

## Release gate / coordination

**STAGING HOLD.** Exact-head CI, real-source browser/axe/PDF/LCP/CLS artifacts, WordPress/Assembler, six individual image rights decisions, provisional crew-ID review with #158, independent historical QA, product eligibility, and founder publication approval are required. Do not merge, publish, change WordPress settings, edit frozen #49/homepage branches, alter original #158, modify Grok's queue, email, spend or activate third-party analytics. #150 is engineering log; #820 is conversion charter cross-reference.
