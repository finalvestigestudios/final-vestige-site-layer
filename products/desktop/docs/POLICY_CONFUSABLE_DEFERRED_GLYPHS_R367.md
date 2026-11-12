# R367 — defer Policy Delta glyph cue formatting until displayed

**2026-11-11 PST / 2026-11-12 UTC · DRAFT · QD + founder HOLD · Not release approved**

## Change

R366 bounded the output citation list to 16 but still called `_changes` for every unique cross-script pair, repeatedly building skeletons, per-character changes and Unicode glyph names for unseen citations. R367 counts every valid changed physical-line pair but only formats a glyph cue when the (hunk, before, after) coordinate can enter the earliest-16 selection. Unchanged source strings are skipped. The one-character-to-one-character skeleton mapping and exact source-str validation guarantee that distinct originals with identical skeletons have a real substitution; the new regressions verify all supported mappings both directions.

Original policy text, source fingerprints, source citations, omission counts, deterministic selection, optional navigation, human interpretation, QD and founder approval remain unchanged. No Decimal money logic, premium entitlement, artifact, production, or WordPress changes.

## Executed local verification (not hosted release acceptance)

- Reconstructed isolated Python policy renderer and budget module: **16/16 R367 synthetic regressions PASS** with `python -W error`; **16/16 PASS** with `python -OO -W error`, **32 passing case executions**.
- A 500-hunk case triggered only **16** `_changes` calls versus 500 from the previous eager algorithm, with exactly +484 omitted; 2-cue and 0-cue configurations required two and zero glyph conversions respectively while counting all matches.
- Coverage includes unchanged pairs, every supported Unicode mapping, ambiguous duplicates, 200 candidates in one hunk, overlong lines, malformed late hunks, provenance ordering, source privacy, original immutability, and human review labels.
- 8,000-hunk synthetic local benchmark, four iterations per algorithm: previous eager minimum **0.2115 s**, R367 deferred minimum **0.0837 s**, about **2.53x faster** on that fixture; **byte-identical** output and exact 7,984 omitted-pair notice.

**Limit:** The executed local modules are reconstructions rather than an exact-head repository checkout. The committed R366 test module was extended by 16 tests to 31 total, already targeted by mandatory Ubuntu and Windows normal/optimized CI invocations without modifying the 212,068-byte desktop workflow. The combined 31-method file, entire inherited six-app regression suite, 22 real AES-GCM tests, and native Windows executable acceptance remain **unexecuted** by hosted CI at this point.

## Blockers / next highest-impact step

The last inspected [R366 Actions run #43132202015](https://github.com/finalvestigestudios/final-vestige-site-layer/actions/runs/43132202015) failed before either Ubuntu or Windows logged any execution steps. Root cause is unconfirmed; repository owner should inspect failed-check annotations, Actions billing/spend and runner assignment, then rerun the exact R367 head with the existing mandatory full suite, including the 31 R366/R367 tests and all 22 genuine AES-GCM cases.

After actual hosted gates pass, complete native Windows 11 x64 packaging, installation and six distinct EXE smoke tests, Defender/PE and SHA-256 verification, keyboard/screen-reader acceptance, offline privacy, and authenticated premium entitlement/download checks. All six utilities remain **UNRELEASED**; no executable, premium public link, production deployment, merge, or QD/founder bypass.
