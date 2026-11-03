# R96 — Visible Source and Safety-Review Shell Custody (PRIVATE HOLD)

**Owner:** Preparedness Archive integration/source safety, Issue #136.  
**Branch:** \`review/preparedness-r96-visible-source-safety-shell-hold-20261103\`  
**Immutable base:** R95 \`b279629f4567bb18d843652bcfde5fdb2795f07a\`.  
**Scope:** four ADD-only files (new gate, isolated test battery, this protocol, private CI). No existing article, research, source registry, source URL, taxonomy, homepage, theme, navigation, CMS, or WordPress edit. No publication permission.

## Specific gap covered

R93 binds 1,959 literal citations to source IDs, original source URLs, exact numbered references, and author-scoped reading uses in 36 actually buildable draft bodies. R94 audits 4,032 original text blocks, including the original authored warning words. R95 protects the entire authored HTML DOM and its 136 original hyperlinks. **However, those three gates do not completely cover the builder-generated outer shell**—particularly the *Sources and verification* section, *Review record*, *Draft: not public* status chips, and the contents of inserted \`<sup class="pa-cite">\` markers.

The R93 matcher checks marker contents and source metadata, but preservation of text by itself is insufficient: a source or safety notice might remain in the HTML while its container is \`hidden\`, \`inert\`, \`aria-hidden\`, or styled invisible. R95 deliberately skips builder-inserted citation superstructures. R96 independently checks these previously uncovered boundaries while preserving all upstream evidence.

## Fail-closed invariants

- Exactly one rendered article, whose \`data-slug\` matches the original article, with one semantic \`header.pa-head\`, \`div.pa-body\`, \`section.pa-sources\`, and \`section.pa-review\`. Fail for duplicate, absent, misnested, or misleading duplicate HTML attributes.
- All head/source/review text and citation superstructures must be structurally visible in the static HTML and exposed to the accessibility tree. Fail on \`hidden\`, \`inert\`, \`aria-hidden=true\`, forbidden inline style patterns, \`role=presentation/none\`, unsafe scripts/forms/iframes/templates, or foreign event handlers in critical regions.
- The *only* allowed event-bearing critical-shell element is the original exact local print button, \`onclick="window.print()"\`, and **only** under the original \`.pa-printbar\`. Added handlers or attributes fail.
- Every inserted \`pa-cite\` must contain **only one direct anchor**, with the exact inline original source rank, \`#src-N\` destination, accessible label and \`[N]\` text. No child HTML, extra anchor, hidden tag, on-click action, or unattributed text is permitted.
- Every source row must have one direct, \`rel=noopener\` HTTPS anchor preserving original contributor source ID, URL, title and unabridged \`Used for:\` reading scope, plus its original human-link-check state. Source URLs shared by independent records are **never merged, approved or de-duplicated**.
- The entire visible review record, explicit draft warning, and any existing \`pending\` safety notice must remain legible and not be removed or reclassified. Review status metadata is **not** proof of qualification, current accuracy, or external approval.
- Run R95, R94 and R93 independently on the same in-memory corpus, then fail if R96 disagrees on article/tool counts or citation occurrences.
- Every report and every per-article row remains \`HOLD\`, \`may_publish=false\`, \`NOT_REVIEWED\`, with a SHA-256 canonical JSON evidence seal.

## Execution, coverage, and limitations

\`\`\`sh
python -I -m unittest discover -s preparedness/tests -p test_r96_visible_source_safety_shell.py -v
python -I preparedness/tools/r96_visible_source_safety_shell.py
python -I preparedness/tools/r96_visible_source_safety_shell.py --private-json-stdout > /tmp/r96-private-report.json
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
\`\`\`

The tests are synthetic, mutation-driven, and never write into the shared repository or source-fragment directory. The builder writes only private offline draft files under \`preparedness/build/\`. The R96 gate itself is read-only. Hosted PR-specific CI is additive: it must not supplant or bypass the existing mandatory 13-stage integrity workflow.

**Limits:** Static HTML inspection does not compute CSS layout, media-query behavior, browser accessibility, external link reachability, source credibility, validity of a claim, or the safety of any medical or emergency instruction. Hiding content through an external stylesheet may not be caught; actual WordPress/desktop/mobile/print screen-reader review remains mandatory. The unchanged source claims and historical practices remain **unapproved**.

## Current integration inventory and coordination

The exact R95 parent retains **35 article drafts and one real tool draft**, six tools planned in total, five tools unbuilt and **not importable**. It protects 1,959 currently rendered citation occurrences; the distinct older four-stage reviewer corpus preserves 2,173 historical citation occurrences and 41 historical packets. Do not claim 41 current WordPress-ready pages. Seven Claude contributor branch references and the release candidate are pinned in the private workflow, not fast-forwarded or merged into R96.

QA PR #157 is a separate unmerged Start Here wording/taxonomy fix requiring human safety adjudication. Food synthetic-fixture PR #169 is a separate draft; its \`_dup_test.json\` scenario still writes in the shared repository working tree and remains a concurrency risk. R92 PR #766 is a separate unmerged shared-URL identity docket with a documented unresolved historical/current citation mismatch. Homepage PR #49 and flagship homepage PR #604 are off-limits.

**Hard blockers:** Mandatory 13-stage integrity pipeline still incomplete; five contributor provenance differences; 30 original source-URL collision groups; 15 safety exceptions; 22 editorial decisions; independent source and human-link review; qualified emergency-safety review; real browser/WordPress accessibility testing; independent QD determination. No artificial approval, blanket source verification, or declaration that advice is medically safe.

**Release: HOLD.** Do not merge or import to WordPress. Do not write CMS/page 6/navigation or publish anything. Engineering success is only a private transport-integrity diagnostic.
