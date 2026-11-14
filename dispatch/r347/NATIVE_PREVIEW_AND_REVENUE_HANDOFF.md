# Dispatch R347 — fail-closed native-preview & sales-proof handoff

**Scope:** future instructions, NOT executed. No WordPress write, post draft, send-test, recipient contact, live tracking or commerce activation is authorized by this runbook.

## Current authenticated read-only snapshot (2026-11-14 05:35 UTC)
- Jetpack enabled; new-post auto email default OFF; **full** content; reply-to **no-reply**; sender display Final Vestige Studios; can_send true is a **technical ability**, not permission to send.
- Subscriber status: total 3, confirmed 3, unconfirmed 2, suppressed 0. Source categories overlap. Jetpack followers: WordPress.com 3; directly listed email 0. **No eligible recipient total inferred.**
- Welcome setting links directly to the 52-page PDF, but receipt is not authenticated. The 2026-10-25 Gmail confirmation email is not that welcome. Latest targeted Gmail search found no Fieldbook welcome receipt. Do not expose email addresses.
- Five recently sampled post notification statuses are `never_sent_opted_out`. This does not prove no older send exists.

## Highest-priority NO-SEND authorization path
1. **Before writing to WordPress**, ask founder separately for permission to create *draft-only* post content (never publish) and to examine Jetpack's editor Preview email. Not granted here. Preview is documented without sending; distinguish from **Send test email**, which is NOT authorized. https://wordpress.com/support/newsletter/email-appearance/
2. If specifically authorized: create a private editor draft with the per-post 'Send this post to subscribers' toggle OFF; do not publish. Open **Preview email** only. Capture desktop, tablet and narrow mobile view, subject/title, proposed intro vs actual preview, disclosure placement and links. Do not infer proposed standalone preheader is supported.
3. A *received-email* test requires fresh specific permission, controlled owner inbox, verified opt-out and publisher postal footer. It was not performed. Preview cannot attest that a real opt-out endpoint works.
4. Founder must supply a **valid business postal address** or legally qualifying P.O. box/CMRA location, outside public GitHub until publication is explicitly approved. Never use Automattic, Hypnosis Live, home-address guesses or placeholder text.
5. Reconcile with authoritative provider account, privately: total_unique_by_provider, confirmed-by-email-channel, WordPress.com followers, opted_out, suppressed, and timestamped opt-in confirmation. Aggregate results only, no subscriber PII in GitHub.
6. Verify the same signup's dedup key, double opt-in, and actual welcome/PDF receipt using a founder-authorized owner-controlled test path. No tests which contact the actual subscriber list.
7. Obtain named merchant acceptance, newsletter-EMAIL rights, issued earning link, claim review, real LIVE Mind first-party guide and checkout/refund verification from Mind/Commerce. An offline preview never turns a guide live.
8. After separately approved sends, Claude may use existing instrumentation to count one deduped `confirmed_signup` from a provider confirmation, source-tagged CTA landings and settled orders. `utm_source=dispatch&utm_medium=email&utm_campaign=mind_pilot_2026_11&utm_content=issue05` is **proposed**; do not deploy and do not override Grok's acquisition UTMs.

## Evidence hierarchy
- BUILT = files exist in PR; TESTED = reproducible local static guard; LIVE = authenticated WP user-facing page; VERIFIED = external authoritative proof (e.g. actual merchant approval or payout).
- Net revenue/1,000 human-qualified sessions = 1000*(settled gross - refunds - fees)/qualified_human_sessions. If numerator or denominator unknown or sample too small, mark **NOT COMPUTABLE**, not zero.
- One primary editorial CTA in each email; source citations are evidence references, not second commercial CTAs.
- 4 editorial / 2 prospective commercial remains founder's draft allocation, not sending cadence approval.

## Priority owner decisions
| Offer → step | Blocker | Experiment / change | Pass/fail proof | Owner |
|---|---|---|---|---|
| Total Focus → first-party guide → merchant | Unapproved affiliate email rights and nonexistent LIVE guide | Check account-level permission & guide QA, no outreach | Merchant proof + reachable approved guide, otherwise FAIL/HOLD | Mind / Commerce |
| Focus → eligible subscriber | Counts conflict / no provider-level consent audit | Deduplicate actual provider confirmations with private audit | Aggregate dedup proof, otherwise UNKNOWN | Claude / Focus |
| Fieldbook → welcome | Delivery not proven | Founder-controlled inbox read after explicit approval | Actual message and PDF accessible, otherwise UNKNOWN | Founder / Focus |
| Dispatch → inbox | No received preview/address/unsubscribe | Use native preview under authorization; separately authorize receipt | Screen evidence plus functional opt-out and verified address, otherwise HOLD | Founder / Dispatch |
| Grok asset → customer | No authenticated paid conversion | Match real asset_id/UTM to independently settled order, deduct refunds/fees | Source-linked 7/30-day cohort, otherwise NOT COMPUTABLE | Grok / Praxxis / Claude / Commerce |
