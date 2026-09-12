# FVD-6 Phase 2 — Governed Content Publishing Control R1

## Status

**Source/build prototype only. Not activated. Not deployed.**

This package defines the bounded control contract for moving one exact, independently QD-cleared Final Vestige article, Library page, or Public Record page/post package to WordPress without routine founder intervention. It does **not** add a live WordPress route, contain credentials, make network requests, change Coming Soon/indexing, or authorize publication by itself.

The established Site Layer Deployment Bridge remains a separate infrastructure path. FVD-6 must receive fresh independent QD review plus any platform-required one-time founder confirmation before an authenticated WordPress content adapter can be activated.

## Why this is fail-closed

`ops/content_publish_control.py` accepts a package only when all of the following are true:

1. The envelope and manifest have exact schemas; unknown fields are rejected.
2. The canonical manifest SHA-256 exactly matches `package_sha256`.
3. `package_id`, QD artifact identity, QD decision identity, target kind/ID, expected destination fingerprint, authorized fields, and mutation are explicit.
4. The target is a `page` or `post` and is present in an **external execution allowlist**. A package cannot authorize its own target.
5. Mutation keys exactly equal `authorized_fields`; no implicit write scope exists.
6. Only resource-local fields in the R1 contract are eligible. User, account, permission, plugin, theme, billing, site-option, global launch/Coming Soon, Public Scout, destructive delete/trash, and other global scopes have no representation and therefore fail validation.
7. The complete governed resource snapshot includes title, content, excerpt, featured media, slug, status, SEO and indexing state. The current destination must exactly match `expected_before_sha256` before any write.
8. A write is followed by an independent adapter readback. The exact expected post-state must match, including fields the package did not authorize.
9. Any write/readback failure triggers restoration to the exact pre-write snapshot and a second readback. Failed or unverifiable rollback raises `CriticalRollbackFailure` and declares destination state unknown.
10. The idempotency ledger is committed only after destination verification. If ledger commit fails, the destination is restored before returning failure.
11. Replaying the same `package_id` is a no-op only when the package hash is unchanged **and** the destination still matches the previously verified after-state. Reusing an ID with different bytes, or replaying after destination drift, fails closed.

## R1 mutable resource fields

The control plane recognizes these resource-local fields:

- `title`
- `content`
- `excerpt`
- `featured_media`
- `slug`
- `status`
- `seo`
- `indexing`

They are **not automatically writable**. Each package must name the exact subset in `authorized_fields`, and that list must exactly equal the mutation keys. `trash`, `delete`, `deleted`, and `auto-draft` statuses are forbidden.

R1 deliberately has no mechanism for global WordPress settings or destructive operations. A future expansion of scope is a new governed artifact, not a configuration tweak.

## Reference package

```json
{
  "manifest": {
    "spec": "fvs-content-publish/v1",
    "package_id": "FVD6.ARTICLE.0001",
    "qd_artifact_id": "QD-EXACT-ARTIFACT-ID",
    "qd_decision_id": "DQ-EXACT-DECISION-ID",
    "target": {"kind": "post", "id": 123},
    "expected_before_sha256": "<64 lowercase hex>",
    "authorized_fields": ["content"],
    "mutation": {"content": "<p>Exact QD-cleared body</p>"}
  },
  "package_sha256": "<sha256 of canonical manifest JSON>"
}
```

The executor's allowlist is supplied independently, for example `{("post", 123)}`. Package bytes never widen it.

## Transaction state machine

`VALIDATE → ALLOWLIST → READ/PRECONDITION → WRITE → READBACK → LEDGER COMMIT → IMPLEMENTED + VERIFIED`

Failure after write becomes:

`FAILURE → RESTORE EXACT BEFORE SNAPSHOT → READBACK → VERIFIED ROLLBACK`

If restore or rollback readback cannot be proven:

`CRITICAL / DESTINATION UNKNOWN → STOP`

No later package may be attempted by a caller after an unknown-state result until the destination is manually reconciled.

## Idempotency

`MemoryLedger` exists for tests. `JsonLedger` is the atomic local reference implementation and uses temp-file + fsync + `os.replace`. A live WordPress adapter may use a stronger durable store, but it must preserve the same invariant:

**one package ID → one immutable package hash, recorded only after independently verified destination state.**

## WordPress integration contract (held, not implemented here)

A later authenticated adapter must:

- read exactly one page/post by numeric ID;
- expose the governed snapshot fields faithfully;
- patch only the exact authorized resource-local fields;
- restore the exact before snapshot when rollback is required;
- return exact destination state for verification;
- never infer or broaden target scope;
- never mutate global site options, users, roles/capabilities, plugins, themes, billing, private-user data, Public Scout release state, or whole-site launch/indexing state;
- keep Coming Soon and unrelated SEO/indexing state unchanged unless a future independently governed contract explicitly authorizes that exact scope;
- preserve the established authenticated/fail-closed bridge principles, while using a content-specific endpoint and identity rather than silently overloading the plugin deployment endpoint.

## Acceptance/adversarial coverage

`tests/test_content_publish_control.py` proves:

- exact package hash/tamper rejection;
- exact schema and mutation scope;
- independent target allowlist;
- preservation of status/slug/SEO/indexing when not authorized;
- destructive status rejection;
- destination precondition mismatch → zero writes;
- successful mutation + destination verification;
- readback mismatch → exact rollback;
- post-write exception → exact rollback;
- rollback exception/readback mismatch → critical unknown-state failure;
- ledger failure after write → rollback;
- exact replay → verified no-op;
- same ID/different bytes → conflict;
- replay after destination drift → conflict;
- atomic durable reference-ledger behavior;
- empty allowlist rejection.

## QD / release boundary

Green tests are evidence only. They are not QD approval and do not authorize an endpoint, credential, WordPress mutation, merge, deployment, publication, indexing change, global launch, private-user processing, spending, billing, account/permission changes, public Scout release, or external commitment.

Any code/test/workflow/contract change after identity freeze creates a new artifact identity requiring fresh verification and QD.
