# R205 — The email that can actually convert: source-to-release evidence

**As of:** November 8, 2026, 00:39 PT / 08:39 UTC. **Release: HOLD_UNSENT for all six.** This is independent source-only work, not a WordPress or email activation.

## What was checked first

- The canonical six-issue pilot remains draft PR #175 at **d57ccdba3aee8f065e143e101c2945f4f3d01647**. Each of the eight Git blobs (manifest, six letter files and original Python tests) was rechecked against the downloaded master; the native original suite ran **6/6 PASS**. Existing readiness PR #201 is unchanged; previous isolated Dispatch PR #1550 is the parent of this draft. Frozen homepage PR #49 is not edited.
- Live `/dispatch/` WordPress page 523 and `/focus/` page 1579 inspected read-only. Both advertise the 52-page Fieldbook and existing Dispatch list. The REST-rendered Subscribe block in page 523 contains an anchor to the page itself, not an email input; **this may be a server/API fallback and does not prove the public hydrated browser form is broken**. Actual browser interaction and real subscriber transition remain untested.
- WordPress Editorial Standards inspected read-only (primary evidence, uncertainty, corrections and commercial independence). Mind #171 and latest handoff #1553 reviewed: Zen12 comparison guide is **unpublished**; no Final Vestige-specific affiliate email permission, live vetted guide, or issued earning link.
- Fresh authenticated Jetpack read at 2026-11-08T08:39:37Z: enabled, `email_new_posts_by_default=false`, `email_content_format=full`, `reply_to=no-reply`, sender Final Vestige Studios, last five posts marked **never_sent_opted_out** (not pilot sends). Status counters 3 total / 3 confirmed / 2 unconfirmed. Jetpack Stats independently reports **3 WordPress.com followers and 0 email-only followers**; these different counters cannot establish the provider-filtered email-eligible recipient number. A WordPress.com signed-in subscriber can have a different confirmation path; do not require a click unconditionally. Received final welcome, footer and opt-out remain unverified.
- Exact merchant claims: Zen12 seller describes twelve levels and 48 Premium MP3s; its twelve-minutes/equivalent-hour effectiveness promise is **not independently established for that product**. Hypnosis Live Total Focus item advertises 33 minutes, 47 MB, and a fourteen-day refund; official FAQ caps refunds at **five sessions per year**. The public Inspire3 portal advertises a special affiliate link but does **not** grant this publisher permission for email campaigns. Displayed prices and merchant offers vary and were intentionally omitted from all email candidates.
- Scoped connected Gmail searches found no message whose subject is exactly the configured Dispatch welcome and no Fieldbook mention since Oct 1; **absence in one connected inbox is not proof non-delivery to every subscriber**. A broad partner-message search primarily returned consumer marketing and was not accepted as authorization.

## Unique high-impact copy/conversion correction

Original Issue 06 sends **existing subscribers back to /focus/**, a subscription landing page whose primary action is to subscribe. This is poor destination matching and risks double-counting attempts; it is *not* proof of any real duplicate subscriber. The new optional Issue 06 version points to **one confirmed published investigation** rather than asking readers to subscribe again. It integrates one first-party research source, context and limits, and a practical log interpretation exercise. The static reviewer HTML intentionally contains a postal and unsubscribe hard stop. This edition **does not replace canonical Issue 06**, and commercial issues 03/05 remain untouched at 4:2.

## One offer, one audience, one purchase

**Audience hypothesis:** viewers of Grok's verified published perception/focus assets who voluntarily subscribe for the Fieldbook, explicitly consent to newsletter offers, then read a vetted Zen12 buyer guide. Grok owns actual asset ID and platform links; no asset ID is invented here.

**One provisional offer:** Zen12 Premium, **not activated**; offers are only conditional until Mind #171 proves named partner approval, EMAIL-channel permission, earning URL/format, seller checkout/refund terms and a live reviewed guide. The link must stay disabled until all are documented.

**Progression (no email send):** qualified-human Grok asset_id / utm_source / utm_campaign / utm_content → Focus arrival → provider-confirmed first eligible subscription transition **once per recipient, securely deduped without exposing PII** → configured welcome/Fieldbook actually received → relevant editorial message → one optional disclosed vetted guide → affiliate outbound click (**not revenue**) → independently reported paid order → refunds/fees and cleared commissions → realized net revenue per 1,000 qualified-human sessions on 7/30-day cohorts. An already-subscribed user clicking Focus is not a new lead.

**Why no performance number:** no verified exact qualified-human session denominator, source attribution to actual Grok asset IDs, provider-confirmed eligible email recipient count, purchase settlement or refund ledger. Report **NOT COMPUTABLE**, not a fabricated 0 or simulated A/B lift. Do not use a two- or three-person list for inference.

## OFFER → FUNNEL STEP → BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL → OWNER

| Offer / step | Blocker | Required safe action | Evidence and status | Owner |
|---|---|---|---|---|
| Zen12 → approved guide | No named acceptance, EMAIL rights, earning link or LIVE guide | Obtain account-scoped written rights/URL and Mind source-reviewed public page | Official catalog ≠ permission; **FAIL release** | Mind #171 |
| Focus → confirmed lead | Provider-filtered eligible recipient count unknown | Privately inspect provider `Email subscription=Subscribed` deduplicated aggregate and real transition | 3/3/2 nonadditive, Stats 3 WPcom/0 email-only; **OPEN** | Claude / Focus #129 |
| Dispatch → real recipient | Native received HTML/plain, valid FV address, unsubscribe unverified | Use Jetpack editor's **Preview email** without sending only if no unauthorized setting mutation; separate authorized received-message audit required | Offline static HTML ≠ real email; **FAIL release** | Dispatch / Site QA |
| Subscriber → next value | Issue06 sends subscriber to another signup | Offer published Change Blindness investigation instead, one CTA | New original optional source HTML/TXT; **LOCAL ONLY** | Dispatch |
| Sale → net cash | No verified partner sales/fees/refunds or human denominator | Privately reconcile completed/cleared orders and cohorts; aggregate only | **NOT COMPUTABLE** | Commerce / Praxxis #820 |

## Legal and delivery hold

FTC requires truthful sender/subject, visible advertiser identity for promotional email, valid **publisher's** postal address and effective opt-out; Jetpack's platform or merchant addresses do not substitute for Final Vestige's address. Source-only alternatives and synthetic MIME tests cannot prove actual rendering/operation. The official WordPress editor's Preview email control appears only after the post-local Send-to-subscribers toggle is selected; **do not toggle or persist anything without controlled approval** and do not click Send test. No email or list mutation is authorized in this sprint.

## Source and provenance

GitHub: #174, #171, #820, #129; draft PRs #175, #201, #1550, #1553. Publisher https://finalvestige.com/editorial-standards/ ; offer https://zen12.com/hnp ; https://hypnosislive.com/mental-skills/total-focus and https://hypnosislive.com/faq ; program https://affiliates.inspire3.com/ ; original experiment https://doi.org/10.3758/BF03208840 ; compliance https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business ; WordPress preview https://wordpress.com/support/newsletter/email-appearance/ .

**Safety:** no messages/test messages, page/settings writes, subscriber imports, affiliate links, merchant contacts, social publications, tracking scripts, spending, releases, or merged code. Founder retains final send and production authority.
