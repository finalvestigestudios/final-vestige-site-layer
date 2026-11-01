# R52 — Consent-promise consistency and actual-send safety (DRAFT / HARD HOLD)

Owner: **The Dispatch Issue #174**. Merchant/guide decisions belong to **Mind & Affiliate Issue #171**. Canonical six letters **PR #175**. Independent edition gate PR #201. Stacked parent R51 **PR #510**. This sprint is an original cross-surface source check and language proposal; it does NOT change any WordPress page, settings, subscriber, existing letter, welcome email, merchant resource, homepage or frozen PR #49.

## Source-of-truth finding — two different promises, one Jetpack list

Read-only authenticated WordPress on **November 1, 2026, 22:31–22:33 UTC**, site ID **256784396**:

**/dispatch/** page 523, published, leads with: “New investigations and archive finds by email, when we publish them.” It includes “Unsubscribe anytime,” a privacy link and the existing Jetpack subscribe block. Its visible signup promise does **not** disclose that some issues could contain a commission-earning recommendation.

**/focus/** page 1579, published, already prominently states: “By subscribing you also join The Dispatch, our email of new investigations and archive finds, sent when we publish them. **Some emails may include recommendations that earn us a commission.** Unsubscribe anytime.” This is an existing, useful commercial disclosure; do not lose it or falsely say both forms omit commissions. Both routes use the same Jetpack subscription setup.

**Configured welcome:** 52-page Seven Day Focus Fieldbook link remains in the welcome body. The closing promise is investigations or archival finds and “No daily flood of emails.” There is no corresponding optional product-evaluation notice. The actual welcome was NOT verified as received. A prior subscription *confirmation* is neither a welcome letter nor an opt-out/legal footer proof.

**Editorial Standards** page 17 published and unchanged: historical conclusions independent of ads/affiliates, material financial relationships disclosed.

**Newsletter status/settings:** enabled, can send technically, new-post email default **OFF**; critically WordPress allows manually turning on emailing for an individual post even when the default is OFF. Global email mode is **excerpt**; full story copy in offline files is not proof of delivered full email. Sender display “Final Vestige,” reply-to “no-reply,” welcome configured, recent_sends=[] means no *reported recent sends*, never proof of zero lifetime messages. Subscriber dashboard returns **total 2 / confirmed 2 / unconfirmed 2**. These labels cannot safely be summed or treated as proof of unique consented recipients. No subscriber identities or addresses inspected or stored.

**Commercial state:** original four editorial (01/02/04/06), two commercial-review-pending (03/05). Zen12 and Total Focus account-specific email permission, earning URL, authorized media creative, independent approved live warm-up guides, final checkout/refund terms and any effectiveness claim are NOT release verified. Public Inspire3 Limitless Labs email swipes relate to a different named offer; they do not grant either product rights. Current seller page features are representations, not clinical efficacy proof.

## Why this deserves its own sprint

The issue is not that a merchant claim needs yet another rewrite. It is that a subscriber who signed up through the **archive-only /dispatch/** page could see a different commercial explanation from a subscriber who signed up through **/focus/**. The configured welcome reinforces the archive-first expectation. This is a material **reader-trust, conversion and editorial-consistency gap** before a six-week editorial-to-affiliate test; it is NOT proof of illegality, absent consent or a CAN-SPAM opt-in requirement. We cannot know which wording any particular subscriber saw from aggregate counts. No new list or re-permission blast is authorized.

Research integrity matters more than nominal “conversion optimization”: the remedy is plain disclosure, original useful investigation, independent seller evidence, one appropriate first-party CTA, and optional purchasing only after permissions. Proposed copy is in **copy_options.md** for founder review. /focus/ already carries the disclosure and is not slated for unnecessary rewrite. The optional welcome/Issue 01 wording in that file is not a silent substitution.

## Files & verification

- **observations.json** — privacy-safe exact live WordPress language and settings, clearly labeled date and unknown evidence; no PII.
- **audit_consent_contract.py** — deterministic standard-library-only parser; reports cross-surface inconsistency, WordPress technical sendability vs editorial authority, 2/2/2 ambiguity, excerpt constraints, all hard stops. Does not connect to WordPress/Gmail or send anything.
- **copy_options.md** — optional evergreen /dispatch/ near-form copy variants and optional prospective welcome/Issue 01 disclosures. No change authorized.
- **review.html** — accessible, no-JS, no-image, no-form, no-pixel static human comparison board. NOT a Jetpack-rendered preview.
- **../tests/test_r52_consent_promise_contract.py** — 46 adversarial Python regression tests including manipulated partner/founder proof flags (even ALL true never unlocks automated send), mismatched signup copy, canonical manifest mutation, data privacy checks and reader-visible vendor-link prohibition.
- **README.md** — this chain of custody and unresolved release checklist.

Run locally when the complete source tree is available:
    python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -p test_r52_consent_promise_contract.py -v
Then run the complete Dispatch Python suite against the **exact R52 PR head**, verifying the SHA in GitHub Actions logs. A green GitHub test is a source-integrity result only, not a real emailed MIME or legal review.

## Primary-purpose and delivery controls

Official FTC CAN-SPAM guidance explains mixed-content *primary purpose*, truthful sending identity/subjects, valid publisher postal address, and functional opt-out in applicable commercial messages. The address of Automattic or Inspire3 cannot stand in for the valid Final Vestige address. An offline mock footer does not count as received-email evidence.

Read-only WordPress settings documentation (reviewed October 26, 2026) confirms manual email enablement even with automatic-post sends OFF; for excerpt mode, it describes using an explicit custom excerpt or a 55-word fallback. A separate Jetpack preheader field has NOT been verified. Actual provider rendering must be assessed with an authorized, real received email. No real test recipient or send has been approved; do not trigger one.

To release even one editorial letter later requires a separately recorded founder approval on actual copy, audience and delivery time, privacy-safe unique subscriber reconciliation, legally appropriate publisher address and received-email functional unsubscribe, provider preview and actual approved received message. 03 and 05 also require a published approved first-party guide and written product/channel-specific affiliate permission and earning-link validation. The founder's original 4:2 allocation is unaltered.

## Sources and boundary notes

- Actual /dispatch/ https://finalvestige.com/dispatch/
- Actual /focus/ https://finalvestige.com/focus/
- Actual Editorial Standards https://finalvestige.com/editorial-standards/
- FTC CAN-SPAM https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- WordPress newsletter settings https://wordpress.com/support/newsletter-settings/
- Official Inspire3 Limitless Labs promotional materials (NOT Zen12/Total Focus permission) https://inspire3.com/ll/
- Official Zen12 product https://zen12.com/hnp
- Official Total Focus https://hypnosislive.com/mental-skills/total-focus

## Non-negotiable release status

**ALL SIX = HOLD_UNSENT; 03/05 also HOLD_MERCHANT.** No email or test-email, schedule, WordPress post, site copy edit, subscriber contact/export/import, merchant contact, offer activation, analytics tracker, platform expense or newsletter settings change. The main website homepage remains the highest priority and separate from this PR. Static scripts never grant permission to send.
