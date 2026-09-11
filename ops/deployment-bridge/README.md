# Final Vestige Deployment Bridge v0.2.0

Review-only prototype for a no-additional-WordPress-plan deployment lane.

## Gate order
1. Independent QD reviews the exact GitHub PR/head and local/static test evidence.
2. Bryan gives one fresh WordPress install/activate confirmation in the QD chat for the exact QD-passed ZIP.
3. After activation, read `GET /wp-json/fv-deploy/v1/status` and require `host_capability.ziparchive=true` and `host_capability.filesystem_direct=true`.
4. Only if both pass, Bryan copies the generated secret from Tools → FV Deployment Bridge into the private GitHub repo as `FV_WP_DEPLOY_SECRET`.
5. Build and QD-review the GitHub Actions sender separately.
6. First signed end-to-end test uses an inert Site Layer release. Visitor-facing production deployment follows only after destination verification.

Installing this bridge does not deploy or activate the Final Vestige Site Layer.
