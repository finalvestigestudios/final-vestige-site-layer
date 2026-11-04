# R120 — citation-occurrence and nearby-context reconciliation — DRAFT / HOLD

2026-11-04. Owner lane: Preparedness source/citation integrity only, Issue #136; conversion coordination #820 and business charter #818. Nothing in this evidence pack authorizes merge, publication, safety approval, paid offers, or QD PASS.

## New exact-object engineering evidence

The 35-article roster is NOT equivalent to 35 changed article bodies. Original and release candidate have 35 paired body/metadata routes. **22 article body blobs are identical**. **13 article bodies differ**, and R120 independently retrieved both versions of each (26 GitHub file reads). All 26 blob IDs matched the R117 frozen catalog exactly.

Frozen original commit: 980659031b0bd5787a326d38698138c1e8cad82d.
Release candidate #584: ddb3528ba6494dada1fa1c3a142ce746e3a67706.
R117 snapshot manifest blob: 1427fbbdea940a339b57a36dda04e7dd2e8d29ab.

Both parts of the new custody dossier are in preparedness/docs/r120. They record source-ID occurrence deltas, approximate visible words, ordered citation-ID sequence changes, and up to five nearby before/after text excerpts for changed citation contexts. Excerpts are reviewer navigation aids, not source or medical safety approvals.

| Observed measure from changed original/candidate bodies | Result |
|---|---:|
| Changed bodies inspected at exact immutable objects | 13 / 13 |
| Identical bodies retained, unchanged | 22 / 22 |
| Articles with source-ID citation occurrence-count changes | 10 |
| Same-ID citation occurrences with different nearby extracted text | 62 |
| Sum of approximate word-count changes | +4,347 |
| Sum of citation-token changes | +48 |
| Independent qualified source/safety reviews completed here | 0 |

A positive aggregate word count does not guarantee retention of *individual* warnings, source relevance, or meaningful article depth. Near-citation text extraction is a heuristic: do not automatically infer from a changed context that the claim is more correct or less correct.

## Highest-priority source and emergency-warning reviews

Household emergency plan: +240 approximate words and NO citation-count change. This is a meaningful example of why citation counts alone cannot validate a safety rewrite; QA #157 and RC use different wording around a main-breaker drill. Human compare all versions.

Three-day kit: +464 words, +4 citations, 11 same-ID changed nearby contexts; reconcile medicine storage and emergency-use qualifiers from #157 before approval.

Home fire escape plan: +505 words, +3 citations, 18 nearby changed contexts; reconcile high-rise warnings, fire-service sources, and exit-plan caveats.

Shelter or evacuate: +749 words, +9 citations, 9 context changes; qualified hazard-specific review required.

Family communication plan: +534 words, +7 citations, 5 context changes; verify source scope for school pickup, reunification and vulnerable households.

Outage heat/cold/generators: +264 words, +5 citations, zero same-ID context changes detected, but new source and uncited instructions still require review.

Pickling/fermentation: +362 words, +7 citations, 5 context changes; historical documents cannot establish current food preservation safety.

Pioneer supply chains, root cellars, navigation before GPS, sanitation before germ theory, go-bags and practical accessibility remain UNREVIEWED. R117 contributor-only Pemmican/Pioneer Rations source-ID discrepancies (nchfp-jerky vs hist-food-nchfp-jerky) remain unresolved and independent of this 13-body RC comparison.

## Source safety gate and tests

Files on the isolated branch:
- preparedness/docs/r120/CITATION_CONTEXT_CHANGED_BODIES_PART_A_HOLD.json
- preparedness/docs/r120/CITATION_CONTEXT_CHANGED_BODIES_PART_B_HOLD.json
- preparedness/tools/r120_citation_context_gate.py
- preparedness/tests/test_r120_citation_context_gate.py

The Python validator checks the 35 paired routes; all changed body blobs must appear exactly once across both frozen dossiers; original and candidate Git identities must match R117; count and source-ID deltas must conserve total citation counts; no duplicate/foreign rows, malformed contexts, illegal QA upgrades or stale heads. Output state is always HOLD.

**57 synthetic/adversarial Python tests PASS** in an independent local prototype (including 13 missing-body and 22 unchanged-body contamination mutations); Python compilation PASS. The exact committed source/tests, native validation/build, full suite and mandatory Actions integrity have NOT been executed in a full repository checkout. Do not call them passed. An additional independent JS comparison of the committed JSON against R117 found all 13 Git-blob pairs and citation-count conservation consistent.

When full checkout available, run:
    python -I preparedness/tools/r120_citation_context_gate.py --snapshots preparedness/docs/R117_NINE_SNAPSHOT_GIT_OBJECT_CUSTODY_HOLD.json --part-a preparedness/docs/r120/CITATION_CONTEXT_CHANGED_BODIES_PART_A_HOLD.json --part-b preparedness/docs/r120/CITATION_CONTEXT_CHANGED_BODIES_PART_B_HOLD.json
    python -I -m unittest discover -s preparedness/tests -p 'test_r120_*.py' -v
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

## Independent QA and other lead heads checked on Nov 4

Seven contributor SHAs were directly read from their refs and MATCH R117: food f911ff7a655de8d81535ea86ec3d65a49ee76648; health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17; historical-field 4e5caf812727953aa45e3bda2d382f2c67b6a09c; historical-food 67e116e536c7410bed30f8f3b1bb8c166f3c223d; historical-home 7504a5f099594d635e3dd7332a33a2e1346c43a2; shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976; start-here 2122d856fce9f64887c16df3d52e64be9f59a55b.

QA #157 draft at 7d1ae6b8ef93d10cfb6810987672360885e9c1aa changes household plan, three-day kit, start.json, taxonomy and tests; not independently approved. QA #169 draft e9cd7766dac59d47ab467d8945269b9146c2aef5 fixes one synthetic source test by copying to a temporary tree but its OTHER test still writes _dup_test.json into shared sources/fragments. Owner must isolate remaining fixture; do not edit PR #169 from this lane. Home lead PR #49 head 10495883299d53596992c26a8987f629b2904670; flagship #604 bdf01b4a3e13fd6179ae9e847c9d4429bbe16176. Unchanged/untouched during read-only inspection.

## Conversion-first acceptance — ONE relevant audience, no unverified sell button

Audience: households needing emergency contact, school pickup, and reunification plans. Existing original source-backed FREE editorial guide: A Household Emergency Plan That Actually Gets Practiced. Proposed /preparedness/household-emergency-plan/ is UNVERIFIED LIVE and safety HOLD. All essential safety guidance stays free and ungated.

Inert CTA copy for the eventual reviewed free guide: “Make a plan your household can use. Read the free, source-linked household emergency planning guide.” Do NOT publish or link to an unverified destination.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE/EXPERIMENT / acceptance | EVIDENCE | OWNER |
|---|---|---|---|---|
| Currently purchasable FV-owned practical pack → confirmed paid order | No authenticated SKU, rights, price, delivery, terms or merchant proof | Authenticate an existing rights-cleared relevant offer; test purchase, download and refund handling in authorized environment. No speculative pack or checkout CTA. | NOT VERIFIED | Growth / Claude |
| Free guide → reader trust | 35 changed protected paths plus citation context, 30 shared-source groups, 15 safety exceptions, 22 editorial decisions, five unfinished tools | Independent source adjudication, warning/caveat and qualified emergency review; preserve 35 original article routes and reading depth | HOLD | Preparedness / Independent QA |
| Grok asset → guide | TASK-008 has no verified appropriate Preparedness asset ID/post URL | Grok/Praxxis supply real immutable asset ID, platform post link, lawful source, caption/bio route, UTM campaign/content; do not invent IDs or change their queue | UNVERIFIED | Grok / Praxxis |
| Relevant CTA → optional paid pack | Guide unpublished; product and checkout unverified | Only after approval: staged 360/390/768/1440 px, keyboard access, transparency, optional offer, fulfilled delivery; no safety-content email gate | NOT TESTED | Claude / Site QA |
| Qualified sessions → confirmed orders → realized net | No matched qualified-human denominator, merchant orders, fees or refunds | Reconcile first-party events and source-confirmed settled orders/refunds/fees at 7/30 days; tiny-sample warnings; never label clicks/leads as sales | N/A | Growth / Claude |

Founder owns publication/spending approval. Claude owns production website/analytics; Grok owns content and distribution; Praxxis owns TASK-008 coordination. No WordPress, CMS, nav, tracking, email, merchant, social, article-body or homepage writes on this branch. Release: HOLD pending full checks and independent QD.
