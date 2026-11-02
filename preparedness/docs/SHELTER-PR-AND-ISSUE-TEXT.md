# Ready-to-paste: draft PR description and Issue #136 update

The GitHub CLI was not available in the session that prepared this, so the PR was not opened and the issue was not commented on. Open the PR from https://github.com/finalvestigestudios/final-vestige-site-layer/compare/feature/preparedness-archive-v1...claude/prep-shelter-continuation as a draft, using the PR description below, then post the issue update.

## Draft PR description

## Shelter, Power and Family Communication: continuation (draft, nothing published)

**Branch head:** `3e214ed` on `claude/prep-shelter-continuation`. It starts from the review candidate `5daeaf2` (branch `claude/prep-shelter-5e1e0e`, left untouched).

**Release state: DRAFT. QD PENDING. Human safety review PENDING.** All four articles and all three tools are `status.publish: draft` and `safety_review.state: pending`. No WordPress, navigation, homepage or `/focus/` change. Nothing here is approved, and no source link has been human-verified (`human_link_check: false` on all 41 sources).

### What changed
1. **Evidence pass.** Read for the first time: NFPA high-rise tip sheet, USFA high-rise, two-ways-out and escape-grid handouts, CDC chemical shelter-in-place (June 2026), NWS stuck-vehicle guidance, FEMA reunification fact sheet (marked archived), NCMEC hotline page, Ready.gov Get Tech Ready, CPSC CO tips. Ten sources added (41 in `sources/fragments/shelter.json`).
   * High-rise: NFPA's own high-rise sheet does not repeat "defend in place"; the documents agree on stairs as the default. #13 says so and tells no one to defend in place on their own judgment.
   * The "fast hazards mean shelter" shorthand is removed from #14 (body, dek, meta description); replaced by four deciding factors, a diagram and "official order first".
   * CDC's 10-minutes-per-hour vehicle instruction is corroborated by NWS and kept with attribution and caveats (flagged for the reviewer).
   * Chemical shelter in place compared across CDC (2026) and Ready.gov (2023); no sealed-room duration is given.
   * NCMEC's number verified against NCMEC's own site; Ready.gov (2026) now leads on texting, FCC demoted.
2. **Three offline-first tools** (free, local-only, nothing stored or sent, work without JavaScript, print scoped to the sheet): home fire escape plan worksheet, power-outage readiness planner (no generator sizing, wiring, fuel, ventilation or medical advice; medical-device households are sent to their provider, supplier and utility), family communication and reunification card (fold-over wallet card, minimal-information version, address and ID warnings, 7.5 pt).
3. **Two original diagrams** and cross-links among articles and tools.
4. **Review package:** `docs/SHELTER-SOURCE-LEDGER.md`, `docs/SHELTER-QD-PACKET.md`, `docs/SHELTER-QA.md`, `docs/CLUSTER-shelter.md`.

### Test results (repo root)
* `python -I preparedness/tools/validate.py`: 0 errors, 0 warnings
* `python -I preparedness/tools/build.py`: succeeded
* `python -I -m unittest discover -s preparedness/tests -v`: 64 tests; with a verified axe-core 4.10.2 bundle (`PA_AXE_JS`), 64 passed, 0 skipped; without it, 63 passed and the axe test is skipped
* Real-browser tests (Edge/Chromium 156 via Playwright 1.64): widths 320 to 1920, keyboard, focus, target sizes, no-JS, reduced motion, print page counts, HTML injection, no network or storage. axe-core: no violations on the three tools and four articles at 390 and 1440 px.

### Not tested, and release blockers
* Not tested in WordPress or the Assembler; not in Firefox or Safari; no screen reader run; no paper print test; layout stability not measured.
* Open reviewer decisions (listed in the QD packet): indoor fuel-heater handling, the numeric vehicle instruction, combined medication wording, the high-rise reading, window wording when sealing in, the four-factor framing, CDC versus Ready.gov hazmat steps, custody and card-privacy guidance with no source, USDA food-safety pages unverified, one state example only for school reunification.
* `taxonomy.json` gained two tool rows and a retitled `reunification-plan` row (all gated).

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Issue #136 update

**Shelter, Power and Family Communication: continuation pushed (draft; nothing published).**

* Branch `claude/prep-shelter-continuation`, head `3e214ed` (this notes file was added after it), from review candidate `5daeaf2`.
* Validate 0 errors/0 warnings; build succeeded; 64 tests (63 pass + the axe test skipped without a bundle; 64 pass with verified axe-core 4.10.2); real-browser QA in Edge/Chromium 156 at 320 to 1920 px; axe: no violations on 3 tools and 4 articles at 390 and 1440 px.
* Added: three offline-first tools, two diagrams, 10 sources (41 total, all `human_link_check: false`), source ledger, QD packet, QA record.
* Changed: high-rise guidance now reflects NFPA's and USFA's high-rise documents; the 'fast hazards mean shelter' shorthand is removed; chemical shelter-in-place compared with CDC 2026; vehicle 10-minutes-per-hour figure corroborated by NWS and flagged.
* **Status: QD PENDING. Human safety review PENDING. Not tested in WordPress/Assembler, Firefox/Safari, with a screen reader, or on paper.**
* Open reviewer decisions: see `preparedness/docs/SHELTER-QD-PACKET.md` (indoor fuel heaters, vehicle numbers, medication wording, high-rise reading, window wording, hazmat step differences, custody and card-privacy guidance, USDA pages unverified).
