# R242 postcommit verification — November 9, 2026 PT

**Source of truth:** #174; parent original PR #175 exact d57ccdba3aee8f065e143e101c2945f4f3d01647. Original manuscript source has not been modified or silently substituted by R235 metadata. Earlier PR #1800 drift finding remains active.

## Native Python on exact original source (executed this run)

Re-extracted `FV_Dispatch_R236_Original_Native_Suite_Evidence.zip` (previously authenticated eight exact original files), rechecked each independently with local `git hash-object`; expected Git blobs exactly matched original #175, as cross-checked with GitHub current branch.

Six original native tests executed using `python -I -m unittest discover -s /mnt/data/dispatch_r242_work/original_175_exact/tests -v`: 6 passed, 0 failed.

Original issue blobs 01=039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8; 02=faa207ab7deafd86460d36f8c17fe62d392d0e14; 03=aeeef34efea0cc281f69901488e4501fea851245; 04=89635bfb9c8d1ff17297a59b6b5b5b2a176934ca; 05=a9dfaa450ba025a7b5113ade8a294d6dbad778dc; 06=004d558df6376d2ad6f4f79a4581e8d2c444e355; manifest=86df98ad8a84e583ff5df64ddbf8c0eaa1335b00; native test=fd7f05e30092a7ec82090993dc5d7d0e23755c8e.

## R242 real committed-source checks

Retrieved five files individually from R242 branch and verified GitHub blob IDs:
- `qa.js`: 2e5abdfe1cc7b3a61acd3fb00c81da3921a9b4ef
- `contract.json`: 337ba3c5f45c2534a2db45b2de1d4ada324079a4
- `REVIEW_ONLY.html`: 7edb0384ddd5b9e55af2b783d0bb2b73a0d4c3f9
- `AUDIENCE_TRUTH_AND_ONE_OFFER_RELEASE.md`: 5799c4be57d42f39c35f549c61943c7d935f1bac
- `MERCHANT_TRUTH_2026-11-09.md`: 1a352cb2abec1342b86dd0ee6ab9a5716c87727f

Executed actual committed `qa.js` text in isolated V8: **39/39 checks passed**, including provider-count nonadditivity, opt-in status transition, consent/PII exclusion, deduplication, commercial per-edition gates, unknown recipient counts, settled-order authority and synthetic net-revenue math. Synthetic values are not FV business figures.

17/17 independent static reviewer/contract assertions passed; HTML source contains no active merchant checkout links, scripts, forms or pixels, and has document language, mobile CSS and keyboard focus styling. **This is source-level accessibility/safety only**, not Chromium/email-client testing or a genuine Jetpack preview.

## Live-source evidence and limitations

Authenticated WordPress reads at 2026-11-09T22:31:32–33Z:
- newsletter: enabled, post auto-send OFF, full content, site can send; current sends show `never_sent_opted_out`, actual recipients NULL;
- provider counters: total 3 / confirmed 3 / unconfirmed 2 / suppressed 0 (not additive);
- distinct Followers API: total 3 / wpcom 3 / email 0 / comment 0 / partial=false;
- actual eligible EMAIL recipients UNKNOWN, because WordPress.com followers may separately enable email.
- configured 52-page welcome NOT proof of actual receipt.

Official subscriber statuses (Nov 4, 2026): https://wordpress.com/support/subscribers/ ; Jetpack post/email preview (Nov 4, 2026): https://jetpack.com/support/newsletter/ . Public seller research 2026-11-09: https://zen12.com/hnp ; https://hypnosislive.com/mental-skills/total-focus ; https://hypnosislive.com/faq . Sender legal requirements: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business .

**NOT TESTED:** actual private row-level email subscription statuses; full eligible audience; final welcome received; native Jetpack email preview; received MIME/preheader, publisher physical mailing address/unsubscribe functionality; approved partner EMAIL terms/earning URL/live guide; actual purchase, tracking/attribution, realized commission; production browser; real CI. No subscriber data exported or exposed.

**Release:** 6/6 HOLD_UNSENT, 03/05 HOLD_MERCHANT. No email/test send, WordPress content or settings writes, list additions, account spending, merchant tracking, social actions or published changes. Net revenue per 1000 qualified-human sessions NOT_COMPUTABLE. Next action: private Jetpack Email subscription status count reconciliation, not further manuscript variations.
