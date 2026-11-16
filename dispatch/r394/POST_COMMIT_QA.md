# R394 — independently re-fetched post-commit QA (HARD HOLD)

**State tested:** branch `dispatch-r394-consent-to-commerce-proof-20261115`, HEAD `ffcf78ae65bf4828cb994c985bd1549bf2d57c5c` BEFORE this evidence-only commit. Stacked on PR #2703 at `fdecaed669799678bab94dae970789bf9107e612`. Original #175 immutable draft source SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647`, reviewer #201 and homepage frozen PR #49 left unchanged.

## What genuinely ran
- **49 / 49 PASS:** authored `proof_gate.test.mjs` test callbacks replayed against the exact GitHub-fetched committed `proof_gate.mjs`, via V8 JS compatibility wrappers for Node test/assert (NOT a native Node run).
- **6 / 6 PASS:** original six `test_campaign.py` static assertions independently mirrored in V8 on the **six immutable GitHub markdown sources and exact manifest** fetched from current R394 branch. Original Python runner itself was NOT executed natively because the container cannot resolve the GitHub host and those connector-only source bytes are not mounted in the native container.
- **10 / 10 PASS:** static reviewer/JSON checks (HTML language, mobile viewport, source-only HOLD, no script/form/active merchant CTA, no fabricated price or subscriber PII, null eligible count, false named approval).
- **4 / 4 PASS:** independent adversarial probes (empty unaudited ledger cannot produce fictitious $0 revenue, download cannot be a provider-confirmed signup, every issue `send_authorized=false` even with all theoretical attestations, negative settlement commission rejected).
- **Detected and corrected a REAL first-test defect:** the original gate treated an **unaudited empty settlement array** as a proven $0. Added `ledger_audited===true` separately from audited sessions; confirmed two distinct fixtures: unaudited empty ledger `NOT_COMPUTABLE`, and independently audited empty ledger + actual audited sessions can represent observed $0. These are synthetic test inputs, **not real FV revenue or sample data**.

## Exact re-fetched blob IDs
- `proof_gate.mjs` = `9ea7343edd45968f45f44fdda34f60100f06a607`
- `proof_gate.test.mjs` = `73771a04ef12c4aa094529ecb2ce5ab756f1d267`
- `PROVIDER_SNAPSHOT_REDACTED.json` = `ec60e30634f7fedfc94121d0aedba3e88a57d1a0`
- `REVIEW_BOARD.html` = `73bf868fd97387afdf9ecf2fb2b44df4677bcd83`
- Canonical original `manifest.json` = `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00`
- Canonical original `test_campaign.py` = `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`
- Canonical original issue markdown 01→06: `039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8`, `faa207ab7deafd86460d36f8c17fe62d392d0e14`, `aeeef34efea0cc281f69901488e4501fea851245`, `89635bfb9c8d1ff17297a59b6b5b2a176934ca`, `a9dfaa450ba025a7b5113ade8a294d6dbad778dc`, `004d558df6376d2ad6f4f79a4581e8d2c444e355`.

## Source-of-truth read-only observation
- **Live authenticated Jetpack** `2026-11-16T04:39:28Z`: newsletter ON, auto-new-post emails OFF, full email content, no-reply, 52-page welcome configured. Total 3 / confirmed 3 / pending 2, WordPress.com followers 3 / direct-email follower count 0, **unique eligible inboxes UNKNOWN**. Not contradictory: unconfirmed excluded from total. Five recent published posts never_sent_opted_out.
- **Received welcome**: NOT VERIFIED. Connected Gmail searched October-forward Fieldbook/welcome terms with zero matching messages; historical October 25 subscriber confirmation alone is NOT welcome/delivery.
- **Merchant**: Mind R413 claims/permissions matrix and official Zen12/Total Focus seller pages reviewed. No named FV SKU+EMAIL approval, issued earning URL, LIVE first-party vetted buyer guide or referred price/refund authenticated. No product efficacy transferred from unrelated psychology studies.
- **FTC release**: actual founder physical postal address, working recipient unsubscribe, genuine native WordPress Preview email and real inbox MIME still NOT VERIFIED. Static HTML cannot prove an email-client rendering or send.

## Distinctions and explicit prohibitions
No actual browser screenshot/accessibility run, hosted CI, native Node, native Python, Gmail received test, provider filter, merchant payout, full checkout, UTM deployment, email or test email occurred in this sprint. Source package and static review board are **BUILT + V8 TESTED**, not LIVE or eligible to SEND. Current observed settled revenue and qualified-human session denominator remain unavailable, so **net USD per 1,000 qualified-human sessions = NOT_COMPUTABLE**, not zero.

**Release:** original six HOLD_UNSENT; 03/05 HOLD_MERCHANT; 04 HOLD_COPY; no production changes, WordPress edits, subscriber contacts/imports, affiliate links, Grok queue changes, PR merge, or expenditure. Evidence owner #174 and coordination #171/#129/#820.
