# R291 — Preparedness source-to-claim context consistency (UNAPPROVED)

2026-11-11 PT. Own lane: Preparedness Archive source, citation, and integration gates only. Coordination: #136, business #820/#818. Stacked from exact R290 commit `a248c8ae9049991d7da110d7305b2684ba26e7e7`. **DRAFT / HARD HOLD — NO PUBLISHING AUTHORIZATION.**

## Defect and correction

Praxxis' independent review of R290 found that a *visible* literal `{{cite:id}}` could inherit context from a hard-CSS-concealed sibling or a form-control sibling. Its reader-context digest and 240-character excerpt could falsely appear to include a supporting claim that readers could not see. This is not an observed live exploitation; it is a reproducible synthetic source-level inconsistency.

R291 uses a single `permitted_reader_context()` predicate for ordinary data and decoded HTML entities, excluding the *already recognized* hidden, CSS-hard-hidden, and non-narrative form-control ancestors. Exact R290 raw source occurrence-position matching, hidden-literal rejections, CSS-concealed-citation rejections, duplicate-source checks and upstream `DRAFT_HARD_HOLD` requirements remain.

Excluded nonreader sibling text is **not erased from the original body**. The reviewer ledger now marks its semantic block with `excluded-nonreader-sibling-context`, so safety reviewers can inspect the source rather than mistake the filtered digest for a complete claim adjudication. A citation left with no admissible surrounding narrative retains `no-claim-text-in-block`.

## Bounded test evidence

- Pre-fix reproduction: 74 new synthetic tests, 61 failures against original R290 source (plus one test assertion regex mismatch subsequently corrected).
- After fix: **74/74 new tests PASS**. Complete locally available R288 56 + R289 68 + R290 51 + R291 74 = **249/249 PASS**, 0 skipped. Python compilation PASS.
- Tests cover 16 CSS concealment variants with both populated and empty citation context, four form-control types with populated and empty contexts, six other hidden-attribute variants, six decoded entities in concealed/control text, contextual digest/excerpt preservation, exact literal raw spans, and rejection of hidden/split source tokens.
- Tests ran against the Git-blob-identical committed R288/R289/R290 sources and the R291 source/test blobs. They are **synthetic**, not full actual-site, body, browser, print or end-to-end execution.

## Authentic input / contributor reconciliation

- Frozen seven Claude contributor refs still compare identical (ahead 0, behind 0) to their exact R200 originals. No contributor body, route, metadata, source register, article, tool, validator other than the R289 derivative, or WordPress exporter was changed.
- Independent QA draft PR #157 (HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`), synthetic-fixture draft PR #169 (HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5`), and homepage lead draft PR #1689 (HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0`) inspected; left untouched. QA #169 still has a second source-directory-writing fixture requiring its QA owner.
- Historical holds remain: 21 three-way lineage discrepancies (four triple-different articles #27/#32/#33/#34), 32 shared-source URL review groups, 15 duplicate source-ID groups, three disputed CDC/Ready.gov citations; Article #7 chemical-contamination advice; Article #15/Tool #104 child privacy, accessibility, printing; historical metadata #6/#21 'approved' labels are not independent safety certification.

## Unexecuted / HARD HOLD

A complete authenticated local repository checkout remains unavailable because github.com/api.github.com DNS fails. Consequently **DO NOT CLAIM PASS** for `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, the current full inherited suite, authentic 41-body/2,173-marker read, all 41 WordPress draft exports, real device/browser QA, independent medical/privacy/child-content review or QD approval. Passing the local 249 bounded tests is not a release gate. Keep draft-only.

## Conversion-first acceptance — no sales claims

Target: household emergency contacts and reunification. The source-backed **currently public free** destination is `https://finalvestige.com/preparedness/`; it links official resources and keeps held FV guidance private. Grok/Praxxis TASK-008 must authenticate an already published asset_id, post URL/date, rights, UTM and signed-out/mobile click before using even that link in campaign mapping. Matching asset remains **UNVERIFIED**.

Existing 'Legacy Triage' has a publicly visible $19 Payhip listing at `https://payhip.com/b/n1RhV`, but its displayed merchant is **Vested Wisdom**, not authenticated as FV; product copy emphasizes financial/incapacity and end-of-life organization rather than emergency child pickup/reunification. This is **NOT an FV-owned rights-clearance or audience-fit proof**; checkout success, file/print usability, refunds, merchant payout/settlement, founder approval and complete offer attribution remain untested. Do NOT publish a commercial CTA to it.

| OFFER | FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
| --- | --- | --- | --- | --- | --- |
| Public free official preparedness links | Reader trust | Hidden sibling text polluted citation evidence | R291 shared context policy and reviewer flag | 249 isolated tests PASS; authentic body FAIL CLOSED / UNRUN | Preparedness integration + independent QA |
| Already-posted Grok contact-plan asset | Social → free guide | No authenticated matching post/asset ID/link | Existing TASK-008 owner validates source+mobile destination | NO VERIFIED MATCH | Grok/Praxxis |
| Free guide → optional practical contact worksheet | Accessibility/child privacy | Resource held, not authorized to distribute | Independent child-privacy, physical print and source checks | HARD HOLD | Preparedness QA |
| Legacy Triage listing → optional paid pack | Merchant/ownership and intent mismatch | Public merchant Vested Wisdom; FV rights, product fit, delivered file unknown | Founder/Commerce validates seller relationship, usable PDF, purchase/refund fulfillment before even proposing CTA | LISTING EXISTS; PURCHASE/FIT/RIGHTS UNVERIFIED | Founder/Commerce |
| Qualified campaign visit → paid order → net | Attribution and settlement | Confirmed sales, refunds/fees and qualified-human sessions missing | Consent-safe 7/30-day merchant reconciliation, no extra scripts | NET REVENUE / 1,000 QUALIFIED SESSIONS NOT COMPUTABLE | Analytics/Commerce |

No live content, WordPress/CMS, navigation, social posts, Grok queue, merchant/affiliate, analytics, email, or spending change. Preserve all founder/QD release permissions and only prepare WordPress-ready drafts after complete native passes.
