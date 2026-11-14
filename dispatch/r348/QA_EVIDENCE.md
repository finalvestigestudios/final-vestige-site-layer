# R348 — Exact-source QA and audit record (2026-11-13 22:33 PT / 2026-11-14 06:35–06:52 UTC)

**Disposition: HARD HOLD / NO SEND / NOT ADOPTED.** No deployment authority or founder final campaign approval. Source-only separate branch stacked on Dispatch #2434; no alterations to PR #175, readiness #201, frozen homepage PR #49, WordPress, Grok queue, merchant accounts or the subscriber list.

## Read-first evidence
- GitHub #174 current newest retrieved handoff (Mind R364): https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174#issuecomment-6872679952 ; https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171#issuecomment-6872676002
- PR #175 exact master HEAD `d57ccdba3aee8f065e143e101c2945f4f3d01647`; PR #201 exact unchanged HEAD `ef53e5a17046e3dff5a4a7e3b0f4c8fbce9cd6f6`; previous Dispatch PR #2434 HEAD `92a2a56e9fa9dbec27a23f5063259e4980c7f353`. R348 branch created from that SHA.
- WordPress authenticated live `/dispatch/` page #523; `/focus/` page #1579; `/editorial-standards/` page #17. Standards require primary sources, visible uncertainty, corrections and commercial independence. Page rendering via WordPress API is NOT a native Jetpack received-email preview.
- Existing Grok/Praxxis Google Drive TASK-008 and dated handoff read for ownership; Grok controls creator posting, Claude owns web engineering. No content queue takeover.

## Native original master tests: independently EXECUTED
Unpacked the earlier archived GitHub-source copy of the full original campaign into a fresh local directory. Compared all **eight** archived Git blob hashes to the exact live PR #175 head; all identical:
- Issue 01 `039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8`
- Issue 02 `faa207ab7deafd86460d36f8c17fe62d392d0e14`
- Issue 03 `aeeef34efea0cc281f69901488e4501fea851245`
- Issue 04 `89635bfb9c8d1ff17297a59b6b5b2a176934ca`
- Issue 05 `a9dfaa450ba025a7b5113ade8a294d6dbad778dc`
- Issue 06 `004d558df6376d2ad6f4f79a4581e8d2c444e355`
- `manifest.json` `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00`
- `tests/test_campaign.py` `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`

Executed `python -m unittest discover -s master/dispatch/campaign-2026-mind/tests -v`: **6/6 PASS** (original exact-current source). GitHub project CI was not run.

## New R348 checks
- 7 new files committed to isolated `dispatch/r348/`, no edits to six originals.
- Precommit source/static checks **30/30 PASS**.
- All seven new GitHub source blobs re-fetched from exact branch commit and non-empty **7/7 PASS**; manifest/release JSON parsed.
- Found a malformed regex in first candidate Node test, **corrected it in a second commit** before reporting validation. The corrected exact GitHub source file `verify_r348.cjs`, along with six companion files independently fetched at commit `e0fd2b3576781e694782c50a5cc2a22200aaee3a`, executed in isolated V8 with a controlled `node:test`, `node:fs`, `node:path` and strict-assert compatibility shim: **23/23 PASS**. This is NOT a native Node or hosted CI execution.
- HTML has lang, viewport, single first-party Apollo CTA, table layout, inline CSS, no script/form/iframe/images or external tracking, visible no-send banner, inert postal/unsubscribe placeholders. HTML is an offline review mock, NOT actual WordPress sanitization, browser viewport, delivered-mail proof or production CSS.
- The new subject avoids original Issue 04's unexplained "Fourteen seconds" framing. NASA safety source supports three-part hatch, cabin environment and a precise ignition point not proven; citations are in manuscript and claim map.
- Not tested: native Node CLI for new module, browser rendering on real phones, native Jetpack Preview email, actual inbox receipt, final postal address, real unsubscribe action, welcome receipt, privacy-compliant production attribution, merchant checkout / affiliate settlement.

## WordPress newsletter — fresh authenticated read-only snapshot (2026-11-14 06:35 UTC)
`subscriptions=true`, `email_new_posts_by_default=false`, `email_content_format=full`, `reply_to=no-reply`, sender "Final Vestige Studios", 52-page welcome configured. `site_can_send=true` reflects technical eligibility, **NOT** founder send approval. Count anomaly total=3, confirmed=3, unconfirmed=2; cannot be added, and actual eligible email recipients remain **UNKNOWN**. Last five sampled post notifications `never_sent_opted_out`, not deliveries. No subscriber identities or timestamps exposed. Gmail targeted searches found vendor marketing, not verified named FV affiliate EMAIL authorization or an actual Fieldbook welcome. A private, appropriately authorized source-of-truth reconciliation is still required.

## Partner and law check
Seller `https://hypnosislive.com/mental-skills/total-focus` claims 33-minute, 47-MB audio; public page currently juxtaposes $2 offer and $22.95 list display. Do **NOT** place price in email pending authoritative checkout proof. Seller FAQ `https://hypnosislive.com/faq` qualifies 14-day refunds with max 5 sessions/year. Branded efficacy is not independently proven; seller content/promo mail is not publisher-specific permission. Mind #2436 presell variants are not LIVE first-party endorsed guides. Affiliate acceptance/EMAIL-channel promotion, earning links, pricing, refund execution, rights-cleared assets and authorization remain UNVERIFIED. FTC: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business . Publisher-specific postal address and functional unsubscribe must be verified in actual received email. Neither Automattic nor Inspire3 addresses establish FV publisher address.

## Conversion-first release decision / owner
| Offer → step | Blocker | Proposed change | Pass/fail evidence and owner |
|---|---|---|---|
| Issue 04 Apollo editorial → investigation | Old unexplained time hook | Optional historically grounded version, first-party CTA | BUILT and offline source-tested, NOT ADOPTED; Dispatch/Founder |
| Issue 03 Zen12 → guide → paid order | Missing EMAIL rights, approved link + LIVE guide | Mind/Commerce attestation and controlled checkout proof | **HOLD_MERCHANT**; Mind/Commerce |
| Issue 05 Total Focus → guide → paid order | Same + volatile sale price/refund qualification | Verify true buyer terms and account permission | **HOLD_MERCHANT**; Mind/Commerce |
| Focus → confirmed lead → Fieldbook | Overlapping aggregates + unproven welcome receipt | Provider-authoritative dedup and authorized inbox check | **UNKNOWN**; Claude/Focus/Founder |
| Dispatch → compliant inbox | FV physical address/native opt-out/render unverified | Native preview then separately authorized controlled received test | **HOLD_UNSENT**; Dispatch/Founder |
| Grok → qualified session → settled payment | Missing actual asset/session/transaction linkage | Existing source UTMs, provider confirmations, merchant settlements | **NOT COMPUTABLE**; Grok/Praxxis/Claude/Commerce |

No email, test email, post, schedule, list import, WordPress setting/content, affiliate link, Grok posting, paid analytics or spending created by this branch. No implied A/B results, approved commercial offer or paid sale.
