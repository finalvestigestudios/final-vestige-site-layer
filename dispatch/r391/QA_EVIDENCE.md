# Dispatch R391 — exact-source and offline QA evidence

**Status: SOURCE DRAFT, HARD HOLD, NOT ADOPTED, NOT A SEND.** Date: 2026-11-15 PT; read-only Jetpack snapshot 2026-11-16 01:30:37Z. Parent Dispatch [draft PR #2687](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2687) @ `ce33a9c60192ef2b044097e67c7dbdd9edf3f0c0`, original master [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) @ `d57ccdba3aee8f065e143e101c2945f4f3d01647`, readiness [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201). Issue [#174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174), companion Mind [#171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171). No original campaign source, homepage #49, Grok tasks, or WordPress content was edited.

## Independent source read

Read latest issue #174, #171 and #2687, all six untouched original PR #175 drafts, #201 summary/PR state, current live WP /dispatch/ ID523, /focus/ ID1579, /editorial-standards/ ID17, newsletter status/settings/followers, Google Drive TASK-008 and handoff. Gmail query found merchant promotional messages, no named final-vestige affiliate EMAIL permission; consumer advertising is NOT a partner contract or authorization.

**WordPress snapshot:** subscriptions true; 3 total/3 confirmed/2 unconfirmed/0 suppressed, separate WordPress.com followers 3/direct-email followers 0; email-eligible recipient count UNKNOWN. Full-content setting; from Final Vestige Studios, reply-to no-reply; auto-send OFF; last five post sends never_sent_opted_out. Fieldbook welcome configured with 52-page link but no evidence of actual delivery. Source calls read-only; no emails sent or triggered.

## Native original-master suite

Fetched the exact eight immutable PR #175 GitHub source blobs and independently materialized their matching source contents. Ran:
`python -I -m unittest discover -s tests -v`
in the isolated master test fixture on this run: **6 tests / 6 PASS**. Distinguish this native suite from previously reported V8 mirrors.

Original manifest exact blob SHA: `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00`; native unittest source: `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`. Six issue blob SHAs:
01 `039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8`, 02 `faa207ab7deafd86460d36f8c17fe62d392d0e14`, 03 `aeeef34efea0cc281f69901488e4501fea851245`, 04 `89635bfb9c8d1ff17297a59b6b5b5b2a176934ca`, 05 `a9dfaa450ba025a7b5113ade8a294d6dbad778dc`, 06 `004d558df6376d2ad6f4f79a4581e8d2c444e355`.

## New R391 source gate

Re-fetched the exact committed `dispatch/r391/release_guard.mjs` GitHub SHA `dde55e099dfb6adc2603026bb55be7fc389b838a`, exact source JSON and email HTML/plaintext. Independently executed `inspectIssue05` using V8 (without a Node test runner) on the fetched source: **16/16 PASS**, release `HOLD_UNSENT_NO_AUTOMATIC_OVERRIDE`. Detected **8/8** intentionally unsafe direct mutations: affiliate href injected, enabled offer CTA, deleted adjacent disclosure, tracking pixel, fabricated eligible subscriber count, invented EMAIL authorization, removed postal block, invented emailed price. The separate committed `release_guard.test.mjs` contains **27 native Node tests**, but **has NOT been run with Node** in this verification. This distinction is intentional.

## Browser and accessibility

Fetched exact GitHub offline email HTML Git blob `c13f5b2ca7e6c9f21dba236d24c200c42b3fac85`; reconstructed it into the isolated local environment and verified byte-identical Git blob SHA. Playwright with installed Chromium initially blocked navigation to a file:// URL; no browser PASS was claimed from that step. The isolated test used Playwright `page.set_content` on the exact same HTML without network access or email calls. **8/8 PASS** across 320,375,390,768,1440 CSS-pixel widths and 320/390/768 at CSS zoom 200%; no horizontal overflow, 1 disabled offer surface, 4 citation links, 0 scripts. Static contrast and screen-reader email compatibility are NOT fully tested WCAG 2.2 or delivery-client validation. Captures: 320px/390px/768px. Browser test was **offline HTML only**, not Jetpack real Preview email, sanitizer, postal footer, mobile inbox or actual delivered email.

## Exact merchant and compliance proof

Inspected exact Total Focus seller page and merchant FAQ on 2026-11-15. Merchant lists 33-minute/47-MB MP3; advertises $24.44 product price on one observed listing and different prices across earlier snapshots; no price appears in the drafted email. Merchant FAQ describes refund limits; no **referred** refund/checkout terms verified. Seller claims brain reprogramming and perfect focus; those are not established SKU-specific results by the independent [NCCIH hypnosis overview](https://www.nccih.nih.gov/health/hypnosis). Public [Inspire3 Limitless Labs swipes](https://inspire3.com/ll/) apply to a different program and do not grant email rights for Total Focus/Zen12.

Historical hook sourced to the translated [Franklin 1784 commission](https://www.gutenberg.org/files/78413/78413-h/78413-h.htm); exercise is educational, not medical or controlled scientific validation. FTC address and working opt-out remain mandatory for qualifying promotional sends; an Automattic address or unresolved placeholder is NOT acceptable. Native WordPress Preview email is separate from actual Send test email; **neither performed**.

## Gate verdict

Original six untouched, all `HOLD_UNSENT`; 03/05 `HOLD_MERCHANT`, original 04 `HOLD_COPY`. R391 Issue 05 alternative `NOT_ADOPTED`. Named account acceptance, precise SKU/email creative/affiliate link, published approved guide, current referred checkout, deliverable inboxes, actual welcome delivery, publisher postal address, functioning native unsubscribe and real email preview all missing. Independent actual paid publisher commissions and audited qualified human sessions are missing; **net realized revenue per 1,000 qualified human sessions = NOT_COMPUTABLE, not zero**.

**Zero sends or test sends, subscriber contacts, WordPress writes, new lists, settings changes, affiliate links, publishing, social queue changes, purchases, merges, expenses.** Founder retains final copy/audience/date/send/merchant approvals. More is built and independently tested, but none is LIVE.
