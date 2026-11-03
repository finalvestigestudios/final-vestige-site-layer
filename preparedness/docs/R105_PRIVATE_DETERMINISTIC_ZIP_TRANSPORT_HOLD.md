# R105 — Reproducible private source/citation review ZIP (STRICT HOLD)

**Preparedness Archive / Issue #136. Private engineering transport only.** This is an additive child of the R104 exact original-evidence packet; it makes no change to original article depth, citation occurrence, source records, shared-URL identity, safety states, taxonomy, URLs, WordPress bodies, navigation, homepage or public content.

## Problem addressed

The R103/R104 reviewer packet consists of five mutually related files. During offline handoff, a reviewer can receive a partial ZIP, an archive with a replaced CSV, an extra misleading “approved” file, a symlink/traversal payload, or a repacked archive with subtly different timestamps, permissions or encoding. Matching the submitted ZIP's own checksum or manifest is not sufficient: an altered packet can be resealed. R105 binds archive **bytes**, ordered member names, metadata, CRC and member data to the **original independently reconstructed R104 source/citation packet**. It never extracts an untrusted ZIP.

## Fail-closed controls

- Exactly the five original R104 evidence files, in original order, with no additional or missing entries; the R104 private HTML, source variants CSV, citation occurrences CSV, R103 summary JSON and R104 manifest remain byte-identical.
- Reproducible UTC-independent ZIP timestamps fixed at 1980-01-01, STORE only (no decompression bomb), regular-file Unix mode 0600, no extra fields, comments, links, encrypted entries, folders, duplicates or alias paths. Prevent ZIP-slip and symlink export attacks.
- Source text, citation context, author-specific reading scope, evidence provenance and all **30 unresolved literal shared-URL groups** remain inherited from R102–R104. No URL collision is treated as a validated citation or shared claim authority.
- Archive is verified against **newly replayed** seven-cluster source records and not against a user-supplied manifest; a rehashed or forged “reviewed” manifest is still rejected. Hashes are not signatures or human attestation.
- Export occurs only to a pre-existing **empty scratch directory outside the Git repository**, with exclusive create / no-overwrite / nofollow file writes; read verification never extracts or writes back to the tree. Only one private `r105-private-source-citation-packet-HOLD.zip` is produced.
- Automated tests use only memory and OS temporary directories, not shared source fixtures.

## Private exact-head usage (Python 3.12, local or GitHub ephemeral runner)

```sh
python -I -m compileall -q preparedness/tools/r105_private_packet_zip_custody.py preparedness/tests/test_r105_private_packet_zip_custody.py
python -I -m unittest discover -s preparedness/tests -p 'test_r105_*.py' -v
python -I preparedness/tools/r105_private_packet_zip_custody.py --dry-check
scratch_dir="$(mktemp -d)"
python -I preparedness/tools/r105_private_packet_zip_custody.py --emit-dir "$scratch_dir"
python -I preparedness/tools/r105_private_packet_zip_custody.py --verify-zip "$scratch_dir/r105-private-source-citation-packet-HOLD.zip"
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

Outputs are for trusted human review **offline only**. Do not copy the ZIP to public hosting, WordPress, a newsletter asset folder, or a publish pipeline. Do not release even a mechanically valid packet without secure approved review procedures.

## Unresolved — NO RELEASE AUTHORITY

This is **not a safety or citation correctness claim**. The original 35-article slate and one complete water-planner tool remain private drafts; five planned tools are not importable. The 30 shared-URL groups require distinct per-claim and per-edition human source review. Five contributor-provenance discrepancies, 15 safety exceptions, 22 editorial decisions, actual browser/print accessibility, qualified medical/emergency guidance review, independent QD and mandatory 13-stage machine integrity remain HOLD. Original author safety records with previously recorded `approved` or `not-required` status are preserved, never promoted into a new independent qualified safety approval.

Independent QA PR #157 and synthetic-fixture PR #169 stay separate draft/unmerged; #169 still has a working-tree-writing `_dup_test.json` fixture. Homepage PR #49 and flagship PR #604 are explicitly outside scope. No merge, publication, CMS write, navigation change or public update is authorized by R105.
