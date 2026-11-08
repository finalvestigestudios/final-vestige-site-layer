# Preparedness R205 — immutable citation-occurrence review receipts (DRAFT / HARD HOLD)

**Scope:** `finalvestigestudios/final-vestige-site-layer` Issue #136 only. Cross-reference conversion #820 and charter #818. Review-only branch stacked **exactly** on R204 PR #1501 at `2a41ec9a35c0285b052f35df6557c78f4a9ef199`. No original article, source register, source-use metadata, taxonomy, historical alias, canonical route, export, WordPress/CMS, navigation, homepage, merchant, analytics, email, social, or spending changes.

## New defensible engineering lift

R204 produced three actionable claim-context workorders but did not assign immutable *per-occurrence receipts* for reviewer notes. Two identical `cdc-find-clean-water` citations in article #7 could be confused, and a free-text review response could be associated with the wrong historical version if the source changed.

R205 adds `tools/r205_occurrence_review_custody.py`: it independently recounts citation tokens across all **35** original owner-branch body byte arrays and compares their offsets to R204's exact three workorders, requiring R202 structural custody and pinning the exact R204 parent Git blob. It verifies closed-world body/metadata identity, all 35 original Git blob hashes and owner SHAs, R204 governance flags, source-register eligible origins, source-record URLs/publishers and unreviewed flags. Expected original census is **1,971** cite occurrences; exceptions remain precisely **two positions** for `homemade-water-filters / cdc-find-clean-water` and **one** for `preparedness-real-households / start-ready-plan`. Anything extra, missing, moved, duplicated, foreign-scope, substituted or incorrectly approved fails **INVALID_HARD_HOLD**.

Every occurrence receives a deterministic SHA-256 receipt of article slug, original body Git OID, true UTF-8 **byte** position, cited source ID and adjacent source bytes digest. Text context is **review-only**, never safety guidance. Human notes can reference only a current receipt, one per occurrence, and a URL identical to its eligible source record. Notes may record `NO_DECISION`, `NEEDS_REVISION` or `NEEDS_SECOND_REVIEW`; they remain **quarantined, unverified draft notes** even if fully populated. Unknown/release/approval fields, duplicate/stale receipt IDs and mismatched URLs are rejected. No reviewer can set QD PASS or publish through this tool. A successful *structural* execution still returns **DRAFT_HARD_HOLD / exit 2**; missing checkout or corruption returns **INVALID_HARD_HOLD / exit 3**.

This explicitly improves traceability and stale-response detection; it does **not** adjudicate any claim, source URL, food/water/medication safety, historical identity collision, or merchant status. Both source explanations and independent review remain outstanding.

## Tests and exact-code evidence

- Locally executed **84/84 Python unittest cases PASS** on synthetic 35-article fixtures, including **35/35 original-body corruption** and **35/35 owner-branch drift** cases, UTF-8 byte-offset tests, duplicate/colliding source IDs, incomplete/unapproved workorders, illegal reviewer approval keys, unrelated source URLs, and determinism. Python compilation PASS.
- Committed source Git blob: `c5b245954bd8df2242d00c2a9635f8f0689610cf`, equal to locally tested `git hash-object`.
- Committed test Git blob: `ce81dd6573203801512690f979c35357e8052be9`, equal to locally executed local test identity.
- Missing local original checkout intentionally yielded exit **3 / INVALID_HARD_HOLD**.
- **NOT EXECUTED:** authentic R205 1,971-citation native input run, full R202/R203/R204 pipeline, `preparedness/tools/validate.py`, `build.py`, original full regression suite, all 41 authentic WordPress exports, real-browser/a11y/print, human official-source QA or independent QD. Local `git ls-remote` failed: `Could not resolve host: github.com`. GitHub connector reads support provenance inspection but are not a complete trusted executable checkout.

Required original checkout commands (do not interpret deliberate nonzero hold exit as approval):

```sh
python -I preparedness/tools/r205_occurrence_review_custody.py --repo . --report /tmp/fv-r205-occurrence-receipts.json
python -I preparedness/tools/r204_citation_adjudication_workorders.py --repo . --report /tmp/fv-r204-workorders.json
python -I preparedness/tools/r203_full_slate_citation_body_gate.py --repo .
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

## Source-adjudication blockers: NOT CLEARED

1. **Article #7 / water:** two original `cdc-find-clean-water` citations have no article-level claim-specific `source_use` descriptions; source registry `human_link_check=false`. Do not infer a verified treatment method or that a heater tank/ice/fuel-contaminated source is safe. Reviewer must inspect full CDC page, exact article paragraphs and any needed corrective copy, then assess independently.
2. **Article #20 / household language:** one `start-ready-plan` citation lacks article-level explanation; source registry flag false. Ready.gov claim and exact semantics require independent authority confirmation.
3. The **seven source-ID origin collisions** (including the two jerky IDs) and later historical evidence remain unadjudicated. Independently qualified food, medication, water, child-data privacy, accessibility and editorial/QD review remain required.
4. No original reading-depth reductions, URL rewrites or content replacements were authored in R205.

## Exact source/ref coordination (2026-11-07 PT)

GitHub compare of each frozen original SHA against its **current branch ref** returned **identical / ahead 0 / behind 0**:

| Claude original cluster | Exact HEAD |
| --- | --- |
| start | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| historical field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| historical food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| historical home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |

Independent QA PR #157 at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` and fixture PR #169 at `e9cd7766dac59d47ab467d8945269b9146c2aef5`, follow-up #973 at `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`, inspected at patch level. #157's power-drill and cold-medication corrections remain essential but unmerged. #169/#973 changes both target `preparedness/tests/test_preparedness.py` and need deliberate reconciliation. Latest homepage lead PR #1507 at `afd41827b2e7a5f1139d0fc03a7ece0016c9d3d7` observed, untouched.

## Conversion mandate — ONE topic and candidate, no speculative launch

Audience: households asking **“Can we find our insurance, identification and family-contact records if evacuation happens tonight?”** Verified currently public provisional free destination: `https://finalvestige.com/preparedness/`; full original Household Emergency Plan is **unpublished and safety-held**, optional free Family Reunification Card is also **unpublished/untested**. No approved on-site paid product. Legacy Triage is **only an unverified candidate**, pending product ownership/rights, approved listing, price, checkout, file delivery, refund and fees. Do not advertise or publish purchase buttons. Existing `/focus/` Fieldbook remains the only authorized sitewide lead magnet; retired water freebies stay retired.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Original emergency plan → free reader | 3 missing citation explanations plus safety and native build | Human official-source claim fit, versioned copy, R203–R205 runs, responsive/no-gate acceptance | **HOLD**, authentic pipeline not executed | Preparedness + independent QA |
| Grok household-records topic → actual public gateway | No verified published matching asset_id/post/rights/destination | Reconcile existing TASK-008 inventory, platform path and UTMs; no Grok queue takeover | **UNVERIFIED** | Grok / Praxxis |
| Guide → optional free Card | Source, privacy, print and keyboard review absent | Real 360/390/768/1440 test with fictitious data, prevent storage/network egress | **HARD HOLD** | QA |
| Free guide → optional Legacy Triage pack | Rights, listing, merchant handoff, returns and receipt unverified | Founder/commerce prove permitted owned SKU and delivery/refund before any CTA | **NO OFFER ACTIVATION** | Founder / Commerce |
| Social asset → qualified sessions → CTA → confirmed lead → merchant-confirmed paid order → net revenue | No trustworthy attributed denominator or merchant-confirmed order/fees/refunds | Use existing privacy-approved instrumentation only; 7/30 day cohorts, tiny-sample warning, refunds netted | **NOT COMPUTABLE**, no paid-conversion claim | Analytics / Commerce |

Draft-only free CTA copy (not for release): **“Read the free household emergency planning guide. Essential guidance stays open—no signup required.”** The canonical *destination for that unpublished guide must not be linked from live social posts*. If approved later, perform mobile, disclosed-intent, source credibility, broken-link and checkout-friction checks before release. No new measurement script, email list, product or public post.

**Final gate: BUILT / 84 SYNTHETIC TESTS / NOT NATIVE-EXECUTED / NOT LIVE / HARD HOLD.** No merge, WordPress/CMS, home, nav, affiliate, merchant, analytics, email, social, external outreach or spending action taken.
