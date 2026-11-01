# R55 — Untrusted reviewer-note quarantine / PRIVATE HOLD

**Issue #136 only.** This is an isolated, stacked draft on exact R54 #511 HEAD
`41f1b39cd033587684fbca9af7e80a89fdd591d6`.
Do not merge, publish, write WordPress/CMS/navigation, issue a QD PASS, or certify any
unreviewed advice as medically safe.

## New gap closed

R54 produced a deterministic, provenance-preserving six-file offline reviewer packet
but intentionally did not accept modified CSVs as verified research. Returning a
spreadsheet with reviewer comments previously had no safe deterministic path to
detect whether the original citations, source-reading scopes, duplicate URL variants,
article IDs, severity labels or unresolved safety states had been altered.

R55 adds **quarantined note intake**, not an approval, to solve that transport problem.
All six files are required; the original evidence JSON and manifest must be
**byte-identical** to the canonical R54 originals freshly recomputed from the current
35 article drafts and water tool. R55 checks every row and every protected CSV column
against the same canonical packet, including exact original row order and identity.
Only original `human_*_blank` columns may receive notes.

A returned note is always **untrusted and unsigned**, never:
- fact-checking completed or source link independently verified;
- independent reviewer identity or receipt-ledger attestation;
- qualified water/food/fire/medical/infant/evacuation safety clearance;
- an edited article or historical safety state; or
- QD approval or authorization to publish.

Quarantine JSON stores annotations separately, keyed to original work-order, source-ID
and incident identities, with original immutable R53 and R54 fingerprints and
edited-sheet checksums. Source records sharing the same URL remain separate by
contributor and article. Repeated citation occurrences and full reading notes remain
in original_evidence.json. Annotations do not rewrite or overwrite this source
evidence.

## Use on a trusted exact checkout

```sh
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I preparedness/tools/r53_qualitative_source_scope_gate.py --summary
python -I preparedness/tools/r54_action_review_export.py --summary
python -I preparedness/tools/r55_review_note_quarantine_gate.py --summary
python -I -m unittest discover -s preparedness/tests -v
```

`--summary` reads the genuine corpus and performs an unedited R54 round trip with
**zero actual human findings**. It is a machine-only smoke test.

To handle an actual privately returned R54 CSV packet, make a copy of the original
six-file R54 directory inside ignored `preparedness/build/`. Do not alter the
original_evidence.json or manifest.json. Edit only the blank human-note columns,
without changing headers, row order, source descriptions, URLs, citation IDs,
readings, risk classifications, source variants or review_state values.

```sh
python -I preparedness/tools/r55_review_note_quarantine_gate.py \
  --private-review-dir preparedness/build/r54-private-review-HOLD-<digest>
```

This is **read-only**. It outputs only an aggregate JSON summary, without echoing
private reviewer text. Optionally append `--write-private` to create a separate
exclusive, ignored `preparedness/build/r55-quarantine-HOLD-<fingerprint>/` containing
`UNTRUSTED_NOTES_NOT_APPROVAL.json`. It rejects unsafe folders, unexpected files,
symbolic links, malformed/non-UTF-8 CSV, row edits or additions, excessive note
sizes, Unicode direction overrides, and spreadsheet formula triggers. It will not
overwrite an existing quarantine directory.

The note overlay is a **machine-custody artifact, not a trusted review receipt**;
any independent safety/editorial approval requires separate authenticated, qualified
human review, source-context checks, and durable external receipt custody. A same-
checkout SHA-256 fingerprint cannot establish human identity or review authority.

## Verification and coordination

The new `test_r55_review_note_quarantine.py` includes 36+ independently named
protected-field mutations, note injection cases, source variant preservation,
row/order tampering, file authorization checks, private-folder checks, and one
real-corpus 35-article+water-tool test. Execute all native tests and 13 mandatory
private stages on exact PR HEAD before claiming engineering success. A green CI
**does not** advance any human source-review count or safety state.

Original seven contributor heads (verified before this sprint):
- Start `2122d856fce9f64887c16df3d52e64be9f59a55b`
- Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- Health `d2212d0ca0750817d3929865d3069835980faf20`
- Food `4b009361277ea1d4617b368f5d45104c7318b284`
- Historical food `2acf65ca3efa9b4b5db7976f379b9ea693be43a4`
- Historical home `f654e600f89c321a480dd8f055be4d13d0673490`
- Historical field `a5ce8a62f168db05c95232e3eb385dccd0d19e7f`

Independent safety QA #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`
and synthetic fixture #169 HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5`
remain unmerged drafts. Homepage #49 `10495883299d53596992c26a8987f629b2904670`,
flagship #254 `8fa6fc52e034f511b96ae526f4a852e1bd76db04`,
and Gutenberg #414 `5b70b26f3d2434a3ae53a39557f0cd5e5ac932d9`
were inspected and left untouched; default main HEAD
`77a87635eb613ce6de268aee11350fa8242efa0f`.

### Release blockers remain OPEN

Original 35 articles + water tool; 1,959 citation occurrences, 367 source-reading
relationships, 43 fallbacks and 30 shared-URL groups must remain unchanged.
**0/206** independently completed direct human source checks; 15 OPEN safety
exceptions, 25 historic inaccessible-source IDs, 542 cited/237 uncited heuristic
action blocks require real contextual source/safety review. Source retrieval,
qualified hazard assessment, actual WordPress/Assembler visual and browser
accessibility QA, independent reviewer identity, Windows test parity and
exact-final-HEAD independent QD approval remain outstanding.

**PRIVATE / DRAFT / UNVERIFIED / RELEASE HOLD.**
