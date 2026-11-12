# Dispatch R295 — Jetpack signup truth (isolated draft)

**Finding:** R294's `doubleOptIn === true` universal predicate is too strict: WordPress.com already-verified accounts skip a new confirmation email; non-account subscribers normally confirm by email. The correct provider-verified `Email subscription: Subscribed` state is mandatory for both, and Reader-only followers are not leads. Do not assume that `email followers=0` means there can be no WordPress.com subscribers who receive email; inspect the subscriber-level **Email subscription** filter and delivery preferences.

**Native local execution:** `node dispatch/r295/test_subscription_evidence.cjs` → **26/26 PASS** on local files; Git object hashes of these two local files matched the retrieved exact GitHub committed blobs. Tests are synthetic. No actual subscriber, merchant purchase, WordPress API lifecycle, consent or inbox integration tests.

**Contents:** `subscription_evidence.cjs` deterministic fail-closed, de-identified test contract; `test_subscription_evidence.cjs` 26 native test cases including email-link and WP.com account pathways, bounce/paused/reader-only, stale evidence, dedup, 4:2 allocation and no send; `aggregate_snapshot.json` no PII; `PROVIDER_AND_INBOX_ACCEPTANCE.md` review procedure; `OFFER_REVENUE_DECISION.md` genuine offer/funnel/blocker/owner register.

**Do not deploy** this offline code into production as analytics or create a new contact list. It has no sending capability and always holds campaign release. PR stacked on [#2131](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2131); originals [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) and #201, homepage PR #49 remain untouched. Founder final release approval absent.
