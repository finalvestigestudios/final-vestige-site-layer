# R453 independent header, offer-claim and legal red-team

**Repository input:** [R446 source-pinned twelve-version manifest](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/fd374e58425a5168418249780a9f61d308c9fbf9/dispatch/r446/SOURCE_PINS_AND_RELEASE.json), exact file Git blob `bfd17cb9df915772ba317616b6d8ebf7b51b218e`. **Do not modify or adopt** that existing founder comparison. [R452 Zen12 manuscript](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/52c3f79bf4f775e977c3e32ebe6e00bd2075bd4a/dispatch/r452/ISSUE03_SUBSCRIBER_BOUNDARY_REVIEW.txt) and [R450 Hypnosis Live subscriber-only review](https://github.com/finalvestigestudios/final-vestige-site-layer/blob/a2124ee0996e28376f5d07f034842bfa2e0de2e3/dispatch/r450/ISSUE05_SUBSCRIBER_ONLY_REVIEW.txt) remain **separate alternatives**, not approved send copy.

## Actual newly reproduced copy hazard: proposed email header formatting leakage

The R446 manifest's alternative `subject` and `preheader` fields for **four** of the six issue slots contain leading Markdown `** ` literal characters. In an HTML Markdown renderer these may be interpreted as formatting; in an email subject or preheader field they can become visible punctuation and lower trust/quality. These are **metadata extraction errors in the prior review manifest**, not proof that the underlying manuscripts have dirty subject lines. Do not paste manifest values straight into Jetpack. No existing source was rewritten.

| Slot | R446 alternative stored (unsafe literal) | Correct proposed unformatted subject | Preheader correction |
|---|---|---|---|
| 01 | `** The person changed. The conversation continued.` | The person changed. The conversation continued. | A 1998 street experiment, a missed substitution, and the difference between observation and confidence. |
| 02 | `** The witness was also the experimenter` | The witness was also the experimenter | Puységur's 1784 account, Franklin's separate tests, and the gap between a record and proof. |
| 05 | `** Before you buy a hypnosis recording` | Before you buy a hypnosis recording | An old lesson about suggestion, and five buyer checks that work today. |
| 06 | `** Eight cups. One useful kind of doubt.` | Eight cups. One useful kind of doubt. | Fisher’s 1935 tea test and a better way to read your seven-day focus notes. |

**Empirical local source finding:** R446 manifest was read by exact repository SHA and checked in V8 with the committed `subject_preheader_gate.mjs` logic. All six original pairs passed static formatting checks; all four flagged alternative pairs were 01/02/05/06; 03/04 alternatives did not share this leading-Markdown hazard. This is NOT a full subject-truth or Jetpack rendering check, and the suggested corrected strings are review-only pending founder choice.

The gate checks **twelve** pairs for missing content, line breaks/header injection, literal Markdown/HTML artifacts, length advisories, and a narrow set of unacceptable guarantees; it does not certify all claims true. It intentionally **does not automatically scrub** any subject from a live campaign. Hard stop even for editorial editions: human subject/content parity and native email preview still required.

## Specific merchant claim/exact-offer separation, checked against seller pages on November 18, 2026

| Actual official page | What seller states | What Final Vestige must not turn into a verified independent fact |
|---|---|---|
| [Zen12 regular description](https://zen12.com/about) | Seller describes 12-minute MP3 sessions, twelve levels, four audio styles (guided, nature, music, noise) and promotes one-hour equivalence and brainwave entrainment | **Do not state** one paid 12-minute session scientifically equals an hour of conventional meditation, reliably improves mental health, or automatically produces quantified brainwave effects. Product-specific independent clinical proof has **not been established**. |
| [Zen12 separate /secret/ sales funnel](https://zen12.com/secret/) | Different current sale presentation, countdown, coupon, 12-level/48-file bundle, extras and advertised price | Do not reproduce the currently visible code, countdown, advertised price, bonuses, refund promise or package identity as authorized/valid for FV traffic. Dynamic offers can change; **not the same package** unless merchant proves exact link/checkout and channel use. |
| [Hypnosis Live FAQ](https://hypnosislive.com/faq) | Seller describes MP3 downloads, recordings of approximately 40 minutes, usual per-session pricing, 14-day refund requests limited to five sessions/year | Treat these as **seller-stated** information. No specific purchased SKU, successful delivery, processed refund, promotional email permission or product efficacy established. |
| [Inspire3 affiliate sign-up](https://affiliates.inspire3.com/) | General terms/public recruitment, not FV's account | Generic signup material cannot prove final acceptance, approved email-channel creative, issued tagged earning URLs, product eligibility, rate or settled commission. |

### Claim-safe conversion copy

The **value proposition should be the free practice, not a vendor miracle**: “Before you buy any meditation recording, try a short independent practice, note what actually happened, and compare the exact product terms.” In Issue 03, “Zen12 is described by its seller as a program with twelve-minute sessions and twelve levels” is bounded and suitable as a *seller statement*. “One session delivers an hour of benefits,” “eliminates anxiety,” or “proved to change brainwaves” is not suitable in FV's editorial voice.

**Audience:** history/perception readers who voluntarily expressed interest in a short practice. Reader content controls remain direct: free Fieldbook available without a purchase; subscriber consent is not a condition for accessing a factual claim or for reviewing a relevant buyer guide. Do not infer interest in buying Zen12 merely because someone visited /mind/, watched a video, or downloaded a PDF.

**Future optional CTA:** “Read our independent Zen12 buyer guide,” but **not live**, so in a held specimen it remains explanatory text, not a pseudo-clickable button. Only Mind/Commerce may supply a genuinely **published and approved** guide URL; it cannot use an unmerged PR's HTML file as a visitor destination. If and only if that future approved guide contains an issued qualifying earning link, its live link needs a clearly adjacent commission disclosure. The newsletter's own near-guide placement also needs clear commercial context.

**Example near-CTA disclosure (draft; not activated):** “This guide discusses a product for which Final Vestige may receive an affiliate commission if you purchase through an eligible link. We explain the product's limitations and do not treat seller claims as independent findings.” This must not imply an existing affiliate contract if none has been approved; until then use: “A possible commercial relationship is under review. No affiliate link is active or approved.”

## CAN-SPAM, editorial standards and genuine inbox witness

Read [FTC CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business): materially commercial messages need accurate sender/from/subject, identifiable promotion, **FV's valid physical postal address**, working opt-out, prompt opt-out processing (10 business days), and continuing responsibility despite a provider. It does not exempt promotional emails merely because a reader signed up for the newsletter; the primary purpose is what matters. See also [FTC endorsements guidance](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking) for disclosure transparency.

The live site [Editorial Standards](https://finalvestige.com/editorial-standards/) requires source-before-story, documented fact/inference separation and disclosing commercial relationships. That applies equally to subjective hypnosis experiences and attention studies: **historical study ≠ modern product's efficacy**.

The authenticated WordPress settings **reply_to=no-reply**: don't write “reply to this email” as the issue CTA unless a verified alternative contact channel and founder permission exist. Actual `email_content_format=full` increases the importance of excluding reviewer-only sections and internal QA notes from any future WordPress email-post body. The sender shown is “Final Vestige Studios,” but a display name is not proof of full header identity. Keep mail-client screenshots and actual sent message headers (if and only if later authorized) as distinct proof types.

The actual Jetpack template, physical footer and unsubscribe experience **have not been witnessed**. A preview in a browser, a static HTML reproduction, an old WordPress confirmation and the Automattic postal address are **not interchangeable**. Do not mark the legal gate passed until the **FV-owned address** and actual unsub path are visibly present and functional in a valid authorized sender artifact.

## Priority and go/no-go verdict

**Editorial choice:** The six original subjects remain eligible for founder copy review. Four of six *alternative subject/preheader metadata pairs* in R446 must be normalized manually before use. **No existing six manuscript, review manifest, or WordPress page was modified.**

**Commercial gate:** Issue 03 Zen12 and Issue 05 Hypnosis Live are both `HOLD_UNSENT`. There is no confirmed named affiliate email authorization, issued link, live reviewed buyer guide, genuine Jetpack preview, publisher postal/footer witness, or founder final send approval.

**Business result:** Completed source/quality assessment is not an order, acquired lead or revenue. As no independently settled orders and audited qualified human sessions were supplied, the realized net revenue per 1,000 qualified human sessions is **NOT COMPUTABLE**. No claims about A/B performance, clickthrough, purchases or conversion rates are warranted.
