# Mobile LCP "bimodal" investigation: findings (2026-11-03)

Branch `perf/mobile-lcp-bimodal-20261103`, cut from `feature/experience-2-living-archive-sprint5` (9a74ecda). Investigation only. **No production change is proposed.** PR #604's branch, page 6 (SHA-1 `8c0dd5c3...`), the header and every plugin were not touched. All variants were applied to a *saved local copy* of the HTML and served from `127.0.0.1`.

Evidence, scripts and raw per-run JSONL: `evidence/perf-2026-11-03-lcp-bimodal/` (`harness.py`, `variants.py`, `analyze.py`, `combine.py`, `runs/`, and the exact saved HTML, `saved_live_home_2026-11-02T22-46.html`, SHA-1 `feef7f1c...`).

## Answer in five lines

1. The two LCP modes are real in the documented local method, and the identical A/A control behaves the same, so it is not an A/B artifact.
2. **The slow mode (about 4.7 s) is not slow rendering of the paragraph. It is the paragraph's real styled-paint time on an uncompressed 406 KB copy. The "fast" mode (about 1.7 s) is a measurement mask, not a faster page.**
3. The mode split is decided by one thing: whether the first paint happens while the header margin strip's markup has arrived but its `<style>` has not. When it does, the strip paints unstyled and huge (about 211,000 px²), becomes the LCP at about 1.65 s, and LCP can never go down, so the later paragraph (34,711 px²) is never reported.
4. **The bimodality does not occur when the local copy is served with the live site's wire size (gzip, about 90 KB instead of 406 KB), nor on the real live URL under identical throttling.** There the paragraph is in the first paint and LCP is about FCP: median 1.8 to 2.1 s, p75 1.9 to 2.3 s, p95 2.1 to 2.5 s (lab, throttled, not field).
5. The one change tested inside the flagship block (hoisting its `<style>` ahead of its markup) produced no measurable gain on the live-like path, so none is proposed.

## Conditions (all runs)

Playwright 1.64 with Edge (`channel="msedge"`, headless), 390x844 mobile with touch, fresh browser context per run, CDP CPU throttle 4x, 150 ms RTT, 1.6 Mbps down / 750 kbps up, HTTP cache disabled, analytics *collection* requests aborted (`collect`, `/e/?`, `/i/v0/e`, `g.gif`, `posthog.com/s/`, `ahrefs.com/api`, `/decide/`, `pixel.wp.com`) so production analytics stay clean. Other third-party scripts were allowed to load; instrumentation was not disabled. Variants alternate order each round. LCP is the last `largest-contentful-paint` entry from a buffered PerformanceObserver (Chromium via Edge). "Light" runs add only observers; "rich" runs also add a requestAnimationFrame sampler, a mutation log and CDP network events (they perturb timing slightly and are used only for explanation, never for distributions). Percentiles use linear interpolation. Machine: the author's Windows desktop with other sessions running; host CPU was sampled but not controlled, so absolute numbers carry machine noise.

CDP throttling applies to the localhost origin too (the local HTML's `responseEnd` is about 9.3 s when served uncompressed).

## 1. The two groups (documented method: uncompressed local copy)

110 runs (`e1`: 40 rounds x base and an identical control; `e6`: 30 base), cold cache, 4x CPU, identity encoding:

| Group | n | LCP median | p75 | p95 | min / max | FCP median |
|---|---:|---:|---:|---:|---|---:|
| fast | 75 | 1,664 ms | 1,672 | 1,698 | 1,404 / 1,908 | 1,584 |
| slow | 35 | 4,748 ms | 4,884 | 4,926 | 4,404 / 4,952 | 1,592 |
| all | 110 | 1,672 ms | **4,563** | 4,900 | 1,404 / 4,952 | n/a |

Slow share 35 of 110 (32%); by batch it varied 13% to 55% (base/control within `e1`: 32% and 45%), so it is a coin-flip-like race, not a stable property of a variant. Fast-group final LCP element: `DIV.fv-margin-strip__window` in 72 of 75 (size 210,456 or 211,088 px² in 72 runs), `P` (tagline) in 3. Slow-group final LCP element: `P.fv-hf__opening-dek` in all 35, size 34,711 px². FCP is the same in both groups (about 1.59 s): the split is not visible in FCP.

## 2. What differs between fast and slow (rich traces, `e4`, 16 runs, identity)

- In **all 16** runs, including the "fast" ones, the paragraph is painted *unstyled* first (computed 16 px, width 390 px, height 79 px, `Inter, sans-serif`) at about 1.6 to 2.4 s, then re-styled (17 px, 354 px wide, 108 px tall, `Inter, ui-sans-serif, ...`) at **3.1 to 4.8 s**. The restyle time matches the slow-mode LCP time. There is no `opacity`, `visibility`, `content-visibility` or script-gated reveal on the paragraph, no class mutation on it, and the font swap is not the trigger (the sampled `document.fonts.check('17px Inter')` stays false throughout; the Inter file does not finish until about 10 s).
- The cause of the unstyled first paint is structural: the shipped block is `fragment + inline_block` (`experience2/home-flagship/wp-candidate/build_candidate.py`, inline delivery), i.e. about 35 KB of hero markup comes first and the 57 KB inline `<style>` comes after it. The paragraph is therefore painted unstyled whenever a paint happens before that `</style>` is parsed.
- The styled paint lands after a 560 to 900 ms long task (style recalc and layout when the stylesheet is applied) at about 3.5 to 4.6 s. Layout shift is negligible in this path (CLS 0 to 0.017 in the rich runs).
- Waterfall (slow run): the 406 KB HTML document streams from 0 to 9.3 s while sharing the 200 KB/s pipe with the 350 KB Inter preload (High, 0.2 to 10 s), the italic Inter file (386 KB, VeryHigh, 1.7 to 11.7 s), a 182 KB gtag script and the hero images. The inline flagship style, about halfway through the document, is therefore not complete until about 3.5 to 4.5 s.
- **Fast vs slow:** in fast runs the *first* LCP candidate is `DIV.fv-margin-strip__window` at 1.6 to 1.7 s with size about 211,000 px². That is the margin strip painted before its own `<style>` (the strip's markup is at about 154 KB into the document, its CSS about 13 KB later). With the strip CSS removed the strip window box is enormous; styled it is 296x76 = 22,458 px² (unthrottled measurement). In slow runs (inferred from their first LCP candidates, not separately instrumented) the first paint happened before the strip markup or after its CSS, so the first candidates are small (a 5,733 px² tagline, then the chapter nav or the unstyled paragraph) and the styled paragraph (34,711 px²) becomes the LCP when it finally paints.
- **Causal test (`e13`, 25 rounds, identity):** moving the strip's `<style>` in front of the strip markup (header region; probe only, not a proposal) turned the fast mode off: strip_css_first 25 of 25 slow (median 4,880, p75 4,928, p95 4,977 ms, LCP element always the paragraph) vs the same-batch base 18 fast / 7 slow.

## 3. The local-copy method does not represent the live wire

The live response is brotli, about 89 KB (gzip 91 KB; 406 KB identity), chunked, from the WordPress.com edge (`curl`, 2026-11-03). The documented local server sent the 406 KB identity body, about 4.5x the live bytes, so through the 1.6 Mbps pipe the flagship `<style>` (about halfway into the document) arrives much later than on the live page (not isolated as a separate number; the gzip runs below show the effect). Serving the same saved copy with `Content-Encoding: gzip` (`--enc gzip`) changes everything:

| Run set | n | LCP median | p75 | p95 | max | modes |
|---|---:|---:|---:|---:|---:|---|
| local copy, **gzip**, base + control (`e2`) | 40 | 1,890 to 1,964 | 2,062 to 2,070 | 2,183 to 2,258 | 2,468 | one: paragraph is LCP in 40 of 40 |
| local copy, gzip, base (`e5`) | 30 | 1,890 | 1,933 | 2,196 | 2,312 | one |
| **live URL** (`e3b`; plain URL, collection aborted) | 30 | 1,810 | 1,875 | 2,074 | 2,236 | one (paragraph, 30 of 30) |
| live URL (`e3`, run first; the next job overlapped its last minutes) | 30 | 2,138 | 2,307 | 2,548 | 2,700 | one |

On the live-like path the paragraph is styled in the first paint (rich runs `e11`, 20 of 20 gzip, and `e12`, 9 of 10 live: first paint 1.5 to 2.1 s; FCP equals or nearly equals LCP; an `EM` candidate 16,128 px² may precede the paragraph by under 125 ms). LCP is therefore gated by FCP, which is gated by a 550 to 625 ms main-thread task at about 1.0 s plus the head's render-blocking CSS, not by the hero.

**One live-path outlier, honestly reported:** in `e12` (rich, 10 live runs) run 3 had FCP 2,948 ms, the paragraph painted unstyled at 3.2 s and styled at 4.1 s, LCP 4,236 ms, with a 273 ms task at 2.97 s and an 821 ms task at 3.4 s. That is the same unstyled-then-styled sequence on the real site. Across all live-path runs (30 + 30 + 10) it was seen 1 time in 70 (1.4%); the other 69 were at most 2.7 s. I did not establish what delayed that one run (a late chunk or edge response is the likely reading; unproven).

## 4. Cold vs warm, CPU and network sensitivity (gzip local copy, base, `n=20` each)

| Condition | LCP median | p75 | p95 | max | paragraph is LCP |
|---|---:|---:|---:|---:|---|
| baseline cold, 4x CPU, 1.6 Mbps (`e2`/`e5`) | 1,890 to 1,964 | 1,933 to 2,070 | 2,196 to 2,258 | 2,468 | all |
| **warm** HTTP cache (primed, then second load), 4x | 1,106 | 1,158 | 1,248 | 1,408 | 20/20 |
| cold, **2x** CPU | 1,446 | 1,506 | 1,649 | 1,740 | 20/20 |
| cold, **6x** CPU | 2,734 | **2,978** | 3,343 | 3,620 | 20/20 |
| cold, 4x CPU, **0.8 Mbps** | 2,270 | 2,390 | 2,571 | 2,712 | 20/20 |

No second mode appears in any of these. At 6x CPU the whole distribution simply moves (p75 about 3.0 s, above 2.5 s; the founder's standard is 4x). The gzip results are unimodal at every setting, so the bimodality is not a CPU-throttle artifact; it is an artifact of the uncompressed-HTML delivery combined with the first-paint race. (Slow-share figures in the raw analyzer output for `e8` use a 3,000 ms split and are only the upper tail of one slow mode, not the bimodal mode.)

## 5. One change, tested on the local copy only

`hoist_css` (variants.py): move the flagship `<style>` element in front of the flagship markup, same bytes, same block, nothing else.

| Encoding | variant | n | LCP median | p75 | p95 | modes |
|---|---|---:|---:|---:|---:|---|
| gzip (live-like) | base | 30 | 1,890 | 1,933 | 2,196 | one |
| gzip | hoist_css | 30 | 1,910 | 2,029 | 2,095 | one |
| identity (documented) | base | 30 | 1,668 | 1,680 | 4,892 | 26 fast / 4 slow |
| identity | hoist_css | 30 | 1,676 | 2,470 | 2,851 | none above 3 s; paragraph is LCP in 8 |

On the live-like path the difference in medians is +20 ms (permutation test p = 0.44): **no measurable gain, so it is not proposed.** On the uncompressed copy it removes the 4.9 s tail only because the paragraph is no longer painted unstyled; this is the right ordering in principle (CSS before the markup it styles) but it solves a problem the live wire does not have. It would also move the 57 KB stylesheet ahead of every byte of hero markup, a risk with no tested benefit. No visual, typography, accessibility or analytics behaviour was altered in any run. `no_inter_preload` exists in `variants.py` but was not run (the founder rejected that lever; the earlier note measured about 0.13 s).

## What is established and what is not

Established (measured, tool and mode as above):
- Both modes reproduce on the uncompressed local copy; the A/A control is identical.
- Both modes have the same real styled-paragraph time (about 4.7 s, rich n = 16); the fast mode is an unstyled-strip LCP mask (causal test e13, 25/25 turned slow).
- With live-like compression, and on the real live URL, there is one mode, with the paragraph in the first paint.
- Warm cache, 2x CPU, 6x CPU and 0.8 Mbps shift the distribution but do not create a second mode.

Not established:
- Field p75 (no RUM data was read). Everything here is lab, throttled Edge, one machine.
- What made 1 of 70 live-path runs behave like the slow mode.
- Whether Chrome's mobile profile on a real device chunk-splits HTML the same way; only Edge desktop emulation was used.
- The residual cost on the live path: LCP is about FCP (1.8 to 2.1 s). Reducing it means improving FCP: the roughly 0.6 s main-thread task at about 1 s and the head's render-blocking CSS and theme/plugin payload, which sit outside page 6's block (consistent with `PR604_MOBILE_LCP_FOLLOWUP_DIAGNOSIS.md`).

## Recommendations (no production edit)

1. Stop treating the uncompressed local copy's "slow mode" as a proxy for the live site. Use `harness.py --enc gzip` for local variants and `--live` runs for the real page; report modes separately.
2. Keep the founder standard on the live-path distribution: lab p75 about 1.9 to 2.3 s at 4x/1.6 Mbps (meets 2.5 s), but p75 about 3.0 s at 6x CPU, so the margin is not large on slower phones. Field data is still the arbiter.
3. Header owner (lead session): the margin strip ships markup before its CSS, so it can paint unstyled when a chunk boundary falls between them (observed locally in the uncompressed case). It did not produce the fast/slow split in the 270 gzip and live-path runs (one live outlier is described above; whether the strip was involved in it was not checked), so this is a note, not a request.
4. If a flagship-block change is ever wanted for robustness, the `hoist_css` ordering is the candidate; it would need a new exact head and independent review, and there is currently no measured justification.

## Reproduce

```
cd docs/experience-2.0/evidence/perf-2026-11-03-lcp-bimodal
PYTHONUTF8=1 python harness.py --html saved_live_home_2026-11-02T22-46.html --variants base,ctl --runs 40 --mode light --wait 1500 --out runs/x.jsonl            # documented (identity) method
PYTHONUTF8=1 python harness.py --html saved_live_home_2026-11-02T22-46.html --variants base,hoist_css --variant-file variants.py --enc gzip --runs 30 --out runs/y.jsonl
PYTHONUTF8=1 python harness.py --html saved_live_home_2026-11-02T22-46.html --variants live --live https://finalvestige.com/ --runs 30 --out runs/z.jsonl
python analyze.py runs/x.jsonl ; python combine.py
```

Run files: e1 identity A/A (80), e2 gzip A/A (40), e3 and e3b live (30 + 30), e4 identity rich (16), e5 gzip hoist (60), e6 identity hoist (60), e7 gzip warm (20), e8 gzip CPU 6x (20), e9 gzip CPU 2x (20), e10 gzip 0.8 Mbps (20), e11 gzip rich (20), e12 live rich (10), e13 identity strip-CSS-first (50). `e3`'s final minutes overlapped the start of `e4` (a missing `pgrep` in the queue script); `e3b` is the clean re-run. The saved HTML was decoded with replacement characters in the earlier session (one em dash is U+FFFD), a same-byte-length difference (3 bytes either way) that does not affect timing.
