# R49 — original-source-scoped numeric evidence worklist (PRIVATE / UNVERIFIED / HOLD)

Issue #136. Isolated R49 branch based on frozen R48 draft PR #483 at
`b418a5583a1dffe7a0f10fdc642a760da50b1cb9`. **Not an approval of any claim or safety instruction. Do not merge or publish.**

## Why this is necessary

R48 introduced useful AI-assisted source accessibility and numeric token triage. Its method looks for the numeric *portion* of a measurement anywhere in combined cited page text: a match for `20` is not evidence of *20 seconds*, the author's intended source, the relevant regulatory scope, or applicability to the specific household. Multiple citations may provide a number in a different context. Consequently the old labels `ALL_FIGURES_FOUND` (178 blocks), `SOME_FIGURES_NOT_FOUND` (4), `NO_FIGURES_FOUND` (1) and `NO_TESTABLE_SOURCE` (3) are **machine number-token observations only**. They do not establish accuracy or contradiction.

R49 independently re-extracts the 186 quantitative claim blocks from all 35 original article bodies. It binds each repeated citation occurrence to its own **article-scoped original source variant** through `Library.source_for(meta, sid)`, not the global convenience register. No original research note is dropped even when two clusters cite the same URL.

It then checks that the separate 89-row R48 accessibility record agrees with every claimed tested / untested source and that none of the 186 rows became stale or fabricated. The output is a **private review worklist** with the original source-record SHA, article SHA, original URL, provenance origin, and explicit pending independent unit/claim/context verification. A source with no recorded content digest is marked as such; it is not declared human-checked.

All 186 claim rows remain HOLD. There is never automatic review progress or an independent QD/safety/publication verdict.

## Independently checked R48 input inventory

| Input | Frozen Git blob SHA / observed summary |
| --- | --- |
| `preparedness/docs/r48/FIGURE-TRIAGE-2026-11-01.json` | `59332bbf77ad911334daef9c22c2edea2eb5465c` / 186 rows: 178 all number tokens located, 4 some missing, 1 none found, 3 without testable source |
| `preparedness/docs/r48/SOURCE-ACCESSIBILITY-2026-11-01.json` | `3361611ff0b7e65af7c432ebcfec8c7bee614ac7` / 89 URLs: 82 script/browser/PDF text extractions and 7 unresolved failures |
| Source record trust | 6 of the 82 usable extraction records contain no recorded content SHA-256; do not treat them as cryptographically pinned |
| Multiple citations | 93 of 186 blocks contain multiple *citation tokens*, which may refer to the same source more than once |
| Unresolved failures | 5 recorded HTTP 403 failures; **2 are TLS certificate-validation errors**, not HTTP 403. The R48 narrative's “seven HTTP403” shorthand is inaccurate; retain the exact source records |

**Accessibility limitations:** A machine/browser extraction is not a human click-through. A returned title/status or numeric token does not prove the original material was read or that a claim is current. No network requests are performed in R49.

## Machine workflow

From the exact R49 checkout:

`python -I preparedness/tools/figure_source_scope_triage_gate.py --format summary`

For all private review tasks:

`python -I preparedness/tools/figure_source_scope_triage_gate.py --format json`

Tests:

`python -I -m unittest discover -s preparedness/tests -p 'test_r49_figure_source_scope.py' -v`

Then run the unchanged project native validator, private WordPress draft builder and full unittest suite. Hosted Linux results, if available, are authoritative for this checkout. R48's Windows failures (symlink privilege, test-fixture newline translation and intermittent OneDrive filesystem errors) are a separate portability workstream, not an excuse to mark tests green.

## Human follow-up to prioritize

1. Verify the actual page/section and *units* supporting each high-consequence quantitative instruction, one cited source at a time.
2. Independently resolve the seven inaccessible URLs before attempting to rely on them; record the two TLS errors separately from the five 403s.
3. For calculations such as family water arithmetic, distinguish the cited agency baseline from the author's arithmetic derived from it.
4. Reconcile all 30 shared URL groups and 43 fallbacks with contributor-specific reading notes preserved.
5. Obtain qualified safety assessment for potentially consequential water, canning/jerky, CO/fire, medication/infant and evacuation advice.
6. Independent editorial, rendered-browser/accessibility and exact-SHA QD reviews are still required.

## Coordination and release boundary

Contributor heads read before R49 branching:

- `claude/prep-start-bbfeb8` @ `2122d856fce9f64887c16df3d52e64be9f59a55b`
- `claude/prep-shelter-5e1e0e` @ `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- `claude/prep-health-837444` @ `d2212d0ca0750817d3929865d3069835980faf20`
- `claude/prep-food-ccdc55` @ `4b009361277ea1d4617b368f5d45104c7318b284`; independent fixture draft PR #169 @ `e9cd7766dac59d47ab467d8945269b9146c2aef5`
- `claude/prep-hist-food-b81f19` @ `2acf65ca3efa9b4b5db7976f379b9ea693be43a4`
- `claude/prep-hist-home-0e0e38` @ `f654e600f89c321a480dd8f055be4d13d0673490`
- `claude/prep-hist-field-9db767` @ `a5ce8a62f168db05c95232e3eb385dccd0d19e7f`

Independent Start Here QA draft PR #157 @ `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` was examined and left separate. Homepage PR #49 @ `10495883299d53596992c26a8987f629b2904670`, homepage PR #254 @ `8fa6fc52e034f511b96ae526f4a852e1bd76db04`, Gutenberg PR #414 @ `5b70b26f3d2434a3ae53a39557f0cd5e5ac932d9` are untouched. All original 35 articles, water planner, taxonomy, crosswalk, source notes, citation occurrences, safety states, WordPress exports, site navigation and homepage files remain unchanged by R49.

**Release state is HOLD in every output.** No source was declared individually accurate, independently inspected, medically safe, or approved for publication.
