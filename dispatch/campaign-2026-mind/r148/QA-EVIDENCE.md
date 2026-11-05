# Dispatch R148 — first-click integrity warning and non-sending proof gate

**2026-11-05 ~15:39 Pacific.** Draft-only. Issue [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), companion Mind [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), Focus [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Stacked on R147 draft PR #1161 exact parent SHA `01b22118a4d9bcac0bc44a7cfcc5957327b2940a`. Master PR #175 at `d57ccdba3aee8f065e143e101c2945f4f3d01647`, PR #201 and homepage PR #49 remain untouched.

## P0: possible leakage at the first click (not a proven guest-browser defect)

**Independently read from authenticated WordPress page #523**:

* The published `/dispatch/` editor source has one native `<!-- wp:jetpack/subscriptions -->` block and no literal email form or email input. The absence in raw Gutenberg source is not itself a defect.
* The WordPress **view** representation of the same page instead contains a `Subscribe` anchor pointing to `https://finalvestige.com/?post_type=page&p=523` (a different URL for the same page), with no email input or `<form>`. That is a tangible API-view representation gap and a potentially circular first click, **not** verification of what an actual anonymous visitor sees. Native Jetpack blocks may render or hydrate differently in the real browser.
* `/focus/` page #1579 has a saved native subscription block and the previously documented permissive `?subscribe=` success branch. A visible download panel is not a confirmed opt-in. Existing Focus correction PR #1079 owns the live change; **do not fork a duplicate fix**.
* Canonical site Editorial Standards require distinguishing source evidence from inference; therefore the risk classification is **P0 VERIFY**, **not P0 CONFIRMED BROKEN**.

**Latest read-only Jetpack at 2026-11-05T23:39Z:** enabled, new-post auto-email OFF, **full** delivery, sender Final Vestige Studios, no-reply, last five posts `never_sent_opted_out`. Dashboard: total 3 / confirmed 3 / unconfirmed 2 are **nonadditive**; imported past rolling 24h 0; actual eligible email recipients unknown. The 52-page Focus Fieldbook welcome URL is configured, **not proved delivered**. No new WordPress settings, pages or subscriber data were changed.

## Required decisive guest QA (Claude/Site QA; zero submissions)

1. Open `/dispatch/` and `/focus/` **signed out** on desktop and mobile at 320, 390, 768 and 1440px. Record a browser screenshot and final DOM for visible email field, submit control, accessible label, focus order, keyboard operation and resulting **first-click action only**. Do **not** enter an email, submit a form or send anything.
2. If the only Subscribe control genuinely reloads page #523 and no email entry appears, classify **CONFIRMED GUEST FIRST-CLICK FAILURE**. Claude proposes the minimum Jetpack-block or display repair on its own production branch, retaining the original single list. Require QD review and founder release approval.
3. If the real guest browser shows a usable subscribe form, close this specific API-representation issue as non-causal; **do not** infer double opt-in, welcome receipt or Fieldbook delivery. For confirmation, use only native consent evidence, privately and with a deduplicated `confirmed_signup` event, never a `?subscribe=` query parameter.
4. WordPress's **native non-sending email preview** is available from a post editor with its per-post newsletter toggle. Obtain a separately approved draft-only, zero-send procedure before toggling anything. Preview ≠ delivered receipt. Final email needs real FV business postal address, working unsubscribe, truthful subject, a single relevant CTA and near-offer disclosure.
5. To actually prove delivery, obtain founder permission for an authorized **received** test or previously received mail artifact, then inspect both HTML and plaintext and the PDF. No mailbox or recipient experiment is authorized by this PR.

## Conversion-first scoped release plan

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Focus Fieldbook → visitor starts signup | `/dispatch/` API view self-referential Subscribe link | Real signed-out **no-submit** DOM/keyboard review | **Representation warning VERIFIED; actual guest UNKNOWN** | Claude / Site QA |
| Focus Fieldbook → confirmed lead | Focus false-positive UI branch and conflicting 3/3/2 counters | Existing PR #1079 and native subscriber consent audit | **UI code risk VERIFIED; actual lead count UNKNOWN** | Claude / Dispatch |
| Fieldbook → welcome | No verified receipt/download | Authorized received welcome and PDF check | **UNKNOWN** | Dispatch |
| Editorial 01/02/04/06 → investigation | Native full-email footer/CTA not previewed | Safe approved WordPress editor preview | **UNKNOWN** | Dispatch / Claude |
| **Zen12 Premium** Issue 03 → paying customer | Merchant acceptance, explicit email permission, earning URL and live approved guide missing | Mind #171 product/account approval; exact checkout/refund review | **HOLD_MERCHANT** | Mind |
| **Hypnosis Live Total Focus** Issue 05 → paying customer | Same partner/guide barriers; vendor pricing/benefit claims unverified | Mind exact 33-minute/47-MB offer and email-rights verification | **HOLD_MERCHANT** | Mind |
| Settled order → realized net revenue | Qualified-human denominator and independent paid orders/fees/refunds missing | Existing #820 7/30-day cohort reconciliation; no duplicate scripts | **NOT COMPUTABLE** | Commerce / Praxxis |

**No paid sale is inferred from a subscriber, an open, a click, a dashboard count or a product page.**

## Original campaign and commerce boundaries

The six-issue allocation remains **four editorial / two reserved commercial**. No alternative manuscript is approved for substitution. Issues 03/05 stay blocked until Final Vestige-specific affiliate acceptance, the actual approved links and the **email channel permission** are documented. The public Hypnosis Live **Total Focus** sales page advertises a 33-minute, 47-MB session; the seller's efficacy and price/refund claims do not constitute independent substantiation or a verified checkout. Zen12's attention/meditation-equivalence claims are not established outcomes. No fabricated postal address, test recipients, fixed price, tracking URLs, affiliate activation or invented A/B metrics.

The merchant and editorial records were checked against [the official Total Focus page](https://hypnosislive.com/mental-skills/total-focus), [WordPress email preview guidance](https://wordpress.com/support/newsletter/email-appearance/), [WordPress newsletter settings](https://wordpress.com/support/newsletter-settings/), [FTC CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), [FTC Endorsement Guides](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking), and the [site Editorial Standards](https://finalvestige.com/editorial-standards/).

## Independent tests and limitations

`node test_guest_path_audit.cjs` — **25/25 passing in native Node 22.16.0** after the negative-case priority bug was found and corrected before commit. The tester is read-only, synthetic, PII-rejecting and fail-closed. **No real anonymous browser, genuine Jetpack preview, actual inbox receipt, checkout or paid conversion was tested.** Host CI not asserted. The original PR #175 exact-head Python suite previously passed independently in earlier runs but was not freshly rerun natively in this sprint; do not claim otherwise.

**Six issues HOLD_UNSENT. Commercial #03/#05 additionally HOLD_MERCHANT.** No emails, test sends, subscriber contact, subscription imports, WordPress writes, product-link activations, spending, social posts or release authorization.
