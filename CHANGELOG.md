# Changelog

## 0.4.0 — FVSL-VESTIGE-ASSEMBLY-HOME-002

- Adds one new progressive-enhancement payload:
  - **Signature Alignment** — drives a divider-slider interaction between two real documents
    already used elsewhere on the page (the 1903 NYPL map from the Library section, and the real
    evidence-boundary diagram from "Six Miles an Hour"): dragging the divider near the midpoint
    reveals the same real "why it matters" fact already used in the Library panel. Fail-closed
    try/catch, duplicate-init guard, no new dependencies, no network calls, no persistence.
    Without JavaScript, the two documents render side by side, split down the middle, each
    captioned — never blank or broken.
- Repins `actions/checkout` and `actions/upload-artifact` in CI from v4 (Node 20, deprecated) to
  v7 (Node 24), exact full-length SHAs, preserving the existing full-SHA-pinning practice.
- Homepage content: replaced the newsletter-style Dispatch framing ("One email a week...") with
  a quieter closing beat ("Some things are worth following...") around the same, untouched
  `wp:jetpack/subscriptions` mechanism; differentiated all six "Worlds" cards with distinct
  material treatments tied to what each pathway actually is (a redaction-stamped ledger for The
  Public Record, a terminal titlebar for Labs, bookshelf spines for Editions, a letterboxed reel
  for Films & Media, a correspondence stamp and real topic tags for The Exchange); added an
  explicit four-act narrative scaffold; fixed a real CSS grid bug that had left two rows with
  unfilled cells. See `homepage/README.md` for the full, current section-by-section record.
- Adds `tests/verify_signature_alignment.py` (exact payload identity, node-executed gate
  behavior, and adversarial safety checks) to CI.

## 0.3.0 — FVSL-VESTIGE-ASSEMBLY-HOME-001

- Adds three progressive-enhancement payloads for the redesigned homepage (see
  `homepage/page-6-home.blocks.html` and `homepage/README.md` for the paired WordPress page
  content, which carries the real headline, copy, navigation, and evidence as plain semantic
  HTML with no JavaScript dependency):
  - **Hero Assembly** — toggles attribute states on the real hero markup so the four evidence
    fragments visibly scatter and then assemble into place; on reduced motion or without JS the
    fragments simply render in their final, fully assembled position.
  - **Margins Wire** — enhances the existing, unmodified "Hidden in the Margins" markup (all 72
    real items, untouched) into a pausable, keyboard-navigable rotator with visible position and
    prev/next/pause controls, replacing the old passive-only CSS animation.
  - **Investigation Walkthrough** — drives the evidence panel of the new Live Investigation
    section (real NASA imagery and quotations from the published "The Hatch Opened Inward"
    investigation) via click, keyboard, and scroll.
- All three: fail-closed try/catch, duplicate-init guards, no new dependencies, no network
  calls, no persistence, real content only (no fabricated captions or citations).
- Adds `tests/verify_hero_assembly.py`, `tests/verify_margins_wire.py`, and
  `tests/verify_investigation_walkthrough.py` (exact payload identity, node-executed gate/timeline
  behavior via extracted pure-function seams, and adversarial safety checks) to CI.

## 0.1.0 — FVSL-BOOTSTRAP-001

- Introduces the governed Final Vestige Site Layer plugin runtime.
- Carries the exact reviewed Signal Finder, Evidence Map, and Detail Lens payloads.
- Verifies byte counts and SHA-256 hashes before emitting any payload.
- Adds deterministic CI for PHP syntax, payload integrity, and embedded JavaScript syntax.
- Establishes `production` as the WordPress deployment branch and requires live destination verification after deployment.
