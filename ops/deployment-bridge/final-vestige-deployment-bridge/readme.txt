=== Final Vestige Deployment Bridge ===
Contributors: finalvestige
Requires at least: 6.5
Requires PHP: 8.1
Stable tag: 0.2.0

Private fail-closed deployment receiver for the Final Vestige Site Layer.

Security model:
- HMAC-SHA256 authenticated requests only.
- Repository and production-branch allowlists are hard-coded.
- Five-minute timestamp window and single-use nonce replay protection.
- Authentication failures produce no state/database write and return no detailed auth oracle.
- Compressed, expanded, entry-count and regular-file-count limits.
- ZIP path traversal, duplicate entry and encrypted-entry rejection.
- Safe streamed extraction; ZipArchive::extractTo is never used.
- Release manifest binds repo, branch and commit and is the complete regular-file allowlist.
- Every declared file is SHA-256 verified before and after the swap.
- Rollback copy lives outside the WordPress plugins directory.
- The Site Layer is never activated automatically.
- Public status exposes only non-secret deployment and host-capability state.
