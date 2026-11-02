# R60 — Frozen contributor drift evidence docket (PRIVATE HOLD)

**Scope:** Issue #136 / Preparedness integration and source/citation safety gates only.
**Parent:** R59 draft head 240cf82a102831dd377b000a3c7b5abb37ee316f.
**Disposition:** NOT MERGED. NOT PUBLISHED. No WordPress, CMS, navigation, homepage, or live-site write. No R14 manifest/source/article change.

## The blocker R60 addresses

The mandatory R15 seven_cluster_git_parity gate halted the R59 pipeline because historical contributor branch refs no longer matched the frozen seven-contributor research baseline. That gate MUST NOT be relaxed, silently rebaselined, or converted into QD/safety approval. R60 supplies a **separate read-only discrepancy docket** that can run even while R15 appropriately fails closed.

R60 first pins the unchanged original R14 manifest Git blob (83263d772fe19fb04d21387a8d051797cc6493c0) and invokes the original R15 checker against the **frozen original Git object trees**, including its one unresolved Start Here metadata exception. It does not substitute the changed contributor refs in that frozen check. It independently reads observed remote-tracking refs and compares the original 72 scoped paths and complete changed-file list to actual Git bytes.

For each changed Preparedness path the docket retains old/new Git blob IDs and SHA-256 hashes, detects line-ending-only changes without dismissing substantive differences, and identifies **unreviewed** citation token changes, source IDs, source-use changes, and metadata safety/publication-state changes. Newly added/deleted Preparedness files are surfaced. Changed frozen paths omitted from the independently generated diff list cause a hard error.

## Fresh GitHub-API investigation (2026-11-01 Pacific)

| Cluster | Observed exact SHA | Frozen R14 SHA | State |
| --- | --- | --- | --- |
| start | 2122d856fce9f64887c16df3d52e64be9f59a55b | same | retained |
| shelter | 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976 | same | retained |
| food | 4b009361277ea1d4617b368f5d45104c7318b284 | same | retained |
| health | d2212d0ca0750817d3929865d3069835980faf20 | same | retained |
| hist-food | 67e116e536c7410bed30f8f3b1bb8c166f3c223d | 2acf65ca3efa9b4b5db7976f379b9ea693be43a4 | **DRIFT: 7 paths** |
| hist-home | a975dbae171251f3585b86d1a5d5a273a231b41c | f654e600f89c321a480dd8f055be4d13d0673490 | **DRIFT: 4 paths** |
| hist-field | a5ce8a62f168db05c95232e3eb385dccd0d19e7f | same | retained |

Both moved branches are one commit ahead of frozen, zero behind. GitHub compare plus old/new file reads found **11 changed paths**. All remained different after CRLF-to-LF normalization; several food files also gained CRLF endings, so Git's raw line counts were misleading.

### Historical food: source identity retargeting requiring human review

The seven changed files include article bodies and metadata for pemmican-and-dried-meats and pioneer-travel-rations, CLUSTER-hist-food.md, hist-food.json, and test_preparedness.py.

- Source ID hist-food-nchfp-jerky was replaced with nchfp-jerky; source URL and reading notes changed too. A material research-provenance change.
- Pemmican retargets **seven** citation occurrences and pioneer rations retargets **one**, with corresponding article source_use key changes. None of these eight citations inherits factual or human-source clearance.
- The contributor's test now uses a synthetic placeholder rather than the original production jerky ID. Independently compare draft PR #169 before accepting the fixture design.

### Historical home: catalogue record does not equal primary-text reading

The branch adds source ID hist-home-wellcome-chadwick-1842 (27 to 28 contributor source records), one citation to sanitation-before-germ-theory (47 to 48 in the affected body), and corresponding metadata and cluster documentation. The source reading notes explicitly distinguish the **Wellcome catalogue** from the **unread 546-image Chadwick report**; human_link_check remains false. Do not promote catalogue metadata into full-book claim support.

The inspected article publication and safety-review statuses did not advance. This is not a qualified hazard review. Both old and new files require independent content examination before any authoring/source change acceptance; R60 changes none of them.

## Commands and trust limits

On a trusted Git checkout with all seven contributor remote-tracking refs fetched, from repo root:

    python -I preparedness/tools/r60_contributor_provenance_drift_docket.py --summary
    python -I preparedness/tools/r60_contributor_provenance_drift_docket.py
    python -I -m unittest discover -s preparedness/tests -p 'test_r60_contributor_provenance_drift_docket.py' -v
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

The R60 CLI writes **nothing**; full JSON is emitted to stdout for private custody. Original frozen objects and all seven refs must be available or execution fails closed. Remote-tracking refs reflect checkout fetch time; compare SHAs to a freshly authenticated branch listing before calling the docket current.

A successful R60 discrepancy report **does not make the mandatory R15 parity check pass**. The R15 gate must remain red until independent provenance adjudication. Do not invent an R60 hosted test count if the workflow fails early. Locally runnable R60 synthetic tests do not replace full archive integration validation.

## Independent QA / homepage coordination

- Safety QA PR #157: 7d1ae6b8ef93d10cfb6810987672360885e9c1aa (draft, unmerged).
- Food synthetic fixture PR #169: e9cd7766dac59d47ab467d8945269b9146c2aef5 (draft, unmerged).
- Shelter continuation PR #521: ac8625faf30dd5538fadc31e06cb5a2cea1defae (draft, unmerged).
- Homepage PR #49: 10495883299d53596992c26a8987f629b2904670 (open). Flagship draft #254: 8fa6fc52e034f511b96ae526f4a852e1bd76db04. Gutenberg draft #414: 5b70b26f3d2434a3ae53a39557f0cd5e5ac932d9. All untouched.

## Strict release HOLD

The 35-article/one-water-tool frozen integration and its 1,959 original citation tasks remain intact. Outstanding: **0/206** independently completed direct source-link checks; 30 shared-URL groups, 43 fallback relationships, 15 safety exceptions, consequential water/food/fire/CO/medical/infant/evacuation advice reviews, actual WordPress/browser QA, and independent exact-head QD approval.

**Never** treat historical source authenticity as present-day medical/emergency safety approval. No publication, WordPress/CMS/navigation writes, source rebaseline, production merges, or fabricated QD PASS.
