# R365 · Citation-neighborhood custody · DRAFT / HARD HOLD

**Scope:** Preparedness Archive Issue #136 only. Stacked on exact R364 commit `1b4819f82b8c2f7641b9f1774682e8943d6cd6f5`. No publication, CMS/navigation, production engineering, merchant, social or existing Grok queue writes.

## Engineering change
R364 preserves per-ID citation totals and source-use identities, but a citation can be relocated to an unrelated paragraph without changing its count. R365 makes that *claim attachment* visible. A read-only HTML block parser builds SHA-256 fingerprints for each cited claim; source-specific one-to-one pairing first matches identical claims, then compares lexical neighborhoods. Unrelated reassignment fails closed, edited claims and changes to safety modalities/section placement require human review. Hiding citations inside scripts/styles/attributes or malformed citation tokens also fails. Each result is a source-ID/claim-hash docket with no personal data or purported safety review.

**Important limitation:** Jaccard overlap is a *screening heuristic*, not semantic proof or a qualified safety judgment. Legitimate major rewrites may be flagged; qualified reviewers decide scope. A claim being unchanged does **not** verify its factual accuracy or original sources.

## Exact local evidence · 2026-11-14 PT
- 58 new adversarial and synthetic Git-object unit tests PASS; includes 35 synthetic articles plus six synthetic tools; 41-document path closure exercised on disposable local repository only.
- 599 inherited isolated Python tests PASS from R355, R357–R364 bundles, and **52 additional** R356 tests PASS separately = 651 inherited. Total **709** isolated PASS with zero failures.
- Python compilation PASS; exact R365 committed implementation Git blob `4cd8f69ec2d5fbf3d1141cb050170ebc7406e214` and test Git blob `454e6e10db69a09d02a6c79d97a3558050de3564` matched locally tested source files.
- `python -I preparedness/tools/r365_claim_neighborhood_custody.py --repo-root /mnt/data/no_checkout` deliberately returns `INVALID_HARD_HOLD`, process exit 2.
- Full authenticated checkout and authentic 41-document native validation/build/50 WordPress drafts + 50 previews **NOT EXECUTED**. Local `git ls-remote` fails with `Could not resolve host: github.com`. Connector readbacks do not replace a native build.
- Independent safety, child privacy, print, QD and source-link review **NOT APPROVED**. QA #157, fixture #169 and dependent #2205 remain unmerged. No QD PASS inferred from green isolated tests.

## Fresh coordination refs (read only)
Seven Claude clusters + two Shelter continuations were checked at exact GitHub branch heads (see Issue #136 run comment for all nine full SHAs). Independent QA PR #157 head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`; #2205 `bbcf1859768624c611df4abadc564c18247cf32a`; home lead #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0`. None was merged or modified by this work.

## Conversion acceptance (Issue #820)
**Hypothesized high-intent topic:** family-contact and school reunification. The existing public, free, ungated official-source Preparedness Archive and its external agency checklist are the only currently supported destinations. Proposed draft free CTA: **Start With Trusted Preparedness Resources**. Tool #104 remains private/HARD HOLD for child privacy, safety wording, scripts/no-JS and print questions.

No authenticated rights-cleared **payable** Preparedness SKU, delivery/refund policy, merchant settlement, genuine matching Grok `asset_id`, approved URL/UTM or qualified cohort exists in reviewed evidence. No paid CTA or fabricated product. Pass requirements: Founder/Commerce verifies one real appropriate SKU, checkout/delivery/refunds; Praxxis verifies an already-published Grok asset ID and allowed destination; Claude/Commerce independently reconcile confirmed leads/orders, refunds/fees and net revenue per 1,000 qualified-human sessions in 7/30-day cohorts. Impressions/clicks are not orders.

**Release control:** All predicates `may_merge`, `may_publish`, `qd_pass`, `source_verified`, `safety_verified`, `sale_verified`, and `net_revenue_verified` are permanently `false` in this audit. No public action authorized.
