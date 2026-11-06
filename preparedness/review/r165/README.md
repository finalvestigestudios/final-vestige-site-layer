# R165 — Family Reunification Card inline-JS dependency custody / HARD HOLD

**2026-11-06 PT · Issues #136 / #820 / business charter #818.** Parent: R164 draft PR #1233 at `3d2395d93c7e8586681cf88f8b10f1e4083bd7c8`. Additive-only, review-only. The 35 instructional article bodies, metadata, source fragments, source crosswalk, staging contents, homepage and marketing/merchant systems are untouched.

## Why this is needed
R164 statically checks 17 form controls, conservative script tokens, and original staged HTML, **but flags two unresolved inline JavaScript dependencies**. WordPress draft rendering uses `build.resolve_tokens` to expand `{{inline-js:...}}`; unexpected JS changes or altered token closure could bypass checks limited to unexpanded HTML. R165 closes the specific dependency-custody gap, NOT the browser privacy or release approval gap.

New `preparedness/tools/r165_inline_dependency_custody.py` calls R164 -> R163 -> R162 -> R161 fail-closed custody first. It then reads both helper scripts by their exact original Git blob identity, refuses symlinks or altered JavaScript, checks all template tokens exactly once and in the build's known order, rejects sensitive network/storage/dynamic-script patterns and HTML/script boundaries, expands the two scripts using the build's identical token-replacement strategy, and records the expanded SHA-256. An optional sandboxed Node VM runs ten narrow model behavior checks (minimal card omits school, alternate meeting point and care/access details; normal model includes them; field limits, ID/address flags, stale review reminders). Node absence returns `NOT_RUN_NODE_MISSING` and cannot be interpreted as success.

Pinned source Git blobs from authenticated GitHub read:
- `preparedness/tools/shelter_common.js` — `efe1c7910d99437e3687621dabab8ce55dc24fd4`.
- `preparedness/tools/reunion_card.js` — `b1a09b1eda1ae26f081de65b400a37bc19538035`.
- R163 staged card remains protected upstream at `1b8a340c69b28280ae485a667da4564d9e849d70`.

**IMPORTANT LIMIT:** Lexical scanning is not a JavaScript security proof; a Node VM of the pure data model is not a rendered browser, printed output, WordPress script integration, network capture, OS spooler, or third-party plugin/extension test. No 'local only', 'never transmitted', or 'medically safe' claims are authorized. The validator always reports `DRAFT_HARD_HOLD` or `INVALID_HARD_HOLD`, exits 2 and sets publication/paid authorization false.

## Evidence and native commands

Executed locally against **synthetic fixtures**, not a complete repository checkout:

```
python -I -m unittest discover -s preparedness/tests -p 'test_r165_inline_dependency_custody.py' -v
python -I -m py_compile preparedness/tools/r165_inline_dependency_custody.py preparedness/tests/test_r165_inline_dependency_custody.py
```

**73/73 tests PASS**, including adversarial injection, dependency mutation, missing Node, broken Node, and missing checkout. Git-blob verification against committed Python files required. R164 static and full 35-article validation are NOT RUN locally because direct GitHub cloning fails DNS; native `validate.py` / `build.py` / full 36+ integration suite and browser QA are NOT VERIFIED. On an authenticated full checkout, execute:

```
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
python -I preparedness/tools/r165_inline_dependency_custody.py --repo .
```

The final command **intentionally exits 2 even on a structural match**; inspect its JSON state, do not interpret the exit code as a test failure or release pass.

## Seven Claude cluster heads examined (read-only; 2026-11-06)

| Cluster branch | GitHub SHA |
|---|---|
| `claude/prep-start-bbfeb8` | `2122d856fce9f64887c16df3d52e64be9f59a55b` |
| `claude/prep-food-ccdc55` | `f911ff7a655de8d81535ea86ec3d65a49ee76648` |
| `claude/prep-health-837444` | `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17` |
| `claude/prep-shelter-5e1e0e` | `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976` |
| `claude/prep-hist-food-b81f19` | `67e116e536c7410bed30f8f3b1bb8c166f3c223d` |
| `claude/prep-hist-home-0e0e38` | `7504a5f099594d635e3dd7332a33a2e1346c43a2` |
| `claude/prep-hist-field-9db767` | `4e5caf812727953aa45e3bda2d382f2c67b6a09c` |

Some contributor SHA snapshots differ from old QA PR base refs; **do not cherry-pick or declare unchanged from older records without direct compare**. Safety PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`, fixture PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5` and fixture follow-up PR #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8` remain separate. Homepage PR #49 `10495883299d53596992c26a8987f629b2904670` and PR #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176` are not modified.

## Source review and commercial acceptance (still blocked)

Prior issue evidence records **75 pending source-review decisions**, including eleven Family Card relationships (Colorado attribution, NCMEC scope, six HTTP-403/manual checks) and eight Historical Food substitution decisions. These counts are carried forward from #136, not re-certified as resolved. No automated inspection is qualified adjudication or QD. No 35-article release approval. WordPress outputs are draft-only.

**Audience:** caregivers planning school pickup and emergency reunification. **Free guide:** source-backed candidate *Household Emergency Plan*, readable without signup once independently approved. **Optional free practical tool:** quarantined printable *Family Reunification Card*. **Paid step:** DISABLED: no independently authenticated rights-cleared, currently buyable Preparedness SKU with merchant, fulfillment, refund and mobile checkout evidence. Do not substitute retired water offers or create speculative products.

| OFFER → STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| Existing paid Preparedness pack → purchase | Current matching SKU/rights/merchant delivery unverified | Read-only review of real existing product and staged checkout/delivery/refund acceptance | HOLD: no verified paid SKU/order | Commerce / Claude |
| Free Household Emergency Plan → reader | Independent source/safety/QD incomplete | Qualified review + actual WordPress preview | DRAFT, not release tested | Preparedness / QA |
| Plan → free Card → print | Two JS deps previously unexpanded; privacy & print untested | R165 source closure + full staged browser network, print, keyboard QA | BUILT; 73 synthetic tests; browser NOT RUN | Preparedness / Site QA |
| Grok published asset → guide | No verified matching creator media ID or page destination | Praxxis/Grok TASK-008 read-only inventory, approved asset_id + permitted bio/caption URL | UNVERIFIED; no fictional UTM | Grok / Praxxis |
| Qualified humans → confirmed purchase → net realized revenue | No attributable settled order, fees/refunds or qualified human denominator | Merchant receipts + consent-respecting 7/30-day attribution | NOT COMPUTABLE | Commerce / Analytics |

Draft-only CTA copy for eventual qualified review: **"Build your household contact and school pickup plan — free guide, no signup required."** Not live. Required landing acceptance checks: matching promised topic and current safe instructions; prominent free CTA on phone; no forced signup; source/date and privacy disclosures; a source-reviewed printable with a clear minimal option; accessible controls; explicit distinction between resource click, confirmed lead, checkout start and merchant-confirmed sale. Track existing permitted events only; no duplicate scripts. Current Grok TASK-008 inventory does not authenticate a Preparedness-specific published `asset_id` and landing URL; leave NULL.

**No merge, publication, navigation, CMS, analytics, email, social, merchant, affiliate, payment, or spending action permitted by this PR.** Founder controls release. The only valid states are BUILT / LOCALLY TESTED / DRAFT / HARD HOLD.
