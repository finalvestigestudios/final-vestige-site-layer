# Dispatch R451 QA receipt — November 18, 2026 08:36–09:00 PT

**Status:** SOURCE-ONLY DRAFT / HARD HOLD. No emails, tests to inbox, subscriber contacts, WP writes, PR merges, merchant activations, social posts or spending. Frozen homepage PR #49 untouched.

## The new finding

Authenticated WordPress Jetpack Newsletter `status` as of **2026-11-18T16:39:09Z**: total=3, confirmed=3, unconfirmed=2, site_can_send=true, most recent 5 posts each `never_sent_opted_out` and `send_subscription=false`. Newsletter `get_settings` as of **16:39:10Z**: enabled, `email_new_posts_by_default=false`, `email_content_format=full`, welcome text includes the 52-page PDF, `reply_to=no-reply`.

Subscriber filter `all`: total=3, all three privately inspected records are `Subscribed` with `email_subscriber=true`; filter `unconfirmed_subscriber`: total=2, `Not confirmed` and excluded. **New discrepancy:** distinct Jetpack Stats `followers` returns `email=0, wpcom=3, total=3, partial=false`. It conflicts with the subscriber eligibility list. Document both, do not infer zero eligible recipients, independently acquired readers, welcome receipt or delivery. No PII in files.

Connected Gmail scoped searches returned the original **August 24, 2026 Refersion pending** notice, not approval / named affiliate EMAIL permission. No authenticated received welcome was established in searched connected mail; absence in this mailbox is not a universal delivery conclusion.

Live /dispatch/ and /focus/ were read read-only; both imply every published investigation triggers email, inconsistent with the default-off setting. Existing [Editorial Standards](https://finalvestige.com/editorial-standards/) support primary sources, disputed-record visibility and near-offer commercial independence. Official [Zen12 about](https://zen12.com/about), separate [Zen12 promotional funnel](https://zen12.com/secret/) and [Hypnosis Live FAQ](https://hypnosislive.com/faq) checked. Seller claims and refund text are **not** independent evidence or named campaign approval. [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) requires actual publisher postal/opt-out in applicable commercial mail. No genuine Jetpack preview, physical-address/footer proof or actual accepted commercial offer witness.

## Native execution (LOCAL; source verified against committed exact blobs)

```
cd dispatch/r451
python -m unittest -v test_audience_contract.py
Ran 21 tests in 0.001s
OK
```

All tests use **synthetic privacy-safe fixtures**. Passed: 3 confirmed vs 2 *additional* unconfirmed, separate followers email=0, malformed/partial source rejection, false lead exclusion, confirmed provider transition requirement, 4:2 allocation/EMAIL gates, unknown vs truly zero realized revenue and denial of unpaid clicks/fee-less sales.

**GitHub blob SHA == natively tested local blob SHA** for:
- `audience_contract.py`: `cf4d53b5b1299e5aca13fd6e6d2bc75a58af0d98`
- `test_audience_contract.py`: `94deaeffd444690ed340b90a69d1b39dabe3845b`
- `run_readonly_audit.py`: `d11567c31f9e9769c77700920a10a0dfb27e308b`

Native `run_readonly_audit.py` tested with a **locally constructed synthetic aggregate snapshot**, yielding `source_count_disagreement=True`, `all_held=True`, 5 never-sent statuses, six issues and null net revenue. The JSON snapshot committed on GitHub was independently read back and verified against the observed current counts, but was **not** natively executed byte-for-byte during this run. Therefore do not claim a native end-to-end run on the exact committed snapshot.

**GitHub readback:** Six new files fetched independently after commit; 14/14 V8/source structural assertions passed. Three Python files independently matched native local Git SHA byte-for-byte. Source snapshots contain aggregate statistics and no email addresses. `REDACTED_LIVE_SOURCE_SNAPSHOT.json` source pins are not actual email delivery receipts.

**Original campaign native QA:** previously independently run on master #175 at unchanged HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647` during R448 (6/6). NOT rerun natively in R451. Original master manuscripts and all prior draft review assets preserved; no founder adoption inferred.

## Open hard gates

- Founder final campaign approval and selection; native WordPress non-sending Preview (not yet witnessed); valid **Final Vestige** postal address; working rendered unsubscribe; received Fieldbook welcome and genuine newly confirmed external consent transition.
- Merchant-named affiliate account acceptance, product-specific EMAIL rights, issued authorized referral link, verified current offer/checkout/refund, approved **published** first-party guide for Zen12 and separately Hypnosis Live. Two commercial positions remain reserved (03 and 05) and not activated.
- Audited qualified-human Grok-to-landing sessions and *independently settled* purchase/commission ledger inclusive of refunds/fees. Net realized revenue / 1,000 qualified sessions: **NOT COMPUTABLE**, not 0.
- Actual email-client rendering, link-click acceptance, paid sales and statistically meaningful conversion test are **NOT TESTED**.

**Owner handoffs:** Dispatch #174 → Focus #129 / Claude for subscriber/feed/welcome; Mind #171 for merchant partner/guide; Revenue #820 to preserve null metric and Grok/Praxxis source ownership. PR #201 remains the earlier per-issue QA; original #175 and frozen homepage #49 unchanged.
