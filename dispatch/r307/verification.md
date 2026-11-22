# R307 native verification report

- Immutable master campaign: PR #175 HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647`, 8/8 source files verified with `git hash-object` against authenticated GitHub `fetch_file` SHA.
- Original six-test native Python suite was executed in a clean archive extraction during this sprint: **6/6 PASS**.
- New first-party source-level regression tests intentionally reproduce permissive query outcomes, including `?subscribe=pending`, `?subscribe=0` and `?subscribe=BLOCKED`. This is a UI display classification issue, *not proven existing analytics misattribution*.
- New offline tests for provider-status interpretation reject client-only signals, unconfirmed/paused/not-subscribed/duplicate/PII evidence and lack of partner permissions. **Review-only:** no actual Jetpack API event authenticated or emitted.
- Authenticated WordPress read-only snapshot as of `2026-11-12T14:39:44Z`: subscriptions true, auto new-post OFF, email format FULL, welcome PDF configured. `total=3`, `confirmed=3`, `unconfirmed=2`, WP.com followers 3, email followers 0. These populations are not additive; actual `Email subscription=Subscribed` population is UNKNOWN. Latest five posts never sent (flag false), not proof of lifetime zero sends.
- Genuine Jetpack native preview, inbox MIME, publisher-specific physical address, working unsubscribe, received welcome, merchant acceptance/email rights, paid commissions and net revenue remain **UNVERIFIED**.
- All 6 original letters HOLD_UNSENT; commercial 03/05 HOLD_MERCHANT. New copy is **NOT ADOPTED**.
