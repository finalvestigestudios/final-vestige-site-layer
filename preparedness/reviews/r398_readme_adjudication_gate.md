# R398 — Source/fork review intake and fail-closed integrity gate

**2026-11-15 PT · Preparedness-only · DRAFT / HARD HOLD · Issue [#136](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/136) · Conversion [#820](https://github.com/finalvestigestudios/final-vestige-site-layer/issues/820) / charter #818.** This branch stacks on unmerged R397 `a22c8797da58ecf186f50fcf47063bd195fd3c17`. No source fragment, original manuscript, taxonomy, canonical URL, CMS, navigation, analytics, commerce or creator content is changed.

## What changes, and what remains deliberately unresolved

- `r398_human_adjudication_intake.json` creates **14 human-review-only cases** pinned to the authentic R397 docket blob `86d22a1d504c93db7689b914e2202a7845b648e2`. It preserves each of the five full **supports_exact / reading_scope_notes_exact** source comparisons (and original branch/blob/URL/human-link-check metadata); and all nine Shelter manuscript/metadata/source fragment candidates, with branch, Git blob and byte counts. All proposed selections are null. The source dossier remains R397's full 203 IDs / 280 original occurrences / 17 exact shared-URL alias groups / 35 article identities / 77-object manifest.
- `r398_adjudication_review_gate.py` is a **read-only, deterministic** verifier for the original R397 docket. It pins the docket's Git blob, all three original manifest/source register blobs, original 35/77/7/280/203/34/5/9 counts, 9 original branch refs, 17 alias groups, source variant crosswalk joins, original body fork joins, and all review/safety-state flags. It rejects automatic manuscript selection, missing claim-reading notes, source substitutions, missing branches and invalid proposed Git objects.
- `test_r398_adjudication_review_gate.py` contains **74 local synthetic/adversarial unittest methods** including absent input, tampered Git objects, erased source-reading scope, altered citation/source provenance, duplicate article/source IDs, unsafe fork paths, alias mismatches and forged approvals. These tests do not independently re-read source pages, perform native 35-article build, or grant QD status.

**Read-only sample command on an authenticated complete checkout:**

```bash
python -I -m unittest discover -s preparedness/tests -p 'test_r398_adjudication_review_gate.py' -v
python -I preparedness/tools/r398_adjudication_review_gate.py --docket preparedness/reviews/r397_original_source_fork_docket.json --emit-template
python -I preparedness/tools/validate.py
python -I preparedness/tools/build.py
```

The R398 CLI **always returns exit code 2 (HARD HOLD)**, even if structural integrity checks return `"integrity":"PASS"`. This is intentional; a passing structural comparison **is not** human source review, qualified emergency/medical/food/water or child-privacy approval, or release authorization. Authentic 50+ private WP and preview HTML pairs require independent native execution; no publish step belongs in this branch.

## Pending decisions for qualified reviewers

1. Compare primary documents and citations for `fsis-power-failure`, `loc-pioneer-diaries`, `loc-prairie-traveler`, `nchfp-home` and `nchfp-jerky`, documenting *exactly what was opened/read*, page/version/date and claim-level scope. All 10 source-variant `human_link_check` values were **false** in the original record; a timestamp in a draft does not equal qualified human verification.
2. Read and compare all three original Shelter branch versions of four body/meta pairs (`family-communication-plan`, `home-fire-escape-plan`, `outage-heat-cold-generators`, `shelter-or-evacuate`) plus `shelter.json`. A repeated SHA does not justify selecting other files; a longer manuscript is not a better one by default.
3. Independently assess Article #7 water/home-filter claims, Article #11 food preservation, family communication Article #15, private Tool #104 child privacy/accessibility/no-JS and other applicable emergency/medical QD; review dependent QA PR #157 (HEAD `7d1ae6b8ef93d10cfb6810987672360885e9c1aa`) and fixture PR #169 (HEAD `e9cd7766dac59d47ab467d8945269b9146c2aef5`), with dependent #2205 `bbcf1859768624c611df4abadc564c18247cf32a` left open.
4. Run all authentic native validators against the complete checkout and private exports; block any approval until reproducible source/claim/render parity, proper source-dated qualifiers, no duplicate canonical URLs and appropriate human signoffs are on file.

## Conversion-first acceptance, without speculative products

| OFFER → FUNNEL STEP | BLOCKER | CHANGE / EXPERIMENT (DRAFT ONLY) | PASS/FAIL EVIDENCE | OWNER |
|---|---|---|---|---|
| One *existing* FV-owned/license-authorized Preparedness family planning pack → real paid order | No genuinely payable/rights-cleared/fulfillable SKU authenticated | Founder/Commerce read-only verify merchant listing, rights, mobile checkout, delivery, license, fees/refunds before paid CTA | **HOLD / UNVERIFIED**; no order confirmation or settlement | Founder/Commerce |
| Genuine published family-contact/reunification Grok social asset → free source-backed Archive | No independently authenticated exact `asset_id`, post, intended hook, rights, permitted mobile destination | Grok/Praxxis compare against original TASK-008, test actual signed-out phone link and intent; do not repurpose unrelated historical video | **HOLD / UNKNOWN**; candidate topic only | Grok/Praxxis |
| Free `https://finalvestige.com/preparedness/` → optional Tool #104 | Child privacy and emergency-review gates not granted; original article still private | Retain free un-gated agency-linked resources; show no Tool #104 offer until independent QD and usable no-JS/print review | **HARD HOLD**; unpublished CTA “Start With Trusted Preparedness Resources” | Preparedness/QD |
| Qualified-human `asset_id`/campaign sessions → relevant click → confirmed lead → merchant order → realized net after fees/refunds | Consent-appropriate attribution and settlement receipts unavailable | Claude/Commerce use existing analytics (no duplicate scripts) and merchant confirmations; 7/30-day cohorts and tiny-sample flags | **NOT COMPUTABLE**, not zero; clicks/signups are not sales | Claude/Commerce |

No paid services, retired water giveaways, commercial offers, publishing, WordPress/CMS, navigation, homepage, affiliate activation, social posting, email, measurement deployment, or spending. Founder retains commercial/production approval. Grok owns social publishing. Praxxis independently QA's real assets. Claude owns core website/analytics. All new code is confined to Preparedness-only review tooling.

**Current evidence scope:** 74/74 synthetic Python tests passed locally on byte-identical tool/test sources, and Python compilation passed. Full native checkout/build and actual private exports not executed in local runner (GitHub hostname could not be resolved); hosted CI outcome and independent QD are not asserted PASS. The PR must remain draft/unmerged.
