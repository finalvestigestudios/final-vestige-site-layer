# R83 — Citation placement and claim-context custody (PRIVATE / HARD HOLD)

**Issue:** #136. **Exact immutable parent:** R82 draft PR #701, commit 33012631e9711168cd2e73edc4992e123f26c664. **Separate untouched candidate:** PR #584 at ddb3528ba6494dada1fa1c3a142ce746e3a67706. Additive review-only engineering, not a live release.

## Motivation / safety boundary

R82 identified contributor-authored article wording changes with unchanged citation sequences. Merely retaining the same citation ID does NOT establish that a changed paragraph is supported by its original source. R83 records *where* each literal citation appears inside its nearest semantic text container (paragraph, list item, table cell, heading, blockquote, caption, etc.), alongside complete nearby container text and preceding section heading. For each recurring literal source ID, it compares the ordinal occurrence of that ID between the exact current Claude contributor and separate RC. Review cues identify changed container text, headings, ordinal, byte offset, scoped source variant, or added/removed citation. Lexical cues are NOT proof of source support, contradiction, unsafe advice, or safe medical procedure.

HTML text parsing is conservative: citations in attributes, comments, scripts, styles and templates, and citations without a recognized semantic container, receive UNMAPPED_OR_NONVISIBLE_REVIEW; they are never certified as claim-supported. Original R82 UTF-8 byte positions are verified before assignment. Unabridged nearby context and distinct source-origin candidate readings remain separate. Same URL or raw ID NEVER silently aliases two readings. No external link/claim verification, editorial decision, medical judgment or human safety approval occurs.

**Scope:** seven original Claude contributor branches; 29 specifically contributor-authored articles; four historical snapshots each (116 article HTML+metadata histories); all complete R82 source fragment histories. R83 validates and pins the complete R82 seal, reconstructs all occurrence-level review records and verifies a private digest. This does NOT replace R80 full archive: 35 articles, six draft tools, 244 complete source readings, 2,173 literal citations, 2,359 source-origin variants, 4,070 text blocks and 347 separate consequential uncited review orders. Never misrepresent 29 as the complete 35-article slate.

## Trusted exact-checkout commands

Requires Python 3.12, full Git history and pinned seven contributor/RC refs.

    python -I preparedness/tools/r83_citation_placement_context_custody.py
    python -I preparedness/tools/r83_citation_placement_context_custody.py --csv-stdout > /tmp/R83-PRIVATE-NOT-APPROVED.csv
    python -I -m unittest discover -s preparedness/tests -p test_r83_citation_placement_context_custody.py -v
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

Delete the temporary private CSV after review. Never upload private reviewer materials publicly. The dedicated workflow enforces exact immutable R82 parent, precisely four ADD-only scoped files, reconstructs four snapshots, runs tests, native validator, offline build and the complete Python suite. No merge, publication, navigation, CMS or WordPress writes. Human source/claim/qualified-safety/QD approvals remain zero; may_publish remains false.

## Independent QA / coordination (verified read-only refs)

- QA PR #157 SHA 7d1ae6b8ef93d10cfb6810987672360885e9c1aa remains draft, unmerged. Do not blindly cherry-pick older medication/drill wording over later RC content.
- Food fixture PR #169 SHA e9cd7766dac59d47ab467d8945269b9146c2aef5 remains draft, unmerged. The upgraded fixture now uses an isolated temporary data tree; the unchanged duplicate-ID test still writes a temporary _dup_test.json under the shared working tree, a concurrency risk for its owner to address.
- Homepage PR #49 SHA 10495883299d53596992c26a8987f629b2904670 and flagship PR #604 SHA bdf01b4a3e13fd6179ae9e847c9d4429bbe16176 are outside this lane, checked read-only and untouched.
- Seven exact contributor heads and separate RC pin are independently verified by inherited R81/R82 Git provenance at runtime.

## Mandatory safety + release gates: HARD HOLD

R82 standalone hosted diagnostics on its own exact head previously passed 6,709 Python tests, native validation and offline build. Its separate mandatory pipeline FAILED at the native_unit_suite 180-second time budget (full suite 195.205 seconds); five historical contributor parity differences are independently documented and remain unresolved. The full mandatory 13-stage release-integrity pipeline has NOT passed. No waiving/parity rebaseline/QD PASS/medical-safety approval/publishing.

Human review remains required for 15 safety exceptions, 22 RC editorial decisions, shared-URL and source-identity conflicts, claim-to-source URL review, qualified emergency/health/food/water instruction review, actual WordPress/browser accessibility tests, independent QD and founder release authorization. Historical accuracy does NOT prove modern safety.

**R83 state:** PRIVATE DRAFT / HARD HOLD. Do not claim exact-head test success before actual diagnostic workflow results are examined.
