# EX2 native staging redirect-boundary regression — November 8, 2026

Parent: draft PR #1639 at exact SHA `940bb82e9177181b6d14de219f290c482c416d32`. Frozen PR #49 unchanged. No production WordPress edits or deployment.

## Demonstrated failure and correction

The prior `verify_native_playground.py` used `urllib.request.urlopen` directly for its three WordPress preflight requests. Python's default HTTP redirect handler follows HTTP 301/302/307/308, including redirects from a caller-supplied loopback staging hostname to an arbitrary external host. Thus the old preflight did not uphold its claim that every fetch was strictly isolated. In browser tests a local homepage can similarly redirect into a public site unless external top-level navigation is explicitly intercepted.

The corrected verifier supplies `RefuseRedirects` to the preflight opener and rejects every HTTP redirect. The native browser route gate refuses cross-origin **top-level navigation** and non-GET/HEAD/OPTIONS requests, but permits read-only external archive image GETs for separate transfer evidence; this is **not** a license or media-transfer approval. Production and external **origin inputs** remain prohibited.

## Tests, provenance and limitations

The exact new code has a self-test with 18 negative-control assertions: 6 prohibited origins, 4 approved local origins, 3 fake WordPress endpoint checks, and 5 redirect-fence checks (301, 302, 307, 308 plus zero requests reaching the second server). This self-test uses ephemeral loopback HTTP servers and does not contact the public site.

Run: `python experience2/review/native-playground/verify_native_playground.py --self-test`.

When a **real, separately authorized, disposable WordPress Playground** is available with the pinned Assembler theme and an actual local review page, run `python experience2/review/native-playground/verify_native_playground.py --origin http://127.0.0.1:9400 --axe-js /path/to/axe.min.js --out native-evidence`. The private PR #1626 Blueprint ZIP is required; the repository does not store that ZIP. WordPress Playground CLI supports `npx @wp-playground/cli server --blueprint=./private-bundle.zip --port=9400`; installing the CLI is a separate machine prerequisite, not permission to modify the live CMS.

Native WordPress acceptance remains **UNEXECUTED** here: WordPress Core, Assembler, Playground CLI and axe-core are not installed and this runner environment has no outbound package retrieval. No results for actual archival image bytes, final rights, axe/WCAG 2.2 AA, 200% zoom, measured Lighthouse/CWV, live Jetpack, or independently confirmed sales are claimed. Current origin protections do not prove a sandboxed browser cannot load read-only external images or scripts; a full network-destination review is still required before release.

**Conversion-first:** Offer = existing free 52-page Focus Fieldbook; step = private archive-to-Focus journey; blocker = reviewer could be redirected outside isolated staging; change = strict preflight/browser navigation fences; evidence = local redirect regressions; owner = interim homepage QA (Claude owns production Jetpack/attribution; Grok/Praxxis social distribution). No subscribed leads or revenue verified.

**Release: HOLD.** CI/QD, WordPress Core/Assembler staging, real media transfers and rights, accessibility, Lighthouse, Jetpack correction and founder approval remain mandatory.