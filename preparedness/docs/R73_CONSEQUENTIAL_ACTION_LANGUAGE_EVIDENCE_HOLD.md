# R73 — Consequential-action wording and exact-evidence review docket (PRIVATE HOLD)

**Issue:** #136. **Isolated parent:** draft R72 PR #638 at `e614894a99dfeeebb2b2d723e1d5816625e80da5`. **Separate release-candidate branch:** draft PR #584 at `ddb3528ba6494dada1fa1c3a142ce746e3a67706`. **Scope:** four additive engineering-only files; no original article, tool, source-register, frozen snapshot, public site or WordPress changes.

## Why this is a distinct review gate

The R69–R72 custody system answers *where is a source cited, to which distinct reading, and in which intact HTML text block?* It does **not** answer *which passages tell readers to act*. Instructions about water treatment, food handling, medicine, fire, generators, or evacuation can be consequential even if an adjacent footnote appears, and even if the author includes a caution.

R73 identifies a **private, non-evaluative review queue** of topical text blocks containing directional language or operational quantities. Its classification is a crude lexical signal, with false positives and false negatives, **not** an unsafe/safe finding, verified procedure, recommended treatment, dosage, or publishing decision. A disclaimer or limiting phrase is captured as context, never as proof of safety.

R73 derives its input from the **exact sealed R72** source-scope/citation-impact docket. It preserves the complete R72 evidence, rather than trimming readings to snippets:

* The complete original 35-article and one-water-tool evidence remain frozen upstream (**1,959** citation occurrences; the original article subset contributes 1,952 and original water tool seven).
* The **separate proposed** release candidate has 35 article drafts, six tool drafts, 244 unabridged origin-scoped source records, 2,173 citation occurrences, and 4,070 distinct HTML DOM text blocks. These are not directly comparable as a simple citation delta.
* R73 carries every candidate source reading (including uncited records), every intact block, each document block order, original URL/ID collision dockets, and any unattached citation records. Source `(origin,id)` identities and exact URLs remain separate even when values match.
* For every potentially consequential action-wording block, R73 creates a reviewer packet with the **unabridged original block text**, exact block and Unicode-text hashes, original R72 task hash, source variants' unabridged reading SHA and URLs, citation ordinals, and adjacent citation navigation hints. All human claim/support, qualified safety, and QD states remain `NOT_REVIEWED`.
* The private CSV is text-complete and defends against spreadsheet formula prefixes, including Unicode invisibles. It is a **worklist export only**: there is deliberately no approval importer, no claims of live URL verification, and no automation that can promote human or QD status.

Every output is SHA-sealed and reproducible. The validator fails closed on missing/duplicated article or tool routes, missing or reordered DOM blocks, source reading truncation, source SHA/URL drift, source variant aliasing, dropped citation edges, forged review status, missing shared-URL/reused-ID collision groups, unexpected uncited source changes, and count mismatch. Mutation tests re-seal their synthetic parent envelopes, so the rejections are not trivial checksum failures.

## Reviewer process / release blocker hierarchy

1. **Human source verifier:** independently open exact source URLs and assess source availability/date, reading depth, relevant passage, scope, and citation placement. Shared URLs and reused source IDs get explicit separate decisions—never auto-merged.
2. **Qualified domain reviewer:** assess actionable water, medicine, food, generator, fire and emergency guidance in full context. Lexical cues only prioritize human attention; both cited and uncited action language remain pending.
3. **Editorial/founder:** decide among changed research versions and draft content after source and qualified reviews. Never overwrite frozen baseline or silently apply seven-branch later changes.
4. **Independent QD:** review the exact assembled publish candidate, actual WordPress/Assembler frontend, keyboard, responsive, print/offline and assistive-tech states; only then can release decisions be considered. A green machine test cannot replace this step.

**Mandatory integrity remains FAILED CLOSED** at `seven_cluster_git_parity`, given five contributors historically diverged from their frozen baselines. The separate full 13-stage pipeline is **not green**. Outstanding previously tracked obligations include 206 original human source-link checks, zero human checks on 244 candidate readings, 30 original/32 candidate shared-URL groups, 43 original fallback relationships, 15 unresolved safety exceptions, 22 release-candidate decisions, production browser/WordPress QA and independent QD. R73 does not clear any of these.

## Commands on exact branch (local or hosted; no network needed for scripts)

```sh
python -I -m unittest discover -s preparedness/tests -p test_r73_consequential_language_review.py -v
python -I preparedness/tools/r73_consequential_language_review.py
python -I preparedness/tools/r73_consequential_language_review.py --triage-csv-stdout > /private/r73-consequential-action-review.csv
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

**No public publishing, navigation, CMS/WordPress writes, merges, retroactive rebaseline, false QD PASS, or claim that unreviewed emergency/medical guidance is safe.**

## Read-only coordination checked 2026-11-02

Seven Claude contribution heads each matched its pinned 40-character ref (ahead/behind 0, identical): Start `2122d856fce9f64887c16df3d52e64be9f59a55b`; Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`; Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`; Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`; Historical Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`; Historical Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`; Historical Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`. RC #584 at `ddb3528ba6494dada1fa1c3a142ce746e3a67706` matched exactly.

Independent safety QA **draft PR #157** at `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` was inspected: it proposes safer non-breaker drill language, product-specific medicine handling, safety-gated Start Here taxonomy, correct Red Cross nonprofit classification, and negative publication tests; it remains **unmerged** and does not establish medical clearance. Synthetic food fixture **draft PR #169** at `e9cd7766dac59d47ab467d8945269b9146c2aef5` isolates test mutations in a temporary research copy and uses unverified synthetic source IDs; it remains **unmerged**, not source approval. Home #49 at `10495883299d53596992c26a8987f629b2904670` and flagship #604 at `5f87f1b0a48ed2f17ecca49a60c44a482ca530de` were checked and left untouched. Re-check every ref on each run.
