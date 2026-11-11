# R289 — Preparedness claim-context review ledger (UNAPPROVED)

**2026-11-11 PT · DRAFT / HARD HOLD · Issues #136, #820, charter #818**

**Base:** exact R288 d2dba5ad1ce0d2079429a282015889626959b889, draft PR #2031. No merge, CMS, export-to-public, navigation, posting, analytics, email, affiliate, merchant or spending authorization.

## Engineering purpose

R287 authenticated raw 41-body citation IDs and R288 rejected comments, hidden HTML, tags and other nonreader citation placements. R288 still allowed synthetic citation markers nested in opacity-zero/scale-zero CSS or non-narrative form controls, and lacked line-specific reviewer context. These are synthetic proof cases, **not an observed live exploit**.

R289 adds a separate, exact-Git-pinned R288 descendant. It compiles authenticated bytes (R288 blob 0924ead810a4df8c169a5e77f05bcf979eac3dc9) instead of path imports, requires upstream DRAFT_HARD_HOLD, and rejects inline CSS opacity:0, filter:opacity(0), transform:scale(0), and citations in textarea/select/option/datalist. It produces a reviewer-only per-citation ledger containing source ID, HTML line/column, enclosing semantic block, SHA-256 context fingerprint, <=240-character nearby text excerpt and warnings for collapsed default-closed details, zero-size text, transparent text, clipping, hidden overflow, missing prose and missing semantic block. Its citation counts and IDs must agree with both R287 and R288. Failures return INVALID_HARD_HOLD and never publication approval.

No original content, 35 article routes, six tools, 41 metadata records, original source registers, source inventory, WordPress exporter or live URL is modified. Inline CSS detection is intentionally narrow. CSS classes, external styles, actual browser visibility, screen-reader behavior and source-claim truth remain unverified.

## Verification and gaps

- **NEW exact isolated Python:** 68/68 PASS.
- **R288 archived exact + R289 exact mixed local:** 124/124 PASS.
- **Python compilation:** PASS.
- **Locally executed source Git blob:** d6902f0fe059de162d103770a47cd6dae5834ec8.
- **Locally executed test Git blob:** 4c29e45ce22319e4ce36577dcbe7f04639dd0083.
- **NOT RUN:** authentic full-repository R289/parent validation, native Python validate.py/build.py, all current inherited tests, all 41 intended WordPress-ready draft exports, browser/mobile/assistive tech/printing, qualified hazard/privacy and independent QD. Local GitHub DNS still prevents checkout. Tests are synthetic, not evidence of live rendering or deployment. Existing full checkout gap is not closed by this PR.

## Source and independent QA coordination

Fresh compare of all seven original Claude cluster branch refs against correct R200 commits: **7/7 IDENTICAL, 0 ahead/0 behind**. Integrated archive retains **21 historical article lineage differences** requiring review. Independent QA PR #157 HEAD 7d1ae6b8ef93d10cfb6810987672360885e9c1aa; independent fixture PR #169 HEAD e9cd7766dac59d47ab467d8945269b9146c2aef5 (a separate _dup_test.json test still touches real source directory, QA-owned); homepage lead PR #1689 HEAD f55c36b6598eec558dd8bb24e4c8988becc51be0. These drafts were inspected and not modified.

HARD HOLDS: 32 shared-URL groups, 15 duplicate source-ID groups, three disputed CDC/Ready.gov instances, Article #7 chemical-contamination guidance, Article #15/Tool #104 child privacy, printing and accessibility. No medical-safety, privacy or QD clearance.

## Conversion-first, OFFER → STEP → BLOCKER → EXPERIMENT → EVIDENCE → OWNER

| OFFER | STEP | BLOCKER | EXPERIMENT / CHANGE | EVIDENCE | OWNER |
|---|---|---|---|---|---|
| Existing public, official-source Preparedness guide | Already published Grok post → signed-out mobile guide | No verified matching family emergency-contact asset ID, rights, date, URL or native mobile link | Grok/Praxxis TASK-008 authenticate existing asset packet/approved UTM into current public https://finalvestige.com/preparedness/; no new post | **NO VERIFIED MATCH** | Grok / Praxxis |
| Free guide → optional practical download | Read relevant guidance → tool | Child-privacy, source accuracy, print and accessibility HOLD | Independent human review and no-JS/mobile/screen-reader/print acceptance; do not link held card | **HARD HOLD** | Preparedness QA |
| Provisional existing Legacy Triage PDF (NOT approved as upsell) | Free guide → optional paid pack | Rights, product fit, real sale status, merchant fulfillment and refunds unverified | Audit actual PDF and authenticated merchant pathway; founder approval before CTA | **NOT APPROVED / NOT TESTED** | Founder / Commerce |
| Preparedness evidence → reader trust | Citation source to surrounding claim | Context may be concealed or unrelated | R289 CSS-risk sentinel + reviewer locator; independent 41-body truth and scope review | **124 synthetic PASS; authentic NOT RUN** | Preparedness / QD |
| Qualified sessions → realized net revenue | Attribution → verified paid order → refunds/fees | No merchant order evidence, qualified-human denominator or Grok asset mapping | Only consent-safe approved 7/30-day reconciliation; no new analytics scripts | **Net revenue per 1,000 qualified-human sessions NOT COMPUTABLE** | Claude analytics / Commerce |

No product activation, paid CTA, social post, merchant/affiliate action, email, CMS write, source rewrite or release. **REVIEW ONLY / HARD HOLD.**
