# R61 — Two-version contributor citation and source-reading lineage (PRIVATE HOLD)

**Scope:** Preparedness Archive Issue #136 only. **Parent:** R60 draft PR #551 at exact `382d649b37476ecd0b463b572acb1187fcb7028d`. Proposed work is isolated, unmerged, unapproved and NOT for publication. No WordPress, navigation, CMS, public website, homepage, taxonomic-state, article, original source, or R14 manifest edits.

## Why R61 exists

The mandatory R15 custody gate is correctly failing: GitHub contributor branch tips have advanced beyond the frozen seven-cluster R14 manifest. Simply rebaselining the manifest would silently replace documented research and defeat the citation/safety approvals. R60 records precise Git-file changes. **R61 adds per-article, per-occurrence and per-reading provenance of BOTH versions**, so qualified editors can compare them without losing the old reading notes, source URLs, duplicated source identities, or claims whose citation ID did not change.

The R61 read-only CLI independently invokes the original R15 manifest checker against **frozen** original Git blobs, then re-runs the R60 observed-vs-frozen comparison. It validates the old and new blobs and SHA-256s, retains both complete source fragment inventories (including complete reading notes), keeps every original and observed citation occurrence with Unicode codepoint positions and local HTML context, and preserves **both full HTML bodies** for each modified body. Metadata source-use maps, original publication statuses and original safety-review states are recorded separately. No ID replacement is treated as an approved alias. Repeated identical URLs are NOT deduplicated; contributor-specific readings remain independent.

The output is a deterministic private JSON with an evidence fingerprint and explicit **HOLD/NOT_REVIEWED** states; `--summary` omits long private article text. It never writes a file or WordPress resource. Any source ID absent from the seven contributing fragments is referred to the broader original R58 35-article crosswalk, NOT automatically classified as a broken citation. Merely matching a source ID or URL is NOT proof of claim support.

## Fresh exact branch comparison (2026-11-01 Pacific)

Authenticated GitHub compare API: frozen SHA to current contributor branch, checked against the R14 manifest and original R15 branch mapping.

| Cluster | Frozen R14 SHA | Observed contributor SHA | Change |
|---|---|---|---|
| start | `2122d856fce9f64887c16df3d52e64be9f59a55b` | same | no drift |
| shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` | same | no drift |
| food | `4b009361277ea1d4617b368f5d45104c7318b284` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` | 1 commit; 2 paths (cluster doc + test) |
| health | `d2212d0ca0750817d3929865d3069835980faf20` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` | 1 commit; 1 cluster doc |
| hist-food | `2acf65ca3efa9b4b5db7976f379b9ea693be43a4` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` | 1 commit; 7 paths |
| hist-home | `f654e600f89c321a480dd8f055be4d13d0673490` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` | 2 commits; 8 paths |
| hist-field | `a5ce8a62f168db05c95232e3eb385dccd0d19e7f` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` | 1 commit; 5 paths |

**New since R60:** Three additional branches have moved (food, health, hist-field), and hist-home moved again. Five of seven now diverge from frozen R14. The change set has expanded from 11 to **23 changed Preparedness paths**, including seven article bodies and six article metadata files. Do not keep describing this as a two-branch/11-file discrepancy.

### Exact observed changes needing human adjudication

- Historical food: the source ID `hist-food-nchfp-jerky` is dropped and `nchfp-jerky` introduced in its fragment, with revised URL/notes. **Eight** article citation occurrences retarget (seven pemmican, one pioneer rations); no count increase. `nchfp-jerky` may also appear in another contributor/integrated source register. R61 does not automatically collapse same-ID/same-URL readings.
- Historical home: fragment records increase from **27 to 29**. Newly observed IDs: `hist-home-wellcome-chadwick-1842` and `hist-home-msu-simmons-1798`; the existing `hist-home-loc-simmons-1796` record changes. This is materially more than the one new source reported at R60. The Wellcome evidence has **catalogue-only** reading depth; the underlying 546-image Chadwick volume was not independently read. Source-link checks remain unverified.
- Historical field: fragment records increase from **26 to 28**. Added IDs: `hist-field-oac-breen-diary` and `hist-field-ia-hastings-guide`. Existing `loc-prairie-traveler` changes. Verify source scope and actual quotations independently.
- Seven changed article bodies: `pemmican-and-dried-meats` (46→46 citations), `pioneer-travel-rations` (39→39), `pickling-fermentation-old-recipes` (42→49), `root-cellars-cool-storage` (37→42), `sanitation-before-germ-theory` (47→48), `navigation-before-gps` (47→47), and `pioneer-supply-chains-failed` (57→63). **315→334 occurrences across these seven bodies, +19 unreviewed citations.** The unchanged 47-citation sequence in the navigation article does NOT prove the changed prose is accurate.

These are new contributor-branch proposals, **not** changes to the R58 integrated original 35-article / 1-water-tool / 1,959-citation baseline. Do NOT announce a corpus-wide 1,978-citation total until proposed changes pass exact source, citation and safety review, are intentionally integrated, and all existing gates are re-run.

## Verification, invocation, limitations

Local synthetic harness for these exact authored R61 source/test blobs: `python -I -m unittest discover -s preparedness/tests -p 'test_r61_contributor_version_source_lineage.py' -q` — **69 passed** in a standalone Python 3 environment with an isolated *local R60 compatibility shim*. That receipt exercises R61 behavior against synthetic old/new blobs; it is **NOT** hosted CI proof and does not substitute the real R60 code, R15 gate, native full suite or private build.

From a trusted exact checkout containing the REAL seven remote refs, original manifest, R15 and R60 modules:

    python -I preparedness/tools/r61_contributor_version_source_lineage.py --summary
    python -I preparedness/tools/r61_contributor_version_source_lineage.py
    python -I -m unittest discover -s preparedness/tests -p 'test_r61_contributor_version_source_lineage.py' -v
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

A successful R61 report is only a **discrepancy review packet**, NOT an R15 pass. The current R15 failure must remain until independently resolved; report hosted status accurately. The separate R58 complete-corpus integrity, all 206 human link checks, 30 URL-sharing groups, 43 fallbacks, 15 open safety exceptions, actual WordPress/browser QA, qualified consequential-hazard review and independent QD approval remain required. Never claim medicine, water, fire, CO, infant-care or evacuation advice medically/safety approved.

## Independent workstream coordination

- Independent QA #157, SHA `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`: household breaker/drill and refrigerated-medication caution, Red Cross nonprofit source kind, Start Here safety gates and negative tests. Actual diff inspected. Separate **draft**, not merged.
- Isolated synthetic-fixture #169, SHA `e9cd7766dac59d47ab467d8945269b9146c2aef5`: temporary-copy fixture for the existing `nchfp-jerky` source and no original source writes. Actual diff inspected. Separate **draft**, not merged.
- Shelter continuation #521 SHA `ac8625faf30dd5538fadc31e06cb5a2cea1defae`, Start Here RC #553 and shelter evidence #554 all remain editorial/safety-review candidates, not incorporated here.
- Homepage #49 SHA `10495883299d53596992c26a8987f629b2904670`, flagship #254 SHA `8fa6fc52e034f511b96ae526f4a852e1bd76db04`, Gutenberg #414 SHA `5b70b26f3d2434a3ae53a39557f0cd5e5ac932d9`: no changes, no integration interference.

**RELEASE HOLD:** zero approvals, zero public publishing, zero WordPress/CMS/navigation writes, zero source rebaselining, zero production merges. Original 35 articles and planner remain private editorial drafts.
