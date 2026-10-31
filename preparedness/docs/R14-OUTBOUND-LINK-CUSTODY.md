# R14 — Preparedness Archive body-link custody and provenance (DRAFT/HOLD)

Issue #136. This read-only utility does **not** verify external websites, medical/food/water/fire advice, source accuracy, reviewer identities or publication readiness. It does not create or edit any WordPress content, public navigation or homepage resources. All existing drafts remain unpublished.

## Risk closed

R8/R10 protect 1,959 explicit citation occurrences and article-specific sources. R11 protects WordPress-ready local artifact bytes. R12 checks rendered citation anchors; R13 heuristically flags potentially consequential uncited instructions. These checks do not, by themselves, account for ordinary inline HTML hyperlinks that can direct readers to unreviewed guidance outside the article's source trail.

R14 compares original resolved article-body HTML anchor events against actual rendered links in the `#pa-main` reader region. It requires exact link order, URL, text/accessible label, target and rel. It rejects malformed/truncated anchors, duplicate IDs, invalid fragments, dangerous URL schemes, credential-bearing authorities, encoded control bytes and unsafe external `target="_blank"` behavior. Existing R12 footnote `#src-N` links are explicitly supported.

Each destination records its exact URL and whether it matches an entry **for that article's contributor-specific source record**. Untracked destinations remain review priorities rather than automatic findings of inaccuracy; known URLs remain pending human review. Repeated URLs are kept as distinct events. No reviewer state changes, crosswalk consolidation or source approvals occur.

## Trusted-checkout commands

Run against the exact private checkout with the complete inherited Preparedness suite:

~~~sh
python -I preparedness/tools/evidence_freeze.py
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/outbound_link_custody.py --json-out preparedness/build/r14-outbound-link-audit.json
~~~

The R14 CLI invokes native source/evidence validation, R10 canonical corpus derivation, R11 byte-bound local draft custody, R12 rendered citation parity and R13 high-consequence triage before issuing a private HOLD receipt. The optional JSON export is restricted to the local build directory. The tool performs no network requests, uploads, CMS writes or public publishing actions. The exact 35-article / one-planner corpus and existing 1,959 citation inventory are not amended.

## Evidence and remaining blockers

A local isolated mirror ran **457 Python tests** successfully: 88 new R14 synthetic/adversarial tests plus the previously tested 369 R10–R13 tests. This is NOT an executed full-repository suite and NOT a factual review of the actual 36 draft items. Native full-corpus integration, actual export audit, external source-link opening, claim-level corroboration, reconciling 30 shared URL groups, qualified consequential guidance review, hosted CI and independent QD authorization remain outstanding.

Heuristic/parser limitations: dynamically injected JavaScript links are not audited, and exact-link match does not establish that link text or a cited document supports the article's factual claim. An empty queue is never a safety PASS. Do not update any human-link-check or safety-review label automatically.

**RELEASE HOLD / may_publish=false.** No branch merging, public release, navigation or WordPress writes based on these tests.
