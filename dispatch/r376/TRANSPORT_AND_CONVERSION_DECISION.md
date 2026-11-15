# R376 — Release truth and consent-to-net-revenue decision

Source of truth: Issue #174, companion #171, original PR #175, R375 PR #2602; read-only Jetpack and published site pages on November 15, 2026. This sprint changes no original manuscript or WordPress setting.

## Critical transport and consent finding

Jetpack still reports subscribers total=3, confirmed=3, unconfirmed=2. This is NOT a mathematical 3+2 audience; the WordPress subscriber guide explains unconfirmed records are excluded from total. Separately Stats reports WP.com followers=3 and email followers=0. These are distinct provider populations, and no individual emails or subscriber addresses are being retrieved or reported. The true number of unique, deliverable, opted-in *email* recipients remains UNKNOWN without the provider's Email Subscription = Subscribed and Not sending status filters, checked privately and recorded in aggregate only.

Source: https://wordpress.com/support/subscribers/

The Welcome setting contains the 52-page Focus Fieldbook PDF link and a promise of infrequent research dispatches, but configuration does not prove actual successful delivery. A read-only Gmail search yielded an October 25 subscription CONFIRMATION, not a subsequent received Welcome. This observation covers that searched inbox only, not the entire list.

The live /focus/ page includes client behavior that can expose a free download panel without provider verification of a confirmed email opt-in. The free download is legitimate; the panel and any subscribe URL parameter must never emit a confirmed_signup event. Use an opaque provider subscription key, current affirmative email state, deduplication, and no PII in public logs.

WordPress official email appearance guidance says post notification messages use donotreply@wordpress.com and the site can change the *display name*, not that source sender address. Current sender display name is Final Vestige Studios, reply behavior no-reply, full-text delivery selected. Original draft subjects and independently authored preheaders are therefore NOT verified as the eventual WordPress message Subject/preview text: the native post title must be checked, and independent preheader support must be established. Email-safe offline HTML is not a native Jetpack rendered message.

WordPress distinguishes a non-sending editor Preview email from Send test email (which sends). No editor preview, actual test message, native unsubscribe, business postal footer, or delivered inbox was produced. The publisher address is UNKNOWN; Automattic's service address does not establish a lawful Final Vestige business mailing address. FTC: a truthful sender/subject, identification of commercial content where necessary, qualifying postal address, working opt-out and timely honoring of opt-outs remain hard release gates.

WordPress source: https://wordpress.com/support/newsletter/email-appearance/ ; FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business

## Actual offer page alignment, not a catalog assumption

**Zen12 (draft issue 03):** https://zen12.com/getstarted presents 12 levels and 48 MP3s and a public $87.99 checkout after an on-page discount. https://zen12.com/secret/ shows a materially different $37 coupon route and countdown. Neither is an approved Final Vestige referral price. Do not copy time pressure, efficacy claims, unverified refund terms or imply a 12-minute recording has independently demonstrated one-hour effects.

**Hypnosis Live Total Focus (draft issue 05):** https://hypnosislive.com/mental-skills/total-focus describes a 33-minute, 47MB single MP3, and currently displays $24.44 on the retrieved public page. Bundled checkout options differ. Seller phrases about 100% concentration or reprogramming are commercial claims, not clinical research established for this specific product. The referred checkout, bundle choice and applicable refund conditions remain unverified.

**Partner permission:** https://affiliates.inspire3.com/ offers sign-up and promises special affiliate links; there is no account-specific Final Vestige evidence of approval, valid earning link, or permission to promote either SKU by EMAIL. https://inspire3.com/ll/ has mail swipe-copy but is a DIFFERENT product with an explicit approval requirement, not portable rights for the campaign. Mind/Commerce owns seller account, claim crosswalk, guide eligibility, checkout and settlement; Dispatch owns messaging and refusal to release.

## Offer → funnel → blocker → next action → proof → owner

| Offer / step | Blocker | Non-live change | Pass evidence | Owner |
|---|---|---|---|---|
| Zen12 buyer guide → checkout | No named EMAIL rights / earning URL / published warm-up / referred price | Obtain partner evidence for the exact SKU, then vet guide and only later enable one disclosed CTA | CURRENT HOLD; no account approval or sales proof | Mind/Commerce |
| /focus/ → confirmed_signup | A visible Fieldbook panel can be mistaken for confirmation | Define a provider-backed, deduplicated affirmative email-subscribed event, not a page/UI event | CURRENT HOLD; no unique recipient eligibility evidence | Focus/Claude |
| Welcome → retained reader | Settings not inbox delivery | Verify consented actual Welcome + PDF accessibility without contacting others | CURRENT HOLD; received welcome not observed | Focus/Founder |
| Dispatch → compliant inbox | Missing native email render, business address and functional opt-out | Authorized non-sending editor preview and publisher-attested address; separate approval before any real test | CURRENT HOLD; offline review != received email | Dispatch/Founder |
| Grok asset → settled commission | Qualified session and merchant settlement not joined | Read existing asset_id/UTM source convention only; join authorized aggregate 7/30 cohorts to reconciled paid partner report | CURRENT HOLD; no denominator and no settled numerator | Grok/Praxxis/Claude/Commerce |

## Explicit conversion contract

Qualifying steps: published source-tagged original Grok asset → qualified human session → related onsite CTA → provider-confirmed, deduplicated consent (when user signs up) → legitimately disclosed approved warm-up guide → permitted referral outbound click → independently settled paid affiliate conversion → refunds/fees → realized net revenue. An attempted signup, email click, WordPress Reader follow, 52-page PDF download, checkout start, or unsupported partner pixel is never a paid order.

Once both REAL data sets exist, compute 7-day and 30-day net revenue per 1,000 qualified human sessions as 1000 × (settled paid order revenue − refunds − fees − chargebacks) / independently qualified-human sessions. Missing numerator/denominator, or denominator <= 0, => NOT_COMPUTABLE, never an invented zero. Do not perform statistical A/B significance on a subscriber list this small.

**Decision:** All six original editions HOLD_UNSENT, merchant 03 and 05 HOLD_MERCHANT, new Issue02 candidate NOT_ADOPTED. NO email, schedule, test send, list contact/import, WordPress write, merchant activation, analytics deployment, Grok queue edit, merge, or spend.
