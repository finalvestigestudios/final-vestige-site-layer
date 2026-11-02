# R75 — Exact literal qualifier scope × citation custody (PRIVATE DRAFT, RELEASE HOLD)

**Owner:** Issue #136, Preparedness Archive integration and safety-gate lane ONLY.
**Base:** R74 draft PR #651 at 33ef31ecfb9bf992eb6e265b45e3e938f178fc3f.
**Separate content release candidate:** PR #584 at ddb3528ba6494dada1fa1c3a142ce746e3a67706 (read-only).
**Change restriction:** four additive, private engineering-only files. Absolutely no edits to article, tool, source, taxonomy, publishing, navigation, homepage, CMS, or WordPress content.

## Substantive engineering lift

Prior drafts preserved all content and distinguished 975 lexically actionable blocks from 272 blocks containing literal values plus units. Neither screen can decide if a medical, food, water, fire, carbon-monoxide, evacuation, or other emergency recommendation is correct. A further high-consequence failure mode is **loss or displacement of a warning/condition**, even when the citation marker remains unchanged.

R75 therefore examines **every one of the 4,070 unabridged proposed article/tool DOM text blocks**, not just the action or quantity queue. It records exact Unicode offsets for visible literal **prohibitions** ("do not", "never"), **exceptions** ("unless", "only if"), **conditions** ("if", "before", "when"), **authority referrals**, and **uncertainty language**. Overlapping literal matches are resolved deterministically by preserving the longest span at a given start. No semantic safety inference, warning adequacy judgment, source verification or natural-language understanding is claimed.

For human review, it forms the **set union** of all pre-existing R73 action-language packets and R74 quantity packets. Each resulting work order includes the entire original DOM block, all directly associated citation/source identity variants, literal qualifier spans, and full text plus exact R72 custody hashes of the immediately preceding and following blocks **inside the same document**. Neighboring warnings are navigation hints, **not** safety disclaimers that automatically qualify a different instruction. A missing same-block lexical cue is a review routing flag, **not** a confirmed unsafe instruction. An identified cue is similarly not evidence of safety.

All 244 distinct complete source readings (including historical versions and uncited records), all 2,173 candidate citation occurrences, all 4,070 exact DOM blocks, all 41 unique draft document paths and their reading order, all 975 previous action packets, all 272 quantity-bearing packets, 32 proposed shared-URL groups, 15 repeated source-ID groups, all duplicate URL/source origin distinctions, all source reading SHA bindings, and original HOLD states must remain intact. The earlier 35+1 archived baseline with 1,959 citations is not silently treated as if identical to the 35+6 release candidate.

R75 additionally recomputes shared-URL groups, reused source-ID groups, uncited source identities, every document's directly used source variant set, and reverse source-to-citation impact edges from the sealed complete source-and-block graph. The recalculated inventories must be exactly equal to the historical R72/R74 preserved lists, including the pending human scope-review flags. This catches a maliciously resealed parent that quietly drops a duplicate URL, rewrites a collision, reorders origin variants or silently erases an uncited original source.

CSV exports are **one-way, private, spreadsheet-formula-neutralized reviewer aids**; there is no CSV approval importer. The schema is sealed and explicitly keeps human claim/source review, qualified safety review, independent QD and publication permissions unresolved/false.

## Scope and QA coordination — November 2, 2026

- Seven contributor refs: Start 2122d856fce9f64887c16df3d52e64be9f59a55b; Shelter 5daeaf2dd5ab71806a6b73c91edfb1d8df5da976; Food f911ff7a655de8d81535ea86ec3d65a49ee76648; Health d5ef5bafd68361434dd1cc9209915b8e8a4eaf17; Historical Food 67e116e536c7410bed30f8f3b1bb8c166f3c223d; Historical Home 7504a5f099594d635e3dd7332a33a2e1346c43a2; Historical Field 4e5caf812727953aa45e3bda2d382f2c67b6a09c.
- Separate original release candidate: PR #584 ddb3528ba6494dada1fa1c3a142ce746e3a67706.
- Independent safety-QA PR #157: 7d1ae6b8ef93d10cfb6810987672360885e9c1aa (separate draft, unmerged). Reviewed exact source changes to breaker-drill safety, refrigerated medication caveat, Red Cross source classification and publishing-gate tests; no endorsement of medical guidance.
- Synthetic fixture PR #169: e9cd7766dac59d47ab467d8945269b9146c2aef5 (separate draft, unmerged). The source-upgrade test now uses a temporary cloned sandbox, but the duplicate-ID fragment test still writes temporary files into the shared source-fragment directory. Isolate remaining test before asserting shared-runner concurrency safety.
- Homepage lead PR #49: 10495883299d53596992c26a8987f629b2904670. Experience flagship PR #604: 5f87f1b0a48ed2f17ecca49a60c44a482ca530de. Both checked read-only and not modified.

## Execution — private, never publication

    python -I -m unittest discover -s preparedness/tests -p test_r75_qualifier_scope_citation_custody.py -v
    python -I preparedness/tools/r75_qualifier_scope_citation_custody.py
    python -I preparedness/tools/r75_qualifier_scope_citation_custody.py --private-review-csv-stdout > /tmp/r75-private-review-worklist.csv
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

Hosted workflow must additionally prove exact four-file scope, fixed R74 base, seven contributor SHAs, separate RC SHA, syntax and synthetic/adversarial regression. **Never report a passing test until a real local or runner result is observed.**

## Mandatory release HOLD

Full 13-stage release integrity still fails closed at historic seven_cluster_git_parity due to five contributor histories diverging from frozen historical baselines. Outstanding work includes 206 original human-source-link obligations, zero human checks on 244 proposed source readings, 30 original/32 proposed shared-URL groups, 43 fallback relationships, 15 safety exceptions, 22 content release-candidate decisions, qualified review of consequential emergency guidance, WordPress/browser/print/screen-reader QA, and independent QD on the exact release candidate. Machine lexical checks do not provide medically safe instructions or human approval.

**Never merge or publish this work.** No public publishing, navigation/CMS/WordPress changes, original source/HTML changes, false QD PASS, or silent approval of historical advice.
