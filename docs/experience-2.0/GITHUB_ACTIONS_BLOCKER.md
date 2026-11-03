# GitHub Actions blocker: evidence and account-owner checklist (2026-11-03)

Repository `finalvestigestudios/final-vestige-site-layer`. This is an account-level restriction, not an application or test failure.

## Evidence (read from the GitHub API on 2026-11-03, about 15:10Z)

- PR #798 head `65f98aad79369c9c8a3ef9dad4bea1f136bf43c5`: two `verify` check runs (workflow `experience-2`, run 41658413757 for `pull_request` and run 41658250956 for `push`; check-run IDs 126000228695 and 126000232872) concluded **failure** within 3 to 4 seconds with **zero steps executed**.
- Both check runs carry this annotation, verbatim: "The job was not started because recent account payments have failed or your spending limit needs to be increased. Please check the 'Billing & plans' section in your settings".
- It is repository-wide. Of the 40 most recent workflow runs, **13 jobs across 6 different workflows** carry the same annotation with zero steps: `experience-2` (2 runs), `Final Vestige Site Layer CI`, `Desktop suite build (internal)`, `Apollo Evidence real isolated WordPress gate`, `Apollo R94 curated Atlas and genuine Chromium`, `EX2 isolated WordPress core save/readback`, and `Dispatch Campaign QA (draft safety)`.
- Timeline: the last job that executed successfully started at 2026-11-03T14:27:59Z. The next job after that to be blocked started at 14:37:15Z (the 14:36:14Z Dispatch job still executed 14 steps and failed on its own merits). Every job from 14:37:15Z to the newest (15:08:39Z) is blocked. The restriction therefore began between about 14:28Z and 14:37Z.
- Not a repository configuration or runner fault: the same workflows ran green minutes earlier on the same repository with the same runners.

## What is not established

- The reason (a failed payment, an exhausted Actions budget or spending limit, or minutes used up) cannot be read from the API. The annotation names two possibilities. Roughly 30 jobs ran in the half hour before the block, which would fit a budget or minutes limit, but that is an inference.
- I did not open the GitHub billing pages and changed no billing settings.

## Account-owner checklist (founder)

1. Open https://github.com/settings/billing . If the repository belongs to an organization, open that organization's Billing and plans page instead; the annotation refers to the owner account.
2. Look for a failed payment or an expired or declined payment method, and fix it.
3. Check the **Actions** budget or spending limit and the included minutes for this billing period. Raise the limit only if you decide to; nothing has been or will be changed without your decision.
4. If billing is healthy, check Settings, Actions, General for the repository (Actions permissions) and any organization policy that disables Actions.
5. Tell the lead session when it is fixed. Then re-run the affected workflows on the **exact reviewed commits** (PR #798 at its final head, and the other release heads), and record the results. Hosted green is required for the gated releases and must not be replaced by local test output.

## Handling until it is fixed

- No further jobs are dispatched on purpose; sessions are told to push once per review-ready head, since every push starts another blocked run.
- No code or test assertion is changed to get around it. Local results are labeled local and are not hosted CI.
- Work that does not use GitHub Actions continues: WordPress.com edits, local browser testing, source corrections.

## Confirmed cause (founder screenshot of GitHub Billing, 2026-11-03)

The billing page shows "You've used 100% of your Actions budget. Additional usage will be stopped." Overview for November 1 to 30: current metered usage $23.36, current included usage $18.36 (so the net charged usage is $5.00, which suggests a $5 Actions budget; the budget amount itself was not shown). Subscriptions: GitHub Pro $4.00 per month, Copilot Free $0.00. Copilot usage is $0. So this is an exhausted Actions budget, not a failed payment method. The only fix is to raise the Actions budget ("Update your budget") or wait for the monthly reset on December 1; raising it is a spending decision for the account owner and was not changed by this session.

Usage notes for the owner's decision: each pushed commit on a pull-request branch starts both a `push` and a `pull_request` run of the same workflow, which doubles minutes; Windows jobs (for example `windows-build` in `Desktop suite build (internal)`) use a higher minute multiplier than Linux; about 30 jobs ran in the half hour before the block. Reducing duplicate triggers or heavy jobs would stretch a given budget; this was not changed.
