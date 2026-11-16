# Dispatch R410 — Focus → Dispatch: source-of-truth lead audit

**HOLD / READ-ONLY / NO SEND.** Issue [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), companion [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), Focus [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), revenue [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). Stacked on [R409 #2795](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2795); original six-issue draft [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) and per-edition gate [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) unchanged.

## Critical new read-only finding

Authenticated WordPress **/focus/** page ID 1579 (modified 2026-11-16T14:54:58 in provider response) contains the `fvf-gift-v2` inline script. Its logic displays the gift after any nonempty `subscribe` URL value except five literal errors: `invalid_email`, `error`, `blocked_email`, `opted_out`, `blocked`. A second condition displays it when the subscriptions-container CSS class matches `/\bis-subscriber\b/`. The panel contains the free 52-page PDF link, visibly asks the visitor to **confirm their email**, and labels the download `data-fv-event="focus_pdf_click"`, `data-fv-location="after_signup"`.

**Source-faithful native Node regression (27/27 PASS)**: In a simulated DOM, `?subscribe=success`, `?subscribe=confirmed`, `?subscribe=paid`, `?subscribe=false` and `?subscribe=arbitrary` all display the gift, without authenticated provider confirmation. `?subscribe=blocked` stays hidden. The regex also recognizes `maybe-is-subscriber-later` because hyphens are word boundaries. This is a demonstration of *client UI-state semantics*, not evidence that WordPress emits those odd values or CSS classes.

**Do not misclassify this as an auth bypass or broken opt-in.** Providing a free download after a form attempt can be intentional; the PDF is already a public resource. The actionable risk is counting gift appearance, URL flags, `focus_pdf_click` or a CSS class as a provider-confirmed subscriber. None can establish opted-in recipient eligibility, successful welcome delivery or paid conversion. Native Jetpack form rendering in an actual browser has NOT been inspected; WordPress's read-only returned page contains a fallback Subscribe link, which alone cannot prove the live form is defective.

## Authoritative confirmed_signup (proposal only, not deployed)

Claude/Focus should count one `confirmed_signup` only when an authenticated Jetpack/provider source record establishes **confirmation, current email eligibility and no suppression/unsubscribe**, reconciled and deduplicated by provider-authoritative subscriber identity. A new page view, download, browser query, attempt, message configuration, CSS state, or aggregated dashboard count must not emit that event. Never expose email addresses, confirmation tokens, raw provider IDs or hashes reusable across sites in browser telemetry or GitHub. If underlying records cannot be inspected, report `UNKNOWN`.

Track as **separate evidence classes**, using existing approved site analytics rather than adding competing JS: qualified `focus_landing`, optional `focus_subscribe_attempt`, provider-authenticated `confirmed_signup`, independently witnessed `fieldbook_welcome_delivered`, `focus_pdf_click`, `dispatch_cta_click`, and merchant-authenticated `affiliate_order_settled`. No click or welcome message setting is a paid order. Paid commissions must be reconciled after refunds and fees in 7/30-day cohorts.

Attribution uses the existing Grok/Praxxis TASK-008 conventions: social `utm_source` actual platform, `utm_medium=organic_social`, `utm_campaign=<topic>_pilot_2026_11`, `utm_content=<published asset_id>`; approved newsletter CTA `utm_source=dispatch`, `utm_medium=email`, `utm_campaign=dispatch_pilot_2026_11`, `utm_content=issue_01` ... `issue_06`. These are only **planned names**: do not deploy links or duplicate trackers. Preserve source-to-landing context only with valid consent and approved retention.

## Current provider truth, 2026-11-16 23:38 UTC

| Read-only source | Observation | What it proves |
|---|---|---|
| Jetpack newsletter | Enabled, site_can_send true, new-post email default OFF | Platform capability, NOT send approval |
| Subscriber counters | Total 3 / confirmed 3 / unconfirmed 2 | Overlapping categories, NOT five distinct people |
| Followers | WordPress.com 3 / direct-email 0 | Different follower categories, NOT a unique deliverable list |
| Recent five posts | All `never_sent_opted_out` | No successful notification in these five examples |
| Welcome | 52-page Focus Fieldbook configured | Content setting, NOT receipt |
| Native Jetpack email Preview | Not performed | True inbox appearance / FV address / unsubscribe still missing |
| Product-specific merchant email rights | Unverified for both | Commercial Issues 03 and 05 remain HOLD |
| Independently settled orders | None authenticated for reporting | Net revenue per 1,000 qualified sessions NOT COMPUTABLE |

Connected Gmail searches for recent affirmative Inspire3 approval/email rights and the actual Final Vestige welcome returned **no matching evidence**. A mailbox non-hit is not proof that no agreement or received message exists elsewhere.

## Offer → funnel → blocker → change → evidence → owner

| Offer / step | Blocker | Proposed acceptance change | Evidence / status | Owner |
|---|---|---|---|---|
| Fieldbook: Grok → Focus → opt-in | Client gift state easy to mistake for confirmed signup | Separate UI attempt/download events from deduplicated private provider confirmation; retain honest free-gift UX | 27/27 native Node source reproduction; genuine subscriber proof **missing** | Claude / Focus |
| Dispatch: confirmed lead → eligible recipient | Mismatched aggregate and follower totals | Private recipient/suppression comparison, publish only aggregate eligible count | 3/3/2 versus 3 WP.com/0 direct email; **UNKNOWN distinct eligibility** | Focus / Founder |
| Six emails: drafts → compliant inbox | No non-sending native Jetpack witness, commercial sender address, operational unsubscribe | Use editor's **Preview email**, post send toggle OFF; verify visible subject, title, CTA, legal footer; no test email | **NOT TESTED**; official WordPress preview documentation | Dispatch / Founder |
| Zen12/Total Focus: guide → checkout | No named email permission, issued earning URL, approved live guide or exact referred checkout | Independently verify partner/product/email rights before considering offer placements | Both remain `HOLD_MERCHANT`; seller marketing is not evidence | Mind / Commerce |
| Paid affiliate conversion → net revenue | No authenticated paid order or qualified-human session denominator | Reconcile merchant settlement less refunds/fees and source-attributed qualified humans | **NOT COMPUTABLE**, no fake zero or conversion rate | Claude / Praxxis / #820 |

The six-issue pilot stays **4 editorial / 2 commercial review-pending**. All six `HOLD_UNSENT`, with 03/05 `HOLD_MERCHANT`, 04 `HOLD_COPY`; no replacement issue adopted. No emails, test emails, WordPress writes, subscriber contact, affiliate link activation, merge or spend.

## Sources

- Live authenticated WordPress pages: [Focus](https://finalvestige.com/focus/) ID 1579; [Dispatch](https://finalvestige.com/dispatch/) ID 523; [Editorial Standards](https://finalvestige.com/editorial-standards/) ID 17.
- [WordPress Preview email, reviewed November 9, 2026](https://wordpress.com/support/newsletter/email-appearance/); [Disable newsletter emails](https://wordpress.com/support/newsletter/disable-newsletter-emails/); [CAN-SPAM business compliance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business).
- [TASK-008 Google Drive](https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit) confirms Grok/Claude/Praxxis ownership boundaries. Public Inspire3 product advertising cannot authorize Final Vestige email promotions.

