# FVF-6 — Evidence Trace

## Visitor job

Let a reader see where an investigation explicitly links narrative passages to its published source notes, then inspect those notes in place without losing the surrounding argument.

## Interaction principle

Evidence Trace adapts the source-in-context principle demonstrated by ProPublica's **Explore Sources** and Wikimedia/MediaWiki **Reference Previews**. It does not clone either interface. Final Vestige's adaptation is an opt-in reading layer: a compact article control reveals source-linked passages and provides an accessible disclosure beneath each passage containing only the source-note content already published on that page.

## Qualification

The payload fails closed unless the current document contains:

- an existing `[data-fv-footnotes]` source list;
- at least four narrative passages with `.fv-fn-ref[data-fv-fn]` markers before that list; and
- at least three valid referenced source-note records.

Pages that do not meet the contract receive no UI or class changes.

## Evidence boundary

The feature does not classify source quality, infer support, score uncited prose, create claims, fetch external material, or alter citation destinations. The interface explicitly says: **“Shows where this page links to source notes. It does not score uncited text.”**

## Accessibility and mobile behavior

- 44px minimum interactive targets.
- Real button state via `aria-pressed`.
- Per-passage disclosures use `aria-expanded`, `aria-controls`, labeled `role="region"` panels and native keyboard activation.
- Mobile stacks the feature control and makes source controls full width.
- Reduced-motion removes the passage transition.
- Forced-colors receives explicit borders/highlight treatment.
- No hover-only interaction is required.

## Performance and privacy

- No third-party JavaScript or CSS.
- No `fetch`, XHR, browser storage, cookies, analytics initialization or remote API calls.
- Source previews are cloned from existing page DOM only after the page qualifies.
- Payload identity is locked by deterministic byte-count and SHA-256 tests.

## Deployment boundary

This branch is an artifact + deterministic-CI candidate based on the inert `production` branch. It must not modify or bypass `FVSL-BOOTSTRAP-001`. Runtime manifest integration happens only after the bootstrap release is live, on a new exact SHA with fresh QD review.
