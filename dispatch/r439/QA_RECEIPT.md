# Dispatch R439 — executed QA and source-of-truth receipt

**Release class:** isolated additive source-only draft. All six original manuscripts in master PR #175 unchanged. No email, test email, WordPress post or settings edit, subscriber import, merchant link activation, paid action, merge or homepage PR #49 change.

## Verified sources

- Original master six-issue PR #175 exact `d57ccdba3aee8f065e143e101c2945f4f3d01647`; six original issue files + manifest + `tests/test_campaign.py` fetched from GitHub. Original Python file Git blob `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`.
- PR #201 checked and remains open draft. R438 source branch PR #2951 exact HEAD `e8e591cbd16b58c461fe203f38f2d6c1ffa57d99` is unchanged and the base of R439.
- GitHub Issue #174 and current comments; Mind companion #171 and latest R460 correction comment. Google Drive TASK-008 and dated Praxxis/Grok handoff read for division of ownership, no edits.
- Authenticated `finalvestige.com` Jetpack Newsletter status + settings as of `2026-11-18 04:31:45 UTC`: 3 total, 3 confirmed, 2 unconfirmed (excluded), 0 suppressed; new-post email default OFF; full-content email; `reply_to=no-reply`; welcome configured and Fieldbook URL present; `site_can_send=true`; most recent five post notifications never emailed because per-post `send_subscription=false`.
- Authenticated WordPress `/dispatch/` ID 523 (2026-11-05 modified), `/focus/` ID 1579 (2026-11-16 modified), `/editorial-standards/` ID 17 (published, last reviewed Aug 23), read-only.
- Jetpack Stats Followers from same session: direct email 0, WordPress.com Reader 3, `partial=false`. Neither report gives authenticated `Email subscription=Subscribed` count.
- WordPress help pages updated/reviewed 2026-11-09 and 2026-11-13: https://wordpress.com/support/newsletter/email-appearance/ ; https://wordpress.com/support/newsletter/send-newsletter-emails/ ; https://wordpress.com/support/newsletter-settings/ .
- Exact public merchant pages checked 2026-11-17: https://zen12.com/about ; https://zen12.com/secret/ ; https://hypnosislive.com/faq ; FTC https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

## Executed native QA

Local environment: Node **22.16.0**. Native execution:
```
node dispatch/r439/consent_promise_gate.test.cjs
26/26 native Node tests passed; no send, no mutations
```
- Test file is byte-identical to GitHub blob `c35ed2eb06fdefb73136e0f7aca946ad3a6796d3`.
- Evaluator is byte-identical to GitHub blob `dbdb04536227bb4161fb83b1a589cc9695253488`.
- Local `git hash-object` for both files matched those GitHub blob SHAs after correcting backtick interpolation and a legitimate `merchant/email/zen12` evidence-reference false positive.
- The original master PR #175's six **Python test conditions** and one extra exact-offer identity guard passed **7/7 using independently fetched GitHub source in V8**. This is **not** a fresh native Python execution. R434 previously documented native Python 6/6 on the same unchanged master commit.

Live-source dry run, with **no fabricated permissions**:
```
observed blockers: 16
structural errors: 0
recipient email eligibility: UNKNOWN
provider confirmed_signup event: UNVERIFIED
Issue 03/05 merchant approval: NOT VERIFIED
net revenue per 1,000 audited humans: NOT COMPUTABLE
editorial_reviewable=false, commercial_reviewable=false, send_authorized=false
```
All 26 native cases are deterministic/synthetic, including 4:2 preservation, Hypnosis Live vs Total Focus identity mismatch, follower-count non-additivity, provider count error handling, URL/PII evidence-reference rejection, provider-scope validation, stale/unknown recipient evidence and merchant net-revenue denominators. Tests do **not** establish a legally valid mail, actual preview or customer order.

## Material R439 findings (higher-value than additional draft volume)

1. **Public promise mismatch:** `/dispatch/` still implies post-time automatic email while the newsletter defaults OFF and five recent posts were opted out. Source-only founder wording candidates supplied, not adopted.
2. **Universal double-opt-in wording is wrong:** WordPress account holders may bypass a separate confirmation email. Require provider confirmation and eligible delivery setting, not a necessarily received double-opt-in email for every legitimate reader.
3. **Issue 05 product drift:** The canonical PR #175 letter explicitly evaluates **Hypnosis Live**, while recent owner coordination sometimes refers to **Total Focus** as Issue 05. Offer identity is pinned to original Hypnosis Live until founder explicitly changes campaign scope; a synthetic Total Focus swap is rejected in code.
4. **Account vs inbox:** 3 confirmed, 0 email-followers and 3 Reader followers are different counters. The actual email audience and welcome delivery remain unverified.
5. **Merchant-specific claims:** Zen12's 12-minute/60-minute seller assertion and `/secret/` coupon/countdown are not Final Vestige-verified outcomes, discounts or eligibility. Hypnosis Live refund limits cannot be replaced by a vague blanket guarantee. No named EMAIL affiliate approval.
6. **Commercial-first reporting:** No verified paid orders or independently audited qualified-human session denominator, so net revenue/1,000 is null, *not* 0.

## Invariants/limitations

The connected WordPress tools expose settings, newsletter status and follower aggregates, **not** the private Subscribers tab receiving filter or genuine non-sending native email Preview. No fake testimonial, subscriber list, product conversion or open-rate report was made. All legal/merchant/welcome states remain closed until a real independent witness. The R439 code always returns `send_authorized=false`, including when synthetic permissions are provided.

This package contributes to Issue #174 and coordinates with #171/#129/#820, not a replacement for Mind pre-sell, Grok social production, Claude site engineering or the founder's final release approval. 
