# R34 — authenticated editorial destination release audit (DRAFT, NO SEND)

Owner: [Dispatch Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Product guide, claims and commercial authorization owner: [Mind & Affiliate Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Original six drafts: PR #175; individual release gates: PR #201. Stacked on draft PR #390 exact parent e4b9be9961a4d7802ff195faf3245cd26347dfed. Homepage PR #49 untouched.

## Material new result: four live editorial CTA records independently authenticated

At 2026-11-01 03:32–03:33 UTC, authenticated WordPress.com site 256784396, pages.list/posts.list with exact slugs and publish status, confirmed:

| Newsletter | Published editorial destination | WordPress record |
| --- | --- | --- |
| #01 Perception | https://finalvestige.com/the-missing-caption/ | page 1122 |
| #02 Puységur | https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ | page 1377 |
| #04 Apollo 1 | https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ | post 434 |
| #06 Evidence Log / Fieldbook | https://finalvestige.com/focus/ | page 1579 |

All four URL strings match the current manifest exactly. This updates the operational evidence after the dated R31 audit left live destination verification open. It proves WordPress returned a published record for each link at that time, NOT that a reader receives or clicks the planned CTA in Jetpack mail, nor future availability. The R31 older historical ledger remains untouched to preserve chronology.

Exact-slug lookup for proposed commercial guides zen12-guide and hypnosis-live-guide returned NO pages in published/draft status, and /mind/ was not found by exact slug. Those are limited exact-slug results; an alternative slug might exist. Neither guide is currently an authenticated approved live CTA. Mind Studio PR #393 remains draft. Two commercial placeholders and all email release holds stay intact.

## Subscriber and email source of truth, with correct limits

At 2026-11-01 03:32 UTC, connected newsletter.status reported total 2 / confirmed 2 / unconfirmed 2 / suppressed 0 / paid 0. These are NONADDITIVE, not four unique subscribers. Actual permissioned eligible unique audience UNKNOWN; no identities queried, exported, transmitted or stored. Jetpack newsletter remains on, site_can_send true, new-post automatic emails OFF, global body mode EXCERPT, zero recent sends, sender Final Vestige and reply-to no-reply. Welcome template contains the 52-page Focus Fieldbook URL but actual receipt remains UNVERIFIED. Connected Gmail searches found an October 25 subscription confirmation, not a final welcome or Final Vestige-specific merchant authorization.

Published /dispatch/ (page 523) API-rendered content includes a Jetpack subscriptions block but shows a Subscribe anchor to its own URL instead of a static email input. This DOES NOT prove the interactive browser form is broken: Jetpack may enhance it client-side, or its API output may vary by viewer state. WordPress screenshot service returned status READY and capture_shows SITE at 1200px for /dispatch/ and /focus/. This was not an interactive form or a genuine email-preview test; future browser QA is required. Do not edit site or form without authorization.

The site's published Editorial Standards (page 17) require primary-record checking, uncertainty on unresolved evidence, AI-source caution and financial relationship disclosure. All pages unchanged.

## Offer-specific truthful email review (commercial remains blocked)

Official seller pages: [Zen12 about](https://zen12.com/about) and [Hypnosis Live Total Focus](https://hypnosislive.com/mental-skills/total-focus). The seller advertises Zen12 product packages and fast meditation claims; these are commercial representations rather than demonstrated equivalence. The Total Focus listing displays a 33-minute / 47 MB file and promises dramatic attention effects. Its displayed pricing, bundles and refund language can change. No statement in either listing establishes Final Vestige affiliate acceptance, product-specific newsletter/email permission, approved affiliate link format, creative usage rights or accurate checkout terms. Public [affiliate signup](https://affiliates.inspire3.com/) is not proof of acceptance; [email swipe creative for Limitless Labs](https://inspire3.com/ll/) belongs to a DIFFERENT offer and provides no Zen12/Total Focus permission. Do not reuse testimonial or performance claim as independently verified result.

Official [Jetpack Newsletter documentation, last updated October 28, 2026](https://jetpack.com/support/newsletter/) distinguishes editor PREVIEW from a real SEND TEST EMAIL. With global excerpt delivery, the full manuscripts cannot be assumed to reach inboxes. No editor preview, new draft WordPress post or test message authorized here.

[FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires truthful header and subject, nondeceptive commercial identification, a valid sender physical postal address and effective opt-out for covered commercial email. As of guidance reviewed October 31, opt-out mechanism must continue processing for at least 30 days after sending and honor requests within 10 business days; do not confuse CAN-SPAM's opt-out standard with RFC8058 one-click header mechanics. Seller or Automattic address cannot be substituted for Final Vestige's legitimate business address. Commission relationship requires clear proximate disclosure under [FTC endorsement guidance](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking). Genuine native mail footer and opt-out operation remain unverified.

## New executable safety verification

The R34 audit compares a dated, zero-PII authenticated WordPress source snapshot with the six canonical GitHub manifest issues. It tests exact editorial URLs, published WordPress IDs, the original 4:2 plan, the absence of active commercial destinations, nonadditive subscriber counts, no confirmed welcome, OFF auto-email and hard release holds. The companion Python suite deliberately mutates these properties to ensure failure, including spoofed domains, fake merchant permission, a forged delivered welcome and private recipient/token fields.

Run from a full checkout:
- python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v
- python dispatch/campaign-2026-mind/r34-live-cta-evidence/audit_live_route_evidence.py

The standalone audit intentionally prints HOLD and exits 2, even when its source checks succeed. Tests validate the consistency of a *dated API observation*, not an independently live authenticated re-query, delivered email, functional unsubscribe or lawful commerce certification.

## Next legitimate release gate (founder authorization still absent)

1. Explicitly authorize ONE unpublished WordPress editorial post editor PREVIEW with the exact reviewed creative and safe audience switch. Even post creation is a CMS write; no such write has been performed.
2. Separately authorize a one-recipient controlled test SEND, then capture the real received MIME/HTML/plaintext privately and test with PR #390's offline parser. No email/test email or recipient contact is permitted now.
3. Privately confirm eligible subscriber cohort and a valid Final Vestige commercial mailing address; verify actual footer, functioning unsubscribe and inbox appearance. Do not put personal data, address strings or tokenized opt-outs in GitHub.
4. Mind Studio supplies reviewed, approved, published Zen12/Total Focus buyer guides plus written merchant-specific permission for EMAIL marketing, eligible package links, current checkout/refunds and allowed creatives.
5. Founder explicitly approves final email subjects, full content, audience and send dates. The four editorial / two optional commercial allocation remains a DRAFT, never an approved scheduled sending plan.

**Current:** all six HOLD_UNSENT; #03/#05 HOLD_MERCHANT. No send/test-send, post creation/publication, schedule, WordPress settings changes, merchant/subscriber contact, affiliate activation, list creation, platform expense, homepage/PR #49 edit or PR merge.
