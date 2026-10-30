# Changelog

## 0.4.0 — FVSL-VESTIGE-ASSEMBLY-HOME-002 (continued, same candidate, pre-merge)

- **Signature Alignment: two further P2 findings from an independent QD review (#5708105650),
  fixed without redesigning the interaction or its historical content.**
  1. **Mobile touch scrolling was blocked in non-enhanced mode.** The static CSS applied
     `touch-action:none` and `cursor:ew-resize` to `.fv-align__stage` unconditionally, so a
     visitor on mobile without JavaScript, or without `inert` support, could land on a large
     region of the page where normal touch scrolling was suppressed even though the slider was
     completely nonfunctional there. Fixed: both properties now live only in a new
     `.fv-align__stage.fv-align--enhanced{...}` rule, and the `fv-align--enhanced` class is added
     by the payload's JS at the same point it applies `role="slider"` — and removed again by the
     existing midway-failure cleanup path if init crashes partway through, alongside the
     role/tabindex/aria-describedby it already removed. Native touch scrolling and the default
     cursor are therefore the default everywhere until a real slider actually exists. The drag
     handle (the circular grab affordance on the divider) is now `display:none` by default and
     only shown via `.fv-align__stage.fv-align--enhanced .fv-align__handle{display:flex}`, so a
     nonfunctional stage never visually implies dragging is possible. The intro copy no longer
     tells visitors to "slide between" the two documents (true only once enhanced); it now reads
     "...shown side by side — then see why we show them together," accurate in every state.
     `tests/verify_signature_alignment.py` gained CSS-structural assertions for the rule split and
     the handle's default-hidden/enhanced-visible behavior, plus copy assertions against the old
     and new intro text. `tests/verify_signature_alignment_keyboard_browser.py` gained real-browser
     checks of computed `touch-action`/`cursor`/handle-`display` across all four required states:
     enhanced, no-JS, unsupported-`inert` (simulated by shimming `document.createElement` before
     the payload loads), and a simulated mid-init failure (simulated by shimming
     `Element.prototype.addEventListener` to throw once, after the JS has already started
     applying enhancement, to prove the catch block actually strips it back out rather than just
     happening to never have applied it).
  2. **ARIA slider min/max didn't match the real reachable range.** The slider declared
     `aria-valuemin="0"`/`aria-valuemax="100"`, but `setPosition()` has always clamped real
     movement to 4–96 (keeping a visible sliver of both images at either extreme), so the
     accessibility contract promised a range assistive technology could never actually reach.
     Fixed: the declared range now matches reality (`aria-valuemin="4"`, `aria-valuemax="96"`);
     the existing 15/85 discovery thresholds are unchanged. `tests/verify_signature_alignment.py`
     gained keyboard-endpoint-clamping assertions (50× `ArrowRight` → `aria-valuenow` is exactly
     `"96"`; 100× `ArrowLeft` → exactly `"4"`) and the declared-range check.
     `tests/verify_signature_alignment_keyboard_browser.py` gained real-Chromium coverage of the
     same keyboard endpoints and announced `aria-valuetext`, plus a real `page.mouse` drag and a
     synthetic touch-type `PointerEvent` drag, both dragged well past either edge of the stage and
     both confirmed to clamp at 4/96, never 0/100.

- **Signature Alignment: three further accessibility findings from a conditional-hold QD review,
  fixed without redesigning the interaction or its historical content.**
  1. **Unsupported-`inert` fallback no longer blurs readable content.** The previous fix only
     gated the `inert` assignment on feature support (`if(supportsInert)fact.inert=true`), but
     still unconditionally added the CSS-blur-triggering `fv-align__reveal--pending` class — so a
     browser without `inert` support got the exact defect the fix was meant to prevent: a
     visually illegible but still keyboard-focusable link. Fixed: the whole enhancement now
     returns early when `inert` support can't be confirmed, falling back fully to the same
     always-readable, non-interactive static presentation as no-JS. New regression test
     (`buildDom({noInertSupport:true})`) asserts no concealment, no role/tabindex, and no event
     wiring happens in that case.
  2. **No-JS fallback no longer advertises slider semantics it can't back up.** The static markup
     baked in `role="slider"`, `tabindex="0"`, and `aria-value*` unconditionally, so a
     non-functional comparison stage (no JS) still claimed to be an interactive, keyboard-operable
     slider — a real WCAG 4.1.2 (Name, Role, Value) violation. Fixed: the static markup now carries
     none of those attributes; `role`, `tabindex`, `aria-labelledby`, `aria-valuemin`,
     `aria-valuemax`, and `aria-describedby` are applied by the payload's JS only, on successful
     init, and stripped again by the existing midway-failure cleanup if init crashes after
     applying them. Both historical documents and the full explanatory finding remain directly
     readable without JavaScript regardless (verified: real-browser Tab order with JS absent now
     lands on the source link two Tabs in, since neither the inert stage nor the JS-only button
     are Tab stops).
  3. **ARIA slider content model corrected.** Nesting two full `<img>` elements (with real alt
     text) and their caption `<span>`s inside a `role="slider"` element risks that content never
     reaching assistive technology at all: slider is a single name/value widget, not a generic
     container, and many screen readers present it as opaque, exposing only its accessible
     name/value rather than walking its DOM children. Fixed: once the slider role is active, both
     `.fv-align__panel` elements get `aria-hidden="true"`, and a new always-present,
     visually-hidden `<p id="fv-align-desc">` — built from the same real alt text and captions
     already used for the images, not new copy — is wired to the stage via `aria-describedby` so
     their actual content reaches screen reader users through a channel the opaque widget role
     can't swallow.
  4. **Real-browser test runner hardened.** `tests/verify_signature_alignment_keyboard_browser.py`
     previously resolved Playwright via two independent bare `require('playwright')`/
     `require.resolve('playwright')` calls — safe only by coincidence wherever both calls happen
     to share a resolution base (e.g. a global NODE_PATH install), but capable of silently
     diverging (prerequisite check succeeds via directory-walk resolution from the repo root,
     while the actual runner script — generated into an unrelated temp directory — fails to
     resolve the same bare specifier) for a locally-per-project-installed Playwright, the more
     realistic "wherever Playwright is available" case. Fixed: Playwright's absolute entry path is
     now resolved exactly once and that literal path is threaded into the generated runner's own
     `require()` call, so the two can never disagree by construction. Exit codes are now also
     distinct and documented (0 = genuinely passed, 1 = ran and failed, 2 = skipped — Playwright
     unavailable), and no skip path ever prints anything containing the word "PASS", so a missing
     dependency cannot be mistaken for successful verification by anything that only checks the
     exit code or greps output.

  `tests/verify_signature_alignment.py` gained scenario coverage for all of the above (the
  unsupported-`inert` fallback, JS-only role/tabindex/aria-describedby application and its
  removal on a midway failure, and the aria-hidden panels / aria-describedby wiring), and
  `tests/verify_signature_alignment_keyboard_browser.py` re-confirmed the full accessibility
  contract end-to-end in real Chromium, including the corrected no-JS Tab sequence.

- **Signature Alignment: concealed-content keyboard accessibility fixed.** An independent QD
  review of the just-redesigned discovery interaction found that CSS `blur()` alone was not
  sufficient: the concealed fact's nested source link stayed in normal keyboard Tab order while
  visually illegible, and activating "Show the connection" could strand focus (the button was
  disabled without any explicit focus destination). Fixed:
  - The concealed fact element is now also marked `inert` (feature-detected, with the existing
    blur as an always-present visual fallback) after a successful JS init, so the link cannot
    receive keyboard focus or be activated until discovery — removed the instant discovery fires.
  - Button-triggered discovery moves focus predictably to the revealed fact (`tabindex="-1"` on
    the `<p>`, focused programmatically); drag/keyboard-triggered discovery deliberately leaves
    focus on the comparison stage and only announces the finding via the existing live-status
    region, so a user mid-interaction with the slider isn't yanked elsewhere.
  - A failure partway through initialization (after concealment was already applied) is now caught
    and reverses the concealment, so a partial failure can never leave the real evidence
    permanently hidden.
  - Added `a:focus-visible` / `:focus` outline styles for the fact element and its link.
  - `tests/verify_signature_alignment.py` gained inert-state assertions across every scenario, a
    focus-call-count check for the button/slider focus-management split, and a new
    midway-failure-leaves-no-residual-concealment regression.
  - Added `tests/verify_signature_alignment_keyboard_browser.py`: a real-browser (Playwright/
    Chromium) keyboard/focus test, run against a fixture built live from the current page markup
    and payload (not a frozen copy). Not part of the CI gate (no Node/Playwright dependency exists
    in this repo for CI to install) — run manually. Confirmed passing against this exact head: the
    concealed link is skipped entirely in the pre-discovery Tab sequence; button-triggered reveal
    moves focus to the fact and the link becomes Tab-reachable immediately after; keyboard/slider
    discovery never moves focus off the stage; re-crossing both extremes after discovery produces
    no duplicate status announcement; the no-JS fallback has no concealment at all.

- **Signature Alignment redesigned as a genuine evidence-discovery interaction**, following a
  second independent QD finding that the prior fix (which only corrected the self-triggering
  badge) still left the interaction decorative: the real "why it matters" fact was printed
  statically below the stage regardless of interaction, so "aligning" the divider changed nothing
  but a badge and a border. Re-verified against the "Six Miles an Hour" post's own text (re-fetched
  2026-10-29) that the 1903 map and the 1918 wreck do not share any literal geographic or
  chronological overlap — the Malbone Street curve did not exist when the map was drawn — so the
  interaction's copy and mechanic were redesigned around that honest relationship instead of a
  false "alignment" framing:
  - The fact panel now stays genuinely concealed (blurred via CSS, never removed from the DOM) until
    the visitor has explored both ends of the comparison stage, or used the new, always
    keyboard-reachable "Show the connection" button — the required non-drag alternative. Concealment
    is added only after a successful JS init, so a no-JS page or a failed init never conceals
    anything.
  - The revealed state unblurs the real finding, locks the stage's amber border, and announces the
    discovery through a new `aria-live="polite"` status region, so assistive technology learns the
    actual finding, not just a badge state change.
  - Headline, intro, and fact copy were rewritten to state plainly that the map "isn't a record of
    the wreck" rather than implying any overlap.
  - `tests/verify_signature_alignment.py` gained scenario coverage for the initial state, real
    pointer interaction, keyboard interaction, the button alternative, insufficient/partial
    exploration correctly NOT triggering discovery, the fail-closed no-concealment path when a
    required element is missing, and the accessible status announcement.
- **Harness fidelity fix**: `harness/index.html` and `harness/experience-b.html` previously
  reproduced "Hidden in the Margins" with only 16 placeholder items under entirely different,
  non-matching class names (`fv-margin-strip__list`/`__viewport`/`__btn`) and inert, hidden control
  markup with no JS wired to it — a real preview-fidelity gap flagged by independent QD. Both
  harness files now use the exact real markup (same classes, all 72 real items, byte-identical to
  `homepage/page-6-home.blocks.html`) plus a faithful duplicate of the governed Margins Wire
  payload's own behavior (dynamically created prev/pause/next controls and position readout),
  instead of a hand-authored approximation.
- Restated the Alignment interaction's selector contract in `homepage/README.md` to include the
  four new real hooks (`[data-fv-align-reveal]`, `[data-fv-align-fact]`,
  `[data-fv-align-reveal-trigger]`, `[data-fv-align-status]`).

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
- **Independent QD review correction (same candidate, pre-merge):** an independent QD review of
  this candidate found two issues, both fixed in place before requesting fresh QD:
  - The homepage replacement had dropped the live `fv-focus-cta` section (the "Seven Day Focus
    Fieldbook" lead magnet linking to `/focus/`), which was added to the live site independently
    after this redesign's content was first captured. Re-verified directly against the live page
    (fetched 2026-10-29) and restored verbatim, in its live position, into
    `homepage/page-6-home.blocks.html` and both harness previews.
  - The Signature Alignment payload initialized the divider at 50%, inside the 45–55% "aligned"
    band, so the "Aligned" badge appeared on load before any user interaction, and
    `aria-valuetext` never updated as the divider moved. Fixed: the interaction now starts at 20%
    (outside the aligned band), `aria-valuetext` updates on every move to describe the current
    position, and `tests/verify_signature_alignment.py` gained a regression test asserting the
    initial state is not aligned and that alignment only follows real interaction. Payload bytes
    and SHA-256 were recomputed and repropagated to `final-vestige-site-layer.php` and
    `release-manifest.json`.

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
