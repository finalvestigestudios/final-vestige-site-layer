# Dispatch R329 — canonical 6-issue editorial/subject review and native compliance evidence

**Source audited:** original master draft PR #175 head `d57ccdba3aee8f065e143e101c2945f4f3d01647`; R328 canonical preview PR #2337 head `6bf50815fcdd6f170bd30e963d6d9140c4cc120b`. All manuscript changes proposed below are **editorial review findings only, NOT source edits or founder-approved substitutions**. The 4 editorial / 2 commercial reserve remains unchanged.

## Review matrix
| Issue | Exact original subject | Credibility and conversion evaluation | Action (not adopted) |
| --- | --- | --- | --- |
| 01, editorial | The mind is not a camera | Metaphor is broadly truthful but story in original message opens generically. Shares exact same Puységur destination as #02, reducing meaningful editorial progression. | Consider R327's researched change-blindness original as a separately approved editorial alternative, or retain original with a differentiated genuinely published CTA. Do not silently replace. |
| 02, editorial | Before hypnosis had a name | Historical bridge fits Standards; avoid implying Puységur observed modern clinical hypnosis. Verify specific primary documents where claimed. | Keep archive-backed nuance; R321 alternative is review-only. |
| 03, commercial HOLD | The twelve-minute meditation question | Subject not a promise, but a product under evaluation with **nonclickable warm-up guide token**, not an actual route to checkout. Seller's hour-equivalence claim must never be borrowed as an independent conclusion. | One preapproved Zen12 comparison guide after account-specific EMAIL permissions, issued link, checkout, product claims and disclosure review. No auto-activation. |
| 04, editorial | Fourteen seconds. A much longer explanation. | The number is arresting but ambiguous without explaining endpoint. Apollo 1 time to pressure-vessel rupture differs from later crew communications, and specific ignition source remains uncertain. | Add endpoint qualifier during founder editorial review; R325 optional revision already exists and is NOT_ADOPTED. |
| 05, commercial HOLD | Before you press play on a hypnosis audio | Ethical checklist, no false guaranteed result, but buyer isn't directed to a **live** specific guide. Hypnosis Live is a catalog, not itself a SKU; Total Focus product specifics are more useful. | Verify exact Total Focus format and current checkout *before* pricing; reviewer R324 is not adopted. Commercial channel permission separate from #03. |
| 06, editorial | What did seven days of attention reveal? | Useful closing question, but returning existing subscribers to /focus/ creates a redundant re-subscription path and can inflate apparent signup intent. | Consider an existing research page or direct already-owned free exercise; R326 remains optional and NOT_ADOPTED. |

**Manifest preheaders are proposed editorial copy only.** No authenticated evidence establishes a configurable Jetpack preheader field, actual inbox text preview or suppression of WordPress-generated excerpt. Do not certify them as delivered.

## Preflight copy/CTA rules
- One primary CTA per edition; editorial source links in footnotes or natural explanatory passages do not become multiple competing purchase buttons.
- Commercial issues #03/#05 must not expose active merchant links, fabricated price/discount, unverified merchant refund promises, claim efficacy or unverified fulfillment of the requested focus outcome.
- Any qualifying recommendation or earning link needs understandable near-offer disclosure. Do not imply a single global disclosure page is sufficient.
- Footer placeholders like `[[VALID_POSTAL_ADDRESS_REQUIRED]]` and `[[JETPACK_UNSUBSCRIBE_LINK_MUST_BE_VERIFIED]]` must intentionally fail release. Never replace them with an invented address or generic WordPress host.
- Keep subject truthful when WordPress derives it from post title. HTML email-safe static previews are **not** evidence of real WordPress rendering or actual inbox receipt.

## Independently checked on this run (2026-11-13)
1. Read #174 and #171 newest comments, #129 and #820 background, #175/#201/#2337 PR head state, authentic WordPress `/dispatch/`, `/focus/`, `/editorial-standards/` pages, exact newsletter settings and status, and Grok TASK-008 assigned source. All original and prior review branches are unmerged.
2. Original #175 SHA remained `d57ccdba3aee8f065e143e101c2945f4f3d01647`. The R328 local QA ZIP's archived source has exact Git blob matches for remote manifest `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00`, unit suite `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`, commercial #03 `aeeef34efea0cc281f69901488e4501fea851245`, #05 `a9dfaa450ba025a7b5113ade8a294d6dbad778dc`. Reran **native Python 6/6 PASS** at this run.
3. Fresh live WordPress snapshot **12:31 UTC 2026-11-13**: enabled, can send, no blockers, new-post auto email OFF, format full, welcome configured, from name "Final Vestige Studios", no-reply mode. Subscriber count reports **total=3, confirmed=3, unconfirmed=2**; these categories are overlapping and do not establish unique eligible recipient count. Five sampled post records individually `never_sent_opted_out`; do not generalize to a lifetime send count.
4. Connected Gmail: the **October 25 confirmation-request MIME** was read privately. The message has the subject "Confirm your subscription", and contains neither the 52-page Fieldbook nor evidence of delivered welcome. **This is not native received Dispatch marketing email.** No recipients or token links were exposed. Focus's raw widget still needs R320's distinct confirmation-proof review.
5. 2026-11-13 targeted account-specific Inspire3 Gmail search did **not** find authorization for affiliate promotion by email. Seller's public sales/recruitment pages are not account-specific permissions.
6. R329 committed `receipt_guard.cjs` + `receipt_guard.test.cjs` were fetched back from GitHub and executed using an **isolated V8/CommonJS shim** against exact GitHub blob contents: **23/23 PASS**, including all-false, negative, privacy and nonrelease scenarios. Initial test case had an erroneous expectation about absent body unsubscribe; fixed on GitHub and re-executed. The two exact GitHub blob IDs were independently matched by `git hash-object` in the native environment, and `node --test dispatch/r329/receipt_guard.test.cjs` **23/23 PASS**. Log preserved privately; see `NATIVE_EXECUTION_EVIDENCE.md`. No original files changed.
7. No native WordPress preview, controlled test send, client receipt, subscriber event export, merchant checkout or paid settlement was performed. A raw MIME guard is offline evidence analysis only; its output remains `HOLD_UNSENT` even when all booleans are supplied.

## Current decision
All six `HOLD_UNSENT`; #03 and #05 extra `HOLD_MERCHANT`. R329 code is NON-SENDING and source-controlled, not deployed. No subscriptions, WordPress content/settings, mailings, social posts, affiliate activation, analytics deployment or spending changed. Net revenue / 1000 qualified humans is NOT COMPUTABLE because actual settled order net value and verified qualified-human denominator are absent.

### Source documents
- https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174
- https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171
- https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175
- https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201
- https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2337
- https://finalvestige.com/editorial-standards/
- https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
