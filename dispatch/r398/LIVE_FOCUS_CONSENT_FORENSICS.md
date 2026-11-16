# R398 evidence: gift panel may appear without a confirmed email signup

**Evidence class:** `LIVE_SOURCE_READ` + `NATIVE_OFFLINE_VM_TEST`; **not a live browser interaction or observed false analytics event.** Read-only WordPress page `/focus/` (published, last modified 2026-11-05 17:44:02). Inspected 2026-11-16 ~10:36 UTC. No form submitted; no addresses read.

## Exact relevant source behavior

The bottom inline script (captured in `focus_live_js_excerpt.txt`) reads `URLSearchParams(window.location.search).get('subscribe')`. If any nonempty value **other than** `invalid_email`, `error`, `blocked_email`, `opted_out`, or `blocked` is present, it calls `show()`, setting `#fvf-gift.hidden=false`. Independently, if a Jetpack subscriptions container's classes include `is-subscriber`, it also shows that panel.

The panel currently reads **“Your fieldbook is ready to download”** and contains an honest note **“Please confirm your email to join The Dispatch.”** But its PDF CTA includes `data-fv-event="focus_pdf_click"` and `data-fv-location="after_signup"`. The script is not a Jetpack authenticated confirmation/eligible-inbox lookup; the “after_signup” location can therefore be a misleading *journey label* if analysts or a tag consumer elevate it into `confirmed_signup_v1`. There is no evidence here that the website actually does so. The PDF is a free, useful resource and must remain accessible without implying purchase.

### Falsification reproductions (native Node VM)

The captured **exact script excerpt** was run locally in a tiny simulated document with no network calls, no actual form and no WordPress mutation. `?subscribe=not_real_confirmation` revealed the gift, as did `?subscribe=anything_at_all` and an `is-subscriber` class. The denylisted `?subscribe=blocked` did not. Five source-behavior tests passed. These observations establish source behavior under the simulated inputs, **not** actual production conversion events.

### Consequence for metrics and trust

- `focus_pdf_click`, fieldbook display, `subscribe` query tokens and WordPress Reader membership are useful UX activity but **not `confirmed_signup_v1`**.
- Jetpack confirmed subscriber counts (3), unconfirmed (2), and WordPress.com follower counts have different meanings. WordPress's own support says “Not confirmed” people are not included in total; “Not subscribed,” “Bounced,” “Emails paused,” and “Not sending” can still be readers/followers. Actual distinct eligible email inboxes are **unknown**.
- Only a **fresh, authenticated provider read** of a unique email-eligible subscription after confirmation, with a durable dedupe key and consent record, can unlock a confirmed signup event. There is no such authenticated per-subscriber evidence in this sprint.
- Source-level frontend property `source_verified:true` cannot be trusted merely because the browser provides it. The test-only gate documents the required server-side trust boundary; integration remains Claude's responsibility.

**Suggested fix:** Show the genuinely free download as a public resource with transparent wording; label its click `focus_public_download`, never `after_signup`, and remove the URL/class-based inference. Track separately verified confirmed signups only through an authoritative server-side Jetpack event and deduplicated consent record. Founder + Claude decide and independently QA before any CMS write.

Sources: [WordPress subscriber statuses, last reviewed November 4 2026](https://wordpress.com/support/subscribers/); [Focus page](https://finalvestige.com/focus/); [Fieldbook and welcome owner #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129); [R398 test source](tests/live_focus_ui.test.mjs).
