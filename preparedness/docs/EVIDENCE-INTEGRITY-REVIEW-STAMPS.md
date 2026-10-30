# Preparedness original-source and complete-copy freeze — HOLD

This nested draft PR adds a deterministic input-integrity barrier on top of Preparedness integration draft PR #176, without changing any of its original 35 long-form article bodies, metadata, seven cluster source fragments, historical approvals, WordPress pages, site navigation, Focus lead magnet or live homepage. Source and body baseline was read directly from the exact Git tree at c8df99cc661e518e93e58e1cc1ea3d7256f58643 on October 30, 2026.

## The holes this closes

The existing source crosswalk guards duplicate URL groups, but did not freeze noncolliding URL records: a unique-URL source's notes, scope, verification date or support claim could drift without triggering a crosswalk comparison. Also, prior named founder safety approval was not cryptographically tied to the actual version of an article; a copied approval could survive subsequent edits.

The existing eight source JSON paths and their original Git blob SHAs are now checked locally against the crosswalk. A new JSON ledger locks all 35 article bodies and metadata plus the water planner body and metadata (72 files), including contributor origin and exact Git bytes. Changing an article, adding/deleting a fragment, adding an untracked article pair or reassigning an article's source origin causes the validator to FAIL until a new independently reviewed baseline is recorded. A SHA is a provenance fingerprint, not proof of honest source interpretation, nor a digital signature.

A new review fingerprint is computed from the exact article copy, important metadata, cited source rows as read by that contributor, notes, source-use statements, human-check state and shared-source resolution status. When an article is marked published, a purported approved safety review (if present) and an approved independent release review must carry that same fingerprint. Old reviews cannot silently authorize a changed article or evidence trail.

Reviewer warning: Never calculate a fingerprint and mechanically paste it into an approval record. The value is provided only so a named qualified reviewer can attest to exactly the copy and source evidence they really read. No fingerprint has been attached to an article or claimed as an approval.

## Exact-head commands, on a checkout with private repository access

    python -I preparedness/tools/evidence_freeze.py
    python -I preparedness/tools/evidence_freeze.py --fingerprint making-water-safer
    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v
    python -I preparedness/tools/audit_integration.py --require-release-ready

The final command is expected nonzero: 30/30 shared-source groups remain unreviewed, 0/224 original link checks completed by a human, independent clinical/food/CO/water editorial review unresolved. Native Python suite and preview rendering must still be executed on the exact PR head; review-only data are NEVER launch permission.

Review companions remain independent: safety QD PR #157 and synthetic-fixture PR #169. Their SHA baselines are recorded in the source crosswalk. Draft PR #176 remains an integration candidate, not a verified release.

> **2026-10-30 Start rebase update:** The subsequently revised Start contributor added a *fourth independently read scope* for the already-shared FEMA V-1008 source URL; the source row total increased from 223 to 224, machine-marked source rows from 208 to 209, while literal unique URLs **remained 186** and unresolved exact duplicate-URL groups **remained 30**. All human link checks remain false. Earlier conclusions about the initial integration baseline apply only to their original Git SHAs. Refer to `START-LATEST-SAFETY-RECONCILIATION.md` and the latest evidence lock. **No QD or medical safety approval is claimed.**
