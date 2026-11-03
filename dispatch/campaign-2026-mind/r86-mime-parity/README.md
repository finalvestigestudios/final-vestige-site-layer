# Dispatch R86 — received-email MIME parity and compliance evidence

**2026-11-03, 00:36–01:00 PT · DRAFT ONLY · NO SEND · NO WORDPRESS WRITE · NO MERCHANT ACTIVITY**

Owner: [Dispatch Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Partner owner: [Mind Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Original six manuscripts are untouched in [draft PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) at exact head `d57ccdba3aee8f065e143e101c2945f4f3d01647`; first independent per-edition gate [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) remains untouched. R86 is deliberately stacked after [R85 #748](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/748) and changes **no existing file**. Homepage PR #49 is untouched.

## A specific remaining weakness in prior email inspection

R85's useful offline parser returns independent indicators for the **HTML and plaintext combined** (e.g. a commercial disclosure can come from `text/plain` while the visible `text/html` version has none). This is a potential false reassurance for HTML-reading subscribers. Similarly, a legitimate footer or CTA may exist in only one MIME alternative, or an HTML advertisement's disclosure might appear only after the offer. This is not proof R85 has ever incorrectly approved a send: R85 always returns a HOLD decision, and no real received Jetpack email has been inspected.

**R86 specifically inspects each MIME rendition separately**, then demands consistency for one first-party CTA, a commercial disclosure both early and preceding/near the link, the supplied publisher-postal string, and visible unsubscribe instructions. It also checks the actual delivered subject against the editorial-approved title and treats unsubscribe headers as **indicators, never functionality**. Missing variants are flagged rather than guessed. Every report, including a spotless synthetic report, returns `HOLD_UNSENT_REQUIRES_HUMAN_VERIFICATION`.

R86 is source-controlled as `audit_render_parity.py` with 28 synthetic-only adversarial unit tests and this runbook. **Never commit, attach to a public issue, or paste a real received .eml, valid unsubscribe token, subscriber address, publisher's private street address, partner referral URL, credentials, or private buyer data.** If a received test email is eventually authorized, inspect privately in a protected local environment.

## Current authenticated evidence — 2026-11-03 08:37 UTC

- WordPress blog **256784396**, Jetpack Newsletter `subscriptions=true`, `site_can_send=true`, and **`email_new_posts_by_default=false`**, which is a *post-editor default*, not a global send prohibition. The email format is **excerpt**, sender name "Final Vestige", reply-to `no-reply`, featured image/date on. The 52-page Focus Fieldbook **welcome body is configured**, but genuine delivery is unverified.
- Five individually published noncampaign post records 1917, 1920, 1922, 1924, 1926 are each `never_sent_opted_out` with no dispatched timestamp. This demonstrates **five known non-sends**, not no other sends ever.
- Newsletter diagnostics: **total=2, confirmed=2, unconfirmed=2**. Separate Jetpack follower stats: **email=0, WordPress.com=2, total=2, partial=false**. Counters are *not additive*. **Actual email-eligible recipients = UNKNOWN**; no names/addresses exported.
- [Dispatch signup](https://finalvestige.com/dispatch/) promises new investigations/archive finds and the Fieldbook; [Focus signup](https://finalvestige.com/focus/) states occasional recommendations may earn commissions. These are **two entrances to the one Jetpack list**. Alignment copy is proposed in previous PRs, not approved/published.
- [Editorial Standards](https://finalvestige.com/editorial-standards/) require primary-source checking, visible uncertainty, and honest commercial disclosure. No verified FV-owned physical mailing address, native rendered email, actual received test, unsub functionality, or final send authorization exists.
- Read-only connected Gmail query found only the October 25 WordPress confirmation and **no verified Final Vestige welcome receipt or product-specific affiliate email permission**. Automattic's address on that confirmation is **not** the publisher's mailing address.

## Exact merchant-page drift/claims — observed November 3, 2026, nonpromotional review only

| Reserved issue | Exact official seller page | Observed product-specific seller claims/terms | Permissible editorial interpretation |
| --- | --- | --- | --- |
| 03 Zen12 | [zen12.com/hnp](https://zen12.com/hnp) | Advertises 12-minute MP3 sessions, 12 levels, four styles; states a session equals an hour's advanced meditation and promotes wellbeing/brainwave benefits. | Session length, levels and styles are seller-described features; hour-equivalence, disease/health or brainwave-outcome assertions are **not independently proven for this product**. No pricing or refund representation authorized. |
| 05 Total Focus | [hypnosislive.com/mental-skills/total-focus](https://hypnosislive.com/mental-skills/total-focus) | Shows **33-minute/47 MB** recording; page simultaneously lists **$24.44 standalone / $29.95 list** and an optional two-title bundle at **$39.90** ($19.95 per title), plus a seller-stated **14-day refund**. Claims brain reprogramming, exceptional concentration and 100% focus. | Seller display snapshots are **not** an approved promotion, guaranteed checkout price or verified refund fulfillment. Never imply specific concentration outcomes, use outdated headline prices, or conflate a bundle with the standalone offer. |

Neither seller's public sales page proves Final Vestige accepted affiliate status, email-marketing rights, affiliate link format, approved creative, PII practices or permission to promote product-specific claims. Mind Studio's [draft PR #750](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/750) has an additional **unpublished** Zen12 guide; it is **not** an allowed live CTA. Both guide destinations are unapproved and non-live. Issues 03/05 remain `HOLD_MERCHANT`. The campaign preserves **4 editorial / 2 commercial-reserved** slots.

## Running R86 privately only after a separately approved test receipt

```bash
python dispatch/campaign-2026-mind/r86-mime-parity/audit_render_parity.py \
  --eml /outside-git/private/authorized-jetpack-received.eml \
  --subject 'The exact approved WordPress post title' \
  --cta 'https://finalvestige.com/exact-approved-first-party-article/' \
  --commercial \
  --publisher-postal 'Verified lawful publisher postal address, supplied privately'
```

Only use `--commercial` for #03 or #05; otherwise omit. The sample is a command **shape**, not a real test receipt. The CLI's report lists booleans/enum warnings and **never** echoes the full subject, address, subscriber identity, unsubscribe token, destination URL or body. Reports must remain aggregate and local. The parser deliberately cannot detect every CSS rendering trick, responsive email-client substitution, client preview text, blocked images, mailing-address *ownership*, unsubscribe functionality or email promotion permission. A real human still must review the authorized email in major inbox clients and verify opt-out by authorized procedure.

```bash
python -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test_r86_render_parity.py' -v
```

The original six Python tests on PR #175 were already independently checked out in the successful R85 hosted runner (see [workflow #41598018447](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41598018447)); no claim is made here about a new direct local checkout of that private SHA. New R86 tests and whole-suite CI must be independently observed on the exact resulting R86 commit; no pass numbers should be reported until they are actually observed.

## Editorial and attribution guardrails

Weekly six-issue original campaign remains a draft, **not scheduled**. WordPress post title—not a standalone preheader field—drives subject. The site currently delivers excerpts; no R86 static asset is a real Jetpack preview. Publish no buyer-guide link in issues 03/05 until the Mind owner attests a vetted LIVE first-party destination and separately verifies affiliate approval and email promotion permission. Disclose commissions in the same commercial issue **before/next to** any commercial guide or buying reference even if only the excerpt is emailed. Never call a seller statement an independently established effect.

Source: [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires truthful headers/subjects, visible ad identification when commercial, a **valid physical postal address**, clearly available opt-out and timely honoring of opt-outs; [FTC Endorsement Guides FAQ](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking). [WordPress Newsletter guidance](https://wordpress.com/support/newsletter/send-newsletter-emails/) reviewed October 19, 2026: native post-editor preview and real test email are separate actions; individual per-post email sending can be enabled even while new-post default is off.

**Launch status:** Editorial 01/02/04/06 = `HOLD_UNSENT`; commercial 03/05 = `HOLD_UNSENT + HOLD_MERCHANT`. Conditions to clear only after independently verified: real qualified publisher postal address; precise consent-eligible audience and opt-out flow; approved native Jetpack excerpt/full MIME preview; **separately approved** real test message and receipt; product-specific affiliate email rights and published approved guides; explicit founder signoff on exact content, audience, date/time. No send, test-send, draft/post creation, WordPress settings change, subscription contact/import, affiliate activation, merchant outreach, CI-to-production or PR merge has been authorized or performed.
