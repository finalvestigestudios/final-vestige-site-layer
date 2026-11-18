# R455 — six-email transport, truthful subject, and CAN-SPAM primary-purpose review

**Decision: all six HOLD_UNSENT.** This is an additive, reviewer-only specification based on GitHub #174, #171, master campaign draft #175, per-edition safety draft #201 and most recent R454 #3036. It neither adopts alternative manuscripts nor changes WordPress.

## Material legal finding — four 'editorial' labels do not establish CAN-SPAM exemption

The FTC's rule evaluates the **primary purpose of each actual message**, not our manifest's internal `kind` label. Promotion of content on a commercially operated site can itself be commercial. A message mixing editorial and commercial content needs individual review of its subject, placement, prominence, and what a reasonable recipient would perceive. An email sent to an already subscribed person is **not automatically transactional**. Source: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business (especially primary-purpose questions).

Therefore, use a **conservative six-of-six** footer and unsubscribe gate, *not* a two-of-six-only legal gate. Every issue must have the genuine publisher postal address and a working opt-out visible in **actual Jetpack output**, even while four issues remain editorial in creative allocation. The physical address must belong to the responsible Final Vestige sender: the Automattic address in an old WordPress subscription confirmation and Hypnosis Live's public London address are not substitutes. Founder must supply/approve a valid street, registered USPS PO box or qualifying private mailbox; do not use an account owner's private address from a connected profile. Verify sender and advertising disclosures with qualified legal review before release.

**FTC-specific requirements**: truthful From/Reply-To/header and subject, nondeceptive subject, conspicuous ad labeling when applicable, valid physical address, an internet/reply-based unsubscribe usable for at least 30 days, and opt-outs honored within 10 business days; do not misclassify an editorial promotional email as transactional. Marketing emails for subscribers remain covered. A global affiliate policy page is not a substitute for issue-specific near-offer disclosure. This is a release checklist, not a legal opinion.

## Provider-native transport boundary (no send authorized)

Official WordPress.com documentation (reviewed 2026-11-09):
- https://wordpress.com/support/newsletter/send-newsletter-emails/ : Gutenberg post **title** supplies email **subject**, email generated from post, and explicit per-post sending selection matters.
- https://wordpress.com/support/newsletter/email-appearance/ : `Preview email` is available in the post editor **even when Send this post to subscribers is OFF**. It displays desktop/tablet/mobile; a separate `Send test email` exists, but it is **NOT AUTHORIZED**.
- `donotreply@wordpress.com` is the default/required outgoing WordPress.com sender address according to the email appearance guide; account display name is configurable. Do not promise custom From domain or Reply-To capabilities not observed on this site.
- A separate site-specific editable preheader control is **NOT VERIFIED**. The offline manifest preheader must not be misrepresented as a real inbox snippet; Jetpack's generated excerpt/body can determine what appears in that position.

### Read-only authenticated site record, 18 Nov 2026 20:44 UTC

Jetpack Newsletter enabled; `site_can_send=true` **is not send permission**; five recent post notifications explicitly `never_sent_opted_out`; automatic new-post setting `false`; email content format `full`; sender display `Final Vestige Studios`; `reply_to=no-reply`. Welcome is configured to link the free 52-page Focus Fieldbook, but final inbox receipt **NOT witnessed**. Public `/dispatch/` and `/focus/` have a rendered subscribe input/button on the publicly fetched pages; this does not establish confirmation or delivery. `/dispatch/` promises email 'when we publish', while automatic email for posts is off, so a specific newsletter cadence/selection notice would be more accurate (unpublished text redline under R448).

### Per-edition transport table

| Issue | Original subject from #175 | Primary-purpose default | Link/form release action |
|---|---|---|---|
| 01 | The mind is not a camera | Indeterminate until final body/subject inspected | Editorial-only; actual post title match; postal + unsubscribe |
| 02 | Before hypnosis had a name | Indeterminate | Editorial-only; original archive source trail; postal + unsubscribe |
| 03 | The twelve-minute meditation question | **Commercial-review pending** | Zen12 exact approved guide + account EMAIL rights + near-offer disclosure + postal/unsubscribe |
| 04 | Fourteen seconds. A much longer explanation. | Indeterminate | Editorial-only; avoid unproven Apollo 1 precise sequence; postal + unsubscribe |
| 05 | Before you press play on a hypnosis audio | **Commercial-review pending** | Hypnosis Live exact approved guide + account EMAIL rights; keep internal review notes outside body |
| 06 | What did seven days of attention reveal? | Indeterminate | Free Focus Fieldbook only; avoid implying a clinical trial; postal + unsubscribe |

Commercial location remains two of six; conservative compliance controls apply to **all six**, not only 03/05. Each send must be individually classified by an authorized reviewer based on its *final* contents and transport.

### Required human non-sending witness (not performed)

1. Founder explicitly approves an isolated safe editor session and identifies an **existing eligible WordPress draft**; until then do not create even a CMS draft.
2. Confirm `Send this post to subscribers` is OFF for this item **and** global auto-send remains OFF; do not touch the list/settings, schedule, or Publish.
3. Place subscriber-only manuscript content in temporary editor for authorized review only; select the exact cleaned subject as the post title. Discard or exit unsaved if that is the only way to avoid writes.
4. Use **Preview email**, **not** Send test email. Capture desktop/tablet/mobile privately, verify first 200 characters (actual preheader behavior), one main CTA, public source links, no private review notes, text legibility, message body and legal footer.
5. Verify *the actual generated* unsubscribe, publisher postal address, and required near-offer disclosures. Inspect a genuine received email and headers **only with separate founder permission to send to an approved internal inbox**. Preview is not inbox delivery evidence.
6. Keep six `HOLD_UNSENT` statuses until evidence, final campaign approval, approved audience and scheduled date are separately recorded. **Never send from the preflight or from a test.**

### Reviewed boundaries

Issue 05 subscriber-only R450 HTML is an *offline specimen*, not native Jetpack MIME. R446 alternatives are options only, not approved replacements. The R453 manifest contains Markdown `** ` contamination in four *alternative* envelope metadata pairs; the original six subjects do not have this particular defect. The new R455 contract is complementary to R454, and does not rewrite or substitute earlier assets.
