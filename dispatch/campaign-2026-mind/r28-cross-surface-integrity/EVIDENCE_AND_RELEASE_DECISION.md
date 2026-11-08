# Dispatch R28 — cross-surface integrity, actual WordPress constraints and release decision

**Status:** SOURCE-SURFACE QA ONLY · **ALL SIX HOLD_UNSENT** · Issues 03 and 05 **HOLD_MERCHANT**.  
**Parent:** [draft PR #351](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/351) at `b0c28c6f343333955b2aa3970d00128d8c3c5184`; master [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), issue [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), merchant issue [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). No homepage/PR #49 changes.

## What R28 adds that earlier sprints did not

The independent `audit_surfaces.cjs` checks **all four editorial delivery surfaces** against each manuscript and the six-issue manifest: the original research copy, static HTML preview, plaintext preview and stored Gutenberg post candidate. It also checks the separately maintained operator ledger and HTML reviewer board. A visually convincing HTML preview alone can miss a dropped source, a change to the source claim, a disabled guide converted into an active link or a missing legal hold in the plaintext alternative.

The audit is pure and cannot contact WordPress, subscribers or merchants. It rejects commercial-link activation, changed classifications, source/preview subject or preheader drift, lost source citations, lost substantive paragraphs, missing commission disclosures, legal footer placeholders being silently removed, unauthorized vendor tracking URLs, and an attestation that claims an email is sendable. All results are **source fidelity**, never permission to send.

### Verified GitHub source and tests

- The parent draft PR #351 was inspected live and is open/draft. All **17/17 original campaign Python source files** (six manuscripts, manifest, generator and nine test files) matched GitHub blob SHA-1 on the exact PR #351 HEAD; independently reconstructed local `unittest` suite completed **134/134 pass**; 13 generated preview assets verified.
- GitHub's **actual** R23 bridge uses `build_native_candidates.cjs` and `tests/test_gutenberg.cjs`. An earlier local ZIP's Python converter was only an offline model, **not** the committed build script. The actual GitHub JavaScript bridge was re-run with read-only V8 file shims on GitHub's exact six manuscripts and current stored Gutenberg/ledger/board assets: **six Gutenberg review candidates verified**.
- R28 cross-surface test uses the exact existing GitHub sources, stored Gutenberg candidates, current manifest, reviewer board, ledger, and the actual GitHub preview renderer. It passed **73 current-source checks**, plus **26 regression assertions including 19 fail-closed adversarial mutations**, in isolated V8. The parent HTML/plaintext files were reconstructed from the exact current preview renderer; browser/email-client fidelity to received Jetpack emails is **not** established by this run.
- A separate local Python prototype of the bridge was previously tested, but is not the committed R23 JavaScript tool. It should not be used as CI evidence. Hosted Actions remains failing without diagnostic steps; **CI is not green**.
- The renderer's separate proposed preheader `<span>` exists **only in static preview**. It is **NOT** evidence that native Jetpack supports a preheader field. WordPress post title is the supported newsletter subject path; actual received subject/preheader remain untested.

### WordPress source-of-truth, 2026-10-31 21:31 UTC (read-only)

Site 256784396: newsletter on; `site_can_send=true`; new-post auto-email **OFF**; global `email_content_format=excerpt`; `reply_to=no-reply`; sender display **Final Vestige**; welcome content configured to deliver the **52-page Seven Day Focus Fieldbook**, but delivery receipt unknown. `recent_sends=[]`. Counts total=2, confirmed=2, unconfirmed=2, suppressed=0. These are **not additive** and must not be reported as four verified recipients. Confirm actual consent/eligibility privately through an authorized WordPress admin flow; never export or expose subscriber identities in PRs.

The existing published editorial CTA targets were independently confirmed through the authenticated content API on October 31: **The Missing Caption** post ID 1122; **Puységur’s Animal Magnetism Files** page ID 1377; **The Hatch Opened Inward** post ID 434; **Focus Fieldbook** page ID 1579. The Dispatch signup page ID 523 and Editorial Standards page ID 17 remain published. This establishes published site records, not subscriber click behavior.

**Delivery-format finding:** the official [WordPress.com newsletter settings](https://wordpress.com/support/newsletter-settings/) reviewed October 26 describe a **55-word** fallback, while the [Jetpack customization guide](https://jetpack.com/support/newsletter/customize-the-newsletter-experience/) updated October 28 describes **350 characters**, with a **per-post full-text override**. Both models in R27 lose CTAs and Issue 03/05 disclosures. Do **not** change the global format based on an offline model. Under a separately authorized process, inspect the per-post override in an unpublished draft, safely test **actual received MIME**, and preserve automatic new-post sends OFF.

## Truth-in-offer check (official source, not acceptance)

**Zen12:** official [About](https://zen12.com/about) offers twelve-minute audio and four listening variations. The [seller product site](https://zen12.com/) advertises Beginner 6/24 MP3s, Premium 12/48, Advanced 6/24; full-course checkout materials do not prove every tier's live sale conditions. Seller language that twelve minutes equals an hour of meditation and that audio changes brainwaves is **seller advertising**, not a verified product-specific conclusion. Editorial Issue 03 correctly isolates features from effectiveness and reserves its single warm-up guide CTA pending publication/permission.

**Hypnosis Live Total Focus:** official [Total Focus listing](https://hypnosislive.com/mental-skills/total-focus) describes 33 minutes and 47 MB, an audio preview, dynamic prices and stronger "reprogramming" and concentration-result promises. These are **merchant-reported features and claims**. Issue 05 does not claim the recording has been independently evaluated or that the posted price/discount will hold. Its warm-up guide is not publicly approved.

No Inspire3-specific written affiliate acceptance, email-promotion approval, permitted earning URLs, approved promotional creative, exact checkout/refund terms or rights to use vendor video/audio have been substantiated. **Do not infer permission from public marketing pages or consumer promotional email.** Mind & Affiliate Studio #171 owns offer-page publication and eligibility; Dispatch must wait.

## Legal + operational release gates, ALL unverified

| Gate | Current evidence | Decision |
| --- | --- | --- |
| Final founder approval of final subjects, email bodies, audience and send schedule | Draft-campaign authorization only | HOLD all |
| Legal Final Vestige physical postal address | Not provided or verified; Automattic's address is not FV's | HOLD commercial |
| Live Jetpack unsubscribe on a genuine delivered newsletter | No received MIME or tested opt-out | HOLD commercial |
| Native Jetpack delivered full body, preheader, subject, disclosure and footer | No authorized preview/test email | HOLD all |
| Recipient consent/confirmed and reachable list | Counters only, not verified unique eligible audience | HOLD all |
| Merchant acceptance, **permission to email**, exact earning link/creative rights | Not verified | HOLD 03, 05 |
| Published, approved product-guide destinations | Not live | HOLD 03, 05 |
| Genuine checkout pricing/refund/media terms | Not verified for final send date | HOLD 03, 05 |
| Hosted CI and real-client accessibility/readability | Hosted jobs failing; offline QA is not MIME proof | HOLD all |

FTC [CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) governs accurate subjects/sender, commercial identification, valid mailing address, and functional opt-out. The separate FTC [Endorsement Guides](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) support prominent near-offer commission disclosure; general site disclosure alone is insufficient.

## Attribution approved in principle, metrics not invented

Do not add pixels, URLs, affiliate click IDs, mailing lists or new platforms. For each edition, record only **source-labeled public pageview/CTA counts** if measured in existing permitted analytics, separately from Jetpack-reported sends/deliveries, downstream outbound affiliate clicks and merchant-confirmed sales if those reports later become available. State clearly when a metric is unavailable, and never treat a pageview as a recipient, an outbound click as a sale or a `site_can_send` flag as deliverability. The current audience is much too small for meaningful A/B statistics.

**No send, test-send, scheduled send, WordPress mutation, merchant contact, affiliate activation, list export or cost was performed.**
