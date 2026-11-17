# R429 — Canonical Gutenberg transport specimens, not WordPress posts

**HOLD / UNSENT / UNADOPTED.** Source master: [draft PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) at `d57ccdba3aee8f065e143e101c2945f4f3d01647`; release work: [draft PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201); owner [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); merchant owner [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). This branch stacks on #2896; it DOES NOT adopt R426/427/428 replacements.

## What this changes
Six WordPress Gutenberg **block-body source specimens**, built deterministically from the six canonical Markdown letters, plus the safety generator, a native Node source-parity test, and machine-readable manifest. These specimens help a human see how the exact canonical bodies might be transferred into a WordPress post editor after approval. **They are not WordPress draft posts; none were uploaded to WordPress.** Native Jetpack email HTML rendering, sender headers, true email preheader, postal address, unsubscribe, recipient list and welcome receipt are still untested. A static WordPress block specimen proves none of those.

Each source is prefaced by a prominent **DO NOT PUBLISH OR EMAIL** paragraph and followed by unresolved postal and unsubscribe tokens, preserving the deliberate release hold. Commercial 03/05 CTA remains plain inert text with no earning URL; any first-party links to existing free articles remain intact. Every source retains the canonical original copy; the out-of-date Issue 04 subject ('Fourteen seconds') and the duplicate Issue 01/02 destination are preserved and explicitly flagged—not silently repaired. Previous **UNADOPTED** corrections are in #2886 and #2891. Official merchant claims and new alternatives remain unadopted in #2896.

## Build/test (without WordPress access)
`node dispatch/r429/render_gutenberg.cjs` compares saved Gutenberg bodies to the exact original Markdown at the branch's inherited `dispatch/campaign-2026-mind/` directory. `node dispatch/r429/test_gutenberg.cjs` tests all six, metadata fidelity, internal links, inert merchant placement, hard-stop legal tokens, no active content and tamper rejection. **These code tests are source-format checks only.** A passing source test must NEVER turn on WordPress's 'Send this post to subscribers' checkbox.

## Release blockers in the real transport
1. **Founder:** approve exact final edition, recipient segment, actual business postal address, issue-by-issue date, final sending and whether publishing a post is permitted. The approved pilot is *draft only*.
2. **Mind & Affiliate:** written FINAL VESTIGE-specific merchant account acceptance, explicit EMAIL permission, exact Zen12/Total Focus SKU, earning-link format, current checkout/refund/price, authorized creatives and LIVE approved guides before issues 03/05 could have real CTAs. No commercial activation from public catalog alone.
3. **Focus/Claude:** provider-confirmed eligible addresses deduplicated privately; real welcome+Fieldbook receipt witnessed without exposing addresses. Distinguish WordPress Reader-followers from email opt-ins; frontend PDF unlock is NOT confirmation.
4. **Dispatch/Founder:** authenticated WordPress post-editor **non-sending Preview email** on desktop, tablet and mobile with send toggle OFF; verify the actually rendered unsubscribe and sender's valid FV physical postal address. A native preview alone is NOT a real inbox receipt; any real test email requires explicit founder authorization. Do not insert legal placeholders into a public post.
5. **Claude analytics/Praxxis:** first-party asset_id to qualified-human visit to relevant CTA to provider-confirmed lead to verified merchant-paid order/commission minus refunds/fees in 7/30-day cohorts. Never equate clicks, opens or impressions with revenue. No duplicate scripts.

## Actual read-only provider snapshot (2026-11-17 18:33 UTC)
Jetpack newsletter ON; new-post auto-email default OFF; email_content_format=full; welcome includes the Focus Fieldbook. Newsletter status total=3, confirmed=3, unconfirmed=2; separately WordPress Reader followers=3, direct-email followers=0. These counts are **not additive**; actual distinct deliverable receiving identities UNKNOWN. Most recent five post notices explicitly `never_sent_opted_out`; lifetime sends UNKNOWN. The public pages still promise notification 'when we publish,' despite the default OFF. This is unresolved copy/cadence trust QA. Source: authenticated WordPress read-only connector.

## Official check links
- https://wordpress.com/support/newsletter/send-newsletter-emails/ — post-based newsletters and per-post opt-in
- https://wordpress.com/support/newsletter/email-appearance/ — non-sending Preview versus sending a test email
- https://wordpress.com/support/newsletter/disable-newsletter-emails/ — per-post and default controls
- https://zen12.com/about — seller's 12-minute equivalence is NOT independently verified
- https://zen12.com/secret/ — different sales context, not an authorized FV offer
- https://hypnosislive.com/mental-skills/total-focus — specific audio; product assertions not third-party validation
- https://hypnosislive.com/faq — refund limits (14 days and max five sessions/year)
- https://pubmed.ncbi.nlm.nih.gov/37205669/ — a binaural beat research review does not test Zen12
- https://finalvestige.com/editorial-standards/ — primary records, uncertainty and independent commercial conclusions

**Outcome:** six faithful block-source specimens; zero WordPress writes, zero email or test-send, zero new signup list, no social queue edits, no affiliate links, no assumed sales. No improvement to commercial conversion has been measured.
