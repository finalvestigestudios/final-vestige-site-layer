# Dispatch R153 | One-offer consent truth and evidence-led editorial companion
**2026-11-05 Pacific | DRAFT, isolated from production | OWNER #174 | COMPANIONS #171, #129, #820.**

## What R153 adds, without redoing previous rounds
- An **optional** original, primary-source-grounded editorial revision to canonical issue **01**, not a seventh newsletter or an approved substitution. Accessible, static, reviewer-only HTML and plaintext previews. No affiliate, no new opt-in, no third-party pixel, one primary first-party Fieldbook CTA.
- A **native opt-in lifecycle correction** specific to WordPress.com. Some already-verified WordPress.com accounts skip another confirmation email. A missing confirmation email is not a complete rejection of a *provider-verified new signup* for this pathway. Conversely, a mailed confirmation request by itself is not a confirmed signup. The new offline `native_optin_truth.cjs` classifies provider-redacted records and **never outputs a proven live count** without independent provider audit.
- A concrete **one-offer Zen12 Premium gate** locked to the exact Mind R159 unpublished buyer-guide source and seller page—not a vague Inspire3 catalog and not the approved public affiliate earning URL. One offer, one meaningful purchaser intent: a reader independently comparing structured short meditation-audio libraries. This is a hypothesis, not an observed customer segment.
- Read-only authenticated WordPress snapshot with a strict **4 editorial : 2 commercial** ledger. Every issue stays HOLD_UNSENT; 03/05 also HOLD_MERCHANT. No changes to master PR #175, QA #201, homepage #49, Grok TASK-008 or WordPress.

## First read: exact sources and existing work (checked this round)
- Owner [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), the latest comment [R152](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1196), master [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647`, per-issue safety [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) HEAD `ef53e5a17046e3dff5a4a7e3b0f4c8fbce9cd6f6`.
- Mind [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), exact latest [PR #1198](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1198) HEAD `ea288fd7afc202fe3c3dbf552901d38acb3ca617`: `mind/r159/zen12-second-signal-buyer-bridge-UNPUBLISHED.html`. It has a disabled purchase control, a near-control prospective disclosure, primary-source constraints, no active earning link, and is **not a live destination**.
- Live WordPress [Dispatch](https://finalvestige.com/dispatch/) page #523, [Focus](https://finalvestige.com/focus/) page #1579, [Editorial Standards](https://finalvestige.com/editorial-standards/) page #17. The last requires primary evidence, explicit uncertainty, provenance and commercial independence.
- Connected Grok/Praxxis [TASK-008](https://docs.google.com/document/d/1_dqcJeqxbvYb1prGxy0nSWTsHu8p0PSRsDB_NPNbL48/edit) and dated handoff [document](https://docs.google.com/document/d/1uK7cZdMv44dkKwDDGILUTCrI2zw3iA0cN5VzdLmF5C8/edit) reviewed read-only. Grok controls creator assets and platform publishing; Claude owns production engineering.

## Read-only WordPress truth at 2026-11-06 04:37 UTC
The connected newsletter status says **enabled**, `site_can_send=true`, with **automatic new-post emails OFF**, **five recent posts explicitly not emailed**, and the site configured for **FULL** post body in email. Sender display is **Final Vestige Studios**, reply-to is **no-reply**, category targeting is OFF. Welcome template contains a link to the existing **52-page Seven Day Focus Fieldbook** PDF.

The dashboard returns `total=3`, `confirmed=3`, `unconfirmed=2`, `paid=0`, `suppressed=0`, imports24h=0. A separate WordPress follower snapshot is `wpcom=3`, `legacy_email=0`. **Do not add 3+2 and call it five subscribers.** WordPress's current documentation says *Not confirmed* is excluded from total; it also says a WordPress.com follower may receive email. The **native Subscribers tab's per-person Email subscription=Subscribed** indicator, not these aggregate counts, is the relevant email-eligibility check. Do not expose, export, mirror, or modify subscriber email addresses.

**Two native signup pathways:**
1. A new email without a verified WordPress.com account can receive a confirmation request, then a welcome message after confirmation. A sent confirmation request is neither a completed confirmation nor evidence of the PDF's delivery.
2. A subscriber whose email is already verified through WordPress.com may skip a second confirmation email and receive the welcome directly. In this case, require a **new provider-subscribed transition and actual email eligibility**; don't falsely reject an otherwise legitimate new signup just for lack of a confirmation-email artifact.

A **snapshot** of existing eligible status cannot be counted as a **new** `confirmed_signup`. This module returns `CONFIRMED_SIGNUP_CANDIDATE_ONLY` on redacted synthetic evidence. Only independently authenticated native event provenance, appropriate consent, nonduplicate transitions, and current Email subscription status can justify actual counts. Site `?subscribe=` parameters and the public Fieldbook success screen are not provider evidence.

The October 25 Gmail message is a **confirmation request**, not proof of the received welcome or actual publisher footer. Current bounded Gmail searches of Oct 1–Nov 5 found the confirmation request but no retrieved matching Final Vestige welcome and no personalized Inspire3 approval. Absence from these queries is **not proof none exist elsewhere**.

## Real conversion route, held until authorized
**One high-intent buyer hypothesis:** someone who already wants to compare an audio-based meditation program, not a general history reader or a person who watched a perception clip. The 4:2 campaign remains weekly/editorial-first.

Creator asset with immutable Grok `asset_id` (Grok) → actual human landing session (Claude) → evidence-backed history/perception article (Mind) → optional Focus Fieldbook and appropriately confirmed Jetpack opt-in (Dispatch) → **approved, published, independently reviewed Zen12 Premium buyer guide** (Mind) → verified partner link (only after accepted account and email rights) → merchant sale/settlement evidence (Commerce).

The Mind R159 guide is an isolated draft, not a functioning public URL. Don't put the GitHub raw draft, fake merchant destination, or a `?utm_` link to it into any newsletter. The commercial buyer guide and affiliate earning link must be tested *after* approval by Mind & Affiliate and founder. Maintain independent right for readers to use free Fieldbook without purchasing.

**Zen12 Premium official page** describes twelve levels, four styles per level, 48 MP3s and twelve-minute sessions. It displayed **$87.99** for Premium on 2026-11-05 and advertises a one-year money-back guarantee, but this is merely a seller-page snapshot: current checkout amount, taxes, eligibility, actual refund practice and fulfillment remain unverified. The seller's “12 minutes equals an hour” and health/cognitive claims are **not independently proven for this product**. Public Inspire3 [affiliate signup](https://affiliates.inspire3.com/) does not prove FV-specific acceptance, earning link, paid commission, or **permission to promote via email**. Even seller-provided creative is not automatically licensed for this specific channel.

**Reserved Issue 05**: Hypnosis Live Total Focus remains a separate HOLD_MERCHANT draft. Do not quietly replace this with Zen12 or double the number of commercial placements.

## Front-end and legal execution blocker: decisive truth vs another mock
- Authenticated WordPress editable content for Dispatch #523 contains the native Jetpack Subscribe block; the separate rendered-view API projects a Subscribe anchor back to page #523, without a serialized email input. That is a **representation mismatch**, not proof that a signed-out browser cannot subscribe. Prior Playwright tests were offline fixtures, **not** a production guest browser pass. Claude/Site QA owns signed-out mobile + desktop live inspection.
- Focus #1579's success panel can be activated by untrusted nonempty `?subscribe=` values. Existing corrective draft [PR #1079](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/1079) is **not live**; no duplicate production edits.
- WordPress documents an actual editor **Preview email** function, separate from **Send test email**. Preview requires the post-level send toggle visible in the editor; this was NOT touched. A local mock does not verify native content length, footers, subject layout, alt text, or actual receive. Do NOT toggle sending, publish, or send a test without final campaign approval.
- For commercial email, FTC CAN-SPAM requires honest sender/subject, valid **FV publisher** physical mailing address, and clear working opt-out; consent alone does **not** waive these requirements. Neither the seller's London address nor Automattic's confirmation footer is FV's physical mailing address. Never guess or insert one. The address and actual live unsub are **NOT VERIFIED**.
- Subject QA for optional Issue 01: the phrase “second thing ... still there” describes a target in a controlled stimulus experiment; body immediately clarifies perceptual report limits. No exaggerated therapy/effectiveness claims, invented testimonials, scarcity, guaranteed outcomes, or partner link. One first-party educational CTA, source URLs are references.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE / EXPERIMENT → PASS / FAIL → OWNER
| Priority | Offer / step | Blocker | Specific acceptance | Evidence | Owner |
|---|---|---|---|---|---|
| P0 | Focus free Fieldbook → email subscriber | Current real signed-out subscribe input unknown | Signed-out 320/390/768/1440 inspection of Dispatch and Focus, no form submission | LIVE UNKNOWN, serialized API mismatch only | Claude / Site QA |
| P0 | Native subscribe → confirmed lead | Dashboard aggregates cannot establish eligibility or transition | Read Email subscription state **privately**; native event evidence for each pathway, redact before aggregate | Count = UNKNOWN | Dispatch / WP owner |
| P0 | Confirmed lead → Fieldbook | Welcome configuration ≠ delivery | Explicitly authorized received welcome, link reaches 52-page PDF, access checks | UNKNOWN | Dispatch |
| P0 | Campaign editorial → inbox | Jetpack full-text rendering, FV postal/unsub unverified | Native non-sending preview and subsequent approved received-message audit | MOCK TESTED / NATIVE UNKNOWN | Dispatch / Site QA |
| P0 | Zen12 guide → paid merchant | Affiliate name, channel rights, URL, terms and LIVE guide missing | Partner authenticated permission + exact SKU checkout + current claims review + founder approval | FAIL RELEASE GATE | Mind #171 / founder |
| P1 | Buyer → settled revenue | No partner paid order/refund/fee statements | Merchant or partner-issued purchase, commission, refund and fee records + verifiable attribution | KPI = NOT COMPUTABLE | Commerce / Praxxis |
| P1 | Grok asset → qualified human landing | Actual stable asset IDs and source-to-page sessions unavailable | TASK-008 inventory + existing first-party consented aggregate analytics | Attribution = UNKNOWN | Grok / Claude |

## Source and QA references
- [Raymond et al. (1992), attentional blink original](https://pubmed.ncbi.nlm.nih.gov/1500880/).
- [Hommel & Akyürek (2005), lag-one sparing / order error](https://pubmed.ncbi.nlm.nih.gov/16365947/).
- [Zen12 exact official seller page](https://zen12.com/?no-popup=1); note merchant representations vs product-specific independent evidence.
- [WordPress.com subscriber status, reviewed Nov 4 2026](https://wordpress.com/support/subscribers/).
- [WordPress.com newsletter settings](https://wordpress.com/support/newsletter-settings/) and [non-sending email preview documentation](https://wordpress.com/support/newsletter/email-appearance/).
- [FTC CAN-SPAM business requirements](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) and [FTC endorsement disclosure Q&A](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking).

## Test record and controlled deployment boundaries
- Original master #175 nine files' Git blob hashes independently checked; eight canonical source hashes match prior local archive; native original Python tests **6/6 passed** this sprint.
- R153 opt-in classifier + adversarial tests source-controlled; **51/51 local V8 assertions passed** on connector readback. The code does not import contacts, call WordPress, count real leads, or send anything.
- Standalone email-safe static reviewer mock generated from R153 optional editorial; HTML/PLAINTEXT previews and generator source-controlled. **12/12 structural tests passed** before GitHub readback. This is NOT a true Jetpack preview and cannot substitute for one.
- No A/B experiment, observed CTR, click-to-order, paid sale, refund, or statistical inference. `net_revenue_per_1000_qualified_sessions` remains **NULL** because numerator and denominator are not independently established.
- No sends, test emails, subscriber modifications, site changes, tracking scripts, merchant activations, social posts, new SaaS or costs. All PRs stay draft; founder governs production release.

**Release:** All six **HOLD_UNSENT**; Issues 03 and 05 **HOLD_MERCHANT**.
