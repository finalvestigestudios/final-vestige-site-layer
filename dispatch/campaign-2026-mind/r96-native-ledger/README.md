# Dispatch R96 — live native delivery ledger, not a send (2026-11-03)

**Status: HOLD_UNSENT (01–06); HOLD_MERCHANT (03 and 05).** Owner: [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); commercial coordination: [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). This is an additive evidence-only stacked change on [R95 draft PR #819](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/819). Original six-issue [master draft #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), [per-edition safety PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), original 4:2 editorial mix, homepage and frozen #49 remain untouched. No mailing-list/WordPress/content/merchant mutations or outreach.

## What changed in our understanding of WordPress

A fresh **authenticated, read-only WordPress Jetpack newsletter status call at 2026-11-03 18:36:42 UTC** returned **five delivery-status records**, NOT an empty `recent_sends` array. All five explicitly say `never_sent_opted_out`, `dispatched_at=null`, `recipients=null` and the WordPress failure reason `send_subscription flag is false`:

| Existing WordPress post ID | Delivery status | What is actually established |
| --- | --- | --- |
| 1926 | never_sent_opted_out | This post did **not** send to the list |
| 1924 | never_sent_opted_out | This post did **not** send to the list |
| 1922 | never_sent_opted_out | This post did **not** send to the list |
| 1920 | never_sent_opted_out | This post did **not** send to the list |
| 1917 | never_sent_opted_out | This post did **not** send to the list |

**Correct statement:** Five records, zero *successful sends among those five records*. Do **not** say “zero historical sends” or “there are no newsletter delivery records.” These five records refer to already-existing public posts, **not campaign issues 01–06**. `site_can_send=true` means technical capability, never permission to publish or contact anyone. All original draft campaign issues remain outside WordPress publishing.

Newsletter settings from 18:36 UTC: `subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, sender display name `Final Vestige`, `reply_to=no-reply`, featured images enabled and welcome message configured with the real 52-page Focus Fieldbook URL. These are **configuration**, not a genuine received HTML/plaintext email, delivery receipt, verified preheader, branded reply-to, footer or opt-out.

Counters from the same live diagnostic: `total=2`, `confirmed=2`, `unconfirmed=2`, `suppressed=0`. A second, distinct authenticated **followers endpoint** at the same sprint reports `total=2`, `email=0`, `wpcom=2`, `comment=0`, `partial=false`. The counts are not four humans; unconfirmed and confirmed should not be added. Reader followers are **not** verified newsletter email recipients. The exact *email-eligible* audience is **UNKNOWN**, including whether its effective size is zero. Never enumerate or print subscriber identities.

## Human-only evidence workflow, prioritized

1. **Native WordPress delivery/preview:** The official [WordPress.com email appearance guide](https://wordpress.com/support/newsletter/email-appearance/) (last reviewed October 6, 2026) explains that the per-post “Send this post to subscribers” toggle makes **Preview email** and **Send test email** controls visible. Those are different actions. **Do not enable the toggle, send a test, create a post, schedule or publish under this authorization.** In a separate founder-approved, isolated dry-run, an owner must capture the genuine native preview and, if explicitly separately authorized, a received test message with its HTML and plaintext formats, source metadata, link destinations, sender, physical mailing address, subscription management/unsubscribe behavior and any conditional sender requirements. Preview alone cannot establish actual inbox delivery or unsubscribe functionality.
2. **Recipient eligibility:** In authenticated WordPress administration, compare the *Email subscription* filter and its confirmation/suppression/paused/bounce states against Jetpack follower stats, without copying contact details into Issues, PRs, screenshots, fixtures, logs or email. Resolve why two confirmed plus two unconfirmed are reported under a total of two and why the follower endpoint shows zero email followers. Record only reconciliation method, totals and date. A public confirmation email or Automattic address is not a Final Vestige newsletter-delivery certificate.
3. **Commercial legal footer:** Identify and validate a **Final Vestige** qualifying physical postal address. The merchant's UK address, Automattic's corporate postal address and a generic privacy-policy link are not substitutes. Inspect a real received message to determine what Jetpack appends; verify a working recipient opt-out and whether any physical-address requirement is actually met. The [FTC CAN-SPAM business guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) notes that covered commercial emails can include promotions of content on commercial sites, and requires honest header/subject, ad identification when applicable, a physical address, functional opt-out and timely honoring. A first-party “read the review” CTA is not an exemption from assessing the email's primary purpose.
4. **Vendor authorization (Mind owns the guide and link):** Get signed-in, named Final Vestige approval for **each product** and explicitly **EMAIL** promotion, exact permitted first-party-guide-to-merchant journey, approved tracking-link/creative rules, actual seller checkout tier/price/refund terms and privacy-safe aggregate-only reporting. Neither general consumer marketing emails, affiliate signup pages nor the public sales page establishes that permission. Guide draft PRs [#813](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/813) (Zen12) and [#822](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/822) (Total Focus) remain unpublished, without approved live URLs.
5. **Claims and post/excerpt QA:** [Zen12 official page](https://zen12.com/hnp) markets “hour in 12 minutes” and other efficacy assertions; these are not independently proven for Zen12. [Total Focus exact page](https://hypnosislive.com/mental-skills/total-focus) describes 33 minutes/47 MB and shows variable bundle pricing and strong concentration promises; the [official FAQ](https://hypnosislive.com/faq) has generic 40-minute/~$22.95 descriptions and a **five-refund-per-year** restriction missing from the brief product-page pitch. No fixed price, implied clinical efficacy, risk-free unconditional guarantee or made-up testimonial in the newsletter. Compare published article, native post title, manual excerpt, native read-more permalink and in-email HTML/plaintext disclosure; no assumptions about a separate preheader field.
6. **Founder release:** Final review must cover exact six subjects, post titles, manual excerpts, original source links, the four-editorial/two-reserved-commercial cadence, audience definition, dates and explicit permission to send. Nothing here grants any such permission.

## Machine-checkable result (offline only)

`wordpress_2026-11-03.json` contains **aggregate counters and five non-send metadata rows** with no addresses, token, PII or subscriber identities. `delivery_truth.py` reads that dated fixture and the untouched six-issue master `manifest.json`. It refuses altered source timestamps, invented recipients/sends, audience category changes, any false-to-true launch attestation, unauthorized partner link activation, campaign rescheduling and personal data injection. It always reports `HOLD_UNSENT`. This code contains **no network, WordPress access, email, publication or live tracking functionality**.

For review in a local repository checkout:

```sh
python -I dispatch/campaign-2026-mind/r96-native-ledger/delivery_truth.py
python -I dispatch/campaign-2026-mind/r96-native-ledger/delivery_truth.py --html > /tmp/dispatch-r96-review.html
python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_r96_native_send_ledger.py' -v
```

The HTML is an **accessible static reviewer**, NOT a genuine Jetpack HTML/received email. The Python suite is not an audit of real delivery. The fixture is a 2026-11-03 point-in-time snapshot; if the live values change, collect **new evidence** and add a separately dated file rather than mutating it to assert send readiness. No sender address or subscriber details should be uploaded to GitHub.

**Current release decision:** editorial issues 01,02,04,06 = HOLD_UNSENT; product slots 03 Zen12 and 05 Total Focus = HOLD_UNSENT + HOLD_MERCHANT; no test emails, real emails, WordPress edits, subscriber imports, settings changes, direct affiliate links, prices or promotion scheduling authorized.
