# QA evidence report (release candidate; local previews only)

**What was actually executed, by whom, and what it proves.** All runs are machine runs by the AI lead on Windows 11 (Microsoft Edge/Chromium via Playwright, Python 3.13, Node 24, PyMuPDF). **Nothing here is human review, independent QD, the live Assembler theme, a screen reader or a real device.** Raw results are in `docs/rc/qa/`; reproduction commands are at the end.

## 1. Repository gates (real tree) and the simulation caveat
| Command | Result |
|---|---|
| `python -I preparedness/tools/validate.py` on the candidate tree | **FAILS closed**: `ValueError: duplicate source id 'fsis-power-failure' is not documented in source crosswalk` (shelter follow-up adds a third variant of a shared source; also new shared-URL groups). Expected: the frozen crosswalk/lock were not edited. |
| `simulate_custody_update.py` (copy only) then `validate.py` | 0 errors, 1 warning (32 shared-source groups without human scope review) |
| `build.py` on the simulated copy | exit 0; 50 pages (35 articles, 6 tools, 8 section hubs including Start Here, the landing page) |
The simulation regenerates `crosswalk.json` and `article-evidence-lock.json` from current bytes in a temporary copy, marked `SIMULATED_FOR_QA_ONLY_NOT_A_BASELINE_NOT_A_REVIEW`. It is **not** a pin or baseline and does not satisfy any gate. Delta: raw rows 224->244, unique URLs 186->202, shared-URL groups 30->32 (new: `weather.gov/safety/winter-during`; FSIS emergencies page), tools 1->6 (5 new article-origin entries).

## 2. Full native test suite (simulated custody, run in the real repo layout)
| Run | Tests | Failures+errors | Skipped |
|---|---|---|---|
| R61 tip baseline | 4,874 | 55 | 1 |
| Candidate | 4,924 | 87 | 2 |
Classification of the candidate's 87: 46 environment (24 symlink privilege WinError 1314; 10 nondeterministic Errno 22; 12 fixture newline README blob) + 41 other. 11 of the 41 also fail on the tip; **30 are new and all are freeze/inventory/crosswalk/count assertions** (the custody machinery, red until a reviewed re-baseline) plus one wording guard (`the two fema sources differ`). Shelter tool tests incl. real-browser tests: 28 run, all pass (1 skipped without an axe bundle). Start Here guard module: the medicine-guard assertion passes after the restore; 4 count assertions and 1 phrase guard fail. Linux/CI not run. Tests were not weakened or removed.

## 3. Rendered QA (`qa_candidate.py`; results `qa/RC-QA-RESULTS.json`)
50 pages x 8 widths (320, 360, 390, 640 [=200% zoom], 768, 1024, 1440, 1920; 320 = 400% zoom of 1280) = 400 loads.
| Check | Result |
|---|---|
| Horizontal overflow | **0** of 400 (after the CSS wrap fix; before it, 2 pages overflowed 14 px at 320) |
| Console/page errors (file URLs) | 0 |
| axe-core 4.9.1 (wcag2a/aa, 21a/aa, 22aa, best-practice) at 390/1024/1440, 150 runs | **0 violations**. Incomplete: `color-contrast` (paper-textured boxes; hand-computed ratios at R48 were 7.4:1 or higher, not recomputed for new pages) and `aria-prohibited-attr` on `reunification-plan` (Start Here tool): **needs manual inspection** |
| Exactly one h1; heading jumps; duplicate ids; broken `[n]` citation anchors; unreferenced sources; broken in-page anchors | 50/50; 0; 0; 0; 0; 0 |
| Tables (68): caption + labelled focusable scroll wrapper | 68/68 |
| External links without `rel=noopener`; JSON-LD parse errors | 0; 0 |
| Archive-internal links resolved to a built page | all (0 unresolved) |
| Keyboard: first Tab stop is the skip link; every one of first 10 stops shows focus | 50/50; 0 failures |
| `prefers-reduced-motion` | transitions 0s (0.18s otherwise) |
| Print: TOC hidden; sources present | TOC hidden 50/50; sources present on all articles; the 3 shelter tool pages print the worksheet only (by their design); PDF length median 12, max 19 pages |
| JavaScript off | article text intact (differences = collapsed TOC); tool pages show their no-JS fallbacks (`noscript` on 4 of 6; `water-planner` and `kit-builder` have none: QA-F2 still open for the water planner) |
| QA-F1 regression (emergency action box above the fold on phones) | 390x844: median 566 px, max 653, **41/41 articles+tools start on the first screen**; 360x740: median 593, max 680, 41/41 |
| Images | none used (no alt/size issues) |

## 4. Lighthouse lab (real runs, Lighthouse 12.6.1, Edge headless, mobile emulation, simulated throttling, local HTTP server; 5 pages)
`hub-start-here`, `landing`, `making-water-safer`, `outage-heat-cold-generators`, `power-outage-planner`: performance **100**, accessibility **100**, best practices **96** (a single console 404 from the local Python server, not a page asset), SEO **60** (the only failure is `is-crawlable`: the draft pages carry `noindex,nofollow` by design). FCP 0.87-1.23 s, LCP 0.90-1.23 s, TBT 0 ms, CLS 0, transfer 34-99 KB. **Limits:** lab numbers on localhost, not field data, not CWV from a hosted server, not the live theme; only 5 of 50 pages were run.

## 5. Source and figure checks (machine triage; `qa/FIGURE-TRIAGE-CANDIDATE-2026-11-01.json`, `qa/SOURCE-ACCESSIBILITY-CANDIDATE-2026-11-01.json`)
189 quantified claim blocks across 97 cited URLs: **178 fully matched** in the cited page text; 4 partial and 3 none (derived arithmetic such as 12/56/112 gallons, and the sentence stating no source supports "72 hours"); 4 had no machine-readable source. 9 cited URLs were **unreadable** by script (SSL failure on 2 Smithsonian pages; HTTP 403 on lewis-clark.org, timeandnavigation.si.edu, Britannica, FEMA reunification page, LoC prairie-traveler, Monticello, ready.gov/hazmat); the FEMA reunification and ready.gov/hazmat pages were later read in a real browser. **Not human link verification** (0 of 244 rows `human_link_check: true`; 15 rows have `verified_on: null`).

## 6. Not tested (explicit)
Live Assembler theme and `wp:html` script/style survival; real phones; Safari and Firefox; any screen reader (NVDA, JAWS, VoiceOver); text-spacing and forced-colors modes; hosted Core Web Vitals; physical print; Linux/CI. Visual review: I looked at 4 candidate screenshots; 6 are saved in `qa/shots/` for a human.

## 7. Reproduce (authorized environment)
```bash
git checkout integration/preparedness-release-candidate-20261101
python preparedness/docs/rc/simulate_custody_update.py ../rc_sim preparedness/docs/rc/CUSTODY-UPDATE-SIMULATION-2026-11-01.json preparedness/docs/rc/INTEGRATION-ACTIONS-2026-11-01.json
cd ../rc_sim && python -I preparedness/tools/validate.py && python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests
python preparedness/docs/rc/qa_candidate.py build/preview preparedness out   # from the repo, pointing at the simulated build
```
For in-repo test runs use `--in-place`, then `git checkout -- preparedness/sources/crosswalk.json preparedness/sources/article-evidence-lock.json`.
