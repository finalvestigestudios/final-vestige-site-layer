# R63 — contributor source-impact crosswalk (PRIVATE / RELEASE HOLD)

**Issue #136.** Exact stacked parent: R62 draft PR #566, SHA d7944cec67c22952e7e74d4981e7e7adad28ea07. R63 is isolated, unpublished, and does not modify any original contributor research, original R14 provenance manifest, R58 complete 35-article evidence, site content or WordPress.

## Substantive improvement over R62

R61 preserved two versions of the seven contributor source inventories and 29 original contributor articles (72 original frozen files). R62 protected changed article claim context. R63 adds a separate deterministic, exhaustive **source-record reverse-impact crosswalk** so even an **uncited source** or source whose URL/notes changed under an existing ID cannot disappear between versions.

Each source work order preserves the complete frozen and proposed contributor source-reading dictionaries, plus all candidate citation occurrences and unabridged article metadata source-use notes. Its provenance identity binds contributor cluster, original source ID, change kind and both record hashes. Four statuses are explicit: ADDED_NOT_APPROVED, REMOVED_NOT_ALIASED, CHANGED_NOT_APPROVED, and UNCHANGED_NOT_REVERIFIED. Every original/proposed record gets exactly one source-identity work order, even if cited zero times.

Shared IDs across contributors and exact URL collisions are preserved as distinct reading identities. Unmatched citations and metadata source-use references are retained separately, not silently mapped to another source. Candidate source IDs are NOT proof of claim support; existing source verified_on or human_link_check metadata is historical data, NOT independent verification. This tool does not claim to revalidate the six additional integrated articles or the original R58 full-corpus 1,959 citations.

The CLI first regenerates the original R61 packet from trusted Git objects, then verifies the full R62 claim-context docket against that packet, then constructs the source-impact report and SHA-256 fingerprint. No cached report or changed freeze baseline substitutes for that check. Missing original Git objects must fail closed.

The separate all-record CSV has immutable source/citation custody columns and exactly one editable notes column. Raw URLs and original reading notes stay in the complete private JSON report, not spreadsheet cells. Returned reviewer notes undergo exact-order/row/column checks and reject formula-like NFKC text, hidden Unicode formatting controls, malformed UTF-8 and altered source identities. Even an annotation declaring “approved” remains unsigned and UNTRUSTED_NOT_REVIEWED, with all publication and medical-safety clearances false.

## Confirmed exact contributor Git refs

- Start Here: claude/prep-start-bbfeb8 at 2122d856fce9f64887c16df3d52e64be9f59a55b (unchanged from R14).
- Shelter: claude/prep-shelter-5e1e0e at 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976 (unchanged from R14).
- Food: claude/prep-food-ccdc55 at f911ff7a655de8d81535ea86ec3d65a49ee76648, original 4b009361277ea1d4617b368f5d45104c7318b284.
- Health: claude/prep-health-837444 at d5ef5bafd68361434dd1cc9209915b8e8a4eaf17, original d2212d0ca0750817d3929865d3069835980faf20.
- Historical Food: claude/prep-hist-food-b81f19 at 67e116e536c7410bed30f8f3b1bb8c166f3c223d, original 2acf65ca3efa9b4b5db7976f379b9ea693be43a4.
- Historical Home: claude/prep-hist-home-0e0e38 at 7504a5f099594d635e3dd7332a33a2e1346c43a2, original f654e600f89c321a480dd8f055be4d13d0673490.
- Historical Field: claude/prep-hist-field-9db767 at 4e5caf812727953aa45e3bda2d382f2c67b6a09c, original a5ce8a62f168db05c95232e3eb385dccd0d19e7f.

Five contributors advanced, with 23 changed Preparedness files. Seven changed article bodies have 315 frozen vs 334 proposed citation tokens, +19 **unreviewed** proposed occurrences. These are NOT merged into the original 1,959-citation archive.

Independent safety QA PR #157: 7d1ae6b8ef93d10cfb6810987672360885e9c1aa (drill/medication safety/source taxonomy). Synthetic fixture QA PR #169: e9cd7766dac59d47ab467d8945269b9146c2aef5 (non-mutating test fixture). Both inspected and remain unmerged. The separate Start Here RC #553 SHA 2af10621b0f4b5837f9224bf7f7163cc21590293, shelter evidence #554 SHA 6a5998ead97eca997e573ce8d3ceacf1c6aabad4, flagship homepage #550 SHA 6ef459ec76208fc84022328b938d79bf556ac774, and Chromium QA #565 SHA 91ca7a7d0e9e1b22374ea354775a0ae9d985e502 were checked but untouched.

## Execution on an exact trusted full checkout

    python -I preparedness/tools/r63_contributor_source_impact_crosswalk.py --summary
    python -I preparedness/tools/r63_contributor_source_impact_crosswalk.py --csv > /tmp/preparedness-r63-private-source-review.csv
    python -I -m unittest discover -s preparedness/tests -p 'test_r63_contributor_source_impact_crosswalk.py' -v
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

The dedicated isolated workflow checks exact R62 parent and the four changed R63 paths, and runs previous R60/R61/R62 tests plus new R63 synthetic/adversarial tests. It is NOT the mandatory full 13-stage pipeline. Historical contributor parity still fails closed; do NOT rebaseline, skip it, or claim full validation and build passed. Hosted outcomes and exact commits must be recorded in Issue #136.

## Absolute release HOLD

The original 35 articles and water tool are private drafts. Outstanding: 206 human source-link checks, 30 shared URL groups, 43 fallback relationships, 15 open safety exceptions, qualified emergency/water/food/medical content review, real WordPress/print/browser/accessibility QA and independent QD. No publication, navigation, CMS writes, production merge, unsafe medical approval, original-evidence overwrite or source-ID alias is authorized.
