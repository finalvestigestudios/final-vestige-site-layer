# The Dispatch — Historical Mysteries, Collectors and Case Files

**Current release state (November 5, 2026): LIVE website offer pages, EIGHT WordPress newsletter drafts, NO EMAIL SENT OR SCHEDULED.**

This is the authoritative state of the founder-directed Mini Museum-first conversion campaign. Earlier six-email Mind & Perception concepts in PR #175 and previous revisions of this branch are retained only as version history, not the current send plan.

## First-party journey now live

- **Subscriber entry:** [Seven Day Focus Fieldbook](https://finalvestige.com/focus/) — native Jetpack opt-in and confirmation, verified by the founder with a received welcome email and the complete 52-page PDF.
- **Curated Collection:** https://finalvestige.com/collection/ — dedicated editorial feature cards for Mini Museum and Cold Case Inc, added as a separately reversible Gutenberg block. Main site navigation already labels this page **Editions**.
- **Primary physical-history offer:** https://finalvestige.com/mini-museum-history-collectibles/ (WordPress page **2088**, published). A source/collector-focused Mini Museum guide with two explicit affiliate disclosures, verified founder-supplied Awin banner creative, and transparent seller-claim/variation cautions. No invented testimonials, urgency or guaranteed resale value.
- **Secondary fictional detective offer:** https://finalvestige.com/cold-case-mystery-games/ (WordPress page **2089**, published). Offers a free short Flat 33 case, accurately distinguishes fictional crime entertainment from real documentary investigations, and includes the founder-supplied sponsored The Waters Edge creative with disclosure.
- **Contextual article bridges:** Crystal Skulls post **1926** → Mini Museum guide, Change Blindness post **1922** → Cold Case guide. These are compact editorial links, **not** abrupt checkout buttons inside sensitive investigations. Original content, related-reading, schema and FAQ blocks were preserved.

### Live content/source location

Exact WordPress Gutenberg blocks for the two presell pages and Collection/article bridges are in `site/`. Do not replay them without fresh WordPress optimistic locks or overwrite the current production content.

The exact Awin click/display creative parameters and original founder-supplied HTML appear in `offers/AWIN_CREATIVE_REGISTER.md`. **Affiliate program joined/active status, actual payout group and email-channel approval have not been verified through an Awin account connector.** An Awin creative's presence does not itself prove that transactions will be commissioned. Confirm these details with the founder in Awin before forecasting revenue or approving merchant-specific email sends.

## Eight-week warm-up and reveal sequence (all drafts)

| Week | WordPress draft | Subject | Reader value | Commercial handling |
| --- | ---: | --- | --- | --- |
| 1 | 2076 | The crystal skull that wasn't ancient | Provenance and documentary evidence | No offer |
| 2 | 2077 | The map that invited a thousand stories | Real 1513 chart, disciplined interpretation | No offer |
| 3 | 2078 | The Roman cup that changed its color | Material history and observation | No offer |
| 4 | 2079 | An accident with no conclusively identified first spark | Apollo 1 source-linked case and timeline | No offer |
| 5 | 2080 | Tarot was a game before it became a prophecy | History of symbols, provenance and objects; **teaser for physical artifacts** | No merchant named |
| 6 | 2081 | What if you could hold a piece of the past? | **Mini Museum collector evaluation**, documentation and buyer questions | First disclosed offer, FV first-party landing CTA |
| 7 | 2099 | One clue can change the entire case | Free evidence exercise and reader participation | No paid offer |
| 8 | 2100 | This time, the case is yours | **Cold Case Inc experience**, free case and paid choices | Disclosed secondary offer, FV first-party landing CTA |

The story arc is **mystery → observation → provenance → credible relationship → collector desire → offer → free challenge → secondary offer**. Each email delivers an independently worthwhile discovery; anticipation comes from truthful future topics rather than fake withheld information or pressure.

All eight WordPress posts are in category `The Dispatch`, **status=draft**. Their exact Gutenberg content is pinned in `issues/`. They have one primary linked CTA apiece, and the two commercial installments contain a visible near-CTA disclosure in addition to the disclosure on their destination pages. **No direct Awin or other merchant tracking links appear in the emails.**

## Native Jetpack delivery configuration

On November 5 the connected WordPress newsletter settings were read and changed:

- `email_content_format`: **excerpt → full** so readers can receive the complete editorial letter, not just a summary.
- `from_name`: **Final Vestige → Final Vestige Studios** for consistent sender identity.
- `email_new_posts_by_default`: **remains false**. No ordinary article publication automatically sends emails.
- `reply_to`: remains `no-reply`; `subscriptions`: remains enabled.
- Existing successful Fieldbook welcome content and consent mechanism remain intact.

**Important:** Jetpack native Newsletter is a post-triggered *broadcast* to the currently eligible list, NOT an 8-email subscriber-relative drip automation. The Fieldbook welcome email is separate. Do not claim new subscribers receive week 1 automatically; do not turn on send-by-default to simulate a sequence.

**Suggested cadence:** one weekly issue; exact first-send date/time subject to founder authorization. No send/schedule action was taken while preparing the campaign.

## Conversion architecture

1. Social/SEO historical intrigue brings visitors to source-rich Final Vestige investigations.
2. Fieldbook popup and sign-up capture **consenting/confirmed** subscribers without forcing a purchase.
3. Weeks 1–5 of Dispatch build trust and value; each provides one relevant first-party research CTA.
4. Week 6 introduces the Mini Museum collector guide as a conditional commercial recommendation with clear evidence/provenance considerations and a first-party Awin-tracked checkout bridge.
5. Week 7 returns to free reader participation to avoid back-to-back selling.
6. Week 8 introduces the optional Cold Case Inc review after real case-solving context, with free first case and no misleading claim that paid cases are free.
7. After these eight emails, return to the normal weekly research-led Dispatch; offer future collector products only where objectively relevant.

**Main KPI:** actually confirmed qualifying commissions and net revenue per 1,000 qualified visitors. Secondary: opt-in rate per relevant site entrance, confirmed/welcome-delivered subscribers, verified Dispatch recipient/delivery counts, first-party presell CTA clicks and actual affiliate orders. Do not interpret impressions, click counts or three-person sample rates as profitable conversion proof.

## Pre-send and ongoing safety/ethics gates

- Confirm advertiser `joined/active` status within Awin, qualifying commission rate, eligible website/email channels, allowed creative and tracking, and any exclusions. The user-supplied banners do **not** complete those checks.
- Verify any product-specific price, returns, shipping, authenticity and case-content notes directly on the merchant page before making claims; do not invent personal use, star ratings, endorsements or testimonials.
- Preview the actual native Jetpack full-email rendering in a real inbox (including one CTA, mobile accessibility, sender, consent and unsubscribe/footer). The founder already proved the **welcome** email; that does **not** verify a promotional **broadcast**.
- Confirm an appropriate physical postal address or other marketing compliance details where required; do not invent one or assume the WordPress default footer alone meets every commercial requirement.
- Ensure commercial recommendations include clear near-link plain-English disclosure. Preserve no affiliate tracking in the first five issues.
- Get explicit founder approval of the **actual recipient audience, exact issue, and send/schedule action** before sending. A request to prepare a campaign is not permission for an email blast.
- Preserve rollback for public pages and avoid changing homepage, WordPress theme, signup plugin, or protected research evidence without a separate justified release.

## Working files

- `manifest.json`: exact eight-issue post IDs, titles, status, CTA destinations and current setting snapshot.
- `issues/`: eight full source snapshots, all draft/unsent.
- `offers/AWIN_CREATIVE_REGISTER.md`: exact tracking creatives provided by the founder.
- `offers/landing-mini-museum.md`, `offers/landing-cold-case-inc.md`, `offers/email-mini-museum-conditional.md`: copy concepts, claim-review gates and pre-sell creative (some predate public page release).
- `COPY_STANDARD.md`: founder's sales-copy design and compliance standards, mapped to their supplied brand screenshots.
- `site/`: exact public Gutenberg release blocks for the pages and article/Collection integrations.

Historical research drafts and the first six-issue campaign source are preserved in earlier PRs/commits. This branch is the **current eight-week production-integration handoff**, not a second campaign to publish independently.
