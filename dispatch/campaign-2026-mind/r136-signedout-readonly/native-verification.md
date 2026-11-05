# R136 independent native verification — 2026-11-05

**No production writes, list access/import, email sends or partner activation.**

## Exact upstream campaign test rerun

GitHub's master [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175) was reread this run: its actual head remains `d57ccdba3aee8f065e143e101c2945f4f3d01647`. A previously captured native local source archive was compared against the **current GitHub file/blob IDs** at that exact head for all 6 manuscripts, 1 manifest and the original test file. **All 8/8 Git blob IDs matched**. Then Python 3.13 executed `python -m unittest discover -s tests -v` against that local exact-source tree. **6/6 passed**, named:

- `test_commercial_copy_has_disclosure`
- `test_legal_gate_requires_footer_verification`
- `test_links_not_activated`
- `test_no_invented_commercial_promise`
- `test_primarily_editorial`
- `test_six_issues_not_scheduled`

The original test file blob is `fd7f05e30092a7ec82090993dc5d7d0e23755c8e`. This validates static manuscripts only; native Jetpack HTML, delivery, legal footer and merchant permissions are NOT verified.

| Original file under `dispatch/campaign-2026-mind/` | Exact GitHub blob SHA |
|---|---|
| `issues/01-the-mind-is-not-a-camera.md` | `039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8` |
| `issues/02-before-hypnosis-had-a-name.md` | `faa207ab7deafd86460d36f8c17fe62d392d0e14` |
| `issues/03-the-twelve-minute-question.md` | `aeeef34efea0cc281f69901488e4501fea851245` |
| `issues/04-the-hatch-and-the-spark.md` | `89635bfb9c8d1ff17297a59b6b5b5b2a176934ca` |
| `issues/05-before-you-press-play.md` | `a9dfaa450ba025a7b5113ade8a294d6dbad778dc` |
| `issues/06-the-evidence-log.md` | `004d558df6376d2ad6f4f79a4581e8d2c444e355` |
| `manifest.json` | `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00` |
| `tests/test_campaign.py` | `fd7f05e30092a7ec82090993dc5d7d0e23755c8e` |

## R136 new source native verification

Exact independently matched GitHub vs local blob SHA for `signedout_probe.py`: `9b8ca5ecfb047fe780307cadcd1152e90473a687`; `test_signedout_probe.py`: `45bd09819008edee7b18ee528d0a49bec0ec35c1`. **25/25 native Python tests passed** on exact source, including **six local Chromium synthetic DOM cases**. Tool tried two actual public GET-only signed-out browser observations; runtime browser policy returned `NOT_TESTED_LIVE` for both (not a live production failure). No form submitted.

## Connected source checks without subscriber exposure

Live WordPress `newsletter.status` and `newsletter.get_settings` read-only at 2026-11-05 11:32 UTC: enabled/sendable, auto-new-post email OFF, excerpt email, welcome Fieldbook 52-page text configured, recent 5 articles not sent, total 3, confirmed 3, unconfirmed 2 (NONADDITIVE). **Native email-recipient eligibility and actual inbox-delivered welcome remain unknown**. This is not evidence of three reachable subscribers.

Targeted connected Gmail searches covering 2026-10-25 onward found **no search match identifying a received Final Vestige Focus Fieldbook welcome** in that connected mailbox and no search match establishing **named Final Vestige affiliate approval / permitted email marketing**. Separate merchant consumer promotional emails exist in the mailbox, but **they do not establish publisher partner rights**, prices or official copy-use permission. Search absence is **not** proof that a valid received welcome or written partner acceptance could not exist elsewhere. No subscriber addresses or full email content are retained here.

Official merchant sales pages reread: https://zen12.com/hnp and https://hypnosislive.com/mental-skills/total-focus . Zen12's `12 minutes = 1 hour` equivalence and hypnotherapy's `100% concentration` language are seller advertisements, not editorial proof. Retail price quotes are storefront displays, not independently verified checkout. Public https://affiliates.inspire3.com/ describes the program generally, **not Final Vestige-specific acceptance, email rights or earning link**.

## Truthful release status

- **BUILT:** R136 offline visitor probe and owner runbook.
- **TESTED:** exact upstream six Python tests + new 25 native tests + six synthetic browser cases.
- **LIVE:** published /dispatch/ and /focus/ exist; no R136 change deployed.
- **VERIFIED:** actual signed-out visitor form/modal, received welcome, final Jetpack footer/unsubscribe, named merchant authorization, settled sales — **NONE ESTABLISHED**.
- **RELEASE:** all 6 emails `HOLD_UNSENT`; commercial 03/05 also `HOLD_MERCHANT`. Realized net revenue per 1,000 qualified human sessions remains **NULL / NOT COMPUTABLE**, not zero.
