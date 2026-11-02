# R68 — Release candidate document → citation → reading scope HOLD

**Issue:** #136. **Exact source parent:** R67 draft PR #606 at SHA
e9a7da397845f289336ba08bde1bee99ee9d8b9e.
**Independent RC input (read-only):** PR #584 at SHA
ddb3528ba6494dada1fa1c3a142ce746e3a67706.
All files are private source-review engineering, not WordPress output.
**RELEASE = HOLD. No CMS, navigation, publication or production merge.**

## What R67 proved, and the hole R68 closes

R67 structurally conserves original 224 full research records versus 244
candidate records, preserving both full readings (20 added, two changed,
no removed). R66 carries the original **35 articles and one original
water-planning tool with 1,959 separate citation occurrences**. Those are
not claims that the sources have been opened by a human or support the
specific emergency guidance.

R68 opens the pinned independent release candidate at its exact Git commit,
without cherry-picking it into the frozen archive, and traces **every
candidate document** to its precise citation tokens and separate
source-reading variants. The input set is the RC's **35 article drafts and
six browser-local tool drafts**, each metadata file paired with unabridged
HTML. It preserves original and proposed bodies side by side.

For each of the 41 items, the report retains:

- Complete unabridged RC HTML and metadata, SHA-256 body fingerprint,
  proposed **draft-only** WordPress URL and original R66 document evidence,
  where available. Unchanged HTML validates structural identity only.
- Every ordered citation with Unicode character offset, source ID,
  exact token and source-adjacent context, never a claim-support verdict.
- Every explicit source-use metadata entry, including **uncited** readings.
  These notes remain even when no citation token is present.
- All matching candidate **(source_origin, source_id)** variants and
  their complete R67 source readings. Duplicate IDs and duplicate exact
  URLs stay separate. The frozen article-origin map gives only candidate
  scope, not endorsement. New tools without a mapping are flagged.
- Explicit flags when wording changes despite unchanged citations, one
  ID appears in several fragments, cited IDs lack source-use notes,
  source-use notes lack a citation, or the frozen 224-record crosswalk
  does not include the 244-source candidate.
- Pending human claim, source, qualified safety and independent QD
  states for every document, even where older RC metadata asserts approval.

## Machine-only safety gate

The validator checks both the R66 original ledger and R67 source-custody
packet against fingerprints and mandatory HOLD booleans. It requires
exact R67 and RC commit ancestry and RC remote SHA; reads direct Git
object bytes without mutable candidate checkout; rejects duplicate
document slugs/URLs, published metadata, malformed citation tokens,
missing sources, changed citation order behind identical HTML,
fabricated human approvals and unexpected census values.

The offline report never updates frozen source crosswalks, article locks,
the seven contributor pins, articles, WordPress or navigation. Exact
citation/source matching is not factual verification or medical safety.

Run from a trusted checkout with refs:

    python -I -m unittest discover -s preparedness/tests -p test_r68_rc_document_citation_scope.py -v
    python -I preparedness/tools/r68_rc_document_citation_scope.py
    python -I preparedness/tools/r68_rc_document_citation_scope.py --task-csv-stdout > /private/review/r68-tasks.csv
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

The CSV allocates **review work only** and does not transfer approval
to any research record. All evidence and reviewer notes stay private.

## Coordination and blockers

- Independent safety QA PR #157 at
  7d1ae6b8ef93d10cfb6810987672360885e9c1aa was inspected:
  power-drill wording, refrigerated-medication caveat, Red Cross nonprofit
  taxonomy, Start Here gating and negative tests. It remains unmerged
  and does not independently establish clinical safety.
- Independent synthetic food fixture PR #169 at
  e9cd7766dac59d47ab467d8945269b9146c2aef5 isolates test fixtures
  rather than mutating real sources. Still an unmerged draft.
- Homepage PR #49 at 10495883299d53596992c26a8987f629b2904670
  and flagship #604 at 5f87f1b0a48ed2f17ecca49a60c44a482ca530de
  remain out of scope and untouched.
- Seven contributor refs match R67 exact SHA pins at the start of this
  sprint; five still diverge from frozen historical custody.
- The separate RC #584 remains unmerged and cannot authorize source
  rebaselining, QD PASS or publication.

The separate mandatory 13-stage release integrity is **FAIL CLOSED**
at seven_cluster_git_parity. Passing these isolated diagnostics does
not unblock that safeguard. Still open: human link/claim checks;
30 original/32 candidate shared-URL groups; 43 fallback relationships;
15 safety exceptions; qualified water/food/medicine/fire/CO/evacuation
review; real WordPress/browser/accessibility checks; independent QD;
founder decisions and explicit publication authorization.

**No assertion that older safety labels or machine link probes indicate
independent, qualified approval of emergency guidance.**
