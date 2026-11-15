# R388 — Preparedness source URL alias and identity-drift custody

**DRAFT · HARD HOLD · review only.** Issue #136; revenue/attribution #820 and business charter #818. This PR stacks on the exact R387 draft HEAD `eaa3ef415cfe59b448255670cc85cb437d039f1e`, without merging or selecting any source/variant.

## New safety gap and implemented behavior

R375 protects exact shared URLs and five divergent source IDs; R385 links original citation occurrences to those sources. Source URLs may nevertheless appear distinct despite differences in host casing, an explicit HTTPS default port, a trailing slash, an unreserved percent escape or marketing parameters. Conversely, **the same source ID may reference materially different destinations**. R388 adds a deterministic *review-only* crosswalk over the BASE source register and all seven original Claude source fragments.

- Retains raw-URL SHA-256, Git source blob SHA, original branch, source ID, sanitized destination host/path and the exact original claim/citation occurrences from R385.
- Generates *probable URL-alias* groups across source IDs and URL spellings, plus a separate *same-ID/different-destination* review queue.
- Normalizes only conservative identity hints: lowercased/IDNA host, default HTTPS port, trailing slash, unreserved percent escapes and known campaign trackers. It intentionally preserves `www` differences, significant query parameters and query order.
- Rejects HTTP, credentials, fragments, malformed escapes, local/private endpoints, suspicious path traversal and nonstandard ports; **never follows redirects or asserts that two URLs are actually equivalent.**
- Redacts full query values from the review docket. Evidence URLs remain available in the original immutable Git objects to qualified reviewers.
- Calls the prior authenticated R385 source-impact gate against pinned original Git blobs, preserving 35 original draft articles, nine unselected Shelter Git-object conflicts and five divergent source IDs; **neither a clean review nor a source link constitutes advice safety clearance.**

The original custody manifest currently identifies **77 original paths, 35 article/metadata pairs and nine unresolved blob forks**. Baseline source crosswalk: **seven fragments, 280 source occurrences, 203 source IDs, 17 exact shared-URL groups and five divergent IDs**. These are historical manifest observations, not a new native R388 count.

## Direct verification

- **80/80** new synthetic adversarial tests PASS (URL attacks, source ID drift, alias groups, immutable provenance, redaction, fail-closed approval gates).
- **774/774** locally assembled, available R374–R388 Python tests PASS; this is not an exhaustive native-repository suite.
- Python source/test compilation PASS.
- Source Git blob `d42cf78f015b6f10946316b768ae5e9e303b4fe8`; test Git blob `bb54ed85ffd81d0d76fbcae7a689a8ccbe80eefe` exactly match locally executed files.
- Local native command `python -I preparedness/tools/r388_source_url_alias_custody.py --repo .` returned exit **2** and `INVALID_HARD_HOLD`: authenticated original Git objects unavailable in the partial container workspace (GitHub DNS resolution failed).
- Full original build, 50 WordPress + 50 private preview exports and hosted CI: **NOT EXECUTED / NOT VERIFIED**. No qualified emergency, food, water, privacy or QD PASS.

Original branch comparisons performed this run: seven Claude cluster heads and two Shelter successor heads, nine of nine **identical** to SHA-pinned manifest (0 ahead/0 behind). Independent QA #157 HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`; synthetic fixture #169 HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5`; its dependent fix #2205 HEAD `bbcf1859768624c611df4abadc564c18247cf32a`. Homepage lead #1689 HEAD `f55c36b6598eec558dd8bb24e4c8988becc51be0`. All left untouched.

## Conversion-first acceptance, in strict priority order

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT | PASS / FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| One **existing, genuinely payable** FV Preparedness pack → merchant-confirmed paid order | No independently authenticated FV-owned, rights-cleared, payable and deliverable SKU; fees/refunds unknown | Founder/Commerce must verify SKU, ownership, product fit, checkout, fulfillment, refund route before any paid CTA | **HOLD**; no verified merchant order, price, delivery or net receipts | Founder / Commerce |
| Published family-contact/reunification social asset → authentic FREE Preparedness Archive | Actual published Grok asset ID, claims, rights and mobile URL not independently verified | Match one real creator asset with free official-resource `https://finalvestige.com/preparedness/` and review message-to-page intent, disclosures and accessibility | **UNVERIFIED**; no social queue/posts changed | Grok / Praxxis |
| Archive free guide → optional Tool #104 | Child privacy, physical printing, accessibility and emergency-advice reviews outstanding | Preserve as **private optional proposed tool** until qualified human review; do not imply it is an approved freebie or product | **HARD HOLD** | Preparedness / QD |
| Qualified human session by `asset_id`/`utm_campaign` → landing → CTA → confirmed lead → confirmed paid order → net revenue | No merchant-confirmed orders, refunds, fees, attributable session cohort; no consent-reviewed instrumentation | QA existing measurement contract with Claude, no duplicate scripts; 7/30-day tiny-sample labels | Net revenue/1,000 qualified sessions **NOT COMPUTABLE** | Claude / Commerce |

**Free-only draft CTA:** “Start With Trusted Preparedness Resources” → the *existing* Archive official-resource landing, subject to authentic Grok social asset verification. It is **not published**. Avoid the retired water manuals and unapproved paid offers.

## Release governance / next authentic integration

Do not merge this draft until the native clean checkout runs the *exact committed bytes* and all source, citation, variant and rendering gates against authenticated originals; resolve actual alias/destination conflicts with qualified review and documentary evidence; keep all nine forks and five source conflicts open until adjudication; inspect full WordPress/private exports and obtain human emergency/food/privacy/QD signoff. Publish nothing and do not touch WordPress, navigation, homepage, analytics, emails, Grok's queue, or commerce activation. Founder alone approves release/spending.

**Never convert DRAFT, TESTED or a mechanically matching citation into LIVE, VERIFIED, medical safety, source equivalence, revenue or QD PASS.**
