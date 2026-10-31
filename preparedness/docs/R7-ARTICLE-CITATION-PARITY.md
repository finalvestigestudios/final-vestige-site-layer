# R7: Full 36-draft citation and reading-depth scan — HOLD

**Exact input:** `903e2ce817659bf3d4e5cf7fa44cdda2682a17aa` (R6). The authenticated GitHub connector fetched **all 72 actual article/tool content files**, eight at a time (five bounded batches). Every returned Git blob matched the stored immutable evidence lock; a simple independent text count found that **all 35 long-form articles exceed 1,800 words** (shortest approximately **1960** words) and the 556-word water-planning tool exceeded its 450-word threshold. This is **not** a run of the native Python parser/build.

### Measured audit results

| Fact | Count |
|---|---:|
| Article bodies + metadata | 35 + 35 |
| Water planner body + metadata | 1 + 1 |
| Unique body citation/source ID relationships | **367** |
| Matching article-specific nonblank `source_use` entries | **367** |
| Missing, extra or blank `source_use` entries | **0** |
| Drifted Git blobs versus frozen original | **0** |
| Status.publish != draft | **0** |
| Existing safety states | {"pending":30,"approved":2,"not-required":4} |

Each article/token check was performed against the actual HTML and its own metadata at the **same exact source SHA**; using another contributor's evidence is still forbidden by the existing crosswalk. The two `approved` metadata states reflect earlier workflow labels; they are **not qualified safety clearance**. Four `not-required` states belong to historical pieces under existing taxonomy rules; no live publication is granted.

The machine-readable detail is `R7-ARTICLE-CITATION-PARITY.json` and lists each exact slug, approximate word count, citation count, and pre-existing safety label. It complements `R7-FROZEN-SOURCE-CUSTODY.json` which independently compared 224 contributor source rows and 30 URL-collision groups.

### Remaining holds

The external webpages/PDFs are **not** independently verified by these tests; every claim still requires factual/source reading-depth review, and consequential water/food/medicine/infant/fire/CO advice needs qualified safety assessment. The 30 shared-URL groups remain pending; full native `evidence_freeze.py`, `validate.py`, `build.py`, full article unit tests, hosted green CI and QD are not complete. There were **no CMS, navigation, email, homepage or live public writes**. Publication is not authorized.
