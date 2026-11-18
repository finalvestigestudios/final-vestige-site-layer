# R435 executed QA receipt — 2026-11-17 16:xx PT / 2026-11-18 00:xx UTC
**Review-only. No delivery or revenue verified.** Base [R434 PR #2930](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2930) at exact commit `4103ed1856c31f8f359cb8f4178e021500a8d500`; master manuscripts [#175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175), 4:2 gate [#201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201), tracking owner [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820). All canonical manuscripts untouched, no alternative adopted.

## Actual source/readback and test execution
Seven initial R435 files were **created on isolated branch, re-fetched independently from GitHub** with these exact returned Git blob IDs:

| File | Git blob SHA |
|---|---|
| `README.md` | `38b3dbbfce92128f7a44de5a80d1ba1c1ace0463` |
| `FOCUS_UI_VS_CONSENT_WITNESS.md` | `8ce217f551f9bd4062fa3eb1fccdcb2d0538d2ed` |
| `confirmed_signup_contract.cjs` | `646911f263f1b9b23ffc87c37bee3c1a4af74fd1` |
| `test_confirmed_signup_contract.cjs` | `478b78843eb31169007f860ed7d61ddbcbadd2e0` |
| `ONE_OFFER_PROGRESS_PATH.md` | `c8076a5930d9c7b7585b6f13648625ab285c667d` |
| `MERCHANT_EMAIL_RIGHTS_DOCKET.md` | `83cb570d8723df3b31cdee0f042e8ded05efe7a5` |
| `OFFLINE_FOUNDER_WITNESS.html` | `09af74cf636678163497412aee60a50d1c9ecf69` |

**Executed exact committed code in V8 using a CommonJS require shim: 46/46 assertions PASS.** Verified (synthetic test fixtures only): UI clicks and query values never count as leads; provider opaque, eligible, deduped consent transitions can count; PII-bearing evidence rejected; duplicate transition counted once; six bad query values do not reveal gift; pending arbitrary query may reveal gift in current UI; tests never grant send authority. Real subscribers were not queried for identification and no provider transitions were created.

Static source/HTML/accessibility/security guard: **54/54 PASS** against the seven fetched GitHub blobs. Initial 53/54 included one false-negative checker looking for the exact string "source-only" in README; its expectation was corrected to the actual "Review-only", and the complete 54-check pass rerun. No source file was modified to appease the assertion. Checks include complete no-JS offline board structure, viewport, lang/main/headings, details summary, keyboard focus, no form/tracking/script/iframe, first-party source links, and no network/sending API in the consent code.

GitHub compare `4103ed1...R435` after seven files: **7 ahead, 0 behind; exactly seven NEW `dispatch/r435/` files and zero deletions**. This receipt makes the eighth additive file; recheck final HEAD and diff after receipt.

## Authenticated external evidence
At 2026-11-18 00:31:52–00:45 UTC, WordPress newsletter status: 3 total / 3 confirmed / 2 unconfirmed, 0 suppressed and 0 paid; auto-send default OFF; five recent notices opted out. Settings: newsletter enabled, full mode, reply-to no-reply, categories disabled, existing configured 52-page welcome. Live /focus/ stored page: `fvf-gift-v2` shows PDF panel for nonblocked nonempty `?subscribe=` or `is-subscriber` CSS class; **neither is authenticated consent evidence**. Media 1737 `application/pdf`, 599,946 bytes, same PDF URL in page/welcome. Published posts 1922 change blindness, 1924 Mesmerism, 434 Apollo 1 each confirmed at their first-party WordPress source URLs. WordPress page/editor source is not an actual browser test or email-client receipt.

Official merchant pages read: https://zen12.com/about ; https://zen12.com/secret/ (distinct offer); https://hypnosislive.com/mental-skills/total-focus ; https://hypnosislive.com/faq . FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . The public promo claims and prices are not attributable to an authorized FV issued referral account. Current website PDF HTTP fetch via public web returned cache miss/inaccessible, **not a proven dead link or HTTP 404**.

## Deliberately NOT tested or established
No native Node invocation of the new R435 scripts (V8 shim only); no production WP browser/Jetpack native Preview; no genuine inbox, welcome receipt, unsub functionality or FV mailing postal address; no individual subscriber query; no actual affiliate grant, email creative permission, live offer guide, merchant checkout or settlement; no real 7/30-day paid cohort. Native **original PR #175** six-test Python run was previously demonstrated in R434 (receipt linked above); not rerun natively in R435. No paid traffic, email sends, test emails, WordPress writes, subscribers contacted, affiliate promotion, new platform/list, social post, PR merge, money spent or change to PR #49.

**Verdict:** R435 source QA PASS; business/release `HOLD_UNSENT`, commercial `HOLD_MERCHANT`, qualified net revenue per 1,000 human sessions **NOT_COMPUTABLE**.
