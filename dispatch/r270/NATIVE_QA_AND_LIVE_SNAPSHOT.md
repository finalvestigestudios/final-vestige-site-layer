# Dispatch R270 — Reproducible source/test receipt and production HOLD

**Evidence window:** 2026-11-11 02:30 UTC (WordPress connected read-only); exact source QA executed 2026-11-11 UTC. This is a local test receipt, **not** GitHub CI or live provider verification. **ZERO** emails, test sends, subscriber contacts, imports, WP edits, scripts, offers, payments, or social publishes.

## Exact original founder PR #175 @ d57ccdba3aee8f065e143e101c2945f4f3d01647

All eight files were fetched independently via GitHub connector at this immutable PR head; reconstituted original bytes; `git hash-object` matched GitHub's file blob identities 8/8:

| File | Independently matched Git blob |
| --- | --- |
| `manifest.json` | `86df98ad8a84e583ff5df64ddbf8c0eaa1335b00` |
| `tests/test_campaign.py` | `fd7f05e30092a7ec82090993dc5d7d0e23755c8e` |
| `issues/01-the-mind-is-not-a-camera.md` | `039b452b5cb7cd6dc2fed6fac4d2dd77fa9d49c8` |
| `issues/02-before-hypnosis-had-a-name.md` | `faa207ab7deafd86460d36f8c17fe62d392d0e14` |
| `issues/03-the-twelve-minute-question.md` | `aeeef34efea0cc281f69901488e4501fea851245` |
| `issues/04-the-hatch-and-the-spark.md` | `89635bfb9c8d1ff17297a59b6b5b5b2a176934ca` |
| `issues/05-before-you-press-play.md` | `a9dfaa450ba025a7b5113ade8a294d6dbad778dc` |
| `issues/06-the-evidence-log.md` | `004d558df6376d2ad6f4f79a4581e8d2c444e355` |

Command: `python -I -m unittest discover -s /mnt/data/dispatch_original_src/dispatch/campaign-2026-mind/tests -p test_campaign.py -v`

Python **3.13.5** result: **6 tests run, 6 PASS, 0 errors, 0 failures**. They check six issues, original 4/2 mix, inactive affiliate URLs, subjects, preheaders, explicit UNSENT status, merchant disclosure/placeholder, legal placeholders and banned promotional promises. They do **not** verify claim authenticity, link live status, lawful eligibility, received emails, revenue or delivery.

## Exact tested R270 files and dependency

| File | Git blob |
| --- | --- |
| `dispatch/r270/proof_gate_v3.js` | `037849805d20e05f0fe12ee14206fecc982820df` |
| `dispatch/r270/proof_gate_v3.test.js` | `c3453a8eaf4c8c0eb2df1f5d176c28ab0b5b2b7b` |
| `dispatch/r268/cohort_audit_v2.js` (unchanged dependency) | `290c3cfd32a84632854ce41a0eefe1409b73389a` |

Command: `node --test /mnt/data/dispatch_r270/r270/proof_gate_v3.test.js`

Node.js **v22.16.0** result: **13 subtests PASS, 0 failures**. Checked status: synthetic sample net commission **-5 cents** on **100 hypothetical qualified sessions**, which produces illustrative **-50 cents per 1,000**; external-mode identical data (even with all four evidence booleans true) returns **NOT_COMPUTABLE / no financial totals / no confirmed subscribers**. All numbers in this test are invented fixtures, not business results. File hashes obtained by native `git hash-object`, then checked again against exact committed GitHub `fetch_file` blob SHA. No runtime code executed against subscriber lists or merchant accounts.

## Read-only WordPress status 2026-11-11 02:30 UTC

Authenticated WP.com / Jetpack newsletter configuration: `subscriptions=true`; `email_new_posts_by_default=false`; `email_content_format=full`; `reply_to=no-reply`; `from_name=Final Vestige Studios`; welcome contains the configured free 52-page Fieldbook PDF. Five inspected recent post sends `never_sent_opted_out`, with `dispatched_at=null` and no actual recipients. Newsletter diagnostic counters: total 3, confirmed 3, unconfirmed requests 2, suppressed 0. Distinct follower endpoint: total 3, WordPress.com 3, email 0, comments 0, partial false. These are NOT additive or evidence of **three email-eligible recipients**. No PII queried or recorded.

**Unverified:** provider-filtered `Email subscription → Subscribed`, actual welcome receipt, download success, actual signed/approved earning link or merchant payment, source-to-order attribution, FV publisher legal postal address, functioning unsubscribe, genuine Jetpack email editor preview or delivered MIME, merchant-specific email promotion permission, final founder send approval. The existing `/focus/` frontend gift display is NOT provider-confirmed consent.

## Release block

**ALL SIX DRAFTS: HOLD_UNSENT; COMMERCIAL 03/05: HOLD_MERCHANT.**

The R270 validator is offline and not deployed. It is intentionally incapable of approving sends, payments, email promotions or numerical real-world KPI claims. No change to PR #49 homepage, original #175, readiness #201, recent preview #1978, WordPress, Grok production or revenue systems.
