# Dispatch R56 — Actual-message evidence gate (NO SEND / NO PUBLISH)

**Owner:** [Dispatch Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). Partner pages and link eligibility remain with [Mind & Affiliate Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). **Stack:** R55 [draft PR #539](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/539) (which itself descends from the original six-letter [draft PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), with independent per-edition gates in [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201)).

## Why this is different from the earlier 1,022 repository tests

Prior static boards, source-derived excerpt models and HTML files **cannot establish what a particular subscriber actually received**. R56 introduces a **local RFC 5322/MIME receiver-side evidence triage**. It can examine, *only after separate founder authorization*, a genuinely received Jetpack email that a human privately exports as an `.eml`. It reads bytes locally, performs NO network calls, then emits a report containing **booleans, safe counters and hold codes only**. It refuses to emit recipient addresses, raw From/To/Reply-To, HTML, the postal string, the unsubscribe destination/token or the input filename. Never commit the original email or a mailbox screenshot to GitHub.

The inspector cannot itself receive or send a message. It cannot prove that an unsubscribe link works, that a subscriber consented, that a physical address is legitimate, that the sending domain is authenticated, that a product offer is authorized, or that a particular email client's CSS visibly renders the notice. **All results remain HOLD_UNSENT**. Neither a parsed MIME message nor a green GitHub Action is CAN-SPAM certification.

## Read-only production facts independently retrieved on 2026-11-02 02:36 UTC

WordPress site **256784396**, Final Vestige; Newsletter `subscriptions=true`, `site_can_send=true`, `email_new_posts_by_default=false`, `email_content_format=excerpt`, `reply_to=no-reply`, sender display `Final Vestige`, `recent_sends=[]`. Welcome settings contain the **52-page Seven Day Focus Fieldbook** link; settings presence is **not proof of receipt**. Dashboard `total=2`, `confirmed=2`, `unconfirmed=2` are **nonadditive by documented WordPress semantics**: [WordPress Subscriber guidance](https://wordpress.com/support/subscribers/) explicitly says *Not confirmed* registrations are excluded from total. **The 2/2/2 arithmetic is therefore not itself contradictory**, although which counted subscriptions can receive email is still UNKNOWN. See [subscriber-counter reconciliation](SUBSCRIBER_COUNTER_RECONCILIATION.md) for the exact private next check. Do not infer four people, conduct a tiny-list A/B test or upload/export the list. Published [Dispatch](https://finalvestige.com/dispatch/) and [Focus](https://finalvestige.com/focus/) share the one Jetpack list. Dispatch signup currently omits the optional affiliate-relationship explanation already present at Focus; proposed clarification [R52 #517](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/517) is **not live**. [Editorial Standards](https://finalvestige.com/editorial-standards/) require original sources, transparent uncertainty and disclosed commercial relationships.

The configured `no-reply` behavior means **do not assume replying to the newsletter is an operational opt-out channel**. Independently verify the actual recipient-visible unsubscribe method.

## Exact execution contract

Run inherited tests **on an exact GitHub PR head** (not a stale local checkout):

```bash
python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v
```

For a **synthetic, non-delivered** local RFC 5322 specimen only:

```bash
python -I dispatch/campaign-2026-mind/r56-mime-evidence/mime_inspector.py \
    --issue 3 --eml /secure-local-path/synthetic-fixture.eml --source synthetic
```

**Only if the founder separately approves receiving, exporting and inspecting a real test email:** obtain the actual original message using a trusted mailbox's *Show original / Download message* function. **Never upload it to GitHub, share addresses/screenshots or provide its unsubscribe URL.** Set the legitimate Final Vestige postal-address string **privately** in the operator's local environment; never hardcode it, log it or put it in shell history. Then run:

```bash
python -I dispatch/campaign-2026-mind/r56-mime-evidence/mime_inspector.py \
    --issue 3 --eml /secure-local-path/received-original.eml \
    --source received --founder-authorized-read
```

Environment key: `FV_POSTAL_ADDRESS`. Absence gives a **false** postal-match result. The analyzer checks exact normalized string presence in a structural approximation of visible body text. A match does **not** certify that the address is valid. Store only redacted generated observations in the issue, not the original RFC 5322 bytes. Keep the raw mail in a private controlled location subject to the owner's retention decision.

### What the instrument can establish — and what it cannot

| Inspection | Source-level factual observation | Not proved |
| --- | --- | --- |
| `Subject` | Decoded subject matches canonical issue title | Jetpack supports a separate preheader field (it has **not** been verified) |
| `From` | Parsed **display label** equals “Final Vestige”; sender address never logged | Header authentication, SPF/DKIM/DMARC alignment |
| `text/plain` + `text/html` | Presence of bodies; basic visible-text approximation | Fidelity in Gmail/Outlook/Apple Mail, accessibility certification |
| Disclosure | Phrase appears in HTML-visible first 85 words / full body | FTC determination of primary purpose or sufficient conspicuousness |
| Postal | Exact private expected string occurs in approximate visible body | Valid USPS/CMRA address or proof it is physically readable to all clients |
| Unsubscribe | Candidate header or visible clickable HTTPS link exists | **Actual opt-out works**, honors within ten business days, remains active 30 days |
| Seller links | Number of direct Zen12/Hypnosis Live/Inspire3 destinations | A reader never saw a redirect or that publisher email permission exists |
| Images | Remote image count, **without loading images** | Tracking intent, client blocking behavior, privacy impact at send time |
| Release | Every issue is **HOLD**, 03/05 also **HOLD_MERCHANT** | Any permission to contact the list, publish or schedule |

This is a conservative HTML parser, **not an actual client visual renderer**. It detects common `display:none`, `visibility:hidden`, `hidden`, and `aria-hidden=true` cases but cannot fully execute CSS or identify all hidden/visible behaviors. It never clicks URLs. It must not be repurposed into a sender.

## Shortest accountable launch path (no action authorized by this PR)

1. Founder identifies an **actual valid Final Vestige business mailing address** (FTC permits registered USPS PO boxes or qualifying CMRA mailboxes); keep it in private production configuration, not a public PR, until inclusion approved. Automattic's address on the October 25 **subscription confirmation** is **not** Final Vestige's address.
2. Privately reconcile the two/two/two subscriber-count anomaly with WordPress support or a verified administrative breakdown. Record only eligible *number*, status semantics and source timestamp; never publish addresses.
3. Obtain a **separate explicit founder permission** for native Jetpack preview interaction and subsequently for one test recipient. WordPress documents that its **Preview email** control appears when the per-post **Send this post to subscribers** switch is ON; the global auto-post-send default OFF is not a guarantee against a mistakenly published per-post send. Do not toggle/send/publish/schedule in this branch.
4. With a separately approved test, check received original MIME and mobile screenshot privately. Verify sender identity, excerpt content, whether the proposed **custom post excerpt** appears, early commission disclosure in #03/#05, first-party CTA, actual physical address and usable unsubscribe. A private authorized human must **exercise** the opt-out flow in a controlled test and log only results, never tokenized URLs or email identities.
5. Obtain **written publisher-specific**, **named-SKU**, **EMAIL-channel** Zen12 and Hypnosis Live Total Focus permission, authorized earning link format, creative rights, current cart/refund applicability and correct published independent guides. Public [Inspire3 affiliate recruitment](https://affiliates.inspire3.com/) is not such permission. Seller ads at [Zen12](https://zen12.com/hnp) and [Total Focus](https://hypnosislive.com/mental-skills/total-focus) support seller descriptions (12-minute sessions; 33-min/47 MB MP3), **not** product-specific efficacy. Pricing displays have conflicted across captures: omit prices/guarantees from current email drafts.
6. Resolve editorial defects first: original #03 contains **two clickable seller citations** bypassing the intended independent guide; #05 must identify the *Total Focus* SKU accurately; both original manuscript disclosures fall outside the modeled 55-word fallback. [PR #187](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/187) contains **optional, uninstalled** custom excerpts with early disclosures; no silent substitution or WordPress changes.
7. Only after legal/content/list/product checks, request founder's **distinct final issue, audience and sending-date approval**. Four editorial / two conditional commercial composition remains unchanged. The homepage flagship stays first priority; frozen #49 is untouched.

## Trustworthy documentation

- FTC CAN-SPAM: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- FTC endorsements: https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking
- WordPress preview / test / per-post switch: https://wordpress.com/support/newsletter/email-appearance/
- WordPress send safety: https://wordpress.com/support/newsletter/send-newsletter-emails/
- WordPress excerpt fallback: https://wordpress.com/support/newsletter-settings/

**No actual test mail, WordPress mutation, partner message, affiliate link, analytics event, subscriber export, signup platform, charge, scheduling or publication occurred in R56.**
