# R461 — GitHub exact-source QA and release receipt

**Review only, November 18 2026 Pacific. Source branch:** `review/dispatch-r461-hypnosis-evidence-claim-gates-20261118` based on exact R460 HEAD `6313affaa6f74ee55fbb7b551f09286e44548dde` (PR #3070). **Master PR #175 at `d57ccdba3aee8f065e143e101c2945f4f3d01647`; safety PR #201 at `ef53e5a17046e3dff5a4a7e3b0f4c8fbce9cd6f6` remain unchanged.** Issue #174 and Mind #171 are canonical.

## Tested, not inferred

Five new committed files were independently **re-fetched from the GitHub branch**, then inspected with source-only V8 assertions. Exact GitHub blob SHAs (before this receipt):
- `ISSUE05_EVIDENCE_FIRST_OPTION.md` — `c7bccc2d8ea047d8bd9289b55803a31a0bd45413`
- `ISSUE05_OFFLINE_REVIEW.txt` — `00721849d6feaef6701756359781c4095110accc`
- `ISSUE05_OFFLINE_REVIEW.html` — `c4715dbce44809326bfb7d3fcca48d409d9d4264`
- `CLAIM_MERCHANT_AND_CONVERSION_ACCEPTANCE.md` — `a35d8936f0e8be4acc0b31ed67a07c82af7ec18d`
- `ISSUE05_DECISION_ATTESTATIONS.json` — `1924e0099e9045a6c7a8a69b2849b426c5768760`

**V8 authoring/specimen/static QA:** 26/27 first checks passed. The sole failed check was incorrectly case-sensitive about the documented sentence “Neither is a witnessed payment checkout”; the exact document does contain that sentence. On independent re-fetch, corrected case-insensitive expectation passed, yielding **27/27 logical conditions satisfied**. Checks cover subject/preheader parity, primary CTA link, five source URLs in HTML and plaintext, reserved commercial slot with inactive purchasing link, disclosure near the reserved offer, no pixels/JavaScript/external assets, readability semantics, no quoted merchant prices in the email, unresolved legal footers, original 4:2 allocation, all-false release attestations, no personal subscriber data, and three intentionally invalid mutations rejected. These are **static source QA** only; there is no browser, real mail-client, source-specific clinical verification or WordPress renderer execution.

**Original six-condition PR #175 Python suite:** Original `test_campaign.py` blob `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`, immutable current HEAD above; original manifest and all six issue blobs independently fetched by GitHub connector. Six conditions mirrored and evaluated in V8: **6/6 PASS**. **This is not native Python execution.** The container could not resolve github.com to clone the exact repository, and code/connector outputs could not be mounted directly as a repository checkout. Native Python rerun and source checkout verification remain TODO; do not claim `python -m unittest` was run in R461. Earlier native runs of master were documented, but are not this sprint's result.

## New first-party/provider evidence

Authenticated Jetpack Newsletter status at `2026-11-19T02:35:52Z`: enabled and can send, default auto-email OFF, last five `never_sent_opted_out`; sender `Final Vestige Studios`, body `full`, reply-to `no-reply`. Newsletter `total=3 confirmed=3 additional_unconfirmed=2`. Stats Subscribers filters returned `all=3` each email_subscriber=true/status Subscribed; email=3, Reader=0; unconfirmed=2 status Not confirmed. Independent Stats Followers email=0, Reader=3, partial=false. Provider conflict unresolved. No exported address, private email or IDs. Stats Emails `posts=[]`, no measurable send/sale.

WordPress page 523 `/dispatch/`, page 1579 `/focus/`, page 17 `/editorial-standards/` all inspected read-only; editor standards mandate first-party evidence, marking uncertainty, source checking, corrections and separation of commercial relationships. Focus's "You do not need to sign up again" instruction was verified as already corrected; do not re-raise it. Public subscription copy that promises email when posts publish still needs alignment with default-off.

Gmail read-only scoped search returned the 2026-08-24 Refersion **pending** approval subject and no named approval in the search results. Search for a received welcome message with exact wording after 2026-10-20 produced no matches (does not establish nondelivery). Affiliate rights, approved email links, checkout and actual welcome receipt remain **NOT VERIFIED**.

## Safety and outcome

- This is one *optional* source-led Issue05 candidate with HTML+plain review; it does not overwrite master #175, activate Hypnosis Live, change Mind presell or unfreeze #49.
- All six actual campaign editions `HOLD_UNSENT`; alternate also HOLD. No Jetpack editor Preview or email MIME inspected; no authorized sender postal address, actual unsubscribe or final approval.
- No emails or test emails sent, no WordPress edits/settings/list mutations, no affiliate buying links, no publish, no merge, no subscriber export, no paid services.
- No independently settled merchant orders or audited qualified-human acquisition denominator. Realized net revenue per 1,000 qualified human sessions = **NOT COMPUTABLE**, not zero.

## Priority owner handoff
1. **Mind/Commerce**: account-specific written email-promotion rights, merchant link/SKU, approved live independent presell, real checkout/refund/payout evidence.
2. **Founder + Dispatch**: valid publisher mailing address, native no-send Jetpack preview and inspected unsubscribe, final copy/audience/date release approval.
3. **Focus/Claude**: provider classification reconciliation, consent-valid first confirmed transition and real welcome delivery; keep PII private.
4. **Grok/Praxxis/Claude**: reuse Issue #820 canonical asset_id/UTM measurement and independent settled-order journal, no duplicated collector or invented A/B statistics.
