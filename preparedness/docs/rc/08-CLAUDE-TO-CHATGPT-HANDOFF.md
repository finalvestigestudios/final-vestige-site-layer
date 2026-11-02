# Claude-to-ChatGPT handoff: Final Vestige Preparedness Archive (self-contained; written 2026-11-02)

You can resume from this file without re-researching. Everything here is AI-produced and **unreviewed by any qualified human**. **Nothing is published. Release authorization is NOT granted.**

## 1. Mission and rules (from the founder)
Build "The Preparedness Archive" for Final Vestige Studios (target `finalvestige.com/preparedness/`): "What people knew. What still works. What keeps a household ready." Two tracks: Modern practical preparedness ("Act now") and "The Lost Ways" (historically documented practices judged against modern safety). Journey: Archive -> Start Here -> Practical Guides -> Lost Ways -> Sources and Safety Notes. Visual identity: obsidian/charcoal, dark teal, antique gold, parchment details, evidence-first, mobile-first. Master spec and worklog: GitHub Issue #136 in `finalvestigestudios/final-vestige-site-layer` (private; use the API with the Git credential helper, `gh` is not installed).
**Hard rules:** never fabricate citations, quotes or numbers (no invented curing, canning, water-dose or medical figures); human safety review before publishing high-consequence pages; keep the archive private; no QD PASS, editorial clearance, medical-safety claim or publish permission without real evidence; a general "I approve" is not approval of a specific item; do not touch the homepage (Experience 2.0 is the top site priority), PR #49, `/focus/`, WP draft 85, live navigation (block navigation ID 5), production WordPress, or frozen SHAs/pins; no spending or subscriptions; coordinate before shared `build.py`/CSS/validator edits; no merges to protected branches.

## 2. State in one paragraph
35 article drafts + 6 local tools + 8 section hubs + landing exist and build (50 pages) on the **release-candidate branch** `integration/preparedness-release-candidate-20261101` (base: R61 PR #559 `bdfd0879`). 29 articles and 6 tools are `safety_review: pending`; 2 articles carry a founder one-word chat "approved" that is **not** a completed review (qualified; decision X-2); 4 history articles are `not-required`. 0 of 244 source rows are human-link-checked. Machine checks are strong (axe 0 violations, 0 overflow at 8 widths, Lighthouse 100/100/96/60 on 5 pages, 178 of 189 figure blocks matched) but the repository tree **fails its own custody gates by design** because the integration changes frozen inputs. Only WordPress write ever made: draft page 1868 (never checked in the live theme).

## 3. Where things are
Read in this order on the candidate branch under `preparedness/docs/rc/`: `01-CANONICAL-RELEASE-CANDIDATE-MAP.md` (PRs, branches, SHAs), `02-R48-R49-RECONCILIATION-REPORT.md`, `RC-ARTICLE-SAFETY-REGISTER-2026-11-01.md/.csv` (41 rows, every row NOT REVIEWED; 20 HIGH / 20 MEDIUM / 1 LOW by a keyword heuristic), `04-START-HERE-SHELTER-DECISION-REGISTER.md` (22 open decisions), `05-QA-EVIDENCE-REPORT.md`, `06-RELEASE-READINESS-MATRIX.md`. Earlier evidence: `docs/r48/` (SX-01..SX-15 safety exceptions, rendered QA, readiness matrix), chain docs R12-R61 in `docs/`.
Tools: `integrate_contributors.py` (re-run integration), `simulate_custody_update.py` (QA-only copy; `--in-place` for repo-layout test runs, then `git checkout -- preparedness/sources/crosswalk.json preparedness/sources/article-evidence-lock.json`), `qa_candidate.py`, `build_safety_register.py`.

## 4. Key facts a newcomer would get wrong
- The chain is R48 -> R50 ... R61 (13 stacked draft PRs by other agents). PR #484 ("R49") is a sibling not in the chain. My earlier branch named `...r49-shelter-continuation-reconcile...` is superseded.
- Contributor branches (frozen pin -> newest): start `2122d856`->`2af10621`; shelter `5daeaf2d`->`6a5998ea`; food `4b009361`->`f911ff7a`; health `d2212d0c`->`d5ef5baf`; hist-food `2acf65ca`->`67e116e5` (**not integrated**, decision S-7); hist-home `f654e600`->`7504a5f0`; hist-field `a5ce8a62`->`4e5caf81`.
- The custody freeze (R22/R23/R53-R59: 35+1 inventory, 224 rows, 30 groups, pinned blobs, independent pins in gate code and tests) must not be edited by the author of the content. Re-baseline = reviewed act (decision X-1). The candidate needs: raw rows 244, unique URLs 202, shared-URL groups 32, tools 6.
- Slug collision resolved: Start Here's `reunification-plan` kept; shelter's card is `family-reunification-card`.
- Historical Simmons cookbook: the **1798** printing was read (MSU Feeding America transcription), the 1796 edition only by catalogue record.
- The Start Here RC had dropped the QD-required "Do not stop, throw away or ration a medicine you depend on..." sentence; restored.
- Windows quirks: CRLF vs LF (commit with `git -c core.autocrlf=false`; the chain is byte-pinned LF); never use bare `git stash`; cp1252 stdout crashes on non-ASCII (use `PYTHONIOENCODING=utf-8`); about 46 test failures are Windows-only (symlink privilege, Errno 22, fixture newline); `git clean -e` did not protect untracked files (commit scripts first).

## 5. What is not done
Independent QD; human safety review (29 articles + 6 tools); named reviewer roster; human link check; 9 machine-unreadable sources; 32 shared-source groups unreviewed; custody re-baseline; live-theme, WordPress script/style, screen-reader, Firefox/Safari, hosted CWV and Linux/CI checks; QA-F2..F6 (water planner no-JS note and silent clamping, flat hubs, 360 px table scroll, live-region verbosity); an archive-level "Sources and safety notes" page (gap, not a new article); editorial excellence rewrites; hub design refinement. The shelter session is paused awaiting direction; other contributor sessions are idle.

## 6. Recommended next three actions
1. **Get human reviewers and decisions.** Name a pharmacist/clinician, a food-safety extension reviewer and a fire/CO reviewer; answer X-2, X-3, S-1 and H-1..H-10 in writing; open and confirm release-critical links. Without this nothing can clear.
2. **Then do one reviewed re-baseline** (QD-owned) from `CUSTODY-UPDATE-SIMULATION-2026-11-01.json`, re-run validate/build/tests, and request independent QD on the exact head.
3. **Run the authenticated WordPress draft and real-device/screen-reader pass** (with the founder's separate go-ahead), then fix QA-F2..F6 and the `aria-prohibited-attr` item on `reunification-plan`.

## 7. Guardrails for the next assistant
Keep every page `draft` and `pending`; never mark approved or claim QD without a named person and evidence; label machine results as machine results; do not publish, merge, edit navigation or production WordPress; report outcomes with commands run and what they do not prove.
