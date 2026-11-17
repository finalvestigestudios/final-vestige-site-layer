# R444 — Preparedness original regression closure and provenance receipt
**2026-11-17 PT · #136 · conversion #820 · charter #818 · DRAFT / HARD HOLD**

**Scope:** isolated read-only additions to `preparedness/tools/`, `preparedness/tests/`, and this review memo. Parent R443 #2910 HEAD `4cd2ba579c7f4dccdaebe6967b4a9c1e203e4b50`. Never merge, publish, edit CMS/navigation, Grok creator queue, emails, tracking, checkout or affiliate configuration without founder approval.

## Concrete engineering finding and fix
R443's attempted legacy-ZIP assembly had 43 failures and 5 errors across 495 tests. A reconstructed review environment from the *available R434–R443 artifact archives* reproduced **360 tests, 56 errors and 1 failure** when the old R440 module was used in place of R441's revised R440 source. Replacing the old module with the R441 local equivalent eliminated all 56 errors; the remaining failure was an **obsolete R440 test expectation** that treated repeated manuscript blob hashes as invalid. The exact current GitHub R443 test blob `244b1ae256a0a0723b16657fe2549af2c0de0128` already has the corrected expectation. Updating ONLY the local test assembly to match that verified GitHub expectation resulted in **434/434 local tests passed** (R434–R444 reconstructed/local-equivalent). The R444-specific pre-commit local-equivalent suite passed **74/74**. Python compilation passed.

**Evidence limits:** The reconstructed local suite is **NOT** a full clean checkout nor an execution of the exact final committed R444 Python files; the locally equivalent R444 modules include extra tests. Hosted CI and the native authentic 35-manuscript validation/build remain NOT VERIFIED. Never report this as CI PASS, actual WordPress parity, original claim safety or QD PASS.

## New deterministic fail-closed gate
`r444_offline_integration_receipt.py` audits source/test/review file bytes and SHA-256 + Git blob hashes for a supplied R434–R443 revision inventory, closes missing/duplicate/misrouted evidence paths, rejects symlinks and oversized files, checks original 35-article/203-ID/280-occurrence/17-shared-URL docket counters and preserves **five source disputes / nine unselected forks**. It rejects unsupported 'cumulative PASS', fabricated QD/publication/paid-offer status and test pass claims with recorded failures. The code never writes files or grants release. Its empty/missing evidence behavior is a HARD HOLD and exit code 2, including when synthetic structure passes.

**Important limitation:** These counts are pinning checks, not a substitute for independently locked *original 35-body* source and claim-to-scope evidence, actual WordPress/private-preview byte captures, quality of medical/food/emergency advice, or a merchant settlement record. Source #157 and fixture #169 require independent QA and #2205 dependent fixture isolation remains unmerged.

## Exact peer heads read on 2026-11-17
- #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, draft.
- #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`, draft.
- #2205 `bbcf1859768624c611df4abadc564c18247cf32a`, draft.
- #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0`, draft.
- #2789 `bfdac3cc9f28b229bfd736514229785e7b15bec5`, draft (changed since R443).
- R443 #2910 `4cd2ba579c7f4dccdaebe6967b4a9c1e203e4b50`.
- All nine original contributor heads read directly by self-compare and identical to original R397 pins: `2122d856`, `f911ff7a`, `d5ef5baf`, `4e5caf81`, `67e116e5`, `7504a5f0`, `5daeaf2d`, `ac8625fa`, `6a5998ea`. No original contributor branch edited.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER
1. **One authentic FV-owned Preparedness pack → checkout/paid order** | Existing rights-cleared payable SKU, delivery, refund terms, actual seller approval and merchant settlement **not verified** | Audit existing permitted merchant records; do not publish an unapproved paid CTA | **HOLD** | Founder/Commerce.
2. **Published family emergency-contact clip → official free /preparedness/ guide** | Actual Grok asset_id, URL/date, rights/hook and mobile route unmatched | Independent Praxxis/Grok TASK-008 link and asset QA, no new creator assignment | **UNMATCHED** | Grok/Praxxis.
3. **Free agency checklist → optional private Tool #104** | Article #15 emergency accuracy, child privacy/print accessibility and #102/#104 separation | Qualified QD review before any tool CTA | **HARD HOLD** | Preparedness/QD.
4. **Qualified human session → relevant CTA → confirmed lead (if applicable) → merchant-confirmed paid order - refunds - fees** | No attributable orders or 7-/30-day cohorts | Use #820's native privacy-safe instrumentation only after owner approval | **NOT COMPUTABLE** | Claude/Commerce.

Free-only unpublished CTA candidate: **Review the official household emergency checklist**. This landing remains public agency links only; no retired water freebie, third-party merchant or unreviewed paid pack has been activated.

**Release governance:** All R444 source/test structures are DRAFT/HARD HOLD. No QD/medical/food/emergency safety approval, full native build, 70 authentic WordPress/export captures or verified paid commercial outcome established.