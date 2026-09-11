# Final Vestige Deployment Bridge — FVDB-001-R1 / v0.3.0

Review-only hardening candidate for the no-additional-WordPress-plan deployment lane. It does not install, activate, deploy, merge, publish, index, or change WordPress production by itself.

## R1 security changes
- Atomic deployment mutex using WordPress `add_option()` unique-key insertion; concurrent authenticated deployments cannot overlap target/backup swaps.
- Explicit idempotency key = SHA-256(commit + package SHA). A repeated release returns `already_deployed` only after installed manifest/file bytes re-verify.
- Race-safe single-use nonce claims use atomic `add_option()` insertion instead of transient get→set logic.
- `/status` is now HMAC-authenticated and returns only bridge version plus `ZipArchive` / direct-filesystem capability booleans.
- Rollback success is checked; failed restoration emits a distinct fail-closed error.
- Adversarial runtime harness covers replay races, concurrent lock ownership, stale/bad signatures, status authentication/minimality, malformed/oversized/path-traversal/duplicate/encrypted archives, manifest mismatch, failed target swap, and post-swap rollback.

## Gate order
1. Independent QD reviews the exact GitHub PR/head plus static/runtime test evidence.
2. Bryan gives one fresh WordPress install/activate confirmation in the QD chat for the exact QD-passed ZIP.
3. In WordPress Tools → FV Deployment Bridge, confirm `ZipArchive` and direct filesystem are available; installation does not deploy the Site Layer.
4. Bryan copies the generated secret to the private GitHub repository as `FV_WP_DEPLOY_SECRET`.
5. A separately reviewed sender signs `/status`; require both host capability booleans `true`.
6. First signed deployment is an inert Site Layer release. Visitor-facing deployment follows only after independent destination verification.

The Site Layer is never auto-activated by this bridge.
