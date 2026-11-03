# R101 — PRIVATE HOLD: printable water-planner input-context repair CANDIDATE

Issue #136. **Never merge/publish** this draft without human source/citation checks, qualified emergency-water/medical review, actual browser print and no-JS/accessibility QA, and independent QD. No CMS, navigation, homepage or live WordPress writes permitted.

## Why this isolated engineering candidate exists

R100 proved a source-preservation/print-context concern in the original unmodified water-planner draft: its .pa-tool form holding **eight** household assumptions is hidden by print CSS, but its #wp-out calculated results sit outside the form. A printed total could be separated from the entered household size, days, stored-water estimate, heat adjustment, pets, clinician-dependent allowances or fill date. This candidate **does not assert** what browsers actually print, or that any water/medical guidance is safe or sufficient.

R101 **does not modify original files**. It starts by executing the complete R100 static form/source/citation gate and the R99 print CSS gate on the original authored source. After confirming status.publish=draft and safety_review.state=pending, it inserts a **candidate-only** printable assumptions summary beside the results *in memory*. The original content/citation tokens and source-reading scopes are left byte-for-byte intact. The existing builder then renders a WordPress-ready *private DRAFT* and a stand-alone HTML review preview. These are **never** published or imported automatically.

## Candidate behavior to independently check

The eight user-input fields appear in the same order as the original form. Their values are updated through input, change and beforeprint handlers; the script uses only .textContent, no .innerHTML or persistent/browser storage and no network calls. The summary mirrors the calculator's current numeric bounds and integer rounding, and flags adjusted values. A visible, review-pending statement explicitly warns that the figures are **not** personal/medical water recommendations. When JavaScript is off, the candidate prints an explicit "no calculation available" fallback, not a fabricated zero. The original body, sources, citations, pending safety record and caveats are preserved.

Screen CSS hides only the duplicate preview summary. Print CSS makes it visible with black text on white paper; neither rule changes the original .pa-tool behavior. Static CSS and JS inspection **cannot** substitute for real Chrome/Firefox/Safari print tests or accessibility review. The duplicated calculation normalization is itself a maintenance concern: a future change to water_planner.js must invalidate/review this candidate.

## Private use only

From the **R101 branch** and an unchanged checkout:

- python -I preparedness/tools/r101_water_print_context_private_candidate.py --inspect-only returns a deterministic SHA-256-sealed HOLD receipt without filesystem writes.
- python -I preparedness/tools/r101_water_print_context_private_candidate.py --out-dir /tmp/preparedness-r101-review creates exactly three **external scratch** files: a WordPress-ready DRAFT-only HTML candidate, a local stand-alone review HTML page, and a HOLD receipt. Output inside the repository is refused. **Do not import** these files into WordPress without explicit new approval after all quality gates.
- python -I -m unittest discover -s preparedness/tests -p 'test_r101_*.py' -v exercises real draft rendering, deterministic receipts, source/citation retention, malformed/duplicate/relabeled fields, changed source-use scopes, premature approval states, and a sandboxed Node mock of the actual input/change/beforeprint DOM behavior.

The exact-head private CI lane must also run the inherited R100 custody script (which invokes R93–R99 across **35 complete article drafts plus one real tool**), native validation, offline build and **all** Python tests. The mandatory 13-stage integrity pipeline is separate and remains unpassed until it runs successfully. The **41 historical reviewer packets** remain distinct from **36 actual WordPress-ready private drafts**; five proposed tools still lack body+metadata pairs. Keep all 30 shared-URL source collision groups, five historical contributor provenance discrepancies, 15 safety exceptions and 22 editorial decisions visible and unresolved until individually adjudicated.

## Human reviewer acceptance checklist

1. Verify complete original sources and each citation's **specific claim**, not just surviving URL/text; independently reconcile same-URL research variants and historical provenance before release.
2. Reproduce **Chrome, Firefox and Safari** print preview with defaults, 0 days, 14 days, altered heat, several pets, unprovided pet allowance, nonzero medical allowance, stored water above the total, an entered fill date, offline operation and JavaScript disabled. Confirm actual paper/PDF output retains both assumptions and calculated results; inspect the resulting printed page, not just CSS.
3. Check browser privacy: no browser storage, network requests, form submission or tracking of household inputs. Test keyboard, screen reader, 200%/400% zoom, narrow mobile, reduced motion and user-agent print overrides. Do not infer these from static inspection or a synthetic DOM mock.
4. Independently inspect any changed normalization, labelling, numeric constraints or medical caveat against the original calculator and current CDC/Ready.gov guidance. Qualified safety reviewer, independent QD and release approver must explicitly sign off.
5. **HOLD** if any evidence, context, source, citation, visibility, prior QA state or calculation differs; record exact SHAs and tests in Issue #136. Do not merge, publish, edit WP navigation or CMS, or announce safety approval.
