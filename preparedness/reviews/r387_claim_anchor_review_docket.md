# R387 Preparedness — immutable claim/citation anchor custody

**DRAFT / HARD HOLD · source-only review · no WordPress/CMS/publication permission**

Issue #136; upstream R386 draft PR #2601 (HEAD `73c730c2917d4827114ed59f36810901b18c01d9`). Related independent QA PR #157; fixture PR #169 and isolated follow-on #2205 remain separate, unmerged. Creator / revenue coordination: #820 and #818; Grok/Praxxis TASK-008 is a research-only dependency.

## Concrete integration gap closed

R386 detects original prose-block drift and overall citation count/order. However, a citation can move to a **different clause or different paragraph while preserving the same prose and global repeated-source sequence**. Such a rendered footnote may misleadingly appear to support a claim other than the original claim. R387 pins each citation occurrence to its original textual block and precise **word-boundary offset**, tracking repeated source IDs, rendered `<sup class="pa-cite">` anchors, headings and paragraph position. It does not claim that a correctly placed citation actually supports advice.

## Deterministic behavior and privacy

- Original 35 article bodies are retrieved by immutable, size-checked Git blob SHA as assembled by R384 from the original 77-path manifest. All nine unselected Shelter conflicts and all original variants remain candidates; none is automatically elected.
- R387 compares all original variants with the same WordPress-ready draft body, detects claim relocation, citation target swaps, missing/doubled refs, prose changes, malformed/ambiguous markup, missing exports and tampered Git identities. It emits only source SHA, branch, slug and error codes; avoids copying sensitive manuscript language to the review docket.
- Read-only; no source-register, article, metadata, taxonomy, permalink, publication status, merchant, tracking, WordPress or Grok queue modifications. CLI exits **2 on every path**, even when synthetic/preview pairs match. Its result must be interpreted **alongside** R386 and original QA; it is not a replacement for R386's source URL, accessibility, noindex or parity checks.
- A syntactically matching citation is **not** independent validation of a food, medical, water, emergency or child-privacy instruction. Qualified adjudication still required.

## Exact available evidence

- 57/57 new R387 Python tests PASSED in local synthetic assembly (separately reported, including cross-paragraph and intra-paragraph repeated-citation mutations).
- 831/831 **available assembled** R377–R387 local Python tests PASSED. This is the actual number executed this run; do not conflate with previously reported larger suites whose complete backing files were not necessarily present in the assembled artifacts.
- Python compile passed for new gate/test. Committed file Git blob SHA compared against locally executed source and test bytes. No authentic native repository build or authenticated 35-article/50+ private preview pairs executed.
- GitHub Actions R386 run `43699730035` one job `132768008605`, conclusion failure; steps empty; downloaded job log returned BlobNotFound 404. Root cause undetermined. Do not claim the new PR's hosted CI passed.
- Original seven Claude and two Shelter branch refs compared against manifest SHAs: nine identical, ahead=0, behind=0. QA #157, fixture #169, dependent #2205 and home #1689 inspected and not edited.

## Human/QA release gates (all still HOLD)

1. Assemble complete authentic checkout and independently run R384–R387 against **actual** SHA-pinned originals and non-public WordPress/preview outputs. Confirm complete export count and per-article canonical URL uniqueness. Reconcile any false positives from deeply nested or semantically equivalent markup manually; do not remove guardrails to get green.
2. Resolve five divergent source-reading-scope identities, nine Shelter manuscript forks and specific Article #7 CDC claim qualifiers, Article #11 food-safety disputes, and child/privacy/print checks for Tool #104.
3. Obtain qualified human safety and independent QD approval. Preserve historic founder labels as historical metadata, not a substitute for QD.

## Conversion-first offer → funnel step → blocker → experiment/check → evidence → owner

| Offer → step | Blocker | Required change / acceptance | Evidence | Owner |
| --- | --- | --- | --- | --- |
| ONE already-authentic FV Preparedness practical pack → paid order | No confirmed FV-owned rights-cleared, payable, deliverable Preparedness SKU | Read-only verify SKU owner/rights, working mobile merchant checkout, disclosure, downloads, refund path, fees; only then draft a consent-respecting paid CTA | **UNVERIFIED — no approved paid CTA** | Founder / Commerce |
| One actual published family-contact video → Archive free official guide | Real matching published `asset_id`, source-backed hook, rights and permitted mobile URL unverified | Praxxis independently verify published post and route; Grok keeps posting/creator ownership; no invented UTM attribution | **NOT VERIFIED** | Grok / Praxxis |
| Free official Archive → optional Tool #104 card | Private card under child privacy/physical-print/emergency safety hold | No public link or delivery; QD independently checks advice/privacy/print | **HARD HOLD** | Preparedness / QD |
| Qualified-human session → CTA → verified order → net revenue | Missing authenticated merchant receipts, fees, refunds, 7-/30-day cohorts | Use existing approved measurement stack only, never duplicate scripts. Revenue/1000 = net revenue / qualified-human sessions * 1000 **when numerator/denominator exist** | **NOT COMPUTABLE** | Claude / Commerce |

Proposed but not posted free CTA: **Start With Trusted Preparedness Resources** → https://finalvestige.com/preparedness/ ; no paid upsell until offer and audience fit independently authenticated. Public Archive states original in-depth guides are still in source/safety review.

**Non-actions:** no merge, live publication, menu, CMS writes, social post, email, payments, affiliate activation, measurement scripts, spending, or QD PASS.
