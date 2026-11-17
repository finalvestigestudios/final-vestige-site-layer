# Final Vestige Dispatch R425 — POST-BACKED TRANSPORT, CONSENT AND WELCOME PROOF

**DRAFT ONLY · NEVER SEND/PUBLISH · SOURCE-CONTROLLED REVIEW**

This new work is deliberately stacked on [R424 draft PR #2873](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2873) at `4b78b9da14a38a25cd73f8cff950aa90e82b0aea`, with [canonical pilot #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) unchanged at `d57ccdba3aee8f065e143e101c2945f4f3d01647`. Original independent release gate [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) also unchanged. Source coordination [Dispatch Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [Mind Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), Focus #129, revenue #820; TASK-008 and Grok handoff read only, no role takeover.

## Material new findings from official sources (checked November 17, 2026)

**1. Native Jetpack is post-backed.** Its documented sending workflow uses publication of a NEW WordPress post, and the **post title becomes the email subject**. Thus an offline beautifully rendered email HTML/TXT file is **not** automatically a sendable Jetpack campaign. Manual per-post enablement can send subscribers on post publication even though the site-wide default is OFF. [Official WordPress send guide](https://wordpress.com/support/newsletter/send-newsletter-emails/) and [Jetpack newsletter](https://jetpack.com/support/newsletter/). No WordPress posts, drafts or settings were written in this sprint.

**2. Preheader is not mapped.** The canonical manifest carries six good preheaders; WordPress documentation does not establish a separately settable *inbox preheader* for these post notifications. It documents an excerpt introduction for `email_content_format=excerpt`, but Final Vestige is set to **full**. An excerpt is not necessarily an inbox preheader. Until a real native editor Preview is witnessed, proposed preheaders are **EDITORIAL SOURCE FIELDS ONLY**, not delivered inbox QA. [Appearance guide](https://wordpress.com/support/newsletter/email-appearance/).

**3. Double opt-in is not uniform.** Official [newsletter settings guidance](https://wordpress.com/support/newsletter-settings/) says new subscribers without a WordPress.com account receive a confirmation email; existing WordPress.com users can SKIP that email and receive the welcome directly. Therefore a universal confirmation-link-click count would **miss legitimate WP.com account subscribers**. Use provider-authoritative verified/eligible subscription state to derive a deduplicated `confirmed_signup` only where the user has permitted the relevant communications; no client-side PDF access, URL flag, Reader follow, or dashboard aggregate proves eligible receiving inboxes. Do not invent individualized events.

**4. The active welcome also contradicts disabled post-by-post sends.** Alongside the two public pages identified in R424, WordPress's configured welcome says “You'll hear from us when there's a new Final Vestige investigation or a worthwhile find from the archives.” The separate `WELCOME_CADENCE_PROPOSED_NOT_APPLIED.txt` offers a truthful occasional-edition replacement. It has NOT been set live and is not approved for substitution.

## Current authenticated read-only snapshot (2026-11-17 14:38 UTC)
Newsletter ON; automatic email for new posts OFF; FULL content; sender Final Vestige Studios; reply-to no-reply. Dashboard: total 3, confirmed 3, unconfirmed 2, suppressed 0. Separate WordPress.com Reader followers 3, direct-email followers 0. These fields overlap/differ; **distinct eligible recipients UNKNOWN**. Five recent sends `never_sent_opted_out` do not prove an entire historical zero-send series. Welcome links the 52-page Fieldbook (asset identity previously verified), but a received welcome is not verified. A 2026-10-25 confirmation in connected mail is **not** the received welcome. Actual Jetpack native Preview, Final Vestige business postal address and functional unsubscribe rendering are unverified.

## Original six pilot issues — transport acceptance
| Slot | Original subject | Evidence and decision |
|---|---|---|
| 01 editorial | The mind is not a camera | Existing Puységur CTA; distinct editorial source; post-title/native Preview HOLD |
| 02 editorial | Before hypnosis had a name | Same Puységur landing destination as 01; CTA fatigue review; post-title/native Preview HOLD |
| 03 commercial | The twelve-minute meditation question | Zen12 guide marker inactive; disclosure retained; named email rights/live guide/earning link/checkout plus native Preview HOLD |
| 04 editorial | Fourteen seconds. A much longer explanation. | Apollo 1 interval is not source-defined in subject; NASA chronology requires correction before adoption; HOLD_COPY |
| 05 commercial | Before you press play on a hypnosis audio | Total Focus guide marker inactive; exact product, pricing, qualified refund and email rights HOLD |
| 06 editorial | What did seven days of attention reveal? | /focus/ leads an already subscribed reader back to signup; progression review HOLD |

**Six new offline post-backed review specimens** are generated from the exact canonical #175 source. They expose the proposed post-title subject and proposed preheader as distinct editorial fields, preserve original body/first-party links and the inactive merchant guide marker, and visually flag all unresolved postal/unsubscribe and email-transmission requirements. **None** is a native WordPress email render, importable campaign or approved alternative issue.

## Funnel proof, owners, and allowed next experiment

| OFFER → STEP | BLOCKER → CHANGE/EXPERIMENT → PASS/FAIL EVIDENCE → OWNER |
|---|---|
| Focus Fieldbook → permitted subscriber | Signup+welcome promise mismatches actual cadence → founder-review 3-surface text then authorized change later → current WP welcome and R424 live pages observed, RECEIPT UNKNOWN → Focus / Claude / Founder |
| Four editorial issues → inbox | Post-title subject / unknown inbox preheader / true postal footer → authorized **non-sending** native post editor Preview on mobile, with send toggle OFF → offline specimens PASS only, native rendering UNWITNESSED → Dispatch / Founder |
| Zen12 → vetted guide → paid order | Partner EMAIL-channel approval, issued URL, approved live guide, seller checkout and paid settlements absent → Mind obtains private proof, release stays HARD HOLD → Mind / Commerce |
| Total Focus → vetted guide → paid order | Same permission blockers plus single SKU/bundle and refund specificity → independently recheck seller FAQ + referred checkout, no offer links until cleared → Mind / Commerce |
| Grok creator asset → qualified visitor → lead → customer | Asset-ID attribution, provider confirmation and settled merchant revenue absent → instrument under existing Claude contract after explicit approval; no duplicate tags, synthetic successes or A/B claims → Grok / Praxxis / Claude |

**Release boundary:** No sending or test-email, scheduling, publishing, subscriber import/contact, changing site settings or live pages, affiliate activation, new newsletter platform, new spending, social posting, core website code changes or merge. Affiliate disclosure next to qualifying links; FTC [CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) still requires accurate sender/subject, valid Final Vestige postal address and functional opt-out in commercial messages. An Automattic/vendor postal footer does not prove a Final Vestige publisher address. Product seller claims are not independently proven. Net realized revenue per 1,000 qualified-human sessions **NOT COMPUTABLE** (no audited settled orders or denominator).
