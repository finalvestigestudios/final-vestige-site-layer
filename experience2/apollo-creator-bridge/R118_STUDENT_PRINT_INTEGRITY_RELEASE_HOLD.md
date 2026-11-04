# Apollo R118 — Student-print integrity & educator-use pathway (STAGING HOLD)

**Date:** 2026-11-04 (Pacific) · **Parent:** #150 · **Conversion/coordination:** #820, charter #818 · **Upstream:** R117 commit `822ec3aa2a78866bfe30195646761f821ef25f74` (draft PR #945). **Proposed draft head:** `qa/apollo-r118-student-print-integrity-20261104`. Isolated from frozen homepage PR #49 and Research Desk PR #158.

## Why this change precedes more page aesthetics

The actual R117 staging page included the original classroom question and two expandable teaching details, but had no student-specific printable worksheet. A teacher printing after expanding the suggested-answer disclosure could risk exposing the answer on the student handout. Conversely, printing with details closed could lose the supplemental prompts. This is a **source-observed print-integrity risk**, not an executed actual-page Chromium failure report. R118 adds an original, contextual, print-only activity with three independent evidence-analysis questions, nine handwriting lines, two direct NASA research references, and an explicit source-diversity / uncertainty submission check. A CSS print boundary suppresses the entire on-screen teacher answer and notes in the student packet, regardless of the `<details open>` state, while retaining the fully accessible expandable on-screen guidance with or without JS.

**Educational conversion hypothesis:** For a high-intent secondary educator arriving from a Grok long-form Apollo 1 video, a genuinely usable free source-criticism worksheet reduces mistrust and lets the educator evaluate future FV classroom offerings. It is a hypothesis, **not a sale, lead, buyer, paid offer, or proof of demand**. The only primary CTA is the original free in-page classroom exercise. Do not insert a merchant destination until a matching rights-cleared product, license, fulfillment and return terms are independently verified and founder-approved.

## Built — exact changed paths

- `experience2/apollo-creator-bridge/landing-preview.html`: print-only **Student evidence worksheet** (3 prompts, 9 writing lines, dated-photo/event distinction, 2 NASA links), explicit print/screen CSS separation. No new JS, external media, forms, scripts or commerce.
- `experience2/apollo-creator-bridge/qa_r113_print.py`: actual-page Chromium matrix adds pre-print no-leak check; opens the teacher answer to mimic a realistic use case; confirms worksheet visibility and teacher-answer suppression after switching to print, 3 questions, 9 blank lines, source and uncertainty text. Inherits JS/no-JS widths 320/360/390/768/1024/1440/1920, touch/keyboard, the PDF and screenshots, lab LCP/CLS and fail-closed axe gate.
- `experience2/apollo-creator-bridge/qa_r118_student_print.py`: offline SOURCE-only print contract; rejects missing screen concealment, missing print boundary, additional CTAs, dropped source references, rights wording or writing space. Prints STAGING_HOLD; does not pretend to certify browser output.
- `experience2/apollo-creator-bridge/test_r118_student_print.py`: 15 new positive/negative controls checking the actual repository landing; includes duplicate attribute and answer-leak regression cases.

**Direct source and historian review:** NASA `https://www.nasa.gov/missions/apollo/apollo-1/report-of-the-apollo-204-review-board/` and `https://www.nasa.gov/apollo-1-resources/` (direct outward references; no image binary redistribution). The event chronology is distinct from the photographic chronology; no geo pins or invented edges. All six photograph-specific commercial-use assessments remain **0/6 cleared** and proposed crew-photo identifier `S67-19766` remains **provisional**, pending separate review. Do not infer usage permissions from NASA's broad media guidance.

## Reproduction and test honesty

Run against checkout-free actual staging HTML once Python/Chromium are functioning:

```bash
python -I experience2/apollo-creator-bridge/qa_r118_student_print.py
python -I -m unittest discover -s experience2/apollo-creator-bridge -p 'test_r118_student_print.py' -v
python -I experience2/apollo-creator-bridge/qa_r117_delivery_boundary.py
python -I experience2/apollo-creator-bridge/qa_r116_nasa_custody.py
python -I experience2/apollo-creator-bridge/qa_r113_print.py \
  --html experience2/apollo-creator-bridge/landing-preview.html \
  --out /tmp/apollo-r118-real-page \
  --chromium /usr/bin/chromium \
  --axe /path/to/reviewed/axe.min.js
```

**RUN EVIDENCE:** Read-only exact GitHub-source checks passed for 13 source-presence invariants after updating the actual branch. The new 15 Python tests are **AUTHORED / NOT EXECUTED**. The real-page Playwright, PDF text/extraction, touch and keyboard acceptance, axe-core four scans, LCP/CLS six lab trials, manual accessibility review, WordPress/Assembler integration and reproducible screenshot/manifest production are **NOT EXECUTED**. The execution container/Python runtime returned `redis.exceptions.ResponseError` on attempted commands; this is an execution blocker, not a passing test. No new screenshot, PDF, CWV or paid transaction evidence is asserted. Fail-closed exact-head CI and real browser acceptance remain mandatory.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL EVIDENCE → OWNER

| Rank | Offer → step | Blocker | Change / experiment | Evidence | Owner |
|---|---|---|---|---|---|
| P0 | Apollo educator casefile → merchant-confirmed paid order | No independently verified existing rights-cleared Apollo SKU, delivery, price, refunds | Read-only inventory of current sellable FV offers; validate merchant fulfillment before any purchase CTA | **NOT VERIFIED**; no attributed sales | Claude / Growth / founder |
| P1 | Grok video (`asset_id`) → Apollo → usable free source worksheet | Teacher/student answer leakage and incomplete print experience risk; real-browser QA outstanding | R118 print-separated worksheet and 14-configuration acceptance assertions | **BUILT; 13 exact-source checks; browser NOT EXECUTED** | Apollo; Grok scripts/distribution, Praxxis independent creator review |
| P2 | Worksheet → approved contextual paid education resource | Matching merchant listing and founder launch approval missing | Keep only existing free exercise CTA, pilot matching product only after rights + seller evidence | **BLOCKED** | Claude / founder |
| P3 | Purchase → refund/fee-adjusted net per 1,000 qualified human sessions in 7/30-day cohorts | No linked first-party sessions and independently confirmed merchant orders | Use existing #820 `utm_source`, `utm_medium=organic_social`, `utm_campaign`, `utm_content=asset_id`; no scripts added | **NOT COMPUTABLE** | Claude / Growth |

**Cross-lane:** TASK-008 / Grok owns content and posting. Praxxis owns independent creator QA and the handoff. This sprint neither overwrites Drive task boards nor declares an Apollo campaign posted. No WordPress writes, email sends, affiliate activation, paid services, analytics changes or production releases. The existing published Evidence Atlas approval state requires separate reconciliation.

## Gate: STAGING HOLD — DO NOT MERGE OR DEPLOY

Before any release: (1) actual source unit suites and real full-page Chromium/axe/print PDF acceptance on exact head; (2) WordPress/Assembler browser QA (including 320–1920 responsive, print, keyboard, touch, screen-reader and reduced motion); (3) NASA image-specific rights and Research Desk crew-ID correction; (4) independent editorial QA; (5) verified offer/merchant and source-linked attribution when commercial activation is proposed; (6) founder release approval and rollback snapshot. Homepage PR #49 / research desk PR #158 remain unchanged.
