# Media-recovery exact-source coverage reconciliation — 9 Nov 2026 Pacific / 10 Nov UTC

**DRAFT / NO MERGE, DEPLOY OR PRODUCTION CMS EDIT.** This document summarizes a read-only, repo-contained research inventory. It does **not** claim image restoration, visitor-browser testing, copyright clearance, actual HTTP statuses or measured speed improvement. Homepage design remains with the interim lead; Site QA PR #154 owns the existing logged-out browser/CDP collector.

## A high-value correction: 167, not the naive 169

The prior [93-unique exact-source reconciliation](../qa/media-recovery/coverage_93_exact_reconciliation_20261109.json) covered 93 unique offsite source slots from **96** research records, including three prior overlaps (418:1, 418:2, 418:5). Since that reconciliation, **12** additional article-level reports were written (Cherry Mine, Mann Gulch, Lady Be Good, Texas City, New London, AZORIAN, Franklin, Antikythera, Herculaneum, Thresher, Eastland, Iroquois).

Those 12 add **76** literal source-evidence rows, all cross-checked by both **post:slot** AND the **exact frozen source URL** against the 288-slot census; no mismatches and no duplicates *within* these 12 batches. But **Eastland 214:0 and 214:4** already existed in the earlier 93-slot register. Deduplicating yields **93 + 76 − 2 = 167 unique externally hosted origin slots with some research**, leaving **121 of 288 pending**. The 167 research slots constitute **58.0%** of the frozen upstream-external inventory, **not** 167 restored/healthy images. The ledger includes **172** research evidence records (96 prior + 76 new); 172 is not a unique-image count.

The historical October 30 published-post snapshot remains **61 posts / 355 raw inline image slots / 288 offsite upstream image slots / 80 upstream hosts**. The prior 286 directly external stored URLs plus two external origins behind Jetpack delivery reconcile to 288; do not merge these figures with the newer **66-post / 361-image** snapshot.

**Machine-readable output:** [288-row register with exact published URLs, source origin, per-batch Git SHA and observation, archival candidate/rights/conditional 960px fields, and explicit null guest evidence](../qa/media-recovery/coverage_167_exact_pr1703_20261110.json). Each of the 121 outstanding positions remains visible with its exact URL and PENDING status; the 167 have detailed source evidence. Rights, full-resolution scene/crop match, caching and WordPress publication are all false/held.

## Remaining research queue, without displacing actual missing-image verification

**First priority stays Site QA's six suspected visitor failures**, in this order: `285:5, 285:2, 287:5, 418:1, 418:2, 407:1`. The following labels must remain separate: independent web-retriever display/error; actual source-origin HTTP status; real logged-out Chromium `currentSrc`, `naturalWidth`/`naturalHeight`, cold uncached response and encoded bytes; and editorial rights/source integrity. A retriever 403/404/502 is NOT an origin/guest 403/404/502.

Among the **121 without dedicated source research**, the largest unresolved hosts are **commons.wikimedia.org (57)**, **upload.wikimedia.org (8)**, **cloudfront-us-east-1.images.arcpublishing.com (4)**, **objects.lib.uidaho.edu (4)** and **tile.loc.gov (3)**. Largest still-unresearched single posts are Courrières **#425 (8)** and **#221, #253, #255, #256, #257 (7 each)**. Research these after the six P0 browser adjudications; do not mass-rewrite blocks just to reduce offsite counts.

## Rights / performance release gate

Every source-candidate mapping requires item-level creator/owner and license documentation, original scene/crop identity and correct historical chronology, attribution record, archival metadata, **≤960px without upscaling**, small-label readability (especially maps), then separate approval before creating or caching any new binary, uploading WordPress media or staging a reversible block change. Government or Commons hosting alone never authorizes republication. No image binary was downloaded for this reconciliation.

The historical **42 allegedly broken originals** are **not** confirmed by a genuine visitor-browser capture. The suggested **76% image-weight saving is not measured**. A proper comparable baseline/staging cold-guest CDP image-slot pair needs same photo/slot semantics, source provenance, uncached completed response, transferred *encoded* network bytes, actual decoded dimensions, visual/ALT fidelity and rollback. Do not substitute stored media size for visitor bytes or a different archival photo for compression.

The **15 WordPress originals strictly >1,500,000 bytes** total **47,096,779 stored-original bytes**; **11** are inline in the current expanded 66-post census, representing **38,480,915 stored-original bytes**. Those are not measured network transfers. The five no-subsize 1672×941 PNGs, Malbone pair, Vasa Jetpack transformations and Halifax detailed map remain their own approved-after-rights performance lanes, subordinate to broken-image restoration.

## Engineering / test evidence

- Ledger: `qa/media-recovery/coverage_167_exact_pr1703_20261110.json`, Git blob `d2337c38aa15903b11b4aae02a2a1f09534cb752`.
- Fail-closed validator: `qa/media-recovery/validate_coverage_167_exact_pr1703_20261110.cjs`, Git blob `a30302918c22db5b4bc2931c184790fabe3882ce`.
- Adversarial Node test definitions: `qa/media-recovery/test_coverage_167_exact_pr1703_20261110.cjs`, Git blob `00e40055e801e09e27983f59f596cdb555c56a0e`.
- Full in-memory replay against the exact 288 source census and all 12 newer batch payloads: **PASS**, 167/288, 121 pending, 172 evidence, two known Eastland overlaps, no literal URL mismatch.
- **25/25 V8-executed Node-compatible test callbacks PASS**. The 26th definition (cryptographic recomputation of 14 source Git blob SHA values) was **not run under V8**, but all **14 GitHub-reported blob identities matched** their recorded pins. Native `node --test qa/media-recovery/test_coverage_167_exact_pr1703_20261110.cjs` and `node qa/media-recovery/validate_coverage_167_exact_pr1703_20261110.cjs` still require execution in CI/native Node. No claim that native CI or Chrome ran.

**Outcomes:** 74 newly reconciled unique research positions beyond the previous 93, not 76; **0 confirmed new browser failures, 0 fixes deployed, 0 WordPress changes, 0 third-party downloads/caches, 0 homepage changes, $0 subscription spend**. This research should be treated as staging intelligence, not publication approval.
