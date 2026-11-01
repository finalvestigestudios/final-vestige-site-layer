# R43 — Private offline article/source review desk | ISSUE #136 | RELEASE HOLD

**Status: MACHINE EVIDENCE PRESENTATION ONLY — NOT editorial, QD, or emergency/medical safety clearance.** Never publish these pages, their source URLs or the 35 articles, never add a public nav link, and never write to WordPress/CMS. This PR changes only the private Preparedness evidence gate, tests and documentation.

## What changed

The existing R42 fingerprints, R37 original reviewer worksheets, 36 separate article/tool dossiers, all 1,959 individual citation contexts, 367 distinct contributor-specific article–source reading scopes, 43 cross-cluster fallbacks and 30 repeated-URL groups remain authoritative. No URLs are merged merely because the string matches, and original source notes / reading depth are not shortened.

The R43 reviewer_offline_html_gate.py creates **38 inert HTML strings** from those *already frozen* inputs: one index, 36 individual articles/tool dossier pages, and one global cited/uncited shared-URL review page. It uses Python html.escape for all dynamic source text (including original HTML-looking text), a restrictive CSP, local-only relative navigation links, no external links/scripts/fonts/images and no HTTP calls. Reviewers see original records and article-specific scope claims as plain text rather than active source markup.

A deterministic SHA256 manifest covers every page's full UTF-8 content and byte count. Release/identity/safety/QD flags remain **false**. The mandatory 13th private validation stage now checks the entire 38-page in-memory output on the real 35+1 corpus, without saving a site or making any public change.

## How to check safely

On a trusted exact checkout of this **draft** PR:

    python -I preparedness/tools/validate.py
    python -I preparedness/tools/build.py
    python -I -m unittest discover -s preparedness/tests -v
    python -I preparedness/tools/citation_fallback_review_gate.py

The optional private Python API is build_offline_html(frozen_R42_dossier, trusted_r42_sha256=INDEPENDENTLY_PINNED_SHA); it **returns** a dict containing html_files and manifest, and never writes. Do not use the supplied packet's own fingerprint as independent trust evidence: that is a **consistency check only**. Stage-13 passes the trusted upstream R42 packet built from earlier frozen gates; independent reviewers require a separately controlled trust anchor.

## Known limitations / mandatory human blockers

- Machine-export integrity does **not** verify whether an external source is accessible or factual, whether historical methods are safe, whether advice is medically appropriate, or whether a claim is supported.
- The generated HTML is a **review aid, not WordPress-ready public editorial copy**. The original 35-article private WordPress-ready drafts remain untouched and held.
- Real human checks are still NOT_STARTED; perform independent verification for 1,959 citation occurrences, 367 reading scopes, 43 fallbacks, and 30 shared URL groups (including uncited variants).
- All consequential water treatment, canning/food storage, combustion/fire, and medication/medical-device claims need qualified human assessment before release.
- Independent QA PR #157 and synthetic-fixture PR #169 remain unmerged; their reviews do not imply a QD PASS. No rendered-browser QA or independent QD approval has occurred.

**Never treat a successful Python test suite, presence of safety metadata such as safety-approved-draft, or a fingerprint match as publication authorization.**
