# R142 — Citation-to-passage custody during contributor reconciliation (DRAFT / HOLD)

**Scope:** Preparedness Archive #136 ONLY; business coordination #820 / charter #818. **Parent:** R141 draft #1076 at `b2cac019fb9c85e8555ff4cf0c24aa996a415041`. Frozen 35-article candidate: `ddb3528ba6494dada1fa1c3a142ce746e3a67706`. The source snapshots and their author-specific interpretations are not merged, rewritten or approved here. No WordPress, CMS, navigation, homepage, analytics, email, commerce, affiliate, social, release or publishing writes.

## New independent inspection — 2026-11-05

Fetched both exact SHA-pinned article bodies from GitHub for **all 14** changed contributor/candidate pairs across **all seven** canonical Claude clusters (28/28 blobs matched R140). Each current contributor branch compared IDENTICAL (ahead=0, behind=0) with the exact R140 pin:

| Cluster | Exact head | Existing article changes |
|---|---|---|
| start | `2122d856fce9f64887c16df3d52e64be9f59a55b` | 4 |
| shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` | 4 |
| food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` | 0 in R140 drift manifest, still divergent history |
| health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` | 0 in R140 drift manifest |
| histfood | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` | 2 |
| histhome | `7504a5f099594d635e3dd7332a33a2e1346c43a2` | 2 |
| histfield | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` | 2 |

A separate **provisional** paragraph-block comparison (JavaScript inspection; distinct from the Python implementation, not a native 35-article execution) found that candidate passages supporting citations are no longer exact textual matches to contributor passages for **72 old citation-context occurrences**, with **43 contributor-only context occurrences** across the 14 pairs. Eight Start/Shelter articles account for 64 old-only and 35 new-only occurrences; two Historical Food jerky-source identity retargets account for 8/8. The remaining four Historical Home/Field pairs and two Start articles have changed Git bodies but no citation-bearing paragraph differences by this approximate block comparison. These counts measure **literal context drift, not factual mistakes, safety failures, unique lost sources or a number of affected claims**. An independently executed exact R142 parser may produce different counts; do not present the provisional figures as the release-gate output.

The actual source losses remain per R141 docket: `start-cdc-power-outage` removed from `three-day-kit`, separate high-rise fire source IDs replaced/dropped in `home-fire-escape-plan`, and eight `hist-food-nchfp-jerky` to `nchfp-jerky` retargets in Historical Food. No same-URL equivalence or safety determination follows from this.

## New engineering

`r142_citation_context_gate.py` compares source identities **and** SHA-256 hashes of the normalized surrounding reader-visible paragraph/list/heading/table text. An unchanged source count can still be flagged if a claim-bearing passage changes. It reports old-only and new-only occurrences with passage ordinal, source ID and 220-character excerpt, so a qualified source reader can examine exactly what moved. It requires R141's immutable R140 manifest pin, R141 docket, and SHA-matching **both** candidate and staged contributor article files; it refuses missing/changed bytes, stray tokens, malformed IDs, citations in explicit hidden/script/template/comment markup, citations outside recognized visible blocks and forged approvals. It cannot infer CSS-class/browser-computed visibility; staged independent browser QA remains required. It never changes articles.

**Execution:**

```sh
python -I preparedness/tools/r142_citation_context_gate.py \
  --manifest preparedness/docs/r140/branch_intake_evidence.json \
  --docket preparedness/docs/r141/citation_occurrence_docket.json \
  --rc-root /trusted/exact-rc-checkout \
  --contributor-root /trusted/isolated-staged-14-authors \
  --report /tmp/r142-article-passage-differences.json
python -I -m unittest discover -s preparedness/tests -p 'test_r142_citation_context_gate.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

Staged contributor root must contain only the selected exact source versions at `preparedness/content/articles/<slug>.body.html`. Do not install them over the trusted RC. Empty or missing input is a blocker; exit 0 from R142 means an **evidence packet was generated**, not editorial approval, QD, source correctness or readiness to publish.

**Executed in local isolated environment:** 75/75 R142 synthetic/adversarial Python tests PASS and syntax compilation PASS. **Actual repo execution / native validation / build / repository-wide suite / WordPress draft / independent QD:** NOT EXECUTED because a complete authenticated local checkout is unavailable and GitHub DNS fails. This limitation is not a code-test pass/fail. No GitHub Actions result is represented as an executed Python test. Never promote an automatic context-difference detector to medical, electrical, fire or food-safety signoff. PR #157 and PR #169/#973 must remain separate for independent qualified review.

## Conversion-first acceptance (not activated)

**One audience:** households preparing emergency contacts, school pickup and reunification. Proposed authentic free guide `household-emergency-plan` remains DRAFT / source and safety hold. Optional family-reunification printable remains DRAFT / mobile, privacy, print and delivery untested. **No matching owned, rights-cleared, currently purchasable Preparedness toolkit is authenticated. No paid CTA is eligible.** Do not promote retired water products. Proposed unlaunched copy: “Plan who to contact, where to meet, and how to reunite. Read the free household emergency plan; an optional printable card can help you practice.” No email gate for emergency instructions.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE/ACCEPTANCE EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Real FV-owned Preparedness digital pack → settled order | Missing authenticated, rights-cleared matching Payhip SKU and fulfillment | Verify price, terms, buyer entitlement, actual checkout, usable file delivery, refunds before rendering any paid CTA | HOLD / UNVERIFIED | Growth / Claude |
| Free household plan → qualified reader | R140/R141 text and citation drift, independent #157 safety wording | Preserve exact RC, run R142 paired-passage audit, specialist review and 35-article native tests | R142 BUILT + synthetic tests; actual release HOLD | Preparedness / qualified QA |
| Grok published asset → approved free guide destination | TASK-008 has no verified Preparedness asset_id and permitted link placement | Reconcile actual post permalink, asset_id, CTA/UTMs and destination with Grok/Praxxis, no queue change | UNVERIFIED | Grok / Praxxis |
| Guide → optional family-reunification printable | No 360/390 mobile, keyboard, printing, private-data and delivery evidence | Test staged page, no PII in URL/UTM/analytics, printable works without email | NOT TESTED | Site QA |
| Customer → realized net revenue / 1k qualified human sessions | No reconciled attributed settled orders or qualified denominator | Merchant-confirmed paid orders less refunds/fees by 7/30-day cohort; distinguish outbound click, checkout intent, lead from actual settled purchase | NOT COMPUTABLE | Growth / Claude |

Release governance: **DRAFT/HOLD**, 32 shared-source groups still unreviewed, independent QD NOT APPROVED. Claude owns production engineering, Grok owns social content/distribution, Praxxis owns independent content QA, founder owns release and spend approvals. Do not send email or activate any offer, analytics script or public CTA.
