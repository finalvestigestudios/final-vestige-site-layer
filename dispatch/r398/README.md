# Final Vestige Dispatch R398 — conversion/consent integrity, source-only

**Status: DRAFT/HOLD. No sending, CMS changes, affiliate activation, list imports, production tracking, spending or merging.** Isolated stacked work on [R397 #2724](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2724). The canonical six-issue campaign [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) and hard-stop readiness [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) are unchanged. Master [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), Mind [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), Focus [#129](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/129), and revenue [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820).

## Why this sprint is different

Direct inspection of the **live WordPress Focus page HTML** reveals a client-side state issue: an arbitrary non-denylisted `?subscribe=` query value reveals a panel with a PDF link marked `data-fv-location="after_signup"`. The `is-subscriber` CSS class also triggers it. Neither is independently authenticated proof of an **email-eligible, provider-confirmed unique subscriber**. The free Fieldbook is an available reader resource, not a verified conversion. This is a source-level/UI state finding, not proof that the existing analytics has recorded false conversions or that actual subscriber count is wrong.

- [LIVE_FOCUS_CONSENT_FORENSICS.md](LIVE_FOCUS_CONSENT_FORENSICS.md): exact source excerpt, five native VM tests, careful scope.
- [FOCUS_FIX_PROPOSAL.md](FOCUS_FIX_PROPOSAL.md): minimal CMS-diff specification owned by Claude; never applied.
- [JETPACK_PREVIEW_LEGAL_ACCEPTANCE.md](JETPACK_PREVIEW_LEGAL_ACCEPTANCE.md): how to get a genuine non-sending preview and verify CAN-SPAM without contacting anyone.
- [COPY_CONVERSION_DECISIONS.md](COPY_CONVERSION_DECISIONS.md): precise six-issue copy/CTA decision matrix without re-authoring approved drafts.
- [MERCHANT_AND_REVENUE_PLAN.md](MERCHANT_AND_REVENUE_PLAN.md): one-offer paid conversion evidence, eligibility and ownership.
- [REDACTED_JETPACK_SNAPSHOT.json](REDACTED_JETPACK_SNAPSHOT.json): no personally identifying subscriber records.
- [focus_consent_gate.mjs](focus_consent_gate.mjs), [tests](tests): fail-closed, source-only Node QA. It is **not** an authenticated production provider adapter.

The WordPress connector provides settings and diagnostics, **not** the live post-editor's native Preview email output. As such this PR cannot claim actual email rendering, footer, unsubscribe operation, or inbox delivery.

Do not infer sales or an eligible recipient count from a form, panel, download, referral click, Woo/Payhip checkout, a platform follower, or seller marketing email. Keep all six issues HOLD_UNSENT (03/05 additional merchant hold; 04 copy hold), including optional editorial variants NOT_ADOPTED.
