# Final Vestige Dispatch — R294 consent-copy parity and conversion release QA

**Scope:** new isolated review files only. No existing campaign rewrite, no WordPress write, no subscriber contacts, no email/test sends, no new list/platform, no posting, no merchant activation, no new tracking, no paid service.

## Distinct findings and deliverables

- Live /dispatch/ and /focus/ use one Jetpack list but present different expectations: **/focus/** explains commission-bearing recommendations, whereas **/dispatch/** presently describes only investigations/archive finds and the Fieldbook. Propose one non-promotional transparency paragraph; **NOT LIVE**.
- Source QA: the original PR #175 remains at exact SHA `d57ccdba3aee8f065e143e101c2945f4f3d01647`. Eight original GitHub blob SHAs matched byte-for-byte against an archived original package locally; **6/6 native Python tests PASSED** this run. The original campaign was not edited.
- `ENTRYPOINT_COPY_PARITY.md`: source wording, proposed copy, commercial-email authorization and legal gates.
- `ONE_OFFER_FOLLOWUP_HYPOTHESIS.md`: unsent, one-guide Zen12 progression that preserves 4 editorial / 2 conditional commercial issues. No duplicate list or mandatory purchase.
- `entrypoint_review.html`: responsive standalone reviewer display (not native Jetpack preview; no signup form or executable visitor tracking).
- `RELEASE_DECISION.md`: per-edition Offer -> Step -> Blocker -> Experiment -> Evidence -> Owner, 6 holds.
- `evidence_snapshot.json`: de-identified aggregate counters and observed statuses; no subscriber addresses.
- `release_contract.cjs` and `test_release_contract.cjs`: fail-closed gates with **32/32 source-byte V8 synthetic assertions passed** in this sprint. The authored test code is committed, but native Node / GitHub CI not executed.
- **No conversion inferred:** 3 Jetpack confirmed in diagnostic endpoint vs 3 WordPress.com followers and 0 email followers in separate reports; true emailable consent count UNKNOWN. 3/3/2 is not an additive total.

## Local read-only test commands

```sh
node dispatch/r294/test_release_contract.cjs
python -m unittest discover -s dispatch/campaign-2026-mind/tests -v
```

The V8 suite is deterministic synthetic QA and does not submit a mail, inspect an actual recipient, or simulate a valid merchant payment. The native Python suite above was run on archived source whose Git blob fingerprints match all current PR #175 originals. This is not evidence of authenticated production event delivery.

## Release decision and owners

**All six newsletters HOLD_UNSENT; Issues 03/05 HOLD_MERCHANT.** The proposed consent copy is NOT_ADOPTED. No founder final campaign approval.

- Mind + Commerce: show actual publisher acceptance, approved email marketing rights, issued earning link, product-specific terms, live vetted guide; later independently settle orders/refunds/fees.
- Claude/Focus: provider-confirmed and deduplicated consent event, privacy, no duplicate measurement script.
- Dispatch/Founder: align signup expectations, actual Jetpack non-sending editor preview, verify legal FV postal and unsubscribe, separately authorize any real received email test.
- Grok/Praxxis: retain social distribution and source-tagged actual asset ownership (TASK-008).
- Homepage / PR #49 remain untouched.

Sources: [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [Mind #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), [Focus #129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), [Conversion #820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820), [master campaign #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), [source gate #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), [Mind R307 #2129](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2129), [WordPress email preview](https://wordpress.com/support/newsletter/email-appearance/), [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business).
