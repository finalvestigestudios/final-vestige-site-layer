# Dispatch R95 — merchant authorization and claim-conflict handoff (HOLD / UNSENT)

**Evidence date: 2026-11-03.** Master [six-issue PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175); [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); [Mind & Affiliate #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171); stacked on [R94 #811](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/811). Four historical/perception editorial editions **01/02/04/06**, two commercial-reserved **03/05**. All six HOLD_UNSENT; 03/05 additional HOLD_MERCHANT. Original copy, WordPress, signup list, checkout links, homepage and frozen PR #49 untouched. No outreach, service expense, list import or test email.

## Material new findings from official merchant sources (November 3)

| Source | Verified public-page detail | What it **does not** prove |
| --- | --- | --- |
| [Inspire3 affiliate portal](https://affiliates.inspire3.com/) | Signup/login invitation and generic payout/special-link marketing | Named **Final Vestige** acceptance, exact eligible products, permission to market by **EMAIL**, authorized earning URL, exact commission or creative rights. |
| [Zen12 official HNP](https://zen12.com/hnp) | Twelve-minute audio sessions, 12 levels/four sound styles, full 48-MP3 vs 24-MP3 beginner tier; advertises one-year refund and one-hour equivalence. | The specific brainwave efficacy, “12 minutes = 1 hour” equivalence, tier selected by a future tracked URL or binding refund terms are independently verified. |
| [Total Focus exact page](https://hypnosislive.com/mental-skills/total-focus) | **33 minutes / 47 MB**, displays **$24.44** promotion against $29.95 comparison, 14-day refund summary, makes extremely strong concentration promises. | Seller’s concentration guarantees are independently established, future price is locked, or that the page includes every restriction. |
| [Hypnosis Live FAQ](https://hypnosislive.com/faq) | Says sessions **typically $22.95**, **most ~40 minutes** (general, not Total Focus); says refund requests within 14 days with a **maximum five refunded sessions per year**, plus processing-time detail. | FAQ general price/length applies to this particular 33-minute product, or a commercial message may omit refund limitations. |
| [Inspire3 privacy](https://inspire3.com/privacy/) | Vendor says it **may share referred buyer's name, email and product purchases with the affiliate**; also describes telephone/SMS marketing for supplied numbers. | FV has consent/need/legal basis to acquire purchaser identities; FV's existing subscriber list may be passed to the vendor. |
| [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) | Covered commercial emails need honest sender/subjects, ad identification, publisher physical postal address, and workable opt-out honored promptly. | Merchant, Automattic or WordPress mailing address substitutes for the **Final Vestige** qualifying address; offline preview proves unsub functionality. |
| [WordPress native email guide](https://wordpress.com/support/newsletter/email-appearance/) | Per-post subscriber toggle gates native preview/test; title provides native subject, manual excerpt provides introduction, native Read-more links to eventual post. | Existing HTML files are actual received email, or preheader is separate supported field. |

**Conflict requiring decision:** Total Focus specific 33min/47MB and displayed price differ from generic FAQ “most sessions ~40min” and “typically $22.95”; the FAQ further discloses a **five-refund yearly cap** missing from the product page's brief guarantee copy. Exclude prices/discounts/refund assurances from newsletter text until current merchant terms and the exact checkout are independently reconciled. Zen12's merchant-advertised “12min = one hour” is not independently established for that product. Seller claims must be attributed and not upgraded to Final Vestige findings.

## Priority — partner-channel permission and private customer data

Public affiliate signup/marketing and publicly downloadable seller “swipe copy” for **other products** cannot establish Final Vestige authorization for **Zen12** or **Hypnosis Live Total Focus**, let alone email-list promotion. Require a named authorized partner reply, approval of the *specific product* and *specific EMAIL channel* (also separately website, social), proper link generator/creative rights, exact landing tier/checkout terms and full advertising restrictions. Require **written exclusion of buyer-identifiable data** from affiliate account reports, emails, exports or API feeds; aggregate conversion/revenue data suffice. If the exclusion cannot be guaranteed, keep offers disabled pending a privacy/legal review. Do not put private correspondence or identities in public GitHub files.

### Exact founder-review outreach draft — **NOT SENT**

**Subject: Final Vestige Studios — written affiliate/email eligibility for Zen12 and Hypnosis Live Total Focus**

Hello Inspire3 Affiliate Team,

We publish independent, research-based investigations and a small, existing opt-in WordPress/Jetpack editorial newsletter. Before considering an optional recommendation for Zen12 or Hypnosis Live Total Focus, please clarify **separately for each named product**:

1. Is the **Final Vestige Studios** affiliate account accepted to promote it? Which signed program terms govern, and do they explicitly allow **opted-in newsletter EMAIL** promotion (separate from first-party websites or short-form social)?
2. Is our proposed reader journey permitted: evidence-based first-party buyer guide with conspicuous near-link commission disclosure → official approved partner URL? Please identify exact approved link/deep-link format, claims, branding, prohibited language, and permissible creative/swipe use. We do not plan to reproduce unverified benefit claims or testimonials as fact.
3. Which currently available Zen12 package/checkout (12 levels / 48 MP3s or six levels / 24 MP3s), exact Total Focus 33min/47MB product, pricing, taxes, recurring billing/upsells and refund terms govern? Please reconcile the Total Focus product-page price with the general FAQ, and the FAQ’s **five-session annual refund limitation**.
4. Your published privacy policy says affiliate-referred purchases may share buyer name, email and item details with an affiliate. **Please confirm in writing that our account can receive aggregate-only reporting and suppress all individual buyer names, email addresses, phone numbers, itemized order data and other identifiers in reports, alerts, exports and feeds.** We will not send you our newsletter subscriber records.
5. Please provide the applicable current agreement, link permissions and approved creatives via the official partner channel and a contact authorized to certify these terms. If users supply mobile numbers, clarify consent/marketing responsibilities.

No live merchant link or promotional send is in place. Thank you.

— Final Vestige Studios

**Do not dispatch this inquiry without a separate authorized instruction.** Drafted for private review only.

## Read-only technical guard

`merchant_evidence.json` is an all-false, dated **public-information ledger**, not written permission. `partner_proof.py` and `test_partner_proof.py` check exact six-issue 4:2 allocation, 03/05 product mapping, publisher status, all 11 external proof requirements, closed merchant links, privacy-sensitive field injection, public-source URI origin and claim differences. Output is ALWAYS `ready_to_send: false`; software tests cannot attest a real affiliate contract, actual email MIME, recipient consent, working unsubscribe, publisher postal address or founder approval. Run offline: `python -I partner_proof.py` and `python -I -m unittest discover -s . -p 'test_partner_proof.py' -v`. No network, send or WordPress mutation path.

Live WP read-only November 3: `subscriptions=true`, `site_can_send=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`; configured 52-page Focus Fieldbook welcome, **actual receipt unknown**. Newsletter counters total=2, confirmed=2, unconfirmed=2 conflict with separate full follower stats email=0, WP.com=2; recipient eligibility **UNKNOWN**. Unconfirmed/unsubscribes must never be inferred as extra addressees. **All six remain HOLD_UNSENT; 03/05 HOLD_MERCHANT.** A genuine received-message footer/opt-out and qualifying Final Vestige postal address are not verified. No live guide is approved for either commercial slot. This audit is not legal advice.
