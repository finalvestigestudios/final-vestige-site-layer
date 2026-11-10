# EX2 / Page 6 native Focus attribute custody — 2026-11-10

**Release HOLD.** Source-only admission change; no WordPress edits, merge, deployment, tracking, Jetpack subscriber action, spending, or affiliate activation.

## Reproduced defect (before fix)

The previous `native_focus_action` regex used `\\bhref=` and a greedy `[^>]*`. As a result, this synthetic HTML **passed** the preservation gate as `/focus/`, even though the actual browser would navigate elsewhere:

```html
<section class="fv-focus-cta">
  <a class="fv-focus-cta__button" href="https://unapproved.invalid/path" data-href="/focus/">Get Fieldbook</a>
</section>
```

A `javascript:` href with a trailing `data-href="/focus/"` also passed. Separately, `data-class` could impersonate a native class attribute. This is a test-admission bypass, **not evidence that the published WordPress site was compromised**.

## Corrected behavior

Only exact `class` and `href` attributes parsed by Python's standard `HTMLParser` can qualify the preserved Page 6 native Focus button. Duplicate attributes and inline event handlers on the button are rejected. Both the actual root-relative `/focus/` destination and exact canonical `https://finalvestige.com/focus/` still pass. All other destinations, duplicates and missing controls fail closed.

## Evidence and scope

- Fresh authenticated read-only WordPress Page 6 editor content (modified 2026-11-05) still shows the preserved native button as `class="fv-focus-cta__button" href="/focus/"`. All 72 Margins items, Jetpack block and 52-page Fieldbook content are outside the proposed seven-chapter replacement boundary.
- Local source-equivalent `unittest`: 39/39 passing (23 inherited composer tests + 16 focused new tests).
- Local Chromium real DOM proof: 12 comparisons at 390/1440 CSS px, real DOM `href` vs old and corrected gate; two spoof types reproduced and rejected after correction. Synthetic HTML; never navigated to unapproved URLs.
- The 11 archived seven-chapter assets (Franklin, Apollo 1, NYPL) and three art directions were not modified. All historical image rights checks remain distinct and **not approved**.
- Current WordPress.com plan is Personal, so no native staging clone. PHP CLI here lacks WordPress runtime/database extensions, and this sandbox cannot fetch WordPress code. An isolated free WordPress Playground/Assembler runtime is still necessary.
- **NOT TESTED:** real WordPress/Assembler render, hosted Jetpack confirmation/delivery, actual image transfers, automated axe, complete WCAG 2.2 AA, native zoom, Safari, Lighthouse/CWV, independent exact-HEAD CI/QD.
- Conversion outcome unknown: no verified lead, purchase, affiliate payout or net revenue. No new tracking instrumentation.

## Reproduce

```sh
python -m unittest discover -s tests/experience-2 -p test_native_focus_attribute_custody.py -v
python -m unittest discover -s tests/experience-2 -p test_compose_page6_flagship.py -v
```

Always compare the **exact full candidate commit SHA** and conduct separately authorized isolated WordPress acceptance before any release. Frozen PR #49 and existing production Page 6 must remain untouched.

## Ownership / next gate

Interim homepage engineering: exact-source integration and fail-closed QA. Claude: WordPress/analytics production engineering. Grok/Praxxis: source-linked social asset IDs and campaign handoff per Issue #820; no new homepage instrumentation. Founder: release/art-direction decision.

**Offer → Funnel step → Blocker → Change → Evidence → Owner:** Seven Day Focus Fieldbook → historic evidence to native Focus action → parser could falsely accept a hijacked CTA → native HTML attribute parser → local 39 regression tests + 12 real Chromium DOM comparisons, NOT staging → interim engineering. No proven commercial conversion lift.
