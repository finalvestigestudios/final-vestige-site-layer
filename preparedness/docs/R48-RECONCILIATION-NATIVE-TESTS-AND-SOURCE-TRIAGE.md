# R48: current-state reconciliation, native test run, and source triage (HOLD)

**Date:** 2026-11-01. **Base:** `review/preparedness-r47-visible-evidence-row-parity-20261101` @ `7b19198ea2d0bf6707eec9a2c2268e74639d14dc` (draft PR #477). **No approval, QD PASS, medical safety clearance, WordPress change, navigation change or publication is claimed or made.** Every article remains `status.publish: draft`.

**Machine authority.** Everything in section 3 is **AI-assisted triage by a model that fetched pages and compared numbers**. It is not independent human verification and must not be recorded as such. `human_link_check` remains `false` for all 206 source records.

## 1. Reconciliation of the true current state

| Item | Finding (verified from Git on 2026-11-01) |
|---|---|
| Default branch `main` | Integration branch is 0 commits behind `main`; R47 is 244 commits ahead of `main`, 229 ahead of the integration branch |
| R47 head | `7b19198e`; draft PR #477 (base: R46 branch). A PR merge-test commit is not a merge into `main`; nothing is merged to `main` or `production` |
| 35 articles + water planner | Present (35 article metas + `water-planner`), 101,874 words in article bodies (min 1,928, max 4,345). Native `validate.py`: 0 errors, 1 warning (30 shared-URL groups lack human source-scope review) |
| Publication state | 35/35 `draft`. Safety review: 2 `approved` (`making-water-safer`, `salt-beef-salt-pork-age-of-sail`, founder approval 2026-10-29, scope recorded in each meta), 29 `pending`, 4 `not-required` (non-gated history pieces). 27 of 35 slate items `gate: true` |
| Contributor heads | The 7 contributor branches are **not** git ancestors of R47 (the integration copies content origin-by-origin and pins exact SHAs). Pins: start `2122d856`, shelter `5daeaf2d`, health `d2212d0c`, hist-food `2acf65ca`, hist-home `f654e600`, hist-field `a5ce8a62` all **equal the current branch heads**; food is pinned to PR #169's head `e9cd7766`, of which the food branch head `4b009361` **is** an ancestor. So the integration contains every contributor's post-QD self-audit commit |
| Base branch | `feature/preparedness-archive-v1` (`ee591e2`) is an ancestor of R47 |
| Open PRs | #477 (R47), #157 (Start safety wording, base `claude/prep-start-bbfeb8`), #169 (food fixture isolation), #49 (homepage, **untouched**, base `production`) |
| Source records / URLs | 224 raw rows; 186 distinct URLs; 30 shared-URL groups and 15 repeated-ID groups unresolved by human review; merged register 206 ids, all `verified_on` set, **0** `human_link_check: true` |
| Safety restrictions weakened? | Not assessed by line-by-line diff in this pass. The validator and the two approved articles' safety-review records are intact. PR #157 wording is merged into Start Here in the integration per `INTEGRATION-RELEASE-HOLD.md`; I did not replace newer wording with older PR text |

## 2. Native test run (the first one: prior sprints reported they could not execute Python)

Environment: Windows 11, Python 3.13.15, Edge. Commands, from the repo root of an exact checkout of `7b19198e`:

```
python -I preparedness/tools/validate.py        -> 0 errors, 1 warning
python -I preparedness/tools/build.py           -> succeeds
python -I -m unittest discover -s preparedness/tests
```

| Run | Tests | Failures | Errors | Skipped |
|---|---|---|---|---|
| R47 head, default Windows checkout (CRLF) | 3,753 | 14 | 43 | 1 |
| R47 head, LF checkout (`core.autocrlf=false`), no build dir | 3,753 | **13** | **38** | 1 |
| After the R48 builder fix (this branch) | 3,753 | 13 | 37 | 1 |

**So the reported "3,753 passing" is not reproduced on Windows: 50 tests do not pass.** I could not run Linux here (no WSL/Docker), so whether the suite is clean on the reference platform remains **unverified**. Classification of the 50 (LF run, final):

| Count | Cause (exclusive; sums to 50) | Nature |
|---|---|---|
| 24 | `WinError 1314`: `os.symlink` needs a privilege an unelevated Windows user lacks | Environmental. Tests should `skipUnless` symlinks can be created; as written they fail for any developer on unprivileged Windows |
| 12 | README-blob assertions in `test_r32_fragment_directory_readme_custody`: the test's own fixture writer uses text mode, so LF becomes CRLF and the Git-blob comparison fails. The committed README blob (`cec167dd...`) **does** match the gate's pin (verified with `git hash-object`) | Test portability, not a content defect |
| 9 (varies 9-10) | `OSError: [Errno 22]` writing temp-directory fixture paths (`test_draft_export_custody`, `test_r23_archive_bytes`). **Nondeterministic:** on two consecutive runs of identical code different tests in this group failed (`test_81_file_drift_46`/`_50` passed while `_42`/`_54` failed), so the total fluctuates between 50 and 51 | Environmental flake on this machine (the checkout lives under a OneDrive-synced Desktop); **root cause not determined** |
| 5 | `source-to-export byte mismatch` in `test_draft_export_custody`: fixtures written in text mode, same newline translation | Test portability |

None of the 50 failures is in a test of article text, citation wording or safety content; all are in custody, export or fixture-IO tests. That is an observation, not a clearance: the Linux result and CI remain the authoritative signal.

### Real defects found and fixed on this branch (isolated, reviewable diffs)
1. **`tools/build.py` output was not byte-deterministic across operating systems.** `Path.write_text()` converts LF to CRLF on Windows, so generated WordPress/preview files differed byte-for-byte by platform. Fixed with `write_lf()` (UTF-8, LF). Verified: 0 CRLF in 100% of regenerated outputs. Removed 1 failure (it was not the root of the export-custody mismatches, which live in the tests' fixtures).
2. **`tools/citation_occurrence_priority_gate.py` crashed printing JSON on a Windows console** (`'charmap' codec can't encode '−'`) because it emits `ensure_ascii=False`. Fixed by reconfiguring stdout to UTF-8. Verified: all **1,959** review tasks now emit as valid JSON. **Ten other `print(json.dumps(..., ensure_ascii=False))` sites in `preparedness/tools/` likely share the bug and are not yet fixed.**

Not changed: any test, any gate, any article, any source record, any fingerprint.

## 3. Source accessibility and figure-to-source triage (AI-assisted, numbers only)

Method (scripts in `docs/r48/scripts/`): extract every article block that carries a `{{cite:id}}` token **and** a quantified figure (number plus unit: degrees, feet, minutes, hours, days, drops, teaspoons, gallons, percent, etc.): **186 claim blocks, 89 distinct cited URLs**. Fetch each URL with an honest user-agent. Where a script is refused or the page is JavaScript-rendered, retry in a real Edge session (no header spoofing; stop on any block page). Extract text from PDFs with PyMuPDF. Test whether each figure's number occurs in the cited page text. A figure being present is **necessary, not sufficient**: it does not prove the claim is read in context, correctly scoped, or current.

**Source accessibility (89 URLs, `docs/r48/SOURCE-ACCESSIBILITY-2026-11-01.json`):** 82 produced usable text (63 by script, 20 by browser, 6 PDFs by browser + PyMuPDF; the browser/PDF counts overlap categories as listed in the file), **7 remained HTTP 403 even in a browser and are recorded as unavailable, not assumed supported:**

- americanhistory.si.edu (2 pages: Ocean King provisions; refrigeration story)
- lewis-clark.org (Fort Clatsop salt works)
- timeandnavigation.si.edu (sextant)
- britannica.com (Donner party)
- loc.gov (The Prairie Traveler resource)
- monticello.org (cisterns)

Two URLs resolve to a different final URL; both are recorded per row. Each row records status, final URL, title, any page-date metadata, byte/char/page counts and a SHA-256.

**Figure results (`docs/r48/FIGURE-TRIAGE-2026-11-01.json`):**

| Result | Claim blocks |
|---|---|
| All figures found in the cited live source | **178** |
| Some/no figures found | 5 |
| No testable source (blocked pages) | 3 |

The 5 "not found" are all explainable, with **no contradiction between a stated figure and its cited source found**: (a) arithmetic that is our own and labeled as such (water-math 12/56/24/112 gallons; 12 gallons in real-households); (b) an "uncertain" note stating the sources do *not* give 72 hours; (c) a sextant "60-degree" arc whose Smithsonian source is blocked. The 3 untestable blocks cite Britannica, Monticello and the Smithsonian pages above. During the work a flaw in my own first checker was found and fixed: a JavaScript-rendered NFPA page returned 58 characters and was wrongly counted as tested; thin pages are now retried in a browser and never counted as tested. With the page rendered, the fire article's **10-foot and 50-foot** NFPA figures **are** present.

**What this does not cover (do not infer verification):** claims with no numbers, qualitative or medical-wording accuracy, whether a figure is attributed to the right document when several are cited, currency of the page versus the article's date, any page whose text I could not read, and anything requiring a clinician. The 2020 FEMA Are You Ready? guide and the Dec 2023 FEMA fact sheet disagree on refrigerated medicine; that reconciliation was handled in the Start Here corrections and still needs qualified human review.

## 4. Still blocking editorial completion (unchanged by this pass)

Human review of all 30 shared-source groups; human link click-through (0 of 206); clinical/food/water/CO/infant/disability safety review (29 articles `pending`); live-theme render check; rendered-page QA for the full archive; the open CDC 6,500 ft vs EPA 5,000 ft boiling-elevation reconciliation (retained exactly as approved, not silently harmonized). Full rendered QA at 360/390/768/1440 and axe was executed in earlier sprints only for the first 11 pages; **the full 35-article archive has not had rendered QA in this pass.**
