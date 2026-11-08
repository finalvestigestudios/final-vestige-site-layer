# R87 — consent truth across two public acquisition routes
This isolated stacked **DRAFT** branch adds only new review files. Parent [#755](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/755) exact `9061e1b416770f0ed82ba433d5f97d7e679dcbbf`; original untouched [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175); owner [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). This is a specific live-site **copy inconsistency**, not a legal opinion or newsletter delivery proof.

## Deliverables
1. `snapshot.json`: sanitized authenticated 2026-11-03 09:36 UTC WordPress status; no subscriber identifiers, physical address, private earning link or opt-out token.
2. `consent_change_request.md`: exact surgically scoped opt-in and welcome proposals. **Nothing approved, changed or installed.**
3. `merchant_and_subject_redlines.md`: line-item six-issue conversion/source audit against **named official seller pages**, historical evidence identity, commercial disclosure order and actual checkout uncertainty.
4. `signup_preview.html` + `signup_preview.txt`: matching, read-only, no forms or JavaScript, high-contrast accessible static review; not a native WordPress preview or received email.
5. `audit_consent_surfaces.py`: strictly offline, privacy-safe aggregate-source auditor; refuses PII/unexpected fields and always outputs `HOLD_UNSENT`. Reports whether the two public signup promises differ. It is intentionally **not** a sender, CRM, analytics collector or compliance-signoff program.
6. `../tests/test_r87_consent_truth.py`: adversarial no-PII, no-magic-approval, false-count, page mismatch and seller-authorization checks.

## Independent execution
```sh
python -I dispatch/campaign-2026-mind/r87-consent-consistency/audit_consent_surfaces.py
python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -p test_r87_consent_truth.py -v
```
Full-suite regression: `python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v`. Hosted execution requires real GitHub Actions logs; do not infer pass from the presence of test code.

## Human proof / operator restriction
Native WordPress subscriber filters and actual email receipts are needed for deliverability and legal-footer evidence. Do not call an email send/test-send, publish/schedule a post, turn on per-post newsletter, import/export subscribers, create an account, change website newsletter settings, contact a merchant or activate an affiliate link without explicit separately scoped founder approval.

Metrics for eventual pilot: unique sends/delivery **only** from the WordPress record, aggregate site CTA clicks when available without subscriber identity, unsubscribes/complaints only as supported by the provider, referrals/outbound clicks never equated with sales, verified purchases only from permitted merchant reporting; no statistically justified A/B tests on the current unknown/tiny audience.

The 52-page welcome Fieldbook remains configured but receipt unproven. All six editions remain `HOLD_UNSENT`; #03/#05 have additional `HOLD_MERCHANT`. No proposed copy replaces the original four-editorial/two-commercial draft.
