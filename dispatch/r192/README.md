# R192 — Offline Dispatch evidence, conversion, and native-email preview readiness

This isolated review PR is stacked on Dispatch R191 #1457. Canonical #175 six issues are **unaltered**, per-issue release QA #201 is not duplicated, and homepage #49 is frozen. Issue #174; commercial #171; Focus #129; conversion #820.

Files: original unsent archival editorial alternative 02 (Markdown, plaintext and static accessible HTML); precise sales-claim/permission and conversion decision matrix; false-by-default attestations; Python offline proof-checker and 19-test adversarial suite.

Test: python -I -m unittest discover -s dispatch/r192/tests -v . Native synthetic tests pass 19/19 against the exact committed Python source blobs. Optional CLI: python -I dispatch/r192/offer_consent_gate.py dispatch/r192/attestation.example.json 03; prints HOLD, never a sending authorization. No network, no subscriber PII, no installed tracker. A referenced attestation is not automatically authenticated and even complete evidence yields HUMAN_REVIEW_CANDIDATE_ONLY, never SEND_APPROVED.

The original six-test Python suite on PR #175 is **not** represented as natively executed during this R192 session. Previous native run and GitHub source identities were independently inspected. HTML is handcrafted, not received or rendered by Jetpack. Offline Chromium with system /usr/bin/chromium evaluated 320/360/390/768/1024/1440 widths: initial horizontal overflow on legal hold tokens FAIL, repaired with anywhere-wrap; final all 6 PASS, no JS errors, no scripts/images and one primary CTA + 2 source links. Screenshots and standalone extended review files are in companion offline QA bundle.

Fresh 2026-11-07 19:29 UTC WP reads: Jetpack Newsletter enabled, automatic emailing OFF, full format, welcome set, counted=3, confirmed=3, unconfirmed=2; follower breakdown WP.com=3, email-only=0, actual email-eligible aggregate UNKNOWN. Real welcome, publisher postal address, actual recipient opt-out, permitted partner email link, native Jetpack preview and settled sales UNVERIFIED.

**NO SEND, NO WORDPRESS OR SUBSCRIBER WRITE, NO LIVE AFFILIATE CTA.**
