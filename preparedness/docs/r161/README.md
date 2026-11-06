# R161 — all-article immutable body custody (Issue #136)

**STATUS: DRAFT / HARD HOLD.** This is an isolated, additive engineering review. All 35 instructional articles remain unpublished drafts. No claim of QD PASS, safety/medical clearance, published guide, purchaser, confirmed sale, live conversion measurement, or native build success.

## Why this change matters

R160's claim-context docket covered 2,000 citation occurrences and pinned 35 metadata blobs, but its per-citation fingerprints bound only local HTML neighborhoods. An edit to an uncited sentence, warning, or HTML elsewhere in a body could leave all those local context fingerprints unchanged. R161 closes this *integrity blind spot* by freezing each **entire original article body**, not only metadata and citation neighborhoods.

The `body_custody.json` baseline was assembled from **35 authenticated, read-only GitHub file fetches at exact R160 commit `9578433a87d6b866848da55ea714f8deac6ed07c` on November 5, 2026 (Pacific)**. For each article it stores the actual Git blob SHA-1 and original citation occurrence count. It preserves **35 body/metadata pairs, 2,000 citations, 385 article-specific source-use records**, and references the exact R151 metadata manifest Git blob `9cf386519eda970209ff6be4ff0243661cd9d996`. The R161 baseline itself is Git-blob pinned at `fede4222c796d92798eff7cf0dcb225c291f7d61`. All seven R151 article three-way candidate Git blobs matched the newly fetched original bodies.

`preparedness/tools/r161_body_custody_gate.py` is read-only. It rejects missing/extra bodies or metadata; symlinks; changed raw body bytes even when citations stay the same; changes to the R151 metadata trust anchor or any 35 source-use interpretations; source IDs without citations or vice versa; reduced reading depth; citation-count/format changes; changed article slugs/routes; unsafe publication or safety state alterations; and changes to the seven article integration decisions. For a structurally unchanged candidate it returns `DRAFT_HARD_HOLD`; for an altered/invalid candidate it returns `INVALID_HARD_HOLD`. The CLI always exits **2** (no green publication pathway).

**Immutable-body custody is not a claim that the frozen content is correct.** In particular, citation context/source suitability, historical food preservation guidance, six previously blocked source lookups, Family Reunification Card privacy/print behavior, and independent safety review remain outstanding. Human-reviewed content edits must produce a new, explicitly reviewed baseline revision in a separate isolated proposal; do not silently re-pin. This PR does not authorize edits to the originals.

## Local isolated testing and full-checkout requirements

New `preparedness/tests/test_r161_body_custody_gate.py` is a wholly synthetic 35-body fixture suite, using temporary directories. **56/56 Python unittest tests passed locally** on Nov 5 PT (35 individual full-body mutation tests plus 21 control/adversarial cases); Python compilation passed. The **committed Python files must match their locally tested Git blob identities**: gate `e2c3ed8eb1e8f2a97a5146b8b4162be87cf02451`, tests `8cffce79c4d420390206a5a7346a6ed3bd768201`. The committed manifest Git blob is `fede4222c796d92798eff7cf0dcb225c291f7d61`.

On a trusted exact-head checkout, the reviewer must run the following read-only validations (do not interpret an expected exit 2 as success without inspecting the JSON):

```bash
python -I -m unittest discover -s preparedness/tests -p test_r161_body_custody_gate.py -v
python -I preparedness/tools/r161_body_custody_gate.py --repo .    # expected exit 2, DRAFT_HARD_HOLD
python -I preparedness/tools/r160_citation_context_gate.py --repo . # expected exit 2, DRAFT_HARD_HOLD
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

Full native validation/build, all 35-article repository regression cases, WordPress draft rendering, mobile/browser privacy and print checks, independent source review and QD remain **NOT VERIFIED**: the local container cannot resolve `github.com` for cloning. No GitHub Actions budget was increased or rerun requested.

## Dependency coordination — exact references checked this run

Seven Claude contributor heads:
- Start Here `2122d856fce9f64887c16df3d52e64be9f59a55b`
- Shelter `5daeaf2dd5ab71806a6b73c91edfb1d8df5da976`
- Food `f911ff7a655de8d81535ea86ec3d65a49ee76648`
- Health `d5ef5bafd68361434dd1cc9209915b8e8a4eaf17`
- Historical Food `67e116e536c7410bed30f8f3b1bb8c166f3c223d`
- Historical Home `7504a5f099594d635e3dd7332a33a2e1346c43a2`
- Historical Field `4e5caf812727953aa45e3bda2d382f2c67b6a09c`

Independent QA draft PR #157 `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; test-isolation draft PR #169 `e9cd7766dac59d47ab467d8945269b9146c2aef5`, follow-up #973 `4d40996a559b0124d74a9bb3bdcd481ad1992aa8`. Homepage #49 `10495883299d53596992c26a8987f629b2904670` and #604 `bdf01b4a3e13fd6179ae9e847c9d4429bbe16176`. No branches changed. R151 already reconciles five of seven later historical-article revisions (two Historical Food substitutions remain pending human source review). Do not merge these divergent contributor heads indiscriminately.

## Business and offer gates — #820 / #818

Narrow audience: families with school-age children organizing emergency pickup, contacts and reunification. Creator ownership stays with Grok; Praxxis coordinates via existing TASK-008 Drive handoff. The November 5 handoff contains **no verified Preparedness asset ID or exact allowed destination**, so do not manufacture one.

**OFFER → FUNNEL STEP → BLOCKER → PROPOSED CHANGE → EVIDENCE → OWNER**

1. Existing rights-cleared FV Preparedness paid pack → merchant purchase → no matching authenticated purchasable SKU/rights/checkout/delivery/refunds → Commerce confirms actual product acceptance and reconciles a permitted checkout/delivery test **before** any public paid CTA → **HOLD** → Commerce/Claude.
2. Household Emergency Plan (free, essential instructions ungated) → reading/optional lead → source, safety and QD review pending → native build plus qualified source review and staged mobile/accessibility → **DRAFT** → Preparedness/QA.
3. Family Reunification Card (optional practical tool, free proposed) → usable printable tool → 11 unresolved source relationships, disputed Colorado/NCMEC scope, privacy/print QA incomplete → review quarantined R159 wording and test in isolation → **HARD HOLD** → Preparedness/Site QA.
4. Grok school-pickup/reunification asset → qualified campaign session → missing verified actual `asset_id`, platform URL and exact landing → reconcile TASK-008 in existing Drive process without changing Grok queue → **UNVERIFIED** → Grok/Praxxis.
5. Paid order → realized net revenue → missing merchant-confirmed settled orders and qualified-human session denominator → privacy-respecting seven- and thirty-day reconciliation (confirmed orders, fees, refunds; never treat clicks/leads as purchases) → **NOT COMPUTABLE** → Commerce/Growth.

**Draft CTA only:** "Make a household emergency contact and school pickup plan — free guide." Do not put essential safety advice behind signup or payment. Do not resurrect retired water offers or invent a paid SKU.

No WordPress/CMS/navigation, live analytics/scripts, merchant, email, affiliate, social posting or spending changes. Source review (75 outstanding tasks), source/medical safety review, independent QD and founder production approval stay mandatory.
