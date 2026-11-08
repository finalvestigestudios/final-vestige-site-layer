# Final Vestige Dispatch — edition-specific readiness and fallback sprint

**STATUS: DRAFT/HOLD. NO NEWSLETTER SEND, TEST SEND, NEW POST, SETTINGS CHANGE, LIST IMPORT, PAID PLATFORM, TRACKER OR PRODUCT LINK ACTIVATION.** 2026-10-30, companion Issues [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Designed to stack above original newsletter PRs **#175 → #178 → #187 → #194** without touching frozen homepage PR #49.

## The real weakness this fixes

The existing campaign-wide gate (`delivery/release_attestations.json` / `tools/release_gate.py`) correctly fails closed if Inspire3 approval is unknown, but it combines **all** six issues. That inadvertently prevents even historical **editorial-only** issues 1, 2, 4 and 6 from being considered for *independent review* when product-specific approvals remain blocked for 3 and 5. The new read-only `per_issue_preflight.py` separates edition evidence from the shared audience/delivery/compliance gates. It is **not** a replacement for the original global gate and cannot authorize or perform a send.

The legacy **4 editorial + 2 commercial-review-pending** mix remains the approved *draft* campaign. The new alternative editions in `contingency/` are simply optional no-offer copies. They would change the approved ratio and require **fresh founder approval** before substituting for commercial editions; they are never silently switched.

## What was actually verified on October 30, 2026 (21:30 UTC)

WordPress.com site 256784396: `subscriptions=true`, `site_can_send=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, zero recent sends, existing welcome copy pointing to the 52-page Focus Fieldbook. Subscriber counters still self-conflict `total=2 / confirmed=2 / unconfirmed=2`; this does **not** prove an exact eligible audience. No subscriber identities or private account details are present here.

Live editorial destinations verified read-only through the WordPress connector: Puységur resource page **1377**, Apollo 1 investigation post **434**, Focus Fieldbook page **1579**; `/dispatch/` page **523** remains published. The proposed `/mind/zen12-guide/` (Mind draft PR #180) and `/mind/hypnosis-live-guide/` (Mind draft PR #188) are **not verified live** and must not be inserted into a newsletter as active links.

A real WordPress **subscription confirmation** email dated October 25 was located in the connected inbox during read-only QA. That demonstrates only a specific confirmation email's presence. It does **not** verify the updated 52-page welcome's actual delivery, a newsletter edition's complete rendering, the subscriber's confirmation action, the mailing list's deduplicated total, or legal compliance for a commercial Dispatch. The confirmation email footer identifies **Automattic**, which is **not** a substitute for Final Vestige's own valid business mailing address in any qualifying commercial message. No private mail contents or tokenized links are stored here.

### Official platform/compliance facts

- WordPress post **title** supplies newsletter email subject. We have not verified that the manifest's separate `preheader` appears in the delivered email; do not advertise that as a supported control. The site currently emails **excerpts**; absent a custom excerpt WordPress says it sends the opening ~55 words. A custom excerpt can be configured per post. WordPress's full-text setting affects the **whole site**, and must not be changed without explicit approval. Sources: https://wordpress.com/support/newsletter/send-newsletter-emails/ , https://wordpress.com/support/newsletter/email-appearance/ , https://wordpress.com/support/newsletter-settings/ .
- WordPress says preview and send-test controls are in the editor while the per-post email toggle is on. That is not an authorization to create drafts or send tests; no actual Jetpack preview or delivered campaign message occurred in this sprint.
- FTC CAN-SPAM requires accurate headers, honest subject, appropriate ad identification, valid business postal address, functioning opt-out, prompt honoring of opt-outs and compliance even when an external email vendor sends on your behalf. It may cover promotional content for a commercial website, not only overt product ads. **Require valid postal/opt-out review for all editions as conservative practice.** Source: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .
- Product-specific Inspire3 approval, allowed email channel, actual earning link, product terms and accurate claim boundaries remain unverified. Public merchant recruiting pages or received consumer offers are **not partner approval**. Actual official product pages: https://zen12.com/ and https://hypnosislive.com/mental-skills/total-focus , https://hypnosislive.com/faq . Original source-first analysis: https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety and https://www.nccih.nih.gov/health/hypnosis .

## New audited release path

`per_issue_preflight.py` demands eight **shared** evidence proofs for the actual audience, WordPress mode and received email, sender/post switch, valid Final Vestige postal footer, unsubscribe and founder audience/date signoff. Every issue independently needs source/CTA/mobile QA. Issues 03 and 05 additionally need six merchant/product proofs **plus replacing the deliberately blocked guide token after approved publication**. A bare boolean cannot be used to satisfy a check: it also requires an opaque internal evidence reference and reviewer role. Never put subscriber names, emails, street addresses, private links or affiliate credentials into this source file. This is bookkeeping, not cryptographic provenance or legal certification.

Even when all proofs are true for an **editorial** edition, the strongest output is `HUMAN_REVIEW_CANDIDATE_ONLY`. Every result explicitly says `send_authorized: false` and no email action exists. Commercial editions with placeholder CTAs remain blocked even if every boolean is set true. Product-specific gaps cannot be bypassed with shared founder approval. None of this changes the existing release contract or site.

Read-only commands on a checked-out *stacked source branch*:

```sh
python -I -m unittest discover -s dispatch/campaign-2026-mind/readiness/tests -v
python -I dispatch/campaign-2026-mind/readiness/per_issue_preflight.py
python -I dispatch/campaign-2026-mind/readiness/build_review_board.py
```

The generated `review_board.html` is a **static offline design proof**, not a WordPress editor preview or email MIME. No scripts, external assets, tracking or earning links. It gives the founder a legible six-edition status review before any actual mailing. Source tests are on fixture snapshots; exact current GitHub head checks and real mail-client QA remain distinct gates.

## Immediate decision sequence (not executed)

1. Fix the list-count inconsistency privately in WordPress's Subscribers screen; preserve confirmed opt-in and never export personal contact data to GitHub.
2. Obtain a valid Final Vestige mailing address, use an authorized non-subscriber test recipient, and check actual received Jetpack headers/footer/unsubscribe and full vs excerpt mode **only after separate explicit founder approval**. The WordPress-confirmation email in Gmail is insufficient.
3. Make four editorial editions eligible for independent founder approval even while product approvals remain blocked. Never auto-schedule weekly sends.
4. When the two actual Mind guides are reviewed and published, confirm exact current merchant terms and private Inspire3 partner-account email promotion permissions before ever enabling a commercial edition.
5. Check actual subscribers' expectation: `/dispatch/` promises historical archive finds when published, not an unsolicited weekly product sequence. Any recurring cadence announcement requires transparent copy and founder approval.

**Measurement:** No sales/opens/CTR assumed. If Jetpack reports legitimate aggregate delivered/clicked counts, distinguish delivered messages from unique clickers, and buyer conversions only from approved merchant reporting. With 0 verified campaigns and ambiguous 2-subscriber count, there is no A/B significance claim.
