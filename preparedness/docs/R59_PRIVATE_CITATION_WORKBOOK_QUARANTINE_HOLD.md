# R59 — Per-citation reviewer CSV and untrusted annotation quarantine (PRIVATE HOLD)

**Owner:** Preparedness Archive Issue #136 only. **Stack:** R58 exact occurrence
docket at `24d1544b9b59b6daa1527b4ee9ee7c7cd05f73ff`. Do not merge or
publish; no WordPress/CMS/navigation/homepage writes, source changes, or
independent reviewer approval implied.

## The gap closed

R58 created 1,959 exact citation-occurrence work orders but they remained
chiefly within a dense private JSON docket. R59 presents those 1,959 work orders
as a deterministic, UTF-8 CSV with one row per **original citation token**,
not one per cited URL. Distinct contributor-specific source records that share
a URL are **not deduplicated**. Every row carries a stable work-order SHA-256,
article/source/origin, ordinal, original HTML codepoint offset, frozen hashes,
URL/context/reading-note *previews*, shared-URL and fallback review flags,
related same-article/source action IDs (**NOT proof of claim support**) and
three fixed NOT_REVIEWED states.

For full context, reading depth, citation repetitions, fallback variant
provenance, and all 15 still-open safety exceptions, use the companion
`original_complete_R58_evidence.json`. Previews are clearly labeled, and
truncation is explicitly disclosed. CSV is only a *display view*, never a
replacement for original research. The reproducible `manifest.json`
checksums both files and binds them to the original R58 docket fingerprint.

## Commands and trust model

From an exact checked-out repository branch:

```bash
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I preparedness/tools/r57_global_citation_action_bridge.py --summary
python -I preparedness/tools/r58_exact_citation_occurrence_docket.py --summary
python -I preparedness/tools/r59_citation_review_workbook_quarantine.py --summary
python -I -m unittest discover -s preparedness/tests -v
```

With `--summary`, the R59 tool regenerates upstream R53/R25/R56/R57/R58
original-evidence custody in memory, verifies the deterministic presentation,
prints a small HOLD summary, and **writes nothing**.

For a strictly private workbook, use `--write-private`. This creates a new,
exclusive, owner-private directory under the existing ignored
`preparedness/build/`. It writes only the CSV, full evidence JSON, and
manifest. The folder must not already exist, and a symlink is rejected. **Do
not commit the generated private review packet** or put it in WordPress media.

An annotated CSV can be processed with `--returned-csv PATH --write-private`.
The original 18 presentation columns, row ordering, work-order IDs, original
source/URL/provenance hashes, original HTML codepoint offsets, and fixed
NOT_REVIEWED review states must match regenerated originals **exactly**.
Only the four explicitly named `reviewer_untrusted_...` fields may change.
Malformed UTF-8, unexpected fields, changed row counts, dropped/reordered
citations, dangerous spreadsheet formula prefixes, control and bidirectional
characters, and oversized annotations are rejected. The returned notes are
quarantined in `returned_notes_UNTRUSTED.json`, with the returned CSV's
SHA-256 and explicit false approval flags. Importing annotations **does not
authenticate a reviewer or transform a review state**. Original evidence is
never modified and no notes are written into article or source files.

If a reviewer types "APPROVED" into a note, that text remains an untrusted
claim, not clearance. Independent qualified review, signed source receipts,
human source checks, and QD approval must be obtained through their
separately governed processes.

## Tests and integration boundaries

The separate adversarial suite covers task uniqueness, exact original JSON
preservation, manifest/source custody, deterministic output, 18 frozen
presentation fields, malicious annotation strings in all four input columns,
tampered/duplicated/reordered/dropped rows, fake approval text, UTF-8 and
CSV edge cases, oversized input, and a live 35-article/1-water-planner
smoke test verifying **1,959 original distinct citations**. No fake reviewer
approval can be obtained by recalculating an output fingerprint.

Do not treat a successful local unit test as a complete, exact-HEAD hosted
PASS. Report actual CI run and checkout SHA. Maintain independent QA
PR #157 and synthetic fixture PR #169 separately; do not blindly cherry-pick
their changes or merge the shelter continuation PR #521. Recheck the seven
original Claude contributor branch SHAs and homepage/Gutenberg branches.

## Remaining HOLD

The archive still has **0/206 independently completed human link checks**,
30 shared-source URL groups, 43 cross-cluster fallbacks, 15 unresolved
qualified safety exceptions, historically unavailable source evidence and
hundreds of consequential emergency-action excerpts needing contextual
review. The success of a machine-generated CSV or untrusted-note quarantine
**cannot** establish source accessibility today, factual claim support,
medical/water/food/CO/infant/evacuation safety, independent QD PASS, actual
production WordPress browser QA, or authorization to publish.

No live writes, no merges, no QD PASS, and no claims of medically safe or
independently verified content.
