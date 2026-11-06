# R171 QA receipt — November 6, 2026 (Pacific)
**UNSENT DRAFT, NOT LIVE**. Issue #174. Stacked PR uses the current prior Dispatch R170 head `23b628498577eeb18f5dab9fb45fe72700578377`; original master pilot PR #175 unchanged at `d57ccdba3aee8f065e143e101c2945f4f3d01647`, original per-issue guard PR #201 unchanged at `ef53e5a17046e3dff5a4a7e3b0f4c8fbce9cd6f6`, homepage #49 untouched.

## Executed—not assumed
- Native CPython `python -m unittest -v test_dispatch_truth_gate.py` in local redacted evidence package: **20/20 PASS**. Covers six-issue hold, correct 4:2, auto-send true failure, missing Jetpack block failure, Focus false-success class/query marker detection, nonadditive counters, fake paid conversion refusal, fake email-permission refusal, denial of PII echoes, and a fully synthetic all-true proof that cannot release a send.
- Static alternative email QA: **12/12 PASS** (first-party CTA exactly one; original paper + retrospective citations; postal/unsubscribe placeholders; no merchant links, script or remote iframe; appropriate review status).
- Actual headless Chromium offline reviewer on **320, 390, 768, 1440px: 4/4 PASS**. Each has zero horizontal overflow, one visible first-party CTA, keyboard TAB reaches the link, zero page errors. **Initial 320/390 widths failed** due long research DOI URL overflow; added `overflow-wrap:anywhere`, then reran all four successfully; screenshot review also caught an orphaned CTA arrow and prompted a shorter, non-wrapping CTA against the **exact GitHub HTML blob `194413fd4f2a3c3c29569bd18a496b9574bb4741`**. Browser screenshots retained locally for reviewer; this does not inspect actual Jetpack email rendering.
- Independent Git blob identity in container `git hash-object` matches uploaded GitHub readback for Python truth gate `e309503f557c25ca441612454736dae5ac765891`, native Python regression suite `be86f8bdb9dadf5a07316ecbba8decca86c49ad7`, and alternative plaintext email `c4c5cf4d18aaa74a3d7c1457d4e9ea37e93dc864`.
- Original PR #175 suite previously passed native **6/6 in R161 at unchanged head**; **NOT independently re-executed in R171** because this container cannot retrieve private repo sources over network. No new claim of that suite's execution.
- This is an offline QA package from sanitized WordPress API observations; **not a signed-out live-browser guest signup test, real received welcome, actual Jetpack MIME inspection or verified merchant permission**.

## Why we did this
New distinction: /dispatch/ stores native Jetpack subscription block while WordPress view API renders a same-page Subscribe anchor. **This is a discrepancy in API rendering, not proven failure on the public website.** The Focus `fvf-gift-v2` source does independently show a false-positive UI signal. Neither satisfies `confirmed_signup`; WordPress follower numbers cannot prove email delivery. Real WordPress subscriber preference, received welcome, paid conversion, publisher postal address, functional unsub and named merchant email rights remain missing.

## Source and legal
- [Editorial Standards](https://finalvestige.com/editorial-standards/)
- [McGurk & MacDonald Nature 1976](https://doi.org/10.1038/264746a0)
- [MacDonald Multisensory Research 2017](https://doi.org/10.1163/22134808-00002548)
- [FTC CAN-SPAM](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)
- [WordPress subscriber guidance](https://wordpress.com/support/subscribers/)
- [Mind & Affiliate handoff Issue 171](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/171)

## Final release result
All six original campaign emails **HOLD_UNSENT**, Issues 03/05 additionally **HOLD_MERCHANT**. New McGurk issue alternative **NOT APPROVED for substitution**. All outside-owner attestations unverified; no emails, test sends, site publishing or modifications, affiliate activation, tracking installation, list imports/updates, spending, or PR #49 changes. Primary commercial KPI = **NOT_COMPUTABLE**.
