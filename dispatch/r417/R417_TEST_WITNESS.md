# R417 post-commit / exact-source witness — no send

**Scope:** isolated `dispatch/r417/` stacked on PR #2833. No changes to canonical PR #175, per-issue QA PR #201 or homepage PR #49.

## Native campaign baseline

- Current master PR #175 HEAD independently read as `d57ccdba3aee8f065e143e101c2945f4f3d01647`.
- The archived canonical source archive supplied in prior R409 QA was unpacked in this run; `git hash-object` on each of the original eight campaign files matched the previously recorded exact #175 blob list, with the manifest and original test source additionally rechecked through GitHub at the current PR HEAD.
- `python -m unittest discover -s dispatch/campaign-2026-mind/tests -v`: **6/6 PASS**.

## New R417 native test on GitHub-identical source

The following three exact GitHub blob hashes matched the files executed locally (not merely equivalent content):
- `OFFER_SURFACE_SNAPSHOT.json`: `002e87247ab4d95c0673b1bc0ae48dbae406fc48`
- `merchant_drift_gate.py`: `fec93e4cc237753dcce3208d2395b9edd73551fd`
- `test_merchant_drift_gate.py`: `f7111cf071279eee7af8291a6a912092817b7f60`

`python -m unittest -v test_merchant_drift_gate`: **18/18 PASS**. Gate output: global **HOLD_UNSENT**; Issue03 **HOLD_MERCHANT** (three distinct public price contexts, 14 missing/conflicting flags); Issue05 **HOLD_MERCHANT** (two distinct price contexts, 14 flags). Tests cover wrong issue/slot mapping, malicious off-domain or HTTP source, price formatting, inferred refunds/efficacy, public link masquerading as earning authority, synthetic complete permissions, and no identifiers. All synthetic passes retain an explicit send hold.

## HTML review and limitations

Static reviewer HTML has one semantic main heading, two separately labeled cards, a table, accessible visible focus style, source links and no scripts/forms/pixels. A **locally authored** static reviewer specimen was tested in offline Chromium with `page.set_content` at 320, 360, 390, 430, 768, 1440, 1920 pixels: **7/7 PASS**, no horizontal overflow or JS errors. Local specimen is **not byte-identical** to the final GitHub HTML; do **not** claim these browser results prove the exact committed HTML. Final GitHub HTML was independently fetched and checked for structure and prohibited active elements; no rendered Jetpack email or real client acceptance test occurred.

Exact GitHub source static QA initially returned **18/19** because a naive string test for `ref=` incorrectly matched HTML anchor `href=`. This is a **false positive in the check**, not an affiliate-link finding. Replaced by validation of actual `href` hosts and known tracking parameter keys; source HTML unchanged. No offered or merchant earning URL exists in the artifacts.

## Authenticated site observations

Jetpack newsletter enabled, new-post automatic email off, full format, no-reply; welcome includes original Fieldbook URL but delivery not observed. Total3/confirmed3/unconfirmed2, separate Reader3/email0; distinct recipient eligibility unknown. Private commercial EMAIL permission, referred checkout, FV mailing address, operational unsub, native email Preview and paid settlements unverified.

**All six original campaign emails HOLD_UNSENT.** No test email, customer contact, WordPress write, affiliate link, signup list, social post, provider subscription, PR merge or expense.
