# R99 — Original print CSS baseline repair and conditional-media source custody

**Private engineering only. Issue #136.** Descendant of R98 exact parent `4f3de05d05e40fe06bf2e1ab68b1b04556fb4378`. No WordPress, navigation, CMS, homepage, public or original editorial/research changes. **HOLD / NOT REVIEWED / may_publish=false.**

## Verified code defect in R98 predecessor (before R99)

The **actual existing** `preparedness/assets/preparedness.css` contains FIVE scoped decorative heading pseudo-elements using `display: none`: `.pa-act h2::before`, `.pa-verdict-head h2::before`, `.pa-sources h2::before`, `.pa-review h2::before`, `.pa-related h2::before`. R98's original nonprint allowlist contained only `.pa-card[hidden]` and `.pa-empty[hidden]`. Thus `audit_stylesheet(lib.css)` would raise `Hold` on an unchanged baseline before it could certify its own CSS custody. Earlier R98 Actions runs failed **before any step execution** and did not expose this. This is a direct static source/code contradiction, not a successful test run or a qualified safety finding.

R99 adds ONLY those five **exact** non-print decorative pseudo-selector exceptions. The sources heading, review heading, warning bodies, citations and all print selectors remain protected. No broad `::before` / `display:none` bypass is permitted. Exemptions are explicitly listed in the machine HOLD receipt as non-safety approvals.

## Additional fail-closed hardening

- Print URL `content` must be the canonical literal `" (" attr(href) ")"`. A forged “verified” / “official” claim cannot be introduced through CSS pseudo-content while retaining `attr(href)`.
- Printed link annotation and required ink-on-paper proofs must occur in an unconditional `@media print` path. An apparent print rule nested under `@media screen`, width/media preference or a `@container` is **not proof** it will print.
- Restrict selector scope to a leading `.pa`-class and fail closed for relational/functional selector patterns pending human audit; merely mentioning `.pa` somewhere in a global selector is insufficient isolation.
- Reject dark/opaque/custom print backgrounds that could obscure required black source/warning text despite an earlier valid print palette declaration. Allow only already-used transparent/white/none backgrounds.
- Extend additive synthetic tests with exact decorative-positive, all-others-negative, nested non-print, selector-scope, print-background and citation-content spoofing mutations. No tests write source fragments into a shared worktree. PR #169's sandbox isolation is preserved as a separate unmerged review.

## Verification and release

Run on a trusted exact checkout:
```sh
python -I -m unittest discover -s preparedness/tests -p test_r98_print_source_visibility_custody.py -v
python -I preparedness/tools/r98_print_source_visibility_custody.py --private-json-stdout
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

A green suite is **not** an actual browser print review, source factual check, claim-level support review, medically qualified assessment, independent QD PASS, mandatory release-integrity PASS, or permission to publish. This private branch changes two R98 engineering files and adds this protocol plus a dedicated exact-head CI workflow; it does NOT edit the original CSS itself. Original 35-article + one real buildable tool distinction, 1,959 rendered citations and source-evidence records continue to be handled by the R93–R98 custody chain.

**Open safety/release blockers:** 5 historical contributor-provenance discrepancies, 30 URL collision groups, 15 safety exceptions, 22 editorial decisions, five planned tools without WordPress-ready files, actual browser/print water-planner exception, qualified water/food/medication/hazard review, independent source/citation checks and QD. CI Actions may still fail before runner dispatch. All remain HARD HOLD.