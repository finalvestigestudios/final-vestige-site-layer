# R69 — Private HTML citation placement and claim-block review dossier (RELEASE HOLD)

**Issue:** #136. **Draft engineering parent:** PR #614 / R68 at exact commit \`654094057e3795902a21d73c39fe678414e4fe11\`.
**Independent read-only RC input:** PR #584 at exact commit \`ddb3528ba6494dada1fa1c3a142ce746e3a67706\`.
**No publication authorization, no CMS/nav writes, no merging, no independent QD PASS.**

## Why the new gate exists

A lexical \`{{cite:source-id}}\` count alone cannot tell whether the token
occurs in ordinary HTML text, within a hidden/script/template element, in an
HTML attribute, or in a comment. All four can pass simple source-ID checks;
only some have potential reader-facing attribution. The R68 41-document,
2,173-citation inventory provides a *pinned original evidence baseline*,
not browser-rendering verification.

R69 analyzes every R68 unabridged candidate HTML string with Python's
\`HTMLParser\`, locating citation tokens by **Unicode codepoint offset**
and source ID, and conserves every occurrence even if it is *not* in
an HTML data node. Output classifications deliberately do not assert that
external CSS, JavaScript, accessibility tooling or WordPress has rendered
anything correctly:

- \`DOM_TEXT_POTENTIALLY_VISIBLE_NOT_BROWSER_VERIFIED\`
- \`SUPPRESSED_OR_A11Y_HIDDEN_DOM_TEXT\`
- \`NON_DOM_TEXT_ATTRIBUTE_COMMENT_OR_TOKEN_SPLIT\`

R69 emits immutable, source-fingerprint-bound review orders for every
candidate document (35 original articles + six RC tools), retaining exact
citation order, origin-scoped source-identity variants, complete
candidate semantic-block DOM text, HTML offsets, block IDs,
review-topic triage signals, and the complete R68 evidence fingerprint.
R69 **does not replace or abridge R68's full original/candidate HTML,
historical 29-contributor readings, 224/244 source records, source-use
explanations, 30/32 duplicate-URL groups or 43 fallback relationships**.

A block's lack of a nearby citation is a **review triage marker, not
proof that it lacks support**. A matching citation is not claim support.
Keyword signals for water, food, medicines, CO/fire/generators, and
evacuation are fallible string flags, **not clinical or emergency
safety verdicts**.

## Integrity, release safeguards and verification

- Exact R68 sealed fingerprint, HOLD booleans, document task
  fingerprints, original 1,959 citation count, 244 RC source count,
  2,173 RC citation count and 35+6 candidate document census.
- Rechecks raw RC HTML SHA-256 and every ordered source ID, exact
  citation token and Unicode offset before classifying HTML placement.
- Rejects fabricated human, safety and QD statuses, changed source
  identity evidence, dropped citations, duplicate draft URLs and
  unexpected publication metadata.
- Private reviewer CSV uses formula-injection neutralization. Reviewer
  notes remain **UNTRUSTED** and cannot grant approval or rewrite
  the source evidence.
- No third-party HTTP requests, no source mutation, no files written
  by the tool itself, no WordPress connection, and no navigation changes.

Local isolated checks (in a synthetic \`preparedness/tools\` and
\`preparedness/tests\` directory) passed **74 targeted tests**. Hosted
Linux exact-head native tests and derived count measurements must be
recorded separately; local synthetic testing is not the full suite.

From a trusted exact checkout with source refs available:

    python -I -m unittest discover -s preparedness/tests -p test_r69_rc_citation_dom_review.py -v
    python -I preparedness/tools/r69_rc_citation_dom_review.py
    python -I preparedness/tools/r69_rc_citation_dom_review.py --task-csv-stdout > /private/review/r69-citation-work-orders.csv
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

The CSV is **private**, not a WordPress import feed or a release manifest.

## Coordination and outstanding blockers

- Independent QA PR **#157** remains at
  \`7d1ae6b8ef93d10cfb6810987672360885e9c1aa\`
  (power drill/medicine warning/source taxonomy/negative safety tests).
- Food synthetic-fixture PR **#169** remains at
  \`e9cd7766dac59d47ab467d8945269b9146c2aef5\`
  (isolates source-upgrade and unverified-source tests).
- Homepage lead PR **#49** remains at
  \`10495883299d53596992c26a8987f629b2904670\`,
  and flagship PR **#604** at
  \`5f87f1b0a48ed2f17ecca49a60c44a482ca530de\`.
- Exact seven Claude contributor heads were independently checked at
  the R69 start: start \`2122d856\`, shelter \`5daeaf2d\`,
  food \`f911ff7a\`, health \`d5ef5baf\`,
  hist-food \`67e116e5\`, hist-home \`7504a5f0\`,
  hist-field \`4e5caf81\`; frozen baseline drift remains.
- Mandatory \`seven_cluster_git_parity\` and 13-stage release pipeline
  **remain FAILED CLOSED** on five divergent contributor branches.
  Do not rebaseline research or suppress this gate.

Remaining human review includes link checks (original 206 tracked
requirements; RC 0/244), original 30 / candidate 32 shared URLs,
43 fallbacks, 15 open safety exceptions, 22 unresolved founder/reviewer
decisions, independent claim and qualified guidance review, actual
WordPress-theme + assistive-technology QA and independent QD on exact
publication head. Nothing in R69 grants any of those permissions.

**Release = HOLD. Do not merge, publish, change navigation or CMS, or
claim that emergency/medical guidance was certified safe.**
