# R75 — channel reality proof, not another sending system

This isolated draft adds **three things that were not previously resolved**: a read-only comparison of published Dispatch vs Focus signup expectation text, a count-only capture of current WordPress newsletter diagnostics, and a strict human-evidence interface that can **never** grant permission to send or certify legal/merchant approval.

## Review
- Open [REVIEWER.html](REVIEWER.html) locally for the accessible static decision board; [REVIEWER.txt](REVIEWER.txt) carries the same decisions without styles or scripts.
- Read [RELEASE_DECISION_RECORD.md](RELEASE_DECISION_RECORD.md) for live WordPress evidence (2026-11-02 21:33 UTC), the 6-edition source/offer ledger, official seller and WordPress links, CAN-SPAM nuance, signup consent gap, attribution limitations, and real blocked paths.
- The recorded [count_only_attestations.json](count_only_attestations.json) deliberately has eligible count null and all human/merchant evidence fields false. **Never enter names, email addresses, postal address text, raw MIME, tokenized links, tracking parameters, actual customer data or account secrets.**
- No new landing pages or newsletter tool. No edits to original PR #175 or PR #201, no page modification, no site settings, and no changes to homepage/PR #49.

## Run the existing Python test lane
From repository root:

    python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v

The R75 suite lives at tests/test_r75_channel_consent_proof.py and validates immutable 4:2 HOLD status, privacy/strict schema, lack of synthetic customer data, disputed nonadditive counters, confirmed-vs-eligible distinction, two isolated named-product holds, and fail-closed behavior even when humans tick all boxes. It does not verify a live send, native rendering or affiliate authorization.

## Produce offline reviewer evidence
From repository root, with only the **count-only** JSON:

    python -I dispatch/campaign-2026-mind/r75-channel-consent-proof/channel_proof.py \
       --input dispatch/campaign-2026-mind/r75-channel-consent-proof/count_only_attestations.json \
       --output-dir /tmp/fv-dispatch-channel-proof

Three outputs are generated: JSON with whitelisted booleans/counts, plaintext, and accessible HTML. Each says HOLD_UNSENT. Input shape is exact, file size limited to 16 KiB, and any unrecognized fields (including leaked subscriber information) fail with a generic error, without echoing the input. Path and raw content never appear in stdout.

The tool is a **human claim register**. A true check box does **not** cryptographically verify evidence, prove CAN-SPAM compliance, authorize mail or enable sending. Even an all-true fixture yields send_allowed=false and HOLD_MERCHANT for slots 03 and 05. GitHub tests only demonstrate the code behaves as designed.

## Actual external evidence needed
1. Founder choice on final six manuscripts/subject titles and the approved site-first excerpt model.
2. Separate founder approval to amend the consent wording on /dispatch/; the proposed copy has not been edited into WordPress.
3. Private native WordPress email-active subscriber count. Avoid inferring 4 from total2/confirmed2/unconfirmed2.
4. Qualified Final Vestige business mailing address, native preview, real approved received email, rendered HTML and plain disclosure/footer, working unsubscribe, and actual Fieldbook welcome receipt.
5. Specific partner acceptance **and** permission for email promotion of **Zen12** and **Total Focus**, verified approved warm-up guides and actual tracking/link requirements. Independent buyer privacy and refund/claim check.
6. **Explicit final founder approval** of copy, audience and sends. Until then no sending, scheduled post, WordPress publishing or subscriber contact.

Relevant work: [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171), original [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), pinned R74 [PR #674](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/674), per-issue [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201).