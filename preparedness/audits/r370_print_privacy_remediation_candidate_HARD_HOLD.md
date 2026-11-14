# R370 — Tool #104 privacy-warning print review candidate

**Disposition: DRAFT / HARD HOLD. No source replacement, merge, publishing, CMS, analytics, social, affiliate, merchant, email, spending or QD clearance.**

Scope: Preparedness Archive integration only, Issue #136; business acceptance #820 / charter #818. Parent draft #2497 exact SHA `e98a50065326ba9c79e367561fe9cb142c4d32e8`.

## Confirmed source facts and proposed private-only diff

Authentic original body Git blob: `be8698ac5d020476ff649d85813810e2000c6f98`. Metadata blob: `47da1e7e20e39f0ea85e26d54a8d58301f6e0a15`; editorial drafted / publication draft / safety review pending. One form, no named controls. Its `pa-card-mainhide` CSS hides the on-screen child-privacy warning in print; source also incorrectly tells JavaScript-disabled readers that the form still works and prints even though its separate `noscript` CSS hides the form.

The new read-only generator emits a deterministic *candidate unified diff* that (a) places the original privacy caution into both generated and no-JavaScript **printed-page note** paths, and (b) corrects the no-JavaScript explanation to direct users to the blank hand-filled fallback. The source documents, source registry, citation occurrence order, print dimensions, emergency advice, no-JS form hiding and all publication statuses are **untouched**. It pins both original Git blobs and refuses changed source without manual rebase.

**Critical limit:** Page-note visibility is not the same as text surviving on the cut-out wallet card. This candidate is not a validated remediation of that residual risk. It still needs actual 100%-scale physical-print/cutout review, off-JavaScript browser verification, readability/accessibility, qualified child-privacy and emergency review, and independent QD; R368's existing original-alert print gate will not be presumed passing. Do not insert into live/private CMS without review.

## Test and checkout evidence

The authored R370 source/test files were locally Python-compiled and 73/73 new synthetic/adversarial Python cases passed. R368 + R369 suites were independently rerun alongside R370: **195/195 isolated PASS** (73 new plus 122 inherited), including offline Chromium synthetic checks inherited from prior suites. GitHub code/test blob identities matched local tested copies. These tests are not an authentic Tool #104 browser rendering or the full native build.

Connector readback confirmed both original blobs, exact five text/structural anchors and pending safety state. A complete native local Git checkout remains blocked by DNS resolution; native build, 35 original article / six tool reconciliation, 50 WordPress + 50 preview pairs and physical-print proof have not been executed. All public/revenue/safety approvals remain false.

## Conversion-first decision: no paid CTA

| Offer → funnel step | Blocker | Change/check | Evidence | Owner |
|---|---|---|---|---|
| One existing FV-owned Preparedness paid pack → confirmed order | Rights-cleared payable SKU, merchant acceptance, delivery, refunds/fees not authenticated | Obtain proof of one existing sellable pack before mapping any paid CTA | HOLD, paid orders and net revenue unverified | Founder/Commerce |
| Existing free household-planning Archive → optional Tool #104 | Original print-hidden caution and misleading no-JS copy; no cutout/device/qualified approval | Review this diff, independent R368/R369 rechecks, real exports and paper card | Candidate only, NOT safe for public download | Preparedness/QD |
| One already-published Grok family-contact asset → free Archive | Published asset_id, allowed UTM and audience match unverified | Research-only TASK-008 matching to https://finalvestige.com/preparedness/; no queue change | UNVERIFIED | Grok/Praxxis |
| Qualified humans → lead → verified paid order → realized net revenue | No independently reconciled merchant receipts, refunds, fees or attributable cohorts | Claude/Commerce use existing consent-safe instrumentation; 7/30-day cohorts, tiny-n warnings | NOT COMPUTABLE | Claude/Commerce |

Proposed, **not deployed**, free CTA: “Start With Trusted Preparedness Resources.” Preserve all essential free source-led instructions, retired water giveaway exclusion and Focus Fieldbook lead flow. Do not count clicks, leads or synthetic tests as paid sales.

Review in context of #157 independent Start Here QA, #169 synthetic fixtures, #2205 dependent isolation repair and #1689 homepage bridge; never claim those drafts are merged or release-cleared. Original nine Claude/Shelter contributor commits remain separately owned.
