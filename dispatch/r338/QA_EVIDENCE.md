# R338 independently observed QA and provenance, November 13, 2026

## Exact master check performed BEFORE new work
- GitHub original six-issue master PR #175, head d57ccdba3aee8f065e143e101c2945f4f3d01647: fetched all eight files; compared Git blob identities against archived source, all **8/8 MATCH**. Ran unchanged original Python suite with Python 3.13.5, **6/6 PASS**.
- Source paths: dispatch/campaign-2026-mind/manifest.json, tests/test_campaign.py, and original issues 01–06. No original manuscript was rewritten or given an approved replacement.
- Read latest Issue #174, Issue #171, PR #201, PR #2383 (R337), Mind PR #2380, live /dispatch/ /focus/ /editorial-standards/ and authenticated newsletter settings. Original source and branch state review completed before R338 branch.

## New reproducible offline package (separate local artifact)
- R338 offline Python proof auditor and synthetic fixtures: **39/39 native Python tests PASS** on local files. It classifies evidence of signup, delivery, merchant authorization, true settled purchase, fees, refunds and attribution, rejects PII and false click→purchase inference. **Local code is not included in this GitHub PR**, is not production analytics, never calls the provider and cannot send email.
- Static offline HTML evidence board checked with Chromium at **320 / 390 / 768 / 1440px: 4/4 PASS**, with no horizontal overflow and six preview cards. This is **not** an actual WordPress editor Preview email, mobile Gmail, inbox receipt, or deliverability test.
- Offline fixtures show missing data as NULL/UNOBSERVABLE and all six release statuses HOLD_UNSENT; commercial 03/05 also HOLD_MERCHANT. Synthetic results are **not** customer metrics, sales, A/B evidence or paid conversions.
- Original-master Git blob matches and test logs, local source/test/reviewer and Chromium screenshots reside in the separately provided R338 offline ZIP. The GitHub PR adds only specifically documented audit/coordination files.

## Fresh provider state
Authenticated read-only WordPress snapshot **2026-11-13 20:38:56–20:38:59 UTC**: site_can_send true (technical capability only); subscriptions true, email_new_posts_by_default false, email_content_format full, sender Final Vestige Studios, 52-page Fieldbook welcome configured. Subscriber totals total 3 / confirmed 3 / unconfirmed 2 non-additive; followers WP.com 3 / direct-email 0. Exact eligible recipients UNKNOWN. Five recent posts show never_sent_opted_out — **not** a lifetime zero-sends statement.
- Connected Gmail targeted 2026-10/11 Inspire3/Focus searches returned consumer seller marketing but no authenticated Final Vestige-specific partner EMAIL marketing approval or a proven received welcome in those results; absence doesn't prove nonexistence.
- Real native newsletter preview NOT RUN; no test or production email authorized. No provider list export/read, no WordPress write.

## Blocking commercial/legality acceptance
Partner account-specific EMAIL promotion permission, issued earning URL and permitted URL format, actual live vetted Mind guides, exact final prices/refunds/consent, valid FV physical mailing address, working received unsubscribe, actual confirmed recipient state and welcome receipt all NOT VERIFIED. Claims from sellers are vendor representations; not independent efficacy. No independently settled paid orders/fees/refunds or qualified human sessions authenticated. **Realized net revenue per 1,000 qualified sessions NOT COMPUTABLE.**

## GitHub isolation and owner boundaries
R338 branch stacks only on R337 PR #2383 and must stay draft/unmerged; creator acquisition Grok/Praxxis TASK-008 unchanged, Claude owns analytics instrumentation, Mind owns merchant eligibility/landing guides, Founder approves all sending/publishing/spend. Original #175, early #201 and homepage #49 unchanged. **NO send, test send, subscriber contact, list import, live CMS edit, tracking deploy, affiliate activation, social post or spending.**