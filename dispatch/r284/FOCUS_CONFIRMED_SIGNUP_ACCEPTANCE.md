# R284 — Claude/Focus provider-authenticated signup acceptance contract (NON-DEPLOYED)
Owner Claude / Focus Issue #129. QA Dispatch #174. Revenue issue #820. **Specification only:** no production event emitted, new instrumentation inserted, user contacted, or WordPress changes.

## Verified source state / trust boundary
Authenticated 2026-11-11 16:31 UTC: Jetpack Newsletter ON, new-post emails default OFF, format FULL, welcome text CONFIGURED with 52-page PDF. Diagnostics 3 total, 3 confirmed, 2 unconfirmed; separate follower types 3 WordPress.com followers and 0 email followers. These are different counts. Actual email-eligible recipients UNKNOWN.

Published Focus page #1579 initially hides its gift panel, but JS may reveal it when URL subscribe status is arbitrary nonempty value not in a short denylist (documented in R283). A panel, URL param, PDF view/download, browser visual class, or email confirmation *request* is NOT proof of consent, confirmed eligibility, welcome receipt, or payment.

## One source-of-truth event: confirmed_signup (proposed, not deployed)
Emit only after **authenticated provider server confirmation** for the existing Dispatch list and appropriate consent scope. Validate current suppression, opt-out, and audience/category eligibility independently before any send. Client-submitted verified:true, a provider-looking URL value, or signup-form display is never a valid attestation.

Suggested internal fields: event_name=confirmed_signup; version=1; provider=jetpack; list=dispatch_existing; confirmed_at=provider timestamp; observed_at=backend timestamp; consent_scope=proven server-side value; eligibility_at_observation=provider-proven status; event_id=server-generated opaque idempotency key. Keep provider subscription identifiers private in restricted systems. NEVER send raw or hashed email addresses, identifiable subscription IDs, signed tokens or user details into GA, UTM query strings, social analytics, a public issue, or the client event.

Deduplicate by authenticated provider/list/subscription-lifecycle transition. Pending→confirmed can qualify ONCE. Confirmed→confirmed page reload/duplicate callback cannot create extra leads. Opted-out→resubscribed qualifies only if the provider authenticates a new consent lifecycle; it does not automatically authorize the commercial email category. Any suppression or unsubscribe blocks delivery even if an earlier lead event exists.

## Acceptance truth table (use synthetic provider fixtures; not real signups)
| Scenario | Public state | confirmed_signup | eligible to receive email |
|---|---|---|---|
| New visitor, no provider status | no confirmation assertion | NONE | UNKNOWN |
| URL has subscribe=unknown_state | NEVER assert confirmed | NONE | UNKNOWN |
| Typed email / pending confirmation | check inbox (conditional) | NONE | NO confirmed evidence |
| Genuine confirmation-request email | pending | NONE | NO confirmed evidence |
| Provider-confirmed transition + correct consent | verified status if securely supplied | ONCE | only if provider eligible |
| Replay / refresh / double CTA clicks | show suitable non-counting state | NONE additional | recheck provider |
| WordPress Reader follower only | don't pretend email consent | NONE | UNKNOWN/NO |
| Suppressed, unsubscribed or wrong category | no promise of delivery | NONE | NO |
| Public Fieldbook PDF download | free resource; no subscription proof | NONE | UNKNOWN |
| Merchant Zen12 free-audio signup | merchant-owned separate list | NONE | NO FV evidence |

## Grok → Focus → Dispatch attribution; NOT ACTIVATED
Preserve Grok TASK-008 canonical asset UTMs: utm_source=<actual platform>, utm_medium=organic_social, utm_campaign=<topic_cluster>_pilot_2026_11, utm_content=<real immutable asset_id>. Grok owns social production IDs, Praxxis owns independent QA, Claude owns instrumentation. Respect caption/bio routing and lost referrers; unobservable sessions are not fabricated. Resolve mind_pilot_2026_11 versus mind_proposed_2026_11 before standardizing.

For a someday-approved email CTA only: utm_source=dispatch, utm_medium=email, utm_campaign=dispatch_pilot_2026_11, utm_content=issue_01...issue_06. Nothing is sent or deployed here. No person-specific link tokens, no raw PII, no unauthorized analytics duplication. Only set source attribution with appropriate analytics consent; do not tie different people's activity by weak fingerprint guesses.

Provider-confirmed signup is distinct from qualified visit, content/guide click, opt-out, delivery, a paid order, an authorized affiliate commission and final net revenue. Do not sum overlapping subscriber categories. Only authentic independently reported merchant orders and settlements less refunds and fees establish net revenue; keep unattributed orders separate. Report 7-day and 30-day tiny-sample limits.

## Founder-gated acceptance dependencies
1. Claude verifies source of provider confirmation, lifecycle replay, suppression and count semantics using consent-safe authorized fixtures; redacted evidence under #129. DO NOT query/expose subscriber email addresses.
2. Claude proposes a local source repair of Focus gift gate; actual production edit must be separately approved. A server-verified panel must not create a duplicate list or require paid tooling.
3. Dispatch may inspect the native WordPress preview only if it does NOT send. Actual received-email MIME and functional unsubscribe require separately authorized test delivery and Final Vestige's valid real postal address. Old Automattic confirmation is NOT publisher proof.
4. Mind Studio authenticates publisher account acceptance, permitted EMAIL channel, approved link and current guide; public affiliate registration is insufficient.
5. Commerce verifies paid settlement, refunds, fees and denominator before business KPI.

Hard gates: no test sends, no contacts, no WordPress changes, no affiliate activation or sending without final founder approval.
