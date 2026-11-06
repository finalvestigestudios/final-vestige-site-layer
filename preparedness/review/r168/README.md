# R168 — print-footprint & browser-persistence review gate (DRAFT/HARD HOLD)

**Ownership:** Preparedness Archive only; GitHub #136. Conversion coordination #820; charter #818. **Stacked on R167** exact commit `0d5b869abbe2949d1a1ccd78617b2e5a3642160d` (draft PR #1253). Additive review-only artifacts. This is NOT a publication, QD, privacy-certification, medical, emergency-use or commercial approval.

## Risk & bounded engineering change

R167 detects transient browser API privacy sinks and in-memory card fields, but its print check only confirms `#rc-sheet` visible and `#rc` hidden. A malicious or accidental extra visible element, CSS-generated text, shadow-root node, or data attribute can still expose synthetic school/caregiver values when `@media print` applies, despite a clean four-card preview. R168 adds a second **Chromium offline** preflight that checks the complete print-visible DOM tree and pseudo-content after synthetic minimal-card selection, synthetic-value leakage into DOM attributes, browser navigation/history/window.name, attempted popup/export APIs, and residual values after clearing all 13 fields. It checks 360/390/768/1440px, four printed copies, and extra requests/errors. Tests exclusively use synthetic sentinel strings and report only booleans/counts, not names, form fields, URLs, or payloads.

**Fixture regression evidence (locally executed 2026-11-06):** `python -I -m unittest discover -s preparedness/tests -p 'test_r168*' -v` -> 94/94 PASS. Real headless Chromium exercised; negative tests intentionally introduced visible print leaks, CSS pseudo-element leak, hidden attribute persistence, simulated history replacement, window.name persistence, popup attempt, external image loading, clear regressions, and print/4-copy faults; those were caught. Python isolated-mode compilation passed. This is synthetic **test harness evidence**, not an authentic article/WordPress/privacy proof.

**Authentic chain on a complete trusted checkout:** R168 `authentic()` calls R167 `authentic()` -> R166 -> R165 -> R164 -> R163 -> R162 -> R161 (full 35-article body/source/citation custody). It then compares the identical R165 inline-script expansion SHA and probes the authentic staged Family Reunification Card. No original article or metadata file is altered. The CLI returns status DRAFT_HARD_HOLD or INVALID_HARD_HOLD and exit code **2 even when local checks pass**; no promotion to QD PASS or LIVE. Run these commands on a trusted full repo:

```
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r168_family_print_persistence_gate.py --repo . --report /tmp/fv-r168.json
```

The trusted full checkout remains inaccessible to this local Python runtime due to DNS failure for GitHub (confirmed this run). Accordingly full validation/build/35-article suite, actual Family Card Chromium, WordPress staging, real printer privacy, independent source/safety review and QD are **NOT RUN / NOT VERIFIED**. The hard-hold is not a claim that all print vectors have been exhausted; printer spoolers, extensions, accessibility technologies and WordPress integrations require genuine staging/human QA. Special caution: printing *any* family details may leave paper or spooler records; never claim universal confidentiality.

## Current exact dependency heads, verified read-only November 6, 2026

| Contributor | Branch | Authenticated SHA | Compare with preceding checkpoint |
|---|---|---|---|
| Start Here | `claude/prep-start-bbfeb8` | `2122d856fce9f64887c16df3d52e64be9f59a55b` | identical |
| Food | `claude/prep-food-ccdc55` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` | identical |
| Shelter | `claude/prep-shelter-5e1e0e` | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` | identical |
| Health | `claude/prep-health-837444` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` | identical |
| Historical Field | `claude/prep-hist-field-9db767` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` | identical |
| Historical Food | `claude/prep-hist-food-b81f19` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` | identical |
| Historical Home | `claude/prep-hist-home-0e0e38` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` | identical |

Independent safety PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, synthetic isolation PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`, follow-up #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`: read-only, unmerged draft; do not overwrite revised claims with historical patch text. Homepage #49 `10495883299d53596992c26a8987f629b2904670` and #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`: separate lanes. Baseline 35 instructional articles, 2,000 citation occurrences and 385 source-use interpretations remain under previous immutable custody; 75 review decisions have **not** been independently approved in this round. Preserve URLs, reading depth and safety states.

## Offer → funnel step → blocker → proposed experiment → evidence → owner

| Priority | Offer and funnel step | Blocker | Change/experiment (not live) | Pass/fail evidence and owner |
|---|---|---|---|---|
| 1 | **Existing FV Preparedness SKU → paid order** | No verified currently sellable, rights-cleared matching SKU, exact terms, usable checkout, delivery, refunds or settled orders | Commerce audits actual Payhip product ownership/fulfillment and end-to-end checkout before enabling any optional paid pack CTA; source/safety guidance remains ungated | **HOLD; no merchant verification**; Commerce/Claude + founder |
| 2 | **Household Emergency Plan → optional free Family Card** | Outstanding source-review workorders and unverified printable privacy | R168 print/persistence preflight plus independent 360/390/768/1440px WordPress browser/print QA, consent/trust disclosures and accessible no-JS pathway | **94/94 synthetic PASS; authentic FAIL-CLOSED/UNRUN**; Preparedness/Site QA |
| 3 | **Grok asset → verified destination** | Published Preparedness-specific `asset_id`, landing URL and UTM absent in reviewed TASK-008; no verified qualified human visits | Grok/Praxxis reconcile actual post IDs and platform allowed link mechanisms in existing Drive handoff; do not change queue or create content | **UNVERIFIED**, Grok/Praxxis + Claude analytics |
| 4 | **Confirmed session/lead → settled order → realized net** | No attributable qualified denominator/settled purchases or fees/refund ledger | Reuse #820 consent-respecting tracking contract; 7/30-day cohorts; distinguish affiliate outbound vs settled commission, Payhip gross vs net | **NOT COMPUTABLE**, Commerce/Analytics |

**Draft CTA only:** “Make a free household emergency contact and pickup plan.” There is NO authorized paid CTA. Do not resurrect retired water freebies, invent a product/price, or gate critical safety information. TASK-008 and dated Grok/Praxxis handoff reviewed read-only; no confirmed matching Preparedness asset ID in the inspected text; no Drive queue writes.

**Release boundary:** no article, source, route, taxonomy, CMS, navigation, homepage, analytics, merchant, affiliate, email, social, or spending changes; PR remains **DRAFT/HARD HOLD** until independently qualified safety/source/QD and founder release approval.
