# The Preparedness Archive (Issue #136)

Source, build and governance tooling for `finalvestige.com/preparedness/`. Nothing in this directory publishes anything. It produces WordPress block markup for **draft** pages and local preview pages for QA.

## Layout

| Path | Purpose |
|---|---|
| `taxonomy.json` | Sections, tracks, the 35-topic slate (with internal status) and the free-tool list |
| `sources/register.json` | Every source: URL, publisher, published/updated/reviewed dates, `verified_on`, what it supports. Unverified entries cannot be cited |
| `content/articles/<slug>.meta.json` + `.body.html` | One article. Body tokens: `{{cite:source-id}}`, `{{link:slug\|label}}` |
| `assets/preparedness.css` | All styles, scoped under `.pa` so the live theme is unaffected |
| `tools/build.py` | Builds `build/wp/*.html` (one `wp:html` block each) and `build/preview/*.html` |
| `tools/validate.py` | Editorial, safety-governance and WCAG-contrast gates |
| `tests/test_preparedness.py` | 18 offline tests, including the governance gates and the pinned CDC bleach table |
| `docs/` | Safety-review checklist, QA log |

## Commands (from the repo root)

```bash
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py            # add --public to list only published guides on the landing page
python -I -m unittest discover -s preparedness/tests -v
```

## Governance rules enforced in code

* A guide cannot cite a source whose `verified_on` is null, or an external link that is not in the register.
* A slate item marked `gate: true` cannot be `published` without `safety_review.state == "approved"` plus a named reviewer and date. Nothing is published today.
* A history guide must carry a safety-verdict panel, a primary or museum source, and a modern regulator or extension source.
* The landing page lists only articles that exist. Sections with no articles are not rendered. Unwritten slate titles never appear on a public page.
* Internal links to unbuilt articles degrade to plain text, never to a dead link.

## Adding an article

1. Add or confirm its row in `taxonomy.json`.
2. Verify its sources and add them to `sources/register.json` with `verified_on` and `supports`.
3. Write `content/articles/<slug>.meta.json` and `.body.html`, cite with tokens.
4. Run the validator, build, tests. Request human safety review if `gate` is true.
5. Only after review is recorded: set `status.publish` to `published`.

## What is not in this directory yet

Section hub pages, Start Here, the interactive tools, printable PDFs, and images (no image rights have been cleared). See the worklog on Issue #136.
