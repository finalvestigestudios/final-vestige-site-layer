# QD review packet: Start Here release candidate

**QD status: PENDING.** No independent QD pass has been obtained for this commit. Nothing below is a QD pass, and nothing here approves anything. All four articles and both tools remain `status.publish: draft` and `safety_review.state: pending`.

Branch: `claude/start-here-rc` (continuation of `claude/prep-start-bbfeb8` at `2122d856`). Review the PR against `feature/preparedness-archive-v1`.

## What changed since the last QD hold

1. **Source audit.** 30 sources re-fetched; 69-row claim matrix; ledger with hashes (`audit/start-here/`). 62 of 63 sourced claims have their anchor phrases on the live pages; 1 (C21b) needs a human.
2. **Discrepancies reworked, no "winner" chosen.**
   * Refrigerated medicine: `three-day-kit` now quotes FEMA 2020 and FEMA Dec 2023 side by side, says we do not know which governs and are not choosing the newer, gives no instruction about any medicine, and routes the reader to the prescriber or pharmacist. Removed the line "we follow the newer, more cautious wording."
   * Refrigerated food: USDA FSIS (new source `start-fsis-emergency-food`) states two different conditions (a closed refrigerator keeps food safely cold about 4 hours; perishable food that has itself been above 40 F for 2 hours should be discarded). The page quotes Ready.gov, FEMA 2023 and USDA, marks the FEMA wording as possibly differing, and no longer says "use the shorter time."
   * Carbon monoxide: Ready.gov and FEMA 2023 both say 20 feet; page says it is a stated distance, not site-specific safety. The CDC power-outage page (`start-cdc-power-outage`, added 2026-11-02) gives the same distance in slightly different words.
   * HUD and FEMA assistance: no landlord-duty, RAD or eligibility inference; FEMA conditions dated and marked changeable.
3. **Two tools** (`content/tools/reunification-plan`, `content/tools/kit-builder`) with pure-logic modules, UI scripts, a no-JavaScript fallback, and tests.
4. **Editorial hub** `content/hubs/start-here.body.html`, rendered through a small new hook in `tools/build.py`.
5. **Worked examples** (invented, labeled) in each article.
6. **Tests:** `tests/test_start_tools.js`, `tests/test_start_here.py` (22 tests), `tests/browser_qa_start.py` (366 browser checks).

## Results (run on this commit)

| Command | Result |
|---|---|
| `python -I preparedness/tools/validate.py` | 0 errors, 0 warnings |
| `python -I preparedness/tools/build.py` | exit 0 |
| `python -I -m unittest discover -s preparedness/tests -v` | 58 run, 58 ok, 0 skipped, 0 failures |
| `node preparedness/tests/test_start_tools.js` | all assertions passed |
| `python -I preparedness/tests/browser_qa_start.py` | 366 checks, 0 failed (Microsoft Edge 156 via Playwright, headless; widths 320, 360, 390, 428, 768, 1024, 1440, 1920) |

Browser checks covered, per page and width: horizontal overflow, console errors, network requests (none leave the page), layout shift, load time, accessible names, id uniqueness, heading order, contrast of rendered text. Tool-specific: validation messages, blocked export on invalid input, hostile-input escaping, focus management on add, remove and clear, status announcements, download contents, no cookies, storage, indexedDB or URL state, print layout rendered to real PDFs and read back with `pdftotext`, wallet cards, reduced motion, JavaScript disabled, keyboard reach.

**Not covered** (be honest about these): axe-core (not installed); a screen reader driven by a person; installed WordPress; a physical printer; forced-colors and text-spacing modes; browsers other than Edge/Chromium; mobile devices (emulated widths only).

## Findings so far, by severity (self-review, not QD)

| Sev | Finding | Status |
|---|---|---|
| High | Plan builder normalization let invalid phone/date strings reach printed output. Found by the new unit tests. | Fixed; invalid values are dropped and export is blocked until the field is corrected. |
| Medium | `three-day-kit` chose the "newer" FEMA wording and carried its own medicine directive. | Fixed (neutral, routes to prescriber or pharmacist). |
| Medium | Editorial reconciliation of 2-hour vs 4-hour food rules could read as an official rule. | Fixed (USDA source, both wordings quoted, flagged uncertain). |
| Medium | `<script>`/`<style>` inside a `wp:html` block may be stripped by WordPress for roles without `unfiltered_html`; tools would then be inert. | **Open.** Untested: no installed WordPress. Same pattern as the existing water planner. |
| Medium | Printing from a WordPress page prints theme header and footer around the plan. | **Open.** Print CSS hides everything inside `.pa` it can reach. |
| Medium | Plan builder prints the "plan for" checkboxes (e.g. powered equipment, cold-stored medicine) and an optional wallet-card note. A reviewer should decide whether that is acceptable or whether to remove the card-note field. | **Open (reviewer decision).** Hints warn what prints. |
| Low | `C21b`: FEMA 2020 "at least 72 hours" is not extractable by `pdftotext`. | **Open (needs human).** |
| Low | Phone validation checks shape only (3 to 20 digits and separators), not locale or reachability. | Documented. |
| Low | Worked examples are invented; a reviewer should confirm none reads as an instruction. | **Open.** |
| Info | Red Cross source kind is `nonprofit`. | Done. |

## Publication blockers

1. Human safety review of the four articles and two tools (`pending`).
2. An independent QD pass on this commit (`PENDING`; to be requested from the lead session).
3. A human link check of all 29 sources in `sources/fragments/start.json` (`human_link_check: false`).
4. Human confirmation of claim C21b on the rendered FEMA PDF.
5. An installed-WordPress test: scripts and styles survive saving, tools run, print output acceptable.
6. A screen-reader pass by a person and an axe-core run.
7. Reviewer decisions: medicine box wording, FEMA 2020 vs 2023 handling, "plan for" checkboxes and wallet-card note, worked examples.
8. ~~CDC carbon monoxide cross-check~~ **Done 2026-11-02:** `start-cdc-power-outage` added and anchored (claim C34b); remaining caveat: no source says 20 feet is safe at every site.
9. Lead decisions listed below. The hub is auto-built from the articles and must not become navigation until reviewed.

## Changes to lead-owned files (please review)

* `taxonomy.json`: rows `reunification-plan` and `kit-builder` gained `"gate": true`, `"status": "drafted-pending-safety-review"` and clearer titles. (The validator raised `KeyError: 'gate'` for tool rows without the key; that is also a validator robustness bug worth fixing: `slate["gate"]` should be `slate.get("gate")`.)
* `tools/build.py`: `build_hub` now uses an optional `content/hubs/<section>.body.html` when present (tokens `{{link:...}}`, `{{hub:...}}`, `{{cards}}`). Behaviour for sections without that file is unchanged.
* Both tools live in section `field-tools` (the validator requires it), so they appear in that hub and are linked from the Start Here hub. If the tools should live inside Start Here, the validator rule and taxonomy need a decision.

## Release recommendation

Do not publish. The cluster is suitable to merge into the integration branch as drafts once an independent QD pass has been obtained, because nothing publishes until the safety gates are satisfied. Do not link the hub or tools from live navigation until the blockers above are cleared.
