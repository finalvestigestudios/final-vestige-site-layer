# R54 — Inbox boundary and manual-send interlock (DRAFT / NO SEND)

**Owner:** [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), aligned with [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). **Canonical creative:** [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175). **Inherited fail-closed readiness controls:** [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) and [PR #525](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/525). This folder adds a *distinct* delivery-boundary rehearsal rather than copying or replacing previous drafts, authority gates, received-MIME inspector, or founder copy options.

**Non-negotiable:** No WordPress post, subscriber contact, test email, scheduled send, site setting, merchant earning link, tracking code, new mailing list or account cost is authorized by this material. The six original issues remain four editorial plus two reserved commercial opportunities. **ALL SIX HOLD_UNSENT. Issues 03/05 additionally HOLD_MERCHANT.** Homepage priority #1 and frozen PR #49 are untouched.

## Evidence independently obtained in this sprint

On **2026-11-02 00:39 UTC**, authenticated read-only WordPress site **256784396** returned:
- Jetpack subscriptions enabled; site `site_can_send=true`; automatic new-post emails **OFF**; `email_content_format=excerpt`; sender display **Final Vestige**; reply-to **no-reply**; featured images and post dates in emails.
- Welcome template still contains the **52-page Seven Day Focus Fieldbook** link. That is *configuration*, not a verified received final welcome.
- `recent_sends=[]`, which establishes **no reported recent sends**, not zero lifetime deliveries.
- Subscriber diagnostic counts **total=2 / confirmed=2 / unconfirmed=2**, suppressed=0. This is **not** a deduplicated eligible audience. No subscriber identity or raw address was accessed or stored.
- Published `/dispatch/` page 523 lacks nearby wording about occasional commission-earning recommendations. Published `/focus/` page 1579 **already** includes it. Published `/editorial-standards/` page 17 requires transparency. The proposed correction in R52 PR #517 is still **uninstalled**.

Read-only connected-mailbox searches for new Final Vestige **Zen12/Total Focus** affiliate approvals, permitted EMAIL channel, and final welcome/received Dispatch evidence found no qualifying new result. Search failure is **not proof of a universal absence of permission**; the actual authorized partner account and received original message must be examined if available. The October 25 subscription **confirmation** is not a delivered Focus Fieldbook welcome or commercial email, and its Automattic return/footer address is not the Final Vestige publisher's physical mailing address.

## Why this is not just another copy-edit review

WordPress's current official documentation [Newsletter Settings](https://wordpress.com/support/newsletter-settings/) explains that when `excerpt` is selected **and a post has no custom excerpt**, WordPress falls back to the first **55 words**. The [Email Appearance](https://wordpress.com/support/newsletter/email-appearance/) guide says a post's custom excerpt replaces that introduction; the editor's **Send this post to subscribers** toggle must be turned ON for the native **Preview email** control to appear. The [Send Newsletter Emails](https://wordpress.com/support/newsletter/send-newsletter-emails/) guide (last reviewed October 19, 2026) says an individual post can send even when the sitewide automatic default is OFF. Publishing an existing post is not equivalent to preparing an email in a separate email-service editor: WordPress uses the **post title for the subject**, and the independently drafted Markdown *preheaders* are not verified native Jetpack controls.

These platform specifics produce a useful, falsifiable editorial finding:

| Canonical issue | Current first-55 fallback *model* | Custom excerpt proposed in PR #187 | What the actual recipient gets |
|---|---|---|---|
| 01 — The mind is not a camera | Story begins, primary link absent | Source-led introduction, not installed | **UNKNOWN** |
| 02 — Before hypnosis had a name | Story begins, primary link absent | Historic evidence note, not installed | **UNKNOWN** |
| 03 — Twelve-minute question | **Explicit commission disclosure absent**; CTA absent; original full issue has 2 clickable seller citations | Early financial disclosure in proposed excerpt; *not installed* | **UNKNOWN — HOLD_MERCHANT** |
| 04 — Apollo 1 | First transmission detail, primary link absent | 17.1-second caveat, not installed | **UNKNOWN** |
| 05 — Before you press play | **Explicit commission disclosure absent**; CTA absent | Early financial disclosure in proposed excerpt; *not installed* | **UNKNOWN — HOLD_MERCHANT** |
| 06 — Seven-day attention log | Diary study begins, primary link absent | Free Fieldbook invitation, not installed | **UNKNOWN** |

In the original article bodies, the explicit commercial disclosures of Issues **03 and 05** occur *hundreds* of words into the narrative—later than a 55-word fallback. This is why the original first-person editorial quality does **not** establish honest commercial disclosure in an excerpt-only received email. The 55-word output is an **offline, whitespace-word approximation** of Markdown narrative; exact WordPress block rendering, HTML sanitization, added WordPress branding, images, buttons, read-more link, footers and the final MIME text **remain unverified**.

A deliberate false-positive test is included: Issue 02's proposed historical excerpt uses the word **royal commission**, which must not be mistaken for an affiliate **commission disclosure**. Checks match actual financial-disclosure phrasing, not any occurrence of the word *commission*.

## Files and actual functionality

- **`inbox_boundary.py`**: standard-library, read-only executable audit of original six source files + manifest + the six already existing PR #187 proposed excerpts. Models the **first 55 words only**, distinguishes historical and commercial uses of the word commission, counts direct clickable seller citations, checks metadata synchronization and all-hold flags, and emits privacy-safe deterministic JSON. It **raises** if its sources, mix, or observed excerpt-mode prerequisite diverge. Its `safe_editor_rehearsal()` requires draft status, per-post send **false**, no schedule, zero test-send, no audience, no claimed received message and no founder send approval; a true result means **offline-safe only, never authorized to send**.
- **`snapshot.json`**: read-only dated WordPress evidence with counts as distinct fields, unique-eligible **null**, no subscriber identifiers and explicit unverified legal/merchant controls.
- **`review.html`**: accessible no-JavaScript, responsive six-card side-by-side editorial reviewer, comparing original first-55 model with existing **uninstalled** optional custom excerpts. No seller outbound links, list form, scripts, analytics or tracking pixels. It is NOT a native email preview.
- **`../tests/test_r54_inbox_boundary.py`**: independently discoverable Python regression tests including hostile per-post toggle/status/scheduling/test-email mutations, false financial-disclosure recognition, source/manifest consistency, legal placeholders, original merchant source link finding, accessibility smoke invariants, and no-unapproved-publication checks.
- **`RELEASE_DECISIONS.md`**: exact, separately authorizable proof handoff and responsible ownership.

Local read-only reproduction from repository root:

```bash
python dispatch/campaign-2026-mind/r54-inbox-boundary/inbox_boundary.py --pretty
python -m unittest discover -s dispatch/campaign-2026-mind/tests -p 'test*.py' -v
```

A successful Python run or generated offline HTML does **not** establish native received-email compliance, partner permission, subscriber consent or founder send authorization.

## Hard release gates in priority order

1. **Actual valid publisher identity**: Final Vestige's own physical mailing address is verified; never substitute Automattic's address from a subscription confirmation. Validate the full subject, visible promotional framing, mailing address and usable unsubscribe in an **authorized received** commercial Jetpack email. [FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business).
2. **Real WordPress message evidence**: Separate founder approval for preview-only or test-send steps; proof that the per-post send switch was returned to **OFF** after a preview; a distinct explicit approval for an inbox test; original redacted RFC 5322 message inspected using the already built R45 inspector. No existing external address should be used by default.
3. **Recipient eligibility**: Private, nonexported Jetpack subscriber admin view; reconcile actual confirmed email-enabled/suppressed entries and category/digest settings to a distinct, eligible count, with all identifiers kept out of GitHub. Existing 2/2/2 totals are not a denominator. [Official subscriber filters](https://wordpress.com/support/subscribers/), last reviewed October 26, 2026.
4. **Named offer authority**: Separate **written Final Vestige-specific Zen12 and Total Focus EMAIL** promotion rights (not merely a public Inspire3 recruitment page or another product's swipe), exact earning/deep link permissions, legal creatives, live approved independent buyer-guide URLs, current checkout/privacy/refund terms and product-specific claim support. Coordinate strictly with Mind #171. [FTC endorsement FAQs](https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking).
5. **Editorial approval and actual delivery path**: Review per-post excerpts versus full post, author-approved final subject and meaningful CTA, no direct seller checkout shortcut, no unverified benefit copy, accurate publication dates and cadence. If the original 4:2 order is blocked at #03, do not publish a promised “next week” offer automatically or silently substitute an unapproved alternative.
6. **Explicit FINAL authorization**: Founder independently approves exact creative, issue, recipient audience, sending date and WordPress-specific post handling. Prior approval of a *draft campaign* is **not** final send approval.

No authorization is inferred from static tests, companion issue progress, a correctly formatted attestation JSON or a merchant's public promotional copy.

**Real outcome this sprint:** concretely measured first-55-word copy boundary for all six original editions, made an existing optional excerpt package reviewable against the WordPress-delivered mode, protected against the historical “commission” false positive and added independent per-post no-send mutations—without rewriting any approved manuscript or touching production.
