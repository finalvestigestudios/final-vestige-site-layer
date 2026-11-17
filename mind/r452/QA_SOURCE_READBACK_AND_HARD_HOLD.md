# R452 — Exact-source QA, traceability, commercial HARD HOLD

**17 Nov 2026 PT · Mind & Perception · Source-controlled DRAFT ONLY.**

## Actually executed during this sprint

Read-only GitHub connector fetched the nine source-controlled files from branch `mind-r452-faraday-ideomotor-conversion-decision-20261117`. An **independent V8 checker** inspected the exact fetched UTF-8 content and returned **66/66 static source assertions PASS**. Checks covered original 2,700+ word article and sources; three responsive/noindex/no-JavaScript/no-form HTML pages; an exact identical buyer `<main>` body in A and B; disabled native purchase controls; adjacent prospective affiliate disclosure; no clickable seller purchase anchor; existing live free Fieldbook; B-only poster/transcript; original script-free SVG; six non-overlapping VTT cues ending at 42 seconds; a machine-readable 38-claim/20-source ledger; 28/28 closed release gates; and attribution with paid-sale separation.

A second **independent read-only V8 negative-fixture pass** applied **13 separate deliberate, in-memory unsafe modifications** to the exact fetched source strings; all 13 were detected while the corresponding originals passed. Synthetic modifications: removal of native disabled attribute, activation of a Zen12 purchase anchor, removing near-CTA commission disclosure, inserting script, inserting duplicate signup form, inserting tracking pixel, false playable-film claim, autoplay video injection, SVG script, VTT 45-second duration, reopening release gate, fabricating $275 net/1,000, and conflating affiliate_click with a verified sale. These were only mutated **in memory**, never written to GitHub.

The dependency-free `check_r452.mjs` is committed for real Node reproduction on a checked-out branch. **Native Node was NOT executed against these committed files**. There was no container access to the authenticated GitHub branch, so read-only V8 checks are not equivalent to a full native Node run or CI.

## Exact fetched GitHub blob identities (source before QA receipt)

| File | Git blob SHA | UTF-8 chars |
|---|---|---:|
| `THE_TABLE_MOVED_WHO_MOVED_IT.md` | `eca206fb2d3a41b7974d71a8100f336305d1b4c1` | 19620 |
| `ZEN12_A_EVIDENCE_GUIDE.html` | `d120b97d5b707a267f3d9fbf34a14e62fadcc3f4` | 11898 |
| `ZEN12_B_OPTIONAL_FILM_CONCEPT.html` | `e663b51afb369818fa070f68aa3dc2f41055f1e2` | 14102 |
| `ZEN12_42S_POSTER.svg` | `bcaf51c7fc4d8fb92f4a1d67f495429cbd652093` | 2177 |
| `ZEN12_42S_CAPTIONS.vtt` | `af15f14015f9a938b081a226f1d7d7109297103d` | 651 |
| `MIND_HUB_WORDPRESS_SOURCE_ONLY.html` | `3a821229d4bb90620c218e727132cf17c1194e2d` | 6853 |
| `CLAIM_SOURCE_PERMISSION_MATRIX.json` | `2a0b7b206d662d3f343afe511dea8eebaa902501` | 20522 |
| `CONVERSION_AND_CREATOR_ACCEPTANCE.md` | `e25753c90e8e74fee9012dba081d2b129b217cca` | 12150 |
| `check_r452.mjs` | `78309d748995a38dafdd7e6a1ed95e7ae35e7784` | 5477 |

## Primary and product-source evidence actually consulted

- Michael Faraday primary letter, June 28/30 1853 https://epsilon.ac.uk/view/faraday/letters/Faraday2691
- Historical methodology analysis https://link.springer.com/chapter/10.1007/978-3-031-52954-2_6
- Gauchou/Rensink/Fels 2012 https://pubmed.ncbi.nlm.nih.gov/22377138/
- Andersen et al. 2018 online / 2019 issue https://link.springer.com/article/10.1007/s11097-018-9585-8
- Existing Puységur primary-trail archive https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/
- Existing LIVE change blindness and Mesmerism investigations https://finalvestige.com/2026/11/02/change-blindness/ and https://finalvestige.com/2026/11/02/mesmerism/
- Existing free Fieldbook https://finalvestige.com/focus/ and Dispatch https://finalvestige.com/dispatch/
- Inspire3 official catalog https://inspire3.com/ ; Zen12 exact https://zen12.com/about , https://zen12.com/ and **distinct** promotion https://zen12.com/secret/
- Hypnosis Live Total Focus https://hypnosislive.com/mental-skills/total-focus
- Brainwave Shots Focus Shot https://brainwaveshots.com/focus-shot
- Public affiliate portal https://affiliates.inspire3.com/ — NOT publisher approval evidence
- FTC affiliate relationship proximity https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- FTC product-specific health-claim substantiation https://www.ftc.gov/business-guidance/resources/health-products-compliance-guidance

A contemporary source result does not turn nineteenth-century reports into replicated experiments. Seller copies are classified only as **seller claims**; no personalized testimony or asserted product use was introduced.

## Commercial and delivery limitations

**28/28 commercial/production release gates CLOSED.** Named FV Inspire3 program approval, issued link, approved SKU/WEB/EMAIL/SOCIAL rights, referred checkout/returns, independently substantiated named product benefits, paid settlement and exact unique human session denominator **NOT AUTHENTICATED**. Existing free Focus Fieldbook is NOT a payable owned SKU. Connected Gmail search results included consumer promotions and unrelated AvantLink application traffic; no named Inspire3 publisher acceptance was established. A lack of discovered proof must not be represented as definitive proof of nonexistence.

**Not executed:** native Node, GitHub CI, actual Chromium/WebKit mobile views (360,390,768,1440), WCAG 2.2 AA / keyboard / zoom / color contrast by browser, production sanitization, WordPress CMS draft creation, optional video encoding and playback, real Jetpack confirmation, actual authorized merchant checkout, consent-aware analytics telemetry, real users in A/B, independent merchant paid commission verification or refund reconciliation.

**No publication or paid conversion claimed.** Net realized revenue per 1000 qualified-human sessions is **NOT COMPUTABLE** (missing both numerator and denominator), not a verified zero. No active affiliate/checkout URL, email, social posting, WordPress write, site settings, analytics deployment, merge, or spend.

**Ownership boundary:** Mind authored presell and QA hypotheses, founder/commercial approval remains outside this branch; Grok creates/posts social, Praxxis verifies already-published media IDs in TASK-008, Claude performs core site/analytics/Jetpack work, Site QA #126 inspects actual browser, homepage #150/PR #49 and Mind hub #172 remain untouched, Dispatch #174 owns newsletter drafts.

**Reproduction:** checkout branch; `node --test mind/r452/check_r452.mjs`; validate native run and failure fixtures before seeking CI/browser approval. This receipt reports only checks actually executed.