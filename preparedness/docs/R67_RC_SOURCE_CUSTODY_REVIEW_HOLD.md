# R67 — Original 224 vs release candidate 244: exact source custody HOLD

**Scope:** Issue #136 only. **Parent:** private R66 PR #593, exact head
`646c89531811bb7bc430ef115f857ff5e36bdc5c`.
**Read-only comparison target:** independent release candidate PR #584,
exact commit `ddb3528ba6494dada1fa1c3a142ce746e3a67706`.
Neither PR is merged. All 35 original articles and the separate water planner
remain in private, non-published draft custody. No public navigation or CMS calls.

## A. Why the numbers do not agree

Different source-census units have been incorrectly easy to conflate:

| Dataset and scope | Count | Meaning | Human approved? |
| --- | ---: | --- | --- |
| Historical issue work orders | 206 | Previously tracked human URL/link-check queue | No; 0 completed |
| Frozen original source rows | **224** | 34 base register records plus 190 records from seven contributor fragments | No; 0/224 human_link_check |
| Frozen exact source URLs | **186** | Exact raw strings, not normalized | No |
| Frozen shared-URL clusters | **30** | Multiple distinct source identities may share one URL; evidence never auto-aliased | No |
| R66 *cited-original* source identities | **208** | Original cited (origin,id) identities only, NOT all research | No |
| Original citation occurrences | **1,959** | 1,952 citations from 35 original articles plus 7 from one original water planner | No |
| Release candidate source rows | **244** | 34 base plus 210 contributor-fragment records; the candidate adds five draft tools | No; 0/244 human_link_check |
| Candidate exact URL strings | **202** | Exact raw URL strings, not equivalent-source groups | No |
| Candidate shared-URL clusters | **32** | Every variant retains its independent research notes and dates | No |
| Candidate machine-accessibility probes | **97** | 88 machine-readable, 9 machine-unreadable, entirely separate from the 244-record universe | **Not human checks** |
| Candidate article/tool readiness register | 41 | 35 articles + six tools in an independent draft RC | No qualified safety approval |

R67's read-only Git-object comparison identifies **20 added source records,
two modified original source readings, zero deletions and 222 unchanged
source records**. The two modified originals are
`hist-field:loc-prairie-traveler` and
`hist-home:hist-home-loc-simmons-1796`.
Their exact original and proposed full source records, URL strings and
field-by-field changes are preserved in distinct review orders. In particular,
a stronger claim to have read a digitized source cannot silently replace
a catalogue/OCR-limited historical reading; different notes require independent
human verification. All 20 additions remain unreviewed.

The candidate contains an additional `shelter:fsis-power-failure`
source identity at an existing URL. It is not merged with the separately
recorded food-cluster reading, and no source-ID collision receives automatic
approval. The RC validator currently **fails closed** against its frozen
crosswalk and article-evidence locks; this R67 audit does not correct or bypass
the underlying RC failure.

## B. Deterministic, isolated gate

The proposed `preparedness/tools/r67_rc_source_custody_crosswalk.py`
requires exact original R66 ancestry and exact RC ref SHA. It independently
regenerates R66's original citation ledger from Git evidence. For every source
it preserves entire JSON source notes, origin-scoped ID, original URL, verified_on
research metadata and human_link_check=false. Every R66 cited source must
match the frozen raw source record including origin and all fields. In addition
all 1,959 original citation contexts remain under the R66 fingerprint.

It reads the candidate's eight JSON source files directly from the pinned RC
Git commit, **never checking out or modifying the candidate's source tree**.
It reads the RC's 97-item machine accessibility artifact as machine evidence
only. That QA artifact is NOT a substitute for a human click or claim-support
review: a 200/OK status proves neither content accuracy nor safety, and a
failed machine request does not independently prove a human cannot open a URL.

A deterministic source work order records both complete source versions,
their individual SHA-256 fingerprints, every cited-original evidence object
where applicable, per-version exact URL-sharing cohorts, optional unchanged
machine-probe evidence and OPEN review states. Changes in source fields,
missing rows, changed contributor SHA, mismatched citation records, fake
human reviews, modified release controls or unexpected census values fail
closed. No URL canonicalization, automatic source aliasing or approved-state
imports are allowed.

Run from the repo checkout with Git refs fetched:

```sh
python -I preparedness/tools/r67_rc_source_custody_crosswalk.py
python -I preparedness/tools/r67_rc_source_custody_crosswalk.py --task-csv-stdout > /private/review/R67-source-delta.csv
python -I -m unittest discover -s preparedness/tests -p 'test_r67_rc_source_custody_crosswalk.py' -v
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

The CSV is a formula-neutralized **private reviewer task projection**, never
a secure import or an approval ledger. Never publish the CSV or full evidence
packet. Saving it privately does not mean the underlying links were visited.

## C. Independent lane inspection and HOLD

- Independent safety QA PR #157:
  `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`.
  Reviewed its changes to power-drill wording, medication caveats, Red Cross
  nonprofit classification, taxonomy safety gates and negative tests.
  Remains isolated, unmerged, not safety-approved.
- Synthetic food-fixture PR #169:
  `e9cd7766dac59d47ab467d8945269b9146c2aef5`.
  Reviewed the actual test patch: new temp-copy fixture prevents working-tree
  source edits. Remains separate, unmerged and not QD-cleared.
- Separate release candidate PR #584:
  `ddb3528ba6494dada1fa1c3a142ce746e3a67706`.
  Its machine QA and link-count inventory are independently scoped; do not
  incorporate it into the original frozen baseline without decisions X-1
  through X-5 and qualified source/safety review.
- Homepage lead PR #49:
  `10495883299d53596992c26a8987f629b2904670`.
  Entirely untouched. Verify its live SHA and the current flagship homepage
  work before any future integration decisions.

The separate mandatory 13-stage private integrity still **FAILS CLOSED**
at `seven_cluster_git_parity` because five original contributor
branches advanced. R67 does not rebaseline those branches, edit frozen
crosswalks, merge, publish, or write to WordPress. Remaining blockers:
206 earlier human-link tasks (reconcile scope, do not assume 244 replace them),
human inspection of all consequential advice and source-reading depth, the
30 original/32 RC shared URL groups, original 43 fallback relationships,
15 unresolved safety exceptions, real browser/assistive technology QA,
independent QD of an authorized exact head and explicit founder release approval.

**RELEASE HOLD — no claims of medically safe or independently verified advice.**
