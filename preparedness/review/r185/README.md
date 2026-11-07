# R185 — six Preparedness companion-tool source/citation custody, privacy and conversion HOLD

**Scope:** Issue #136 ONLY; conversion coordination #820, charter #818. **Exact parent:** R184 draft commit `9afd20a1252fa8c5651fdd68a4bdd0f66b3af779`. **State:** BUILT / SYNTHETICALLY TESTED / DRAFT HARD HOLD; never approval or automatic release.

## Material contribution

R184 admits the 35 original instructional articles, but its gate does not inspect the six *separate* downloadable/printable tools. R185 adds a read-only validator `preparedness/tools/r185_tool_custody_gate.py` for the six original companion drafts. It joins original article/tool metadata and citation occurrences to the existing human-review docket `preparedness/docs/r149/tool-source-use-review-docket.json`. It retains author-specific source interpretations, literal URLs, and pending human review instead of treating an archived machine check as independent safety clearance.

**Authentically verified at R184 head via connected GitHub:**
- **Six original tool body/meta pairs**: Family Reunification Card, Home Fire Escape Worksheet, Kit Builder, Power Outage Planner, Reunification Plan, Water Planner; all original body/metadata blob IDs match the 12 pinned R149 identities.
- **Four source inventory/crosswalk inputs** also match their R149 pinned blob IDs: **16/16 identical in the original repository tree**.
- **67/67 authored source-use rows** match the six tool metadata dictionaries and the *exact original citation token counts*: **173 occurrences** (per-tool **16, 11, 106, 26, 7, 7**). Original docket declares **58 currently unresolved source relationships**, not 58 unique URLs and not 58 independently reviewed claims. Per-tool unresolved: **11, 6, 19, 16, 6, 0**. In particular the Family Reunification Card has **11 unresolved relationships**.
- Original source/citation corpus was read through GitHub; the **generated** WordPress-ready drafts and native build-report were **not rebuilt here**. The 35-article citation count of 2,000 remains inherited R184 custody, not reexecuted.

The R185 validator requires every original tool to remain unpublished, exact source/body Git blob identity and complete original authored source mapping, no duplicate roster/URLs, matching per-tool source order and 173 citations in generated WordPress-ready draft exports, QD/source/safety warnings, noncommercial destination URLs, no false approval or order claims, and no loss of the Family Card's minimal/privacy controls.

For the Family Card, extra **static** deny checks reject browser storage/network APIs, added form submission/external script/iframe destinations, lost physical-card warning, or bypassed minimal-model rendering in the generated draft. These scans are a limited backstop, **not proof that user data cannot leak**: browser network inspection, JavaScript execution, manual keyboard/accessibility, 360/390/768/1440 responsive, real printing/trimming, fake-family-data tests, no-JS handling and independent privacy review remain required. No real children's information should be entered during QA.

## Executed test evidence and honest limitations

**Local tests:** `python -I -m unittest discover -s preparedness/tests -p 'test_r185*.py' -q` — **99/99 PASS, 0 skipped**, including 67 source-review false-clearance mutations, six citation-loss mutations, eight injected privacy sink detections, and other falsified approval, route, reviewer, roster and document cases. Python compilation PASS. Tested original Git blob IDs match the two files actually committed in this PR: gate `fd9665aeaa18f57476e119da06ae60f56fd764c5`, test `1f4a9deb94230fe5e49dcfd0e1c65a75965d3730`. Clean **synthetic** fixture always yields `DRAFT_HARD_HOLD` exit **2**; deliberately incomplete checkout yields `INVALID_HARD_HOLD` exit **2**.

**Not executed:** authentic 35-article + 6-tool `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, full real repository test discovery, WordPress runtime/browser, independent citation/source adjudication or QD. `git ls-remote https://github.com/finalvestigestudios/final-vestige-site-layer.git HEAD` failed locally: `Could not resolve host: github.com`. The local synthetic fixture has no actual `validate.py` or `build.py`; attempted commands correctly failed because those files are absent. The real checkout and generated outputs remain necessary. These 99 tests are **structural synthetic** tests only.

Trusted full-checkout commands after `validate` and `build`:
```sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r184_report_admission_gate.py --repo .
python -I preparedness/tools/r185_tool_custody_gate.py --repo .
```
Both R184 and R185 return **2 by design**, even for intact draft custody. Never interpret exit 2 as publication success, independent safety approval, QD PASS or revenue.

## Contributor and release coordination

Compared exact original seven Claude Preparedness branch commits with current refs: **7/7 identical, 0 ahead/behind** (Start `2122d856fce9f64887c16df3d52e64be9f59a55b`; Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; historical Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`; Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`). Reinspected PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` safety corrections and #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` / #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` fixture patches; all remain independent. Homepage review #1358 `4272cc5860ce6f56a9460c50891001a4372b0d89` remains separate/frozen.

No original 35 articles or six tools, registers, source docket, CMS, homepage, navigation, analytics, affiliates, merchant, email, posting or spending were changed by R185.

## OFFER → FUNNEL → BLOCKER → CHANGE / EXPERIMENT → EVIDENCE → OWNER

| Offer / funnel step | Blocker | Change / acceptance experiment | Evidence / disposition | Owner |
| --- | --- | --- | --- | --- |
| **Actual matching paid Preparedness pack → verified paid order** | **No authenticated existing, purchasable, rights-cleared Preparedness SKU, offer, delivery, refund/fee ledger or consent-approved campaign** | Commerce verify live SKU, seller rights, files, accessible checkout and provider confirmed order; publish nothing until founder release | **HARD HOLD**, no offer/checkout/sale verified | Founder / Claude Commerce |
| **Grok social caregiver audience → free plan** | No verified existing published `asset_id`, platform post, destination or CTA for school pickup/phones-down topic in TASK-008 | Grok/Praxxis supply actual published media URL, source/rights clearance, asset ID and CTA placement; no new Grok assignment | **UNVERIFIED** | Grok / Praxxis |
| **Household Emergency Plan → optional Family Card** | Unpublished guide; 11 Family Card source decisions; private data + physical loss/print risk | After source/safety/QD approval, staged fake-data acceptance and exact download/print evidence at 360/390/768/1440; preserve ungated access | **DRAFT HARD HOLD**, R185 99 synthetic tests only | Preparedness / independent Site QA |
| **Approved opt-in → confirmed lead** | No verified caregiver-specific consent/confirmation; Focus Fieldbook remains sole approved opt-in | Never gate emergency content or add a subscriber script; reuse existing `/focus/` only after relevant consent/relevance decision and provider delivery proof | **NOT VERIFIED** | Claude / Dispatch |
| **Paid conversion → realized net revenue** | No authenticated merchant orders or deduped qualified human sessions | Use existing #820 contract (actual `asset_id`, exact destination, CTA, independently verified sale, refund, fees; 7/30-day cohorts) | **NOT COMPUTABLE**, not zero | Commerce / Analytics |

**Proposed disabled copy (not a public button):** “What happens if you cannot call your child's school? Read the free Household Emergency Plan.” Companion after independent privacy/source review: “Print a private family reunification card — free; use first names only.” No paid upsell is proposed until a genuinely sellable/rights-cleared matching product is confirmed. **Do not revive retired water freebies or change the Focus Fieldbook.**

No live, sale or source-approval claim is made.