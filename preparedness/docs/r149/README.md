# R149 — Authentic tool-level source-use docket and fail-closed custody

**DRAFT / HOLD · Preparedness-only · Issues #136 / #820 / #818 · 2026-11-05**

Stack base R148 PR #1123 exact commit `1ff2ea77afba5e6fd0d0c11577235a5f36f6f92e`. No changes to any original source, article, tool, WordPress, homepage, analytics, commerce, email, social channel, CMS, navigation or safety approval. Never apply a candidate origin automatically.

## What changed

1. `tool-source-use-review-docket.json` contains **67 authentic tool/source-use relationships**, including the author-specific explanation, literal source URL, original fragment's support description, effective origin and number of citation occurrences. Every row is explicitly **PENDING** qualified review. The docket pins **16 exact Git source blob identities**: crosswalk + register + two contributor fragments + six tool bodies + six tool metadata records.
2. `r149_tool_claim_custody.py` regenerates the same docket from a trusted full checkout and rejects any change, deletion, altered URL, explanation, citation multiplicity, candidate origin, source scope, publication state, evidence path, forged QD state or hidden/linked source file. It is a read-only diagnostic; successful structural verification still prints **DRAFT_HOLD**, never medical or QD PASS.
3. `test_r149_tool_claim_custody.py` includes **80 isolated Python tests**: 60 independent author-specific claim mutations, 15 other negative scenarios and five positive controls. Compilation and 80/80 tests passed locally against synthetic fixtures. GitHub readback matches exact locally tested source and test Git blobs.

## Authentic-source findings

| Tool | Current unresolved source IDs | Candidate ONLY | Unique cited sources | Total citation occurrences |
|---|---:|---|---:|---:|
| Family Reunification Card | 11 | shelter | 11 | 16 |
| Home Fire Escape Worksheet | 6 | shelter | 7 | 11 |
| Kit Builder | 19 | start | 22 | 106 |
| Power Outage Planner | 16 | shelter | 17 | 26 |
| Reunification Plan | 6 | start | 7 | 7 |
| Water Planner | 0 | existing base | 3 | 7 |
| **TOTAL** | **58** | **NOT APPLIED** | **67 row relationships** | **173** |

All 67 selected source records contain a stored `supports` explanation and the respective tool metadata includes an author-specific `source_use` note. **Zero** of these 67 records has `human_link_check:true`. Although many records have `verified_on` metadata, that must **not** be described as today's live URL verification, qualified source-scope adjudication, medical review or approval. One source row is not one medically verified claim.

The five candidate mappings are still missing from the active `sources/crosswalk.json`. Until reviewed, `Library.source_for()` retains its fallback behavior and the native build may fail. The source register and crosswalk remain untouched. No draft URL or finished download is asserted.

### Independent review order (human, not executable approval)
- Source reviewer checks **each of 67 author-specific explanations** against the actual live primary source and citation passage; validate exact publisher and update dates. Record any corrected support interpretation in a separate reviewed proposal, never overwrite the original docket.
- Prioritize the 11 Family Reunification Card mappings, then generator/heat, home fire, medication/medical-device, and food/kit claims. Do not mistake a consistent URL or support excerpt for independent guidance clearance.
- Complete conflict adjudication of 32 shared-URL groups, Historical Food source-ID substitutions, CDC outage/high-rise fire citation changes and QA #157 refrigerated-medication wording before replacing any article body. Preserve all 35 original article bodies, source citations and statuses.
- PR #169's fixture isolation requires separately reconciling #973; these test patches must not change real source fragment files during tests.
- Run full R133–R149 integrated gates, native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py` and `python -I -m unittest discover -s preparedness/tests -v` against a trusted complete repo; 35-article/6-tool draft output + viewport/print/offline/QD remain **NOT VERIFIED**.

Run R149 in a trusted checkout (expected exit **2** while review is pending):

```sh
python -I preparedness/tools/r149_tool_claim_custody.py --preparedness preparedness --docket preparedness/docs/r149/tool-source-use-review-docket.json
```

The local 80-test synthetic suite is only a code-contract check; this is **not** a native 35-article regression, live WordPress verification, merchant validation or source approval. No GitHub Actions rerun is requested while the machine fails before reporting test steps.

## Conversion-first, exactly one proposed reader path

**Intended existing audience:** caregivers planning emergency contacts/school pickup and family reunification. **Authentic free article:** Household Emergency Plan, still DRAFT/HOLD. **Optional authentic tool:** Family Reunification Card, still DRAFT/HOLD, with 11 unadjudicated source IDs and no mobile/print/offline/private-data review. **Paid pack:** no verified rights-cleared, currently purchasable FV Preparedness SKU, so **NO paid CTA, product claim or checkout link**.

Unpublished copy for future editorial review: “Build a household communication plan you can practice. Read the free Household Emergency Plan and, once its source and usability reviews are complete, optionally prepare a private printable Family Reunification Card.” This is not a public promotion and does not gate safety information behind a lead form.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Existing **paid** Preparedness pack → confirmed paid order | No authenticated matching SKU/rights/price/delivery/return terms | Commerce verifies existing Payhip offer and checkout, order/fulfilment, refunds/fees before any purchase CTA | **HOLD; no offer or paid sale verified** | Growth / Commerce / Claude / Founder |
| Authentic Household Emergency Plan → reader | Source/safety/QD/native build incomplete | Qualified review; check article/citation/WordPress draft parity | **DRAFT/HOLD; not live** | Preparedness + independent QA |
| Article → Family Reunification Card | 11 source-origin gaps, print/privacy/offline/360px/390px untested | Human review of precise 11 rows, then staged export QA | **67-row structural docket BUILT; live download NOT TESTED** | Preparedness + Site QA |
| Actual Grok content → article | TASK-008 has no verified Preparedness asset_id/permalink/destination/UTM | Praxxis/Grok reconcile immutable asset_id and allowed landing placement; no new creative queue | **UNVERIFIED** | Grok / Praxxis |
| Qualified sessions → CTA → confirmed lead → settled paid order | Consent-safe human denominator, merchant orders/fees/refunds, offer missing | Use existing #820 event contract and 7/30-day cohorts; don't add scripts | **NET REVENUE PER 1,000 QUALIFIED HUMAN SESSIONS NOT COMPUTABLE** | Claude / Commerce / Analytics |

Preserve existing `/focus/` lead magnet; do not resurrect retired Water Resilience freebies. No email, affiliate activation, spend, live CTA, production content or social post.

## Coordination and holds

The seven Claude cluster branch names and their pinned commits were read via GitHub and **all seven comparisons returned identical/0 ahead/0 behind**. Independent QA #157, synthetic fixture #169, corrective #973, homepage #49/#604 were inspected at their exact heads; nothing changed in those other lanes. Grok/Praxxis Drive TASK-008 and dated handoff were read; no existing content queue was modified. Issues #136 and #820 contain cross-referenced release/business governance.

**Final state: BUILT + 80 LOCAL SYNTHETIC TESTS PASSED; GENUINE REPOSITORY NATIVE BUILD / BROWSER / QD / HUMAN SOURCE AND MEDICAL REVIEW / OFFER / LIVE / PAID SALES UNVERIFIED.**
