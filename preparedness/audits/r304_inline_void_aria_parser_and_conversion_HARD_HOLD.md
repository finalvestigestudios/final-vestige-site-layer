# R304 — Inline void/self-closing and ARIA attribute parser hardening (#136)

**2026-11-11 PT · DRAFT / HARD HOLD · NO PUBLICATION · NO QD PASS.**
Parent: R303 draft PR #2118, exact baseline `4792e8e487d5a70b0f03175c8848fc206405eb58`. Scope restricted to Preparedness validator, synthetic tests, and this audit; no original manuscript, source register, URL, metadata, tool, production code, WordPress or navigation edits.

## Independent review finding and correction

Praxxis Round 313 in the existing dated TASK-008 handoff identified an edge in the R303 parser: `<wbr/>` triggers `HTMLParser.handle_startendtag`, and inherited R302's void list does not include `wbr`. The previous implementation therefore emits a spurious `INLINE_VOID_CLOSED:wbr` against *identical* source/export HTML. This is a false rejection, **not** evidence that any of the real 35 article bodies currently contains this syntax.

The bounded fix explicitly delegates slash-terminated `wbr` to the same event path as ordinary `<wbr>`. A literal `</wbr>` remains invalid. Deleting, inserting, moving or changing `wbr` and its attributes remains detectable. Broader HTML/browser equivalence is **not** inferred.

A second defensive hardening prevents a valueless `class` on an export `<sup>` from raising an unhandled `AttributeError`. For authored tracked inline elements, duplicated attributes and valueless nonboolean attributes now cause `INLINE_DUPLICATE_ATTRIBUTE` / `INLINE_VALUELESS_ATTRIBUTE` failures even when malformed source and export match. Explicit boolean `hidden`, `inert`, and `itemscope` remain accepted, but their real-world browser/accessibility behavior is not independently reviewed.

## Exactly executed test boundary

- **96 new committed R304 synthetic tests PASS**: twenty tracked inline tags × 4 perturbation patterns (80), plus 16 focused parser/fail-closed controls.
- **707 inherited R295–R303 Python tests PASS; 803/803 tests in the committed-scope suite PASS.** Python compileall PASS.
- An additional **101 private, noncommitted exploratory tests** passed locally, but are **NOT** counted toward committed-scope results. Evidence retained locally only.
- Missing authenticated repo checkout returns `INVALID_HARD_HOLD` with exit 1; no success exit or independent release state.
- The R303 code modification and new R304 test file were compared against exact GitHub blob identities after upload. **No full authenticated native** `validate.py` / `build.py` or 41 real WordPress draft exports executed; local `github.com` DNS still fails.
- 35 source article body pins, 12 metadata-lineage discrepancies, existing original citation adjudications and previous source QA remain **unresolved**. No assertion that advice is medically safe.

## Fresh coordination evidence

All seven canonical Claude cluster branches were compared directly against the exact frozen R200 commits from custody blob `5822f9dfde21d1f3bdfc26658769d852c639438c`: each reports `identical`, `ahead=0`, `behind=0`, `changed_paths=0`.

| Cluster | Branch | Frozen R200 commit |
| --- | --- | --- |
| Start | `claude/prep-start-bbfeb8` | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| Shelter | `claude/prep-shelter-5e1e0e` | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| Food | `claude/prep-food-ccdc55` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Health | `claude/prep-health-837444` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Historical Field | `claude/prep-hist-field-9db767` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| Historical Food | `claude/prep-hist-food-b81f19` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Historical Home | `claude/prep-hist-home-0e0e38` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |

Independent QA PR [#157](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/157) remains OPEN/DRAFT at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`. Synthetic fixture QA PR [#169](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/169) remains OPEN/DRAFT at `e9cd7766dac59d47ab467d8945269b9146c2aef5` and retains a source-directory `_dup_test.json` test fixture write. Homepage owner PR #1689 remains OPEN/DRAFT at `f55c36b6598eec558dd8bb24e4c8988becc51be0`. No edits to any of these PRs.

## Conversion-first guarded lane — Issue #820 / charter #818

**One audience:** households planning emergency communication and reunification. **Existing candidate free resource:** <https://finalvestige.com/preparedness/>. This is not an assertion that all original guidance or Tool #104 is cleared; free official agency resources must remain available.

| Offer | Funnel step | Blocker | Proposed change/experiment | PASS/FAIL evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| Original free Preparedness Archive guide | Matching Grok organic social visit | No authenticated published `asset_id`, rights check or approved destination | Crosswalk ONE published family-contact asset to live mobile-safe archive route, only after Praxxis/Grok TASK-008 verification | NOT VERIFIED | Grok / Praxxis |
| Free family contact guide → practical Tool #104 | Reader tool click and usable deliverable | Emergency-dispatch threshold and N911/CDC source support, child-data privacy, printable form and no-JS conflicts remain unresolved | Qualified content+privacy/accessibility/browser acceptance; do not unhold tool prematurely | HARD HOLD | Independent Preparedness QA |
| Optional paid practical pack | Guide-to-purchase intent | No confirmed FV-owned/licensed, approved, merchant-fulfillable, audience-fit Preparedness SKU | Founder/Commerce verify exact SKU, rights, checkout, delivery and refund terms **before** drafting paid CTA | NOT APPROVED | Founder / Commerce |
| Qualified human visit → CTA → confirmed lead → actual paid order | Commercial measurement | No verified end-to-end `asset_id` / `utm_campaign` / merchant order attribution, fees or refunds | Existing analytics owner reconcile consented 7/30-day sessions/orders/refunds without duplicate scripts | NOT COMPUTABLE | Claude Analytics / Commerce |

The KPI **realized net revenue per 1,000 qualified human sessions** remains unknown; an affiliate click, checkout start, signup or view is **not** a sale. Do not reactivate retired water freebies, introduce unapproved Legacy Triage offers, publish a CTA, send email, write CMS, alter Grok's task queue, purchase services, or claim conversion outcomes.

## Release gate

`DRAFT_HARD_HOLD` means only a reviewable mechanical comparison passed on a complete isolated fixture; it is **not** a passing publication state. Source claims, 14 body and 12 metadata lineage differences, Article #7 water hazards, Article #15/Tool #104 messaging/privacy/printing/accessibility, PR #157/#169 review, authentic 41-draft builder, independent QD, browser and merchant proof must all be separately resolved. Never merge or publish on these tests alone.
