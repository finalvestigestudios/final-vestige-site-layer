# R94 — Exact WordPress editor handoff, no sending

**Status: ALL SIX HOLD_UNSENT; issues 03 and 05 additionally HOLD_MERCHANT.**
This is a read-only build plan, **not** a WordPress REST request, posted draft, email, verified Jetpack email preview, or authority to send. Source project: [canonical six original issues #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) at `d57ccdba3aee8f065e143e101c2945f4f3d01647`. Builds on [per-edition guard #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), [R92 excerpt candidates #796](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/796), [R93 evidence escalation #804](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/804), issue [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), and Mind / Affiliate issue [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). No original content has been rewritten. The alternate subjects/excerpts are unapproved editorial proposals.

## What this closes that previous offline previews did not

The original 6 full Markdown manuscripts are *not* the body subscribers will automatically get with current site setting `email_content_format=excerpt`. Official WordPress documentation indicates the **WordPress post title** is the email title/subject and a **per-post manual excerpt** can supply the email introduction. The native read-more CTA points at the **eventual published WordPress post**, not the existing deep-dive URL in a campaign manifest. Furthermore, the intended custom **preheader is not a confirmed Jetpack-supported editor field**. Our original full newsletter HTML is an offline copy review surface, not a genuine inbox representation.

Previous R92 drafted six safe alternatives, but did not turn the source-of-truth relationship into one conservative, source-derived *field-by-field operator handoff*. This R94 tool reads R92 and original #175; it stops when either source or WordPress assumptions drift. It never copies original `[[VALID_POSTAL_ADDRESS_REQUIRED]]` / `[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]` placeholders into a post or email and never generates a directly POST-able WordPress API payload. It flags original vs proposed subject changes, leaves sender/test/live authorization false, and sets commercial guide and merchant link slots inactive.

**Run locally from repo root:** `python -I dispatch/campaign-2026-mind/r94-native-editor-handoff/editor_map.py`. For the six human editor cards as JSON **to stdout only**, add `--json`. **Test:** `python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_r94_native_editor_handoff.py' -v`. The integration test reads the exact existing master manifest and candidate JSON at current branch head. No external libraries or credentials are required.

## Separate surfaces and their real constraints

| Surface | What editor can actually control | Required proof / approval |
|---|---|---|
| Site authoring source | Source manuscript and article body, with source citations | Research and conversion QA; keep original manifesto, founder approval for any replacement |
| WordPress post title | Native subject text; alternative R92 subject != original title | Founder must approve *which* title; ensure it describes rendered excerpt |
| WordPress post excerpt | Candidate manually written intro, not automatic fallback | In native preview, check exact text and disclosures; no assumptions about truncation |
| Intended preheader | A proposed review note, **not a verified independent Jetpack field** | Verify actual supported template / MIME, otherwise omit preheader promise |
| Native email CTA | WordPress *Read more* to that **post's eventual permalink** | A future published post must host meaningful full research and only then link to cited sources or approved guides |
| Commercial guide CTA | On-site guide, not a direct checkout in inbox | Guide approved, live and tested; final near-link disclosure in the guide; merchant permission for email confirmed separately |
| Email footer | WordPress delivery footer, dynamic unsubscribe | Qualified FV publisher postal address + tested unsub in a real received commercial message |
| Audience | WordPress subscriber eligibility | Privately reconcile two confirmed + two unconfirmed from total two vs separate 0 email / 2 Reader followers |
| Sending | Explicit per-post newsletter toggle and publication | ***NOT AUTHORIZED***. Current new-post default OFF is not a sitewide physical send lock |

**Operational choice:** Preserve the existing Jetpack excerpt mode and the existing list for now. Do not change settings or create CMS drafts in this workflow. If full-text email is later preferred, that is a *separate global-setting decision with genuine before/after rendering tests* and final founder approval. No alternative paid platform or list is proposed.

## The six human-only handoff cards

Use `editor_map.py --json` to get six individually attributed proposals. The source manuscript path is a reference and includes intentional legal placeholders; **do not paste it blindly into the CMS**. Editorial issues 01/02/04/06 can ultimately point inside their future on-site post to a verified first-party research URL. The *email's one reliable CTA in excerpt mode* is its generated Read-more destination. Issues 03/05 have **no live approved product-guide CTA**. The R92 introductions put the commercial disclosure at the beginning specifically to withstand excerpt-mode conditions; disclosure must also appear immediately adjacent to an eventual qualified recommendation in the guide. Do not use an unapproved alternate subject or preheader as if founder signed off.

## Verified observations — November 3, 2026, 16:34 UTC

Authenticated WordPress source: newsletter `subscriptions=true`, `site_can_send=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, `reply_to=no-reply`, `from_name=Final Vestige`; five most recent posts each `never_sent_opted_out`; configured welcome points to 52-page Fieldbook (**delivery unknown**). Newsletter diagnostic `total=2, confirmed=2, unconfirmed=2`; separate complete Stats report `email=0, wpcom=2`. These are not additive and cannot establish a recipient denominator. /dispatch/ page ID 523 and /focus/ page ID 1579 are published with an existing Jetpack signup, but the former does not disclose potential future commission earning and the latter does. Editorial Standards ID 17 requires source provenance, uncertainty and commercial independence. Neither signup page was changed.

[WordPress.com native appearance guide, reviewed 2026-10-06](https://wordpress.com/support/newsletter/email-appearance/) documents that a **per-post Send-to-subscribers toggle** is required for its Preview email and Send test email UI, and native post notification From address is `donotreply@wordpress.com`. These controls remain strictly **unoperated**. [Jetpack customizing guide, updated 2026-10-28](https://jetpack.com/support/newsletter/customize-the-newsletter-experience/) says an empty excerpt falls back to 350 characters; [WordPress.com newsletter settings](https://wordpress.com/support/newsletter-settings/) says 55 words. A site-specific received test, not either online article, must resolve actual behavior. **No receiving inbox/MIME test exists and no test email is authorized.**

## Real dependencies, not editorial filler

- Product-specific merchant account acceptance, permission for *email* promotions, approved earning URL/tracking and creatives, privacy/data-sharing restrictions, checkout/refund terms, and correct product claims **unverified**. Official sellers: [Zen12](https://zen12.com/hnp), [Hypnosis Live Total Focus](https://hypnosislive.com/mental-skills/total-focus). Their efficacy promises are *seller assertions*. No hard-coded price, guarantee, discount, or customer quote.
- Mind Studio's [draft Zen12 guide #806](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/806) is **not** a published vetted buyer guide. A Total Focus approved live destination is likewise unverified.
- For applicable commercial messages, [FTC CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires accurate sender/subject, publisher postal address and opt-out. Editorial vs commercial labels alone do not settle the message's legal primary purpose. We require a visible footer and robust unsubscribe proof across the pilot rather than gamble on labels.
- No synthetic scorecard proves deliverability, welcome delivery, subscriber intent, clicks, sales or conversion. No statistical A/B outcome is supportable with the known tiny/inconsistent count.

## Release operation: founder's final gate, not agent's

After private eligible-audience reconciliation, verified publisher mailing address and merchant permissions, independently approve the exact on-site final content and subject/excerpt; separately authorize a *safe* native preview/received test and examine actual text and HTML, footer, unsubscribe behavior and email CTA; approve the final six assets, timing, target audience and sending in a distinct final instruction. Before that, **ALL HOLD**. Frozen flagship homepage PR #49 and all WordPress content, mailing list and Jetpack settings remain untouched.
