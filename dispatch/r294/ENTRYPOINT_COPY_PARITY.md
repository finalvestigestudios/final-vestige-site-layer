# R294 — One Jetpack list, two different signup expectations

**Review-only. No publication, no settings change, no send.** Sources read authenticated 2026-11-12 02:34 UTC.

## New finding: a practical consent-expectation inconsistency

The published [Dispatch page](https://finalvestige.com/dispatch/) (WordPress ID 523) promises "New investigations and archive finds by email, when we publish them." The subscribe area promises the 52-page Fieldbook, privacy and unsubscribe. It does **not** mention that future issues may include commission-bearing recommendations.

The published [Focus page](https://finalvestige.com/focus/) (ID 1579) tells a prospect: "By subscribing you also join The Dispatch, our email of new investigations and archive finds, sent when we publish them. Some emails may include recommendations that earn us a commission. Unsubscribe anytime."

Both feed the **same Jetpack newsletter**. The disclosure is present on one entrypoint and absent from the other. This is an **editorial trust / informed-expectation gap**, *not* evidence of illegal mailing or of invalid existing consent. Do not retroactively presume /dispatch/ entrants consented to commercial email because /focus/ mentioned commissions.

## Proposed minimal change — NOT LIVE

Add one paragraph beside the existing Dispatch signup, retaining the historical editorial promise:

> The Dispatch brings you investigations, archival discoveries and practical evidence notes. Occasionally, an issue may include a clearly marked product recommendation; if a linked purchase earns us a commission, we'll say so beside that recommendation. You can unsubscribe anytime.

Keep the published Focus disclosure unchanged, and do not make a second list or mandatory affiliate pathway. Founder/Claude must approve any website copy changes separately. This does not substitute for a commercial email's disclosure beside its qualifying offer.

## Remaining actual launch blockers

- Merchant: Final Vestige-specific Inspire3 affiliate acceptance, **email channel** permission, issued earning URL and use of approved creative unverified. Public recruiting is insufficient. Mind Studio R307 guides in [PR #2129](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2129) remain unpublished. Commercial Issues **03 and 05 HOLD_MERCHANT**.
- Eligibility: Jetpack newsletter reports total=3, confirmed=3, unconfirmed=2. Independent follower stats reports WordPress.com=3, email=0. Different scopes, not additive. Actual consented email-eligible recipients **UNKNOWN**.
- Delivery: Welcome *configured* with 52-page PDF, **received** welcome unverified. Site send-capable but default new-post emails OFF and recent five posts explicitly opted out.
- Legal: valid **Final Vestige** physical postal address and functioning unsubscribe in an actual commercial email **unverified**. Automattic address on a subscription confirmation does not count as verified publisher address.
- Email rendering: native Jetpack Preview email is **not** demonstrated; separate actual preheader implementation is unverified. No test sends authorized. Source [WordPress Preview email](https://wordpress.com/support/newsletter/email-appearance/).
- Founder: no explicit final creative/audience/schedule approval. All six **HOLD_UNSENT**.

[FTC CAN-SPAM primary-purpose, address and opt-out rules](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business). [FV Editorial Standards](https://finalvestige.com/editorial-standards/): maintain documentary fact/inference distinction and disclose material financial relationships.

## Offer-specific verified seller scope (not proof of benefits)

- [Zen12 official About](https://zen12.com/about): twelve-minute listening routine, twelve levels/four versions, and marketing claims that it replaces an hour of conventional meditation; no independent validation of **this product** or exact hour-equivalence.
- [Hypnosis Live Total Focus](https://hypnosislive.com/mental-skills/total-focus): seller lists 33 minutes and 47 MB; concentration/brain-reprogramming promises are merchant marketing, not proven product results. Public pricing/refund conditions can change and are not approved partner email terms.
- Neither direct seller destination should appear as an active promotional CTA before authorization and published vetted warm-up guide.

**Risk priority:** The immediate blocker to paid conversion is not the lack of another email. It is insufficient permissions, recipient eligibility and a lawful verified path to a *settled purchase*.
