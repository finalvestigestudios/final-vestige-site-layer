# R121 — Exact Git-object author-scoped source/citation gate — DRAFT/HOLD

Preparedness Issue #136; commercial coordination #820 and charter #818. Date: 2026-11-04. Stacked on draft R120 PR #943, without modifying original article bodies, metadata, tools, categories, the homepage or the CMS. Nothing may be published or merged from this report.

## New substantive engineering

R120's 13 changed body comparisons check source-ID delta counts but do not independently prove that the referenced source has an author-specific source_use explanation, nor that a purported historical body/meta was actually loaded unchanged from Git. R121 uses read-only local Git cat-file, rehashes each blob with Git's blob header, loads the paired 35-body and 35-meta files for BOTH historical and candidate versions, rejects duplicate metadata keys/malformed citation IDs, checks exact citation count and per-source deltas against the R120 dossier, and flags absent/blank author source_use notes, historical safety-state changes, unauthorized publish states and large reading-depth losses. Deterministic JSON reviewer worklist only; no approval or release side effect. A source-use note's existence does not establish claim truth; equal counts do not prove citation semantics.

## Evidence checked independently this round

- All 13 changed original and 13 candidate body Git objects were fetched through authenticated GitHub blob reads. Their original/candidate citation totals, per-source delta arrays and changed-order flags matched R120. Every R120 example occurrence key was within both versions' source occurrence ranges.
- Fetched the 13 candidate metadata Git objects: all 13 remain publish=draft; all newly cited IDs have nonempty article-scoped source_use explanations. Cross-read the 13 corresponding historical metadata Git objects: safety state remained unchanged in all 13. This is a partial API inspection, NOT full corpus execution or expert safety clearance.
- Authenticated comparison of the seven Claude contributor refs, R116 frozen baseline and prepared release candidate against R117 pinned commits: all NINE compare as identical (zero ahead/behind).
- Independent QA PR #157 at 7d1ae6b8ef93d10cfb6810987672360885e9c1aa differs from RC on medicine and electricity-drill wording; human reviewer needed. PR #169 at e9cd7766dac59d47ab467d8945269b9146c2aef5 remains draft; its second test still writes temporary _dup_test.json to shared source fragments, an isolation blocker. RC #584 head ddb3528ba6494dada1fa1c3a142ce746e3a67706. Homepage lead #49 and #604 inspected and untouched.

## Reproduction on exact trusted checkout (no production writes)

    python -I preparedness/tools/r121_exact_blob_source_scope_gate.py --repo . --snapshots preparedness/docs/R117_NINE_SNAPSHOT_GIT_OBJECT_CUSTODY_HOLD.json --part-a preparedness/docs/r120/CITATION_CONTEXT_CHANGED_BODIES_PART_A_HOLD.json --part-b preparedness/docs/r120/CITATION_CONTEXT_CHANGED_BODIES_PART_B_HOLD.json
    python -I -m unittest discover -s preparedness/tests -p 'test_r121_*.py' -v
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

The new gate reads immutable Git blobs only and returns HOLD even if its structural checks have no blockers. Exit 0 would mean only that structural checks found no blocker. No runner with an accessible complete repository/Git object database is available here. A separate local prototype passed 79/79 adversarial tests and Python compilation; exact committed tests, native validation/build and the complete repository-wide test suite are unverified. Do not label any of these QD PASS, medically safe, LIVE or merchant-verified.

## Source & safety HOLD

R119's union of 35 changed protected paths, 30 previously grouped shared source URLs, 15 carried safety exceptions, 22 editorial decisions and five unfinished tools need review and/or delivery. R120's 62 changed citation contexts, household drill and refrigerated-medicine differences, source-ID retarget in the historical food cluster, human link checks, WordPress dry run, independent browser accessibility and QD remain unresolved. These are historical unresolved totals, not fresh evidence of failure or clearance.

## Conversion-first offer → funnel step → blocker → change/experiment → evidence → owner

| Offer / step | Blocker | Change or acceptance check | Evidence | Owner |
| --- | --- | --- | --- | --- |
| One existing FV Preparedness toolkit / paid order | No authenticated matching rights-cleared currently purchasable SKU | Verify original seller listing, ownership, price, delivery file, refund terms and merchant acceptance before a paid CTA | UNVERIFIED; no paid CTA | Growth / Claude; founder approves release |
| Free source-backed household emergency plan / reader | Qualified safety/source adjudication and release tests pending | Complete R119-R121 author-claim review and emergency guidance approval; keep safety advice accessible without email/purchase | HOLD, not live | Preparedness / independent QA |
| Grok preparedness video / staged guide | No authenticated matching asset_id and permitted destination | Grok/Praxxis TASK-008 to supply real asset ID, actual platform link/bio placement, exact staged landing URL and UTM; do not interrupt TASK-002 through TASK-007 | NOT VERIFIED | Grok / Praxxis |
| Guide / optional verified toolkit click and checkout | Offer, mobile CTA, disclosure and fulfillment not accepted | Only after SKU verification: stage 360/390/768/1440 tests, keyboard/CTA, Payhip confirmation and downloadable delivery | NOT TESTED | Claude / Site QA |
| Verified sale / realized net revenue | No attributed qualified human sessions or reconciled merchant orders/fees/refunds | Compare actual 7- and 30-day cohorts; calculate net revenue per 1,000 qualified human sessions only from confirmed sales and credible denominator | N/A | Growth / Claude |

Draft-only reader CTA: “Build an emergency contact and meeting-place plan your household can practice. Read the fully source-linked free guide. Any optional paid companion must first be independently verified for rights, delivery and clear terms.” The proposed guide is NOT published/qualified as safe. Never show the optional-purchase suggestion publicly before an actual SKU is approved.

Retired water freebies excluded. Nothing merged, posted, deployed, emailed, tracked anew, sold, purchased or changed in WordPress, navigation, merchant or social systems.
