# R56 — Private high-consequence action/source review crosswalk (HOLD)

**Issue #136 only. PUBLIC / WORDPRESS / NAV / CMS RELEASE HOLD.**

This independent, read-only-by-default downstream gate extends R54/R55 without changing
a single original article, tool, citation, source reading, contributor identity, URL,
safety status, QA record or WordPress export. No qualified human review is asserted.

## Why this is useful

The 779 machine-flagged consequential action blocks include 237 blocks with **no
citation in that same visible block** and 542 with at least one same-block citation.
A citation somewhere else may support an uncited block; the reverse may also be true:
a same-block citation can fail to substantiate its claim. Neither classification is
an editorial verdict. We need traceable, usable human work queues **without** losing
original reading depth, repeated citations, differing contributor interpretations
of the same URL, or the existing 15 OPEN safety exceptions and 25 historical
access holds.

`preparedness/tools/r56_unreviewed_action_source_crosswalk.py` re-derives the
original R53 report through R54's native source, safety and census audit. It
independently checks per-action source-reading coverage, repeated citation counts,
exact article/block provenance and unique article/ordinal identities. The resulting
JSON includes **all** original R54 action and per-action source rows, plus linked
queues for:

* 237 same-block-uncited work orders (full original excerpt and action identity).
* Exact-URL groups carrying multiple source-identity variants or historical
  shared-URL review flags, with every original reading and contributor preserved.
* Original fallback source-reading work orders, without silently attributing
  or collapsing source scope.
* All 25 historical machine-access IDs, including those not used by the high-risk
  action subset. These are **not** current source outage claims.
* All 15 still-OPEN safety exceptions, **without inventing article-specific
  incident-to-claim locations**; that qualified mapping remains a human task.

The action-subset shared-URL and fallback queues are deliberately **not
represented as exhaustive closure** of the original corpus-wide 30 shared-URL
groups and 43 fallbacks. That larger source-crosswalk review remains open.

All release, source-verification, hazard/medical approval and QD flags are
hard-coded FALSE. The SHA-256 fingerprint detects transit mutations; it
does not authenticate a reviewer or establish a trusted safety decision.

## Reproduce from exact checked-out branch

```bash
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I preparedness/tools/r56_unreviewed_action_source_crosswalk.py --summary
python -I -m unittest discover -s preparedness/tests -v
```

Default execution only reports a limited, unverified machine summary and creates
no files. Optional `--write-private` creates a new fingerprinted directory
**only** in the already-present ignored `preparedness/build/` folder and
writes `UNVERIFIED_ACTION_SOURCE_CROSSWALK.json`; existing directories are
never replaced. Never upload these review dossiers to public WordPress.

Run the repository's complete 13 private engineering stages and native tests on
the **final exact PR head**; no hosted green result should be claimed before
the run has completed. A trusted, independent source and qualified hazard review
remains mandatory before publication.

## Exact branch coordination at the start of R56

* R55 parent: `05ee322283e2a2f326304b91a899d81eb347ba18` (draft #516).
* Default main: `77a87635eb613ce6de268aee11350fa8242efa0f`.
* Seven original Claude contributor heads, freshly checked:
  * Start: `2122d856fce9f64887c16df3d52e64be9f59a55b`.
  * Shelter: `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`.
  * Health: `d2212d0ca0750817d3929865d3069835980faf20`.
  * Food: `4b009361277ea1d4617b368f5d45104c7318b284`.
  * Historical food: `2acf65ca3efa9b4b5db7976f379b9ea693be43a4`.
  * Historical home: `f654e600f89c321a480dd8f055be4d13d0673490`.
  * Historical field: `a5ce8a62f168db05c95232e3eb385dccd0d19e7f`.
* Independent QA #157: `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`,
  draft, not merged. Its five-path Start Here wording/taxonomy/test delta
  must be compared to later integrated safety advice, not blindly cherry-picked.
* Synthetic food fixtures #169: `e9cd7766dac59d47ab467d8945269b9146c2aef5`,
  draft, not merged. Its single test-file delta must likewise not overwrite
  later isolated tests.
* New shelter continuation #521:
  `ac8625faf30dd5538fadc31e06cb5a2cea1defae`,
  43 changed files on original shelter branch, with consequential high-rise,
  generator, stranded-vehicle and family guidance; preserve as separate
  **unreviewed** source/claim work; conflicts with later integrated articles
  require full safety-reviewed three-way reconciliation.
* R48 preview mobile fix #483 current `23544eaeee5354b7943da668409f65d12931370f`
  changes shared CSS and build logic and must not be blindly merged.
* Homepage #49: `10495883299d53596992c26a8987f629b2904670`.
  Flagship #254: `8fa6fc52e034f511b96ae526f4a852e1bd76db04`.
  Gutenberg #414: `5b70b26f3d2434a3ae53a39557f0cd5e5ac932d9`.
  All outside this lane; do not touch.

## Outstanding external and editorial blockers

**No human source checks may be inferred from machine source retrieval.**
The previously documented 206 direct source-link review tasks, 30 corpus-wide
shared-URL groups, 43 fallbacks, 15 open safety incidents, 25 historical
accessibility records, exact claim-source context, independent qualified
hazard/medical safety review, actual WordPress/browser accessibility, and
final exact-commit independent QD remain HOLD items.

A reviewer CSV note and a self-hashed JSON crosswalk cannot satisfy any of them.
No publishing, merging, WordPress writes, navigation edits, or false safety
clearance are authorized by this PR.
