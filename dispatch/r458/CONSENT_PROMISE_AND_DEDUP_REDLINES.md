# R458 · Consent-promise, duplicate-signup, and offer-eligibility correction handoff

**State:** Founder review only. No live WordPress changes or newsletter settings changes. WordPress pages inspected read-only November 18, 2026: [The Dispatch / ID 523](https://finalvestige.com/dispatch/) (modified Nov 5), [Focus / ID 1579](https://finalvestige.com/focus/) (modified Nov 16), [Editorial Standards / ID 17](https://finalvestige.com/editorial-standards/) (last reviewed Aug 23). Existing newsletter settings: enabled, can send, `email_new_posts_by_default=false`, `email_content_format=full`, `reply_to=no-reply`, welcome content configured with 52-page Fieldbook PDF. Five recent post notifications are `never_sent_opted_out`.

## P0: expectation versus delivery

Current Dispatch masthead: **“New investigations and archive finds by email, when we publish them.”** Current welcome: **“You'll hear from us when there's a new Final Vestige investigation or a worthwhile find from the archives.”** Neither is a confirmed cadence with automatic new-post notification disabled. Selected manual sends could occur in future, but none of the last five did. **Proposed replacement**, without promises of every post:

> The Dispatch brings selected historical investigations, archival finds and careful looks at perception to your inbox occasionally. We do not email every new article. Subscribe once for access to the free 52-page Focus Fieldbook and future editions, subject to email confirmation.

**Proposed welcome sentence if founder approves an eventual WordPress edit:** “We'll send selected Dispatch editions from time to time, not an automatic email for every post.” Do not claim a successfully received welcome until a consenting witness supplies evidence.

## P0: avoid duplicate consent attempts

Current Focus troubleshooting tells readers who cannot open a PDF from a social-app browser to **“sign up again.”** This can create needless repeat attempts, obscure the distinction between pending confirmation and already-confirmed membership, and impair `confirmed_signup` attribution. **Proposed troubleshooting replacement:**

> If the PDF does not open, try opening this page in Safari or Chrome. If you already subscribed, check your confirmation or welcome message for the original download link; you do not need to submit the form a second time. If you never received a message, check spam and your email address, then use the contact page for help rather than repeatedly subscribing.

On the actual subscriber form, display a modest expectation line: “One list. Confirmation may be required. Occasional emails, with an unsubscribe option.” Only publish after confirming what the Jetpack form and welcome really do.

## P0: proof of confirmed signup

Contract: `confirmed_signup` is a single private server/provider-grounded transition from a pending subscription to eligible/confirmed status for a **new** recipient on the existing Jetpack list, with proof timestamp. NOT a form submit, Reader follow, welcome configuration, PDF download, repeated signup attempt, or a fabricated client-side click. Deduplicate in a private internal join keyed by provider subscriber identity + confirmation event, not raw public emails or publicly exposed hashed emails. One event per transition. Keep all subscriber-identifying fields in the authorized provider system, not GitHub. When provider APIs cannot prove the transition, report `unknown`, never infer from count changes.

Provider surfaces disagree: Newsletter confirms 3 eligible records and separately reports 2 unconfirmed (do not add these as a clean total); Stats Subscribers email3/Reader0 conflicts with Stats Followers email0/Reader3 (partial=false). Escalate for first-party interpretation and do not use an arbitrary surface as a unique-human or new-acquisition KPI.

## P1: paid-order conversion only after authority

Primary candidate **Zen12** only (reserved commercial Issue 03); source-aligned materials from [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171) remain DRAFT, not live. This candidate has no named Final Vestige affiliate acceptance, EMAIL-channel authorization, earning URL, eligible SKU, current checkout/refund verification or independently reported settlement. [Seller's standard page](https://zen12.com/about) advertises 12-minute, 12-level MP3 sessions and strong outcomes; [separate promotional funnel](https://zen12.com/secret/) may show time-varying offers. Do not borrow prices, urgency or scientific claims. Hypnosis Live Issue 05 remains reserved and independently blocked. Vendor consumer marketing messages—including the Nov 13 Zen12 gift email—are NOT proof of publisher approval. FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

## Handoff ownership

- **Founder:** select any text substitution; provide and authorize genuine FV business postal-address evidence; final approve every post/send separately.
- **Claude / Focus:** check existing public form flow and free PDF delivery without creating a new platform; implement dedup only when appropriate consent and approved engineering access exist; no parallel tracker.
- **Dispatch:** compare actual Jetpack preview (non-sending), footer and opt-out to source; create review-only manuscripts, never publish.
- **Mind #171:** verify account-specific partner EMAIL permission, approved SKU and first-party LIVE warm-up guide before any commercial CTA can be enabled.
- **Grok/Praxxis TASK-008:** preserve creator-owned social assets; use source-tagged landing pages once approved. Dispatch does not post to social.

**Evidence state:** BUILT = these proposals and offline copy; TESTED = source and text consistency only; LIVE = original WordPress pages and configured Jetpack list; VERIFIED DELIVERY / PAID SALES = neither. Realized net revenue per 1,000 qualified humans is NOT COMPUTABLE without audited qualified-human sessions and merchant/first-party settlement, fees and refunds.
