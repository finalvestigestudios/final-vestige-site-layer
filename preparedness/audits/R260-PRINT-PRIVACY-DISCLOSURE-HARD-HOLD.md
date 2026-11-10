# Preparedness R260 — Tool #104 printed privacy-disclosure custody witness (DRAFT / HARD HOLD)

**Owner:** Preparedness integration/source safety, Issue #136; commerce/attribution handoff #820; charter #818.
**Base:** R259 draft PR #1867 at 511d08c32bebffdf185f6a024768ea1a2dac3a9f.
**Editorial source:** E259 independent finding, Issue #136 comment 6762993443.
**Scope:** Preparedness only; NO original article, tool, taxonomy, source register, WordPress, navigation, analytics, social, email, merchant or public production changes.

## Original safety defect — source-level only
Original Tool #104 family-reunification-card.body.html Git blob be8698ac5d020476ff649d85813810e2000c6f98 has a screen warning **“A printed card can be lost”** inside an element with class pa-card-mainhide. In @media print, the original CSS sets .pa-card-mainhide { display: none !important; }. The source therefore instructs that this screen warning be hidden when printed. The JavaScript print-page note mentions cutting, folding and review, but not the privacy warning. The no-JavaScript blank printable card includes 13 labeled fields and no equivalent printed privacy warning in the checked fragment. The separate no-JS claim “The form below still works and prints” remains disputed.

These are authenticated **source observations**, NOT computed-style, browser, print, privacy, medical, child-safety or independent QD verification. The underlying tool has NOT been changed or certified.

## Engineering / testing
- R260 read-only Python validator pins the original Tool #104 body, checks balanced print @media rules, concealed screen privacy warning, JavaScript print-note scope and no-JS 13-field fallback. If source evidence changes, fail closed for independent re-review. Production uses original source pin; a caller-supplied pin exists for synthetic testing only.
- R260 standalone regression suite: **67/67 Python tests PASS**, ten positive and 57 adversarial. Python compilation PASS. Verified exact Git source/test identities against the locally executed files.
- R220 custody pipeline loads R260 by pinned Git blob before WordPress draft rendering, records explicit review HOLD and verifies the module pin again at audit completion.
- GitHub source-level checks verified the original HTML body SHA, CSS, alert, JavaScript note and all 13 fallback labels.
- **NOT EXECUTED:** complete native repository validation/build, inherited tests, authentic original-data Python R260 execution, browser/print behavior, all 41 WordPress draft exports. The local environment has no GitHub DNS for a complete checkout. Do not reinterpret synthetic results as end-to-end verification.

## Contributor and independent QA custody
R200 frozen manifest blob 5822f9dfde21d1f3bdfc26658769d852c639438c, 35 articles/41 intended drafts. Verified seven exact current contributor SHA refs: start 2122d856, shelter 5daeaf2d, food f911ff7a, health d5ef5baf, hist-field 4e5caf81, hist-food 67e116e5, hist-home 7504a5f0. Independent draft QA PR #157 at 7d1ae6b8; synthetic fixtures PR #169 at e9cd7766; homepage lead #1689 at f55c36b6. None changed.

Inherited audit remains **2,000 original citation occurrences**: 562 shared-source, 1,438 other. All 32 shared-source review groups and three original Article #7/Article #20 citation disputes remain held. Article #7 chemical-contamination language and Article #15/Tool #104 disclosures are not adjudicated. No source, reading depth, URL or safety label edits.

## Conversion-first REVIEW-ONLY acceptance (no activation)
**Audience:** households organizing emergency contacts and essential records. **Free:** existing ungated /preparedness/ Archive; no retired water freebies. Grok/Praxxis must verify an already published, rights-cleared creator asset_id and signed-out mobile destination through TASK-008; no new asset is authenticated by this gate.

**Unpublished candidate CTA copy:** “Start with a free family emergency contact plan. Review who you would call, where you would meet, and what you would keep off a printed card. No purchase or signup required.” Do NOT imply the held original printable tool is approved or safe.

**One provisional commercial candidate:** existing Legacy Triage family-records PDF, not approved as a Preparedness upsell. Verify the full PDF, genuine storefront sale, rights, sensitive-information/credentials handling, audience suitability, checkout, payment, refund/fees, fulfillment and founder/Commerce authorization BEFORE presenting any paid CTA.

| Offer → funnel step | Blocker | Change / experiment | PASS / FAIL evidence | Owner |
| --- | --- | --- | --- | --- |
| Free guide → printed card | Privacy notice concealed and no-JS mismatch | Independent editorial decision + true browser/print/privacy acceptance | Source witness HELD; 67 synthetic PASS only | Editorial + QA |
| Grok social → free Archive | Matching asset ID, rights, mobile link unknown | Verify TASK-008 inventory; 360/390/768/1440px mobile/accessibility; consent | UNVERIFIED | Grok + Praxxis |
| Free Archive → optional Legacy Triage | Product fit, full contents, privacy and rights unknown | Audit entire existing PDF; founder authorization | NOT APPROVED | Founder + Commerce |
| Optional paid PDF → delivery | Merchant checkout, refunds and actual fulfillment not tested | Authorized merchant-side acceptance | NOT TESTED | Commerce |
| Human sessions → realized net revenue | Attributed paid orders, fees, refunds absent | 7/30-day verified asset_id + utm_campaign → qualified sessions → CTA → confirmed leads → merchant-paid orders → realized net revenue | NOT COMPUTABLE | Analytics + Commerce |

No measured revenue claim, affiliate activation, paid CTA, live scripts, WordPress/CMS writes, socials, publication, email or spending. All approvals remain FALSE.
