# R283 — authentic section-qualified route regression repair (UNAPPROVED)

**Issues:** #136 source/citation custody; #820 commercial attribution; charter #818.  
**Disposition:** DRAFT / HARD HOLD / no merge or public publishing.  
**Ancestry:** PR #2001 exact R282 HEAD `3edee430ea1bb5442f9a550423983b388f437737`.

## Reproduced defect and correction

Independent Praxxis review of R282 identified an invalid assumption: `derive()` required every frozen R200 article to have a *flat* `/preparedness/{slug}/` route. The authenticated 35-row frozen register actually uses `/preparedness/{section}/{slug}/`, e.g. `/preparedness/start-here/household-emergency-plan/`. This guarantees an invalid result on genuine frozen inputs despite the committed R282 review docket already having the correct routes. Do **not** change source routes, docket, or original article content to satisfy the old test.

R283 replaces that check with a strict, *exact-component* path validator: lower-case `preparedness` root; exactly one of seven authenticated sections (`start-here`, `water`, `food`, `shelter-power`, `family-communication`, `health-sanitation`, `lost-ways`); slug must match its original ID with safe lowercase hyphenated syntax; leading and trailing slash required. Rejects flat paths, unknown category, extra levels, path traversal, URI/query/fragment, encoded separators, case changes and malformed slugs.

The inherited R282 synthetic fixture now uses a section-qualified route. Added a distinct suite of 35 malformed-route controls, seven legitimate-section acceptance controls, exact category-contract test and two complete-checkout tests (authentic frozen 35-route roster and complete pinned R282 docket). The two native checks **skip** in the isolated partial test environment; they are intended to execute as part of the full checkout.

## Source-linked independent read-only verification

Connected-GitHub read at R282 HEAD pinned all four inputs: R200 original manifest blob `5822f9dfde21d1f3bdfc26658769d852c639438c`; R276 integrated inventory blob `b8c7c6df0dca62b04b01abc5671b7083ad9cb61e`; historical evidence lock blob `2dc41fccad6f1272f0a9d9585b6c10c760dcb08c`; R282 review docket blob `410226ffc7dcbcc65ad356055a81d9bef4e91eb2`. Every one of the 35 authentic original routes satisfies R283's new exact section/slug syntax. Independently recomputed all 35 three-way article rows from connected source objects: **35/35 identical** to the existing R282 docket. The aggregates also match, including **21 review-required articles**, **17** original/integrated differences, **14** body differences, **12** metadata differences, and six historical origin differences. Read-only connector parity is **not** full-tree Python execution and does not establish editorial adequacy.

Seven contributor refs were freshly compared to their R200 pinned commits: **7/7 identical**, ahead=behind=0. QA PR #157 remains open/draft HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (its safety fixes remain independently unmerged). Fixture QA PR #169 remains open/draft HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5` (its `test_register_fragments_cannot_duplicate_ids` still writes an `_dup_test.json` in the actual repository source tree). Homepage lead PR #1689 remains another owner's unmerged draft and is not touched.

## Bounded execution

Local Python 3.13.5: **247 isolated regression tests discovered, 245 executed and PASSED, 2 SKIPPED** because the four pinned authentic repository files were unavailable locally. Executed source and test files have **exact Git blob identities** `02260a61b0b74ec3110aa6a22a9d37ae49694260` (route gate) and `84fac949654ea9157b34461db2812c6a9a1010c5` (tests). Python compile check passed. This is explicitly not a claim of 247 full native passes.

The runner cannot resolve GitHub DNS for a full repository checkout. Therefore native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, full inherited tests, full-tree R283 validator execution, and all 41 WordPress draft outputs are **NOT EXECUTED**. None of the source files/artifacts, source-citation review states, 35 articles, six tools, original URLs or WordPress exporter are modified. GitHub CI and independently signed QD PASS are **NOT VERIFIED**.

## Editorial / source hold

All 32 shared-URL source groups, 15 duplicate source-ID groups and three disputed CDC/Ready.gov citation occurrences remain under human adjudication. Article #7 chemical-contamination guidance is not medically certified. Article #15 and Tool #104 require independent child-data privacy, accessibility and paper-usage review. The 21 three-way historical lineage differences (including four all-distinct body witnesses #27/#32/#33/#34) require substantive editorial review: matching hashes or counts do not prove safety or reading-depth parity. The historical water planner and retired water freebie remain unauthorized. Never promote unapproved content by changing status flags.

## Conversion-first handoff (internal acceptance only)

**Audience:** households seeking emergency contacts and family reunification plans. **Free:** existing public Preparedness Archive, not unreleased manuscript/card. **Provisional paid candidate:** existing Legacy Triage PDF only; merchant purchase, rights, audience fit, privacy, delivery, refunds and founder authorization remain unverified. Do not activate merchant CTA or promise suitability.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Legacy Triage → paid order | Actual SKU, rights, fulfillment and price unverified | Independent merchant and rights audit before any paid CTA | NOT VERIFIED / HOLD | Founder & Commerce |
| Free archive → optional practical tool | Safety/privacy/usability gates unresolved | Qualified source and printing/accessibility review | NOT APPROVED | Preparedness QA |
| Grok post → free public archive | Published relevant asset_id, rights, tagged actual native-mobile URL missing | TASK-008 existing owner verifies asset and destination; no new Grok task | NO VERIFIED MATCH | Grok / Praxxis |
| Landing → CTA → checkout | No approved congruent offer; mobile and merchant acceptance missing | Review-only CTA copy and instrumented acceptance plan, not deployment | NOT TESTED | Claude / Commerce |
| Verified paid orders → realized net revenue | Provider-confirmed orders, fees, refunds, 7/30-day attribution unavailable | De-duplicate qualified-human sessions and reconcile merchant settlements | NOT COMPUTABLE (not zero) | Commerce / Analytics |

**KPI contract:** net realized USD per 1,000 qualified-human sessions (merchant-confirmed orders less refunds/fees divided by 7/30-day attributed qualified-human sessions × 1,000), with small samples marked; clicks/checkout starts/signups are never equated to sales. No new tracking vendor or script.

**Forbidden:** merges, WordPress/CMS writes, public navigation, publishing, Grok posting/queue replacement, sales/affiliate activation, emails, paid services and QD PASS declarations.
