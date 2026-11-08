# Dispatch R146 — reproducible, non-sending QA record
**Date:** November 5, 2026, after connected WordPress snapshot at 21:31 UTC. **Trust level:** source-controlled fixtures + executed local native Python, NOT hosted CI, NOT live email rendering, NOT recipient verification.

## Test provenance
1. Read GitHub [master PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) at exact commit `d57ccdba3aee8f065e143e101c2945f4f3d01647`; fetched the six issue source blobs, manifest and original Python suite via GitHub. Compared **8/8 Git object hashes** to independently extracted local archive; README is unchanged and not included in the archive hash comparison.
2. Executed the original unmodified Python suite in the local environment with `python -m unittest discover -s master/dispatch/campaign-2026-mind/tests -v`: **6 tests / 6 passed**.
3. Executed new `python -m unittest -v test_native_contract` using new exact source files and redacted observational fixture: **33 tests / 33 passed**. Checks cover synthetic-only evidence, fake opt-in, optional email-specific recipient count, nonadditive followers, 4:2 allocation, merchants 03/05, PII injection, false positive paid sale, unsafe link activation, default send toggled on, unknown delivery mode and missing postal/unsubscribe or actual PDF receipt.
4. Verified **three exact GitHub blob SHAs match locally natively executed files**:
   - `native_contract.py`: `ac5af4790e41616c67ca5ed927769d4a696b28f1`
   - `test_native_contract.py`: `66a4c6e7f1ba7b9d6b8abfcbb184ca7dd6ca8c6b`
   - `native_contract.json`: `4211ce0f9de6c64764e7fd3a2f54566f8c772da1`
5. `python native_contract.py native_contract.json --out audit_output.json` produced **6 HOLD_UNSENT** individual editions, **2 HOLD_MERCHANT**, **5 shared missing-proof blockers**, unknown email-eligible count and unknown realized net revenue. A synthetic "all true" adversarial scenario remains **HOLD_UNSENT** even if someone manufactures all attestation booleans. These gates cannot grant send permission.
6. No GitHub-hosted workflow run or actual Jetpack email was tested. No mobile render of a received email was tested. No browser claim about live signup or public PDF retrieval was made.

## Evidence and boundaries of the snapshot
- WordPress native newsletter read-only status `2026-11-05T21:31:00Z`: total 3, confirmed 3, unconfirmed 2, imported last 24h 0; five recent post notices never sent, site can send. Reported counters overlap and do not prove 3 email-eligible recipients.
- WordPress read-only settings `2026-11-05T21:31:05Z`: subscriptions true; automatic post-email default false; **full**; sender Final Vestige Studios; no-reply; newsletter categories disabled; configured 52-page Fieldbook welcome URL.
- WordPress media #1737: registered PDF, `application/pdf`, 599946 bytes; actual public 200 response, final file bytes/52 pages and welcome receipt NOT independently established.
- WordPress read-only slug lookups of `zen12-guide` and `hypnosis-live-guide` returned no published post/page by those exact slugs; this does **not** prove no other Mind draft or approved route exists.
- Jetpack followers summary: WordPress.com followers 3, email followers 0, separate counters from native subscriber total/confirmed.
- Connected Gmail *targeted* searches showed no matching named Inspire3 affiliate acceptance/permission to email, no proven received 52-page Dispatch welcome. A generic Refersion "account pending" email was read and does NOT name Inspire3 approval; another merchant's MenthorQ affiliate promotions were unrelated. Absence from one mailbox is NOT evidence that permission is absent everywhere.
- Official support [email appearance](https://wordpress.com/support/newsletter/email-appearance/) explicitly describes preview in editor; no new email platform or subscriber list is needed. Preview is blocked on editor access/authorization and no campaign WordPress draft was created.
- FTC [CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) physical mailing address, identity and working opt-out must be evidenced in the real sent-mail rendering, not a simulated placeholder. Merchant copy must distinguish sales claims from proof.

## Independent founder-relevant outcome
Current configuration demonstrates a **post-based newsletter with full-content delivery** and disables auto-post notices. It does not independently evidence a *triggered* follow-up sequence, per-reader behavior targeting, a separate custom inbox preheader control or ability to measure newsletter→paid order attribution automatically. Do not describe the proposed six-email pilot as a live segmented drip. Customer willingness can instead be measured through voluntary topic selection on existing first-party pages after consent and owner-approved CTA/UTM integration.

## Release decision
No new email, test send, scheduled post, new subscriber, price/affiliate link or WordPress setting. No claim of legally verified sender/footer, actual delivered Fieldbook, merchant accepted account or settled paid order. The founder's reserved campaign remains **4 editorial / 2 commercial**. **ALL SIX HOLD_UNSENT; 03/05 additionally HOLD_MERCHANT.** Snapshot is observational and must be refreshed before any release review. This code and document are read-only, require no purchased service, and never activate a send.