# R105 — real native Jetpack excerpt contract and compliance probe (UNSENT)

Owner: [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); merchant coordination [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171).
This is a **new isolated, additive evidence-only layer** stacked on R104 draft PR #879. Frozen original master #175 is pinned at `d57ccdba3aee8f065e143e101c2945f4f3d01647`; PR #178 descendants are known to have changed 7/7 issue+manifest blobs. No alternate creative selected.

## Verified 2026-11-04 03:34 UTC; read-only authenticated WordPress

- Enabled and site_can_send=true; **email_new_posts_by_default=false**, hence no new-post auto sends. The last five native delivery records are `never_sent_opted_out` with **null dispatched_at and null recipient/sent counts**. These are *not* six campaign sends.
- Actual native `email_content_format=excerpt`; `reply_to=no-reply`; `from_name=Final Vestige`; 52-page Focus Fieldbook welcome text configured, **actual welcome receipt not verified**.
- Newsletter total=2 / confirmed=2 / unconfirmed=2; separate Jetpack follower telemetry email=0 / WordPress.com=2 (partial=false). **Do not add counts or assert any eligible email recipient**; no PII exported.
- Public /dispatch/ (page 523) says investigations/archive finds + Fieldbook, but **does not explain prospective affiliate recommendations**. /focus/ (page 1579) does, using “Some emails may include recommendations that earn us a commission.” Original Editorial Standards (page 17) requires primary sources, uncertainty, independent findings and commercial disclosure. No live page changed.

## NEW evidence: simulation of frozen original issue *body* under first-55-word default

Read exact frozen issue Markdown blobs at #175 and extract the first 55 words of **editorial body text after its internal status/header separators**, removing Markdown marks. For all six, the first 55 words contain neither the primary article/guide CTA nor the later legal footer; Issues 03/05 also omit their near-offer `Commercial disclosure:` text. This is a **local conservative content simulation**, not a claim about the precise rendered WordPress email: Gutenberg/HTML rendering, custom excerpt, HTML truncation and default read-more link may differ. Nevertheless it proves the master manuscript does **not** become a full email in current native excerpt mode.

### Consequence for campaign strategy

The existing campaign emails are *full manuscript drafts*, whereas Jetpack currently sends a post **excerpt** plus a link. The proposed custom excerpts in `transport_contract.json` are narrow, 28–55-word **EDITORIAL OPTIONS**. They do not create a real WordPress post, do not convey a fully rendered offer CTA, and do not supply a legally compliant footer. Because native preheader configuration was not verified, preserve the original proposed preheaders as creative metadata only—not a promised inbox display.

**Recommended delivery decision (awaiting explicit founder approval):** Keep Jetpack defaults OFF, preserve the current list, and retain excerpt mode for a *web-first* journey after a proper native email proof: honest subject → custom excerpt/context → explicit on-site evidence-based article → approved guide only if active. However, **all six issue manuscripts would need matching approved on-site article destinations and current consent messaging**; the two product guides are not live. If the founder instead wants the *entire six-issue text in email*, that requires separate reviewed full-content settings behavior and a real received email proof; no settings or publishing changes are authorized here.

## Commercial and consent gates

1. Named, written Final Vestige Inspire3 affiliate acceptance; Zen12/Total Focus **email promotion** approval; authorized creative and tracking URL per exact product. Generic seller newsletter promotions and a public affiliate application page **are not approval evidence**. Targeted Gmail search through Nov 3 found no qualifying written approval; this is absence of evidence, not proof no approval could exist elsewhere.
2. Two independently vetted LIVE warm-up guides must exist before commercial edition CTAs change from placeholders; Mind #171 owns those guides. Seller claims such as Zen12 “12 minutes equal one hour” and Total Focus productivity promises are **not established** product-specific efficacy facts. Pricing, refunds and audio terms require fresh checkout-level confirmation; neither seller links nor amounts inserted.
3. Obtain a legitimate **Final Vestige postal mailing address**, not an Automattic address copied from the Oct 25 *subscription confirmation* email. Independently inspect the actual final received HTML/plaintext commercial sample and confirm unsubscribe link actually works without exposing addresses; no sample send authorized. Verify Jetpack renderer's behavior with a founder-authorized test only after separate permission.
4. Resolve private opt-in audience status using site-owner WordPress Subscribers UI or platform support; group-level numbers cannot establish email eligibility, and the connector does not expose a safe read-only per-subscriber eligibility inventory.
5. Final founder approval must identify exact six manuscript blobs/commit, revised consent language, transport mode, web pages, audience, timing and each approved commercial offer. **No emails, test sends, scheduling, posts, subscriber changes, settings writes, or affiliate activation in this PR.**

## Operational QA artifacts and no false claims

- `transport_contract.json` pins original subject/preheader, six proposed custom excerpts, 4:2 mix and actual contradictory diagnostics. Every release and merchant flag is closed; count `eligible_recipients=null`.
- `reviewer_board.html` is accessible offline HTML, with no scripts/pixels/forms/merchant links. It visually previews **candidate** excerpts only—not actual Jetpack inbox/MIME.
- `audit_transport.py` and `tests/test_transport.py` implement a fail-closed, offline guard: run `python -m unittest discover -s dispatch/campaign-2026-mind/r105-jetpack-excerpt-contract/tests -v` and `python dispatch/campaign-2026-mind/r105-jetpack-excerpt-contract/audit_transport.py`. Source content exact-byte verification remains R104's separate ledger.
- Simulated view/click/opt-in metrics: **none**. No A/B statistics with a tiny ambiguous list.

## Official dated documentation and sources

- WordPress Newsletter Settings (last reviewed **2026-10-26**): https://wordpress.com/support/newsletter-settings/ — excerpt vs full, first 55 words if no custom excerpt, only sender display name editable, confirmation vs welcome flow.
- WordPress email appearance: https://wordpress.com/support/newsletter/email-appearance/ — custom excerpt introduction and truncated text.
- WordPress Disable Newsletter Emails (reviewed **2026-10-06**): https://wordpress.com/support/newsletter/disable-newsletter-emails/ — per-post send opt-in.
- FTC CAN-SPAM primary-purpose and sender obligations: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- FTC affiliate disclosure: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- Product-specific seller landing pages (descriptions are *not* independent efficacy evidence): https://zen12.com/getstarted/ ; https://hypnosislive.com/mental-skills/total-focus
- Existing standards: https://finalvestige.com/editorial-standards/

**End state: ALL SIX HOLD_UNSENT; 03/05 extra HOLD_MERCHANT.** Homepage flagship/frozen #49 untouched. No live changes or emails.
