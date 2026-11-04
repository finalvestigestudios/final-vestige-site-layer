# R113 — Preparedness free-guide citation visibility and conversion HOLD

**2026-11-03 PT. DRAFT, PRIVATE, HOLD.** Preparedness only: Issue #136; commercial issue #820 and charter #818; Grok/Praxxis TASK-008. This is not permission to publish or deploy any public changes.

## Specific R112 defect closed

R112's source regex counts citations inside HTML comments, attributes or hidden/nonreading elements as if they support visible article claims. It also lacks a full reading-depth floor. R113 adds a read-only HTML visibility gate that rejects concealed citations, scripts, broken nesting and duplicate HTML IDs; requires full visible citation scopes and source-use descriptions; and refuses an abbreviated manuscript even if an emergency action box survives. These are structural checks, **not factual verification, source approval or medical-safety approval**.

Frozen original Git blobs from R112 exact head fee3a49db04d6c4da8525bce78e1c5f38447d56d:
- household-emergency-plan.body.html: 8ca5c261dba56eeaf79c445332381a74867233de
- household-emergency-plan.meta.json: 0681d51e6e29166eaae27ac2b7f1fbde3f836787
- preparedness/taxonomy.json: eea601e53e16e36cd4fc890876bc249b39632370

R113 checks every raw Git blob before semantic checks; any legitimate editorial/safety change must be human adjudicated and re-baselined, not auto-trusted. It also checks all 35 unique slate routes, author-specific 14 source IDs, 40+ visible citation occurrences and minimum reading depth; original article has 57 occurrences and about 3,200 whitespace words. It preserves editor=drafted, publish=draft, safety_review=pending, the complete source material and the QD HOLD. No manuscript or source file was changed.

## Offer and funnel

Audience hypothesis: a household choosing an out-of-area contact, meeting place and practice rehearsal. Original free source-backed draft: item #1, household-emergency-plan. **Proposed URL only, not independently live/safe:** https://finalvestige.com/preparedness/start-here/household-emergency-plan/

**Commercial HOLD:** No independently verified, genuinely purchasable, rights-cleared, FV-owned and delivered Preparedness Payhip SKU is established. Public examples on Payhip from other vendors are not FV inventory. The one paid-toolkit category remains an unverified hypothesis, not a product listing, checkout URL, price or conversion. Do not revive retired water freebies or misdirect this audience to the Seven Day Focus Fieldbook. The R113 private WordPress-ready preview contains only non-clickable copy; the optional paid card is omitted.

Proposed free copy (unpublished): “Plan an out-of-area contact, a meeting place and a practice day. The complete source-linked household guide remains free. Follow local emergency officials during an active emergency.” The preview explicitly states that the guide is not published and no FV paid Preparedness offer has been verified.

## OFFER → STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL EVIDENCE → OWNER

| Priority | Offer / funnel step | Blocker | Change / experiment | Evidence | Owner |
| --- | --- | --- | --- | --- | --- |
| P0 | Existing owned paid household-planning SKU → verified order | No seller-origin ownership, SKU, rights, price, file/delivery, refund/fee receipt | Verify one real current product/fulfillment via account and permitted safe checkout before any buy CTA | HOLD; no live buy link | Claude/Growth + founder |
| P0 | Free original guide → safe substantive reading | Pending qualified review, 23 changed contributor paths, 30 multi-author shared URLs | Pin complete originals, reject concealed citations/depth loss, then obtain independent source/safety review | Structural code built; human support/safety unverified | Preparedness + qualified reviewer + Site QA |
| P1 | Grok high-intent asset → free guide | No asset ID, post URL, link-route acknowledgment and live destination | TASK-008 Grok asset/link inventory; Praxxis fit/rights check; Claude/Site QA staged landing test | HOLD, no attributed sessions | Grok, Praxxis, Claude |
| P1 | Optional paid card → delivery | No merchant acceptance, disclosure/license/returns/mobile QA | After real SKU verification, stage honest optional offer adjacent to fully free content and test keyboard/360/390/768/1440/print/no-script and approved merchant handoff | NOT TESTED, paid card omitted | Claude, Site QA, founder |
| P1 | Qualified sessions → paid orders/refunds/fees → realized net/1000 | Unique humans, order-source join, refunds and fees absent | Existing #820 privacy-safe event scheme and 7/30-day merchant cohort reconciliation; no duplicate scripts or PII | KPI N/A, never 0 or sales inferred from clicks | Growth, Claude, Praxxis |

## Tests, evidence and remaining release blockers

Committed focused tests cover independent adversarial mutations of hidden/visible citation markers, source-use drift, duplicate URLs, shortened prose, warning loss and HTML manipulation; tests run in GitHub Actions only if its runner starts. A broader *locally authored related R113 prototype* passed 85 synthetic Python tests and compilation, but that is **not proof of exact committed-head execution**. Native validator/build, full suite, R111 real Git integration, browser, checkout and mandatory release integrity remain unverified until independently observed. CLI: python -I preparedness/tools/r113_preparedness_landing_custody.py --repo-root .

Seven Claude contributor branches, one Preparedness RC, QA PRs #157/#169 and homepage PRs #49/#604 must remain untouched. PR #157 has no independent QD pass. PR #169 retains an in-tree _dup_test.json write in its synthetic fixture test. Existing 23 contributor-file differences, 30 URL collision groups, 15 safety exceptions, 22 editorial decisions, five unfinished tools, qualified guidance review, browser/print QA, mandatory 13-stage integrity and independent QD all remain HOLD.

No WordPress, CMS, navigation, public site, homepage, product, tracking, Payhip, social posting, emails or merchant financial writes.