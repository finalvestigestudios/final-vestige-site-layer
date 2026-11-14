# Dispatch R362 — the free-PDF/confirmed-lead distinction (source only)

**Status:** DRAFT / NO SEND / NO PUBLISH / NO MERCHANT LINKS. Stacked on Dispatch R361 PR #2516, preserves the exact six original manuscripts of master PR #175 and the four editorial/two merchant-review allocation. No rewrite, adoption, change to WordPress, Grok, Focus, Mind, homepage or PR #49.

## Why this sprint exists

The publicly rendered [/focus/](https://finalvestige.com/focus/) presents a **Download the Seven Day Focus Fieldbook** link, plus a separate notice asking the user to confirm their subscription. This is good for user access, but means a download action cannot establish newsletter consent or delivery. The URL is also present in the configured Jetpack welcome message. The public PDF fetch itself returned a cache-miss error in the independent crawler; successful anonymous delivery has **NOT** been demonstrated. The WordPress media-library inventory finding in R361 is an existence check, not a received-message/guest-download receipt.

### Deliverables

- [FOCUS_CONSENT_TRUTH.md](FOCUS_CONSENT_TRUTH.md): page evidence, precise funnel event definitions and two independent verification paths.
- [ONE_OFFER_BUYER_SEQUENCE.md](ONE_OFFER_BUYER_SEQUENCE.md): a non-sending reader progression preserving exactly six slots, with merchant selection blocked until account proof.
- [RELEASE_AND_CLAIM_QA.md](RELEASE_AND_CLAIM_QA.md): current WordPress settings, 3/3/2 non-additivity, merchant seller-claim alignment, CAN-SPAM and native-email pass/fail.
- [funnel_truth.py](funnel_truth.py) / [test_funnel_truth.py](test_funnel_truth.py): pure offline, PII-minimizing read-only receipt classifier and 32 synthetic regression tests.
- [QA_EVIDENCE.md](QA_EVIDENCE.md): actual execution and exact Git blob verification.

The classifier **never returns SEND_READY**. Its provider-labelled confirmation and traffic events are only *input candidates*, not evidence of actual real-world leads, sales or attribution. This deliberately differs from optimistic engagement dashboards.

## Source-of-truth cross-team ownership

**Dispatch:** Issue #174, consent/preview/subject/release acceptance. **Focus/Claude:** Issue #129, private recipient eligibility, fieldbook delivery and first-party analytics. **Mind/Commerce:** Issue #171, named affiliate EMAIL rights, issued links, exact checkout and live pre-sell. **Grok/Praxxis:** existing Drive TASK-008, source asset IDs and real social distribution. **Conversion:** Issue #820, only independently paid settlements included in revenue. Founder retains final sending and production approval.

This is a zero-cost, no-list, no-send verification sprint, not a new marketing platform.
