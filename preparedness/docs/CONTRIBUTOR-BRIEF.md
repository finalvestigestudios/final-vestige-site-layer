# Contributor brief: Preparedness Archive research and drafting sessions

You are one of several parallel sessions building articles for the Final Vestige Preparedness Archive (Issue #136 in `finalvestigestudios/final-vestige-site-layer`). Read `preparedness/README.md` first, then `preparedness/content/articles/making-water-safer.*` and `salt-beef-salt-pork-age-of-sail.*` as models of voice, labeling and structure. Match them.

## Goal
The most robust, most trustworthy public library on household preparedness and historically documented "old ways" on any website. Quality and verifiability over count. Warm, composed, resourceful, plainly human prose. Preparedness without panic; history without mythology.

## Hard rules (non-negotiable)
1. **Verify every source yourself.** Fetch the live page (Firecrawl `firecrawl_scrape`, `maxAge: 0`), read it, and record it. Never cite a page you did not read. Never fabricate a citation, quotation, experiment, firsthand experience, expert approval, statistic or date. If a source is silent, say it is silent. If official sources disagree, say so on the page and flag it for the reviewer.
2. **Prefer** FEMA/Ready.gov, CDC, USDA/FSIS, NCHFP and university Extension, NOAA/NWS, USFA, EPA, NPS, Library of Congress, Smithsonian, Royal Museums Greenwich, archives and primary documents, with museum or scholarly secondary sources for history. Three or more checked sources per article, at least one modern regulator/extension source for anything actionable, and at least one primary or museum/archive source for every history piece. No blogs, forums, survival-site summaries or AI summaries as evidence.
3. **Never invent** curing formulas or ratios, shelf-stability claims, meat-processing temperatures or times, water-treatment quantities, medical instructions, fuel/generator practices or numbers. Reproduce current official figures only with their context and caveats, or link out. History pieces contain **no** actionable recipe or quantity and end with a modern safety verdict panel.
4. **Label statements**: `pa-tag--fact` (official guidance), `pa-tag--doc` (documented history), `pa-tag--unc` (uncertain), `pa-tag--ed` (editor's reasoning, ours, not the source's).
5. **Safety gate.** Every article whose taxonomy row has `"gate": true` (water, food preservation, combustion, medicine, fire, shelter/evacuation, pemmican/curing, fermentation, cisterns, fire-making, purification) must have `"safety_review": {"state": "pending", ...}`. You may NOT mark any article `approved` and may NOT set `status.publish` to `published`. Only the founder approves, in chat, via the lead session.
6. **Do not touch** WordPress (no wpcom writes at all), navigation, the homepage, `/focus/`, PR #49, the GitHub issue, `production`/`main`, other contributors' files, approved articles (`making-water-safer`, `salt-beef-salt-pork-age-of-sail`), `taxonomy.json` or `sources/register.json`. Propose changes to approved text in `docs/REVISION-QUEUE.md` under a new heading instead.
7. **Images:** use none unless the rights are unambiguously public domain or open-licensed and you record the license, credit and alt text. When unsure, use no image.
8. **Indigenous knowledge:** attribute accurately and respectfully, name the peoples and the sources, and do not generalize. If you cannot support attribution from a reliable source, say so.

## Files you own and create
* `preparedness/content/articles/<slug>.meta.json` and `<slug>.body.html` for **your assigned slate items only** (slugs are fixed in `taxonomy.json`). Meta fields follow the existing articles (`n`, `slug`, `title`, `h1`, `dek`, `description` <=165 chars, `section`, `track`, `tags`, `updated`, `last_checked`, `recheck`, `status`, `safety_review`, `related`, `source_use`). Use `{{cite:id}}` and `{{link:slug|label}}`.
* `preparedness/sources/fragments/<your-cluster>.json`: every source you verified, same shape as `register.json` entries (`id, title, publisher, kind, url, published, updated, reviewed, verified_on` (today, YYYY-MM-DD), `human_link_check: false`, `supports`, optional `notes`). Ids must be globally unique. `register.json` contains *placeholder* entries (`verified_on: null`) for sources the issue listed: you may NOT cite a placeholder as is. After reading the page, **redefine it in your fragment with the same id** (that upgrades it), or use a new id prefixed with your cluster name. Entries already verified in `register.json` may be cited by id and must never be redefined. Kinds (validated): `regulator, extension, nonprofit, professional-body, museum, museum-study, museum-object, archive, primary-digitized, scholarship, journal`. The American Red Cross, AHA and similar bodies are `nonprofit`/`professional-body`, never `regulator`.
* `preparedness/docs/CLUSTER-<name>.md`: a short notes file: what you verified, source disagreements, claims you could NOT verify, items for the human safety reviewer (same table format as `SAFETY-REVIEW-CHECKLIST.md` section C).

## Quality bar (validator enforces much of it)
* 1,800+ words of real substance per article. No padding, no filler paragraphs, no generic listicles. Depth: what to do now (action box), why, the evidence, limits, what we do not know, then sources.
* Modern pieces: "What to do now" box first, emergency-services pointer, options for budget/disability/renters where the topic calls for it. History pieces: documented practice, how it worked, what the record supports, where it failed, and a modern safety verdict (`validated`, `context-dependent`, `not-validated`, `unsafe`), plus a Then/Now panel.
* Internal links via `{{link:slug|label}}`; never link an unbuilt article. Related guides listed in meta.
* Accessibility: tables need `<caption>` and `scope="col"`, wrapped in the `pa-tablewrap` region with `tabindex="0"` and `aria-label`; labelled divs need `role`.

## Run before every commit (from the repo root)
```
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests
```
All must pass. Fix validator errors by improving the article, never by weakening the validator. Do not edit `tools/`, `tests/` or `assets/` (shared). If you need a new component or a tool change, write it up in your cluster notes for the lead.

## Git
Work on your own branch (your worktree provides one). Commit your files only. Push your branch to `origin` (do not push to or merge into `feature/preparedness-archive-v1`, `main` or `production`). End commit messages with `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.

## Report back
End with: articles drafted (slug, words, sources), sources verified, source disagreements found, what you could not verify, items for the safety reviewer, and your branch name and head SHA. State plainly anything unfinished. Do not claim an article is "done" beyond "drafted, awaiting human review".

## QD lessons (added 2026-10-30 after the first independent review)
* A fetched page is not a fully read page. If a source is a long PDF or you read only part of it, say exactly how much you read in the register `notes`.
* Where an older and a newer official document differ (for example the 2020 FEMA guide vs the Dec 2023 FEMA power-outage fact sheet), use the newer, and state the difference. Never tell readers to discard, stop or skip prescribed medication; defer to the prescriber or pharmacist.
* Do not recommend rehearsals or tests that interrupt life-safety equipment (for example switching off a household's main power). Simulate with nonessential items.
* Do not infer legal duties or eligibility rules from a template or a secondary summary; verify against the binding source or say it is unverified.
* Do not commit `preparedness/build/` (git-ignored).
