# Preparedness Archive — multi-review discrepancy audit (DRAFT / HOLD)

**Ownership:** Final Vestige Studios Preparedness Archive integration and source/citation safety gates, Issue [#136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136). This is an **additive, offline, unpublished, read-only safeguard** on top of the immutable reviewer packets (PR #200) and self-reported response intake (PR #207). It never changes articles, source registers, reviewer responses, CMS, subscribers, navigation, or release state.

## Problem this addresses

A single source-review intake only validates one response per citation or shared source group. It does not detect **two separately prepared reviewers disagreeing** about the same source, whether the source redirected, what page they read, whether a claim is supported, or whether safety risks were noticed. Nor did it compare the individual contributor scopes in shared-URL groups against the state of the article-level reviews. It would be unsafe to merge responses, silently overwrite a contradiction, or let a second person's matching report count as professional approval.

`preparedness/tools/review_discrepancy_audit.py` takes one or more separate, structured **self-reported** response files, validates *each* with the prior `review_response_audit.audit`, and derives a deterministic **conflict and missing-review triage**. Its per-request and per-group summary records are bound to the original exact review manifest. The report contains no raw reviewer names, evidence notes, reading limitations, or newly observed redirect destinations.

### Additional source/citation integrity gate

Before considering a response, the tool verifies **cross-structure references** the earlier intake did not fully link: every declared shared-URL packet must preserve its unique URL, complete cited+uncited physical row partition, and each referenced citation must match the corresponding request's article, source ID, physical source row, exact article claim scope, contributor support scope, contributor reading limits and shared-URL flag. Every shared citation must occur in exactly one packet; no foreign, missing or repeated cross-reference can pass, even if someone recalculates all JSON SHA-256 fields. This is structural integrity, **not** proof that a real external source is correct or safe.

### Discrepancy and dependency logic

For article citations, report disagreement when reviewer submissions differ on reached/redirected/unreachable status, observed URL, exact source locator, claim support/contradiction/uncertainty, or reported safety risk flags. **Matching statements that a claim is contradicted, a source redirected, or a safety topic is flagged still require follow-up.** Different dates or free-text evidence notes are *not* semantically reconciled: even a display label of `MULTIPLE_SELF_REPORTS_AGREE_UNVERIFIED` only means a few structured fields matched, not that evidence was independently verified.

For shared-source groups, compare each physical contributor row separately (reading status and source locator) and the reported scope relationship. Even when two self-reports claim the group is consistent, a **missing, unresolved, flagged, or conflicting article-specific citation** forces `CITATION_DEPENDENCY_HOLD`. Shared URLs are not consolidated into one source identity, and no contributor's source inspection can clear another contributor's article claim.

The tool rejects duplicated bundles; duplicate self-declared reviewer labels for the same request across files (after Unicode compatibility normalization, casefolding and whitespace normalization); invisible/control characters in reviewer labels; missing/extra/duplicate responses; out-of-date source manifest bindings; and upstream malformed inputs. Review labels **are not authenticated**: two different names can still be the same person. The tool makes no claim of independent or qualified human review. Input is limited to 64 local files, each bounded by upstream 2 MB JSON size guards. No networking or source URL retrieval occurs.

### Non-destructive cumulative review custody

An optional `--previous-report` binds the new triage to a prior full report: a changed manifest, missing request, deleted or rewritten reviewer record, or corrupted prior digest fails closed. The prior file is an **integrity receipt, not an authenticated signature**: anyone with uncontrolled write access could forge a replacement. Corrections must be explicitly reviewed and documented by a human rather than silently removing an unfavorable source assessment. If content legitimately changes, generate a new manifest and restart the review cycle; the old reviewed claim may not be carried forward automatically.

## Safe use in a trusted exact checkout

First execute the full existing validation/build/test gates on the **exact** branch and make sure the 35 drafted articles, water planner and seven source clusters have not drifted:

```sh
python -I preparedness/tools/evidence_freeze.py
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/review_receipts.py --out-dir preparedness/build/review-packets
python -I preparedness/tools/review_response_audit.py --emit-empty-template > preparedness/build/review-packets/review-a.json
```

A separate person may fill a copy of the **same exact-manifest scaffold** with their observations and save it to a distinct private file (for example `review-b.json`). Files must not be pushed to a public GitHub PR: they can contain reviewer identities, sensitive observations, or excerpts with intellectual-property constraints. No sample files containing fabricated approvals are shipped.

Then run:

```sh
python -I preparedness/tools/review_discrepancy_audit.py \
  --responses preparedness/build/review-packets/review-a.json \
  --responses preparedness/build/review-packets/review-b.json \
  > preparedness/build/review-packets/discrepancy-triage.json
```

On subsequent reviews, preserve the previous report and pass `--previous-report` to forbid silently dropping earlier statements:

```sh
python -I preparedness/tools/review_discrepancy_audit.py \
  --responses preparedness/build/review-packets/review-a.json \
  --responses preparedness/build/review-packets/review-b.json \
  --responses preparedness/build/review-packets/review-c.json \
  --previous-report preparedness/build/review-packets/discrepancy-triage.json \
  > preparedness/build/review-packets/triage-next.json
```

`--require-no-discrepancies` returns 1 for missing second-person inputs, recorded disagreements, adverse findings or dependent group holds, 2 for invalid input. **Exit 0 only means the specified *self-reported structured fields* were internally consistent.** It is emphatically not authorization to publish. `--require-release-ready` is deliberately and permanently nonzero (1) even when every input matches. Only independent editorial/subject-matter review plus separate explicit founder approval can authorize WordPress draft promotion after other gates are satisfied.

All outputs go to stdout; the program never creates or writes a file. Redirect output **only** to the existing private `preparedness/build/` location with secure permissions. Delete or quarantine personal reviewer data under the organization's retention policy; don't copy it into a public page or external mailing platform.

## Decision table

| Inputs for the exact request | Result (all are unverified) |
| --- | --- |
| None | `PENDING_HUMAN_INPUT` |
| Only one valid self-report | `SINGLE_SELF_REPORT_UNVERIFIED` |
| Multiple reports contradict on a structured field | `DISAGREEMENT_ESCALATE` |
| Multiple reports agree about adverse/uncertain/redirected evidence or flagged safety risk | `FOLLOW_UP_ESCALATE` |
| Multiple shared-source-group reports match but a cited article lacks corresponding aligned reports | `CITATION_DEPENDENCY_HOLD` |
| Multiple structured reports match and no adverse flags appear | `MULTIPLE_SELF_REPORTS_AGREE_UNVERIFIED` — still **not source clearance** |

The report intentionally exposes only request/packet SHA-256 identifiers, counts, classified disagreement dimensions, union of safety-risk labels and hashes of input records. It does not output free-form reviewer comments, personal names, observed redirect URLs, claim-specific text, or reading notes. SHA-256 is an input-change detector, not a signature, identity proof, or independently verified source custody.

## Test and release evidence

This additive sprint has 68 new local synthetic unittest methods (no downloaded external material), alongside the prior 138 source-queue/receipts/response-intake tests. Execute from the reconstructed **six-module synthetic fixture** if a full trusted checkout is unavailable; clearly distinguish results from full-corpus tests. The cases exercise malformed manifest cross-references, duplicate source rows, contradictory labels, redirected URLs, claim disagreement, uninspected scope, missing group dependencies, Unicode duplicate reviewer labels, append-only review receipts, confidential report output and safe failure.

**Release HOLD:** 35 long-form articles and one water planner are still drafts. Recorded source inventory (prior run) was 224 physical rows, 186 literal URLs, 367 article-source relationships and 30 shared-URL groups with **no documented independent human URL checks**. This sprint does not independently recheck external URLs, certified health/food/infant/medication/CO/water safety advice, copyright, the full WordPress preview, browser accessibility or production Core Web Vitals. Do not merge, publish, change menus, edit WordPress, or assert QD PASS based on this tool.
