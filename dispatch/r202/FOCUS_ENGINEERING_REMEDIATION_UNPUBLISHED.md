# R202 — Focus client-side gift display is not an opt-in signal

**Observed 2026-11-07 21:31 PT** via authenticated, read-only WordPress page #1579. Source last modified 2026-11-05T17:44:02; this is a developer proposal, not a production change.

The `fvf-gift-v2` script currently checks `new URLSearchParams(window.location.search).get('subscribe')`, and calls `show()` whenever the value is nonempty and not in `['invalid_email','error','blocked_email','opted_out','blocked']`. It also shows the panel when a client-side Jetpack container acquires the `is-subscriber` class. Both cause the download panel to become visible; **neither establishes an authoritative confirmed email subscription**. Reproduction of the *branch logic* (not a WordPress server transaction): `?subscribe=anything`, `?subscribe=pending`, `?subscribe=1` all show the gift panel. The panel itself currently tells readers to confirm by email; it does **not** explicitly assert that they have joined. The defect is **conversion-inference ambiguity and weak state semantics**, not evidence of fraudulent subscribers.

The WordPress REST-rendered page content includes a Jetpack Subscribe block fallback anchor to `?post_type=page&p=1579` rather than a fully hydrated email form. This is **NOT** proof the public browser widget is broken; live browser widget initialization must be inspected separately. The published public page has an email input on text extraction. On /dispatch/ page #523, REST content similarly includes a Subscribe-block anchor. Both are legitimate QA targets for Claude.

## Smallest safe remediation candidate (Claude engineering owner, review only)

1. Distinguish **gift availability** from **email confirmation**. The PDF remains a free gift and can be downloadable without proving consent. Set the panel title to `Your Fieldbook is available`, and make the confirmation instructions explicit. Do not use a query parameter or CSS class to emit `confirmed_signup`.
2. Never fire `confirmed_signup` in browser code based on `subscribe=` or `is-subscriber`. A trusted server-side/provider adapter must check `Email subscription = Subscribed`, an observed provider consent transition, suppression/unsub status, and a *private* idempotency key. No emails, names, or per-recipient hashes may appear in page URLs, public events, or GitHub.
3. Use only the existing Jetpack list; no platform migration, import, or duplicate tracking script. Every transition has a private, access-controlled proof reference. Repeat submissions, Reader-only follows, unconfirmed requests and opt-outs must yield **zero** new confirmed-signup events.
4. Confirm mobile (320/360/390/768 px), keyboard, no-JS, reduced-motion and direct-PDF behavior on isolated staging. Compare public live DOM versus WP REST content before alleging widget failure.
5. Keep production content and the already-functional 52-page welcome message intact. Any page edit/analytics write requires the founder's separate authorization.

### Candidate microcopy (not approved or published)

Before confirmation: **Your Fieldbook is available to download. If WordPress asks you to confirm your subscription, please use the link in your email to join The Dispatch.** On confirmed proof: **Your newsletter subscription is confirmed. The welcome email contains this same Fieldbook link.**

### Acceptance matrix

| Fixture / transition | UI gift | `confirmed_signup` event |
|---|---|---|
| Direct PDF request | Download allowed | Never infer |
| `?subscribe=anything` | May display gift | **Never** |
| CSS `is-subscriber` | May display gift | **Never** |
| Pending/unconfirmed provider | Show confirm instructions | **Never** |
| WP Reader follower (not email subscribed) | No assertion | **Never** |
| Provider pending→email subscribed, affirmative consent, non-duplicate | Confirmed copy only if verified | One only after trusted provider event |
| Duplicate confirmation | No duplicate | **Zero additional** |
| Unsubscribed / suppressed | Do not imply eligibility | **Zero** |
| Received Fieldbook welcome | Delivery evidence only | **Not a substitute for provider consent** |

**Caveat:** The `focus_ui_audit.cjs` test uses a synthetic excerpt of observed script text, not a full visual WordPress transaction. Need a safely authorized QA browser and eligible provider evidence to verify the actual funnel. Original campaign and WordPress were not modified.
