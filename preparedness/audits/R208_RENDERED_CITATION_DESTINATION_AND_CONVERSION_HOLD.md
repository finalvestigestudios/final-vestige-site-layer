# R208 — Citation destination and source-use custody | DRAFT / HARD HOLD

Scope: Preparedness Archive issue #136, coordination #820 and business charter #818. Review-only branch stacked on R207 PR #1523 at 58a08cf4cfdb0a0ad6dab0f0a33a6e0f8c7cd6e8. No original articles, source registers, canonical routes, website, merchant, email, social, analytics or WordPress modifications. No QD or medical-safety approval.

## Gap and engineering change

R207 compared all original 35 authored prose bodies to WordPress drafts/previews and verified citation number order. It did not independently prove that bibliography notes linked to their correct original source URLs, displayed correct source titles, preserved an article-specific reason for citing that source, or that literal and internal body links retained their original destinations.

New independent Python gate: preparedness/tools/r208_citation_destination_gate.py. It requires the frozen R200 manifest, original Git blob identities and R207 parity before authentic audit execution. It checks 35 unique frozen routes and both generated outputs for each article; compares complete authored body-link destination and anchor-text sequences; checks bibliography src-N IDs, one source link per note, exact registered HTTPS URL, title, publisher and article source-use note; rejects protocol-relative or active-script URL schemes, hidden event handlers, forms, embeds, scripts, false approval states, missing rows and duplicate source identities. Review-required exceptions are preserved for missing source-use notes and unchecked links, rather than promoting unknown evidence. No source substitution, safety state or publication authorization is granted.

## Test evidence and limits

Local synthetic Python regression tests: **79/79 PASS**. Of these, 35 mutate authored body link destinations and 35 independently substitute preview citation/source URLs; nine cover complete-slate, missing notes, unverified human link checks, missing inputs, forged approvals and unsafe URLs. Python compilation PASS. Exact tested and committed Git blob identities:
- validator: 0e209927ad5e0eb914879c6b22a451d3979347f0
- tests: 1f08015094605c83d3ad24434e446294b7099866

The original complete repository is **NOT locally executable**. GitHub direct clone/ls-remote failed DNS resolution; native validate, native build, full repository tests and actual 35 rendered draft plus six tool outputs could not run. Missing repository evidence returns INVALID_HARD_HOLD and exit code 3. R208 original-content gate is **NOT AUTHENTICALLY VERIFIED**; synthetic PASS is structural only. No GitHub Actions runner completion or independent QD certificate.

## Contributor coordination (GitHub exact branch heads checked 2026-11-07 PT)

- start: 2122d856fce9f64887c16df3d52e64be9f59a55b
- shelter: 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976
- food: f911ff7a655de8d81535ea86ec3d65a49ee76648
- health: d5ef5bafd68361434dd1cc9209915b8e8a4eaf17
- historic field: 4e5caf812727953aa45e3bda2d382f2c67b6a09c
- historic food: 67e116e536c7410bed30f8f3b1bb8c166f3c223d
- historic home: 7504a5f099594d635e3dd7332a33a2e1346c43a2

Independent safety PR #157 remains draft at 7d1ae6b8ef93d10cfb6810987672360885e9c1aa. Synthetic-fixture PR #169 remains draft at e9cd7766dac59d47ab467d8945269b9146c2aef5 and stacked follow-up #973 at 4d40996a559b0124d74a9bb3bdcd481ad1992aa8. Homepage lead PR #1529 exact head ee89305a33e6e6d0400ec63265341567b713212d and prior #1522 at 5220131734747879879fe77893056065a5aa8f2e. No branch overwritten or merged.

Still held: original Article #7 has two unexplained cdc-find-clean-water citations, Article #20 has one unexplained start-ready-plan citation; seven historical shared-source conflicts include hist-food-nchfp-jerky vs nchfp-jerky. Independent food, medication, electric, water, privacy and QD safety review remains necessary.

## ONE conversion-first audience/offer track — no live CTA

Hypothesis audience: households organizing identity, insurance, finance and contact documents before evacuation. The public free Preparedness Archive gateway is provisional; original Household Emergency Plan and Family Reunification Card remain unpublished. The Legacy Triage $19 PDF previously appeared on a public Payhip listing, but seller rights, actual checkout, successful delivery, refund handling, pricing at payment and verified paid orders remain unverified. Do not advertise as an approved Preparedness product.

Proposed review-only CTA copy: “Organize the documents and contacts your household would need during an evacuation. Start with the free Preparedness Archive. An optional practical records pack may be offered once checkout and delivery have been independently verified.” No email gate for urgent information. TASK-008 and Praxxis handoff reviewed; no real published Preparedness asset_id + post URL + allowed campaign destination authenticated, so attribution remains UNVERIFIED. Grok retains all creative/distribution ownership.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL | OWNER |
|---|---|---|---|---|
| Public free archive → long-form household guide | Source-use and safety review incomplete | Human claim/source adjudication, native build and mobile QA | HOLD | Preparedness / QA |
| Grok topic → archive | Published asset_id, link and rights unknown | TASK-008 destination and UTM check without new posts | UNVERIFIED | Grok / Praxxis |
| Free guide → optional Legacy Triage | Ownership, checkout, delivery, refunds unverified | Approved sandbox or staged purchase/delivery journey | HARD HOLD | Founder / Commerce |
| Guide → optional Reunification Card | Child-data privacy and accessibility untested | Synthetic-data 360/390/768/1440px preview | HARD HOLD | Site QA |
| Attributed visitors → paid orders → realized net | No verified orders, fees, refunds or qualified-human denominator | Reconcile 7- and 30-day cohorts | NOT COMPUTABLE | Commerce / Analytics |

Immediate next executable steps on trusted complete checkout: Python native validate, native build, full test discovery, R207 authored-vs-export check, then R208 destination audit. Inspect all 41 outputs and adjudicate sources and safety independently. No release, publication, CMS, merchant, email, social or analytics writes.