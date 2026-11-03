# Mobile LCP follow-up: measured diagnosis (2026-11-02)

Founder condition 5 asks for a separate post-release PR that brings mobile LCP to 2.5 s or better without changing the approved visuals. This note records what was measured on the **live** plain URL `https://finalvestige.com/` before any change is proposed. No code was changed and PR #604 (frozen) was not touched.

## Two tools, two answers (they are not comparable)

| Tool / mode | What it is | FCP | LCP |
|---|---|---:|---:|
| Lighthouse 12.6.1, mobile, `simulate`, **live site**, Edge, 1 run | Lantern model estimate | 2.0 s | **8.4 s** (perf 66) |
| Lighthouse same run, *observed* (unthrottled) | what the browser really did | 1.59 s | 1.59 s |
| Playwright/Edge + CDP (390 px, 4x CPU, 150 ms RTT, 1.6 Mbps), 4 runs, cache off | real throttled load | 1.9 s median | 1.9 s median |
| Earlier acceptance figure (ACCEPTANCE_MATRIX): Lighthouse `simulate` on a gzip+cache proxy of the candidate | front end only, not production | 1.30 s | **4.58 s** |

The 4.58 s figure was measured on a proxy that carried none of the production page's head scripts, analytics or theme extras. **Against the live page the same Lighthouse mode reports 8.4 s.** The founder's first-release exception was approved against 4.58 s, so the approver should know the like-for-like live figure is higher. The LCP element in every run is text (`p.fv-hf__opening-dek`), not an image.

## Why a text element is "8.4 s" in the model

Real LCP equals FCP (about 1.6 s). Lighthouse's simulation adds everything the page requested before that moment (network and CPU) to the LCP estimate, so the gap is explained by bytes and requests initiated before first paint, not by the hero text itself. Render-blocking CSS ends about 2.1 s in the throttled Playwright run, with the 350 KB `InterVariable.woff2` (theme preload) competing for the same pipe.

## Lever tests (blocking one group at a time on the live page)

Throttled Playwright (median of 4, FCP / LCP in ms):

| Variant | FCP | LCP |
|---|---:|---:|
| baseline | 1900 | 1900 |
| drop 2 minor blocking CSS | 1894 | 1968 |
| drop both Inter files | **1084** | 1668 |
| drop 3 eager thumbnails | 1740 | 1740 |
| drop analytics/third-party scripts | 1872 | 1916 |
| fonts + CSS + thumbnails | 1016 | 1574 |
| all of the above | 950 | 1518 |

Lighthouse `simulate`, live, 1 run each (noisy; indicative only):

| Variant | simulated LCP | perf |
|---|---:|---:|
| baseline | 8.4 s | 66 |
| Inter fonts blocked | 8.4 s | 69 |
| analytics/third-party blocked (gtag x2, PostHog, ahrefs, bilmur, stats.wp) | **5.7 s** | 77 |
| 3 thumbnails blocked | 7.8 s | 69 |
| Jetpack related-posts + Gravatar CSS blocked | 8.6 s | 71 |
| fonts + 3 thumbnails blocked | **4.2 s** | 80 |

## Findings

1. By the throttled-load measure the live page is already under 2.5 s (about 1.9 s). By Lighthouse `simulate` it is 8.4 s. Which one the "2.5 s" target refers to must be fixed first; the two cannot be reconciled by a code change.
2. Under `simulate`, no single lever reaches 2.5 s. The best single groups (third-party scripts, then fonts plus thumbnails) get to 5.7 s and 4.2 s, and even removing all of them leaves a simulated FCP of about 2.0 to 2.3 s from HTML plus render-blocking CSS.
3. Every lever that matters sits **outside page 6's block**: the Inter preload and render-blocking CSS belong to the Assembler theme and plugins; the analytics tags are site-level; the three eager thumbnails come from the page's query-loop blocks (core adds `fetchpriority=high` to the first). A change to those is a site or other-block edit, not a PR #604 follow-up that leaves the approved block alone.
4. The 202 KB inline `<style>` (the page's own CSS) is a real cost for parse and for the simulated CPU graph; it was not isolated in these tests.

## Founder decision (2026-11-02) and first one-change-at-a-time test

The binding benchmark is **real throttled mobile LCP of 2.5 s or better**; p75 field LCP becomes the standard once enough field data exists. Lighthouse `simulate` is reported separately. Non-block surfaces (font delivery, render-blocking CSS, thumbnails, analytics scheduling) may be optimized in a separate PR if isolated, measured and reversible, with tracking preserved.

What-if harness (`evidence/perf-2026-11-02/whatif.py`): serves a saved copy of the live HTML from localhost with exactly one edit, 390x844, CPU 4x, 150 ms RTT, 1.6 Mbps, cache off, 8 runs per variant in alternating order. Analytics collection requests are aborted so the tests add no data to production analytics. The live site was not changed.

| Variant | FCP median (range) | LCP median (range) | CLS | Inter loaded |
|---|---:|---:|---:|---:|
| v0 baseline | 1560 (1544-1640) | 1634 (1620-4684) | 0 | 8/8 |
| v1 remove the Inter `<link rel=preload>` only | **1270** (1192-2348) | **1506** (1416-3468) | 0 | 8/8 |
| v2 lazy-load the 3 query-loop thumbnails, drop `fetchpriority=high` | 1572 | 1668 | 0 | 8/8 |
| v3 v1 + v2 | 1234 | 1434 | 0 | 8/8 |

Reading: removing only the font preload gains about 0.3 s FCP and 0.13 s LCP in this method and the font still loads (the earlier "block the file" test also removed the font, which changes typography and is not a valid candidate). The thumbnail change alone does nothing measurable. These runs use a local copy of the HTML, so absolute values are lower than the live-URL runs; compare variants only with each other. Outliers (LCP up to 4.7 s in single runs) occurred in v0 and v1.

Adverse effects to check before any release: with `font-display: fallback` the first paint uses the fallback face and swaps to Inter when it arrives (measured CLS 0, but a visible swap on slow connections must be judged against the approved typography); the italic face is declared by the theme but was not requested in any run.

Open: the preload is emitted early in `<head>` by WordPress or the platform, not by `theme.json` (which has no preload setting) and not by the page block. The mechanism that emits it has not been identified, so there is no live implementation yet. Candidate paths: a small, reversible plugin using the proper hook, or a platform setting. Installing a plugin on production is a configuration change that has not been done.

## Addendum 2026-11-03: the throttled LCP is bimodal, so a median understates it

Repeated throttled runs (same conditions as above, 390 px, CPU 4x, 150 ms RTT, 1.6 Mbps, cache off) of the live page, served from a saved copy and with analytics requests aborted, show two modes. In most runs the LCP is about 1.6 to 1.7 s (the Hidden in the Margins strip, FCP about 1.6 s). In roughly a third to a half of runs a later LCP candidate, the hero paragraph `P.fv-hf__opening-dek`, is reported at 4.5 to 5.3 s. Counts: old HTML 2 of 10 runs high, current HTML 5 of 10 (the difference is within noise at this sample size; FCP is identical at about 1.59 s); a 12-run sample of the current page had 4 of 12 high. With the Inter font file blocked the high mode still occurs in 4 of 12 runs but at 3.0 to 3.2 s, so the web font delays it but is not its cause. The FREE EBOOK header change did not change FCP.

Consequence: a median of about 1.6 to 1.9 s is true of the typical run, but a p75 of these lab runs is above 2.5 s (about 3 to 4.6 s). The founder's long-term standard is p75 of mobile field LCP, so the "meets the lab goal" statement should be read as a median and not as a p75. The cause of the late hero-paragraph paint has not been identified (candidates: a script-gated reveal or a re-render of the hero text; the flagship block and its CSS/JS are the first place to look). This belongs to the post-release performance PR, not to PR #604's frozen head.

## Not yet done

* A like-for-like Lighthouse measurement of any candidate change (nothing has been changed).
* Repeated Lighthouse runs (single runs above).
* Mobile real-device or field data (none available).

## Decision needed from the founder

Choose the measure the 2.5 s goal binds to (Lighthouse `simulate`, or throttled real load), and approve which non-block surfaces may be edited (analytics loading, query-loop thumbnail loading attributes, theme font preload). Without that, a PR limited to the page-6 block cannot honestly claim 2.5 s under `simulate`.
