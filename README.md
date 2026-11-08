# Final Vestige Site Layer

Private production deployment repository for versioned, QD-reviewed Final Vestige front-end features.

## Safety model

- `production` is the WordPress deployment branch.
- Feature releases are proposed from release branches through pull requests.
- QD reviews the exact PR/head SHA and test results before delegated approval.
- The Decision Queue authorizes only the exact approved SHA.
- Deployment is not completion: live destination verification is required before Notion closes `IMPLEMENTED + VERIFIED`.
- This bootstrap commit is intentionally inert and contains no WordPress plugin runtime.
