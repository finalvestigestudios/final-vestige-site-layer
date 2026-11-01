# R40 — Preparedness private receipt transcript audit (RELEASE HOLD)

**Issue:** #136. **Scope:** source/citation review custody only. Built on the R39
reviewer-key receipt gate; neither R40 nor any earlier machine validator
proves that a person reviewed a source or that emergency/medical advice is safe.

## What R40 adds

R39 checks one quarantine-note receipt against a separately trusted current
chain head. Repeated nonces, duplicated notes, reordered receipts and a missing
full transcript could still escape detection if a caller mishandled its
external ledger. R40 adds a **read-only, bounded, offline segment audit** that:

1. Checks *each* signed receipt from the exact original R37 evidence-bound
   worksheet baseline through the R38 quarantine and R39 HMAC gate.
2. Requires an independently pinned **start AND end** chain head; the untrusted
   transcript is not permitted to choose its own authoritative endpoint.
3. Enforces a contiguous incrementing chain with no dropped, substituted,
   reordered or duplicated receipts.
4. Rejects any (key handle, 128-bit nonce) pair already in the separately
   trusted prior-nonce register or duplicated in this segment. Identical nonce
   values under **different** independently provisioned keys are distinct.
5. Checks issuance times are in order, all applicable key credentials remain
   ACTIVE/within scope and valid at verification time, and every submitted
   original CSV/evidence lineage matches the signed fingerprint.
6. Produces an SHA-256-fingerprinted, HOLD-only audit report containing
   receipt hashes, the externally pinned heads, and **proposed** new nonce
   entries. It does not persist or approve anything.

The batch cannot exceed 128 receipts. Historical replay of arbitrarily old
receipts is **not supported**: R39 deliberately rejects receipts older than
24 hours relative to an independent UTC verification clock. This is a
recent-window custody validator, not a permanent historical audit mechanism.

## Mandatory private checkout check

The existing citation/source preflight stage 13 now imports the R40 module via
its exact nonsymlink sibling path and checks the complete original R37/R38/R39
**unsigned** challenge. It refuses altered original evidence, changed HOLD
flags, nonzero fabricated progress, substituted code or missing R40. No key,
signature, registered reviewer, ledger or artificial human-review annotation
is created by CI. The stage stays read-only.

Synthetic tests demonstrate valid chaining and independently exercise
false QD, safety, human/source-verified and publication assertions, byte-level
receipt changes, missing/extra fields, nonce reuse, mutated source evidence,
changed edited observations, revoked/wrong-scope keys, bad timestamps, false
anchors, transcript truncation, reordering, and absent prior replay state.
Test secrets are clearly synthetic, and never service credentials.

## Threat model / external controls

- **HMAC proves key possession**, not independent real-world identity.
  A registry administrator with the symmetric key can impersonate its holder.
- The verifier cannot establish that the supplied end checkpoint, nonce
  register, registry or clock was genuinely controlled by an independent
  authority; the caller must enforce that separation.
- The module returns *proposed* replay-state changes. Without **atomic and
  durable compare-and-swap** of the endpoint and nonce register in a trusted
  service, concurrent submissions can fork despite passing offline audits.
- Key issuance, access controls, identity verification, revocation/rotation,
  incident response and durable append-only log administration do **not** exist
  in this module. A revoked key fails closed on current verification; historical
  verification across rotations needs a separately designed trusted audit log.
- Worksheet text remains *unverified observations*. A correct signature
  cannot authenticate true source reading, source availability, claim
  correctness, independence, credentials, emergency-safety clearance, QD
  approval, or a release decision.

## Preserved source and article custody

No edits to the 35 original articles, one water-planning tool, 224 original
source records, 186 URLs, 1,959 citation occurrences, 367 contributor-specific
article/source relationships, 43 fallback relationships, 30 shared-URL groups,
15 duplicate source-ID groups, source-reading notes, historical safety verdicts
or draft statuses. Source URLs are **never** deduplicated by citation shape.
No CMS, WordPress, production, homepage, top-level nav, public publishing,
email/focus flow, or merge operations.

The original seven Claude contributor heads and independent safety QA PR
#157/synthetic fixture PR #169 must continue to be reconciled and checked
independently. A green machine pipeline is not an editorial clearance.

## Required human blockers: release HOLD

Qualified independent review of the 1,959 claim/citation occurrences,
367 source-reading scopes, 43 fallbacks, 30 shared-source groups, live URL
access and official advice, medical/food/water/fire safety, rendered browser
and print output, and independent exact-head QD remain outstanding.

**No publication, no CMS/nav writes, no false QD PASS, and no unreviewed
emergency/medical guidance marked safe.**
