# R405 — Three-edition Article #11 citation custody and conversion HOLD

**Preparedness source/citation integration only:** [#136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136), [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). **OPEN DRAFT / HARD HOLD**. No source/recipe/canonical URL/safety status/CMS/navigation/merchant/analytics/social/email/paid deployment. No auto merge.

## Actual engineering change

The previously delivered R404 read-only custody verifier authenticates the original E395 ZIP and nested WordPress-oriented Article #11 HTML only. New private editorial E397 and E398 HTML variants were then reported in [Issue #136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136), but were not transferred to the integration runner. R405 binds **three separate immutable HTML receipts** to the original ZIP receipt and forbids substituting a derivative for the original:

| Edition | SHA-256 from original editorial handoff | State |
|---|---|---|
| Original E395 ZIP | `21a2142c6050eb3bae020c67744ee82439d854525ba63915ea9092a0b7bba46b` | Not received by this runner |
| Original nested E395 HTML | `bc0537e611d35b195e10ee49ceb9772a904b7c8fea0749a6203da38e835f8184` | Not received |
| E397 derivative HTML | `edd96e850ada775e7394b08d0c59f79415efb2d08f2d088685265e5881e0d50c` | Not received |
| E398 derivative HTML | `be180cb0443ebf2dc16c0cd2c5e638a1dc3e49f1f282f03be4f946244d5e4643` | Not received |

Reader changes in E398 are not verified simply by these digests. The new R405 tool invokes the adjacent **unchanged original R404 ZIP custody checker** on the original archive, binds its nested HTML bytes to the separately supplied E395 HTML, then checks the E397 and E398 HTML digests independently. It inventories outbound HTTPS citations, reports additions/removals edition-by-edition, rejects missing four-source scope citations and basic active/remote HTML hazards (script, form, iframe, inline event handlers, CSS external URLs, tracking attributes, duplicate IDs, nonportable links). It cannot verify the **meaning, safety or completeness** of article claims or whether a live FSIS page has been authentically read. Legitimate editorial citation changes may require manual adjudication. It *never selects an edition*, exits 2, reports `eligible=false`, `publication_approved=false`, and retains `DRAFT_HARD_HOLD`.

**Four cited source scopes held separately:** NCHFP/UGA jerky (2014-derived); FSIS Ask USDA room-temperature FAQ (reported indexed-only, direct original inaccessible); University of Minnesota Extension home food-drying guidance (reviewed 2026); UMN Extension emergency cooking-without-kitchen page (reviewed 2025). Same-publisher evidence does NOT authorize an interchangeable homemade jerky storage rule, and industrial guidance is not a household recipe. No claim of medically safe/validated household storage follows from structural PASS.

## Exact-source and test evidence

- New code: `preparedness/tools/r405_editorial_lineage_citation_gate.py` Git blob `ea6128e8636d049f0b0d2f28aa0c406b6efd29fe`, 13,280 bytes, exact local == remote blob.
- Committed exact-source new test: `preparedness/tests/test_r405_editorial_lineage_release_hold.py` Git blob `39a68253ef304e5464455fb609d24cb7e27dda04`, 7,831 bytes, exact local == remote blob.
- **58/58 new committed-code synthetic tests PASS locally.** Existing R403 45/45 and R404 68/68 tests also PASS on unchanged matching Git blobs. All 171 committed-source/inherited local tests PASS. Additional 77 analogous locally prototyped cases also PASS, for **248/248 available assembled local tests**; those 77 are **not** part of this PR.
- `python -I -m py_compile` on all available source/test files PASS. CLI with no private artifacts returns expected exit 2 / `integrity=FAIL` / hard hold. No genuine original/derivative editorial bytes available, so no authentic receiver ingestion PASS.
- All 9 original contributor pins (7 Claude + 2 Shelter successors) compared live on 2026-11-15 PT and returned `identical`, ahead=0, behind=0. Original 35 article IDs / 203 source IDs / 280 source occurrences / 17 shared exact-URL review groups remain pinned in R397; 5 original source disputes and 9 Shelter manuscript forks **remain unadjudicated**.
- Independent QA #157 exact head `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` and synthetic fixture #169 exact head `e9cd7766dac59d47ab467d8945269b9146c2aef5` inspected, unchanged, open drafts; dependent fix #2205 exact head `bbcf1859768624c611df4abadc564c18247cf32a` remains unmerged. Homepage draft #1689 exact head `f55c36b6598eec558dd8bb24e4c8988becc51be0` not touched.
- **Not run:** native full 35-article `python -I preparedness/tools/validate.py`, `build.py`, authentic original 50+ HTML WordPress/private previews, independent food-safety/QD or creator/merchant release. Authenticated full checkout unavailable locally. No claim that hosted CI ran/passed. Any CI result must be checked at the final commit.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER

| Offer | Funnel | Blocker | Draft-only change/acceptance | Evidence | Owner |
|---|---|---|---|---|---|
| **ONE existing genuinely payable and rights-cleared FV Preparedness pack** (none verified) | Qualified reader → actual checkout → delivered order | Existing SKU, authorized merchant checkout, license, fulfillable files, refund policy/fees unverified | Founder/Commerce to authenticate one already-existing SKU; **no speculative purchase CTA** | HOLD; 0 verified orders **in this audit** is not proof of 0 site sales | Founder / Commerce |
| Genuine published family-contact Grok asset → free official checklist | Actual `asset_id` and rights → mobile `/preparedness/` landing → relevant source click | Asset ID, permitted link slot, hook and match not authenticated | Grok/Praxxis via original [TASK-008](https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit); no queue change | Not verified | Grok / Praxxis |
| Official free Archive → optional Tool #104 | Ungated checklist / print | Child privacy, reunification, accessible print, qualified emergency review incomplete | Keep optional Tool #104 PRIVATE; proposed free-only CTA **“Start With Trusted Preparedness Resources”** unpublished | HARD HOLD | Preparedness / independent QD |
| Attributed human sessions → merchant-settled paid order → net revenue | 7/30-day exact asset`_id`/campaign → relevant CTA → provider-confirmed order → refunds and fees | Actual merchant settlements and consent-appropriate attribution absent | Reuse approved Claude/Site analytics only, no duplicate pixel or tracking | Net revenue per 1,000 qualified sessions **NOT COMPUTABLE** | Claude / Commerce / Founder |

### Release acceptance
Receive all *original* E395 ZIP/E395 HTML/E397 HTML/E398 HTML through approved private transfer, validate their SHA pins and complete HTML/source/citation diff. Run native full validate/build and 35-article reconciliation; adjudicate five source-reading disputes and nine Shelter manuscript forks; get qualified domain reviews for Articles #7/#11/#15 and Tool #104; independent QD plus founder release approval. **No publication, WordPress/CMS/nav write, editorial article change, social posting, email, merchant/affiliate activation, tracking deployment or spending was authorized or performed.**