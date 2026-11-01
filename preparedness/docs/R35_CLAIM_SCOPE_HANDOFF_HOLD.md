# R35: Evidence-bound human-review intake — RELEASE HOLD

**Preparedness Issue #136 | Draft PR only | No WordPress, public site, navigation, CMS or publish writes.**

This increment adds `preparedness/tools/citation_review_handoff_gate.py`, a read-only, deterministic transfer format for human review. Its mandatory invocation is inside the existing **thirteenth private source/citation stage** of `citation_fallback_review_gate.py`, after R25, R31, R33 and R34 complete. Missing/symlinked code fails closed. This is **not a human evidence check, approval engine, or a claim that any emergency advice is medically safe**.

## Exact frozen reviewer workload
- 35 original article drafts and one water-planning tool; zero original content, source inventories, taxonomy, safety states or contributor notes edited here.
- 1,959 **distinct citation-occurrence intake forms**, one per exact source-bound claim reference/Unicode offset.
- 367 **distinct original source-use scope intake forms** with full unabridged contributor source records, reading-depth `supports`/notes and article-specific `source_use` explanations. No URL-based de-duplication.
- 43 additional explicit cross-cluster/base-source fallback scope review items.
- All 30 shared-URL inventory groups remain **unreviewed**. Separate coordination forms cover only the shared-source URLs actually represented in the 367 cited source-use cards; do not confuse that subset with the 30 globally unresolved groups.
- Source-use and claim form IDs are deterministic SHA-256 values linked through the signed R34 packet and its R25/R33 ancestry. These digests detect accidental stale/substituted evidence when compared to the trusted Git checkout; they are **not third-party human signatures**.

Every reviewer field is initially null; all reviewer states are `NOT_STARTED`; machine `release_state=HOLD` and `may_publish=false`, with independent QD, qualified safety, source-accuracy and human-review flags explicitly false. Even successful machine tests cannot flip those flags. A submission of findings needs its own separately governed independent human evidence process; this change does **not** accept self-attested approvals or write review data.

## Private read-only commands

```bash
python -I preparedness/tools/citation_review_handoff_gate.py --format summary
python -I preparedness/tools/citation_review_handoff_gate.py --format json
python -I preparedness/tools/citation_review_handoff_gate.py --format ndjson
python -I -m unittest discover -s preparedness/tests -p 'test_r35_*' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

JSON/NDJSON go to **stdout only**; callers should keep exports private and must not assume a printer, CMS integration or public export is authorized. The GitHub Actions private preflight runs the mandatory thirteenth stage; it should remain a HOLD receipt even when green.

## Independent human work still required

Human reviewers must visit the actual sources, note verification and source access dates, locate every supporting passage, decide whether it supports the specific claim in context, reconcile 43 fallback scopes and all 30 global shared URL groups without discarding different contributor reading scopes, and flag consequential water/food/fire/medical guidance for qualified specialist assessment. Resolve source-README versus repeated contributor-ID provenance, food origin alias, rendered browser/print/accessibility QA and independent QD on the exact release head. No machine test in this PR replaces any of those gates.

Reviewer forms are *empty assignments*, not completed reviews, medical recommendations, citations proving assertions, editorial approval, or permission to publish. The Preparedness release remains **HOLD**.

## Governance and coordination

Seven frozen Claude cluster branches, QA #157, synthetic fixtures #169, homepage #49 and flagship #254 must be checked by exact current SHA each run. The two QA PRs remain independent unmerged drafts and are not a shortcut to QD approval. This PR is stacked on R34 and must not be merged, deployed, or used for WordPress writes without separate authorization.