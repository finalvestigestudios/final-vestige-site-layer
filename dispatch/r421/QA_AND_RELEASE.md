# Dispatch R421 — source-hash/native QA receipt and release holds

Timestamp: **November 17, 2026, 10:34 UTC** for authenticated WordPress observations; validation performed same session. Owner: [Dispatch #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174). This additive branch is stacked on [draft R420 PR #2853](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2853) exact parent `b7d2bb1f5454000f206f479919047feca27bdf43`. Original [campaign PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) exact head `d57ccdba3aee8f065e143e101c2945f4f3d01647`; original campaign not rewritten. [Per-edition draft #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201) and frozen homepage PR #49 unchanged. All six remain unsent.

## Independent original master execution — PASS, exact files

Via a previously retained local exact-source archive and authenticated GitHub `fetch_file` reads against **#175 HEAD**, independently compared all eight Git blob SHA-1 identities, then ran native Python **3.13.5** `python -m unittest discover -s campaign-2026-mind/tests -v`. Result: **6/6 passed; zero failures; exit 0.**

| Source file under `dispatch/campaign-2026-mind/` | Git blob SHA-1, exact |
| --- | --- |
| `manifest.json` | `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00` |
| `tests/test_campaign.py` | `fd7f05e30092a7ec82090993dc5d7d0e23755c8e` |
| `issues/01-the-mind-is-not-a-camera.md` | `039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8` |
| `issues/02-before-hypnosis-had-a-name.md` | `faa207ab7deafd86460d36f8c17fe62d392d0e14` |
| `issues/03-the-twelve-minute-question.md` | `aeeef34efea0cc281f69901488e4501fea851245` |
| `issues/04-the-hatch-and-the-spark.md` | `89635bfb9c8d1ff17297a59b6b5b5b2a176934ca` |
| `issues/05-before-you-press-play.md` | `a9dfaa450ba025a7b5113ade8a294d6dbad778dc` |
| `issues/06-the-evidence-log.md` | `004d558df6376d2ad6f4f79a4581e8d2c444e355` |

## New R421 exact-source native execution — PASS

Three newly committed source files were re-read from their **current GitHub branch at commit `3473f2a70621185ffeffc00ccf026d14b391ebf0`**, and their blob identities matched the local Python execution bytes exactly:

| New file | Exact Git blob SHA-1 |
| --- | --- |
| `consent_snapshot.json` | `89a35ae2c170d002d7b1dae617054f9f0f90b683` |
| `consent_snapshot_gate.py` | `fd523d55156140151374716690c218002d012258` |
| `test_consent_snapshot_gate.py` | `0a6a2490cbf2bd457642780b9b902da44d1aa143` |

Native `python -m unittest -v test_consent_snapshot_gate.py` at Python 3.13.5: **20/20 PASS, zero failures**, with 19 source/privacy/false-positive behavior cases plus negative controls for malformed counts, a forged merchant email permission, synthetic Fieldbook receipt, raw email field, unprotected hash-like ID, false release state and mismatched PDF. Native diagnostic execution prints `HOLD_UNSENT`, no PII, null eligible recipients, null `confirmed_signup` events, null independently verified paid orders, and null net revenue/1,000 audited human visits.

The R421 validator is deliberately **READ_ONLY_AGGREGATE_DIAGNOSTIC**: it rejects asserted verified proof because we do not possess any. It is not a production subscriber-events integration, a real opt-out test, actual HTML/email rendering, an email API sender or a legal certification. Native host run is local, not hosted GitHub Actions CI. A passing snapshot does **not** resolve the underlying provider count conflict.

## Dated source-of-truth checks

- Authenticated WordPress newsletter status: `subscriptions=true`, platform can send, new-post emailing OFF, full/no-reply, total3/confirmed3/unconfirmed2, last 5 opted-out post notifications with no recipients. These figures are not a unique recipient set.
- Authenticated WordPress Stats follower composition: `partial=false`, Reader3, direct-email0, comment0. Different endpoint definitions; does not mean 3 reachable inboxes or zero eligible subscribers.
- Authenticated media listing: ID1737, application/pdf, 599946 bytes, URL exact match to active welcome; receipt/open/download still unverified.
- Live /dispatch/ ID523, /focus/ ID1579 and /editorial-standards/ ID17 read without writes. Editorial Standards require close-to-record sources, separating reported facts from inference and transparent commercial relationships.
- Official merchant surfaces rechecked: [Zen12](https://zen12.com/about) and [coupon funnel](https://zen12.com/secret/); [Total Focus product](https://hypnosislive.com/mental-skills/total-focus) and [FAQ](https://hypnosislive.com/faq). This does not grant Final Vestige specific EMAIL permission, issued URL, approved first-party guide or checkout terms.
- Legal reference: [FTC CAN-SPAM guidance](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business); native Preview reference: [WordPress email appearance](https://wordpress.com/support/newsletter/email-appearance/).

## Non-sending release result and independent acceptance

`HOLD_UNSENT` ALL SIX. Issue03/05 `HOLD_MERCHANT`; original Issue04 `HOLD_COPY`; optional alternatives `NOT_ADOPTED`. The verified media file does not convert the welcome into a demonstrated delivered email. `site_can_send` does not authorize a send. No named account-specific affiliate **EMAIL** rights, referred checkout, final settlement, verified FV address, unsubscribe, exact Jetpack native Preview or founder final send approval. No subscribers contacted, real/test mail sent, WordPress writes, extra lists, affiliate links, social posts, merges, account expenses or homepage modifications. Realized net revenue per 1,000 audited qualified-human sessions: **NOT COMPUTABLE**, not a known zero.

### Acceptance evidence required from owner lanes

1. **Focus / Claude**: private provider-export-free, deduplicated recipient eligibility + confirmation transition, actual final 52p Fieldbook welcome receipt and opt-out state; only aggregate proof IDs publicly.
2. **Dispatch / Founder**: non-sending *native* editor Preview screenshots, then separately authorized receiving-inbox + valid FV physical postal address and functional unsubscribe proof.
3. **Mind / Commerce**: named product-specific Inspire3 EMAIL permission, issued earning URL, real approved live guide, referred checkout / pricing / returns.
4. **Grok / Praxxis / Claude**: actual asset identifiers, qualified-human landing sessions, independently confirmed paid order/commission, fees and refunds for 7/30-day cohorts; missing values marked unknown.
