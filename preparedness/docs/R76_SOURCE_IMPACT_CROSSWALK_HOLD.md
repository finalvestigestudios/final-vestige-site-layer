# R76 — Origin-scoped source impact × consequential citation review (PRIVATE DRAFT / HOLD)

**Issue:** #136, Preparedness integration/source-and-safety gate lane only. **Stacked base:** R75 draft PR #658 at `16b6ff1141b56686c0e9db0cde3adc1e637dd524`. **Separate content candidate:** PR #584 at `ddb3528ba6494dada1fa1c3a142ce746e3a67706`; untouched.

## Why this lift matters

R66–R75 preserved the 35 article drafts, six proposed tools, complete 244 origin-scoped research readings, 2,173 citation occurrences and 4,070 DOM blocks while developing lexical, action, quantity and qualifier review queues. However, human reviewers still need a **source-centric map of impact**: if a source proves invalid or is differently scoped, which article and tool passages, including potentially consequential instructions, need re-review? A reused ID can refer to multiple original research readings and a shared URL does not mean the sources can be collapsed.

R76 constructs **one packet per original research identity**, including its exact URL (not normalized or aliased), unabridged research reading SHA, every downstream citation-to-DOM block edge, the document set, both source collision flags, and a count of citations colocated with R75's union of action/quantity review candidates. It also creates an occurrence-level source-variant crosswalk, independently checks every document route and DOM order, preserves even uncited complete readings and unattached citation review tasks, and flags potentially consequential blocks with no same-block citation. The full R75 source/DOM/document/review inventories are carried unabridged; no source identity is silently merged.

The review work order sorts by **number of consequential citation touchpoints** and number of documents citing a source. It is **not a risk score or claim-verification finding**. One citation ID can have several origin-scoped source variant edges; source-variant edge counts must never be mistaken for the number of actual citations. A same-block citation is never proof that it supports the claim.

## Safeguards and limitations

- Four **additive private engineering-only files**: tool, synthetic/adversarial tests, this HOLD document and isolated workflow. No content, source data, taxonomy, public site, CMS, WordPress, navigation or homepage writes.
- The new report is deterministic, SHA-256 sealed, immutable from its input, and explicitly HOLD with `may_publish=false`, independent QD false, qualified safety clearance false and human source link verification false.
- 36+ synthetic/adversarial tests include tampering with source readings and historic notes, source IDs, URLs, citations, source variants, blocks, document routes, reviewer queue, false permissions and missing records.
- Reviewer CSV is one-way and escaped against spreadsheet formulas; no approval importer or hidden publishing switch.
- This is static code/data analysis. **No human source/claim checks, medical or emergency-safety endorsements, real WordPress/browser/screen-reader testing, independent QD approval or publishing authorization** is conferred.

## Verified current coordination snapshot (2026-11-02; before R76 implementation)

| Lane | Exact current head |
|---|---|
| Start | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| Shelter | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| Food | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| Health | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| Historical food | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| Historical home | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |
| Historical field | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |
| RC PR #584 (DRAFT) | `ddb3528ba6494dada1fa1c3a142ce746e3a67706` |
| QA PR #157 (DRAFT) | `7d1ae6b8ef93d10cfb6810987672360885e9c1aa` |
| Fixture PR #169 (DRAFT) | `e9cd7766dac59d47ab467d8945269b9146c2aef5` |
| Homepage lead PR #49 | `10495883299d53596992c26a8987f629b2904670` |
| Experience flagship PR #604 | `71f1f23b9346e40f164bc7bf21ee998ebba2fcb5` |

**Independent QA inspection:** PR #157 addresses unsafe main-breaker drills and refrigerated-medication wording but is not approval or merged. PR #169 isolates its source-upgrade fixture to a temporary copy and uses an in-memory unverified source for another test; its `test_register_fragments_cannot_duplicate_ids` still writes `_dup_test.json` inside the **shared working-tree fragments folder**, preventing a concurrency-safe claim. Both remain separate and unmerged. The homepage and flagship lanes were inspected for head SHA only and left untouched.

## Reproducible exact-branch run

```bash
python -I -m unittest discover -s preparedness/tests -p test_r76_source_impact_crosswalk.py -v
python -I preparedness/tools/r76_source_impact_crosswalk.py
python -I preparedness/tools/r76_source_impact_crosswalk.py --private-review-csv-stdout > /tmp/r76-private-review.csv
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

A hosted private-only workflow must independently verify the exact fixed R75 base, all eight contributor/RC refs, exact add-only scope, corpus census, unmodified original sources and document bodies, all 36+ adversarial tests, native validator/build and complete Python suite. Do not claim a passing test before observing its actual execution.

## Mandatory publication HOLD

The historical mandatory 13-stage integrity job still **fails closed at `seven_cluster_git_parity`**; five historical contributor branches diverge from the frozen provenance baseline. Outstanding: human source-link checks (original 206 obligations; candidate 0 of 244), 30 original / 32 candidate shared-URL groups, 43 fallback relationships, 15 safety exceptions, 22 release-candidate editorial decisions, qualified review of consequential food/water/CO/fire/medical content, real WordPress/browser/print/assistive QA and independent QD. Neither this work nor machine diagnostics relaxes any gate.

**No merge, publish, menu/navigation/CMS/WordPress write, medical safety claim or false QD PASS.**
