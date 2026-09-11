=== Final Vestige Deployment Bridge ===
Contributors: finalvestige
Requires at least: 6.5
Requires PHP: 8.1
Stable tag: 0.3.0

Private fail-closed deployment receiver for the Final Vestige Site Layer.

Security model:
- HMAC-SHA256 authenticated deploy and status requests only.
- Repository and production-branch allowlists are hard-coded.
- Five-minute timestamp window and race-safe single-use nonce claims backed by atomic option insertion.
- Authentication failures produce no state/database write and return no detailed auth oracle.
- One atomic deployment mutex serializes authenticated deployment attempts across PHP workers.
- Exact commit + package SHA idempotency returns already_deployed only after installed bytes still verify against the manifest.
- Compressed, expanded, entry-count and regular-file-count limits.
- ZIP path traversal, duplicate entry and encrypted-entry rejection.
- Safe streamed extraction; ZipArchive::extractTo is never used.
- Release manifest binds repo, branch and commit and is the complete regular-file allowlist.
- Every declared file is SHA-256 verified before and after the swap.
- Rollback copy lives outside the WordPress plugins directory and rollback success is checked.
- The Site Layer is never activated automatically.
- Authenticated status exposes only bridge version and host capability booleans.
