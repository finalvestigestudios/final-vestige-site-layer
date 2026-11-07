# R183 — WordPress draft review-label truth correction (HARD HOLD)

**Owner:** Preparedness Archive #136 only. **Commercial coordination:** #820 and business charter #818. **Parent:** R182 exact `589c48811aa79daa7d50a0674da6b3e9d7662796`. This is an isolated **draft / nonrelease** patch: no WordPress, CMS, navigation, public URL, affiliate, analytics, email, social, merchant or spending writes.

## Actual bug found in the authenticated builder

At the R182 parent, `preparedness/tools/build.py` converted metadata `safety_review.state=approved` to **“Approved by…”** inside the rendered Review record, `not-required` to **“Not required for this topic”**, and `render_card()` to `data-verify="reviewed"` when the historically approved/not-required state coincided with an editorial review. This could present unverified legacy judgments as independently cleared in WordPress-ready drafts and on the landing card filter even while the source-review backlog and independent QD remain open. This is a **real representation defect**, not evidence that any underlying guidance is right or wrong.

R178's authenticated roster has 35 original articles: **29 pending, 4 historically not-required, 2 historically approved**. For the 2 approvals, the original metadata itself says the sole founder response was ambiguous and explicitly **did not establish independent source/safety/QD review**. The 4 not-required items still need editorial/source and independent QD. Original `reviewer`, `date` and `scope` metadata are preserved unaltered.

## Narrow correction

1. **Safety Review markup**: render **historical recorded state**, distinguish it from independent fact-check and QD authorization; missing state defaults to pending, unknown states fail closed in text; preserve escaped recorded reviewer and date.
2. **Editorial Review markup**: “Editorially reviewed” now explicitly says that is not independent safety/QD approval.
3. **All draft article headers**: visibly state **Independent safety/source and QD verification pending**, including the 6 historically misleading label cases; preserve existing “Draft: not public” chip.
4. **Landing cards**: `data-verify` is always `pending` until a future explicitly signed independent clearance policy exists; no passive “reviewed” badge from historical metadata.
5. **Tests**: `test_r183_rendered_review_truth.py` provides **56 synthetic fixture regressions** (21 named scenarios + 35 per-slug dynamically named cases) plus **one fail-closed authentic 35-metadata SHA/rendering integration test**. The latter requires the complete trusted checkout and is NOT yet executed. Local analogous synthetic-module tests: **56/56 PASS**; this does **not** prove that the committed suite passed against the original native builder. The committed file has an additional authentic integration method; native suite must run independently.

No original article, safety-review JSON, source register, citation, route, printable, taxonomic label, reading-depth body, URL or source-use interpretation was edited.

## Latest authenticated contributor coordination (2026-11-07 UTC)

All seven Claude cluster branches freshly compared using the GitHub connector, **identical / 0 ahead / 0 behind** against these exact commits:

| Cluster/ref | Pinned current SHA |
|---|---|
| `claude/prep-start-bbfeb8` | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| `claude/prep-food-ccdc55` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| `claude/prep-shelter-5e1e0e` | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| `claude/prep-health-837444` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| `claude/prep-hist-field-9db767` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| `claude/prep-hist-food-b81f19` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| `claude/prep-hist-home-0e0e38` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |

Independently held PR heads: #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (open/draft); #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` (open/draft); its stacked #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` (open/draft). Their shared `test_preparedness.py` modifications still require custody-aware review; none were merged. Current homepage EX2 PR #1351 head `6bad43a36d7473f1061adb25bb9f63e15710f4a7` is separate and untouched. Independent QA remains open.

## Explicit executable acceptance requirements

On a **trusted complete checkout at the exact R183 PR head**, run:

```sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I -m unittest discover -s preparedness/tests -p 'test_r183*.py' -v
```

Then inspect every `preparedness/build/wp/*.html` review record and landing-card `data-verify` value using original 35 metadata identities. Negative-control the two historical approved slugs and four not-required slugs. Validate citation source custody and safety warnings with inherited R161–R182 gates, plus WordPress staged browser/print/privacy accessibility at mobile sizes. **None of these native/WordPress steps has been executed in this runtime**: local `git ls-remote` still errors `Could not resolve host: github.com`. Synthetic test evidence is not a QD pass or medical/food-safety judgment.

## ONE audience → offer funnel → blockade → evidence → owner

| Offer → funnel step | Blocker | Draft change or gated experiment | PASS/FAIL evidence | Owner |
|---|---|---|---|---|
| Existing FV Preparedness pack → payment | No authenticated rights-cleared SKU, exact checkout, delivery, refund policy | Commerce owner verify exact item and order delivery first; **NO buy CTA** | HARD HOLD; merchant order count unknown | Commerce/Claude |
| “What if phones fail at school pickup?” → ungated Household Emergency Plan | Unverified published Grok asset and full independent guide safety review | Proposed `/preparedness/household-emergency-plan/` only after route/safety approvals; record `utm_content=<real_asset_id>` | UNVERIFIED; no claimed published URL | Grok/Praxxis + Preparedness |
| Free guide → optional printable Family Reunification Card | 11 source decisions, sensitive data handling/printing/mobile reviews | Optional free tool, no forced signup or paid gating | HARD HOLD | Preparedness / Site QA |
| Optional paid practical pack → checkout | No existing matching SKU proven purchasable or rights-cleared | Only after merchant acceptance; distinguish physical supplies from original FV digital rights | NOT AUTHORIZED | Commerce/founder |
| Qualified sessions → CTA → confirmed lead/order → realized net | Missing human-session denominator, actual asset identifiers, order/refund/fee reconciliation | Use existing #820 privacy-safe attribution owner, no new script; 7/30-day cohorts | NOT COMPUTABLE | Claude / Analytics / Commerce |

**Draft CTA only, not activated:** “Make a household pickup-and-reunification plan — read the free guide”; optional companion: “Print a family contact card (free; review pending).” Do not place a buyer button until actual SKU, rights, checkout, usable delivery and refunds are independently authenticated. Do not revive the retired water giveaway or change the existing Focus Fieldbook. No paid KPI or revenue uplift is asserted.

TASK-008 Grok/Praxxis handoff and dated document were read via connected Drive; no immutable caregiver asset ID, matching published video URL, authorized channel placement, approved destination or verified paid Preparedness SKU is currently established. This handoff does not overwrite Grok's content queue or Claude's live-site/measurement engineering.

**Release state:** BUILT / synthetic preflight TESTED / native NOT TESTED / DRAFT HARD HOLD. No author advice is asserted medically or food-safety approved. Founder holds explicit release approvals.
