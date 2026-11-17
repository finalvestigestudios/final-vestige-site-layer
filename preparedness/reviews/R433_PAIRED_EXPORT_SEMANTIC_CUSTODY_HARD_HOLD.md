# R433 — Paired WordPress/Preview Semantic Custody (REVIEW ONLY)

Issue #136 · conversion governance #820 · DRAFT / HARD HOLD · 2026-11-17 PT

## Scope and frozen lineage
Parent draft PR #2852 / HEAD 846d56fce158cae8f32073e98a0c633a47f1b08e. This is an additive gate; no changes to article manuscripts, source registries, canonical routes, seven original Claude clusters, two Shelter descendants, taxonomy/safety flags, active templates, publishing/analytics or payment settings. PR #157 and #169 remain independent, unmerged, unapproved safety/fixture QA; dependent #2205 and homepage #1689 are not altered.

## Purpose
R425 checks the SHA-256 of each of 35 WordPress and 35 private preview export files against a private reviewer-generated lock, but does not by itself prove *semantic parity*. Two exports may both be hash-locked while omitting a paragraph, altering a citation ID or moving a CTA. R433 adds a read-only second channel check over exactly 35 original slugs and routes using the existing R425 evidence-lock schema, with:
- ordered readable main editorial blocks, headings, quotes, lists and tables; whitespace-normalized channel comparison
- ordered citation-marker identities, closed coverage to each article's manifest source IDs, no silent ID merging
- exact anchor target comparisons; rejection of changed mobile CTA or source destination paths
- detection of hidden safety text, duplicate/missing main, unapproved form insertion, non-HTTPS or script links, unapproved checkout destinations
- detection of absent, extra, duplicated articles, mismatched byte locks, forged approval claims, and incomplete pairs
- review-only deterministic output SHA-256; CLI always exits 2 even if a supplied synthetic fixture is structurally coherent

**Scope limitation:** This is an HTMLParser/structural comparison, not browser rendering, authenticity of WordPress exports, source-to-claim accuracy, emergency/food/medical safety, merchant authorization, checkout or consent testing, visual accessibility, or independent qualified review. It intentionally fails closed on unsupported markup. The authentic original manuscripts, complete native checkout, 70 WP/private export files and qualified approvals are still missing.

## Locally executed evidence
- Original R433 source: Git blob 90927b283aa3393dc8909d143a9fefa7720cccce
- R433 test file: Git blob 028745abc8438760bd9269ac3ed8ee071feaafe0
- 62/62 new tests, synthetic 35-article pairs with adversarial mutations
- 250/250 combined tests, R430/R431/R432/R433 in one local unittest process
- Python compilation passed
- Absent-original-evidence CLI exited 2, HARD HOLD
- GitHub remote blob identity matching the executed local files checked independently
- Full native validate/build NOT executed; native validate.py and build.py absent from the partial local reviewer checkout
- Hosted CI is separate and must not be reported as PASS without job evidence

## Single conversion hypothesis, not an activation
One previously published and rights-cleared family-contact/reunification social asset (still **unmatched** to Grok immutable asset ID) could lead to the existing **free**, ungated https://finalvestige.com/preparedness/ and a draft CTA: "Start With Trusted Preparedness Resources". Original Article #15 and free Tool #104 remain private and require child privacy/emergency/accessibility review; do not confuse Tool #104 with original plan builder #102. Do not resurrect retired water offer. **No authenticated paid Preparedness toolkit SKU**, Payhip ownership/checkout/delivery/refund evidence, Grok asset ID or merchant-confirmed order exists for release acceptance. Paid CTA must remain absent.

Acceptance ownership: Grok creates/publishes social; Praxxis independently verifies asset ID, rights, destination and link; Preparedness/QD reviews citations and health/emergency/child privacy; Founder/Commerce verifies one licensed/payable/deliverable existing SKU and seller acceptance; Claude measures only consentful qualified-human → CTA → lead → confirmed order → fees/refunds/net, with 7/30-day cohorts. Net revenue per 1,000 qualified-human sessions remains NOT COMPUTABLE.

## HOLD
NO MERGE, NO WORDPRESS OR NAVIGATION WRITES, NO PUBLISH, NO SOCIAL POSTS, NO EMAIL, NO NEW TRACKING, NO MERCHANT OR AFFILIATE ACTIVATION, NO SPEND, NO QD PASS.
