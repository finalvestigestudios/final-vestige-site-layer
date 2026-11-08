# Dispatch R13 — subscription entrypoint, exact-SKU copy and proof review

**Decision: HOLD_UNSENT.** Evidence captured Friday 2026-10-30 23:31 PT (2026-10-31 06:31 UTC). This is an independently scoped, read-only engineering/editorial package stacked on [R12 PR #253](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/253), whose base traces to original [campaign PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) / [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Product owner [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). No replacement of a founder-approved issue, published WordPress content, homepage #49, mailing list, settings, affiliate URL, or live signup.

## Executive judgment — **the acquisition funnel itself deserves proof**

The prior R12 review correctly prioritized actual delivered email and merchant rights. An independent authenticated check now surfaces a potentially earlier funnel concern: **WordPress MCP's rendered content for both published signup entrypoints contains a Subscribe anchor pointing to that same page, and *no* HTML `<form>` or email `<input>` elements.**

- Published [The Dispatch](https://finalvestige.com/dispatch/) = WordPress page **523**. The returned Jetpack Subscribe block contains a button-looking `<a href="https://finalvestige.com/?post_type=page&#038;p=523">Subscribe</a>`. After removing inline CSS/scripts, REST-rendered body has **0 form tags and 0 email inputs**.
- Published [Focus Fieldbook](https://finalvestige.com/focus/) = page **1579**. The returned Jetpack Subscribe block contains `<a href="https://finalvestige.com/?post_type=page&#038;p=1579">Send me the fieldbook</a>`, again **0 form tags and 0 email inputs** in API content.
**Additional native editor-context confirmation (read-only):** Both pages preserve an explicit `<!-- wp:jetpack/subscriptions {...} /-->` Gutenberg block. /dispatch/ saves `submitButtonText="Subscribe"` and `buttonOnNewLine=true`; /focus/ saves `submitButtonText="Send me the fieldbook"`, `subscribePlaceholder="Your email address"`, and `buttonOnNewLine=true`. Neither saved block declares an explicit button-only style in the inspected attribute string. [WordPress's October 5, 2026 Subscribe Block documentation](https://wordpress.com/support/wordpress-editor/blocks/subscribe-block/) says the standard form exposes an email field, whereas a configured **button-only style** opens a subscription popup. A `buttonOnNewLine` setting is only a layout option, not proof of the button-only style. Therefore the REST self-link representation merits a real logged-out clickthrough check, but the presence or absence of visible fields in the REST API alone remains inconclusive.

- **This is NOT proof the public signup is broken.** WordPress may intentionally render a linked subscription flow, inject interactive UI in a real browser, or use a hosted page on click. The WordPress API response is not a real browser DOM or a completed opt-in. Do not publish a "site broken" claim or make a live edit from this observation. It is a new **browser acceptance-test priority** because we are pursuing subscribers via these exact two CTAs.

A meaningful browser proof means: logged-out / incognito mobile and desktop view; visible email form **or intentional WordPress-hosted opt-in destination after clicking**; working keyboard and screen-reader label; no silent dead-end loop back to the same page; privacy/consent language present before submission; and screenshots of the state **without entering any real address or submitting**. Proof of actual welcome delivery requires a *separately founder-authorized opt-in*, not just screenshots. Public-facing HTML may vary by logged-in state, region, device, and Jetpack runtime.

## Merchant copy gap — original issue 05 is not sufficiently durable

The existing original draft `issues/05-before-you-press-play.md` still contains an exact numerical refund-policy statement: "within 14 days" and "five sessions per year." It also references the full Hypnosis Live catalog (more than 200 products) and the typical roughly 40-minute recording. The commercial opportunity under review is **one specific SKU: Total Focus**, whose current official sales page lists **33 minutes and 47 MB**. Treat catalog-wide averages and refund numbers as an editorial drift risk; the seller can change refund policy and checkout terms before our weekly issue is actually mailed.

**Proposed surgical change — founder/editorial approval required; NOT applied here:**

- Replace the old paragraph's numerical terms with: *"If an audio isn't useful for you, the purchase terms matter. Check the merchant's current checkout screen, refund policy, access format and any exclusions yourself before paying. Those terms can change; an older email is not a reliable guarantee."*
- Replace the vague catalog lead with: *"One recording under review is Hypnosis Live's Total Focus. The current product listing describes a 33-minute, 47 MB audio download and offers an audio preview. That tells us the file format and the advertised subject, not whether it will improve a particular person's concentration. We have not independently tested the recording or substantiated its specific outcome claims."*
- Maintain a single **inactive, first-party evaluation-guide** CTA, not a merchant link; retain the adjacent conditional commission disclosure. If the guide does not exist when permission is finally verified, **hold issue 05** rather than substitute a home page or the merchant checkout.
- Never insert the seller's current "$2", "$29.95", "93% off", countdown, money-back guarantee, "limitless powers", guaranteed focus, NLP/brain reprogramming claims, or a fake user experience. The same page currently has volatile price components; a quoted snapshot is not a future checkout assurance. [Exact official SKU](https://hypnosislive.com/mental-skills/total-focus).

Issue 03 currently avoids promises about Zen12's 12-minute equivalence and offers a free, self-directed routine first. Retain that approach. Zen12's **twelve-minute recordings, twelve levels and four styles** are seller-described product features, but its same-as-one-hour and automatic brainwave claims are unverified seller assertions, not outcomes for Final Vestige to adopt. [Official Zen12 description](https://zen12.com/about).

The optional alternative issue 05 in [PR #220](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/220) is **not** approved for substitution; neither is the optional no-offer version in [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201). This R13 recommendation does not overwrite any of them.

## First-party CTA source-of-truth verification — real WordPress records

Unlike public web crawlers that could not retrieve finalvestige.com in this environment, authenticated WordPress reads verified:
- Issue 01/02 → Puységur archive, **published page 1377** at https://finalvestige.com/free-resources/puysegurs-animal-magnetism-files/ .
- Issue 04 → *The Hatch Opened Inward*, **published post 434** at https://finalvestige.com/2026/08/20/the-hatch-opened-inward-apollo-1/ .
- Issue 06 → Focus Fieldbook, **published page 1579** at https://finalvestige.com/focus/ .
- Issue 03/05 → **no** first-party published offer guide URLs established. Recent Mind draft PRs #242, #248, #256 are not live routes. A published WordPress record is stronger than an inferred route but does not alone prove an unauthenticated visitor receives an HTTP 200 and can complete its CTA; the latter still needs an authorized browser check.

No email CTA should include `?utm_` query parameters until attribution/privacy deployment is explicitly reviewed. Email and first-party click reporting must not fabricate a delivery event, distinct subscriber, sale, A/B result, or partner conversion from a generic web click. A tiny and inconsistent subscriber tally is insufficient for meaningful A/B inference.

## Counts, welcome, delivery and compliance — no change

Read-only Jetpack status at **2026-10-31 06:31:32 UTC**: newsletter enabled and `site_can_send=true`; default new-post email **off**, `email_content_format=excerpt`, `recent_sends=[]`, `reply_to=no-reply`, `from_name=Final Vestige`. Configured welcome still links to the complete 52-page Fieldbook; **no received welcome has been verified**.

Counts persist at **total=2, confirmed=2, unconfirmed=2, suppressed=0**. Confirmed plus unconfirmed exceeds total, but we cannot infer these represent four people, a confirmed deliverable audience, or a specific implementation bug. No addresses or row-level subscriber data were retrieved.

Native Jetpack email **editor preview** and *received* MIME are still unavailable. Exact subject/preheader in markdown is not proof of native preheader support; excerpt-only WordPress may truncate disclosures and CTAs. Real sender postal address and an actual opt-out in the delivered commercial email remain unverified. The FTC's CAN-SPAM guide explains that commercial messages can include emails promoting content on commercial websites and requires truthful sender/subject, a valid sender mailing address and functioning opt-out. Four editorial / two commercial is a **content mix**, not an exemption. [FTC guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business).

Gmail recheck on 2026-10-30 found many **consumer promotional** Inspire3 messages but no conclusive Final Vestige-specific partner approval or email-marketing grant. Receiving a merchant's consumer emails does not make Final Vestige an approved affiliate. [Public affiliate recruitment](https://affiliates.inspire3.com/) likewise does not establish merchant rights; no outreach was sent.

## Strict hold and owner-level next proof

1. **Frontend/site QA** (separate from frozen homepage #49): test both Jetpack Subscribe controls *in a real logged-out browser* without entering emails. Record device, screenshot, whether it opens a real form or hosted confirmation page, and keyboard flow. If it actually loops or fails, obtain **separate founder approval** for a targeted signup-block fix. Do not edit either page in this PR.
2. **Founder / WordPress operator:** private native subscriber status/consent reconciliation using aggregate-only evidence; never export or expose subscriber addresses to GitHub.
3. **Founder / compliance:** confirm a real Final Vestige business/PO box/registered commercial mailbox address; verify opt-out in an authorized real received email; no merchant/Automattic address substitution.
4. **WordPress operator:** native editor Preview Email in a no-publish/no-send state; confirm actual excerpt, CTA, visible disclosure, subject and footer. A separately approved test recipient is needed for raw received-MIME verification.
5. **Mind & Affiliate Studio:** publish two full vetted first-party guides only with proper separate website approval; provide exact live direct-load URLs. Validate exact SKUs and seller claims; keep all merchant links inactive without written account, SKU and email-channel approval.
6. **Founder:** final review of any copy amendment and an independent explicit campaign authorization for the exact edition, recipient set, date and send action.

The independent `r13_probe.cjs` is a **source-only** deterministic scanner, not a browser automation or a release certification. Its only output is HOLD_UNSENT. All six campaign issues stay unchanged and unsent, with #03/#05 additionally blocked for merchant authorization.

## Sources and custody

- Authentic WordPress.com `newsletter.status`, `newsletter.get_settings`, `pages.get` IDs **523/1579/17/14/1377**, `posts.list` slug `the-hatch-opened-inward-apollo-1` (**434**) on 2026-10-31 at 06:31 UTC.
- Public site standards: https://finalvestige.com/editorial-standards/ and https://finalvestige.com/affiliate-disclosure/ .
- Merchant-specific product pages: https://zen12.com/about ; https://hypnosislive.com/mental-skills/total-focus .
- Merchant recruitment: https://affiliates.inspire3.com/ .
- US FTC compliance: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .
- Master source: https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175 ; release evidence https://github.com/finalvestigestudios/final-vestige-site-layer/pull/253 .

**Non-actions:** no email sent or test-sent; no subscriber imported/added/contacted/inspected individually; no WordPress page, post, settings or newsletter changed; no merchant inquiry; no merchant link activated; no work on homepage PR #49.
