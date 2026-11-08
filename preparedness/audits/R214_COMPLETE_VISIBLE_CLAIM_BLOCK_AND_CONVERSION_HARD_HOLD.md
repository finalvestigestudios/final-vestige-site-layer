# R214 — Full-claim block source review safety gate (DRAFT / HARD HOLD)

Owner: Preparedness Archive integration, Issue #136 only; conversion coordination #820 / charter #818.
No merge, publishing, WordPress/CMS/nav, live scripts, email, affiliate activation, social posting, or spend.

## Source-review problem
R213's held-citation docket uses a 320-byte window on either side of each citation, strips HTML with regex and may truncate an element or interleave adjacent list items. That can cause a qualified reviewer to read an incomplete or misleading excerpt without seeing the full statement the citation is attached to. R214 is a separate optional read-only safety companion, not a replacement for R212/R213 receipts or human adjudication.

## Exact engineering deliverable
- New preparedness/tools/r214_visible_claim_block_gate.py imports the authenticated R212/R213 HOLD result only in its CLI, and pure evaluate_from_docket() verifies original Git blob bytes, unique receipt SHA-256, marker byte span, and three exact occurrences (Article 7 twice, Article 20 once).
- HTMLParser identifies the smallest fully closed P, LI, heading, table-cell, blockquote or figcaption containing the source citation, rather than arbitrary 320-byte context. Returns raw-block byte boundaries, SHA-256 of the exact raw block, Unicode-decoded human-readable claim text and a second SHA-256. It explicitly detects a citation hidden in an HTML comment/attribute or an unclosed/misaligned block and remains INVALID_HARD_HOLD.
- No source-verification, review, QD, medical-safety, commerce or publication state can become true. On valid frozen originals CLI prints a docket and returns exit 2 = DRAFT_HARD_HOLD; invalid returns exit 3. Neither state is a PASS.
- New preparedness/tests/test_r214_visible_claim_block_gate.py has 90 discoverable Python unittest tests, including 70 individually discoverable synthetic claim-text or exact-byte-span corruptions. All asserted intact baseline HOLD first and then required INVALID after mutation; 20 additional tests cover full-block boundaries, hidden/unclosed markup, Unicode, HTML entities, determinism, invalid approval states, duplicate receipts and reader input.
- Existing 35 original articles, seven contributor branch heads, source register, WordPress exports, and prior QA branches untouched.

## Exact local execution (2026-11-08)
python -I -m unittest discover -s preparedness/tests -p 'test_r214*.py' -q => 90/90 PASS.
python -m py_compile preparedness/tools/r214_visible_claim_block_gate.py preparedness/tests/test_r214_visible_claim_block_gate.py => PASS.
Exact Git blobs matching the locally tested files: tool 368776765f08cc4886fad331cea16ecbbb0e5768; test 5e4dbee5f4980be2ba1dccb10fecc58a8c3cc868.
Tests are synthetic, not real-authored 35-article integration, native validation/build or independent review.

## Source custody and independent QA
Seven frozen contributor commits checked as IDENTICAL to their current named Claude refs using GitHub comparisons:
start 2122d856fce9f64887c16df3d52e64be9f59a55b;
food f911ff7a655de8d81535ea86ec3d65a49ee76648;
shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976;
health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17;
hist-field 4e5caf812727953aa45e3bda2d382f2c67b6a09c;
hist-food 67e116e536c7410bed30f8f3b1bb8c166f3c223d;
hist-home 7504a5f099594d635e3dd7332a33a2e1346c43a2.
QA PR #157: 7d1ae6b8ef93d10cfb6810987672360885e9c1aa; fixture PR #169: e9cd7766dac59d47ab467d8945269b9146c2aef5; stacked #973: 4d40996a559b0124d74a9bb3bdcd481ad1992aa8. These are older, unmerged drafts; never overwrite newer content or blindly transplant test files.
Frozen slate: 35 article routes, 41 planned outputs; no new destination.
Still held: Article #7 two cdc-find-clean-water occurrences (water heater versus space-heating tank, only originally uncontaminated ice, chemical/fuel caveat); Article #20 one start-ready-plan occurrence (languages). Seven historical source-identifier collisions and independent safety/QD review remain unresolved.

## Verification limits / blockers
Trusted complete repository cannot be cloned in local runtime because GitHub DNS resolution fails, although connected GitHub read/write API succeeded. Native python -I preparedness/tools/validate.py, python -I preparedness/tools/build.py, entire inherited Python suite, authenticated original 35 article and 41 WordPress output parity, current WordPress full browser/print test, and authentic R214 CLI with six original files NOT EXECUTED. A synthetic PASS has no authority to change human_link_check or medical-safety state. Original QA #157 negative-test equivalence and all held citations still need qualified human adjudication.

## Conversion-first separate research lane (#820)
One audience: households organizing emergency contacts, record locations, insurance information and fallback decision-maker instructions.
One ungated, already-live free destination: https://finalvestige.com/preparedness/ (read-only public check 2026-11-08). Do not use retired water freebies or an unpublished guide as a live destination.
One optional candidate: Legacy Triage, public $19 PDF listing at https://payhip.com/b/n1RhV (merchant page says Vested Wisdom, not independently authenticated as FV-owned; 580KB description); this listing is NOT merchant-verified rights, purchase, delivered content, support/refunds or realized revenue. Do not activate a sale link or paid CTA.
Offer → free archive → intent-matched optional product: blocker = unverified Grok published asset ID/destination, citation/human QA, seller ownership/rights, consumer intent, mobile access, pay/deliver/refunds and purchase attribution. Experiment = read-only TASK-008 asset reconciliation, independent source review, founder-authorized merchant E2E staging. Evidence = current free page/live and public listing only; NO authenticated completed checkout or product fulfillment. Owners = Grok/Praxxis social ID, Preparedness/QA sources, Founder/Commerce merchant, Claude analytics.
Only merchant-confirmed paid orders/cleared affiliate conversions less fees/refunds count as realized net revenue. Qualified-human 7/30-day sessions, attributable sales and fees unavailable; net revenue per 1,000 qualified-human sessions NOT COMPUTABLE, NOT ZERO. No new tracking script, email, social post or commerce action.

## Required reviewer sequence
1. Run authenticated six-file CLI and inspect complete HTML claim blocks with exact bytes; independently review source meanings, conditions and dates, then handle historical crosswalk conflicts.
2. Reconcile #157 / #169 / #973 test intent without destructive content overwrites.
3. Once complete trusted checkout is obtainable, run native validate/build/full tests + 35 body/41 export citation parity, route and reading-depth checks, staged browser/print/accessibility.
4. Keep independent QD, qualified safety editorial review and founder release approval as separate non-scriptable gates.

DRAFT / HARD HOLD is final; no approval or public changes.

## Final independent test integrity correction
Five added R214 negative cases repin deliberately modified synthetic bodies and rebuild the exact citation spans BEFORE execution, ensuring failures are attributable to hidden markup, HTML attributes, comments, script-only citations or broken nesting—not merely stale blob fingerprints. Each checks the specific rejection reason. Final exact-code total: 90/90 Python unittests PASS and Python compilation PASS, final test blob 5e4dbee5f4980be2ba1dccb10fecc58a8c3cc868. Current home lead is separate draft PR #1568 HEAD e8176caa9d3d1dcc5bd47f0cf6dd1b5d16d11ebf. No real-body/native-source approval established.
