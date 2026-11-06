# Dispatch R160 | Provider evidence, first-click diagnostic and commercial revenue handoff
**2026-11-06 ~03:32 Pacific | DRAFT / UNSENT / UNPUBLISHED**

Owner: [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); Mind [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171); Focus [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129); conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820); [TASK-008](https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit). Baseline [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) at d57ccdba3aee8f065e143e101c2945f4f3d01647 (six original letters; four editorial, two commercial); independent earlier gate [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201); preceding stack [#1242](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1242). No original copy or frozen homepage PR #49 touched.

## The genuinely new verification: provider media matches configured welcome

Authenticated read-only WordPress Newsletter Settings at **2026-11-06 11:32 UTC**: newsletter ON; new-post auto-email OFF; full email content; sender Final Vestige Studios; reply-to=no-reply; welcome copy points to the 52-page Seven Day Focus Fieldbook. A separate WordPress media-library search found **item #1737**, title Seven Day Focus Fieldbook — Complete Edition, MIME application/pdf, size **599,946 bytes**, created October 29, 2026. Its source URL **exactly matches the welcome message URL**:

https://finalvestige.com/wp-content/uploads/2026/10/Final_Vestige_Seven_Day_Focus_Fieldbook_Complete_Edition.pdf

**Provider media object: MATCHED. Actual public download, PDF page count, delivered welcome, recipient open/download and confirmed signup: NOT VERIFIED.** Never convert a configuration match into a delivered lead or revenue claim. The connected Gmail October 25 confirmation request is NOT a received final welcome. No test message authorized/sent.

## Subscriber arithmetic is NOT a funnel

WordPress Jetpack status at 11:31:59 UTC: total **3**, confirmed **3**, unconfirmed **2**, suppressed 0, paid 0, imported-last-24h 0, site_can_send true; five recent articles never emailed (opted out). Separately, WordPress.com followers breakdown: three WP.com followers, zero legacy email-only followers, partial false. Different categories are NOT additive. The only authoritative email-eligibility verification is native Jetpack > Newsletter > Subscribers filtered by **Email subscription** status: Subscribed / Not subscribed (Reader only) / Not confirmed / Bounced / Emails paused / Not sending. Source [WordPress subscriber manual, reviewed November 4, 2026](https://wordpress.com/support/subscribers/).

The newsletter welcome guide [WordPress settings](https://wordpress.com/support/newsletter-settings/) also explains that addresses already verified through WordPress.com can skip an additional confirmation. A reported confirmed record is NOT a newly verified consent event or proof of current reachability. Collect only **private aggregate eligibility counts and timestamp** if the owner has native access; do not export identities. Deduplicate genuinely provider-verified NEW signups; never count a web success banner, site visits, imported record, repeated subscription click or aggregate delta as a confirmed_signup event.

## Two published pages require real guest-browser first-click QA

Read-only WordPress published pages: **/dispatch/** #523 and **/focus/** #1579. In the content-view API representation, each Jetpack Subscribe control is a **same-page anchor** to a WordPress page query; CSS/JS-stripped markup contains no email input. API output is not guaranteed to match a signed-out, hydrated visitor browser. Do NOT claim the form broken from this alone.

WordPress screenshot service returned READY, PUBLIC for two 390px captures:
[Dispatch capture](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2Fdispatch%2F?vpw=390&vph=1700&w=1200) and [Focus capture](https://s0.wp.com/mshots/v1/https%3A%2F%2Ffinalvestige.com%2Ffocus%2F?vpw=390&vph=1700&w=1200). The image pixels were NOT inspected, and screenshot service availability is not usability evidence.

**New targeted operational artifact:** guest_firstclick_readonly.cjs. An optional no-submit Playwright runner for 320/390/768/1440px on both exact published pages. It creates a signed-out ephemeral browser context, blocks non-GET requests, never types or submits email, never follows offsite/merchant links, and only attempts a known self-page GET anchor when a visible email field is absent. Output is redacted first-click counts/status and viewport screenshots, not subscriber data. If the network guard blocks widget activity, it reports UNKNOWN rather than a failure. No live browser run occurred here (Playwright unavailable). With an existing browser installation, Claude/Site QA can execute:

node dispatch/campaign-2026-mind/r160/guest_firstclick_readonly.cjs --run --out=/tmp/fv-r160

Manual owner must inspect visible real email inputs, keyboard focus, exact anchor behavior, console errors, and whether Jetpack hydration changes the guest UI. NO subscription submission or test-mail delivery is authorized.

## High-intent buyer pathway: one offer first, no imaginary merchant approval

**Hypothesis (unmeasured):** Grok's relevant Mind/Attention social asset with unique asset_id → published [Change Blindness investigation](https://finalvestige.com/2026/11/02/change-blindness/) or [Puységur sources](https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/) → optional free /focus/ → native confirmed email-eligible consenting subscriber → substantive editorial Dispatch → **vetted live Zen12 Premium buyer guide** → account-authorized merchant link → **independently paid and settled affiliate commission**.

Grok owns source production and distribution under TASK-008; Claude owns CMS / instrumentation engineering; Dispatch owns consent, recipient and newsletter proof; Mind owns first-party buyer guide and merchant claim/rights verification; founder approves production release/merchant activation; Commerce and Praxxis own paid settlement. No software, social queue, Payhip or merchant changes by Dispatch.

Official [Zen12 seller page](https://zen12.com/?no-popup=1) currently describes twelve levels, four versions each (48 recordings). Claims that twelve minutes equals an hour of meditation and health/focus gains are **merchant representations, NOT independently established product-specific outcomes**. Displayed sales-page amounts and refund promises are NOT verified checkout/refund fulfillment. The buyer guide is currently **unpublished** with disabled earning control. For Issue 03 Mind/Founder must verify exact Final Vestige affiliate account acceptance, permission specifically for email, permitted creative/link/tracking, current product terms, authorized earning URL and published first-party guide. Hypnosis Live Total Focus has the same independent gate for Issue 05. Public affiliate portal, merchant catalog and unrelated promo email are not sufficient authorization.

**Progression hypothesis, not targeting permission:** history-only readers receive historical value. Voluntary Focus users may receive a useful evidence-led editorial sequence, contingent on verified consent and founder delivery approval. Only someone who intentionally explores a genuine, approved buyer guide may encounter an optional disclosed product evaluation. No PII/behavioral segments or speculative tag system are deployed. Original four editorial / two reserved commercial allocation stays intact.

**Source/measurement contract:** creator asset_id + utm_source/utm_campaign/utm_content → qualified unique human first-party sessions → relevant content/offer CTA → provider-confirmed consented lead where applicable → separately verified merchant paid order/commission → refunds/fees → realized net revenue. Draft Dispatch convention: utm_source=dispatch, utm_medium=email, utm_campaign=dispatch_mind_pilot_2026_11, utm_content=issue_01 through issue_06, used ONLY on permitted live URLs after approval. No email/user/hash data in query. KPI **1000 × realized net revenue ÷ unique qualified-human sessions**, with 7/30-day cohorts and tiny-N warnings. Both numerator and denominator are UNKNOWN; **net revenue per 1,000 sessions is NOT COMPUTABLE**. CTR/signups are not orders.

## Hard-hitting copy/CTA review of unchanged six originals

| Issue | Retain | Highest-impact weakness | Release |
|---|---|---|---|
| 01 Mind not a camera | Historical evidence-first transition | Strengthen source trail for named claims | HOLD |
| 02 Before hypnosis had a name | Three useful evaluation questions | Repeats issue 01's Puységur destination; existing R155 alternative targets published Mesmerism article but NOT approved | HOLD |
| 03 Twelve-minute question | Honest vendor claim separation + local disclosure | Non-live warm-up placeholder; no email permission, accepted link, published guide | HOLD + MERCHANT |
| 04 Hatch and spark | Strong historical counterweight and live Apollo CTA | Fourteen-second subject requires exact source check; R154 alternative exists but NOT approved | HOLD |
| 05 Before you press play | Useful independent checklist | Generic category vs exact Total Focus, absent buyer guide/merchant rights; R156 alternative NOT approved | HOLD + MERCHANT |
| 06 Evidence log | Fieldbook reflection value | Already provided Fieldbook in welcome; R155 distinct Piri Reis alternative NOT approved | HOLD |

Neither optional alternates nor fallback replacements may be silently substituted. All six demand honest subjects/preheaders, original substance, one primary CTA, complete source links, accessible HTML/plaintext and explicit final founder approval.

## FTC, consent, delivery & release line

Jetpack [official newsletter instructions](https://jetpack.com/support/newsletter/) distinguish non-sending **Preview email** from actual **Send test email** and confirm a per-post send toggle can override auto-send OFF. No native Jetpack rendering, received email, unsubscribe result or preheader has been independently inspected. Current reply_to=no-reply is not a functional opt-out route. The [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires honest sender/subject, conspicuous commercial nature, sender's actual valid **Final Vestige physical postal address**, and effective opt-out for commercial mail. Automattic's footer address in a subscription confirmation does not establish the publisher's. Direct/guide-linked commercial CTA must carry plain near-link commission disclosure in both HTML and plaintext, repeated beside merchant earning link on guide. Nothing is to be sent or published while the requirements remain open.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → EVIDENCE → OWNER

| Step | Blocker | Change/test | Evidence today | Owner |
|---|---|---|---|---|
| Focus/Dispatch → first click | Provider API self-link/no email input | Read-only guest browser + keyboard QA | API OBSERVED, guest UNKNOWN | Claude / Site QA |
| Welcome link → PDF | Unknown stale location | Independent welcome/media URL match | **MEDIA RECORD MATCHED**; actual delivery UNKNOWN | Dispatch |
| Signup → eligible confirmed lead | Nonadditive three/two counts | Native status filter + verified consent transition | UNKNOWN | Dispatch |
| Eligible lead → welcome | Only old confirmation message found | Consent-safe inspect actual received welcome | UNKNOWN | Dispatch |
| Draft letter → reader | Native email rendering/footer unverified | Non-sending Preview email, later authorized receipt QA | UNKNOWN | Dispatch/Claude |
| Zen12 → paid commission | Merchant approval and exact allowed email link/guide missing | Founder/Mind authenticated source-of-truth clearance | HARD HOLD | Mind / Founder |
| Paid commission → net revenue | Settlement/fees/refunds and qualified human sessions unavailable | Independent order+cohort reconciliation | NOT COMPUTABLE | Commerce/Praxxis |

## Independent source and test receipts, and boundaries

- provider_truth_contract.cjs + test_provider_truth_contract.cjs: **11 tests / 63 assertions PASS** using V8 Node-compatible shims against actual committed GitHub readback; no native Node claim. Distinguishes configured media, actual welcome, confirmed signup, ability to send, receipt and paid purchase.
- guest_firstclick_readonly.cjs + test_guest_firstclick_readonly.cjs: **7 tests / 37 assertions PASS** under V8 with Node and URL shim against actual GitHub readback. The URL shim is necessary because the code-runner V8 does not provide Node's global URL. A too-broad test matcher for ".type()" was narrowed to actual typing APIs, not console.message.type(). No live browser evidence.
- R160-REDACTED-PROVIDER-EVIDENCE.json: data from authenticated WordPress provider surfaces, aggregates only, no private subscriber records.

**18 test groups / 100 source assertions passed under V8 mocks**, with no native Python, native Node, browser, hosted CI or Jetpack delivery claim. Canonical PR #175 Python suite was read at its exact unchanged head; it was NOT natively executed anew because the GitHub connector files cannot be mounted directly into the Python runtime. Prior native-suite evidence remains in #174. On a real repo checkout: python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v; then node --test dispatch/campaign-2026-mind/r160/test_*.cjs.

**Final gate:** All 6 = **HOLD_UNSENT**; 03 and 05 additionally = **HOLD_MERCHANT**. No sending, scheduling, WordPress changes, subscriber contact/import/export, affiliate activation, social content, paid commerce, analytics scripts or expense. Source-controlled DRAFT and QD evidence only.
