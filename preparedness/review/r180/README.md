# R180 — Joined human source-adjudication docket (DRAFT / HARD HOLD)

**Owner:** Preparedness Issue #136; commercial coordination #820 / charter #818. Stacked on R179 exact head `05eae18a39ec53305050ad3df2bcbfdbf94852c6`. Three **new** files only, no original articles, 35 metadata files, eight source inventories, citation tokens, original source interpretations, home, CMS, or Grok task queue modified. No release authorization.

## Safety engineering

The new read-only `preparedness/tools/r180_docket_reconciliation_gate.py` requires R179 to establish a valid **35 original articles / 2,000 citation tokens / 385 authored source-use relationships** structural hard hold before accepting the four authenticated preexisting human-review dockets R170–R173. The gate pins their exact Git blobs, checks every unresolved family card source and food-safety claim, verifies claim source IDs in the original article-specific crosswalk, binds the three affected article metadata identities, preserves the literal NCHFP trailing-slash difference, rejects fabricated reviewer decisions and HTML/CMS publication promotions, and emits an optional deterministic 21-ticket packet. The CLI **always exits 2**, including on intact sources, and never says QD PASS, human safety approval or commercial approval.

| Source docket | Git blob independently authenticated | Unresolved scope |
| --- | --- | --- |
| R170 family card | `54b7d61fbd5829c458d125d63c0b171c6f36998e` | **11 of 11 PENDING**, human-link and safety checks explicitly false |
| R171 source variance | `cd757a36e3015b732916ffd6655856a575140350` | One NCHFP jerky URL slash discrepancy; **32 shared literal URL review groups** |
| R172 affected articles | `45963b30ce48a069539c66ace9f1a2d2f5cf1dfd` | **Three draft articles** and their unchanged metadata/source identities |
| R173 claim review | `48e1050e815f55c5f2564dc030b8ba2aa24df548` | **10 of 10 PENDING** human source, qualified food-safety and independent QD decisions |

Original inspected article metadata Git blobs: `safe-jerky-dehydration` `50b365e8109c14bdb9ce1a9365db88215a678ec5`; `pemmican-and-dried-meats` `03d3824e07fe51931671d0ddc7aa8c85eda58435`; `pioneer-travel-rations` `7191acba55d63dc405ad9c2003d66193276da89f`. All ten claim source-ID lists and the three impacted source IDs were independently checked against those original metadata files through connected GitHub. All matched. **This is an authenticated file/source inspection, not authentic native Python execution or human verification of claims.**

**Review count caution:** 11 family source questions + 10 distinct jerky claim questions = **21 specifically indexed review tickets**. The previously reported **75 source decisions** and **32 shared-URL groups** may overlap these; do not add them as independent cases. None is resolved by inventory generation. The NCHFP/USDA FSIS food-preservation difference remains safety HOLD; neither URL variant nor heat-treatment method was approved. Original 29 pending / 4 historically not-required / 2 historically approved-but-unverified metadata safety labels remain **non-authorizations**.

## Testing / remaining checks

- `python -m py_compile` on the exact validator and test files: **PASS**.
- `python -I -m unittest discover -s preparedness/tests -p 'test_r180*.py' -v`: **73/73 PASS**, 0 skipped, in a **synthetic** 35-article / 385-relationship fixture. Includes **52 independent reviewer-state mutation cases**: 11 family records × 2 corruptions and 10 jerky claim records × 3 corruptions. Malicious links, source-citation swaps, missing claims, altered article custody, fake approvals, stable digest and CLI invalid-input tests also exercised.
- Committed code blob identities checked against exact local tested bytes: validator `f349eb14cf1bd271e8d70123e78a6bf90d3bf0c8`, tests `f4c60b19d85dbfa35d6df69a85f3a711dc33cd6d`.
- `git ls-remote https://github.com/finalvestigestudios/final-vestige-site-layer.git HEAD` failed in local container with **Could not resolve host: github.com**. Full checkout, original `validate.py` / `build.py` / full `preparedness/tests`, authentic R176/R178/R179/R180 Python runs, WordPress export/browser/print/privacy QA and independent QD are **NOT EXECUTED**. An intentionally incomplete-checkout CLI returned `INVALID_HARD_HOLD`, exit 2.

Full trusted checkout runbook (intentional exit-2 gates are NOT a build success claim):

```sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r176_native_review_preflight.py --repo . --timeout 300
python -I preparedness/tools/r178_safety_state_admission_gate.py --repo .
python -I preparedness/tools/r179_source_use_crosswalk_gate.py --repo . --summary
python -I preparedness/tools/r180_docket_reconciliation_gate.py --repo . --summary
```

These last safety/citation review gates **always return code 2** and explicitly retain `DRAFT_HARD_HOLD` for structurally valid artifacts. Do not treat status as publication readiness or fake a QD pass.

## Seven Claude branches + independent QA

Fresh connected-GitHub comparisons returned **7/7 identical, 0 ahead / 0 behind**:

- Start `2122d856fce9f64887c16df3d52e64be9f59a55b`; Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`.
- Historical Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; Historical Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; Historical Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`.

Independent safety PR **#157** `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (main-breaker exercise rewrite / medication warnings), fixture-isolation PR **#169** `e9cd7766dac59d47ab467d8945269b9146c2aef5`, and #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` were freshly inspected as actual patches and kept separate. Current homepage lead PR #1326 `36888bea912c4dafad16d8dd96b059ff164b6350` was checked but not modified. No blind cherry-picks or contributor changes.

## One-topic conversion lane — OFFER → STEP → BLOCKER → ACTION → EVIDENCE → OWNER

| Offer and funnel step | Blocker | Proposed draft-only experiment | Result | Owner |
| --- | --- | --- | --- | --- |
| Existing paid FV Preparedness toolkit → real order | No authenticated matching currently purchasable rights-cleared SKU, seller checkout/delivery/refund evidence | Commerce authenticate exact owned SKU/listing/price, licenses, download and refund/fee records **before** a purchase CTA | **HARD HOLD**, no purchase link or verified SKU | Commerce / Claude |
| Caregiver-school-reunification social asset → free Household Emergency Plan | No matching real published Grok `asset_id`, permitted caption/profile CTA, accurate publish timestamp or approved landing | Grok/Praxxis review an *existing* social asset through TASK-008; do not create/post/modify queue | **UNVERIFIED**, TASK-008/handoff read, no confirmed fit | Grok / Praxxis |
| Ungated free Household Plan → optional free Family Reunification Card | 11 source-review decisions, privacy, print, keyboard, accessibility, real WordPress rendering incomplete | Qualified review; staged fake contact data at 360/390/768/1440, test privacy/no exfiltration and legible print | **HOLD**, 11 of 11 pending | Preparedness / independent Site QA |
| Source-backed article → credible citation | Ten jerky claim reviews, conflicting NCHFP/FSIS practice interpretation, exact URLs unresolved | Qualified source/food-safety reviewers reconcile each claim and preserve original context; independent QD | **HOLD**, 10 of 10 pending | Safety/source/QD reviewers |
| Qualified humans → CTA → confirmed lead → verified paid order → net | No first-party qualified session or merchant settlements, fees/refunds, 7/30-day attribution | Existing #820 measurement only, no new pixel; QA consent/attribution and merchant reconciliation | **NOT COMPUTABLE** | Claude / Commerce / Analytics |

**Draft-only on-site CTA:** “Who picks up your child if phones fail? Read the free Household Emergency Plan and make a household contact plan.” No live link is asserted. Proposed **ungated** guide is an original draft, not a current live route. Free Family Card remains unlaunched and must never be described as tested privacy-safe. The sole approved email opt-in remains the existing Seven Day Focus Fieldbook at `/focus/`; do not revive retired water freebies.

Future UTM proposal **only after verified Grok actual ID and landing approval**: `utm_source=<actual_platform>`, `utm_medium=organic_social`, `utm_campaign=preparedness_pilot_2026_11`, `utm_content=<actual_asset_id>`. Paid orders must come from authoritative merchant records; clicks/leads are not sales. KPI `1000 * realized_net_revenue / qualified_human_sessions` is **not computable** without verified numerator, nonzero denominator, cohorts, fees/refunds, and tiny-sample warnings.

**Nonrelease covenant:** No merge, WordPress/CMS changes, public nav, publication, homepage, affiliate/merchant activation, tracking scripts, email, social posts, Grok queue edits, or spending. Founder retains all release approvals. Relevant Issues: [#136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136), [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).
