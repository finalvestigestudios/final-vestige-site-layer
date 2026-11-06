# R172 independent QA receipt — 2026-11-06 15:35–16:00 PT

## What changed

This draft-only branch is stacked **directly on** Dispatch R171 draft PR #1315 at `ed1b31aadc5bff42db152331df870c06736efaf3`. R172 creates five additions under its own `dispatch/campaign-2026-mind/r172/` directory (Python truth-checkpoint, regression suite, offline HTML board, offline Chromium smoke test, analytical release review, plus this receipt). It does not touch master PR #175, control PR #201, homepage PR #49, Mind PR #1317, or any WordPress page.

It addresses one discrete measurement flaw not solved by a per-batch `Set`: recurring checks can re-count the *same* provider transition unless the checkpoint survives **across runs**. The local checkpoint persists only 64-character SHA-256 digests of strictly **random, non-PII** opaque event tokens; its contents remain confidential operational data, are never uploaded, and must not be interpreted as authenticated proof of new subscribers. Source truth requires manual native provider verification, unavailable in the connected WP action.

## Exact source matches

- Core module `confirmed_signup_checkpoint.py`: Git blob `b5d5ac89026909bcae220a779b433cda866e7c91`.
- Native test `test_confirmed_signup_checkpoint.py`: Git blob `c152dca4071952e1592b46669b8dd6548aa91cf2`.
- HTML offline reviewer: Git blob `4de7ca705242c3445a9459b683e250cd0ae7dad2`.
- The above Git blob hashes were checked against **exact locally executed files** using `git hash-object`, not inferred from names.

## Execution

`cd r172 && python -I -m unittest discover -s . -v` → **24/24 PASS**, native CPython, including replay same batch, replay across repeated calls, reactivation **not** reported as new signup, Reader-only to email subscription treated as **candidate**, invalid proof/provider source rejected, PII rejected, forged green status rejected, no paid revenue imputed.

Offline reviewer `python browser_qa.py` with local Chromium via Playwright in **in-memory HTML** (file URLs blocked by the sandbox) → **320/390/768/1440 px all PASS**, no horizontal scroll, 4 clickable first-party/official evidence links, one H1, 6 funnel steps, visible HOLD; **390px screenshot inspected**. This is an offline visual QA only; it is NOT WordPress's native email preview or a received inbox message.

R171 is the unchanged direct base of this branch. **Original PR #175** remains at `d57ccdba3aee8f065e143e101c2945f4f3d01647`; a fresh independent readback of all six original manuscripts + the canonical manifest gave **24/24 source-level equivalents** of the original Python guards: 6 issues, 4 editorial/2 commercial, null merchant links, subjects/preheaders, hard-stop legal placeholders, no banned hyperbole, local commercial disclosures. The **original PR #175 Python suite was NOT re-executed natively in this sprint** because this isolated runtime cannot download the private repository to its Python process. Do not describe 24 source-level checks as native suite execution.

## November 6 source of truth

Authenticated WordPress provider at `2026-11-06T23:35Z` reports newsletter enabled, default new-post emails OFF, full content, configured 52-page Fieldbook, counted3/confirmed3/unconfirmed2/suppressed0 and no sends of the last five posts. Follower breakdown `wpcom=3; email=0` is a separate audience surface. Email eligibility and consent of specific recipients **unknown**, no export read. Provider support page https://wordpress.com/support/subscribers/ documents nonadditive statuses and the native `Email subscription` field.

Bounded connected Gmail search found no delivered Fieldbook welcome and no Final Vestige-specific named Inspire3 affiliate email permission; the prior Oct 25 confirmation message is only a request to confirm. This is **not proof of zero delivery or zero merchant permission across all possible accounts**.

Exact Zen12 site https://zen12.com/ read November 6 describes 12 levels / 48 MP3s, displays Premium $87.99 (Beginner/Advanced $67.77), advertises one-year refund; product efficacy, final checkout price, refund performance, email channel rights, tracking/affiliate approval unverified. Do not turn on promotional CTAs.

## Unresolved authorization gates

1. Actual signed-out visitor subscription, real provider `Email subscription=Subscribed`, double opt-in and **received** welcome/Fieldbook.
2. Real non-sending Jetpack native Preview email, Final Vestige valid postal address, functional unsub/opt-out and commercial disclosure in delivered template. Automated source checks cannot prove these.
3. Final Vestige-specific Inspire3 approval, allowed email marketing, authorized merchant earning link, exact approved live Mind guide, actual price/terms.
4. Founder approval of **final creative, audience, schedule and send**; none exists for a mailing. All 6 `HOLD_UNSENT`, slots 03/05 additional `HOLD_MERCHANT`.
5. Settled orders, fee/refund accounting, trusted qualified-human 7-/30-day denominators. `Net revenue / 1,000 qualified sessions = NOT COMPUTABLE`.

No email or test email was sent, no subscriber was contacted or changed, no WordPress write, new tracker, sales link, social post, Grok queue edit, publication or spending.

Owner handoffs: **Claude/Site QA** handles signed-out Focus/Dispatch UX and production fix; **Dispatch** reconciles private WordPress status and inbox with approved evidence; **Mind Studio** owns affiliate acceptance and guide; **Commerce/Praxxis** owns settled-revenue attribution; **founder** is the only campaign release approver.
