# R382 — Mind buyer-conversion acceptance, producer handoff and release evidence
**Status:** source-controlled editorial/commerce experiment only · 14 November 2026 · **HARD HOLD**

## Decision the next sprint must prove

The immediate business objective is **one legitimate, independently verified paid conversion** attributable to a relevant Mind reader, after authorization and production approval. A published article, email address, merchant click or scroll depth does not achieve that goal.

**Offer candidate 1: Zen12 Premium** — seller page consulted [14 Nov 2026](https://zen12.com/); product-format fit is a structured meditation audio MP3 library. The public [Inspire3 network](https://affiliates.inspire3.com/) says it runs an affiliate program. This does NOT authenticate Final Vestige's accepted publisher account, issued URL, channel rights, sales-page allowances, attribution policy or actual commission. Targeted connected-email search during R382 found consumer/promotional materials rather than affirmative provider-specific approval. Authorization **UNKNOWN**; all earning links withheld. Generic advertised commission rates are not contract terms.

**Offer candidate 2: FV-owned paid Mind digital product** — no presently purchasable, rights-cleared, active SKU and merchant-owned order-delivery-refund records were authenticated in R382. The free [52-page Focus Fieldbook](https://finalvestige.com/focus/) is NOT an eligible paid order, and assigning it a speculative price would violate the owner's product validation gate. Commerce should inspect existing Payhip inventory, original rights, licensing, tax/currency, delivery and refund setup under authorized account access. Do not list or test-buy a merchant item without founder authorization.

**Priority:** account eligibility and payable SKU evidence BEFORE more speculative landing-page variants. The source-controlled Zen12 guide is a conditional buyer-decision asset, not a launchable offer. Conversion remains **NOT COMPUTABLE**, not a demonstrated zero.

## Original article and evidence boundary

- [The Choice You Didn't Make](THE_CHOICE_YOU_DIDNT_MAKE.md): 2,470-word original sourced investigation, not live. Sources: [Johansson et al. 2005](https://doi.org/10.1126/science.1111709), [Johansson et al. 2006](https://doi.org/10.1016/j.concog.2006.09.004), [Hall et al. 2010](https://doi.org/10.1016/j.cognition.2010.06.010).
- The experiment is about covertly manipulated outcomes and subsequent explanations, **not** direct evidence for meditation/audio products or buyer conversion rates.
- Editorial historical bridge: [Puységur files](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/) — document chains, failures, operator power, consent; no assertion that choice-blindness experiments prove or disprove animal magnetism.
- Presell [A](ZEN12_A_EVIDENCE_BUYER_GUIDE.html): source-grounded text-only guide, product structure, free twelve-minute self-audit, five purchase objections, limitations, close affiliate disclosure, natively disabled CTA.
- Presell [B](ZEN12_B_OPTIONAL_42S_STORYBOARD.html): A's identical substantive buyer content plus original static SVG poster, 42-second timed transcript and [caption proposal](ZEN12_42S_CAPTIONS.vtt) in a native details component. NO actual encoded, hosted or playable video, no pretend play CTA. 42-second original film requires rights-cleared real production, media codec/bitrate/bandwidth work, captions, transcript and site QA.
- [Source-only /mind/ hub](MIND_ARCHIVE_WORDPRESS_REVIEW_ONLY.html): four editorial streams, accessible structure, independent source trails and existing free Focus CTA. Not an actual WordPress CMS draft or route.
- [Claim/right matrix](CLAIM_EVIDENCE_RIGHTS_MATRIX.json): 32 distinct claim records with source URLs and 36 commercial release gates explicitly HOLD. No invented payout, referral URL, testimonials, guaranteed effects or checkout figure.

## Three creator-topic → existing article → resource → conditional offer fits

| Proposed interest, NOT assigned Grok task | Existing public landing | Downstream user value | Optional vetted offer |
|---|---|---|---|
| “How did the camera miss a big change?” (change blindness / attention) | https://finalvestige.com/2026/11/02/change-blindness/ | Fact-check experiment → optional https://finalvestige.com/focus/ with same Jetpack list | Zen12 buyer guide only if approved, accurate and genuinely relevant |
| “What did Franklin's 1784 commission actually test?” (expectation/suggestion history) | https://finalvestige.com/2026/11/02/mesmerism/ | Actual historical inquiry → Puységur archive → optional Focus | Hypnosis Live independent review only if exact sales page, evidence and approval validated |
| “What did Puységur's witnesses record and what didn't it prove?” (original archives, consent) | https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | Original documents and source-trail method → Focus | No automatic affiliate placement; conditional independent evidence guide only if intent shows fit |

**Grok owns creation/publication**; **Praxxis independently checks** existing assets and original hooks. Before adding any link or tracking parameter ask Praxxis through the established TASK-008 handoff for: published actual platform URL, immutable `asset_id`, publish date, hook text, source/rights/caption review, allowed mobile click destination, resulting landing URL and platform-specific UTM capabilities. **All three are candidate mappings, not evidence of published, verified videos.** Do not invent IDs. No edits to content queue.

## Internal navigation plan

Preserve all six current editorial categories, flagship PR #49, owned art Issue #150, canonical Mind hub PR #172 and live routes.

Proposed review-only linking: Explore/Library → /mind/ (pending approved WP route); /mind/ → published change-blindness, published Franklin/Mesmerism, Puységur evidence files, and Focus Fieldbook. Existing topic pages may carry one contextual source-led invitation to Mind after editorial approval. The separate commercial guide is not a broad homepage billboard. Never route Grok to unapproved /mind/ or R382 draft files.

All important content and Focus route available without JS. Product recommendations never require subscribing. Do not duplicate newsletter forms or replace Jetpack's Focus welcome.

## A/B controlled hypothesis and allocation

**Treatment A:** accurate source-first buyer guide without film. **Treatment B:** identical source-first buyer guide with a lightweight original, optional 42-second film *only once encoded, hosted, approved and tested*. Until B has actual media, the present comparison is a content parity/static-design test, **NOT an audience experiment**.

Test hypothesis: among truly comparable qualified-human visitors with high-intent focus/audio interest, B might improve independently confirmed purchased orders per qualified eligible visitor relative to A without hurting mobile completion, time-to-interactive, source comprehension or disclosures. This is not a guaranteed conversion lift.

Before any live test, founder/engineering/site QA must document: valid affiliate account and approved outbound destination; consent-appropriate first-party anonymous assignment; stable 50/50 eligible split and one user in one variant (without intrusive fingerprinting); approved UTM handling; baseline page; no forced video load; poster+transcript available when media disabled; VTT/caption sync; keyboard controls; WCAG 2.2 AA; no-JS functional links; legal disclosure visible beside earning control; genuinely payable checkout; independent sale callback/export or reconciliation; fraud/QA exclusion definitions; stop rules and sample-size plan.

**Primary metric:** realized net revenue / 1,000 qualified-human sessions, cohort by initial campaign/variant; only compute when both independently attributable net revenue and trustworthy qualified-session denominator exist. **Secondary metrics:** independently verified paid-conversion rate, settled orders, gross/net, refunds/fees, confirmed-lead-to-purchase rate, informational CTA click and verified engagement (diagnostic only). Report 7-/30-day cohorts, incomplete attribution and small denominators prominently. Never infer a sale from `affiliate_click`, `checkout_start`, lead or "thank you" screen.

Proposed event contracts for Claude to map onto existing WordPress/Jetpack instrumentation — **do not deploy a duplicate script**:

- `campaign_landing`: `asset_id` and approved `utm_source`, `utm_medium=organic_social`, `utm_campaign=mind_<cluster>_2026_11`, `utm_content=<actual_asset_id>`, `landing_path`, `variant`, `consent_state`, time bucket; exclude IP, email address, full UTM free text and fingerprint IDs from reports.
- `article_to_resource_click`: existing Focus route and campaign context, no personal subscriber identifiers.
- `confirmed_signup`: **only** from existing Jetpack authenticated confirmation, not click, form submit or anomalous audience-count dashboard.
- `affiliate_click`: authorized external URL outbound **only after release**; distinct from merchant-confirmed sale.
- `verified_paid_order` / `partner_paid_conversion`: only trustworthy merchant transaction ID or external partner settlement export, de-duplicated and access-controlled, not sent to public analytics as PII.
- `refund`, `fee`, `settled_net`: reconciliation within restricted commerce ledger; irreversible aggregation and privacy retention policy.

Do not use UTMs as proof that users are human; reconcile known internal/test traffic, bots, unexplained view spikes and consent limits. `qualified-human` criteria and exclusions must be approved and disclosed. Aggregate until sample size is sufficient to avoid leaking personal data.

## Prioritized OFFER → STEP → BLOCKER → CHANGE → PASS/FAIL EVIDENCE → OWNER

| Rank | Offer / funnel step | Blocker | Experiment/change | Evidence as of R382 | Owner |
|---|---|---|---|---|---|
| P0 | Zen12 → real affiliate commission | Named approval, permitted channels, issued earning URL, T&Cs missing | Read provider dashboard/approval and merchant checkout, record permission evidence | HOLD — public network + promo emails insufficient | Founder/Commerce |
| P0 | Owned Mind product → payable SKU | Rights, live checkout, fulfillment/refund ownership not authenticated | Inspect existing Payhip item IDs and transaction/export ownership | HOLD — free fieldbook is not paid | Commerce |
| P1 | Relevant Grok creator → landing | Exact authentic asset ID and mobile link unknown | Praxxis verifies existing posts, no new production | UNVERIFIED — topic mappings proposed only | Praxxis/Grok |
| P1 | Landing → confirmed Focus lead | Jetpack confirmation attribution ambiguous | Claude uses existing list and consent safely, no test subscribers without permission | UNTESTED | Claude/Dispatch #174 |
| P1 | A/B buyer page → merchant order | B film storyboard only, native browser/WordPress QA absent, affiliate hold | Produce rights-cleared optional media; test 360/390/768/1440/1920 and WCAG; separately approve earning CTA | STATIC DRAFT ONLY | Mind + Site QA #126 + Claude |
| P0 | Purchase → realized net | Merchant export, fees/refunds and trustworthy denominator absent | Reconcile 7-/30-day qualified cohorts on approved first-party/merchant sources | NOT COMPUTABLE | Commerce/Claude #820 |

## Responsible QA handoff and release boundaries

Source inspection may PASS assertions; that is not a browser or CMS launch. Run `node mind/r382/verify.mjs` on the actual branch; capture exit code and exact SHA. Independently test keyboard, focus, colors, screen reader, 360/390/768/1440/1920 layouts, WordPress sanitization and link path behavior before eligibility to release. Withhold video because there is no encoded file. Test pre-approval CTA has native `disabled`, and reject swapped `aria-disabled` as only protection. Ensure source links to zen12.com are framed strictly as citations, not product purchase links; **no merchant hyperlinks appear in the presell A/B variants** in this pilot (merchant only named in text).

Keep source links in the investigative research article as independent bibliographic references; commercially oriented guides never link to merchant until authorized. General affiliate disclosure page is no substitute for immediately adjacent disclosure at the actual earning link.

Site QA #126: independent source, WCAG/label, contrast, mobile, disclosure, no-JS, no merchant/PII/analytics leakage review. Art lead #150: visual direction only, never touch flagship frozen work. Dispatch #174: no email edits, no welcome replacement; context coordination only. Claude: no analytics code merge/deploy from this lane. Founder: final spend, publishing and release approval.

**HARD HOLD remains:** no WordPress CMS/navigation/settings writes; no PR #49/PR #172/Issue #150 overwrite; no auto social posting or newsletter; no affiliate link activation, merchant purchase, tracking script, deployment, merge or spending. This is a draft and review trail, not live revenue evidence.
