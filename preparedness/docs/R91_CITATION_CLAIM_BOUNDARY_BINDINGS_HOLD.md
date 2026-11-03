# R91 — Literal citation-to-historical-claim-boundary custody — PRIVATE HOLD

**Issue #136**. Branch: \`review/preparedness-r91-citation-claim-boundary-bindings-hold-20261103\`. Parent: R90 exact commit \`93415c0bb00c35e0a9789abbd8614fa417148cd7\`. This is a **read-only engineering diagnostic**, **not a release candidate**.

## Problem and nonclaims

R90 detects when ordered citation IDs, qualifiers, quantities and entire claim clauses change. However, a citation can retain the same source ID, same token order and same total count while moving from one instruction to another. A repeated source ID also has no guaranteed claim identity when articles are revised. A citation located after a statement is not evidence that the source supports that statement.

R91 conservatively fingerprints all literal \`{{cite:source-id}}\` anchors in both available historical text versions, including their exact source ID, occurrence rank, codepoint offsets, complete unabridged containing clause, source-relative rank, unchanged-versus-changed claim context, and position within that clause. When a matched-rank source moves to a different clause, moves within the clause, retains its ID while surrounding wording changes, or appears more than once, the system raises a **lexical human-review workorder**. Cases where one historical side is absent remain flagged as **missing-context**, not silently cleared. It never claims to have automatically proven which source originally supported which claim.

The cited source's complete text and URL remain in the **untouched R90 → R89 → R88 → R80** ancestor evidence. The R91 report embeds the entire original R90 record, preserving the 35 articles, six tools, 4,070 original DOM blocks, 2,173 literal citation occurrences, 2,359 source-variant edges, 242 distinct cited variants, and all 11 unmatched historical comparisons. No original text, citation, identifier, URL or navigation route is shortened, canonicalized, merged, published or silently reclassified. One original citation ordinal generates exactly one R91 reviewer row. The full-slate census is required for production \`live()\` and CI.

**These are lexical cues, not evidence of factual error, claim support, medically safe advice, historical-source equivalence, or permission to publish.** Sentence/clause parsing is deliberately limited. Abbreviations, decimal points, mixed HTML, rewritten sentences or repeated IDs may lead to extra review flags. They must **not** be silently auto-resolved.

## Review and verification

Each private row is indexed by exact \`(kind, slug, citation_ordinal)\`, points to the preserved original source variant keys and original DOM hash, and records the original unabridged historical clause(s) and literal source token positions. Both historical sides keep their complete-text SHA-256 receipts. Source, claim, qualified safety, and independent QD statuses remain \`NOT_REVIEWED\` with \`may_publish=false\`.

The optional CSV is **metadata only**, formula-injection escaped, and **not an approval import**. Never publish CSVs or source dossiers on the public site.

To reproduce on the trusted exact checkout (offline, private):

\`\`\`bash
python -I preparedness/tools/r91_historical_citation_claim_boundary.py
python -I -m unittest discover -s preparedness/tests -p test_r91_historical_citation_claim_boundary.py -v
python -I preparedness/tools/r91_historical_citation_claim_boundary.py --private-csv-stdout > /tmp/r91-private-metadata.csv
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
\`\`\`

Use private short-lived storage for CSV and remove it promptly. Running these commands does **not** satisfy the separate mandatory 13-stage integrity pipeline, independent QD approval, external claim verification, qualified safety review, WordPress accessibility checks or founder authorization.

## Dependency coordination and active HOLD gates

Pin/inspect all seven Claude clusters each run, the separate release candidate, QA #157 and synthetic-fixture #169, custody-repair and Hastings correction branches, homepage #49 and flagship #604. This branch only adds a reviewer overlay, isolated tests, docs and private CI; **do not merge, edit or deploy** any of those independent branches.

The custody-repair branch \`97921ca5e1f37535c34de95f12c99769a1bcb74d\` remains separate from RC \`ddb3528ba6494dada1fa1c3a142ce746e3a67706\` (three additional commits involving Hastings-route article, \`sources/crosswalk.json\`, and historical-field source evidence). Reconcile exact original evidence with qualified editors, not by changing historical baselines automatically.

QA PR #157 and #169 are independent drafts and unmerged. PR #169 still retains a \`_dup_test.json\` temporary fragment in the shared working tree. It must be fixed independently; R91 does not modify that PR.

Five advanced/frozen Claude-branch provenance differences; 30 duplicate-URL collision groups; 15 safety exceptions; 22 pending editorial decisions; unverified external citations/claims; qualified emergency and health assessment; actual WordPress/browser accessibility QA; mandatory workflow integrity; independent QD; and explicit founder release permission remain **OPEN**.

**HARD HOLD**: No human source/claim/safety approvals, no QD PASS, no CMS, WordPress or nav writes, no homepage edits, no branch merges, no public publishing.
