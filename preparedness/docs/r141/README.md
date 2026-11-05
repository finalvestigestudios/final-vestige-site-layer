# R141 — Exact citation-occurrence reconciliation (DRAFT / HOLD)

**Issue:** Preparedness #136; conversion coordination #820/#818. **Parent:** R140 draft PR #1069 at `b7f81c8ad6963b7f44fe8898d6bca12f4c562634`. **Frozen release candidate:** #584 at `ddb3528ba6494dada1fa1c3a142ce746e3a67706`. No merge, public publishing, CMS/nav/homepage, analytics, social, seller, email or affiliate writes. No safety/QD approval.

## Independently observed new source-integrity discrepancy (2026-11-05)

All seven canonical Claude contributor heads still match the exact R140 branch SHAs (0 ahead / 0 behind in fresh GitHub comparisons). Independently fetched the *authentic* before/after bodies for **eight Start/Shelter articles and two Historical Food articles** from frozen RC and contributor commit refs. GitHub returned the exact expected article blob SHAs. Counted literal `{{cite:author-source-id}}` occurrences per *source ID*, not merely total citations or distinct-ID membership.

**New confirmed omission in the R140 summary:** `three-day-kit` drops `start-cdc-power-outage` **1 → 0** in the contributor copy, but R140's frozen `removed_source_ids` listed only `start-fsis-emergency-food`. That earlier summary was not an exhaustive list of dropped source IDs. **Do not silently edit R140**: its source manifest has Git blob `a839c53bc3b6f7c72c7eaf1c901edae02664007e`. R141 pins that identity, records the newly observed omission explicitly and holds review.

**Additional high-stakes citation movement concealed by aggregate counts:** `home-fire-escape-plan` drops `shelter-nfpa-high-rise` **2 → 0**, `shelter-usfa-high-rise-handout` **3 → 0**, `shelter-usfa-escape-grid` **1 → 0**, *while* increasing the occurrences of `shelter-nfpa-escape` **20 → 21**, `shelter-usfa-high-rise` **2 → 3**, and `usfa-fire-escape` **10 → 11**. The net change of three citations does **not** establish equivalent source support. Qualified fire-safety and editorial review is required.

**Historical Food S-7:** `pemmican-and-dried-meats` changes **7** citations from `hist-food-nchfp-jerky` to `nchfp-jerky`; `pioneer-travel-rations` changes **1**. This is **8 source-identity retargets despite no total citation loss**. The authors' separate source interpretations and safety limitations remain independent until review. Identical URLs are not equivalent claims.

**Evidence scope:** 14 SHA-different contributor article pairs from R140; **30 exact source-ID occurrence-count changes** in the new docket, across **8 articles**; **6 others** have unchanged source counts but changed exact blobs/prose. The eight Start/Shelter substitutions collectively shorten approximately 3,245 whitespace-counted words and remove a **net 29 citation tokens**. Sources for generator/CO, emergency food, chemical evacuation, family reunification, mobility and high-rise fire require priority review. Neither the presence nor disappearance of a citation establishes the advice's safety.

## Engineering and exact commands

R141 adds **three additive files** only:

- `preparedness/docs/r141/citation_occurrence_docket.json`: 14 article identities and 30 per-source old/new counts; `UNREVIEWED_HUMAN_REQUIRED`.
- `preparedness/tools/r141_citation_delta_gate.py`: read-only Git-blob-pinned manifest and exact per-source occurrence validator. Detects duplicate/malformed IDs, missing/mismatched articles, source-identity substitution, aggregate-cancellation, review-status forgery, symlinks and altered bytes. An optional separately staged contributor checkout verifies all 14 before/after exact files. Never grants an approval or changes draft data.
- `preparedness/tests/test_r141_citation_delta_gate.py`: isolated adversarial/fixture suite, including individually discovered mutation cases for all 14 article records and a regression for the R140 missing identity.

On a **trusted, complete checkout**, run:

```sh
python -I preparedness/tools/r141_citation_delta_gate.py --manifest preparedness/docs/r140/branch_intake_evidence.json --docket preparedness/docs/r141/citation_occurrence_docket.json --root . --report /tmp/r141-citation-audit.json
python -I -m unittest discover -s preparedness/tests -p 'test_r141_citation_delta_gate.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

To compare exact staged contributor bytes, add `--contributor-root /path/to/isolated/staged-14-article-contributors` (same relative folder structure, never a shared worktree). A structurally matching run is **NOT** a source review, medical safety review, qualified QD PASS, merge recommendation or WordPress publication authorization. R133–R140 remain stacked. Full 35-article/2,000-citation custody and 32 shared-source link/claim reviews remain independently gated.

**Executed locally:** isolated R141 Python **76/76 tests passed**, plus Python compilation, with locally tested source/test exact Git blob identities matching the submitted files. **Separately verified:** real GitHub 14-row R140/R141 crosswalk (one documented legacy omission), and ten authentic source article pairs via connector. **Not executable in this environment:** the authenticated full repository checkout, native build/validation, end-to-end 35-article test suite, independent browser QA and qualified human QD. A failed pre-runner workflow does not count as code-test failure or success.

**Independent review dependencies unchanged:** PR #157's household electrical drill and medication language need qualified adjudication; PR #169 still has one shared-directory fixture and separate PR #973 holds its isolated test fix. Do not merge or alter them here. Homepage #49/#604 and other production owners remain independent.

## Conversion-first, scoped and unlaunched

**ONE intent:** households developing emergency contacts, school pickup and family reunification plans. **Existing proposed free guide:** `household-emergency-plan` (authentic but DRAFT / safety review pending). **Existing practical download:** family reunification card (DRAFT; print, privacy and accessibility QA pending). **Existing matching paid SKU:** no authenticated, FV-owned, rights-cleared, currently purchasable Preparedness pack has been proven. **Paid CTA: HOLD**; do not invent a price, promise a pack or revive retired water products.

**Unpublished CTA draft:** “Plan who you'll contact, where you'll meet and how you'll reunite. Read the free household emergency plan and use the optional printable card.” Safety guidance must remain free and available without email or purchase.

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / ACCEPTANCE EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- |
| Authenticated FV Preparedness SKU → actual purchase | No verified rights-cleared matching product/price/fulfillment | Verify merchant listing, checkout, delivery entitlement and refunds **before** any paid promotion | HOLD / UNVERIFIED | Growth / Claude |
| Free plan → guide reader | R141 article drift, #157 safety wording, unreviewed sources, QD missing | Keep full RC, trace source IDs and obtain qualified source/safety decisions | Citation docket BUILT, 76 tests PASS; release HOLD | Preparedness / qualified QA |
| Grok Preparedness social asset → guide | TASK-008 lacks confirmed actual Preparedness asset_id, post URL and approved landing URL | Grok/Praxxis verify a real published asset and canonical destination; no queue edits | UNVERIFIED | Grok / Praxxis |
| Reader → family card | Private household data leakage, accessibility, printing and download reliability not independently tested | Staged phone/keyboard/print/no-email check; no PII in URLs, UTMs or analytics | NOT TESTED | Preparedness / Site QA |
| Purchaser → realized net revenue | No verified attributable merchant paid orders, fees or refunds | Reconcile 7/30-day unique human sessions → CTA → settled orders (not clicks) → refund/fees → realized net per 1,000 | NOT COMPUTABLE | Growth / Claude |

**Current Grok TASK-008:** content/distribution owned by Grok, independent review by Praxxis; no verified Preparedness-specific published asset/destination or paid-SKU attribution in the shared handoff. Do not add tracking scripts, publish social/email posts or infer purchases from pageviews.

## Remaining release gates

Adjudicate the exact disappeared and retargeted citations with qualified source readers; review #157 and #169/#973; execute full native suite and WordPress-ready *local draft* build; verify all 35 pages, 2,000 occurrences, 244 sources, 32 shared-source groups, unique routes, safety-state custody, mobile/print/privacy, reviewer provenance and independent QD; obtain separately documented founder release approval. **Until then: DRAFT / HOLD.**
