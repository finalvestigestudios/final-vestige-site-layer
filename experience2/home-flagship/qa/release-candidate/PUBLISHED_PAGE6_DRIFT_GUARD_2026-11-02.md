# Published page 6 versus rights-safe source — read-only release gate

**2026-11-02, evening Pacific | DRAFT/HOLD | No production changes.**

## A previously unknown publication state is now observable

Two independent authorized WordPress.com **read-only** requests, edit/raw and view, returned **page 6 in `publish` status** with WordPress `modified` field `2026-11-02T17:48:13`. The raw Gutenberg document contains the Experience 2.0 seven-chapter flagship, not merely the previous homepage hero. We do **not** have evidence identifying who authorized the change; do not claim it was unauthorized. Do not automatically revert a real published revision or overwrite subsequent edits.

There is one accessible production site, ID **256784396**, and **no native staging clone**; the site's WordPress.com Personal plan does not provide a Business/Commerce staging clone. The `wpcomstaging.com` alternate address is not a separate testing site.

Read-only WordPress source findings:

| Gate | Published page 6 | Known rights-safe source candidate |
| --- | --- | --- |
| Published status | `publish` | draft Git source only |
| WordPress local modified field | `2026-11-02T17:48:13` | n/a |
| Gutenberg raw content | 150,727 characters | 112,330-character proposed HTML block |
| Flagship HTML block | exists, ~107,978 characters including Gutenberg wrappers | single candidate block |
| Hidden in the Margins | exactly 72 `fv-margin-strip__item` spans | protected outside replacement |
| Jetpack signup | one native `wp:jetpack/subscriptions` marker | protected outside replacement |
| Seven Day Focus Fieldbook | contextual `/focus/` link plus independent CTA link | preserved |
| NYPL map reproduction | **YES:** `<img src=https://i0.wp.com/.../edit-017-v02-nypl-5003296-original.jpg?fit=1024...>` | **NO** map image fetch URL; source/catalog links retained |
| Apollo / Franklin pictures | present | present, including the no-JS safeguards |
| Exact production/candidate parity | **NO** | cannot treat live as qualified candidate |

The existing live page's claim that NYPL *believes* the item is US-public-domain does not substitute for Final Vestige's image-specific review. This is an **unresolved internal image-reuse approval gate**, not a legal determination that an infringement occurred. The catalog citation should remain available even if reproduction is removed.

**Do not infer from metadata or raw markup that anonymous users successfully fetch any image.** Anonymous network/media and production mobile measurements have not been reverified for this revision.

## Engineering control delivered

`audit_published_homepage.py` is an isolated, completely offline/no-CMS-write gate. It requires a *local* raw WordPress page JSON export (not HTML rendered from the public API) and the source-controlled candidate, rejects any page other than published ID 6, and records only SHA-256 digests, counts, revision time and Boolean guards. It explicitly checks:

- exactly 72 Margins spans, one native Jetpack subscription block and at least two `/focus/` anchors;
- exactly one flagship HTML block and strict text equality with the candidate;
- captured or emitted NYPL map reproduction through `img`, `source`, `srcset`, `data-srcset`, or CSS `url()`, including HTML entity and URL-encoded aliases; **catalog links do not count as reproduction**;
- expected WordPress modified-field pin when supplied;
- a perpetual `release_decision: HOLD` even if all automatic tests pass.

Exit code 0 means all **mechanical checks** pass, **not** permission to deploy; 1 means a release blocker, 2 means invalid/unreadable input. Example, from the repository root:

```bash
python -m unittest discover -s experience2/home-flagship/qa/release-candidate -p test_audit_published_homepage.py -v
python experience2/home-flagship/qa/release-candidate/audit_published_homepage.py \
  --wp-page-json /private/local/page6-raw-only.json \
  --candidate experience2/home-flagship/qa/release-candidate/fixtures/proposed-production-block-pr604.html \
  --expected-modified 2026-11-02T17:48:13
```

**Never commit/upload the raw WordPress response**, bearer tokens, subscriber list, production DB or private preview credentials. Export only the local `data` page object, not the whole user account. The test code uses synthetic data. Eleven adversarial tests passed locally for the pre-commit implementation; CI must independently run them on the exact new PR SHA before merge.

## Release adjudication

1. Freeze additional production writes/merges/rollback pending founder authorization and an actual production readback. Preserve revision 1914 and any later revisions; never blindly restore revision 1899.
2. Confirm image-specific rights/reuse and whether the live NYPL `<img>` should remain. Prefer the existing rights-safe candidate if permission is not documented; this requires a separately approved WordPress edit with fresh backup, guarded page readback and post-save confirmation.
3. Reconcile WordPress.com hosted output and actual anonymous image bytes, five breakpoints, 200% zoom, manual WCAG 2.2 AA keyboard/screen-reader/physical-device behavior, and measured LCP/CLS/INP. Do not treat disposable WordPress/Assembler lab as hosted certification.
4. Keep #49 frozen, #713 ABBA performance diagnostic independent, #158 Apollo component research and #171 Mind/editorial work separate. No additional chapters, affiliate URLs or new subscriptions.
5. Require independent QD, image-rights approval, founder exact release authorization and an auditable rollback manifest before any publication.

**No WordPress post/page/theme/navigation/settings changes, branch merges or deployments occurred in creating this gate.**
