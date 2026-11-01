# R46 — Private reviewer DOM scaffold and source-text anti-spoofing

**Issue #136 · Release state: HOLD · Unpublished engineering draft.**

R45 verified the **tags**, static stylesheet, CSP and link destinations of the
38 private R43 reviewer pages packaged by R44. Those necessary checks were not
sufficient to prove that an actual HTML browser would display the hold notice
or navigation in the intended places. Python's HTMLParser does not perform
browser tree repair. A page could contain one syntactically valid HOLD warning
nested inside the HTML head, or a correct back-link moved into a source citation
record. It might pass the original R45 tag census while a browser hides, moves,
or reinterprets the structure.

R46 closes that concrete machine-verifiable gap **without rewriting any
research evidence**:

1. Freeze the exact R43 parent-child grammar for head, body, main, section,
   source-reading tables, evidence paragraphs, and local navigation. Reject
   browser-repairable malformed nesting even when every element is allowlisted.
2. Require the exact head order: UTF-8 charset, restrictive CSP, title, inert
   stylesheet. Require the direct-body order: article title, prominently
   marked **PRIVATE / UNVERIFIED / HOLD** paragraph, optional private return
   link, and complete main evidence body. The warning can no longer be hidden
   in the head or moved to an evidence row or to the end of the page.
3. Bind each anchor to its exact local role, not merely its URL:
   article/tool/global-source return links must be in the body return
   paragraph; index article links belong to the article list; the global
   shared-source link belongs to its index paragraph. Existing R45 exact-link
   counts, 38-page census and R42/R43/R44 provenance checks remain intact.
4. Reject invisible C0/C1 control characters, HTML-decoded bidi overrides,
   bidi isolates and selected invisible formatting characters in any printed
   source evidence, title or warning. The program **fails closed**; it does
   not delete, normalize, sanitize, abbreviate, or substitute the original
   words, source URLs, reviewer notes, research depth, or historical context.
   Normal tab/newline/CR layout whitespace and ordinary multilingual text are
   preserved.
5. Add individually named native Python negative regression cases for
   misplaced warnings, hidden/off-body content, misplaced source links,
   reordered head structures, malformed citation row nesting, direct and
   HTML-entity-encoded bidi spoofing, and C0/C1 controls. Synthetic fixtures
   are isolated and do not alter original contributor files.

The **existing required R45 audit is already invoked by stage 13**, so this
hardening is exercised by native private preflight without creating a new
optional or bypassable validation path.

Run on the exact working tree/PR merge SHA:

~~~bash
python -I -B preparedness/tools/validate.py
python -I -B preparedness/tools/build.py
python -I -B -m unittest discover -s preparedness/tests -v
~~~

Machine green confirms internal evidence-custody constraints, **not**
independent source accuracy, current live links, human source reading,
qualified safety review, receipt-ledger trust, rendered-browser QA, or
independent QD PASS. Source-warning text is verified structurally; full
screen-reader and print behavior must still be checked in real browsers.

The frozen slate remains **35 article drafts + one water planning tool**,
with **1,959 citation occurrences**, **367 original reading-scope
relationships**, **43 cross-cluster fallback relationships**, and **30
shared-URL groups**, including uncited source variants. The seven contributor
branches are never altered by this work.

**Release HOLD remains absolute.** No public publishing, WordPress/CMS
writes, public navigation, branch merging, source reclassification, medical
safety certification, or human/QD approval.
