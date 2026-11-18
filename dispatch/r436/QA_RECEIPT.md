# Dispatch R436 executed QA evidence — 2026-11-18T01:33:35Z
**Not a production release, email-client test, permission grant, or revenue report.**

## Exact committed source and execution
- WordPress live read: ID 1579, published, last modified `2026-11-16T14:54:58`; stored source length **31,961 characters**. Read-only only.
- GitHub source `focus_patch.mjs`: blob **b24adf941ed0fd5873c225a64281b17e9dc2a210**, 3,681 bytes. `test_focus_patch.mjs`: blob **9df2a8543f67f88352b578d07a2646ad86e360bc**, 4,417 bytes.
- Both exact GitHub blobs were independently fetched and compared by `git hash-object` against the local executed copies; hashes match. Native **Node 22.16.0 `node --test test_focus_patch.mjs`: 17 tests passed, 0 failed, exit 0**. A second in-tool V8 execution on fetched committed code passed 17/17 test cases, 58 assertions (Node-compatible assertion shim).
- Against the **actual authenticated live WordPress page** the patch generator planned the expected two text substitutions without writing: 31/31 checks passed, no failures. It retained the original Jetpack subscriptions block, public PDF link, existing PDF event count, untouched surrounding text and zero `confirmed_signup` events; removed only the arbitrary query/class reveal logic and associated `after_signup` attribution. Proposed page was 31,637 characters, stored page still 31,961. No API call wrote the proposed content.
- Offline preview GitHub blob **36f045acc31deb62b459c85a76350611eb704702**: static source checks confirm English locale, named content landmark, visible PDF section, mobile viewport, keyboard focus, no forms/scripts/third-party tracking. **No native browser screenshot, Lighthouse, accessibility audit, real HTTPS PDF receipt or Jetpack MIME rendering was performed.**
- Original master PR #175's **native Python 6/6** test run at exact head d57ccdba was recorded in previous R434 receipt; **not rerun natively this R436 sprint**. Master files were preserved, original issue/manifest no edits.

## Unsafe mutation coverage
**Rejected:** stale WordPress modified timestamp, duplicate/absent exact gift block, duplicate/absent reveal script, absent Jetpack subscription block, already-modified source, empty or null body. Synthetic URL values (`?subscribe=success`, `confirmed`, `blocked`, `is-subscriber`, etc.) cannot alter the proposed result. None of these tests asserts a genuine subscriber action.

## Legal / commerce hard holds
No named Final Vestige Inspire3 EMAIL permission, issued earning URL, live vetted guide, independently confirmed checkout or settled sale. No unique receiving inbox count, actual welcome receipt, native Jetpack preview, or Final Vestige publisher postal/unsubscribe proof. WordPress provider reports 3 total / 3 confirmed / 2 not-confirmed, which are **non-additive** and not a validated eligible recipient population. Email default remains OFF, recent five posts never sent (not a claim about all time).

## Delivery boundary
No WordPress post/page/settings/subscriber writes, no email or test email, no imports, no new platform, no affiliate link activation, no paid subscription, no real user contact, no merge, no founder adoption of copy. Six issues remain `HOLD_UNSENT`, with issues 03/05 additionally `HOLD_MERCHANT`. Homepage PR #49 untouched. Realized net revenue / 1000 qualified-human sessions **NOT_COMPUTABLE** because independently audited numerator/denominator are unavailable.

## Reproduction
`node --test dispatch/r436/test_focus_patch.mjs` under Node 22+. On the authorized read-only WordPress page, supply current raw source and `modified` to `proposeFocusPatch()` **locally**. The method returns an unpublishable proposal; no writer exists. Halt if live version or exact anchors change.