# R320 — Focus gift visibility is NOT confirmed consent (NO SEND)
**2026-11-12 19:36 PT / 2026-11-13 03:38 UTC · isolated DRAFT review.**
Parents: R319 #2286 at acb80b485d7bc9429e215c0f7937845c2366a27a, canonical Issue #174, companion #171, master untouched #175, readiness #201. Frozen homepage #49 untouched.

## New source-of-truth finding, not a repetition of R319
The actual published WordPress **page 1579 /focus/** contains an initially \`hidden\` gift panel. Earlier text extraction exposed its text and could have implied that every visitor sees the PDF. **Correction:** the raw HTML hides it by default, but the published \`#fvf-gift-v2\` inline script reveals the gift when \`?subscribe=\` has *any* non-empty value other than five hardcoded failure words. That user-controlled URL parameter is neither proof of a Jetpack form submission nor proof of confirmed, eligible email consent. The script also reveals the gift if the Jetpack widget bears an \`is-subscriber\` class; that CSS class is not enough to certify delivery consent. A free PDF may deliberately be given after an attempt; the problem is using the visibility signal as an acquired lead or a reliable entitlement.

**Existing site evidence:** /dispatch/ and /focus/ are published, one Jetpack subscription list, no new platform. The Focus page also instructs users with PDF browser trouble to “sign up again,” which risks duplicate attempts and muddies attribution. The page's opt-in promise says mail will come when investigations publish, but automatic new-post sending remains OFF by founder design. Preserve that safety setting; request editorial consistency review instead of silently activating sends.

## Tests
- Original PR #175 HEAD d57ccd... all eight newsletter/manifest/test Git blob SHAs independently matched and its six native Python tests passed 6/6.
- This PR adds \`live_focus_gift_fixture.mjs\` copied from the current published WP inline script, a **Node VM offline reproduction** showing arbitrary \`?subscribe=foo\` reveals a hidden gift, and a pure non-deployable \`gift_review_contract.mjs\` plus adversarial native Node test cases.
- The pure evaluator **never** emits \`confirmed_signup\`, \`paid_order\`, \`send_authorized\` or raw subscriber identities. An \`adapter_attestation\` boolean is a synthetic interface input, **not authentication**; real Jetpack UI behavior and provider eligibility still require Claude's private read-only verification.
- No scripts deployed, no listener/analytics introduced, no CMS draft, no live A/B, no postal/unsubscribe claim, no emails/test sends.

## Founder and release decision
Retain 4 original editorial / 2 merchant-draft emails. All six HOLD_UNSENT, 03/05 HOLD_MERCHANT; optional creative not adopted. Account-specific Inspire3 affiliate acceptance, EMAIL-promotion permission, issued earning URLs, verified guide publication, actual checkout, legal publisher postal address, received Jetpack preview and actual welcome still unknown. Exact paid revenue and net revenue per 1,000 qualified-human sessions NOT COMPUTABLE.

**Sources:** https://finalvestige.com/focus/ ; https://finalvestige.com/dispatch/ ; https://finalvestige.com/editorial-standards/ ; https://wordpress.com/support/newsletter/email-appearance/ ; https://wordpress.com/support/newsletter/send-newsletter-emails/ ; https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174 .
