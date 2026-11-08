# Dispatch R127 — WordPress account confirmation and conversion acceptance
**SOURCE-CONTROLLED DRAFT ONLY • NO SUBSCRIBER CONTACT • ALL SIX UNSENT • 03/05 HOLD_MERCHANT**

Parent PR #1019. Preserve master campaign #175, independent gate #201 and 4 editorial / 2 offer-reserved allocation. Frozen homepage PR #49 is not touched. This lane does not own social, merchant guide publishing, or production analytics.

## NEW verified platform distinction (read-only, 2026-11-04)
WordPress.com's official Newsletter settings explicitly says that **new signups without a WordPress.com account receive a confirmation email first**, whereas **signups already holding a WordPress.com account skip that separate confirmation email** and receive a welcome immediately. The general October 5 Subscribe-to-a-site page describes confirmation generically; use the more specific conditional documentation for this audit.

Sources:
- https://wordpress.com/support/newsletter-settings/ — confirmation-path difference; welcome after confirmed address.
- https://jetpack.com/support/newsletter/customize-the-newsletter-experience/ — same exception for existing accounts; welcome message handling.
- https://wordpress.com/support/subscribers/ — "Not confirmed" not counted in total, with Email subscription statuses Subscribed, Not subscribed, Not confirmed, Bounced, Emails paused, Not sending.
- https://jetpack.com/support/newsletter/ — account migration and preview versus received email distinction.

**Implication:** Do not treat absence of a confirmation message as proof that a WordPress.com-account subscriber failed consent. Conversely, do not treat an aggregate "confirmed" or WordPress.com follower as proof of marketing-email eligibility. Native status transitions, requested newsletters, confirmed/account context and actual received welcome must be separately reviewed.

## Live source observation
On November 5 at 02:34:13 UTC the authenticated Newsletter status returned: total=3, confirmed=3, unconfirmed=2, suppressed=0, paid=0, imported24h=1. Recent five posts: never_sent_opted_out. Newsletter enabled/site_can_send true, but **no campaign email sent**. Because the WP Not confirmed status is excluded from the counted total, the diagnostics' 3+2 is not evidence of five active subscribers; verify if diagnostics' unconfirmed maps exactly to native status before any confident reconciliation. Prior Jetpack follower total3/legacy-email0/wpcom3 cannot establish reachable count. No addresses accessed.

Dispatch page #523 remains publicly published and uses a native Jetpack subscriptions block. Focus page #1579 remains public, and its query/CSS PDF reveal does not prove native confirmation. Source correction remains draft PR #1007; production deployment is Claude's responsibility.

## One actual Jetpack preview is still missing
Official Jetpack documentation describes **Preview email** for an unpublished post even with the send switch OFF; it does not require sending. The connector currently available to this lane exposes post/page reads, Newsletter settings/diagnostics, but **does not expose the block editor's native Preview email action or filtered per-subscriber email statuses**. Therefore do not substitute offline HTML, synthetic MIME, or screenshots from a different renderer.

Read-only next step for authorized WP editor: (1) verify post draft and email-toggle OFF; (2) use Jetpack Newsletter sidebar → Preview email (NOT Send test email); (3) capture desktop/mobile renders of subject, excerpt, CTA, near-offer disclosure, postal/footer/unsubscribe; (4) record exact source post revision, as-of time, and preview screenshot. A native editor preview is still NOT a received email; separate founder authorization is required before any test message. **Do not publish posts to obtain a preview.**

## Native subscriber dashboard reconciliation without PII
In WP Admin → Jetpack → Newsletter → Subscribers, use only **Email subscription** filters and record aggregate totals for Subscribed / Not subscribed / Not confirmed / Bounced / Emails paused / Not sending. Do NOT use "Not sending (any reason)" in a sum with the overlapping statuses. Do NOT search by or copy names, addresses, subscriber IDs, screenshots of individuals, or exports. Review confirmation method privately without recording identity. No changes to subscription status. This tool contract requires real status-filter data, not the existing follower summary.

## Source-grounded offer claims and hold
Official merchant **Zen12** sales page https://zen12.com/hnp advertises 12-minute sessions and a Premium library of 48 MP3s, plus a purported one-year money-back guarantee and price panels. These are **seller statements**, NOT evidence the 12-minute practice equals an hour of meditation, that brainwave entrainment is proven specifically for Zen12, or that present checkout/renewal/refund terms apply to the user. Do not quote prices/coupons/guarantees as verified final buyer terms. R131 Mind handoff #171 reports unpublished guide and no named affiliate approval, authorized email promotion, or live earning link. Issue 05 Hypnosis Live remains similarly unapproved. The commercial issues' email CTA destinations stay null until a live first-party buyer guide and named permission are verified. Prospective same-issue disclosure: "If you buy through a link in our guide, Final Vestige may earn a commission."

## Commercial/legal acceptance
FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business — valid Final Vestige physical mailing address, accurate subject/sender and a working opt-out in the received/rendered commercial email are release gates. Automattic's address on a WordPress confirmation email does not meet FV's own verified publisher-address requirement. Need legal confirmation of sender and footer; this package cannot approve sending.

## Conversion ledger and handoff
**Offer → funnel → blocker → action/experiment → pass evidence → owner**
1. **Free Fieldbook → confirmed lead:** two distinct confirmation paths and reachability unknown → audit native email status and consent transitions → source-attested per-path aggregate, no PII → Dispatch/Claude. **FAIL / UNKNOWN now.**
2. **Welcome → Fieldbook:** sender receipt and 52-page PDF open unknown → review authorized actual received welcome and PDF → real mailbox evidence and PDF validation → Dispatch/Site QA. **UNKNOWN now.**
3. **Editorial issue → first-party article:** true Jetpack preview not captured → exact draft with toggle OFF and native visual preview → subject/excerpt/footer/CTA screenshots at 360/390/768 desktop → Dispatch/Site QA. **UNKNOWN now.**
4. **Zen12 → buyer:** email rights, guide live, checkout terms unknown → Mind validates named rights and publishes only after separate approval → actual accepted merchant terms + live first-party guide + approved tracking link → Mind Studio. **HOLD_MERCHANT.**
5. **Grok → verified net revenue:** asset-linked qualified-human sessions and settled orders missing → Claude reconcile authenticated orders/refunds/fees to existing source tags → 7/30-day cohorts, honest missing-source flags and tiny-n limits → Claude/Praxxis. **NOT COMPUTABLE.**

No new forms/scripts, costs, subscriber list, sending, CMS writes, or affiliates. This is a native-status acceptance specification and synthetic code QA only; it does NOT establish actual consent, real delivery, settled orders, or a legal opinion.
