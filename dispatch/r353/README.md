# Dispatch R353 — provider consent, guest form and paid-outcome proof (DRAFT / NO SEND)

Source-only stacked draft on #2462; master campaign #175 and independent per-edition #201 remain unchanged. November 14, 2026, 03:38 PT. One Jetpack list, six original issues (4 editorial/2 commercial), zero emails, WordPress writes, live tracking changes or merchant activation.

## Meaningful difference from R351/R352
R351 found a **self-link in WordPress's view-content representation** and correctly did not conclude the guest form was broken. An independent public /dispatch/ extraction on November 14 contains **an email input and Subscribe button**. This reverses the urgency of a presumed missing form, NOT proof of a submitted or confirmed subscription. Do not change a live signup block based only on the content API. The new offline gate explicitly preserves this source disagreement and prevents fabricated leads, eligible recipients and revenue.

Files: `gate.mjs` is zero-dependency pure offline logic; `verify.mjs` uses synthetic data and makes no network calls. `PROVIDER_AND_GUEST_EVIDENCE.md` and `LEGAL_EMAIL_RELEASE.md` define manual unapproved verification; `SIX_ISSUE_CONVERSION_ALIGNMENT.md` maps the existing six without new sends. `MERCHANT_EVIDENCE.md` records exact seller source vs account-specific permission. `reviewer.html` is a static accessibility-minded board, not an email client screenshot.

Run when checked out: `node dispatch/r353/verify.mjs`. This code is not wired into production analytics. No real PII, subscriber IDs, active affiliate links or order records in this PR.
