# WordPress.com deployment target

- Site: `https://finalvestige.com`
- Platform: WordPress.com Atomic
- Production branch: `production`
- Target directory: `/wp-content/plugins/final-vestige-site-layer`
- Plugin entrypoint: `final-vestige-site-layer.php`
- Receiver: `https://finalvestige.com/wp-json/fv-deploy/v1/deploy`
- Repository secret: `FV_WP_DEPLOY_SECRET`

## Governed Deployment Bridge flow

1. A release candidate is reviewed and QD-approved at one exact PR head SHA.
2. CI checks out that exact head, validates the runtime payloads, builds the Deployment Bridge ZIP twice, requires byte-identical output, and verifies the bridge manifest/HMAC contract.
3. The exact deterministic ZIP is retained as the PR CI artifact.
4. Production deployment is permitted only through a two-parent GitHub PR merge commit whose tree is byte-identical to the reviewed PR head. Direct pushes, squash/rebase merges, or merge-tree drift fail closed and do not call WordPress.
5. The production job rebuilds the same package, binds its generated `release-manifest.json` to repository `finalvestigestudios/final-vestige-site-layer`, branch `production`, and the exact reviewed PR head SHA, then HMAC-signs the exact request body using `FV_WP_DEPLOY_SECRET`.
6. The Deployment Bridge verifies authentication, nonce/timestamp, package SHA-256, manifest identity and file allowlist before swapping files. The bridge never auto-activates the Site Layer.
7. Deployment success is not completion. Independently verify the installed bytes and live destination before marking the decision `IMPLEMENTED + VERIFIED`.

The source `release-manifest.json` remains the reviewed feature/payload metadata. `ops/build_site_layer.py` deterministically adds the Deployment Bridge identity and complete regular-file allowlist to the manifest placed inside the deployment ZIP.

Never print or commit `FV_WP_DEPLOY_SECRET`. Any change to workflow, builder, sender, package bytes, or candidate head invalidates prior exact-artifact approval and requires fresh QD.
