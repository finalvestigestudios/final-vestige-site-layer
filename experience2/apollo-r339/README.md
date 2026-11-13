# Apollo R339 — Research Desk NASA photo custody and chronological precision

**2026-11-13 · DRAFT / NOT INSTALLED / NOT LIVE.** Independent Apollo/Research Desk lane for [Issue #150](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/150), cross-referenced to conversion priority [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Derived from the isolated R338 Research Desk multinstance branch, **not** homepage PR #49. No WordPress, merchant, social, analytics or content writes.

## Problem reproduced in actual checked-in source

The Research Desk's original six contextual photographs were labeled generically with photo IDs, creating three specific provenance risks: (1) card 01 asserted the exact accession `S67-19766` even though its linked NASA *Apollo 1 Crew Honored* page does not display this catalogue ID; (2) 1966 astronaut altitude training could be confused with the 1967 instrument chronology; (3) 2017 tribute/exhibit photography could be misread as contemporaneous 1967 accident/hardware evidence. An archival URL does not itself prove an accident mechanism or grant commercial reuse permission.

## Implemented correction

The six historical cards retain documentary evidence as the FIRST source link and link-only photography as SECONDARY context. The visible metadata and link labels now distinguish: a January 1967 crew image with **no asserted catalogue ID** on the linked NASA page; January 3, 1967 spacecraft preparations (S67-15717); October 18, 1966 altitude-chamber training (S66-58038); January 24, 2017 memorial mockup (KSC-20170124-PH_KLS01_0164); January 28, 1967 post-fire cabin interior (S67-21294); and January 24, 2017 redesigned-hatch memorial display (KSC-20170124-PH_KLS01_0090). The NASA Review Board's probable electrical initiator remains distinct from a proven ignition source.

**Authoritative/identification sources:**
- [NASA Apollo 204 Review Board](https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/): primary findings and limitations.
- [NASA Apollo 1 Crew Honored photo page](https://www.nasa.gov/image-detail/apollo-1-crew-honored/): early-1967 crew photograph; specific S67-19766 catalogue number not stated on the linked page.
- [NASA S67-15717](https://www.nasa.gov/image-detail/amf-s67-15717/): January 3, 1967 spacecraft movement/preparation.
- [NASA S66-58038](https://www.nasa.gov/image-detail/amf-s66-58038/): October 18, 1966 altitude-chamber training.
- [KSC-20170124-PH_KLS01_0164 source identification](https://images.nasa.gov/details/KSC-20170124-PH_KLS01_0164): January 2017 tribute mockup; direct NASA archive navigation not verified in this runner; cross-checked in [Wikimedia Commons record with NASA catalogue attribution](https://commons.wikimedia.org/wiki/File:Apollo_1_Tribute_spacecraft_mockup.JPG). Do not treat this as a 1967 photograph.
- [NASA S67-21294](https://www.nasa.gov/image-detail/amf-s67-21294/): January 28, 1967 post-fire interior.
- [NASA KSC-20170124-PH_KLS01_0090](https://www.nasa.gov/image-detail/amf-ksc-20170124-ph_kls01_0090/): January 24, 2017 exhibit showing the redesigned hatch.
- [NASA media/brand restrictions](https://www.nasa.gov/nasa-brand-center/): no NASA endorsement, photo-identity/right-of-publicity/third-party checks before commercial reuse. Photo links are not a licence determination.

## Reproducibility and executed checks

Run `python experience2/apollo-r339/qa/provenance_contract.py`: 6 source pairs and 6 adversarial mutations must pass. R338's inherited browser gate is re-pinned to the R339 ledger blob (`e33395a4d9a16164e9867e2a38c7eb95b3520cd8`). Independent local Chromium run against the EXACT PHP, CSS, JS and modified template source passed 15 scenarios, 320–1920px, JS enabled/disabled, search isolation across two shortcode renders, keyboard `details`, source hitboxes >=44px, forced colors, reduced motion, a 320px/64px-root stress scenario, and 6+6 NASA source pairs per instance. Five viewport screenshots, a source-hash receipt and checksums are provided separately. Fixture LCP 84–196ms and observed CLS 0 in seven JS configurations; **not field CWV**. These observations cannot assert axe-core or an installed WordPress pass.

## Conversion-first decision

**Audience:** Grok Apollo 1 long-form viewers seeking a trustworthy investigation. **Path:** documentary link (publication/asset ID unverified) → NASA primary-source Research Desk → exactly one free Apollo investigation CTA → separately approved, verified rights-cleared Apollo educational product, if one is actually available. No unverified payment or affiliate link is embedded. Hypothesis: correcting chronology and documentary/photograph custody reduces the trust break before the editorial CTA. **Measurement:** qualified-human session by asset ID → landing → editorial CTA → consented confirmed lead if applicable → independently confirmed paid order → refunds/fees → realized net revenue per 1,000 qualified human sessions. No observed sale or attribution can be claimed.

**OFFER → STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER**

1. Apollo educator resource → paid checkout → no authenticated payable, rights-cleared SKU → keep commerce link blocked pending merchant verification → **HOLD**, Founder/Claude.
2. Grok long-form → Research Desk → no verified immutable published video asset/UTM → request TASK-008 handoff without modifying Grok's production queue → **UNVERIFIED**, Grok/Praxxis.
3. NASA Research Desk → free investigation → mistaken photo-era/accession implications → clarify six source captions and retain single CTA → **LOCAL PASS**, Apollo lane.
4. Paid conversions → net revenue → no reconciled human sessions/orders/refunds/fees → no revenue claim; reconcile 7/30-day cohorts in owner analytics lane → **NOT COMPUTABLE**, Claude/Commerce.

## Release gates

**HARD HOLD:** genuine axe-core not run; independent screen-reader, WebKit/Firefox and installed WordPress/Assembler/CDN acceptance not run; browser-native HTTP/CSP and production LCP/CLS unverified; hosted exact-HEAD CI not yet independently green; photo/media rights and historic editorial final signoff pending; verified Grok asset ID and payable product absent; founder approval required before deployment. No new geographic pins, speculative relationships, external photo embedding, analytics scripts, emails, affiliate activation, publication, or spending.
