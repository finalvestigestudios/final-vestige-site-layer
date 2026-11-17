# R422 — QA execution receipt / exact source provenance / release HOLD

Date: 2026-11-17, 03:34–03:55 PT. Owner: Final Vestige Dispatch. Master [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), baseline [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), last [#2858](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2858), owner [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). **No WordPress/Gmail message/subscriber/social/affiliate writes, no test email, no expense, no PR merge.**

## A. Original campaign suite was independently executed first

- Read #175's actual current head, `d57ccdba3aee8f065e143e101c2945f4f3d01647`; all **eight** manifest/issue/test source Git blob identities from that head match the eight byte-identical files in the preexisting QA archive.
- Local `PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s campaign-2026-mind/tests -p test_campaign.py -v` under Python **3.13.5**: **6/6 PASS**, exit 0. This confirms static guards only, not delivery, FTC signoff or product approval.
- Verified Git blob hashes: manifest `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00`; issues 01–06 respectively `039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8`, `faa207ab7deafd86460d36f8c17fe62d392d0e14`, `aeeef34efea0cc281f69901488e4501fea851245`, `89635bfb9c8d1ff17297a59b6b5b5b2a176934ca`, `a9dfaa450ba025a7b5113ade8a294d6dbad778dc`, `004d558df6376d2ad6f4f79a4581e8d2c444e355`; test `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`.

## B. New R422 source tests (test fixture, not production signup integration)

- Node **v22.16.0** with native `node --test dispatch/r422/test_consent_truth_gate.mjs`: **25/25 PASS**. It covers normal/no-query Focus gift visibility, arbitrary nonblocklisted `subscribe` values, blocked query states, simulated subscriber CSS class, provider-witness eligibility, unconfirmed, suppressed, opt-out, wrong scope, forged browser proof, nonopaque identity, PII field, dedup and preserved 4:2 campaign HOLD. All provider records used by this suite are **synthetic**. Its one conditionally eligible mock is NOT a genuine `confirmed_signup` or subscriber count.
- After commit, both JS source blobs independently fetched from GitHub and matched the exact locally executed bytes: `consent_truth_gate.mjs` `31b0a572f9377a718bf88c03d61f4b4e1f1edaab`; `test_consent_truth_gate.mjs` `c183cd943534f09d9a93f480278d1fc1cecfd54e`.
- **Source-boundary limitation:** Focus gift script was observed in authenticated live WordPress #1579; R422's model follows its branch conditions. The browser did NOT execute the live page itself. No live subscriber record was used.

## C. Static review-board QA

Eight new source files were fetched from the exact GitHub branch. V8 read-only assertions: **30/30 PASS** on accessibility landmarks, one H1, skip link, mobile CSS, all three `scope=col` headers, safe first-party and official-source URLs, absence of scripts/forms/trackers/merchant checkout, proper HOLD, dashboard definitions, official FTC/merchant URLs, and denial of fabricated signup/sale status. **7/7 deliberate HTML release-unsafe mutations rejected**. First pass caught an *overly lax header mutation assertion* and an *overly specific copy check*; corrected the **QA assertions** and reran successfully, without changing the HTML. Exact HTML Git blob: `830aedb8daf43e4b8143614a9de348e64868ad76`; plaintext Git blob: `5abdf964a10b7e87189b7ec18a08d7115c843a96`.

**Not tested:** full native Chromium accessibility or real received HTML/text MIME; actual WordPress editor Preview; functional unsubscribe; legal publisher postal address; visitor-verified Fieldbook download; affiliate contract or checkout; conversion reporting. Offline review board is **NOT** the Jetpack email template.

## D. Authenticated platform witness

- WordPress as-of **2026-11-17 11:36:32 UTC**: `subscriptions=true`; `site_can_send=true`; new-post auto-send OFF; recent five posts `never_sent_opted_out`. WordPress Settings as-of **11:37:22 UTC**: full email, no-reply, welcome still links configured Fieldbook.
- Newsletter dashboard 3 total / 3 confirmed / 2 unconfirmed; separate Stats Reader 3 / email 0 / comments 0 / no partial error. Not additive or proof of distinct inboxes.
- Live Focus script has query or CSS condition for exposing the free Fieldbook. The page explicitly allows downloading before confirmation; client gift access cannot be used as provider consent evidence.
- Connected Gmail scoped search for current welcome phrase/title after Oct 28 returned 0 messages in the queried account; this is a limited negative, not proof that no subscriber ever received it.
- Official product source check: https://zen12.com/about / https://zen12.com/secret/ / https://hypnosislive.com/mental-skills/total-focus / https://hypnosislive.com/faq . Seller claims and prices do NOT prove Final Vestige affiliate EMAIL rights.
- Official legal/platform docs: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business and https://wordpress.com/support/newsletter/email-appearance/ .

## E. Release decision / revenue truth

**ALL SIX HOLD_UNSENT.** 03 and 05 `HOLD_MERCHANT`. Original 04 `HOLD_COPY`. No optional copy adopted. Required founder final campaign approval, unique provider-confirmed eligible recipients, independent received welcome, real Jetpack native preview, lawful FV postal identity, functional unsubscribe, individual approved offers and paid settlement still **UNVERIFIED**.

With no independently audited qualified-human-session denominator and no settled order/refund/fee crosswalk, **realized net revenue per 1,000 qualified-human sessions = NOT COMPUTABLE**, not $0 and not an inferred conversion rate.
