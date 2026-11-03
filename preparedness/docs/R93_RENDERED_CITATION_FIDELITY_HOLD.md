# R93 — Original body to rendered WordPress draft citation fidelity (PRIVATE HOLD)

Issue #136. Parent R91 exact commit f4e3577839cef3590f83fca90dca6ab165794bd3. Parallel additive private diagnostic, independent of still-active R92 draft PR #766. No CMS, WordPress, navigation or publication writes.

## Reconciliation boundary

Earlier R80–R91 ledgers preserve 41 complete research/reviewer packets, including six planned tools. R92 discovered an important inventory distinction: original working draft files have 35 article body+metadata pairs, but only one implemented WordPress-ready tool (water-planner). The other five tools are planned, not yet WordPress-ready. R93 derives these two counts independently from the actual Library, rather than silently treating all 41 historic review packets as 41 importable draft files.

For every actual draft, R93 connects the complete literal original body citation to its contributor-specific source record and generated WordPress-ready HTML. Its scoped HTML parser checks each literal citation occurrence (including repeated IDs), rendered inline footnote number, anchor, aria label, separate exact literal source URL, original source title, full author-specific source_use reading note, and human-link verification flag. It checks that shared-URL collision notices remain visible only for affected unresolved sources; an undeclared same-URL identity fails. Both WordPress wrapper and noindex local preview must retain the complete rendered document. The draft badge and pending human safety warning must survive. Distinct actual articles/tools cannot share routes.

Each private report retains original source IDs, author scope, literal URLs, per-occurrence ranks, and a deterministic SHA-256 seal. No URL is canonicalized or silently merged. Human claim, qualified safety, and QD statuses remain NOT_REVIEWED and every row is HOLD/may_publish=false.

**This gate verifies rendering/transport fidelity only. A citation surviving rendering does not show that its source supports any claim or that emergency/medical instructions are correct or safe.** An existing metadata flag saying approved is not independently qualified safety review; the tool does not forge or revoke it. Manual review remains required.

## Trusted checkout commands — private only

1. python -I -m unittest discover -s preparedness/tests -p test_r93_rendered_citation_fidelity.py -v
2. python -I preparedness/tools/r93_rendered_citation_fidelity.py
3. python -I preparedness/tools/r93_rendered_citation_fidelity.py --private-json-stdout > /tmp/r93-source-review.json
4. python -I preparedness/tools/validate.py
5. python -I preparedness/tools/build.py
6. python -I -m unittest discover -s preparedness/tests -v
7. rm -f /tmp/r93-source-review.json

The private JSON includes literal URLs and full contributor reading notes; do not publish, share or CMS-import it. The proposed private Actions workflow runs 49 individually discoverable mutation scenarios (seven source locations across seven distinct corruption dimensions), additional independent adversarial tests, real library reconciliation, validator, offline builder and the complete Python test suite. Green diagnostics are NOT mandatory release-integrity completion.

## Mandatory HOLD list

Five currently missing tool draft pairs; the R92 recorded family-communication-plan citation ordinal 16 historical/current source-ID disagreement; 30 unresolved same-URL reading-scope groups; five contributor branch differences from historical baselines; 15 safety exceptions; 22 editorial decisions; human source/link/claim assessment; qualified emergency/medical safety review; actual WordPress/browser accessibility; independent QD; mandatory 13-stage release integrity; founder final approval. No invented safety or human-verification claims.

Independent QA draft PR #157 and synthetic-fixture draft PR #169 are unmerged; homepage PR #49 and flagship PR #604 remain outside this lane. This R93 branch never touches original article/source metadata, taxonomy, external CMS, homepage or public navigation.

**Release state: HARD HOLD. No merge and no publication.**
