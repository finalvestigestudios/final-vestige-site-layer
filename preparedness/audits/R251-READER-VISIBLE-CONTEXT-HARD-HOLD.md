# R251 — Preparedness reader-visible context safety gate (DRAFT / HARD HOLD)

Date: 2026-11-09 PT. Scope: Issue #136; business attribution issue #820; charter #818.

## Gap and evidence

R249's draft-only copy parser allows arbitrary attributes other than enumerated prohibited ones. In particular an HTML `popover="auto"` attribute was not on the rejection list, yet the parser consumes the popover's paragraph data as ordinary reader-visible text. A later edited copy containing mandatory caveats inside a popover could satisfy keyword-only disclosure requirements without showing the warnings on initial load. This is a **source-level gap**, not a confirmed production exploit. No existing R249 preview content uses popovers. R250's source-to-reader six-field ledger also counts paragraph text without independent browser visibility.

R251 introduces an **independent, additive**, read-only allowlist parser for the **existing unsigned R249 draft**, preserving its authentic Git blob `ce5c363786deb0296f78598818af1fd7abefae65`. It accepts only the original section, two headings, seven directly visible paragraphs and single /preparedness/ anchor. It rejects `popover`, hidden/conditional attributes, nested foreign elements, event handlers, rewritten disclosure paragraphs, commercial links, displaced cautionary phrases, and loss of the HOLD-only notice badge. It verifies the R249 prior-result SHA-256, issue numbers and false approval flags before emitting a deterministic report labeled `UNAPPROVED_OFFLINE_READER_COPY_ONLY`.

New gate blob: `677285daafbd53ab3bd2b5ea71e4a84a211bb30a`. Test blob: `042d343450bf5a973e0024c2f65909e2385c5618`. R220 loader blob after integration: `91cb4eca9d1a6ae96c371fceb5df4a03a6691261`. The R220 path authenticates the R251 blob, executes it after R248/R249/R250 checks and **before** WordPress draft rendering; it rehashes the gate at end.

## Test scope and blockers

Local isolated `python -I -m unittest discover -s preparedness/tests -p 'test_r251*.py'` **88/88 PASS** and `python -I -m py_compile` PASS. Of 88 methods, 81 generated adversarial mutations (27 paragraph attributes, 9 section attributes, 21 foreign wrappers, 14 redactions, 10 structural drifts) and 7 additional controls. Tests ran against a byte-matched R249 preview fixture and local module whose Git blob is identical to the new committed file. The R249 upstream receipt was synthetically modeled for these isolated cases. No genuine original Tool #104 browser, print, storage/network, or WordPress rendering was executed.

Local native repository checkout remains unavailable due GitHub DNS; `preparedness/tools/validate.py`, `build.py`, inherited 36+ tests, 35 original manuscripts / six tools / 41 export outputs were **NOT EXECUTED** this run. The earlier 35/2,000-citation census is inherited, not freshly repeated. Thirty-two multi-use source groups and three disputed occurrences (CDC Article #7 ×2; Ready.gov Article #20 ×1) await human adjudication. Article #15/Tool #104's minimal-card privacy, no-JS form and written-plan claims, plus 11 editorial proposals, remain HARD HOLD. No medical, independent QD, privacy, sales or publication clearance.

## Conversion-first acceptance contract — NOT A SALES CLAIM

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Existing Grok creator asset → authentic free /preparedness/ guide | Matching live asset ID, rights, original hook/date and signed-out mobile link **UNKNOWN** | Praxxis verify **already published** Grok asset in existing TASK-008; do not modify creator queue | Unverified | Grok/Praxxis |
| Free family communication guidance → optionally printable card | Original Tool #104 privacy and no-JS copy conflicts; draft review text must be reliably visible | R251 offline notice guard then qualified editorial choice and native browser/mobile/print/network acceptance | R251 isolated 88/88 PASS; original tool NOT TESTED; HARD HOLD | Preparedness/independent QA |
| Free guide → optional existing Legacy Triage owned PDF candidate | Rights, actual product fit and data handling not verified | Founder/Commerce review actual rights-cleared SKU and file; keep any CTA inert until authorized | NOT APPROVED; no unapproved or retired products | Founder/Commerce |
| Approved optional offer → checkout/fulfillment | Price/checkout/refund/delivery merchant proof unavailable | Authorized merchant-side verification of completed purchase, delivery and reversal | NOT TESTED | Commerce |
| Qualified-human session → reader click → confirmed lead → verified settled paid order | No authenticated creator or merchant conversion ledger | Only pre-existing privacy-approved attribution; reconcile 7/30-day asset_id/UTM cohorts with confirmed paid orders net of fees/refunds | Net realized revenue per 1,000 qualified human sessions **NOT COMPUTABLE** | Praxxis/Claude analytics/Commerce |

No additional website design, live affiliate, advertising, checkout, email form, analytics vendor or creator production is authorized. Essential safety guidance must remain free. No public navigation, WordPress/CMS, social or merchant changes; nothing merged or published.

## Fresh collaboration identities (read-only, 2026-11-09 PT)

Confirmed live Git refs against the frozen R200 manifest: `claude/prep-start-bbfeb8` `2122d856`, `claude/prep-shelter-5e1e0e` `5daeaf2d`, `claude/prep-food-ccdc55` `f911ff7a`, `claude/prep-health-837444` `d5ef5baf`, `claude/prep-hist-field-9db767` `4e5caf81`, `claude/prep-hist-food-b81f19` `67e116e5`, `claude/prep-hist-home-0e0e38` `7504a5f0`. **Seven of seven exact HEAD matches.**

Independent QA draft #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` (safety corrections, five-file patch inspected); synthetic-fixture draft #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` (isolation test patch inspected); homepage lead #1689 `f55c36b6598eec558dd8bb24e4c8988becc51be0`. Parent R250 #1811 `542f193c1ddd9214458c50197600057b2cd49253`. No changes made to any collaborator branch. The seven-branch SHA check verifies branch heads, **not** the medical correctness or rendered citation safety of the 35 articles.
