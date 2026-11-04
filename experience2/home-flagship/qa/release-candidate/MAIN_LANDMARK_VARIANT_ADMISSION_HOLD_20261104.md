# EX2 isolated WordPress — HTML and ARIA main landmark admission (2026-11-04)

**RELEASE HOLD.** Stacked on PR #954 exact starting SHA `cf52429a1a94139270306625631a2299cbf2f20f`; all work confined to this independent QA branch. Frozen PR #49 and live WordPress page 6 are untouched.

## Concrete integration problem

The previous Playground candidate generator used Python `re.search(r"</?main(?:\\s|>)", embedded_body, re.I)`. Because the expression is a *raw string*, `\\s` is two slashes and the regex matches a literal backslash-s, **not HTML whitespace**. It detects only a literal `<main>` and misses `<main class="rogue">`, `<MAIN id="rogue">` and whitespace after a closing tag. More seriously, a nested `<div role="main">` has main-landmark semantics without using the `<main>` element, and the full-document browser gate counted only tag names. Thus variants of the same original #954 defect could be admitted as single-main.

## Minimal corrections (no visual or commercial changes)

1. Source compiler requires one exact standalone `<main>` opening and closing, substitutes them for the **isolated WordPress-only** embed, then rejects any remaining start/end main tag with whitespace/case/self-closing variants, plus explicit `role="main"`, single-quoted, and unquoted forms.
2. Full WordPress/Assembler document and nested-root admission now count `main,[role="main" i]`, preserving the parent theme-main containment check. CSS attribute selector `i` handles case-insensitive role values.
3. Eight adversarial source mutation cases and a benign `data-role` control are committed, along with strict browser-gate source-contract assertions.
4. Existing actual WordPress/Assembler test remains required: *these source changes do not establish a browser/axe or manual WCAG pass*.

## Reproducible before/after verification

With the old exact-source raw-regex, the eight HTML/ARIA mutations evade the source compiler's extra-main check. The corrected Python expression rejects all eight. The unchanged benign `data-role="main"` remains permitted; it is not an ARIA landmark. Browser selectors now count both native and explicit-role landmarks. Run `python -I -m unittest discover -s experience2/home-flagship/qa/release-candidate -p test_source_flagship_playground_candidate.py -v` and the existing complete-document axe source tests on **this exact head**. GitHub Actions currently fails before runner steps; until actual execution, record source/mutation preflight only.

## Scope, release and ownership

- **Offer:** existing free 52-page Focus Fieldbook.
- **Funnel:** source-backed investigation to contextual Focus CTA.
- **Blocker:** false passing accessibility admission from HTML/ARIA main duplicates.
- **Change / experiment:** fail-closed source + full-document DOM enforcement with adversarial controls.
- **Pass/fail evidence:** regex vulnerability reproduced; complete WordPress/Assembler browser execution, exact-head CI, measured Lighthouse/CWV, manual WCAG and independent QD remain unverified.
- **Owners:** Homepage engineering (this QA); Claude retains analytics/payments; Grok/Praxxis retain acquisition and independent review.

No WordPress production writes, staging install, publishing, merge, deployment, media rights signoff, affiliate activation, email or spending. A local WordPress Playground with the authentic Assembler theme remains necessary, and cannot establish WordPress.com/Jetpack parity.
