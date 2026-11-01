# R51 — Joint quantitative/safety source custody (PRIVATE / HOLD)

**Issue:** #136  
**Base:** exact R50 safety-review HEAD `4c55d2a86a419c81c96d04d06ed880ba33af3500`  
**Additional source:** exact R49 numeric-review HEAD `dffad453c064e28b84dd0a4f5505a29e21441247`  
**Release authorization:** NONE. No live WordPress, homepage, CMS, public navigation, publishing or merge.

## Why this integration exists

R49 was created on R48 `b418a558`; R48 subsequently advanced to
`dbd53411` with an additional 15-incident / 25-blocked-source safety register.
R50 was built on that newer R48 head. GitHub compare showed these lines
**diverged at `b418a558` (R49 4-only commits, R50 5-only commits)**
but the changes introduce **non-overlapping files**. R51 starts at R50
and restores all three original R49 files at their exact original Git blob
identities, not a manual paraphrase or lossy reimplementation.

The joint R51 validator consumes the *existing* R49 and R50 read-only
audits on one original archive Library object and one original R48 source
accessibility snapshot. It verifies report payload hashes, both releases'
unreviewed/human/HOLD status, all 186 numeric citation-bearing blocks,
89 machine-sampled URLs (7 inaccessible), 15 OPEN safety incidents,
25 historically blocked original source IDs, 29 machine candidate rows
with B09 an unevaluated placeholder, exact article-body SHA-256 parity
across matched R49/R50 tasks, original per-article selected source SHA-256
parity across both work orders, contributor variant preservation and
individual source evidence identities.

Importantly, a historically failed source **does not become human-verified**
merely because a later machine snapshot lists a usable page. Numeric
tokens found anywhere on a page also do not establish correct unit,
claim attribution, scope, chronology or emergency/medical safety.

## Native test / trust boundary

- R49's original 65 tests and R50's original 139+ synthetic checks remain
  in place and are both discovered by the native Python test runner.
- R51 adds 70+ separately named repinned-payload adversarial mutation tests,
  positive same-URL/different-original-record checks, and a full-archive
  one-checkout integration smoke test. The mutation tests deliberately
  recompute same-checkout report digests after altering evidence; the
  independent checks must reject the forged claims and false approvals.
- The exact repo-level census is strictly pinned by the R51 command.
  Small synthetic tests pass an explicit reduced census, never the CLI default.
- Execute from the repository root:
  `python -I preparedness/tools/validate.py`
  `python -I preparedness/tools/build.py`
  `python -I preparedness/tools/r51_joint_review_gate.py --format summary`
  `python -I -m unittest discover -s preparedness/tests -v`
  and existing 13 mandatory private stages.
- A successful same-checkout test is **machine consistency only**, not a
  trusted out-of-band custody anchor or independent qualified review.

## Original content and safety states

R51 does not modify the original **35 article draft bodies**, water
planning tool, any of **1,959 citation occurrences**, **367 original
source-reading relationships**, **43 fallback relationships**, or **30
shared-URL source groups**. It does not deduplicate same-URL contributor
reading scopes. Original 7 contributor Git SHAs remain the custody inputs.
Historical metadata such as `safety-approved-draft` is not publication authority.

## Independent QA remains independent

PR #157 (Start Here safety wording) and #169 (synthetic food fixtures)
remain separate draft reviews; inspect their diffs before incorporating
any suggestions. Homepage #49/#254 and Gutenberg #414 are outside scope.

## Current open blockers — never mark PASS from this file

0/206 documented direct human source-link checks; independent claim scope
and contextual support reviews; 30 shared-URL groups; 43 fallbacks;
15 still-open safety exceptions; qualified human water/food/fire/clinical/
infant/evacuation review; complete rendered-browser/WordPress accessibility
QA; unresolved historical source retrieval; cross-platform Windows test
fixture issues; independently controlled reviewer identity, receipt ledger,
external trust anchor; exact-current-head independent QD. Preserve HOLD.

**No publication, no new public pages, no navigation or live CMS writes,
no QD PASS, no certification that unreviewed advice is medically safe.**
