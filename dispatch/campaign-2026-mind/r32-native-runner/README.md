# Dispatch R32 — native Node CI coverage (DRAFT, NO SEND)

**Parent**: draft PR #377, exact SHA f6a5170f8f868a8eb4b044a7fca16960670f078b. Owner: [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); affiliate coordination [Issue #171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). Original master PR #175 and gates PR #201 remain unchanged. Homepage/frozen PR #49 out of scope.

## Material gap fixed

The previously successful [GitHub Actions run #41257670345](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/41257670345) checked out exact PR #377, ran 154 Python tests, checked preview JavaScript syntax and checked generated snapshot integrity. It DID NOT execute the actual functional Node assertions in R11, R12, R22 and R27–R31. In particular the R31 39 assertions and 15 adversarial mutations were run in a read-only V8 shim, not in Node20 on GitHub Actions.

R32 adds a Python-unittest bridge in tests/test_r32_node_runner.py, automatically discovered by the EXISTING scoped Dispatch workflow (no workflow edits). On the exact Actions checkout, it launches eight native JavaScript test scripts: R11 native-delivery source gate, R12 merchant evidence gate, R22 default excerpt audit, R27 two excerpt models, R28 source/HTML/plaintext/Gutenberg parity, R29 draft sentinel and inbox risks, R30 editorial excerpt facts, R31 two-hop click-path and disclosure gate. Two run with the built-in Node TAP test runner; six run their committed CJS assertions. The bridge rejects nonzero exits, script absence, timeouts and success-marker absence. No internet, WordPress edits, mail, PII or paid services are added.

Reproduce from full checkout (Python 3.11+, Node 20+):

    python -I -m unittest discover -s dispatch/campaign-2026-mind/tests -v

**Honest proof boundary**: a local synthetic test of the bridge covered eight marker formats plus three fail-closed cases (nonzero exit, fake/missing success marker and missing script). That is NOT evidence that the eight real JS audits pass. Exact hosted Actions checkout must be observed separately. The bridge is an engineering safeguard, not a proof of native Jetpack email delivery or CAN-SPAM compliance.

## Source of truth checked 2026-11-01T01:34Z

Authenticated WordPress: Jetpack newsletter enabled, site_can_send=true, new-post automatic emails OFF, global content mode excerpt, recent_sends empty, the 52-page Focus Fieldbook welcome configured but receipt unverified. Counters total=2/confirmed=2/unconfirmed=2 are nonadditive and are not recipient identities. Published /dispatch/ page 523, /focus/ 1579 and Editorial Standards page 17 checked unchanged. Connected Gmail search yielded consumer merchant promotions but no Final Vestige-specific Inspire3 approval, Zen12/Total Focus email-channel permission or received final welcome. No addresses or account secrets logged.

Relevant current official seller references: https://zen12.com/about (Beginner first six levels/24 MP3, Premium all twelve/48 MP3, Advanced last six/24), https://hypnosislive.com/mental-skills/total-focus (seller lists 33 minutes and 47 MB), https://inspire3.com/ll/ (another product's swipe/affiliate approval page, NOT Zen12/Total Focus permission). Seller claims are not independent efficacy findings. Prices, checkout/refunds, approved creative and eligible tracking link remain unverified.

Jetpack documentation: https://jetpack.com/support/newsletter/customize-the-newsletter-experience/ (updated 2026-10-28) and https://wordpress.com/support/newsletter/email-appearance/ (reviewed 2026-10-06). FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

## HARD HOLD and operational decision

All six issues HOLD_UNSENT; Issues 03 Zen12 and 05 Total Focus additionally HOLD_MERCHANT. Original four editorial/two proposed commercial mix unchanged. No send, test-send, schedule, WordPress post publication, settings change, subscriber import/export/contact, paid tools, email partner contact or live affiliate URL activation. A valid physical address belonging to Final Vestige, a working real-email unsubscribe link, genuine received native preview, eligible recipient evidence, published reviewed buyer guides, written product-specific affiliate email authorization and founder's final campaign approval remain mandatory. The successful offline tests do not authorize release.
