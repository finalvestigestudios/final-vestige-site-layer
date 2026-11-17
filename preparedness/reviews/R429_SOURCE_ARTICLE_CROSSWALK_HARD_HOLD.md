# R429 Preparedness source-to-article crosswalk — DRAFT / HARD HOLD

Issues #136, #820, and charter #818. Isolated additive changes stacked on R428 PR #2831 head be48fbe205886f968d0d90bb6500bf57e7748cb0.

## Scope
Adds a read-only, never-publishing reverse source-ID-to-article crosswalk to the existing R409–R428 provenance and paired-export gates. It checks every article ID, canonical path, citation source ID and source order against the original review docket and private manifest, while preserving separate identities for source IDs that share an exact URL. It emits all affected article slugs for each shared-URL review group; any normalized URL alias is recorded for human review, never merged automatically. It binds supplied manifest bytes to SHA-256, refuses an unpinned R397 original in native mode, and exits 2 regardless of structural success. No QD, medical/food/emergency/child-privacy, publishing, commercial or revenue approval may result.

## Real original inventory read-only verification
The GitHub original docket is preparedness/reviews/r397_original_source_fork_docket.json at Git blob 86d22a1d504c93db7689b914e2202a7845b648e2. Its 115,400 bytes contain 35 article identities, 203 distinct original source IDs, 280 source-record variants, 17 separate exact-URL multiple-ID review groups, 5 source-applicability disputes, 9 unselected manuscript forks and 9 branch pins. A narrow normalized-host/path screen found zero distinct raw-URL alias families; no source-truth, DNS, title/content, license or safety audit was performed.

All original seven Claude contributor refs and two Shelter descendants were compared against the original nine pins: IDENTICAL, ahead=0 and behind=0 each. Independent draft heads inspected without change: QA #157 7d1ae6b8ef93d10cfb6810987672360885e9c1aa; synthetic fixture #169 e9cd7766dac59d47ab467d8945269b9146c2aef5; dependent repair #2205 bbcf1859768624c611df4abadc564c18247cf32a; homepage #1689 f55c36b6598eec558dd8bb24e4c8988becc51be0.

## Exact executed source and local tests
- R429 source Git blob a8a99b9a3b3a9a94eefef5a8b9bc5ddcbae75bee.
- R429 test Git blob ee03da4a7bd166e7b0453772a72bce0938ab6cc2.
- Each remote blob matched locally executed bytes.
- 80/80 R429 new Python synthetic tests PASS (65 adversarial and 15 baseline). Independent module test runs: R409 66/66, R410 77/77, R426 53/53, R427 64/64, R428 57/57, all PASS. This is 397 separately passing local tests, NOT a combined full-suite PASS.
- Python compilation PASS. A larger assembled local full-suite invocation timed out; DO NOT report it as PASS. The historical R425 local copy differs from its committed GitHub blob and therefore cannot substantiate the remote implementation.
- Actual original 35 manuscripts, private 35-article manifest and 70 WordPress/preview paired exports were NOT PRESENT for native validation/build. Qualified food, water, medical, emergency, child-privacy and independent QD reviews NOT GRANTED. No genuine sale, social asset attribution, merchant receipt or 7/30-day net revenue demonstrated.

## Conversion-first offer and safety plan
One high-intent topic only: family emergency contacts and reunification. An ALREADY PUBLISHED, independently authenticated on-topic Grok asset may eventually direct readers to the existing FREE public official-resource https://finalvestige.com/preparedness/ with permissible mobile UTM. Original Article #15 and optional Tool #104 remain PRIVATE / UNAPPROVED. Tool #102 is separate; all retired water freebies excluded. Do not invent creator asset IDs, product SKUs, merchant sales or cohort attribution.

OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER:
1. Genuine FV-owned licensed Preparedness digital pack → paid checkout → no authenticated existing payable and deliverable SKU, merchant rights or refund records → verify ownership, live seller acceptance, checkout/delivery and disclosures before proposing any paid CTA → HOLD → Founder/Commerce.
2. Real family-contact video → free Archive landing → immutable asset ID, published post URL/date, actual hook, rights and permitted mobile link unverified → Praxxis independently checks Grok inventory, without modifying production/posting queue → UNMATCHED → Grok/Praxxis.
3. Free Archive → optional private Tool #104 → Article #15 claim provenance, local contact privacy, applicable agency guidance and print/accessibility review unresolved → qualified human review and real device testing → HARD HOLD → Preparedness/QD.
4. Qualified-human sessions → CTA → confirmed lead → verified paid order → fees/refunds → realized net revenue → provider/merchant cohort receipts missing → reconcile 7/30-day attribution with existing approved measurement, tiny-sample warnings and privacy consent → NOT COMPUTABLE → Claude/Commerce.

Draft/free-only CTA (UNPUBLISHED): Start With Trusted Preparedness Resources. It must not go live without an actual on-topic published creator asset and release approval. No paid CTA, CMS, navigation, social post, email, tracking script, merchant/affiliate activation or spending.

R429 remains DRAFT / HARD HOLD / UNMERGED. It supplements, not replaces, full candidate/paired-export fidelity, reading-depth, external-source verification or independent release governance.
