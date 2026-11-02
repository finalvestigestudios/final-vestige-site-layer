# R81 — Frozen contributor / current contributor / separate RC three-way custody (PRIVATE HOLD)

**Owner:** Issue #136, Preparedness Archive only. **Parent:** R80 draft PR #694, exact baseline `c4661d9e8fa5366977f010ec581da757ac03b1d6`. **Separate article release candidate:** draft PR #584 at `ddb3528ba6494dada1fa1c3a142ce746e3a67706` — untouched. No public release or CMS writes.

## Actual blocker R81 addresses

The R14 immutable historical integration manifest records seven contributor commits, 29 contributor-authored articles, 72 scoped Git blob paths, and a single historical integrated-metadata exception awaiting human review. Five of the current seven Claude contributor references have moved forward. Previous per-run exact-current-SHA checks proved only that each *current* branch had a known head; they did **not** prove that older frozen authored text, metadata, source fragments, and the separate release candidate were equal. The mandatory release-integrity check has been failing closed; no baseline must be silently rewritten to make it pass.

## Additive engineering

`preparedness/tools/r81_frozen_contributor_threeway_custody.py` independently reads the immutable R14 manifest and 72 original scoped file records; validates original frozen contributor blobs **and** the frozen integrated tree's Git blobs exactly; reads complete byte streams from frozen, advanced contributor and independent RC commits; records per-file actual SHA-1 Git blob identities, SHA-256 byte digests, exact byte lengths and literal citation-token counts. It distinguishes unchanged, advanced-contributor-matched RC, frozen-retained RC, unrelated RC change and three-distinct-blob conflicts. Branch ancestry is recorded separately from file identity and does not establish source or emergency-safety validity.

The ledger preserves the **full unabridged candidate records** of all seven contributor source fragments (record contents, origin, raw ID, literal URL and JSON SHA-256). Duplicate exact URLs and repeated IDs are retained as **separate unresolved origin-scoped readings**. No URL canonicalization, aliasing, source merging, confidence upgrading, claim inference or medical/food/water/generator clearance is possible. Historic R14 exception remains an unapproved work order. Ledger output has SHA-256 tamper seal, exact file-count/human-state safeguards and one-way CSV that neutralizes spreadsheet formulas. The tool writes **nothing**: only stdout summary, optional private JSON or CSV.

The preexisting R80 offline full-text evidence room still covers **35 article and six tool drafts**, all 4,070 complete DOM blocks, 2,173 distinct citation occurrences, 2,359 source-origin edges and 244 complete research readings. R81 complements this with an **independent frozen-lineage comparison for the 29 specifically Claude-authored articles**; it does not replace R80 or assert that the 72-path comparison covers every one of the 35 articles.

## Reproduce in an exact trusted checkout (private only)

```sh
python -I preparedness/tools/r81_frozen_contributor_threeway_custody.py
python -I preparedness/tools/r81_frozen_contributor_threeway_custody.py --json-stdout > /tmp/r81-PRIVATE-DO-NOT-PUBLISH.json
python -I preparedness/tools/r81_frozen_contributor_threeway_custody.py --csv-stdout > /tmp/r81-PRIVATE-REVIEW-ONLY.csv
python -I -m unittest discover -s preparedness/tests -p test_r81_frozen_contributor_threeway_custody.py -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

Requires Git checkout with full historical objects and remote refs (GitHub Actions checkout fetch-depth 0), Python 3.12. Use only private temporary storage for exported review packets; **no uploaded CI artifacts, web assets or CMS publication**. Source URLs in JSON are data only. No executable workflow has been declared successful until its exact-head runner job and test totals have been inspected.

## Coordination / release hold

As verified before development, independent draft QA PR #157 is at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` and synthetic-fixture draft PR #169 is at `e9cd7766dac59d47ab467d8945269b9146c2aef5`; neither was merged. PR #169 still has a `_dup_test.json` working-tree race in a separate test, requiring owner-isolated repair. Homepage PR #49 `10495883299d53596992c26a8987f629b2904670` and flagship PR #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176` were inspected read-only; untouched. Separate RC #584 is untouched.

Human verification of source URLs/claim applicability, unresolved shared URLs/alias/fallback decisions, 15 safety exceptions, 22 editorial decisions, qualified high-consequence emergency-guidance review, actual WordPress/browser/mobile/print/assistive QA, and independent QD remain outstanding. The separate 13-stage integrity pipeline **has not passed** and cannot be waived by this tool. No branch merge, content rewrite, website navigation, WordPress, CMS, homepage, public publication or false QD PASS. **MAY PUBLISH = FALSE; all human source, claim, qualified-safety and QD approvals = 0.**
