# R65 — Integrated 35-Article Citation Conservation (PRIVATE / RELEASE HOLD)

**Owner:** Issue #136, Preparedness Archive source/citation safety lane. **Parent:** exact R64 draft head 6d6d7f6c7666f00ff11290581c897662e1843f17 (#579). **Status:** engineering-only review draft, NOT source verification, NOT qualified safety review, NOT independent QD, NOT WordPress publication.

## Purpose

R60–R64 independently preserve the seven original Claude contributor branches, including every source-reading record (cited or uncited) and all article/source-use relationships. R58 separately preserves the complete integrated **35 original articles, one water-planning tool, 1,959 original citation occurrences**, full source readings and link/safety review states.

The contributor family covers **29 frozen original articles** with **1,709 frozen citation tokens**, compared against **1,728 proposed, still-unreviewed tokens**. **Six other integrated articles are outside that original contributor-branch scope.** An article-level reconciliation that silently discards these six or conflates proposed research with the integrated baseline is unacceptable.

R65 adds **one review work order for each of the 35 integrated originals**. It uses the actual old integrated R58 citation work orders and unabridged source records, plus both contributor versions from R61 and complete dependency work orders from R64. Neither all-corpus evidence nor contributor lineage is substituted or rewritten.

## Explicit identity rules

- A contributor token is marked as an exact candidate match **ONLY** when the complete frozen article HTML SHA-256 agrees with the integrated original, its source ID agrees, and its Unicode codepoint token offset agrees. A match is a **structural identity** and **never** establishes that the source supports the statement.
- A matching URL, shared source ID, similar paragraph, fallback reading, or position in an altered article never creates equivalence, approval or an automatic alias.
- Each original cited source is retained in full, with original origin, notes, source URL and citation contexts. Each source-use note and every R64 candidate reading remains separate across contributor identities.
- Original and observed body/metadata/citation differences are flagged without accepting changed advice, source records or safety states.
- Both complete article sets, original six out-of-scope articles and all unpaired frozen tokens remain in the private review dossier. No truncation or deduplication.
- Exact census, original source identity/HTML SHA, unique citation offsets, R64 dependency coverage, complete source-use notes, per-source citation ordinals and pending safety states are mandatory; tampering fails closed.
- A machine-generated SHA fingerprint binds the **review evidence only**. It is not a human signature, independent fact check, permission to publish or clearance for emergency, food, water, medication or medical content.

## Exact production procedure

Only in an exact trusted Git checkout with all seven contributor refs present (no public writes):

    python -I preparedness/tools/r65_integrated_citation_conservation.py
    python -I -m unittest discover -s preparedness/tests -p test_r65_integrated_citation_conservation.py -v
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

The R65 CLI freshly regenerates R58 (from original R25/R54/R56/R57 lineage and frozen source/article inputs) and R61 two-version source inventory from Git objects, then derives R62/R63/R64 and verifies both roots. Emits a private summary to stdout only. No CMS, WordPress, navigation, publishing or public artifact writes. The private CI workflow checks the exact parent, exact four-file scope, contributor SHAs, source conservation, and native tests as **diagnostics**.

## Provenance snapshot: 2026-11-02

Start Here: 2122d856fce9f64887c16df3d52e64be9f59a55b (unchanged)
Shelter: 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976 (unchanged)
Food: f911ff7a655de8d81535ea86ec3d65a49ee76648 (advanced)
Health: d5ef5bafd68361434dd1cc9209915b8e8a4eaf17 (advanced)
Historical Food: 67e116e536c7410bed30f8f3b1bb8c166f3c223d (advanced)
Historical Home: 7504a5f099594d635e3dd7332a33a2e1346c43a2 (advanced)
Historical Field: 4e5caf812727953aa45e3bda2d382f2c67b6a09c (advanced)

Five changed contributor heads, 23 changed Preparedness files and 19 additional proposed citation occurrences remain unreviewed. **Never alter frozen R14 provenance manifest** to silence seven_cluster_git_parity. Mandatory 13-stage machine-integrity pipeline stays FAIL CLOSED independently of diagnostic success.

Independent QA #157 7d1ae6b8ef93d10cfb6810987672360885e9c1aa includes safety-critical household-drill/medication language, Red Cross source taxonomy and safety-gated Start Here tests. Synthetic-fixture QA #169 e9cd7766dac59d47ab467d8945269b9146c2aef5 isolates food-source tests. Both separate unmerged drafts, neither imported. Home lead and other agent workstreams remain untouched.

**Other release blockers:** human source-link checks 0/206 tracked; 30 shared-URL groups; 43 fallback relationships; 15 safety exceptions; qualified review of consequential household/emergency guidance; actual WordPress browser, keyboard, print and screen-reader QA; independent QD; contributor drift review. Original 35 articles and water tool remain **PRIVATE / HOLD**. No independently reviewed source, medical safety, QD PASS or production readiness asserted.

**Changed scope:** exactly R65 tool, adversarial tests, private runbook, pinned CI. Zero original articles/contributor data/URL registries/frozen manifests/WordPress/navigation/homepage/release pipeline changes.
