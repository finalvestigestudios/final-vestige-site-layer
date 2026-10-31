# R8 exact-source inline-citation census (DRAFT / HOLD)

The authenticated GitHub connector read **all 36 article/tool HTML bodies and all 36 matching metadata JSONs**, using a stable exact Git source commit 78efa0eb06854707eb78607bb11306803a86958d. Four bounded fetch batches each validated the downloaded blob SHA against the Git tree. **72/72 source files matched**, and every article was still an unpublished draft. Inline literal citation tokens were counted in each body, deduplicated per article and reconciled against that article's own source_use map. This is a machine-only inventory and not an independent content/source-truth review.

## Actual new finding

**1,959 visible citation-marker occurrences** are distributed among the 35 article bodies and one water-planning body. They correspond to **367 unique article–source relationships**. That is approximately **5.34 individual invocations per source-use relationship**. R7's source-use parity and existing reviewer packets operated at the pair level. They did not prove that every distinct sentence invoking the same source was supported by a correctly inspected source passage. This is why the new per-occurrence reviewer queue matters.

Most-cited draft: **outage-heat-cold-generators** at **116 occurrences / 16 distinct article–source pairs**. Other consequential reviews include **water-purification-through-history** (76/14), **three-day-kit** (75/16), **pressure-canning-low-acid** (74/17) and **safe-jerky-dehydration** (71/11). The machine identified **zero source-use parity discrepancies** across all 36 objects. This does **not** establish factual or safety correctness.

The machine census is source-pinned in R8-INLINE-CITATION-CENSUS.json with per-file blob SHAs and individual counts. Its **1,959** occurrence total is now an explicit build-time baseline in claim_occurrence_audit.py; any drift should require source and reviewer authorization, not silent acceptance.

**80 original synthetic tests + one new occurrence-baseline test = 81/81 passed** in local Python against byte-identical committed source and tests. Full GitHub corpus execution, complete native validator/build suite, human verification of external source pages, human reconciliation of 30 repeated URL groups, qualified medical/food/water/fire/CO reviews, hosted CI and independent QD remain **NOT RUN / NOT APPROVED**. All 35 articles and the water planner remain drafts, release HOLD, no WordPress/nav/homepage writes.
