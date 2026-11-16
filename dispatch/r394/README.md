# Dispatch R394 — consent-to-commerce proof bridge (DRAFT / UNSENT)

Source of truth: [master #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174) and [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Stacked on [R393 #2703](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2703); original six issues remain at #175 SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647`. No canonical issue, preview, homepage, or Mind page changed. Homepage priority and frozen #49 respected.

**Purpose:** resolve the biggest actual blocker rather than draft another unapproved alternate newsletter: can a provider-authoritatively subscribed human receive a compliant, relevant email which can eventually lead to a *genuinely settled* product commission? Currently: **NO PROVEN END-TO-END PATH**.

Files:
- `PROVIDER_SNAPSHOT_REDACTED.json` — live authenticated counts/settings, no subscriber PII.
- `ONE_OFFER_PATH.md` — one high-intent Zen12 hypothesis, not a merchant or efficacy endorsement.
- `CAMPAIGN_COPY_DECISIONS.md` — all six original CTA/subject decisions, not silent rewrites.
- `LEGAL_AND_PREVIEW_ACCEPTANCE.md` — actual WordPress non-sending email preview/recipient/footer acceptance.
- `MERCHANT_PERMISSION_DELTA.md` — current exact SKU/claims/checkout constraints versus Mind R413.
- `ATTRIBUTION_AND_PRIVACY.md` — once-only confirmed_signup_v1 and net-realized-revenue rules.
- `proof_gate.mjs`, `proof_gate.test.mjs` — isolated, fail-closed offline proof logic (nothing sends).
- `REVIEW_BOARD.html` — static, non-interactive operator summary; no external scripts.

**Separation:** 4 editorial / 2 conditional commercial review, all six `HOLD_UNSENT`. Commercial email rights, direct earning URLs, approved presell pages and settlement all unverified. **Never enable emails, schedule, publish, import, contact, spend, activate affiliate links or merge without founder approval.**

**Validation:** use `node --test dispatch/r394/proof_gate.test.mjs`. No claims of native Jetpack rendering, mailbox receipt, subscriber eligibility, reviewed email rights or revenue. Avoid creating a second conversion event or analytics script; coordinate #129/#820.
