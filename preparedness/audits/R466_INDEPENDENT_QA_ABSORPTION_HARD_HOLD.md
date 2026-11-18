# R466 — Independent QA absorption custody (DRAFT / HARD HOLD)

**Inspected:** 2026-11-18, 11:18–11:xx PST. **Owner/lane:** Preparedness integration and source/citation safety only. **Canonical:** #136; commercial #820/#818. **Parent:** R465 draft PR #3030 at `fdc2bbcd9883e0956679d35537302d46580a756c`. No merge, WordPress/CMS/navigation, user tracking, commerce, social, email or publishing.

## New substantive evidence: independent QA fixes are present in candidate, but not verbatim cherry-picks

Read-only GitHub fetch of five complete files at R465:
| Input | Git blob SHA | Independent QA invariant |
|---|---|---|
| household-emergency-plan.body.html | `f81cd43516e8295104230412f18776919148f905` | Simulated outage instructs **not** to turn off the main breaker; retains powered refrigeration, alarms and medically essential equipment |
| three-day-kit.body.html | `933f38ff3cd55a241cf9b392014fc52d4961e84f` | Does not tell readers to stop/discard/ration medicines; directs individualized prescriber/pharmacist advice and replacement planning, including refrigerated medicines |
| sources/fragments/start.json | `96140d6d1872588e5d20d9052445c9157e88934d` | American Red Cross classified as `nonprofit`, not regulator |
| taxonomy.json | `15c547bb3018ac182b12a51036389cfa39a59168` | All four Start Here articles `gate=true`, 35 original article rows retained |
| tests/test_preparedness.py | `c329f98e051d2aabe31a3343869b0fdac355b315` | Both source-fixture tests use `TemporaryDirectory`, copied source tree and `Library(root=sandbox)`; neither test writes a canonical source fragment |

**Crucial nuance:** #157 independent QA HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` is unmerged; #169 independent fixture HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5` remains unmerged; dependent repair #2205 HEAD `bbcf1859768624c611df4abadc564c18247cf32a` is also unmerged. Their changes are **semantically represented, not line-for-line identical**, in R465. This is NOT a merge of, approval for or replacement of their PRs. Independent reviewer must adjudicate exact wording, authority and fixture semantics before any release.

## R466 deliverable

`tools/r466_independent_qa_absorption.py` is a read-only guard over the exact five Git blob pins. It rejects missing/symlinked evidence, altered source bytes, duplicate JSON keys, lost or unsafe household drill qualifiers, missing medicine caveats, fraudulent Red Cross regulator classification, missing/ungated Start Here entries, duplicate article slugs, published statuses, and source-fixture tests that do not demonstrably use temporary copies. It has no write side effects and intentionally emits `HARD_HOLD`/exit 2 **even if all structural checks pass**. It does not imply human medical or emergency safety review.

`tests/test_r466_independent_qa_absorption.py`: 74 deterministic exact-file local unit tests; 64 mutation cases plus 10 baseline/negative cases. Local `python -I -m unittest discover -s preparedness/tests -p 'test_r466_*.py' -v` **PASS 74/74**; Python compilation PASS. New GitHub source and test blob hashes matched **exact executed local files**, not merely prototypes. Native R466 gate on incomplete local checkout exited 2 with five missing original files; authenticated full 35-article `validate.py` / `build.py`, 41 WP / 41 preview exports, signed-out/mobile/checkout/browser, and full suite **NOT EXECUTED**. Five real source pins independently fetched back and matched GitHub values; not a native run.

## Original contributor/provenance and other agents

Compared all 7 Claude originals and 2 Shelter descendants to frozen R460 Git refs using repository comparison: each reported `identical`, ahead 0 / behind 0. Current separate Apollo/home lead #3031 inspected, left unchanged. Historical human-held items remain: 5 substantive source disputes, 9 unselected forks, 17 diverging articles and 32 shared URL/reading-scope groups (not interchangeable citations). No false QD PASS.

## One prepared audience / conversion-critical acceptance (all draft)

**Audience/topic:** household emergency contacts, school pickup and family reunification. **Only already-live free resource candidate:** https://finalvestige.com/preparedness/ ; its public page promises free, ungated official-source resources. Any claim of a matching *published* Grok social asset remains **UNMATCHED** until Praxxis/Grok supplies exact platform, immutable asset_id, public permalink, posted message, rights and signed-out mobile click path.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Existing FV-owned rights-cleared Preparedness paid pack **not authenticated** | eligible paid order | payable SKU/rights/merchant acceptance/delivery/refund/settlement missing | founder/commercial evidence collection; DO NOT add paid CTA | HOLD; no SKU or confirmed sale | Founder / Commerce |
| Existing free official-source Archive | published social link -> relevant free landing | actual matching Grok asset_id, permitted URL and mobile proof unknown | draft-only message/landing intent, visible free/no-signup framing, mobile click-through checklist | Source-backed public landing exists; asset UNMATCHED | Grok / Praxxis |
| Original Article #15 -> free Tool #104 (optional) | guide -> optional downloadable aid | emergency dispatch, school/child privacy, printing, no-JS accessibility, human QD | draft CTA only after qualified review | HARD HOLD; not public | Preparedness / QD |
| Real merchant confirmed order | CTA -> lead -> checkout -> paid order -> fees/refunds -> net revenue | qualified sessions and merchant+attribution evidence absent | 7/30-day privacy-safe cohort and mismatch audit; no duplicate measurement scripts | NOT COMPUTABLE (net revenue/1000 qualified sessions) | Claude / Commerce |

**Draft free CTA only:** “See official household emergency-planning resources.” This is proposed copy, NOT a deployed page element. Never gate official help, revive retired water products, invent urgency, or claim a checkout start, click or lead as a sale.

**Release owners:** Grok content/posting, Praxxis independent creator QA, Claude website/analytics, Preparedness original integration/review, founder publication/spending/commercial approval. No approval or activation implied.
