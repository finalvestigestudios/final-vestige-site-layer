# R263 — Wallet-cutout privacy custody witness (DRAFT / HARD HOLD)

Owner: Preparedness source/citation integration lane, Issue #136. Cross-reference business conversion #820, charter #818 and existing creator research-only TASK-008. Exact base: R262 draft #1887 (`e73e5a3e65c46082f0306b953106e6142bc091ca`). No merge, public WordPress, CMS, navigation, scripts, social, merchant, email or spending changes.

## Independently observed source-level problem

R260 correctly found that Tool #104's original page-level privacy alert disappears on print. R261 added a privacy warning to the *printed sheet*, and R262 repaired its inaccurate no-JavaScript feature promise. Neither correction establishes that the warning remains attached to the wallet card after the reader follows the original instruction to cut out and fold the 7 × 2.125-inch card.

The authenticated original Tool #104 Git blob is `be8698ac5d020476ff649d85813810e2000c6f98` (19,145 UTF-8 characters). In its no-JS blank fallback, 13 labeled fields occupy two `pa-face` elements inside `pa-foldcard`; the R261 notice is before `pa-foldcard`, not inside it. In the JavaScript path, `pr.appendChild(el('p', 'pa-printpage-note', ...))` precedes the loop that appends each `pa-foldcard`; `face(title, rows)` constructs rows but has no privacy notice. Original print CSS constrains cards to 2.125 inches tall and clips face overflow. These are source observations, **not physical output or computed CSS/browser proofs**.

**Safety result: a printed-page warning does not automatically accompany a separated wallet card.** The R262 candidate is a partial draft, not a privacy remediation PASS; child names, locations, school/care information and personal data on a lost card require an editor's separate risk decision. No claim is made that the proposed notes render without clipping, or that removing sensitive fields makes the card safe.

## Engineering gate

New module `tools/r263_wallet_cutout_privacy_witness_hold.py` (Git blob `d07b2e504c0c5cf0c4d1e900e81d79740bb587ea`) and 73-test regression suite `tests/test_r263_wallet_cutout_privacy_witness_hold.py` (Git blob `95e65ffc8d305ae010078842f276a4978db25b60`) operate only on bytes and a candidate held in memory. New pre-export R220 check authenticates the exact R263 blob before running and again at audit completion.

R263 invokes the authenticated R261/R262 candidate path, checks its source SHA, original citation/link token order, 13 no-JS fields, two card faces, original wallet dimensions and clipping rules, placement of *both* printed-page warnings, corrected functionality copy, and every privacy/medical/QD/release negative state. It explicitly returns:
`wallet_cutout_has_privacy_warning=false`, `printed_card_privacy_resolved=false`, `actual_browser_and_physical_cutout_qa_completed=false`, `qualified_child_privacy_review_completed=false`, `requires_editorial_resolution_before_publication=true`.

Changes to the witnessed original or candidate cannot silently flip these negatives to PASS. The original article and tool bodies, 35 article routes, 2,000 citation occurrences, seven frozen contributor heads, and release states are untouched.

## Test evidence / explicit limits

- **73/73 synthetic isolated Python unittest PASS**; `py_compile` PASS against the locally executed module/test files. GitHub committed blobs read back equal exact executed local Git hashes.
- Independently retrieved authentic Tool #104 from GitHub: original CSS/card/JavaScript/face/no-JS anchor strings each occur exactly once; no-JS source has 13 labels and two card faces; source notice is outside cutout. This is independently checked source-level evidence.
- **NOT EXECUTED:** full native `python -I preparedness/tools/validate.py`, `python -I preparedness/tools/build.py`, inherited 36+ tests, full R220/R263 authentic Python audit, actual 41 WordPress draft exports, physical cutout, JS on/off browser/computed CSS tests, qualified child/privacy/medical/source review. Local execution environment still cannot resolve github.com for trusted full checkout; GitHub connector-only reads/writes are available. Static anchor review is not a substitute.
- QA #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, fixture #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` and home lead #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0` remain unmodified, draft and independent.
- Frozen R200 seven-cluster manifest `5822f9dfde21d1f3bdfc26658769d852c639438c`; all 7 original Claude branches directly compared with frozen SHA: identical (ahead 0/behind 0).

## Required independently reviewed resolution

1. **Editorial/privacy decision, not automatic source transformation:** decide whether a physical wallet card should contain only a minimal out-of-area contact and reunion cue, omit child/school/caregiver fields, include an on-card readable privacy caution, or use a separate paper-first design. Require reviewer to document residual exposure risk and avoid implying that a cut-out card retains warnings printed elsewhere.
2. **Real testing:** print JS enabled/disabled at 100% scale, cut/fold along intended edges, photograph resulting card with *synthetic* fields only, inspect privacy language and clipping at 320/360/390/768/1440px; include 200% browser zoom and disabled JS; physical paper and print-to-PDF checks. Do not use real child data.
3. **Source safety:** unresolved 32 shared-source groups; Article #7 two CDC water references and chemical-advisory stop condition; Article #20 Ready.gov disputed citation; Article #15/Tool #104 independent child/privacy assessment. No medical or QD PASS.
4. **Pipeline:** execute exact R220 → R263 native audit and entire validate/build/inherited test suite on trusted checkout; review all 35 authored manuscripts, 2,000 citation witnesses, six tools and 41 held WordPress draft exports. Stop if any original source/slug/citation/release flag drifts.

## Conversion-first acceptance (review only; no commercial activation)

| Offer → funnel | Blocker | Change / experiment | Pass/fail evidence | Owner |
| --- | --- | --- | --- | --- |
| Verified existing Grok family-contact/reunification asset → ungated published /preparedness/ | No authenticated matching creator asset_id, public post, rights, tagged URL and signed-out mobile witness in TASK-008 | Ask Grok/Praxxis for existing ID, exact hook/date, platform link and tagged landing destination, or NO MATCH; never invent social asset | UNVERIFIED | Grok/Praxxis |
| Existing free guide → optional printable family card | Warning outside cutout; source, print, child privacy and QD holds | Independently decide risk scope; run real cutout/browser/physical tests before any CTA | R263 static/synthetic TESTED, cutout privacy FAIL/HOLD | Preparedness/QA |
| Free guide → optional existing Legacy Triage PDF | Product suitability, licensed rights, credential privacy and founder acceptance not verified | Review complete PDF, privacy advice, truthful description and source provenance; no premature upsell | NOT APPROVED | Founder/Commerce |
| Optional approved PDF → customer payment/delivery | Checkout, merchant acceptance, fees, refunds, actual download not verified | Approved merchant-side test before promotion | NOT TESTED | Commerce |
| `asset_id` → qualified session → relevant CTA → confirmed lead/order → fees/refunds → net revenue | No independently reconciled order IDs, customer evidence or attribution | 7/30-day consent-respecting cohorts, de-duplicate and human-qualify traffic | NOT COMPUTABLE; no paid sales asserted | Analytics/Commerce |

**Hard hold:** no public publication, WordPress, site/menu, analytics, checkout, affiliate, creator queue, email, approval flags or expenditure. This is not a released Tool #104 fix.