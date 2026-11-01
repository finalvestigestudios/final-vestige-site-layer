# R39 — Private reviewer-key receipt custody (HOLD, Issue #136)

**Scope:** Preparedness Archive source/citation safety gates only. This R39
stack follows R38 without changing the 35 article bodies, water-planning tool,
224 source records, 1,959 citations, 367 original article/source reading scopes,
43 fallbacks, 30 shared-URL groups, 15 repeated source-ID groups, or any WordPress
page, menu, homepage, production file or CMS record.

## Why this exists

R37 exports blank reviewer worksheets; R38 revalidates edited worksheets and
quarantines *only* untrusted observations. R38 fingerprints are **not** author
authentication. R39 adds a domain-separated HMAC-SHA256 receipt covering the
exact R37/R38 source and observation fingerprints, a 128-bit submission nonce,
a UTC second timestamp, a registered key handle, and an explicitly chained
receipt sequence + previous receipt hash.

A successful verification proves **possession of the independently provisioned
symmetric key** only. It does not prove a human identity, independence,
professional credentials, actual source reading, link accessibility, medical
or emergency safety, human review completion, editorial approval, QD PASS,
or authorization to publish. Every receipt and verification result is HOLD.

## Immutable evidence custody

- unsigned_challenge(trusted_r37_bundle, edited_csv_tables) invokes R38's
  exact immutable-column, citation-case, four-table, source/citation/lineage
  gate. The returned SHA-256 fingerprint binds the full quarantined
  observations, edited worksheet hashes, R37 and R38 receipts, and the
  R34/R35/R36 lineage. No review fields are promoted into approved findings.
- prepare_unsigned_receipt(challenge, reviewer_key_id, submission_nonce_hex,
  issued_at_utc, trusted_chain_head) builds the exact signing payload.
  The nonce must be cryptographically generated and encoded as **32 lowercase
  hex digits**. Timestamps must be precise UTC seconds ending in Z.
- sign_progress_receipt(unsigned_receipt, secret) is an offline,
  standard-library signing primitive. The HMAC key must be **at least 32 random
  bytes** and provisioned outside this repo. Do not record it in WordPress,
  issues, CSV files, a command line, Git history or CI artifacts.
- verify_progress_receipt(trusted_r37_bundle, edited_csv_tables, receipt,
  trusted_registry=..., trusted_chain_head=..., trusted_now=...) recomputes
  the original R38 quarantine and R39 challenge *from the independently
  trusted original worksheet baseline*. It rejects changed evidence, missing
  or extra receipt fields, weak/unknown/revoked/incorrectly scoped keys,
  noncanonical date or nonce, replay/fork/sequence drift, stale or future
  submissions, and bad signatures using constant-time tag comparison.

The registry is intentionally **not** an input field inside the receipt and
does not live in this code. External administrator-controlled registry entries
must contain exactly: secret (bytes), state (ACTIVE), scope
(PREPAREDNESS_UNVERIFIED_PROGRESS_ONLY), not_before and not_after (UTC
seconds). Revocations and identity-to-key provisioning are external controls.
The verifier's trusted_now must be independently sourced, timezone-aware UTC.

The trusted chain head is exactly a mapping with sequence and receipt_sha256.
The initial head has sequence 0 and a 64-zero hex receipt digest only for a
new independently controlled ledger. Every accepted receipt returns a
**proposed**, not automatically persisted, successor head. An authorized
ledger service must commit each successor **atomically and durably before
accepting any other submission**. Otherwise stale concurrent heads can still
admit forks, and a copied registry/ledger can defeat verification. Neither
this module nor CI provides that external state service.

**Threat boundaries:** HMAC is symmetric. A registry administrator holding the
secret can impersonate a key holder. A stolen key can be misused until revoked.
No legal or clinical identity is independently checked. SHA-256 alone is not
authentication. The apparent reviewer handle is not a certificate or name.
Real deployment requires securely bound key issuance, revocation, rotation,
incident response, audited ledger custody, and independently qualified
human reviewers; those remain unimplemented/release-blocking.

## Machine-preflight scope

R39 is loaded from an exact non-symlink sibling through the existing mandatory
private stage 13. CI derives an **unsigned, zero-progress** R39 challenge from
the complete R37 baseline. It checks HOLD flags, R37 and R38 fingerprints, and
the zero-progress case census. It deliberately does **not** create a real
key, fabricate a signed receipt, claim a human reviewer has signed, or silently
persist any ledger. Isolated synthetic tests use an explicitly labeled
nonproduction key and a tiny made-up 4-table workbook.

All R39 verification is read-only and offline. There are no network requests,
new external dependencies, public builds, WordPress writes, nav changes,
branch merges, or publication side effects.

## Independent coordination and release blockers

The seven original Claude source/contributor branches remain authoritative;
independent safety QA PR #157 and synthetic-fixture PR #169 remain separate,
unmerged drafts. Their exact commit identities and patches must continue to be
checked on every engineering run. Homepage work is a separate lane and untouched.

All **1,959 citation/claim observations, 367 source-reading scopes, 43
fallback relationships and 30 global shared-URL groups** still need true,
independent human review. Consequential emergency and medical guidance needs
qualified review; current official sources, source-reading equivalence,
rendered-browser safety/accessibility, and exact-head independent QD remain
release blockers. A successful HMAC check cannot satisfy any of these gates.

**Release state: HOLD. No real reviewer identities authenticated, no actual
signed human submissions or trusted durable ledger established, and no
source/medical/QD/publication approval conferred.**
