# Dispatch R76: Real site traffic, zero invented newsletter attribution
Status: November 2, 2026 — all six HOLD_UNSENT; Issues 03/05 additionally HOLD_MERCHANT.

## What is new
This independent stacked draft follows the R75 channel and consent report in PR #681. It adds an **authenticated WordPress.com site traffic baseline**, not another email mockup or subscriber test. Existing master PR #175 includes the six canonical letters. PR #201 owns edition release gates and alternate no-offer letters. Nothing here changes any original letter, WordPress page, mailing setting, email subscriber, affiliate link, or homepage PR #49.

## Source-reported statistics, not modeled
Authenticated WordPress.com statistics.get on 2026-11-02:
- Oct 19–25 inclusive: 287 site-wide views, 18 visitors; 0 posts, 0 pages published in this period.
- Oct 26–Nov 1 inclusive: 795 site-wide views, 17 visitors; 0 posts, 1 page published in this period.
- Nov 2 current INCOMPLETE day: 32 views, 6 visitors at check; exclude from comparison.

The prior and recent complete-week numbers yield +508 views but -1 visitor. That is not evidence of email marketing success. Repeated visits, automated audits, previews, crawlers or other unexplained traffic may affect views. The native site-wide statistics endpoint does not expose email-related referrer, per-URL intent or unique campaign conversions. Site total 67 posts/99 pages cannot be equated with previous published-investigation inventories; scopes can differ.

Authenticated WordPress newsletter.status at 2026-11-02T22:29:42Z: total=2, confirmed=2, unconfirmed=2, suppressed=0, recent_sends empty; subscribers overlap and email-eligible recipients remain UNKNOWN. The get_settings check at 22:29:45Z showed Jetpack enabled, new-post auto-send OFF, excerpt content, sender Final Vestige, and configured 52-page Fieldbook welcome; actual receipt unverified.

## Safe executable contract
The source_snapshot.json has AGGREGATES ONLY. The read-only Python metrics_contract.py accepts a fixed schema and rejects unknown fields (so a subscriber address/URL/token cannot be injected), negative or boolean counts, misaligned date windows, and unexpected merchant slots. It emits local JSON, HTML and plain-text review reports. Unknown email opens, campaign-site visits, Fieldbook downloads, guide clicks, paid conversions and A/B winner stay NULL / NOT_OBSERVED, never synthetic zero. The routine always returns HOLD_UNSENT and cannot approve any sends, even if supplied merchant flags are true. This is an offline reporting tool, no network/pixels, tracking, cookies, external images or emails.

Execution from its directory:
python -I metrics_contract.py --input source_snapshot.json --output-dir ./local-review
Native tests from parent:
python -I -m unittest discover -s tests -p test_r76_source_attribution.py

## Policy: truthful measurement and attribution
Observed website traffic can be described only as traffic. Do not infer email recipient engagement, top posts, signups, clicks, downloads or affiliate purchases from a sitewide view change. A newsletter sent to two reported total subscribers (with unknown eligibility) cannot support A/B winner claims. If sources lack the data, store NOT_OBSERVED rather than numeric zero. Partial days are not comparable to full weeks; use fixed windows and source timestamps.

A future founder-authorized pilot may observe per-edition post ID, exact approved title and send timestamp from Jetpack; aggregate eligible-email count from native filtered subscriber screen without identities; privacy-compliant site referrals only where objectively supported; offer-guide clicks only through separately approved site analytics; settled vendor transactions only when actually reported through an authorized, non-PII merchant account. An outbound click is NOT a sale and sitewide pageviews are NOT email attributable by themselves. There is no new platform expense or list.

## Copy + source scrutiny and channel blockers
The six-issue plan remains FOUR source-led editorial letters (perception, Puységur, Apollo, evidence log) and TWO independent offer examinations reserved for Zen12 and Total Focus. Neither published, approved buyer-guide CTA exists. An original Apollo subject says "Fourteen seconds"; another draft says "Seventeen seconds". A founder-reviewed evidence-first subject might be "Apollo 1: why one spark was never the whole story", but no replacement approved. The two commercial issues must place prospective commission disclosure near the relevant CTA and early enough to survive real excerpt-mode email delivery; no invented claims/prices.

Public /dispatch/ promises investigations and archive finds; /focus/ explicitly mentions possible commission-earning recommendations. R75 drafted an optional consent-alignment sentence, NOT published. The same Jetpack list does not establish that all subscribers joined under identical expectations. There has been no approved received email, verified opt-out, qualified Final Vestige physical mailing address, or welcome receipt.

Official WordPress support: https://wordpress.com/support/newsletter/email-appearance/ and https://wordpress.com/support/newsletter-settings/ . Excerpt mode uses a custom excerpt or first approximately 55 words; a native preview is NOT actual received mail. FTC CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . An Automattic postal address on a subscription confirmation is not a verified Final Vestige mailing address, and a syntactically correct unsubscribe link is not proof it works.

Merchant-source alignment, checked November 2: Zen12 exact sales https://zen12.com/hnp describes 12-minute sessions, 12 levels and 4 formats; equivalence to an hour, brainwave and health claims are seller assertions, not verified named-product outcomes. Total Focus exact page https://hypnosislive.com/mental-skills/total-focus describes 33-minute/47-MB audio; promises of 100% concentration, brain reprogramming and career improvement are vendor marketing, not independently established. No newsletter fixed prices/refund representations. Inspire3 promotional page https://inspire3.com/ll/ explicitly covers DIFFERENT product Limitless Labs and cannot confer Zen12/Total Focus permission to email. Inspire3 privacy https://inspire3.com/privacy/ says purchaser identity data may be shared with referring affiliates; no buyer PII collection is authorized.

## Release
ALL SIX HOLD_UNSENT; #03/#05 HOLD_MERCHANT. Missing verified named-offer partner EMAIL permission and approved earning URL, live approved warm-up pages, actual filtered email eligibility, Final Vestige-owned valid postal address, real founder-authorized received Jetpack preview+functional unsubscribe, and explicit final founder approval of copy/audience/schedule/sending. No site changes, test messages, subscriber contacts, merchants contacted, production writes, affiliate links or traffic tracking. Issue #174 is the Dispatch master; Issue #171 is the independent Mind owner.
