# Campaign QA / release-gate report — 2026-10-30

## Verified live WordPress / Jetpack
- `finalvestige.com`, blog ID 256784396; newsletter `subscriptions=true`, `site_can_send=true`, `recent_sends=[]`, `email_new_posts_by_default=false`.
- Welcome email currently links to 52-page Focus Fieldbook; `/dispatch/` page ID 523 and `/focus/` page ID 1579 are published. Leave all unchanged.
- **Subscriber API inconsistency** repeated at 2026-10-30T18:36:43Z: `total=2`, `confirmed=2`, `unconfirmed=2`, `imported_last_24h=2`. These statuses cannot be interpreted as a reconciled list. The tool does not provide subscriber identities or a distinct-recipient export; do not estimate delivery count or infer 4 recipients.
- The WordPress content connector offers content CRUD but is not a real inbox test-email rendering or a mailbox. WordPress support documents a *separate editor test-email preview flow*; a standalone HTML snapshot here **does not certify the WordPress-wrapped email**.

## Immediate blockers (ordered)
1. **Audience consent and counter reconciliation** — inspect WordPress Jetpack Newsletter > Subscribers with proper authorized account, confirm deliverable/confirmed, deduplicated recipients, and whether two unconfirmed are overlapping counts. No emails imported or sent during this QA.
2. **Actual merchant authorization** — Final Vestige's Inspire3 approval, per-brand/product availability, exact tracking URL, and **email marketing permission** cannot be established from public partner catalog. Approval remains required; no affiliate links added.
3. **Commercial email compliance** — verify rendered sender headers; include valid business postal address (do **not** borrow Inspire3 London address), working unsubscribe and reply/opt-out route. The two commercial offers must be visibly labelled and independently disclosed.
4. **Real WordPress test preview** — create a **private/unpublished test-only** draft with both CTA configurations after founder has authorized test-email recipients; use the WordPress editor's **Send test email** option to a founder-controlled address, without publishing or sending to subscribers. Confirm received inbox/mobile rendering, subject/preheader behavior, footer and unsubscribe destination in actual received MIME. Test sends are not authorized in this run.
5. **Editorial** — verify each factual statement, links, subject, disclosure, source credit and scope against site's Editorial Standards and the product audit. No false implied product testing.
6. **Founder send approval** — explicit final content/audience/date consent after all other gates. Do not schedule or publish early.

## Findings from first independent quality pass
- Historical **1785** opener in edition 02 was less precise; corrected to **1784** using Adam Crabtree's [2019 peer-reviewed history](https://pubmed.ncbi.nlm.nih.gov/31273811/) and the scholarly translation listing.
- Apollo issue previously advertised **“Fourteen seconds”** in its subject; NASA describes ~**17 seconds** from first crew indication of fire to end of communication. Corrected subject, inserted [NASA Review Board findings](https://www.nasa.gov/wp-content/uploads/static/history/Apollo204/find.html) and [NASA's safety investigation summary](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1).
- Zen12 offer now identifies the specific vendor program format and sound styles and explicitly distinguishes *seller claims* from broader meditation evidence (NIH/NCCIH).
- Hypnosis Live offer now identifies typical audio format, current merchant-specific refund restrictions and limits, but no guaranteed behavior or health result, and links to NIH/NCCIH.
- Templates deliberately omit images, pixels, scripts, autoplay video, remote fonts and live merchant links. Display-only previews are **not deployment-ready**.

## Rendering and instrumentation policy
- Offline snapshot previews: branded table-based responsive HTML, plain text, no remote assets. No tracking pixels. Product CTA remains a visible **non-clickable HOLD** token. Preview index must carry an explicit unsent banner.
- Real WordPress's `email_content_format=excerpt` is a **potential campaign blocker**: publishing rich posts may only send their excerpts, not the full 200–300-word newsletter stories. Must inspect real editor preview before considering any launch; do not change setting without founder approval.
- Analytics: count actual *delivered* via WordPress, named-edition website sessions where measurable; outbound FV-to-merchant clicks only when implemented under privacy policy; vendor-confirmed purchases only when reports exist. With ~2 total subscribers, do **not** run meaningless confidence-interval A/B tests.
- No new paid tooling, WordPress edits, subscriber records, publishing, scheduling or account changes.

## Brand source
- https://finalvestige.com/editorial-standards/
- https://finalvestige.com/affiliate-disclosure/
- https://wordpress.com/support/newsletter/
- https://wordpress.com/support/newsletter/disable-newsletter-emails/
- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
