# R187 — independent receipt identity, native \`-I\` import repair, and hold integrity

**Issue #136 ONLY.** Conversion coordination #820; charter #818. **DRAFT / HARD HOLD; not a source, privacy, clinical, food-safety, QD or commercial approval.** Stacked on isolated R186 PR #1373 exactly at \`2daf260b4bfe3687afd056df84ed00c003a42d3d\`. Do not merge or publish. No original content, six companion tools, source registries, media, checkout, CMS, navigation, live analytics, email or social work has been changed.

## Concrete gaps found and repaired

R186's aggregate \`verify_gate()\` checked release-state, select counts and QA PR keys but **did not bind the nine subprocess responses to their specific producer schemas**, did not require a complete negative approval-state record for each, accepted arbitrary QA PR values provided their *keys* were 157/169/973, and did not require all four original safety-excerpt observations. A structurally forged but wrong-producer receipt could have been counted as an acceptable HOLD. No claim that such receipt was observed in production; this was a testable validator gap.

R186's CLI example uses \`python -I\`; Python isolated mode removes the script directory from normal import discovery. Its prior bare sibling import \`from r176_native_review_preflight import ...\` could fail before native validation even began. R187 replaces it with an explicit, path-pinned \`importlib.util.spec_from_file_location\` loader. The same loader reads the new R187 contract module. This repairs module *discovery* only, not the separate unresolved complete-checkout and subprocess checks.

The new strictly **read-only** \`r187_receipt_contract_gate.py\` binds:
- Seven original versioned gate schemas (R174/R175/R177/R178/R179/R180/R182). R184/R185 currently have no schema, and their absence is explicit rather than silently fabricated.
- Each gate's required negative safety, source, QD, WordPress, commerce and publication flags; recursively reject hidden positive releases.
- Exact independently expected source/citation metrics, including 35 + six drafts, 2,000 article citations, 173 tool citations, 385 + 67 author/source-use relationships, 244 inventory rows, 225 unique IDs, 21 indexed tickets, the legacy 75-source and 32-URL review groups; **these overlapping classes are not additive**.
- R177's four original safety-critical source/draft observations for the Household Emergency Plan and Three-Day Kit.
- R178's two historical \`approved\` but unverified states and four historical \`not-required\` editorial holds.
- Exact independent PR SHA values: #157 \`7d1ae6b8ef93d10cfb6810987672360885e9c1aa\`, #169 \`e9cd7766dac59d47ab467d8945269b9146c2aef5\`, #973 \`4d40996a559b0124d74a9bb3bdcd481ad1992aa8\`. These are custody baselines, not authorization to merge.

R186 now calls the new semantic contract **only after** its existing structural receipt check passes, and converts discrepancies to failed steps, resulting in \`INVALID_HARD_HOLD\`. If every real step eventually passes, the only permissible aggregate result remains \`DRAFT_HARD_HOLD\`, exit 2. The existing 83 synthetic R186 tests continue to cover the original pure adjudicator unchanged.

## Evidence / honest execution limits

On a local isolated *synthetic* copy of the **exact committed helper/test text**, ran:
\`\`\`sh
python -I -m unittest discover -s . -p 'test_r187*.py' -v
# Ran 77 tests in 0.002s — OK
python -I -m py_compile r187_receipt_contract_gate.py test_r187_receipt_contract_gate.py
# success
\`\`\`
77 actual Python \`unittest\` cases include 72 positive/negative combinations across the nine independent contract types; incorrect producer schemas, rejected historical/medical/merchant/QD clearance, missing fields, incorrect typed counts, wrong QA commits and nested false approvals fail closed. Source Git blob identity of committed helper/test has been matched to local \`git hash-object\` (see PR/Issue #136). This test count is **NOT** the full native repository suite, and semantic correct receipts are NOT independent source verification.

**NOT EXECUTED:** R186's authentic 35-article + six-tool native validation/build, all original tests, 41 WordPress drafts/preview, staging accessibility/print/privacy tests, independent source adjudication, medical/food-safety/QD reviews. At this local environment \`git ls-remote https://github.com/finalvestigestudios/final-vestige-site-layer.git HEAD\` still fails with \`Could not resolve host: github.com\`. GitHub connector review can verify committed text/SHAs, not make a trusted full checkout.

## Current contributor boundaries and release priority

Seven contributor branches remain byte-identical to pinned heads: Start Here \`2122d856\`, Food \`f911ff7a\`, Shelter \`5daeaf2d\`, Health \`d5ef5baf\`, Historical Field \`4e5caf81\`, Historical Food \`67e116e5\`, Historical Home \`7504a5f0\` (full SHA and 0/0 compare receipts in #136). Independent PRs #157/#169/#973 remain draft, with overlapping \`preparedness/tests/test_preparedness.py\`; R182 checks semantic protections without blind merge. EX2 homepage PR #1372 \`c2544b8407bc612b758d780c0036aad428961fed\` remains separate.

**Safety publication blocker:** All 35 original articles and six tools remain source/safety/QD HARD HOLD. Historical \`approved\`/ \`not-required\` labels cannot grant release. Original depth and citation instances are retained; no article/tool body is rewritten here.

## Conversion-first acceptance (proposed only; no live CTA)

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Existing **Legacy Triage** Payhip PDF → paid purchase | A public $19 listing describes nine-section financial/records continuity PDF, not emergency pickup or child reunification; seller identity, rights, final checkout/delivery, returns and current product contents are not independently authenticated | Seek founder/commerce authorization for actual SKU/merchant/fulfilment evidence before any optional paid link; never mislabel this as a family emergency instruction product | Public candidate \`https://payhip.com/b/n1RhV\`; **COMMERCIAL HOLD**, no verified FV settled sale | Founder / Claude commerce |
| Creator high-intent topic “Who can collect your child when phones fail?” → free **Household Emergency Plan** | No verified Grok asset_id/post/destination + independent article review outstanding | After approval, map actual Grok asset in TASK-008, link to *released and reviewed* guide only; preserve /preparedness/ official-source-only gateway in meantime | **PROPOSED / NO CONTENT POSTED** | Grok / Praxxis |
| Free guide → optional **free** Family Reunification Card | 11 human source judgments; disclosure, local-only data retention, keyboard/mobile/print loss-risk validation | Staged 360/390/768/1440 checks with fake data, printable warning, no hidden network storage; leave all emergency advice ungated | **HARD HOLD / NOT TESTED IN BROWSER** | Preparedness / Site QA |
| Optional Focus opt-in → confirmed lead | Existing Seven Day Focus Fieldbook remains sole lead magnet, family-plan audience fit questionable | Only contextual secondary CTA with explicit consent; do not replace Focus signup or assert delivery without receipt | **UNVERIFIED** | Claude / Dispatch |
| Confirmed order → realized net/1,000 qualified humans | No paired first-party Grok campaigns + independently confirmed merchant orders/refunds/fees | Seven- and thirty-day cohorts with exact source-qualified denominator, tiny-sample flag; do not count clicks/signups as sales | **NOT COMPUTABLE**, not zero | Commerce / Analytics |

No retired water freebie, speculative offer, new measurement script, paid service, merchant activation, social post, queue change, email, site publication or spending.
