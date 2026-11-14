# Conversion P0 — anonymous first click is an unverified *guest UX* issue
**Source read:** 2026-11-14 09:39 UTC, authenticated read-only WordPress page #523 (/dispatch/), #1579 (/focus/), Jetpack newsletter diagnostic and follower split. No production changes.

## Observation vs inference
- The WordPress page VIEW representation of published /dispatch/ contains a Jetpack subscriptions block, but inside it renders an anchor `href="https://finalvestige.com/?post_type=page&p=523"` instead of the expected email-input/submit form. This is **real representation evidence**, but could be an API/fallback representation rather than final browser DOM. It is NOT evidence anonymous visitors cannot sign up.
- `/dispatch/` promises the 52-page Fieldbook and confirmation step. The core subscriber-to-customer funnel depends on the first click resolving to a working consent flow. Therefore **actual anonymous guest browser test** outranks further copy/layout polishing.
- `/focus/` gives direct PDF access and subscription; its existing troubleshooting suggestion to **sign up again** risks needless repeat attempts. R350 already proposed a change; do not overwrite Claude/Focus ownership or pretend duplicates occurred.
- Jetpack status is total=3, confirmed=3, unconfirmed=2, suppressed=0; follower sources are WP.com=3/email=0. Their definitions and membership overlap are NOT established; 3+2 is not five recipients, nor is WP.com=3 proof that three inboxes can receive Dispatch.
- Welcome message **configuration** includes 52-page Fieldbook URL. This does NOT establish that any message or PDF reached an actual inbox.
- Five recent WordPress posts are `never_sent_opted_out`; status `site_can_send=true` means technical capability, NOT campaign permission.

## Reproducible anonymous guest acceptance (Claude/Focus owns implementation)
1. Open a fresh *signed-out* browser at /dispatch/ and /focus/ at 320px, 390px, 768px and desktop. Capture timestamp, URL, network/DOM state and screenshots with no accounts, cookies or PII in evidence.
2. Tab through to Subscribe. Record whether a labeled email field and explicit user-action submit control are present, or whether a legitimate WordPress.com modal opens. Do **not** enter any real or synthetic email or press submit. A click on a control known to instantly subscribe logged-in WP.com users is expressly prohibited; inspect role/actions without triggering it.
3. If a self-link is shown, record the actual **guest browser** navigation destination and whether an email form/modal appears. The REST/view HTML alone is not a FAIL verdict.
4. Confirm public direct Fieldbook PDF link accessibility independently with **GET/HEAD read-only** and a human-readable PDF; do not count downloads as signups.
5. Preserve no-send settings; no newsletter send/test, no signup, no welcome trigger, no opt-out test on a real recipient. Founder must separately authorize a controlled inbox/end-to-end test.
6. For real `confirmed_signup`: count **only provider-authenticated unique confirmed subscription transitions**; ID deduplication is private/hashed/provider-side. No subscriber identity in issues/telemetry. Stay UNKNOWN until source-of-truth export or private provider event trace is legally authorized.
7. Only when subscribed with appropriate consent and message-specific permissions may newsletter audience be evaluated. A marketing email must include Final Vestige's verified valid postal address and actual working rendered unsubscribe. Automattic's or merchant's address cannot substitute.

## Decision thresholds
- If guest browser presents usable accessible subscription control: **guest first click structurally PASS**, still no confirmation or welcome-delivery PASS.
- If guest browser demonstrably loops or fails and no alternate accessible subscribe control: **guest first click FAIL**, assign Claude/Focus to fix existing page, preserve consent platform, obtain founder approval before WP write.
- If authenticated editor snapshot only: **UNKNOWN**, no false performance conclusion.
- If provider aggregate counts look clean: unique confirmed lead **still UNKNOWN** without consent event evidence.

## Attribution owner handoff
Grok owns published asset IDs and UTM landing intents (TASK-008), Claude owns one deduplicated `confirmed_signup` provider event, Dispatch owns first-party email CTA `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_mind_pilot_2026_11&utm_content=issue_0N`, Mind owns approved guide eligibility, Commerce owns merchant settlements. Preserve first known Grok origin separately; an email click is not a paid order. Use 7/30-day cohorts, never infer identity joins from anonymous UTMs.

## Primary sources
[Live Dispatch](https://finalvestige.com/dispatch/), [Focus](https://finalvestige.com/focus/), [WordPress double opt-in](https://wordpress.com/support/newsletter/), [WordPress Preview email](https://wordpress.com/support/newsletter/email-appearance/), [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business), [site Editorial Standards](https://finalvestige.com/editorial-standards/).
