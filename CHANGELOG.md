# Changelog

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
