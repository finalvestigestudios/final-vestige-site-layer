# R263 — source-of-truth inbox and private subscriber verification

**Read-only today.** WordPress Newsletter returned subscriptions true, auto emails false, format FULL, sender Final Vestige Studios, no-reply, and a configured 52-page Focus Fieldbook welcome at 2026-11-10 19:35 UTC. Recent post sends indicate `never_sent_opted_out`. Diagnostics total3/confirmed3/unconfirmed2, separate Jetpack email followers0 and WordPress.com followers3; do not add, subtract or call these an accurate recipient roster.

Read-only connected Gmail searches found a 2026-10-25 `Confirm your subscription` request but not a final welcome/Fieldbook message. Targeted 2026-11-10 searches for the Fieldbook phrase also produced no matching message. A confirmation request does not establish the confirmation click or actual welcome delivery; unsuccessful searches do not establish nondelivery to every possible recipient.

**Verification sequence (not permission to send):**

1. An authorized operator privately opens the actual `Email subscription: Subscribed` status filter, records only aggregate and timestamp (redact identities), reconciles WP.com Reader follows and unconfirmed requests without exporting emails.
2. Inspect server/provider event origin and unique identifier to decide whether a consented confirmed_signup exists. Explicitly disqualify Fieldbook download, subscribe query parameter, a request email, a click or an unconfirmed subscriber row.
3. Only if already exposed without toggling send, view native WordPress composed-email preview for one *unsent* draft; check subject, preheader, full content, clear offer disclosures, CTA, mobile widths and native footer. An editor HTML preview is not proof of received MIME.
4. After **separate final founder authorization** to perform a controlled real email test, use the existing R258 received-message MIME inspector; check visible actual Final Vestige valid postal address, true opt-out mechanism and whether it functions in a safe test context. Never unsubscribe a real user's address.
5. Report pass/fail evidence (no subscriber identities), and maintain all six as HOLD_UNSENT absent full explicit founder approval. One real verified independent merchant commission, net of fees/refunds, is the monetization proof—not clicked links, opt-ins or purported A/B uplift.

No new emails, signup tests, vendor signup, list imports, WordPress writes, analytics vendors or account spending were performed.
