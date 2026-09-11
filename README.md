# Final Vestige Site Layer

Private production plugin for versioned, QD-reviewed Final Vestige front-end features.

## Release model

- Feature work lands through pull requests.
- QD reviews the exact PR/head SHA and test results.
- The Decision Queue authorizes only the exact approved SHA.
- Production is the `production` branch.
- WordPress.com GitHub Deployments targets `/wp-content/plugins/final-vestige-site-layer`.
- Deployment is not completion: live destination readback is required before Notion closes `IMPLEMENTED + VERIFIED`.

## Bootstrap release

`FVSL-BOOTSTRAP-001` / plugin `0.1.0` contains the exact reviewed Signal Finder, Evidence Map and Detail Lens payload files. Runtime SHA-256 and byte-count verification is fail-closed: if any payload drifts, none of the three are emitted.

## Production safety

This plugin does not change Coming Soon/global indexing, accounts, permissions, billing, private-user processing, Scout publication state, or real-money trading controls.
