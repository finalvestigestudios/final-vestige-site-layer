# Dispatch R401 — exact-source QA, conversion findings, review-only release receipt

Date: 2026-11-16, read-only WordPress snapshot at **13:43–13:44 UTC**. Work owner: [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Editorial partner [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Canonical [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), historical per-issue gate [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), immediate predecessor [draft PR #2741](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2741). **All HOLD; no email.**

## What is NEW, not a rewrite of the original six issues
1. **Optional editorial Issue02**, linking to different, already-published historic Mesmerism investigation (WordPress post ID 1924). James Braid's catalogued original 1843 *Neurypnology* (Wellcome) provides a later change-in-explanation frame; no interior passages falsely quoted; no medical or seller efficacy claims. Original Issue01 and Issue02 both link Puységur; the optional new Issue02 avoids that repeated CTA, pending explicit founder editorial substitution.
2. **Full manuscript-parity offline HTML and plaintext specimens**, generated from the full authored markdown (not a shortened summary) with only **one main conversion CTA** plus separate archival citations. Tested 11/11 custom parity/source/accessibility static conditions. `html lang=en`, viewport, presentation table, no script, no tracking pixel, clearly visible UNSENT/NOT ADOPTED and five hard-stop tokens. These specimens do **not** pretend to be actual Jetpack email.
3. **New verified platform behavior:** WordPress official guide reviewed 2026-11-13 explicitly says the *WordPress post title is used as the newsletter email subject*. The six `**Preheader:**` lines are editorial metadata, not authenticated inbox snippets. New official Email Design was reviewed 2026-10-30 and is on **staged rollout**; not confirmed available on this site. A real native editor preview/actual received-email check is necessary to assess subject, preheader, footer and unsubscribe behavior.
4. **Fail-closed reviewer-only `release_gate.cjs` and authored `release_gate.test.cjs`**. Structural evidence requires reviewer+source+timestamp+opaque reference, separated by provider/native preview/received message/legal/founder/merchant. Editorial cases do not inherit commercial merchant terms; Issue04 additionally needs explicit Apollo correction adoption. Even hypothetical complete evidence yields `HUMAN_REVIEW_CANDIDATE_ONLY`, `send_authorized:false` and cannot authorize delivery.
5. **Conversion-first owner docket**, one provisional Zen12 path only, requiring named email channel rights and independently settled commissions, with no reader-level profile, extra list, tag code, email or published commerce link.

## Verifiable execution / evidence scope
- **Canonical source**: locally retained exact original eight Git blobs from previously documented canonical PR head, rechecked against GitHub on this R401 branch. Confirmed original manifest Git blob `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00`; original Python suite `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`; six canonical issue blobs unchanged. Executed `python -I -m unittest discover -s campaign-2026-mind/tests -v` **natively, 6/6 PASS, exit 0**. Test log held in the associated local evidence archive.
- **Exact fetched R401 gate source** Git blob `f7912f6d35e73f6fdfa035d77aac44b12321a7d3`, 3,013 bytes. Executed that **exact fetched source** in a sandboxed JavaScript V8 isolate: **37/37 assertions PASS**, including all-six hold, bad issue type, source authority, privacy-safe proof reference rejection, complete-proof never sending, Issue04 copy hold and seven adversarial manifest mutations. The authored Node test file was **NOT executed natively**; never describe it as such.
- **Canonical actual manifest** loaded directly from GitHub and evaluated by the fetched R401 gate: `MANIFEST_UNCHANGED_AS_DESCRIBED`, four editorial / two commercial-review-pending, zero active earning links, six hold, `send_authorized:false`.
- **Editorial reviewer preview tests**: initial 24/24 in-memory source/static checks pass; the full HTML/plaintext parity replacement passed 11/11 static assertions against the authored manuscript. Browser screenshots, actual email clients, inbox MIME and native Jetpack Preview were **NOT tested**. Static HTML accessibility hints are not WCAG certification.
- Final WordPress public page checks via authenticated connector: /dispatch/ published page 523, /focus/ published 1579, Editorial Standards published. Live /focus/ querystring `?subscribe=` pitfall remains with Claude/Focus owner; an alleged confirmation is not a provider-confirmed lead.
- WordPress current `subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=full`, `from_name=Final Vestige Studios`, `reply_to=no-reply`, `featured_image_in_email=true`; `site_can_send=true` is *ability*, not founder approval.
- Counts total 3 / confirmed 3 / unconfirmed 2 / suppressed 0; follower breakdown WP.com 3 / direct email 0 / comment 0, **not additive**. Five most recent posts `never_sent_opted_out`. Configured 52-page PDF welcome exists but **no received final welcome verified**, unique eligible inbox count unknown.
- Zen12 seller home and alternate promotional funnel can describe different pricing paths; Hypnosis Live Total Focus product-specific format/pricing is merchant-controlled; no named Final Vestige accepted partner account, product-specific **EMAIL** permission, issued earning URL, cleared guide, operational referral checkout or settled affiliate payout has been authenticated. Merchant claims never treated as independent findings.
- Postal address / functional unsubscribe in a final actual received commercial email **not verified**; Automattic's mailing address in its own confirmation message is not an FV publisher business address.

## New code/test caveat
The release gate checks structure of supplied evidence artifacts **not their truth**. Test fixtures use clearly synthetic `proof.example.org` references; real account/provider validation and founder decisions are entirely separate. The gate returns **no send permissions** under any condition. The new HTML is not WordPress-generated code, and an offline good-looking fixture is not proof of deliverability.

## Final decision
All canonical Issues 01–06 `HOLD_UNSENT`. 03 and 05 `HOLD_MERCHANT`, 04 `HOLD_COPY`. R401 alternate 02 `NOT_ADOPTED`. No sends, no test emails, no WP post or settings writes, no subscriber imports/contact, no affiliate activation, no spent funds and no merge. No paid conversions or audited qualified-human denominator: net revenue / 1,000 qualified sessions **NOT_COMPUTABLE**, not a verified zero.

### Reference sources
- Canonical: https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175
- Mind: https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171
- Wellcome 1843 original: https://wellcomecollection.org/works/g59kkex8
- Alternative 1843: https://content.www.wellcomecollection.org/works/demkv24m
- Published on-site CTA: https://finalvestige.com/2026/11/02/mesmerism/
- WP title/subject: https://wordpress.com/support/newsletter/send-newsletter-emails/
- WP native Preview: https://wordpress.com/support/newsletter/email-appearance/
- WP Email Design phased rollout: https://wordpress.com/support/newsletter-email-design/
- WP double opt-in and welcome: https://wordpress.com/support/newsletter-settings/
- FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- Named seller pages: https://zen12.com/ ; https://zen12.com/secret/ ; https://hypnosislive.com/mental-skills/total-focus .
