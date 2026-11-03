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

## Not yet done

* A like-for-like Lighthouse measurement of any candidate change (nothing has been changed).
* Repeated Lighthouse runs (single runs above).
* Mobile real-device or field data (none available).

## Decision needed from the founder

Choose the measure the 2.5 s goal binds to (Lighthouse `simulate`, or throttled real load), and approve which non-block surfaces may be edited (analytics loading, query-loop thumbnail loading attributes, theme font preload). Without that, a PR limited to the page-6 block cannot honestly claim 2.5 s under `simulate`.
