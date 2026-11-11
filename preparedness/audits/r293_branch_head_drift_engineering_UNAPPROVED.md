# R293 — Live Claude Contributor Head Drift Admission / Unapproved

**Date:** 2026-11-11 PT. **Scope:** Preparedness Archive source/citation integration only. **Issues:** #136, #820, #818. **Release:** DRAFT / HARD HOLD / NEVER AUTO-MERGE.

## Why this changes the integration plan
Fresh GitHub `compare_commits` on 2026-11-11 compared each named Claude branch **against its immutable R200 frozen SHA**. Previous reports said 7/7 identical; at this observation only **2/7 are identical and 5/7 changed**. The frozen originals themselves are not corrupted. The stored evidence is a point-in-time comparison; it cannot establish live status after capture. `r293_branch_head_drift_hold.py` validates seven exact branch/ref pairs, status/count consistency, bounded changed-file paths and conservative output flags. It does not fetch GitHub or authorize publication.

Source-of-truth JSON: `audits/r293_live_contributor_branch_crosswalk_UNAPPROVED.json`, GitHub compare baseline vs each branch HEAD. 23 changed-path observations; seven articles affected.

| Contributor | Frozen | Observed head | Comparison | Reconciliation class |
|---|---|---|---|---|
| start | `2122d856` | same | identical | No delta |
| shelter | `5daeaf2d` | same | identical | No delta |
| food | `e9cd7766` | `f911ff7a` | diverged 1/1 | Docs/tests only; do not conflate QA #169 with Claude branch |
| health | `d2212d0c` | `d5ef5baf` | ahead 1 | Docs only |
| hist-food | `2acf65ca` | `67e116e5` | ahead 1 | Two bodies/metas, one fragment; citation-source identity change |
| hist-home | `f654e600` | `7504a5f0` | ahead 2 | Three bodies/metas, one fragment; newly cited historical sources |
| hist-field | `a5ce8a62` | `4e5caf81` | ahead 1 | Two bodies, one meta, one fragment; new primary-source references |

**Read-depth and citation deltas checked from exact frozen/live Git blobs (review evidence, NOT human source verification):** hist-food pemmican 2415→2415 whitespace-word tokens, 46→46 cites; pioneer rations 2352→2352 tokens, 39→39 cites, but both change `hist-food-nchfp-jerky` to `nchfp-jerky`. Hist-home: pickling 2391→2756, 42→49 cites; root cellars 2434→2801, 37→42; sanitation 2646→2680, 47→48; source fragments add `hist-home-msu-simmons-1798` and `hist-home-wellcome-chadwick-1842`. Hist-field: pioneer supply chains 2790→3151, 57→63 cites with `hist-field-ia-hastings-guide` and `hist-field-oac-breen-diary`; navigation before GPS 2902→2902, 47→47, but bytes changed. **Word counts and citation counts cannot prove claim fidelity or suitability.**

## Integration hold requirements
- **No automatic cherry-pick.** For these seven changed articles, compare frozen R200, current integrated 35-article collection and moving contributor head; preserve every citation ID, distinct source reading scope, source register provenance, reading depth, meta safety state and canonical URL unless reviewed explicitly.
- Match added source IDs against all eight frozen register origins and R282 three-way provenance ledger. Preserve earlier 21 historical article discrepancies, 32 shared URL groups, 15 duplicate source ID groups and three disputed agency citations. Citation substitutions are not inherently equivalent.
- Qualified human review required for Article #7 chemical contamination and Article #15/Tool #104 school/child privacy, print/no-JS/accessibility. Do not portray historical safety flags as QD PASS.
- Independent QA PR #157 draft/head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`. Synthetic-fixture QA PR #169 draft/head `e9cd7766dac59d47ab467d8945269b9146c2aef5`; one real-tree-writing fixture remains QA-owned. Homepage lead PR #1689 draft/head `f55c36b6598eec558dd8bb24e4c8988becc51be0`. Earlier R292 PR #2050 head `5876206fba65cb3f689d4473f0e14277332a0473`.
- Local repository clone still cannot resolve github.com. No complete native Python build/validate or authentic 41 WordPress drafts executed in this run. Independent release QD: **NOT GRANTED**. No public/CMS/navigation, commerce, social, analytics, emails or spending changes.

## Executed versus proposed tests
An isolated **long-form R293 prototype** in local evidence package was executed with **65/65 offline Python regression tests**; its computed snapshot remained DRAFT_HARD_HOLD (5 drifted clusters, 23 paths, 7 article slugs). The committed compact reviewer gate and its adversarial test file are **BUILT, not separately executed on the authenticated full repository**; do not present those 65 as tests on the committed gate. GitHub CI result is not asserted. No WordPress exporter acceptance is inferred.

## Conversion-first blocker mapping
**Audience:** households planning school pickup/family reunification. **Free:** existing `/preparedness/` public official-resource landing, not an assertion that the original detailed guide is live. **Optional practical tool:** Tool #104 is held for child-information privacy/print/no-JS QA. **Paid:** Legacy Triage Payhip $19 under seller *Vested Wisdom*; FV ownership/license, relevance, checkout/delivery, refunds and merchant settlement unverified. No publishable paid CTA. Grok/Praxxis TASK-008 has no authenticated matching already-posted family-reunification asset ID. Scorecard: unique `utm_content=asset_id` qualified-human sessions → landing → relevant CTA → provider-confirmed lead → independently confirmed paid order → fees/refunds → realized net revenue per 1k qualified sessions (7/30-day cohorts; tiny-sample warning). All numerators/denominators remain **UNVERIFIED / NOT COMPUTABLE**, not zero.

**Owner/next experiment:** Preparedness Integration: three-way source adjudication; independent QA: safety/privacy; Grok/Praxxis: existing asset identity/rights; Founder/Commerce: seller/fit/fulfillment; Claude: approved staging checkout/mobile validation and privacy-safe attribution only after release approvals. Nothing here changes another owner's queue.
