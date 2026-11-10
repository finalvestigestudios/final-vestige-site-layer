# R275 — repair synthetic R274 census fixture without weakening authentic source custody

**2026-11-10 PT | Issue #136 | Commercial coordination #820 | DRAFT / HARD HOLD / UNPUBLISHED**

## Exact defect and bounded correction
Independent Praxxis review (Round 277, shared TASK-008 handoff) found that R274's `test_authentic_raw_slash_group_remains_an_original_label` intentionally changes a synthetic `base` source URL from `https://example.org/jerky` to `https://example.org/jerky/`. Once both synthetic readings have identical exact URL spellings, the toy corpus contains **2** distinct exact URLs rather than 3. The test overrode the caller's census to 2 but left the embedded fixture's `unique_source_urls=3`, so R272's final census consistency gate correctly rejects it. An expected HOLD assertion would fail, independent of the repaired production URL join.

**R275 fixes only the intentionally changed synthetic fixture's embedded `unique_source_urls` to 2.** It does **not** change `CENSUS`, the authentic production crosswalk `unique_source_urls=202`, the original eight source registers, any citations, article text, tool, routes, status flags or the R272 validator. A new negative test explicitly preserves the fail-closed invariant: if a synthetic source changes but its embedded census stays stale, R272 must raise `ValueError("advertised source census inconsistent with actual rows")`. The positive and negative paths now exercise different contracts without manufacturing a passing source audit.

## Execution evidence (scope labeling required)
- **BUILT:** isolated follow-on to R274 #1957 at `c59a6f404c853cc5247ac617be6c241517e96d78`, one corrected test module plus this audit.
- **CONNECTED-SOURCE CHECKED:** GitHub returned R274 test blob `9fbdf55f028e177ea55e626f2323258a71330175`; R275 changes only the synthetic-test file and this audit; review unchanged production gate R272 blob `c85a958ef9e69951b39ca036d85237c5f39a1772`, R273 blob `4a962e8f35249b35e69fbfb64a3ae52ea5c45375`, 8 original source blobs, frozen original crosswalk `d62e493a67dedd23e04cfdf3cce762ef933c6bf9` and R273 docket `db59f659b0e1c513011539bbc9b6fc1ebf056785` remain independent of this test-only change.
- **PYTHON EXECUTED — inherited prior R273 only:** 50/50 isolated R273 synthetic tests passed on 2026-11-10. These are **earlier R273 source bytes**, NOT execution of R274/R275's modified test suite.
- **NOT EXECUTED:** committed R275 amended R272 tests, authentic 8-origin R272/R273 native audit, full `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, complete inherited test suite, and 41 authentic WordPress draft exports. Native checkout cannot resolve `github.com` from current container; prior R274 Actions 42916493710 has failed job with no returned steps/log archive (BlobNotFound 404), and no cause can be asserted.
- **RELEASE:** no independent QD PASS, medical/privacy safety signoff, publication approval, or live commerce evidence.

## Source/citation review still outstanding
Frozen authenticated source set remains **244 distinct source reading records; 202 exact original URLs; 201 review-only terminal-slash aliases; 32 pending shared-URL interpretation groups; 15 pending duplicate-ID groups**. Exact source URLs, query strings, fragments, reading support/evidence and origin/row provenance must not be normalized in-place. The three disputed Article 7/20 CDC/Ready.gov citation occurrences, Article 7 chemical guidance, Article 15 and Tool 104 personal information/child card, and physical printing/accessibility remain independent manual holds. No reviewer clearance may be inferred from structural fixture tests.

## Agent coordination
- Seven `claude/prep-*` heads must be compared live to the frozen R200 SHAs every run, never silently accepted on the basis of older comments. Read-only exact branch API comparison at R275: **7/7 unchanged**.
- Independent QD PR #157 and fixture PR #169 remain separate draft owner lanes; PR #169's residual repository-source `_dup_test.json` fixture mutation remains an inspected risk; no cherry-pick.
- Homepage lead PR #1689 is owned outside Preparedness; do not touch.
- Product/commerce/attribution coordination belongs to #820 and founders; no UX or analytics production changes in this branch.

## Single proposed conversion pathway and blocking gates
**Audience intent:** already-published Grok/Praxxis family communication/reunification audience **only if asset_id, post URL/date, source rights and actual mobile-clickable destination independently authenticated**. **Free public destination:** existing `https://finalvestige.com/preparedness/`, not unpublished household manuscripts or unapproved cards. **Optional commerce candidate:** existing Legacy Triage digital PDF **PROVISIONAL**. No product/CTA authorization until complete copyright/rights audit, content suitability, privacy and secure records handling, independent checkout/delivery/refunds and founder approval. Current net realized revenue per 1,000 **qualified human** sessions is **NOT COMPUTABLE** (do not substitute clicks or checkout starts for paid orders).

**Funnel acceptance:** verified asset and tagged destination (Grok/Praxxis) → live free landing and relevant source-backed resource (Preparedness/QA) → applicable clearly disclosed optional product (Founder/Commerce) → independently confirmed paid order, fees and refunds (Commerce/Analytics) → net revenue per 1k qualified sessions by 7/30-day cohorts (Analytics). No unauthorized promotion, email, tracking script, social post, public CMS or payment activity.

**DRAFT / HARD HOLD.**