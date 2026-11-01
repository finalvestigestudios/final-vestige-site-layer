# R41 — private historical review-receipt evidence custody (RELEASE HOLD)

Issue #136 only. This is an **engineering draft** stacked on frozen R40
\`e7982fd6554130d5f596e068b16e75aec4d21475\`. Neither this code
nor an archival hash is human identity, source verification, a clinical
or emergency-safety assessment, independent QD, or publishing permission.

## Reason for R41

R39/R40 validate recent receipts with a strict 24-hour freshness window.
A later audit should not silently discard complete edited worksheet evidence
or falsely claim the expired R39 key/clock validation was rerun. R41:

- Accepts a **new candidate** only by invoking the real R40 audit against
  original R37 worksheet evidence, the caller's externally controlled key
  registry, UTC clock, prior replay register, pinned start head and end head.
- Returns one **uncommitted** archival record retaining the entire original
  private edited CSV tables and signed receipts—not merely their hashes.
  Original source/citation evidence is still controlled by the separate
  frozen R34/R35/R36/R37 lineage, without URL de-duplication.
- Chains SHA-256-fingerprinted records to a separately pinned archive tip,
  the exact R39 receipt head, original R37 fingerprint, all R40 receipt hashes
  and all (key, nonce) pairs. Provides deterministic bounded retrospective
  audit against **both independently pinned** archive endpoints.
- Detects tampered or missing complete submission evidence, altered signatures,
  missing/reordered/repeated events, incompatible source fingerprints, R39
  sequence or digest discontinuities, nonce replay and forged QD/safety/PASS.
- Preserves *unverified* reviewer notes for investigation, never converts
  observations into completed human review. All release states stay HOLD.
- Adds **76 synthetic tests** including the two real R40 integration tests
  when executed in the full private repository. The required private stage 13
  checks only the zero-receipt unsigned R41 preflight. CI never manufactures
  a registered person, secret signing key, actual receipt or source finding.

## Non-negotiable trust boundary

This library is **read-only**. It **does not** implement the external ledger.
An administrator must provision independently trusted R37 fingerprints, R40
key/clock/nonce controls and archive start/end checkpoints. At ingestion,
an access-controlled service must atomically compare-and-swap the R39 tip,
archive tip and entire replay register, and durably store the complete
encrypted/private evidence plus independently pinned record receipt. The
R41 output's field \`independently_atomic_commit_performed\` is always false.

A hash chain is only tamper-evident **relative to an independently pinned
checkpoint**; a party controlling both ledger and its anchors can rewrite
history. Historical inspection verifies evidence preservation and structural
continuity, **not** that R40 authenticated signatures at ingest, that an
authority actually pinned the prior report, that an HMAC key belonged to
a real person, or that a reviewer consulted a live source. Those assurances
require independent identity/key issuance, logging, oversight, audit controls
and retention policies. Never trust an archive tip from the submitted record.

Historic R39 validity is **not** rechecked after the 24-hour window. Replaying
old evidence as recent or calling a historical archive a validated human
review is prohibited. Lost private submissions cannot be recreated from
their SHA-256 hashes.

The complete original edited worksheets may contain personal review notes.
They must **not** be committed to GitHub, attached to issues/PRs, published
or sent to WordPress. The fixture content committed to the tests is explicitly
synthetic; it has no real key material or actual reviewers. Production
retention would require private encryption, authorization, redaction and
appropriate deletion/retention policies.

## Preserved and pending

R41 changes **no** original article text, original 224 source inventories,
source URL groups, contributor reading-depth accounts, taxonomy, safety
states or generated WordPress-ready public articles. The frozen draft corpus
remains 35 articles plus one water-planning tool, 1,959 citation occurrences,
367 original article/source reading scopes, 43 fallback relationships and 30
shared-URL groups. The seven Claude clusters remain separately referenced.

Independent QA PR #157 and fixture test PR #169 remain distinct drafts.
No merges, navigation changes, public deployment, WordPress/CMS writes, or
false QD approval.

**Release status: HOLD.** Independent citation/source audits, qualified
emergency-safety review, current-link checking, rendered browser QA and
independent QD approval are still required.
