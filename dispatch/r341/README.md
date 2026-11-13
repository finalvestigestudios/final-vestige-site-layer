# Dispatch R341 — Evidence-to-Revenue Acceptance Lab (DRAFT / DO NOT SEND)

This add-only, stacked review deliberately leaves the six original PR #175 issues unchanged. **No sender/list access, test send, WordPress write, merchant link, analytics deployment, or payment action.** This is not release approval.

## What changed beyond R340
* One testable, **source-to-outcome acceptance contract** rejects newsletter clicks, downloaded PDFs, incomplete subscriber counts, and affiliate outbound links as paid conversions. Rejects private recipient fields and duplicates. Requires merchant settlement evidence and qualified session match. Zero revenue means zero only when *both* reporting systems attest complete records; otherwise the number is **unknown**, not 0.
* Explicitly supports Jetpack's previously verified WordPress.com user pathway as distinct from a new double-opt-in challenge; both require provider-authoritative evidence.
* Provides a per-offer decision and a no-sending progression hypothesis to guide subscribers toward *one* approved relevant offer, not blanket marketing.

Run native Node tests if available: \`node --test dispatch/r341/outcome_proof.test.cjs\`. Input deliberately defaults to no live records. \`outcome_proof.cjs\` is a pure CommonJS module: no network, no file writes, no external packages.

Canonical: [Issue #174](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/174); original six-edition [PR #175](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/175); independent release gate [PR #201](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/201); parent editorial [PR #2398](https://github.com/finalvestigestudios/final-vestige-site-layer/pull/2398).