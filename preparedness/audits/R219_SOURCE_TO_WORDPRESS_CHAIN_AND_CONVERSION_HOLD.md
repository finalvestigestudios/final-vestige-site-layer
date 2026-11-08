# R219 — citation-to-WordPress draft chain, exact-source HOLD

**Scope**: Issues #136 / #820 only. **Status**: BUILT; 123/123 isolated synthetic Python tests PASS; DRAFT/HARD HOLD. No original 35-article or 41-output native build, browser, accessibility, QD, medical safety or merchant tests were executed. No publication permission.

## Engineering lift

R218 corrected a visible false publication-approval phrase bypass inside R217, but its module was not automatically invoked by the R215/R216 transport chain. Independent review also flagged that synthetic receipts did not exercise the authentic upstream R214→R215→R216 sequence.

This branch adds a single **read-only fail-closed entry point**, preparedness/tools/r219_source_to_draft_chain.py, invoking existing R215 source-text/citation transport, R216 visibility/bibliography and R217's **R218-corrected** browser-semantics/false-approval guard sequentially. Each stage must return DRAFT_HARD_HOLD with empty structural errors and explicit false release flags. Article identity, original Git blob identity, three R214 unresolved citation spans/claim blocks and SHA-256 of all four article/channel outputs are cross-checked before and after stage execution. The module refuses unreviewed stage code blobs, symlinks, duplicate JSON keys, escaped input paths, spoofed approvals, altered citation receipts, skipped stages, changed channel ordering and stage report identity drift. It performs no filesystem writes: stdout JSON and exit 2 (HOLD) or 3 (INVALID).

Exact inherited source Git blob pins at R218 HEAD:
- R215 r215_wp_claim_transport_gate.py: 1cd0d239dfcf2b91ff70dca33c3b93cd9a3b55c1
- R216 r216_draft_exposure_guard.py: 6918b0ebfd3b73bcf513eb29ab352b4d94ca5060
- R217 repaired in R218 r217_transport_semantics_guard.py: abefe8954e6dcd8f609db4359586120360828acd

Exact new Git blobs after upload:
- R219 integration: 06cb734bc08ef4f28c7cdfd5d2ae1f54824cad2d
- R219 synthetic test suite: dc03184a1719db3c9028ab0dd6e208df2978c498

**Testing**: Python compilation of both byte-identical files PASS; python -m unittest discover: 123/123 PASS. Tests use **mocked inherited R215/216/217 stages** to exercise R219's invocation contract and mutation rejection. Native inherited stages were NOT run together against original article assets; synthetic mock tests must not be conflated with full integration.

## Frozen contributor and independent QA branch identities, 2026-11-08

Seven Claude heads checked against GitHub branch metadata:

| Contributor | Current HEAD |
|---|---|
| claude/prep-start-bbfeb8 | 2122d856fce9f64887c16df3d52e64be9f59a55b |
| claude/prep-food-ccdc55 | f911ff7a655de8d81535ea86ec3d65a49ee76648 |
| claude/prep-health-837444 | d5ef5bafd68361434dd1cc9209915b8e8a4eaf17 |
| claude/prep-shelter-5e1e0e | 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976 |
| claude/prep-hist-home-0e0e38 | 7504a5f099594d635e3dd7332a33a2e1346c43a2 |
| claude/prep-hist-food-b81f19 | 67e116e536c7410bed30f8f3b1bb8c166f3c223d |
| claude/prep-hist-field-9db767 | 4e5caf812727953aa45e3bda2d382f2c67b6a09c |

Independent QA PR #157 HEAD 7d1ae6b8ef93d10cfb6810987672360885e9c1aa, older Start Here base 10f58fed1ba808056813064ca5f9680589db8da1; do not overwrite newer authored safety wording. Food synthetic-fixture PR #169 HEAD e9cd7766dac59d47ab467d8945269b9146c2aef5, follow-up #973 HEAD 4d40996a559b0124d74a9bb3bdcd481ad1992aa8. Separate DRAFT/unmerged. Home lead ownership unchanged.

## Release and source HARD HOLD

Full original Git checkout unavailable to local Python because GitHub DNS resolution fails. Native preparedness/tools/validate.py, build.py, full 36+ original repository tests, complete seven-branch integration, original 35-article reading-depth/canonical-URL parity, and all 41 intended WordPress outputs require an executable trusted checkout. This new supplemental integration guard covers **only** source-exception Articles 7 and 20, not all 35 articles.

Outstanding: two CDC citation occurrences in Article 7 (Homemade Water Filters), one Ready.gov in Article 20 (Preparedness for Real Households), plus seven historical source-ID conflicts. Qualified human claim/source adjudication and medical/food/water safety review remain mandatory. Neither the source review nor publication safety can be inferred from synthetic passes.

## Conversion-first OFFER → FUNNEL → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER

**Audience/topic**: households needing emergency contacts, insurance and important records when a decision-maker is unavailable. **Free**: authentic ungated public Archive https://finalvestige.com/preparedness/. Longer original FV guides and printables in this repository are unpublished, not permitted campaign destinations. **Single provisional paid candidate**: Legacy Triage, publicly listed as a $19 printable PDF at https://payhip.com/b/n1RhV, under seller Vested Wisdom. FV rights, on-brand fit, secure completed-record handling, authorized referral, merchant acceptance and successful fulfillment unverified.

| Offer / step | Blocker | Change or experiment | Pass/fail evidence | Owner |
|---|---|---|---|---|
| Existing Grok post → free archive | Actual prepared-household post, immutable asset_id, link, rights and UTM pair not matched in TASK-008 | Reconcile **existing** posts and permissible destination only; no queue changes | UNVERIFIED | Grok / Praxxis |
| Free Archive → relevant guide | Original article safety/source reviews incomplete | Mobile accessibility, guide/context and official-source navigation review, no email gating | NOT TESTED here | Preparedness / Site QA |
| Free guidance → optional paid pack | Seller rights, buyer fit, privacy and disclosures unknown | Inspect actual contents, merchant permission, no credential collection and non-coercive copy | HARD HOLD | Founder / Commerce |
| Paid CTA → confirmed order | Checkout, delivery and refunds unverified | Founder-authorized transaction and delivered-PDF inspection | NOT TESTED | Commerce |
| Qualified sessions → realized net | No authoritative orders, fees, refunds or human-session attribution | Seven- and thirty-day cohorts; revenue per 1,000 qualified humans with tiny-sample warnings | NOT COMPUTABLE (not zero) | Claude analytics / Commerce |

**Draft on-site CTA, not activated**: “If someone in your household needed to find emergency contacts, insurance details or important records today, would they know where to start? Explore the free Preparedness Archive.” Optional commercial CTA remains disabled until founder approval, rights, privacy and checkout/delivery gates pass. Existing Seven Day Focus Fieldbook remains the free signup offer; retired water freebie must not return.

**Governance**: no CMS/WordPress/navigation/homepage/social/affiliate/email/analytics/merchant/production writes, no merge, spend or release. #136 owns citation/integration safety; #820/#818 own verified commercial economics.
