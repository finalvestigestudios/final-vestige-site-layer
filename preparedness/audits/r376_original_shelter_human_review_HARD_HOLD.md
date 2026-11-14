# R376 — Original Shelter source/reading-depth preservation

**DRAFT / HARD HOLD · Source-integrity issue #136 · conversion issue #820 · charter #818**

All nine original Claude/Shelter refs were checked on November 14, 2026: identical to their pinned SHAs, 0 ahead / 0 behind. R376 is based on draft R375 at 0e99d3798ad69641706bc3b2290814b7e26ae74a. It preserves all original manuscripts and source fragments unchanged.

Four Shelter article bodies were fetched from **11 distinct original Git blobs**. Their four metadata objects and the Shelter source-fragment fork were fetched from **11 further distinct Git blobs**. Together they account for the nine original divergent paths. Both new JSON dockets preserve exact original branches/blobs and paragraph/citation differences without choosing or merging a version.

| Article | Original body word counts | Later blocks not identical to first original | Focus for qualified reviewers |
| --- | --- | --- | --- |
| Family communication | 3,026 → 3,463 → 3,563 | 7 / 8 | Child reunification, NCMEC reporting order, state-specific school policy, contact privacy |
| Home fire escape | 3,746 → 4,256 | 5 | High-rise fire escape, stairs vs. sheltering, windows, authority guidance |
| Outage heat/cold/generators | 4,196 → 4,463 → 4,463 | 4 / 4 | Carbon monoxide, generators, extreme-temperature safety, food |
| Shelter or evacuate | 3,437 → 4,089 → 4,193 | 5 / 5 | Chemical emergency ventilation, local evacuation instructions |

A paragraph not matching verbatim is not necessarily lost advice: changes require a qualified comparison for meaning, source support and safety. None of the four article revisions removed an original unique citation ID; new IDs also need review. Higher word counts are NOT proof of completeness or safety.

**Metadata source-use scope:** Family 14→18→20, Fire 10→13, Outage 16→18→19, Shelter/Evacuate 13→14→15, with zero original source-use keys removed among the forks. Each authentic metadata version remains publish=draft and safety_review.state=pending. R375's five semantic source collisions and 17 shared-URL distinct-ID groups remain unresolved; zero original source records were marked human-link-checked.

**Gate and tests:** New read-only Python validator pins the original R374 manifest and both R376 review JSONs by Git blob identity, preserves nine object forks and all metadata safety holds, rejects auto-selection, dropped variants and falsified approval. Always exits code 2. Exactly **105 new** synthetic adversarial tests and **219 combined** isolated R374–R376 tests PASSED, Python compilation PASS. Matching executed code/test Git blobs: fcda2fb7822f0a53ec373b1320f45503eb3c5471 / 754e1a35ed88a496b6dc30e5ab0d4068d2fdaa58.

**Limitations:** Native full checkout blocked by local GitHub DNS, therefore native validator/build/all repository tests and actual 50 WordPress + 50 private preview pairs NOT executed/verified. The real three-JSON Python integration command was NOT executed in the local runner (original authenticated JSON inputs not locally available), although the original Git versions were fetched for the dockets. Hosted CI success not confirmed. Independent QD #157, synthetic fixture #169, dependent fix #2205, homepage #1689 remain separate drafts. Qualified source/medical/emergency/child-privacy/print review NOT GRANTED.

## One high-intent funnel — offer, step, blocker, acceptance, owner

| Offer / funnel step | Blocker and required change | Evidence | Owner |
| --- | --- | --- | --- |
| ONE existing FV-owned rights-cleared Preparedness pack → paid order | Authenticate real payable SKU, delivery, refund terms, merchant receipt | No authenticated paid pack or receipt; HOLD | Founder / Commerce |
| Actually published Grok family-contact asset → free emergency-contact resources | Match original asset ID, hook, date and mobile URL; request independent Praxxis QA only; no creator assignment | Matching asset and UTM UNVERIFIED | Grok / Praxxis |
| Free guide → optional private Family Reunification Card #104 | Qualified print, cutout, accessibility, emergency and child-privacy signoff first | Private, not offered; HARD HOLD | Preparedness / QD |
| Qualified human sessions → confirmed paid orders → realized net | Consent-safe existing attribution, verified orders/refunds/fees, 7/30-day cohorts | No reliable numerator/denominator; NOT COMPUTABLE | Claude analytics / Commerce |

Unposted free CTA candidate: **Start With Trusted Preparedness Resources** to https://finalvestige.com/preparedness/ . No retired water offer. No invented paid CTA. Net revenue per 1,000 qualified human sessions is not computable.

No merge, publication, CMS/navigation write, Grok queue/post, email, analytics deployment, merchant/affiliate activation, spending or false QD PASS.
