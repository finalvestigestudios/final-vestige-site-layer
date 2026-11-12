# R305 — Citation display ↔ bibliography and source-safety crosswalk (#136)

**2026-11-11 PT | DRAFT / HARD HOLD | REVIEW ONLY | NO RELEASE.**

## Discovery
The authenticated native `preparedness/tools/build.py` renders source references as `<sup class="pa-cite"><a href="#src-N" aria-label="Source N: TITLE">[N]</a></sup>`, with matching `<li id="src-N">...` source records. Existing R302's structural parser intentionally ignores the citation's visible marker and accessible label. In isolated tests, source text and the href target can remain unchanged while the visible number or accessible title changes. R299 exact native build reproduction is a **separate existing control**; do not misstate this as a proven live defect or an R299 bypass.

## R305 independent local package (prepared, not yet verified in an authentic repository checkout)
- New read-only source-display/bibliography parity validator checks numbered citation hrefs, visible markers, accessible titles, ordered bibliography targets, source URLs, rel=noopener, duplicate/unused IDs and review-scope disclosures.
- 88 new synthetic mutation tests passed; inherited R295–R304 803 passed; **891/891 local synthetic tests passed** and Python compilation passed.
- New validator and 88 tests are now **committed** to this isolated draft branch. Exact tested files match independently fetched GitHub Git blobs: tool `3e8ae9d035f4485ce87af565a87905e0c1865187` (commit `b7737c52ab1009e449bbc06c81e39958b9e6468e`), tests `0abd0e19c2b6c36751941b815155038cdf2cce28` (commit `9414f5829368e35a95ca66678cf4b30e1f82b12b`). This establishes committed synthetic mechanical checks, not authentic native integration, source/safety approval or release readiness.
- Synthetic source and citation URLs are fixtures, not independently verified official guidance. The standalone validator rejects an incomplete repository with `INVALID_HARD_HOLD` and exit code 1. No release-positive state is possible.
- Native authenticated `validate.py`, `build.py`, 41 actual WordPress draft outputs, browser print/JS/accessibility, independent source/safety and QD remain **NOT RUN / NOT APPROVED**. Local `git ls-remote` still fails `Could not resolve host: github.com`.

## Fresh exact coordination
- Original seven Claude branches compared against frozen R200 source-head SHAs: **7/7 identical**, ahead=0, behind=0, changed files=0.
- Previous R304 draft PR #2125 at `2ec5f75c37291773f49d57281aeb73e2a3886cc0`. Independent QA #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; fixture PR #169 HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5` retains a test writing `_dup_test.json` under the actual source fixture directory. Homepage lead #1689 HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0a0` untouched.
- 14 body and 12 metadata R200 lineage differences, historical food source identity disputes, Article #7 water safety and Article #15/Tool #104 privacy, emergency communications, accessibility and printing remain HOLD.

## One-audience conversion acceptance (not live)
| Offer → funnel | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|
| Paid Preparedness practical pack → checkout | No authenticated FV-owned/licensed, audience-fit, purchasable SKU, delivery or merchant settlement | Founder/Commerce verify rights, order, customer delivery/refunds before paid CTA | NOT APPROVED | Founder/Commerce |
| Existing free family-contact archive → Tool #104 | Child-data privacy, 911, source, no-JS and print discrepancies | Qualified independent source/privacy and browser/print testing; no real child data | HARD HOLD | Preparedness QA |
| Grok published social → free archive | No verified existing matched `asset_id` and permitted mobile URL | Praxxis/Grok TASK-008 read-only match; no queue/posts | NOT VERIFIED | Grok/Praxxis |
| Qualified sessions → confirmed lead → paid order → net revenue | Missing merchant-confirmed transactions, fees/refunds, asset attribution | Reconcile 7/30-day cohorts, human sessions and tiny sample caveats | NOT COMPUTABLE | Claude/Commerce |

**Draft CTA only:** “Make a plan for how your household can reconnect. Explore free, official preparedness resources.” Candidate free path `/preparedness/`; do not promote Tool #104 as safe or paid pack as available. No public publishing, CMS/nav, social, email, analytics, merchant or spending writes.
