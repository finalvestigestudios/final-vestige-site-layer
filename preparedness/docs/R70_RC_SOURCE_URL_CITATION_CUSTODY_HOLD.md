# R70 — Exact source URL trust boundaries and citation/source custody (PRIVATE HOLD)

**Issue:** #136. **Exact engineering parent:** R69 #620 at
\`531af57730c9039857df18d9444e0aaedaa4abda\`. **Independent candidate:**
#584 at \`ddb3528ba6494dada1fa1c3a142ce746e3a67706\`. These are
not publish, editorial, or Qualified Design (QD) approvals.

## Purpose

Previous review stages reconcile 35 original articles + the original water
planner (1,959 citations), seven Claude source branches, and the 35 article +
six tool release candidate (2,173 citation occurrences). R69 classifies where
those 2,173 tokens occur in raw HTML, but a visible citation pointing to the
wrong research identity or an unsafe URL still needs a separate gate.

R70 independently reads and verifies the sealed R67 source-custody report,
R68 complete-document/citation report, and R69 HTML-context report. It
conserves **all 244 unreviewed release-candidate source records**, including
uncited records. It relates each candidate citation occurrence to its exact,
origin-scoped candidate source identities and **all exact URL variants**,
with original source readings preserved in the R67 chain and copied once per
source into this reviewer dossier. URLs are never normalized or deduplicated
into assertions of reading equivalence. No citation becomes human-reviewed by
passing a syntax check.

This gate flags URLs with non-HTTPS structure, userinfo, untrusted local or
private-network hosts, malformed hostnames, unsafe control or markup
characters, and malformed authority, and separately flags redirection
parameters, URL query credentials, fragment deep links, internationalized
hostnames, and literal IPs for **manual review**. These are lexical signals,
not HTTP/redirect checks and not source-quality or factual verdicts. Reviewers
must inspect exact source passages, redirects, stale links, scope and authority
themselves. *A passing source URL syntax gate does not mean a source is
reachable, credible, or supports advice.*

R70 rechecks R67/R68/R69 SHA-256 report fingerprints, immutable document task
fingerprints, all distinct source-reading record hashes, origin+ID variants,
source-use identities, document URLs, ordered citation IDs, Unicode offsets
and HTML visibility classifications. It rejects fabricated human approvals,
changed source IDs/positions, missing documents/citations, and silently
merged shared-URL groups.

## Artifacts, tests and execution

Four additive, review-only files in this PR: this dossier, the Python
validator, synthetic/adversarial tests, and a private GitHub Actions workflow.
No modifications to original articles, source registers, frozen evidence,
crosswalk, contributor branches, homepage, navigation, or CMS.

From the exact branch with all seven source refs and release-candidate ref:

    python -I -m unittest discover -s preparedness/tests -p test_r70_rc_source_url_citation_custody.py -v
    python -I preparedness/tools/r70_rc_source_url_citation_custody.py
    python -I preparedness/tools/r70_rc_source_url_citation_custody.py --source-csv-stdout > /private/r70-source-url-review.csv
    python -I preparedness/tools/r70_rc_source_url_citation_custody.py --citation-csv-stdout > /private/r70-citation-url-review.csv
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v

Derived CSVs remain **private, untrusted, and NOT WordPress import feeds**.
No temporary files are written by the validator itself; both CLI CSV modes
write only to stdout, so the operator decides where private evidence stays.
Spreadsheet-formula prefix sanitization is applied to exported fields.
The tool stops with code 2 on structural source URL blockers, even though it
still emits a reviewer HOLD report for investigation.

## Independent QA and coordination

Current inspected source refs at R70 start:

- PR #157 independent Start Here safety QA:
  \`7d1ae6b8ef93d10cfb6810987672360885e9c1aa\`. Still draft,
  unmerged; power/medicine warnings and human-safety gate changes need review.
- PR #169 isolated synthetic food-source tests:
  \`e9cd7766dac59d47ab467d8945269b9146c2aef5\`. Still draft,
  unmerged; not used as evidence of independent source approval.
- Homepage lead PR #49:
  \`10495883299d53596992c26a8987f629b2904670\`.
- Flagship homepage PR #604:
  \`5f87f1b0a48ed2f17ecca49a60c44a482ca530de\`.
- Seven contributor refs: start \`2122d856\`; shelter \`5daeaf2d\`;
  food \`f911ff7a\`; health \`d5ef5baf\`; hist-food \`67e116e5\`;
  hist-home \`7504a5f0\`; hist-field \`4e5caf81\`.

All other agents' branches remain separate. R70 does not authorize
historical-source rebaselining, acceptance of drifted contributor claims,
or release of the original 35-article slate.

## Release blockers (fail closed)

The mandatory \`seven_cluster_git_parity\` gate remains blocked by five
contributor branches diverging from frozen custody. The complete 13-stage
release-integrity pipeline has not passed. Outstanding requirements include
206 historical human source-link obligations, RC human link checks (0 of
244), original 30/RC 32 shared-URL groups, 43 fallback relationships,
15 open safety exceptions, 22 RC decisions, medical and consequential
emergency-advice review by qualified people, genuine WordPress/browser
accessibility tests, and independent QD approval.

**RELEASE: HOLD.** The engineering diagnostics on this PR establish
only syntactic/provenance properties. No one has published a Preparedness
article, navigated readers to the archive, changed WordPress/CMS,
merged a branch, or declared unreviewed advice medically safe through
this R70 work.
