# Dispatch R126 — native subscriber-classification and commercial-path QA

**Unmerged DRAFT; all six HOLD_UNSENT; commercial 03/05 HOLD_MERCHANT.** Owner Issue #174, master PR #175, source gate #201, parent PR #1013, affiliate Issue #171, conversion Issue #820. No newsletter manuscripts, original PR, or homepage PR #49 modified.

## New read-only finding (2026-11-05 01:33 UTC)
WordPress newsletter diagnostics: **total 3, confirmed 3, unconfirmed 2, imported last 24h 1**; new-post automatic emails OFF, format **excerpt**, last five post notifications `never_sent_opted_out`. Separate Jetpack follower stats: **total 3, email 0, WordPress.com 3, comment 0**, `partial=false`. These two views use distinct classifications. DO NOT treat 0 legacy email followers as 0 email-reachable people; DO NOT add confirmed and unconfirmed into 5. Jetpack documentation says subscribers may have WordPress.com accounts. The real deliverable set must be read from the native **Email subscription** status across subscribers: Subscribed, Not subscribed, Not confirmed, Bounced, Emails paused, Not sending. Neither aggregate endpoint returned that full breakdown; verified reachable count is **UNKNOWN**, not 0 or 3. An import count is not proof of affirmative consent or a new confirmed_signup event.

The connected /dispatch/ page (523) is PUBLISHED but its REST-rendered subscriptions block shows a self-link fallback `?post_type=page&p=523`; whether interactive subscription works needs a real browser, not an assumption. /focus/ page (1579) is PUBLISHED and its download reveal is not authenticated subscription confirmation (related unmerged proposed correction #1007). Its public PDF link is configured in the existing welcome message, but received completion and document access remain unverified. Gmail's Oct 25 confirmation is not the welcome message.

## Original four editorial / two reserved affiliate issues
`recipient_contract.cjs` creates static *preview-only* original-master editorial CTA URLs using privacy-safe tags: `utm_source=dispatch&utm_medium=email&utm_campaign=mind_pilot_2026_11&utm_content=dispatch_issue_0N`. The 01 and 02 routes intentionally match original PR #175 (Puységur); 04 goes to original Apollo 1; 06 still points to Focus and is **flagged for returning-subscriber repeated-signup review**. This is not founder approval of rewritten CTAs. For 03 Zen12 and 05 Hypnosis Live, both guide URLs remain null and no merchant URLs are present. There is no new tracker or subscriber identifier, no A/B claims. Jetpack emails require publication of a **new post**; this is not a tested automated post-signup drip. No posts or sends authorized.

## One independently substantiated partner-promotion reality check
The public Inspire3 affiliate network marketing page says it provides partner-specific links, but it is not an authenticated Final Vestige affiliate account; commission/EPC claims there are *marketing claims*, not FV earned revenue. The exact seller pages advertise Zen12 twelve levels / 48 MP3s and Hypnosis Live Total Focus 33 minutes / 47 MB. Prices, guarantees and effectiveness are seller representations; affiliate acceptance, exact email-channel permission, claim proof, rights-cleared creative, tracking URL, approved published warm-up guide, real buyer terms and settlement are **NOT VERIFIED**. Adjacent to any future earning link, clear commission disclosure is needed. The FTC requires truthful claims, sender identification, valid publisher postal address, and functional unsubscribe; Automattic's address is not Final Vestige's.

## Native test run
`node dispatch/campaign-2026-mind/r126-native-channel-evidence/test_contract.cjs`
Test mutations reject counts as leads, legacy-email=0 as eligibility, bad/partial native snapshots, personal data, missing provider email-status groups, merchant/PII URLs, activated links and fake sending/outcomes. Even synthetic full evidence cannot release emails.

## OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER
- Focus Fieldbook → confirmed, reachable subscriber → overlapping counters/unknown actual email status → inspect read-only native subscriber Email subscription filter; verify received welcome → SNAPSHOT VERIFIED; EMAIL STATUS/WELCOME NOT VERIFIED → Dispatch + Claude.
- Editorial archive → site-returning reader → excerpt-only rendering / possible self-link signup fallback → authorized **editor Preview email** + browser QA (no send), review 4 static first-party tags → NOT TESTED LIVE → Dispatch + Claude.
- Zen12 (provisional) → first-party buyer guide → named partner acceptance/email permission and live warm-up missing → Mind #171 verifies authorized channel and exact merchant terms → HOLD_MERCHANT → Mind.
- Grok source → paid net revenue → asset IDs, qualified human sessions and merchant-settled orders/fees/refunds unjoined → report not computable; no substitute click metrics → Praxxis + Claude #820.

**Commercial KPI:** realized net revenue per 1,000 qualified human sessions: NOT COMPUTABLE. No email sent/tested/scheduled; no WordPress/affiliate/list/social/spending changes.

## Official sources
- https://jetpack.com/support/newsletter/
- https://wordpress.com/support/subscribers/
- https://wordpress.com/support/newsletter-settings/
- https://affiliates.inspire3.com/
- https://zen12.com/hnp
- https://hypnosislive.com/mental-skills/total-focus
- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
