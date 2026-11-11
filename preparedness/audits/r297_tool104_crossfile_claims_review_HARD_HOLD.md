# R297 — Tool #104 No-JavaScript / minimal-output / privacy cross-file review

**Date:** 2026-11-11 PT · **Status:** DRAFT_HARD_HOLD · **Publication/QD/medical/privacy/merchant approvals:** NONE  
**Owners:** Preparedness integration (#136) mechanical witness only; independent Preparedness QA owns editorial/print/privacy acceptance; Claude core web; founder release; Grok/Praxxis creator TASK-008 (#820, #818).

## Direct authenticated Git witness — checked against R296 HEAD 82f2ca9adeeed7a98343098a7bc42f4eec9dcf14

| Path | Git blob |
| --- | --- |
| content/tools/family-reunification-card.body.html | be8698ac5d020476ff649d85813810e2000c6f98 |
| content/tools/family-reunification-card.meta.json | 47da1e7e20e39f0ea85e26d54a8d58301f6e0a15 |
| tools/reunion_card.js | b1a09b1eda1ae26f081de65b400a37bc19538035 |
| audits/r200_seven_cluster_35_article_frozen_custody.json | 5822f9dfde21d1f3bdfc26658769d852c639438c |

Paths are relative to preparedness/. All four were independently read at that exact R296 commit. Frozen custody says **35 article originals / 41 proposed article+tool draft targets, DRAFT_HARD_HOLD**. These counts are *targets*, not proof that exporters produced or reviewed 41 valid WordPress drafts.

## New mechanically grounded acceptance issues, not editorial adjudications

1. **T104-NOJS-001 — explicit source contradiction:** The body at line 89 promises that the no-JavaScript form "still works and prints," but line 132 hides #rc when JS is off; line 91 assigns the form class pa-card-mainhide and line 83 hides that class under @media print. A separate blank handwritten card exists at line 131. Browser, no-JS and real printed output must be independently tested. Do not claim the data-entered form prints without JS.
2. **T104-MIN-002 — additional data on the supposedly minimal card:** Body line 94 limits its advertised contents to out-of-area contact, a phone, first meeting place and review date. The rcModel front list at JS lines 39–40 also includes household name/nickname and household phone, plus out-of-area name/phone and first meeting place. This may exceed a reader's minimal-disclosure expectation; it is not proof of a sensitive-data leak. QA must choose between *actually reducing rcModel's minimal fields* and accurately describing a less-minimal output. Printing a lost card is a real-world privacy consideration.
3. **T104-PRIV-003 — untested absolute storage promises:** Body line 9 states information is not sent/saved and tab close clears it; metadata description says "Nothing is stored." A JS source comment is not sufficient to prove request/network/cache/autofill/session/browser/WordPress behavior. Require browser devtools, privacy threat review and consent checks; no contact data in test fixtures.
4. **T104-911-004 — citation scope and audience distinction:** Body line 9 pairs life-threatening 911 calls with texts for "everything else", citing shelter-ready-tech. This does NOT explicitly tell readers to text 911; the concern is that household check-ins and emergencies requiring immediate dispatch are ambiguously blended. R296 identified candidate National 911 Program/CDC source checks; do not auto-edit citation registers or imply an independent approval. Note the source wording may follow older Ready.gov language; a qualified reviewer must resolve claim scope.

**Unchanged source IDs, original HTML/JS, metadata, status, safety flags, URLs and WordPress exporters.** Source verification is not actual browser observation, safety validation or QD signoff.

## Tool/test evidence

- **Added:** tools/r297_reunion_privacy_print_crosswalk_hold.py (Git blob 8991fb33a2b2041c6b59297a41e8928d45b787a3), tests/test_r297_reunion_privacy_print_crosswalk_hold.py (Git blob c27ece4d16c20b832a304fb2d3b6d1e0ace1992c). New Python synthetic tests: **51/51 PASS**.
- Inherited archived R295/R296 synthetic suites + exact new R297 files: **166/166 PASS** (55+60+51) in bounded local setup, Python 3.13; no full native repo validation/build executed. Exact new committed blobs were independently read back and matched local test-executed blobs.
- Incomplete local archive run returns **INVALID_HARD_HOLD (exit 1)** with four missing authentic source witnesses; does not imply a regression in valid source. Fully authenticated output would still be **DRAFT_HARD_HOLD (exit 2)**; no zero/approval path.
- Source-level class/regex matching on a pinned artifact is not a browser accessibility/printing/JS/consent test. New code is deliberately restricted to review receipts and never writes to CMS or safety states.

## Coordination / current-ref checks

- Authentic R200 Git baseline vs seven named Claude contributor branches freshly compared: **7/7 identical, 0 commits ahead/behind, 0 changed paths**. Corrects the superseded R293/R294 baseline misclassification; no content rewrite.
- Independent QA **PR #157** open/draft HEAD 7d1ae6b8ef93d10cfb6810987672360885e9c1aa; synthetic fixture **PR #169** open/draft HEAD e9cd7766dac59d47ab467d8945269b9146c2aef5. PR #169 still has test_register_fragments_cannot_duplicate_ids writing ROOT/sources/fragments/_dup_test.json at lines 71–78. One other fixture now uses a temp sandbox. Independent QA owner must fix the remaining write; do not alter their branch.
- Homepage lead **PR #1689** open/draft HEAD f55c36b6598eec558dd8bb24e4c8988becc51be0. Do not touch or replace the existing /focus/ lead-magnet system.
- Previous R296 **PR #2074** open/draft HEAD 82f2ca9adeeed7a98343098a7bc42f4eec9dcf14; this R297 is stacked on that exact head, no original files changed.
- Existing 21 historical discrepancies, 32 shared-URL groups, 15 duplicate source-ID groups, eight historic-food alias occurrences, disputed agency citations, Article 7 chemical advice and Article 15 family-communication privacy hold remain unresolved.

## Conversion-first cross-lane gates — OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER

| Offer | Funnel step | Blocker | Review-only change / experiment | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Official free preparedness resource (no email/paywall) | Existing social visitor → free household-planning destination | No authenticated matching published family-reunification asset ID/mobile route in TASK-008 | Review an existing creator asset, rights, UTM content=asset_id and a real mobile click; no new creator assignment | NO VERIFIED MATCH | Grok/Praxxis |
| Free archive → optional free card | Article → Tool104 / print | Four source/copy and browser/privacy discrepancies | Resolve no-JS contradiction, true minimal field set, emergency distinction; test actual 360/390px, JS off and paper/PDF print in browser | R297 51 synthetic PASS; independent acceptance HOLD | Preparedness QA |
| Optional existing paid FV pack | Free guide → paid checkout/delivery | No verified rights-cleared, live purchasable and family-reunification-fit SKU | Founder/Commerce verify exact seller/rights, customer terms, merchant checkout, refund and download fulfillment before CTA | NOT APPROVED; Legacy Triage public Vested Wisdom listing is not FV ownership proof | Founder/Commerce |
| Verified commercial sale | Attributed human visit → legitimate paid order → fees/refunds → net | Merchant settlements and traffic attribution missing | Consent-respecting 7/30-day cohorts using existing Claude-owned analytics, no extra scripts | NET REVENUE/1,000 QUALIFIED HUMAN SESSIONS **NOT COMPUTABLE** | Claude + Commerce |

Draft free CTA, **not published**: “Make a plan to reconnect. Start with official, free preparedness resources.” Existing free archive: https://finalvestige.com/preparedness/ . No retired water freebie, unapproved paid CTA, email, product, affiliate activation or CMS write.

**Next actions:** Independent QA reviews corrections/options; obtain complete authenticated source checkout; native Python build/validation and all 41 *draft* export checks; inspect browser/print behavior and safety-source signoffs. Founder separately approves any eventual public release.
