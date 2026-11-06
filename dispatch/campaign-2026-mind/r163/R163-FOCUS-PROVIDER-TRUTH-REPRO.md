# Dispatch R163 — Focus signup gift display: provider-truth regression (2026-11-06)

**Status: DRAFT / UNSENT / no WordPress mutation**. Source-of-truth: Issues #174, #129, #171, #820. This is not a Jetpack received-email preview, not a live browser test, and not consent or purchase evidence.

## Independent live-source observation
Authenticated WordPress page #1579 at /focus/ includes script `fvf-gift-v2`. Its `show()` executes whenever `new URLSearchParams(window.location.search).get('subscribe')` is truthy and not one of five denylisted error strings. The same script also reveals the gift on a subscriptions element with CSS class `is-subscriber`. Neither condition proves that the provider reports `Email subscription: Subscribed`. A publicly accessible PDF is not inherently a problem; the commercial risk is to confuse `gift_visible` or a client display with **confirmed consent** or delivered welcome.

Executed the observed JavaScript in a native Node.js VM with synthetic DOM and **no network requests, account creation, POST or real subscriber data**. `?subscribe=anything` and `?subscribe=confirmed` reveal the gift despite no provider evidence. `?subscribe=invalid_email` does not, and the class `is-subscriber` alone reveals it. Plain guest with no signal leaves it hidden. This proves a source-level conditional error, **not** live signup failure or a received PDF.

Read-only WordPress results **as of 2026-11-06 14:40 UTC**: Jetpack newsletter enabled; automatic new-post emails disabled; full email format; sender Final Vestige Studios; reply-to no-reply. WordPress counts total=3, confirmed=3, unconfirmed=2, suppressed=0, imported last 24h=0; overlapping categories do **not** imply five people or three email-eligible recipients. Five November 3 posts were never emailed (`never_sent_opted_out`). Welcome message contains the configured 52-page Fieldbook URL; **receipt unknown**. /dispatch/ #523 and /focus/ #1579 API content expose same-page Subscribe anchors without an HTML form, which does **not** prove real signed-out browser interactivity fails.

No merchant clearance surfaced from bounded read-only Gmail searches; generic Inspire3 promotional mail is **not** Final Vestige-specific account acceptance or email promotion permission. Mind #171 currently identifies its R169 Zen12 presell guide as **unpublished**, with earning link, partner approval and email rights unknown.

## Implemented NEW in this draft PR
- `test_live_wordpress_script_repro.cjs`: Five exact-behavior VM assertions against the stored Focus script logic; reveals its URL/CSS trust deficiency without hitting the site.
- `focus_signup_ui_gate.cjs`: deterministic, no-network offline evidence classifier; returns CHECK_YOUR_EMAIL unless an explicit provider email-subscribed status and independent provider consent are supplied. A client query/class/click cannot mint confirmed signup; welcome receipt is separately tracked and email reachability still cannot be claimed. Always returns HOLD_UNSENT / HOLD_MERCHANT.
- `test_focus_signup_ui_gate.cjs`: 19 synthetic evidence/negative-path assertions. **Native Node 22.16.0: 24/24 tests passed** on local equivalents; source-controlled GitHub readback and actual file hashes should be checked separately.

This module is **NOT** a replacement for actual provider-side verification and is **NOT wired to WordPress or analytics**.

## Narrow, proposed Claude / Site QA change (NOT APPLIED)
1. Remove the automatic gift-success state triggered by arbitrary `subscribe` query values. An allowlist of client-controlled strings is **still forgeable**. Do not infer confirmation from `.is-subscriber` unless the provider independently proves email subscription status.
2. On the page, clearly state: “If you're asked to confirm your email, open the confirmation message. Your Fieldbook link is included in the welcome email after confirmation.” Do **not** falsely say a subscriber was confirmed. If the PDF is offered to everyone, call it an **ungated free download** rather than a signup conversion.
3. Signed-out interactive review at 320/390/768/1440 px with tab/keyboard focus and no-JS path; then privately reconcile provider-native email-eligible statuses for existing subscribers. No actual signup or test email without founder's authorization.
4. Native WordPress *Preview email* rendering (not *Send test email*) and verified Final Vestige postal address/unsubscribe; the provider/Automattic address is not the sender address. Check sender and preview text. Don't send a campaign automatically from a post editor.
5. Preserve single Jetpack list and homepage PR #49. Coordinate Focus Issue #129 and the conversion KPI contract on Issue #820; Grok retains social posting and Praxxis retains creator analytics QA.

## Business outcomes and release gates
**OFFER → STEP → BLOCKER → CHANGE → EVIDENCE → OWNER**
- Focus Fieldbook → signup: client-side false-success display; remove URL/CSS confirmation and keep accurate instructions; **24 synthetic native tests PASS**, real guest verification UNKNOWN; Claude/Site QA.
- Signup → confirmed lead: provider *Email subscription* eligibility and opt-in data inaccessible here; private native reconciliation (no PII in issue); UNKNOWN; Dispatch/Claude.
- Confirmed lead → welcome: configured link only, no received message or download proof; non-sending/authorized verification; UNKNOWN; Dispatch.
- Zen12 → buyer: named account acceptance, explicit email rights, approved earning URL, live reviewed first-party guide and merchant terms absent; HOLD_MERCHANT; Mind #171.
- Buyer → revenue: independently settled FV commission/order, refunds/fees and qualified human sessions unavailable; NOT COMPUTABLE; Commerce/Praxxis.

Original six weekly drafts and **4 editorial / 2 conditional commercial** allocation unchanged. Commercial Issues 03 and 05 remain **HOLD_MERCHANT**. All six **HOLD_UNSENT**. The static artifacts contain no active affiliate earning link, real subscriber address, fabricated A/B result, sale or conversion.

## Measurement (proposal only, NOT LIVE)
`focus_signup_click` and `focus_gift_visible` are diagnostic, **not** `confirmed_signup`. Dedupe `confirmed_signup` once per provider-confirmed email subscription transition for a consented individual; anonymous reporting and private provider reconciliation. Grok inbound uses `utm_source=<actual_social_platform>&utm_medium=organic_social&utm_campaign=mind_pilot_2026_11&utm_content=<asset_id>`. Conditional approved Dispatch-to-guide CTA: `utm_source=dispatch&utm_medium=email&utm_campaign=dispatch_pilot_2026_11&utm_content=issue03`, no PII. Paid conversion means independently settled actual payout, not CTA click. Use 7/30-day cohorts; tiny sample warning. Do not inject duplicate scripts.

### Source references
- FV published standards: https://finalvestige.com/editorial-standards/
- WordPress subscriber distinctions: https://wordpress.com/support/subscribers/
- FTC commercial email: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- FTC endorsement guidance: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- Official merchant: https://zen12.com/hnp
- Canonical campaign PR #175: https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175
- Prior independent release controls PR #201: https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201
- Latest Dispatch parent PR #1260: https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1260
