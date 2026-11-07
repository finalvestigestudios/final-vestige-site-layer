# R203 — 35-article authored-body citation closure (DRAFT / HARD HOLD)

**Governance:** Preparedness source/citation safety Issue #136; revenue coordination #820, charter #818. No merge, publication, WordPress or navigation writes, homepage changes, affiliate/merchant activation, emails, social posts, or spending. Original contributor content and frozen manifests unchanged.

## Authenticated original-source census, November 7, 2026

Independently fetched all **35 authored HTML bodies plus 35 metadata files** from seven immutable Claude contributor commits using authenticated GitHub reads. **70/70 returned blob SHAs matched the frozen R200 roster.** Observed **1,971 citation marker occurrences, 133 internal-link marker occurrences, zero unknown template opcodes and zero internal link targets outside the frozen 35 article slugs.** This is a read-only identity/structure check, NOT proof of claim support, human link review, or safety.

**TWO REAL CITATION-TO-METADATA FAILURES; three occurrence positions:**

| Original article | Unexplained body citation ID | Uses | Underlying record |
| --- | --- | ---: | --- |
| #7 homemade-water-filters | cdc-find-clean-water | 2 | Global CDC record exists; source-use explanation absent from original article metadata. |
| #20 preparedness-real-households | start-ready-plan | 1 | Start-cluster Ready.gov record exists; source-use explanation absent from original article metadata. |

The two records were fetched separately from their registers. Their **human_link_check flags are false**. Source existence does not establish verified claim support. For #7, citations occur beside alternate indoor-water-source and fuel/chemical-contamination discussions. For #20, the citation occurs beside household-language-needs text. An author/qualified reviewer must inspect those exact claims and sources, then produce a **versioned adjudicated source-use explanation**. No silent changes to immutable originals, no invented source equivalence, no unqualified safety declaration.

## R203 engineering

New isolated all-35 Python validator authenticates exact parent R202 Python Git blob and invokes R202 closed-world directory and scoped metadata/source checks. It loads all 35 complete original bodies from owner-branch Git paths and compares byte length/Git object hash to the frozen manifest; requires every citation token to resolve through that article's explicit source-use metadata and only an eligible own-cluster/global source; verifies every internal-link target against frozen canonical article routes; rejects malformed/nested/unrecognized template markers, replaced/extra bodies, broken UTF-8, missing source use, and unsupported publication/QD flags. Deterministic JSON ledger includes source IDs, eligibility/collisions, cite/link ordinals and byte offsets, routes, source SHA and links for independent review. Competing source identities remain **HUMAN_REVIEW_REQUIRED**.

**Testing:** exact locally authored Python and regression files match GitHub stored Git blob IDs: source **c89a9b0fda60b8f3eca0b9d2273161db92e31159**, tests **b6b7f7f060935913c2291afb3da3c212495a2096**. Executed **126/126 Python unittest methods PASS** locally (105 per-article corruptions: citation, broken link and body SHA, plus 21 edge tests); py_compile PASS. Missing-local-repository exit code **3 / INVALID_HARD_HOLD** confirmed.

**Native limitation:** local GitHub DNS resolution failed; full original checkout and complete R202→R203 Git execution, validate.py, build.py, full test discovery and inspection of all 41 WordPress exports remain **NOT EXECUTED**. The authenticated provider-based census above is narrower than those original native tests. If all other gates pass, the three citation-to-source-use gaps should cause **R203 INVALID_HARD_HOLD** on current original inputs. Even successful structural HOLD (exit 2) never means QD PASS or independent medical/food/electrical safety.

Trusted full-checkout command sequence (no production writes):
~~~sh
python -I preparedness/tools/r202_directory_and_source_closure.py --repo . --report /tmp/prep-r202.json
python -I preparedness/tools/r203_full_slate_citation_body_gate.py --repo . --report /tmp/prep-r203.json
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
~~~

## Exact contemporary coordination

Seven current Claude heads freshly matched frozen identities: start 2122d856fce9f64887c16df3d52e64be9f59a55b; shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976; food f911ff7a655de8d81535ea86ec3d65a49ee76648; health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17; hist-field 4e5caf812727953aa45e3bda2d382f2c67b6a09c; hist-food 67e116e536c7410bed30f8f3b1bb8c166f3c223d; hist-home 7504a5f099594d635e3dd7332a33a2e1346c43a2. Independent safety QA draft PR #157 @ 7d1ae6b8ef93d10cfb6810987672360885e9c1aa improves unsafe power-off drills and refrigerated-medicine wording; synthetic fixture draft #169 @ e9cd7766dac59d47ab467d8945269b9146c2aef5 and follow-up #973 @ 4d40996a559b0124d74a9bb3bdcd481ad1992aa8 avoid shared-tree test writes. Their common test_preparedness.py requires conflict-aware reconciliation; none merged. Homepage lead PR #1493 @ df7457a13917e5662b6e41febcf145ba7f765090 untouched. Seven historical duplicate-identity source issues, including jerky alias, remain pending.

## Conversion-first one-path HOLD and draft landing contract

**Intent:** households organizing identity, insurance, financial records and family contacts before evacuation. **Current free destination:** https://finalvestige.com/preparedness/ — publicly accessible official-resource gateway, no forced signup. Original Household Emergency Plan, optional Family Reunification Card and separate WP household-records-map draft #2150 have **not** cleared release. The Focus Fieldbook remains the sole approved site-wide opt-in magnet. No retired water freebie.

**Single potential paid candidate:** existing Legacy Triage, but ownership/rights, actual active listing/price, merchant payment, fulfillment and refunds **UNVERIFIED**. It is NOT a valid offer to link until separately authenticated. Grok/Praxxis TASK-008 handoff checked; no matching published Preparedness asset ID/post URL/approved landing map verified. The confirmed Tunguska social asset is history/meteorite interest, not honest household-records purchase intent. Do not seize Grok production or posting.

| OFFER → STEP | BLOCKER | CHANGE/EXPERIMENT | PASS/FAIL | OWNER |
| --- | --- | --- | --- | --- |
| Legacy Triage → paid | Rights, listing, delivery/refunds unverified | Founder/commerce SKU & terms audit; authorized test checkout and download | HARD HOLD | Commerce/Founder |
| Grok records content → free gateway | No verified published Preparedness asset_id or platform link | Reconcile TASK-008 and exact permitted post/UTM link | NOT VERIFIED | Grok/Praxxis |
| Free gateway → long-form guide | Two absent source-use explanations and separate safety/QD gates | Human adjudication of three citation occurrences, then native 35-article/source gates | FAIL/HOLD | Preparedness+QA |
| Free plan → optional printable | Child privacy, mobile/print/keyboard unmet | Test synthetic data on 360/390/768/1440 widths; offline/focus/privacy safeguards | HARD HOLD | Site QA |
| Paid order → net revenue | No merchant-confirmed orders or qualified-human sessions | Reconcile asset ID and UTMs → qualified sessions → CTA → verified paid order → refunds/fees in 7/30-day cohorts | NOT COMPUTABLE | Commerce/Analytics |

**Unpublished draft CTA:** “Organizing your household emergency records? Start with the free official planning resources. Our independently reviewed household guide and optional printable are still being prepared.” No false availability or urgency, paid link, or new instrumentation. Acceptance checks before any future launch: creator asset intent/URL match, actual 200/canonical destination, sources and safety notices, accessible keyboard/mobile CTA, user consent and transparent disclosures, nonduplicative UTMs, rights-cleared paid SKU checkout/returns/delivery and independently confirmed sales. Clicks, signups and checkout starts are not paid sales.

**Release:** independent source verification; qualified food/medication/electrical review; child privacy, printing and accessibility; full native build/tests; separate QD and founder approval. This PR stays DRAFT / HARD HOLD.
