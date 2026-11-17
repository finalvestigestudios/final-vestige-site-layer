# R422 — Founder copy decisions and actual Jetpack transport

**Draft-only recommendations.** No copy in this file has been adopted, scheduled, sent, or published. Scope: existing single Jetpack subscriber path, published [Dispatch](https://finalvestige.com/dispatch/) and [Focus](https://finalvestige.com/focus/) landing pages, six unchanged emails in [master PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175). Preserve original 4 editorial + 2 commercial split.

## P0 — Clarify what someone receives

The live Dispatch page still promises "new investigations and archive finds by email, when we publish them"; Focus still says the same. That can sound automatic. Authenticated Newsletter settings show **new-post automatic sending OFF**; the last five new-post records had `send_subscription=false`. This is not a reason to enable it. It **is** a consent-expectation issue.

**Proposed Dispatch hero (review only):**

> **The Dispatch: evidence worth reopening.**
>
> Original investigations, overlooked records, and practical Mind & Perception research when a carefully checked edition is ready. Subscribe to receive the free 52-page Seven Day Focus Fieldbook. You may need to confirm your email to receive future editions. No daily blasts. Unsubscribe anytime.

**Proposed Focus consent line (review only):**

> The Fieldbook is free to open whether or not you confirm an email subscription. If you choose to subscribe, we'll ask you to confirm your address before treating you as a Dispatch subscriber. The Dispatch sends occasional researched editions, not an automatic notice for every new site post. Some editions may include clearly identified affiliate recommendations. Unsubscribe anytime.

**Proposed near-download clarification (review only):**

> **Your PDF is available.** Opening or saving it does not confirm a newsletter subscription. If you signed up for The Dispatch, check your email for any confirmation request; the welcome message also includes this same Fieldbook link.

These edits avoid implying that a gift's appearance is a verified subscriber event, but **must** be reconciled against the actual Jetpack signup copy and confirmation flow by Claude/Focus. Their adoption needs founder approval, WordPress-page ownership review, and a safe standalone PR—not an unapproved write in this sprint.

## P1 — Six original letters: exact practical editorial findings

| Original slot | Current subject | Highest-impact conversion/editorial issue | Proposed action, not adopted |
|---|---|---|---|
| 01 editorial | The mind is not a camera | 01 and 02 share Puységur archive CTA, reducing topic-to-destination specificity | Founder consider source-led change-blindness candidate R414; preserve single CTA |
| 02 editorial | Before hypnosis had a name | Historical source good; 01's duplication is the conflict | Keep archive as its natural destination; no affiliate promotion |
| 03 commercial | The twelve-minute meditation question | Inactive merchant guide CTA; exact sale route, email permission and checkout unavailable | Retain placeholder, near-CTA commission disclosure, no public merchant link |
| 04 editorial | Fourteen seconds. A much longer explanation. | The interval is underspecified and can mislead about ignition | Founder review R412 NASA-source correction; no substitution yet |
| 05 commercial | Before you press play on a hypnosis audio | Inactive Total Focus guide CTA, product/bundle/refund/EMAIL rights unverified | Reserve offer; no activation or implied efficacy |
| 06 editorial | What did seven days of attention reveal? | Subscriber is returned to a page with a subscribe action, not a direct next step | Founder consider pointing to already-received PDF or its 30-day log **only after** public-link/accessibility QA; avoid a second signup |

All canonical subjects and preheaders remain the original text. WordPress's documented **post title is the actual email subject**; a second independently controlled inbox preheader is **not established** for this site's Jetpack configuration. Do not promise a custom preheader solely because one appears in Markdown or offline HTML. Official WordPress guides: https://wordpress.com/support/newsletter/email-appearance/ (last reviewed Nov 9, 2026) and https://wordpress.com/support/newsletter-settings/ .

## P2 — Non-sending progression: qualified recipient, one offer

No list-wide automation or hidden segmenting. This is an *editorial decision rule* inside the existing six-issue draft, not an additional email program.

- **Existing welcome, once subscribed:** configured 52-page PDF; actual inbox delivery NOT verified.
- **01/02 editorial:** a falsifiable observation from original historical/psychological sources, one matched first-party investigation CTA; no offer.
- **03 commercial (conditional):** reader who has a clear interest in a short audio format is invited, with a near-offer disclosure, to a **vetted first-party Zen12 evaluation** *only if* named Final Vestige EMAIL permission, approved product, true checkout terms, and founder release are all verified. Otherwise **HOLD**, not a surprise switch to public merchant URLs.
- **04 editorial:** archival evidence and uncertainty (Apollo 1), one first-party investigation CTA.
- **05 commercial (independently conditional):** Total Focus after *separate* rights/claims/guide approval; holds even if Zen12 receives approval.
- **06 editorial:** seven-day notes → 30-day practice record; *no new signup step, no unsupported psychological outcome claims.*

**Important:** No commercial issue is currently send eligible. Four editorial issues are also globally held for founder/legal/recipient/actual-preview acceptance. Editorial does not bypass the physical-address/unsubscribe requirements of any message classified commercial by primary purpose; apply legal review to every issue.

## P3 — Exact Jetpack test without email

Official WordPress supports editor **Preview email** while the post's Send this post to subscribers toggle remains OFF and distinguishes it from **Send test email**. The newer Appearance → Email Design may be staged and cannot be assumed available. Required screenshot/witness: desktop/tablet/mobile previews of the **actual Jetpack-rendered body**, the true subject, link targets (one primary CTA), disclosure proximity, full mailing address for Final Vestige, working unsubscribe mechanism and author/from identity. Also compare dark/light or system inversion and full-vs-excerpt. Real inbox delivery and functional opt-out need separately authorized tests; a static generated HTML is not equivalent.

**Blockers before any send:** eligible and deduplicated consenting recipients UNKNOWN; received welcome UNKNOWN; actual native email preview UNKNOWN; Final Vestige's valid business postal address and functional unsub UNKNOWN; product-specific publisher EMAIL rights, issue 03/05 approved live guide, earning URL, actual checkout and current refund terms UNKNOWN; founder final approval ABSENT.

**Editorial standard:** official and archival sources primary; preserve disagreements and precision; commercial relationships cannot change the historical conclusion. https://finalvestige.com/editorial-standards/ .

No WordPress, Gmail subscriber, affiliate, tracking, merge, or email write is authorized by this document.
