# R315 · HTML5 browser semantics and citation-source integrity — HARD HOLD

Issue [#136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136), conversion acceptance [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), charter [#818](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/818). Preparedness-only, read-only, original manuscripts/metadata/citation registers/taxonomy/routes unchanged.

## New integrity risks and release guard

**HTML5 nonvoid self-closing:** The existing R313 HTMLParser accepts `<script/>`, `<template/>`, `<strong/>` and similar nonvoid HTML elements as self-closed. In browser HTML parsing, their slash does not generally close an HTML nonvoid element. This can create parser-versus-browser disagreement about citation visibility or author warnings. R315 explicitly flags nonvoid self-closing HTML markup, while preserving legitimate HTML void self-closes and foreign SVG/MathML self-closing syntax, including HTML integration-point handling for `<foreignObject>`.

**Entity-materialized citations:** `&#123;&#123;cite:source-a&#125;&#125;` may render as a citation-looking marker without being a literal `{{cite:source-a}}` source token for the archive builder. R315 compares decoded citation occurrences against the raw source-token occurrence multiset and rejects source-token laundering without rewriting author content.

**Other citation concealment:** The older hidden-style check covers `display:none` and `visibility:hidden`, but not transparent text, zero opacity or font-size, content-visibility, inset clipping, and zero-scale transforms. R315 treats those inline CSS patterns as possible hidden citation evidence and refuses to equate machine-visible tokens with reader-visible claims. These are conservative evidence flags, not comprehensive browser layout or screen-reader validation.

**Inherited gates:** R315 independently pins unchanged R313 code blob `209457045d1d44a18a26c1e2e31ddb8541bad49c` and R314 code blob `c46c5f7a9d1c691ba5f19268a3215ebd5ae85589`; source custody and safety-state checks remain inherited. All release, medical, QD, WordPress-export and merchant-order fields remain negative.

## Exact local execution

- Code Git blob: `e0518450c3b45e5e8b59a2f5d0f801279be4821b`.
- Test Git blob: `8512dd34fde83b9c6dcbaff675be5afaf0a068c3`.
- Locally executed byte-identical source/tests: 422/422 Python tests passed (297 inherited R310–R313 + 74 re-executed R313 fixture cases under R315 + 51 new HTML5/CSS/entity cases). Python compilation passed.
- Incomplete native checkout negative control: exit 1, `INVALID_HARD_HOLD`.
- Current complete GitHub checkout is unavailable to local Python owing to GitHub DNS resolution. No native `validate.py`, `build.py`, full source 35+6, generated HTML, browser/printing/no-JS, WordPress export, customer-funnel or independent safety/QD approval was executed.
- This is a validator regression demonstration, not an authentic 35-article publication PASS.

## Upstream coordination

Canonical seven Claude contributor heads compared with frozen R200: 7/7 IDENTICAL, 0 ahead, 0 behind. Additional Shelter continuation remains +6 and follow-up evidence +9; neither merged or silently substituted. Independent QA PR #157 draft HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic fixture PR #169 draft HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5`, and its second `_dup_test.json` writer still touches a source-directory location. Homepage lead #1689 draft HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0`, untouched. R314 draft #2184 HEAD `327e16c6d6091a5f21bb9c472458a5dfa221611f`.

Ongoing substantive holds: ten editorially changed article bodies and twelve metadata records; two misleading approval fields; duplicate USDA source custody; Article #7 hazardous-water; Article #15/Tool #104 emergency calls, texting, child privacy, JavaScript/printing/accessibility; distinct Tool #102/#104 and duplicate tool numbers; all 41 authentic exports and independent QD.

## Conversion-first bounded handoff

**Audience:** households planning family communication/reunification. **Free destination:** already-live https://finalvestige.com/preparedness/ with official resources; detailed guides remain unpublished and must not be described as live. **Optional free practical tool:** Tool #104 is a draft, held for dual-surface emergency, privacy, printable/browser and qualified safety review. **Optional paid Preparedness pack:** NOT SELECTED: no independently verified FV-owned/licensed currently purchasable and deliverable fit-matched SKU. Public Payhip results for unrelated sellers are NOT FV offers. No paid CTA authorized.

| Offer → funnel | Blocker | Change / acceptance check | PASS/FAIL evidence | Owner |
| --- | --- | --- | --- | --- |
| Actual published Grok family-contact asset → free official-resource destination | Published `asset_id`, rights, permitted campaign URL and mobile audience landing not verified | Require existing TASK-008 asset ID, exact landing and platform-safe UTM mapping; inspect mobile load and matching promise | UNVERIFIED | Grok/Praxxis |
| Free landing → optional #104 | Both article and card lack qualified 911/texting/privacy/print review | Distinguish free official resources from unpublished tools; keep #104 hidden pending signed-off reviews | HARD HOLD | Preparedness/QD |
| Free guide → paid Preparedness pack | No authenticated owned/licensed payable SKU, delivery or refund terms | Founder/Commerce verify actual SKU, rights, checkout, mobile deliverability and returns; only then draft paid CTA | NO OFFER APPROVED | Founder/Commerce |
| Paid order → net revenue | No authorized paid transactions/qualified session denominator/fees/refunds | Reconcile consentful asset_id + UTM → visit → CTA → confirmed lead → settled paid order → refunds/fees by 7/30-day cohorts | NOT COMPUTABLE | Claude/Commerce |

Primary KPI only when verified: **realized net revenue per 1,000 qualified human sessions**. Never equate CTA clicks, registrations, checkout starts or traffic with completed purchases. Tiny-sample warnings required.

## Release boundary

DRAFT / HARD HOLD. No public publishing, CMS/navigation writes, original content rewriting, Grok production, paid merchant activation, analytics scripts, email, order attribution claim, independent-QD PASS or spending.
