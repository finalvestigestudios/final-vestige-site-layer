# R132 — Dispatch excerpt-to-article conversion bridge (UNSENT, NONPRODUCTION)

Owner: [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Product clearance: [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Funnel consent: [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129). Business KPI: [Conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Canonical six source drafts: [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) @ `d57ccdba3aee8f065e143e101c2945f4f3d01647`; stacked after **draft #1050** @ `38b448b1101ae3ae01d1ae8276bb911e62e7bfec`. All releases and emails remain HOLD. **This branch does not replace any of those drafts.**

## One consequential decision

The previous R131 review proved that six canonical CTA positions and two commercial disclosures are beyond *modeled* excerpt windows, but it did **not** prove what a genuine Jetpack message looks like. Instead of silently changing sitewide email settings, this project provides SIX exceptionally concise **optional manual excerpt candidates** as an alternate single-CTA route: email native *Read more* (if actually rendered) → first-party Dispatch issue post → original referenced investigation or independently cleared merchant evaluation → verified paid order. No link, copy or permission is activated here.

Crucially, **a visible imperative sentence in a proposed excerpt is not a clickable HTML button**. WordPress automatically adds a full-post link for excerpt emails according to its documentation, but we have not seen it rendered for this site's actual post, nor proved whether the manual excerpt retains all words or disclosure. The same issue must be tested inside the native pre-publish preview for both desktop and mobile; no post may be published or sent as part of this review.

## Native source-of-truth and what it establishes (read 2026-11-05 07:37 UTC)

- Authenticated WordPress Newsletter status: enabled, `site_can_send=true`, `email_new_posts_by_default=false`, the five most recent posts all `never_sent_opted_out`. No Dispatch send evidence.
- Newsletter setting: `email_content_format=excerpt` and configured 52-page Focus Fieldbook welcome. **Configured welcome ≠ received welcome or working attachment.**
- Diagnostics: **total=3, confirmed=3, unconfirmed=2** (not additive), imported_last_24h=1; followers **WP.com=3, legacy email=0**. A zero legacy-follower bucket is **not** a proof of no eligible mail recipients. Individual statuses/consent/delivery remain unknown, and addresses must not enter GitHub.
- Published `/dispatch/` (page 523) promises investigation updates and the Fieldbook. The stored REST subscription block contains a fallback Subscribe link; this alone does **not** prove that the dynamic block is broken in rendered browser HTML. The published `/focus/` (page 1579) exists, but the native opt-in/welcome/PDF delivery is not proven by the UI or a URL parameter.
- Live [Editorial Standards](https://finalvestige.com/editorial-standards/) insist on primary records, documented uncertainties, independent source checks, and separation of commercial interests from history.

### Verified platform rule (not a site-specific rendering test)

Official WordPress.com [Newsletter settings](https://wordpress.com/support/newsletter-settings/) says an explicitly supplied post excerpt is used in lieu of the first 55 words if selected; setting remains "excerpt". Official [Email appearance/preview](https://wordpress.com/support/newsletter/email-appearance/) explains that **Preview email** requires the *per-post* "Send this post to subscribers" toggle to be switched on within the draft editor, and also offers *Send test email* as a separate action. Switching a draft toggle or publishing needs user approval for this program. **DO NOT click Send test email. DO NOT publish or change any WordPress setting.** Native preview without a send is a future authorized manual procedure, not accomplished here.

## Six ethical and compact *alternative* excerpts

[excerpt_candidates.json](./excerpt_candidates.json) contains all six proposed subjects, preheaders, human-readable 300-character/55-word maximum text snippets and **one verbal CTA each**. The constraints are deliberately tighter than both previously modeled limits but are *not* evidence of actual Jetpack truncation behavior. These candidates are *not inserted into WordPress*. They preserve **four historical/evidence editorial slots and two commercial-review-pending slots** and do not alter master manuscripts. Source-first editorial routes refer to existing first-party investigations/Fieldbook; 03 and 05 remain **no URL, no approval, no live warm-up guide**. Each commercial draft contains an honest possible-commission disclosure within its own proposed excerpt. Neither claims that seller results or email-marketing permissions are independently established. Treat merchant prices, audio format, refunds, creative-use rights, data-sharing terms and checkout as unverified until current source-of-truth validation.

**Specific persuasion and trust fit:** 
1. Issue 01 opens with the uncertainty of memory, then a Puységur source trail. This directly bridges a Mind acquisition topic to FV's historic-evidence promise.
2. Issue 02 presents the historical witness-versus-cause puzzle; one source-trail action.
3. Issue 03 starts with free, controlled practice, then frames Zen12 claims as claims; one optional independent guide action **only after guide approval** and near-action prospective disclosure.
4. Issue 04 uses Apollo 1 as our evidence-first flagship counterweight; one historical record action.
5. Issue 05 identifies hypnosis audio buyer objections—format, efficacy, terms—without claiming outcomes; one optional independent guide action and near-action disclosure.
6. Issue 06 serves returning Fieldbook readers without claiming that another signup is required or that downloads mean consent.

## Two legitimate editorial release options — neither approved

**A. Keep sitewide excerpt setting** and, if finally authorized, use a post-specific *manual excerpt* for the **WordPress post** behind each Dispatch issue, not an email-only replacement manuscript. Native `Read more` becomes the only intended first click. This is a two-click journey: email → full original researched post → guide/source. It protects editorial substance on-site but needs direct verification that custom excerpts, commercial disclosures, and link text render as expected. No invisible CTA, embedded external tracking, unapproved affiliate URL or false 'send ready' state.

**B. Consider sitewide full-text delivery** to preserve the original editorial experience, provided the native preview genuinely retains the whole original, the one clear CTA, near-offer disclosure, postal address, unsubscribe, and responsive HTML. Founder approval is mandatory before changing `email_content_format`; sitewide changes may also affect unrelated post notifications.

**Decision rule:** Neither model may be considered pass until a **native unsent preview** evidences the actual CTA and commercial notice, legal footer, subject/preheader, plain text (if available), reading order and 360/390/768px layouts. A synthetic template or arbitrary email specimen cannot satisfy this proof. If preview needs a write to an existing production draft, request specific clearance separately; do not opportunistically create a post, toggle sending, or send tests.

## Actual inbox and legal checks to keep CLOSED

1. **Recipient:** Export/inspect only privacy-protected native subscriber status under appropriate authorized access; distinguish confirmed, email-subscribed, bounced, opted-out, WP.com follower and newly imported. No recipient addresses in repository, logs or screenshots.
2. **Welcome:** Read one already-authorized received welcome if available, confirm Fieldbook link and actual PDF access. The 2026-10-25 subscription confirmation is not a welcome receipt.
3. **Commercial footer:** Supply a **genuinely valid Final Vestige physical postal address**, not Automattic's address, and verify it is visible in **actual** commercial email; verify working unique unsubscribe mechanism and removal behavior. Do not replace placeholders with guesses.
4. **Merchant:** Mind Studio provides written named acceptance, specifically allowed **email promotion**, earning URL/link formatting, permitted creatives and claims, checkout price/refund conditions, whether a seller freebie adds another merchant newsletter, and settlement report proof. The public affiliate portal is not approval.
5. **Founder:** final campaign creative, audience, cadence and sending permission must be an explicit separate instruction. Current six-week pilot remains unscheduled and unsent.

## One attribution contract: distinguish clicks, leads and **paid orders**

If eventual native email links can carry standard parameters, use `utm_source=dispatch&utm_medium=email&utm_campaign=mind_pilot_2026_11&utm_content=dispatch_issue_0N` on the *first-party* destination **only after** testing that Jetpack preserves them; do not inject duplicate analytics tags or leak subscriber IDs. With native auto-generated `Read more`, query-parameter preservation is unknown: record attribution as `UNATTRIBUTED`, never fabricated. Grok-origin traffic uses its own `asset_id`/platform source under #820 and must not inherit a false "dispatch" origin.

The native confirmed_signup event must require *platform-authenticated subscription state with evidence of legitimate opt-in* and privacy-safe deduplication; neither CTA click, `?subscribe=` UI state, Fieldbook download nor subscriber-count delta proves it. Join qualified sessions to independently reported **settled** merchant or rights-cleared paid FV orders (where lawful attribution exists), subtract fees/refunds for realized net revenue. `net_revenue_per_1000_qualified_sessions=1000*net_revenue/qualified_sessions` only if both operands are verified and denominator positive. Otherwise **NOT_COMPUTABLE**, not zero. Use 7/30-day cohorts with tiny-sample warnings; no statistically confident A/B claims with 3 reported subscribers.

## Evidence / owners / priority queue

| Offer → funnel step | blocker | change / experiment | pass/fail evidence | owner |
| --- | --- | --- | --- | --- |
| Verified, rights-cleared paid FV product OR eligible Zen12 → **settled order** | Paid offer eligibility / commissions / settlement unavailable | Vet ONE high-intent offer; reconcile fees/refunds | **FAIL CLOSED**: no approval and no orders | Mind / commerce / Claude |
| Dispatch → post → qualified guide | Current excerpt may suppress 6/6 CTA and 2/2 commercial notices | Compare exact native excerpt-with-manual-field versus full text **without sending** | **SOURCE-MODEL PASS / NATIVE UNKNOWN**: 6 under 300 chars/55 words; no real WP mail preview | Dispatch / Claude |
| Focus → genuine lead | Native email eligibility / welcome delivery unproven | Read-only subscriber-state and authorized received welcome/PDF | **FAIL CLOSED**: counts do not prove eligibility | Dispatch / Site QA |
| Commercial guide → vendor checkout | Publisher permissions, actual buyer terms missing | Written terms & direct merchant receipt | **FAIL CLOSED**, no activated link | Mind Studio |
| Grok → audience → net revenue | Social asset IDs and independently matched customer evidence missing | Match source-tagged quality sessions to settled records | **NOT_COMPUTABLE** | Praxxis / Claude |

## Test instructions and scope

Run offline: `node test_guard.cjs`. The 24 test cases exercise six editorial slots, 55-word/300-char limits, visible *text* CTA, disclosure retention, **no live commercial URLs**, and adversarial attempts to claim partner approval, native rendering, personal eligibility or release permission. These are offline structural tests, not a WordPress browser or actual email test. Keep full hold on **every** issue; 03/05 have additional merchant hold.

No homepage/PR #49 work, no website publish, subscriber contact/list mutations, sending, merchant activation, paid tools or analytics instrumentation. Do not merge this without independent review and founder direction.
