# R441 — Authentic R397 multiplicity and source-crosswalk correction (HARD HOLD)

Scope: Preparedness Archive integration only; Issues #136 and #820. Parent R440 `e91daa072cc4425e57da6f70db12ce38c167da26`. No CMS, routes, public posts, merchants, social assignments, traffic scripts or publication writes.

## Reproduced real-data defect

Independently fetched immutable original R397 docket Git blob `86d22a1d504c93db7689b914e2202a7845b648e2` (115,400 UTF-8 characters). Its `original_articles[].body_candidate_git_blobs` intentionally records *source appearances across branches*, not unique manuscript bytes. R440's `not unique(shas)` check falsely rejected seven authentic article rows:

| Article slug | Original appearances | Unique body blobs |
|---|---:|---:|
| home-fire-escape-plan | 3 | 2 |
| homemade-water-filters | 9 | 1 |
| making-water-safer | 9 | 1 |
| salt-beef-salt-pork-age-of-sail | 9 | 1 |
| two-week-water-storage | 9 | 1 |
| water-advisories-explained | 9 | 1 |
| water-math | 9 | 1 |

R441 removes only that *incorrect uniqueness restriction*. It **does not** deduplicate the records, claim editorial equivalence across different blobs or select any fork. For the four actually disputed body paths, the new relational gate compares SHA **multisets** against their individually branch-attributed fork variants, and fails on missing/replaced/colliding contributor records. Any same-byte reuse from independent contributors remains preserved.

## Crosswalk independently reconciled (docket structure, NOT source truth)

- Exactly 35 original article identities; 203 distinct source IDs and 280 (branch, Git blob, URL) source variants.
- Exactly 181 original unique exact URLs; exactly 17 URLs link *different* source IDs. The 17 recorded shared-URL review groups match the set derived independently from all 280 variants, including each group's source-ID membership. Neither source IDs nor URLs are silently collapsed.
- All five contested source IDs exist in the full crosswalk with exactly the same `(branch, source_blob, URL)` triple multiset; all decisions remain `HUMAN_REVIEW_REQUIRED`.
- Exactly four disputed article bodies (plus four metadata paths and one Shelter source fragment) remain unselected. The original evidence, longer versions and differing passage context require qualified human review.
- All three original manifest/source-register/fragment Git blob pins are retained as evidence identity anchors.

## Test boundaries

Locally rebuilt R430–R440 + R441-style branch fixture produced **768/768** Python unittest cases passing, after restoring R434 and R436 parent modules from supplied R434/R436 evidence archives (initial partial assembly failed; rerun was clean). Python compileall passed. A focused 131-case local variant of R440+relational tests also passed. Local sources are equivalent candidates; **the exact uploaded R441 GitHub bytes have not been executed within the local container, and hosted CI is not claimed PASS**. R441 adds a separate 62-test synthetic regression module committed to this review branch. Test fixtures cannot attest source truth or safety of authentic articles.

## Exact immutable coordination and outstanding gates

All original nine Claude/Shelter branches directly compared to their R397 frozen commit SHAs today: **9/9 identical; 0 ahead, 0 behind**. Independent QA #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; isolated fixture #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`; dependent #2205 `bbcf1859768624c611df4abadc564c18247cf32a`; homepage #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0`; editorial #2789 `c485aa6a75a5e7e2abeab258c0004231bd72cdf4`—all open drafts, not modified in this run.

**Still blocked:** native authenticated 35-original validate/build; 70 genuine WordPress/private-preview exports; raw CSS captures; full compiled suite executed against final committed branch; qualified food, water, medical, emergency, accessibility, child-privacy and QD review; 5 source disputes and 9 forks; actual confirmed payable rights-cleared Preparedness SKU with merchant delivery/refund proof. No automatic approval, monetization activation, or claim of medical safety.

## One conditional conversion-first intent

**Audience:** already-published, rights-cleared Grok family emergency-communications/reunification topic **only if an actual asset ID and mobile link path are verified by Praxxis/Grok TASK-008**. **Free destination:** existing `https://finalvestige.com/preparedness/` with a descriptive official household checklist CTA. **Optional tool:** Tool #104 identity/Article #15 safety/child-privacy/print use remains HARD HOLD. **Paid step:** HOLD until existing owned rights-cleared payable Preparedness SKU verified. Do not resurrect water freebies or manufacture a pack. Qualified-human asset-tagged sessions → landing → CTA → confirmed lead → merchant-confirmed paid order → refunds/fees → net revenue; none can be inferred without evidence. 7/30-day net revenue per 1,000 qualified-human sessions currently NOT COMPUTABLE.

**Always DRAFT / HARD HOLD.** Only founder+qualified reviewers may authorize release; this evidence is not QD PASS.
