# R122 — Reader-visible citation custody, full candidate census, conversion HOLD

Date: **2026-11-04**. Engineering lane #136; founder conversion #820; charter #818. **DRAFT ONLY / NO RELEASE.**

## Integrity improvement

R121 checks immutable Git article bodies, source-use records and counts, but an HTML comment, hidden element or attribute containing a `{{cite:...}}` token could still be counted in the raw source while not supplying visible evidence to readers. R122 adds a distinct **read-only, fail-closed** validator to evaluate citation visibility inside HTML text nodes. It obtains original and release-candidate article bytes from immutable Git blob identifiers in `preparedness/docs/R117_NINE_SNAPSHOT_GIT_OBJECT_CUSTODY_HOLD.json`. It requires exactly 35 paired article names, the seven Claude contributor heads and a HOLD governance record, and checks Git-object hashes before inspecting content.

Concealment classes include HTML comments, attribute-only citations, script/style/template/noscript/iframe/SVG contexts, the `hidden` attribute, `aria-hidden=true`, inline display/visibility hiding and common visually hidden classes. Missing or malformed citation tokens, unexpected roster/authority changes and mismatched blob bytes are rejected. Machine result is **HOLD even with zero findings**. This does not replace R114/R115, R121, actual print/style/browser inspection, evidence URL review, qualified emergency-safety review or independent QD.

Run on a trusted checkout containing referenced Git blobs:

```sh
python -I -m unittest discover -s preparedness/tests -p 'test_r122_reader_visible_citation_gate.py' -v
python -I preparedness/tools/r122_reader_visible_citation_gate.py --repo . --snapshots preparedness/docs/R117_NINE_SNAPSHOT_GIT_OBJECT_CUSTODY_HOLD.json
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
python -I -m unittest discover -s preparedness/tests -v
```

## Observed evidence — carefully separated

- **BUILT:** `preparedness/tools/r122_reader_visible_citation_gate.py` and isolated synthetic test suite. No original article, source, route, safety state or generated WordPress artifact modified.
- **TESTED LOCALLY:** **62/62** isolated Python tests and Python compilation pass. The exact committed blob SHAs match the local tested files: tool `31d0c67b4aec62a317f5c619b77e82f6a6b2af44`; tests `52924dc51e378a46bafc7141400cbc88b1ff1590`.
- **INDEPENDENT GITHUB EVIDENCE READ (not Python exact-checkout execution):** all 35 release-candidate body objects at pinned PR #584 head `ddb3528ba6494dada1fa1c3a142ce746e3a67706` were retrieved from GitHub. Simple HTML comment/script/tag stripping found **2,000 raw citation occurrences and 2,000 retained text tokens**, with no mismatched counts or malformed tokens observed. This is a *coarse preliminary cross-check*, not the complete Python parser's result and not print/CSS/browser proof. R120 reported 1,952 original-body citation occurrences, so candidate delta +48 agrees with previous reconciliation.
- **NOT VERIFIED:** full native 35-pair R122 parser run against a Git checkout, `validate.py`, `build.py`, repository regression suite, browser/print CSS, mandatory integrity, independent QD and qualified safety review. The container cannot resolve the private GitHub clone host; no trusted checkout is mounted. GitHub Actions has previously failed before runner startup; do not treat runner failures as code failures or passes.
- **SEVEN CONTRIBUTORS:** On 2026-11-04 re-resolved exact live head references; each matches frozen R117 SHA: food `f911ff7a`, health `d5ef5baf`, historical-field `4e5caf81`, historical-food `67e116e5`, historical-home `7504a5f0`, shelter `5daeaf2d`, start-here `2122d856`.
- **OTHER LANES:** PR #157 `7d1ae6b8` remains a separate draft with substantive household-drill and refrigerated-medication safety corrections requiring human adjudication against candidate #584. PR #169 `e9cd7766` remains a draft; its `test_register_fragments_cannot_duplicate_ids` still creates `_dup_test.json` in the shared source directory even though its first fixture was isolated. Homepage PR #49 `10495883` and flagship PR #604 `bdf01b4a` untouched.

## Preparedness conversion-first path: strict gate

**Audience intent:** household emergency contacts, school pickup/reunification and low-cost readiness. **Free guide candidate:** existing source-linked *A Household Emergency Plan That Actually Gets Practiced*, unpublished/safety HOLD. **Paid practical pack:** no FV-owned live Payhip SKU has been authenticated for seller, rights, current checkout, pricing, delivery and refunds; **DO NOT display a commercial link**. The 7-Day Focus Fieldbook may continue independently as existing non-preparedness lead magnet, but should not be substituted as a misleading preparedness pack. Retired water products excluded.

**Draft editorial CTA (not staged/published):** “Make a household emergency plan before you need one. Read the source-linked planning guide and adapt it to your family.” Add a free worksheet mention **only after** the exact public asset and download have passed safety/source/accessibility/delivery checks. No paid upsell unless an actual rights-cleared matching pack and fulfillment are independently established.

| Offer → funnel step | Blocker | Proposed change/acceptance | Pass/fail evidence | Owner |
| --- | --- | --- | --- | --- |
| Optional owned preparedness pack → payment | No verified live matching SKU, rights, pricing, delivery or refund terms | Seller records, read-only offer audit, approved staging checkout and file open on mobile | **UNVERIFIED/HOLD** | Growth / Claude |
| Free planning guide → reader | Safety wording #157 and source/citation reviews unresolved | Human claim adjudication, direct citation/link review, mobile/print proof | **HOLD** (structural tests only) | Preparedness / independent QA |
| Grok high-intent video → guide | TASK-008 asset_id and landing URL unverified | Coordinate real `utm_content=asset_id`, `utm_campaign=preparedness_pilot_2026_11` and allowed bio/pinned-link behavior | **NOT TESTED** | Grok / Praxxis; Claude destination |
| Relevant CTA → checkout | No verified pack or approved placement | Clear digital-delivery/disclosure, 360/390 px keyboard/touch checks, merchant acceptance | **NOT TESTED** | Claude / Site QA |
| Order → realized net revenue | No verified transactions, refund/fee and human-session denominator | Source-confirmed 7/30-day cohorts; calculate net revenue/1,000 qualified sessions, warn small samples | **N/A; no orders claimed** | Growth / Claude |

**Release HOLD:** no Git merge, CMS, WordPress, nav, homepage, analytics instrumentation, email, social distribution, merchant or spend. Do not assert QD PASS, unreviewed medical safety, sales, or attributed conversions.
