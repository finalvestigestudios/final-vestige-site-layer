# R29 — HTML parser and collapsed-content citation custody | HOLD

**Issue:** #136. **Branch:** `review/preparedness-browser-parser-visible-evidence-r29-20261031`. **Parent:** R28 `f52d1bdc33534d8c4167dece10711fce379137f6`.

## Real defect closed

R28's `HTMLParser.handle_startendtag` silently ignored non-void self-closing elements. This creates a browser/Python parsing differential: HTML '<div hidden/>Claim {{cite:id}}</div>' is **not** a self-closing `div` to the HTML browser parser. The slash is ignored and the following citation remains hidden, while the old Python guard would count it as normal visible text. R29 rejects any non-void self-closing element rather than pretending to have browser-equivalent HTML parsing. HTML void tags such as `<br/>` remain permitted.

R29 also conservatively refuses citation support hidden behind initially closed `<details>`, closed `<dialog>`, or a `[popover]`, even when the citation is inside a summary, and it protects default visibility against common inline CSS disguises: escaped CSS property/value keywords; `opacity:0` numeric variants; `color:transparent`; and `font-size:0` common units. A malformed or unparseable escape fails closed.

These are conservative structural guards. CSS classes, external stylesheets, media-specific/computed visibility, browser DOM repairs outside the guarded cases, and JavaScript-driven changes **are not proven by R29**. Human browser and source/claim review is not replaceable by these checks.

## Tested facts, not release approval

- New R29 module: **75 new synthetic tests** (`50` rejection, `19` acceptance, `6` contract tests); locally executed against the **exact Git blob** in this branch.
- Local reconstructed R25–R29 relevant modules: **335 tests passed, no skips/failures**. This is not a complete repository test execution.
- Python compile check passed for the new production and test files.
- Authenticated read-only GitHub scan of the 35 original article bodies and one water-planning tool body at this branch: **36/36 fetched**, **1,959 literal well-formed citation placeholders** (1,952 articles + 7 water tool); **no lexical occurrences** of the self-closing non-void / closed details-dialog / popover / inline concealment patterns screened. This is a preliminary lexical scan only, not execution of this Python parser on the actual GitHub corpus or a complete WordPress draft build.
- No original article text or metadata, source fragments/crosswalk, taxonomy, water planner, original reading-depth explanations, or safety states changed.

## Coordination and review requirements

All seven original Claude contributor ref heads must remain pinned to their independently verified 2026-10-31 SHAs. Independent safety QA PR #157 and food synthetic-fixture PR #169 remain **separate and unmerged**. Homepage PR #49 and flagship #254 were inspected and not modified. Never cherry-pick stale source text or override qualified reviewer findings.

**Full release state: HOLD.** Authenticated GitHub file reads are available, but local DNS still cannot resolve `github.com`, so no trusted full private checkout. The original `preparedness/tools/validate.py`, `build.py`, WordPress draft build, full 13-stage private preflight and repository-wide tests were not executed at this exact head. Hosted GitHub Actions has a runner-dispatch failure without executed steps in previously inspected runs; do not infer a PASS from workflow activation.

Still requires human review of 30 shared URL/crosswalk groups, 43 base-source fallback relationships, 1,959 individual citation occurrences and their claim scopes; qualified evaluation of consequential emergency/medical guidance; independent QD signoff on the exact final head. No source is deemed clinically or factually correct by these regex/HTML tests.

**Strict no-write boundary:** No WordPress/CMS writes, public publishing, live nav, homepage branch, safety approval or misleading QD PASS. `may_publish=false`.
