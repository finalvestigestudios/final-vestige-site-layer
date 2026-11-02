# Dispatch R75 — live opt-in consent parity and actual-channel acceptance
**Reviewer-only · November 2, 2026 · NO WORDPRESS WRITE · NO MAIL · ALL SIX HOLD_UNSENT · #03/#05 HOLD_MERCHANT**

**Lineage:** Original [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) at d57ccdba3aee8f065e143e101c2945f4f3d01647. Original native six-test suite independently verified by [R74 PR #674](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/674), base SHA 3039937413aed94b2283fa7d4dc6c8ef4c785f35. [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) already owns per-edition release gates, six-CTA source ledger, alternate fallback letters and a review board. This isolated PR does not recreate them. Campaign [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), commercial owner [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Homepage PR #49 stays outside scope.

## Newly verified public consent-parity gap

Authenticated WordPress read, blog 256784396, 2026-11-02:
- Published [Dispatch page](https://finalvestige.com/dispatch/), **ID 523**: promises “New investigations and archive finds by email, when we publish them,” includes the 52-page gift and says “Unsubscribe anytime.” The existing pre-opt-in explanation does **not** say there may be commission-earning recommendations.
- Published [Focus page](https://finalvestige.com/focus/), **ID 1579**: the existing pre-opt-in statement explicitly says **“Some emails may include recommendations that earn us a commission.”** Same Jetpack list. Its clear advance disclosure does not retroactively fix differences on Dispatch's signup page.
- Published [Editorial Standards](https://finalvestige.com/editorial-standards/), **ID 17** (reviewed 2026-08-23): primary sources, meaningful uncertainty, consequential date/quote checks, material correction notes, and separate disclosure of commercial relationships.

**Proposed exact addition for /dispatch/ (NOT AUTHORIZED, NOT PUBLISHED):**
> We also occasionally examine tools related to attention and perception. Some Dispatch issues may include clearly labeled recommendations that could earn Final Vestige a commission if you choose to buy. Most issues remain independent research and archive reporting. Unsubscribe anytime.

Place immediately before the email-entry form if founder specifically authorizes the copy change. It must be checked for responsive display, truthful frequency, editorial meaning and readability. This is a **proposal only**, not an instruction to change WordPress. No new form or email list.

Current welcome message retains the 52-page Focus Fieldbook link and its non-daily archive/investigation promise. Preserve the welcome and PDF. **Configured does not mean actually received.** The October 25 confirmation Gmail message previously inspected is a subscription confirmation, not proof of the subsequent welcome.

## Authenticated WordPress evidence recorded this sprint

At **2026-11-02T21:33:53Z**, newsletter status:
- site_can_send: true; recent_sends: empty; **total 2, confirmed 2, unconfirmed 2, suppressed 0, paid 0**. These are **nonadditive** counters: not four people, not necessarily two email-eligible recipients.
- The connected WordPress status API does not return an individually scoped delivery-eligible email count. **Email-eligible audience = UNKNOWN.**

At **2026-11-02T21:33:58Z**, newsletter settings:
- subscriptions enabled; email_new_posts_by_default **FALSE**; email_content_format **excerpt**; from_name **Final Vestige**; reply_to **no-reply**; welcome text includes the 52-page PDF; categories disabled.
- Technical site_can_send true is not approval, legal compliance or proof of a send. **No changes were made.**

### Private count-only reconciliation, no subscriber details

Through the **native WordPress.com Subscribers UI**, filter for active subscribers whose email delivery is actually enabled. Distinguish confirmed site follower, confirmed email subscriber, paused, bounced and suppressed. Count only; do not export names, addresses, credentials, confirmation tokens or opt-out URLs. If the UI cannot establish an email-active filtered number, the evidence file's email_eligible_count remains null. Never infer it from confirmed count, add the counters, import subscribers or contact the list.

## Delivery is not the manuscript: site-first excerpt contract

Official [WordPress email appearance guide](https://wordpress.com/support/newsletter/email-appearance/) reviewed October 6, 2026 and [newsletter settings guide](https://wordpress.com/support/newsletter-settings/) establish:
- In **excerpt** mode, a custom excerpt controls the email intro. Without one, WordPress typically uses the first **55 words** of a post, with a link to the site. The post title forms the subject. A separate preheader editor is **not independently verified**; previously drafted preheaders remain editorial notes rather than guaranteed delivery.
- Native **Preview email** in the post editor is not the same as **Send test email**, and a screenshot preview is not proof of an actual inbox receipt. WordPress describes a draft-editor “Send this post to subscribers” toggle that exposes preview controls; **never publish, save a risky send toggle state or send without separate specific authorization**.
- An eventual received message requires HTML and plaintext inspection, a legally qualifying Final Vestige mailing address, and functional opt-out evidence. R74's existing synthetic MIME inspector only detects local content/syntax; **it neither authenticates delivery nor executes unsubscribe**.
- If commercial #03 or #05 were ever approved, an excerpt-specific commercial disclosure must reach the subscriber. A disclosure buried below word 55 in the long article cannot satisfy that email reader. Check the actual rendered excerpt, not only a GitHub Markdown preview.

**Provisional recommendation: site-first, existing Jetpack excerpt setting and only one editorial CTA per issue.** Do not switch to full mode, use another newsletter platform, or change settings unless approved. Final six manuscripts and excerpts are not yet chosen.

## Original founder-approved allocation; offer rights still false

| # | Type | Original PR175 subject | CTA and rights situation |
|---|---|---|---|
| 01 | Editorial | The mind is not a camera | Existing published site route, final variant unselected |
| 02 | Editorial | Before hypnosis had a name | Published Puységur historical archive; verify source context |
| 03 | **Commercial reserved: Zen12** | The twelve-minute meditation question | **Warm-up guide still an unpublished Mind draft; no product-specific email permission or link** |
| 04 | Editorial | **Fourteen seconds. A much longer explanation.** | Published Apollo 1 article, but subject has disputed timing; later draft used “Seventeen seconds”; choose an accurate founder-approved final |
| 05 | **Commercial reserved: Total Focus** | Before you press play on a hypnosis audio | **Guide still unpublished; no product-specific email rights or approved link** |
| 06 | Editorial | What did seven days of attention reveal? | /focus/ public; no miracle/outcome claim |

All newer candidate copy from R65–R74 remains **OPTIONAL**, not permission to substitute. Exactly **four editorial, two commercial reserved**, with real editorial value in every issue. No active merchant links. One meaningful CTA.

### Named merchant source alignment, not generic catalog claims

- [Official Zen12](https://zen12.com/) and its [free audio entry](https://zen12.com/welcome) describe twelve-minute sessions and recordings. The vendor's “one hour in twelve minutes” analogy is an **unverified product-specific efficacy claim**, not proof. The free entry also invites a **seller-owned newsletter signup** — it is not an authorized substitute for our independently reviewed paid-guide CTA. No price/guarantee promise should appear without complete current checkout and terms.
- [Hypnosis Live Total Focus exact product page](https://hypnosislive.com/mental-skills/total-focus) describes a **33-minute, 47-MB audio** by J. A. Amos. Promises of near-limitless concentration, automatic mental reprogramming and career gains are **vendor assertions**, not independently demonstrated effects of this recording. The page presents alternative pricing/bundles; the full refund conditions must be rechecked before anything commercial is activated. General [NCCIH hypnosis evidence](https://www.nccih.nih.gov/health/hypnosis) does not prove named-product effectiveness.
- [Inspire3 public affiliate recruitment](https://affiliates.inspire3.com/) is not FV-specific affiliate acceptance. [Limitless Labs promotional resources](https://inspire3.com/ll/) apply to another product and do not authorize Zen12/Total Focus email creative. Current affiliate rights, actual link formats, media licenses, pricing, refund eligibility, specific claims and consent to email promotion = **NOT VERIFIED**.
- The seller's privacy disclosures describe that referring affiliates **may receive purchaser identity/transaction data**. FV's proposed pilot should not request or ingest any buyer PII, and site privacy disclosures require independent review.
- Scoped **read-only Gmail searches** conducted this run found old consumer marketing promotions and free-audio welcome messages, but no affirmative named-product FV email authorization among the returned results. This limited search cannot prove no such authorization exists elsewhere. Consumer promos are not merchant approval.

## Correct legal requirements, no phantom one-click mandate

[FTC CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business): truthful sender/subject, recognizable commercial nature, a **valid postal address for Final Vestige**, easy opt-out, honoring opt-out requests, and sender accountability even when the platform handles email. A USPS-registered PO box or properly registered private mailbox may qualify; **an Automattic mailing address on a subscription confirmation does not establish FV's own publisher postal address**.

**Distinction:** CAN-SPAM generally requires an effective easy opt-out, not a specific RFC List-Unsubscribe-Post one-click header for each email. One-click syntax may be relevant to email-provider bulk-sender guidance. Its mere presence doesn't prove an opt-out works; absence is not by itself proof of CAN-SPAM violation if another compliant method exists. R74's inspector correctly remains only an offline signal extractor. The founder must verify actual publisher postal credentials privately and a functioning method through a separately authorized received email.

## Small-list marketing without synthetic metrics

No invented opens, clicks, purchases, conversion rates, A/B “winner,” confidence intervals, ROI or percentages with a reported total of 2 and **unknown eligible audience**. The only observed sends in the connected status are none. A zero recent-send history is **not** a measured open rate or demand failure.

The post-approval count-only measurement sequence would be: actual publication URL and exact approved title, confirmed send time if there was one, email-eligible count from authorized native UI, measured site pageviews/source where tools already provide them, verified outbound CTA events only with policy-compliant existing analytics, and sales only in future non-PII partner reporting. Store unavailable values as **NOT_OBSERVED**, not numeric zero. Don't invent UTM affiliate parameters or add any tracking link before partner rights and format are known.

## Read-only proof tool and human acceptance plan

This PR's **channel_proof.py** accepts only whitelisted yes/no and count fields. It refuses stray fields that might contain subscriber addresses, tokens, raw messages or merchant tracking links. It builds redacted HTML/text/JSON evidence. It will NEVER set send_allowed true, even if every human box is marked true: humans can assert evidence, but this code cannot independently establish any assertion. The stored count-only fixture has all attestations **false**, merchants #03/#05 **all false**; edition statuses remain fixed HOLD.

**Actual closeout remains external to CI:**
1. Founder explicitly chooses final six copies, excerpt mode and whether to approve the suggested Dispatch consent paragraph.
2. Authorized publisher privately inspects native email subscriber status and obtains an active email-eligible count; zero identities exposed.
3. Publisher privately proves the qualifying FV address, genuine Jetpack desktop/mobile preview, explicitly approved received email, footer, MIME parity, welcome PDF receipt and working opt-out.
4. Mind owner #171 separately clears each named offer, warm-up guide and exact email/channel rights, plus approved tracking format.
5. Only then founder decides final audience, dates, content and specific **sending** permission. **No approval inferred from this PR or its tests.**

**No website content, newsletter settings, welcome message, subscribers, merchant accounts, hosted campaigns, homepage PR #49 or existing manuscripts modified.**
